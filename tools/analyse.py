#!/usr/bin/env python3
"""Bildanalyse für Sketch Help, zweistufig, mit groben Ansichten statt Winkeln.

Stufe 0  Bild aufrecht drehen (EXIF), auf 1280 px verkleinern, Helligkeitsstreuung messen.
         Fast einfarbige Bilder (grau, schwarz, weiß) gelten ohne KI als unbrauchbar.
Stufe 1  Ganzes Bild: brauchbar?, Art, Geschlecht, Haare, Ansicht (Drehung, Neigung),
         Rahmen um die Figur und um das Gesicht.
Stufe 2  Gesichtsausschnitt (mit Haaren, vergrößert): Ansicht noch einmal und Rahmen für Augen,
         Mund, Nase, Haare, Ohren. Rahmen werden auf das ganze Bild zurückgerechnet.

Ansicht: Stufe 2 gilt, wenn sie gelaufen ist, sonst Stufe 1 (z. B. Figur von hinten).
Beide Urteile stehen im Ergebnis (ansicht_ganz, ansicht_kopf), damit man sie vergleichen kann.
Das Feld kopf (yaw/pitch/roll) wird nur aus der Ansicht abgeleitet, damit ältere App-Versionen
weiter sortieren können. Es ist keine Winkelschätzung.

Alle Rahmen als [x1, y1, x2, y2] normiert auf 0..1000, bezogen auf das aufrecht gedrehte Bild.

    python3 analyse.py --dir test --out ergebnis3.jsonl --ollama http://192.168.178.135:11434
    python3 analyse.py --dir test --out ergebnis3_spiegel.jsonl --spiegeln   # Gegenprobe

--spiegeln spiegelt jedes Bild waagerecht. Eine stabile Analyse liefert dann die gespiegelte
Drehung (¾ rechts wird ¾ links) und sonst dieselben Schlagworte; vergleich.py wertet das aus.

Braucht Pillow. Erfolgreich ausgewertete Bilder werden beim Neustart übersprungen,
fehlgeschlagene wiederholt. Nach 3 Verbindungsfehlern in Folge bricht der Lauf ab.
"""
import argparse, base64, io, json, pathlib, sys, time, urllib.error, urllib.request

from PIL import Image, ImageOps, ImageStat

VERSION = 4
EXT = {".png", ".jpg", ".jpeg", ".webp"}
BOX = {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4}

DREHUNG = ["frontal", "dreiviertel_links", "dreiviertel_rechts", "profil_links", "profil_rechts", "hinten"]
NEIGUNG = ["oben", "augenhoehe", "unten"]
SPIEGEL = {"dreiviertel_links": "dreiviertel_rechts", "dreiviertel_rechts": "dreiviertel_links",
           "profil_links": "profil_rechts", "profil_rechts": "profil_links"}
# Nur für ältere App-Versionen: typische Winkel je Kategorie (yaw positiv = Gesicht zur rechten Bildseite,
# pitch positiv = Ansicht von oben)
YAW = {"frontal": 0, "dreiviertel_links": -45, "dreiviertel_rechts": 45, "profil_links": -90, "profil_rechts": 90, "hinten": 180}
PITCH = {"oben": 25, "augenhoehe": 0, "unten": -25}

ANSICHT_TEXT = """drehung: wohin das Gesicht aus Sicht des Betrachters zeigt.
- frontal: Gesicht schaut zum Betrachter, beide Augen etwa gleich groß.
- dreiviertel_rechts: Gesicht zur rechten Bildseite gedreht, beide Augen sichtbar, das rechte kleiner.
- dreiviertel_links: Gesicht zur linken Bildseite gedreht, beide Augen sichtbar, das linke kleiner.
- profil_rechts: Seitenansicht, Nase zeigt zur rechten Bildseite, nur ein Auge sichtbar.
- profil_links: Seitenansicht, Nase zeigt zur linken Bildseite, nur ein Auge sichtbar.
- hinten: man sieht den Hinterkopf, das Gesicht kaum oder gar nicht.
neigung: von wo man auf den Kopf schaut.
- oben: Kamera über dem Kopf, man sieht viel Scheitel, das Kinn wirkt klein.
- augenhoehe: Kamera etwa auf Augenhöhe.
- unten: Kamera unter dem Kopf, man sieht unter das Kinn."""

SCHEMA_1 = {
    "type": "object",
    "properties": {
        "brauchbar": {"type": "boolean"},
        "grund": {"type": "string"},
        "art": {"type": "string", "enum": ["kopf", "oberkoerper", "ganzkoerper", "sonstiges"]},
        "personen": {"type": "integer"},
        "geschlecht": {"type": "string", "enum": ["maennlich", "weiblich", "unklar"]},
        "haarlaenge": {"type": "string", "enum": ["kurz", "mittel", "lang", "unklar"]},
        "frisur": {"type": "string"},
        "drehung": {"type": "string", "enum": DREHUNG},
        "neigung": {"type": "string", "enum": NEIGUNG},
        "figur": BOX,
        "gesicht_sichtbar": {"type": "boolean"},
        "gesicht": BOX,
    },
    "required": ["brauchbar", "grund", "art", "personen", "geschlecht", "haarlaenge", "frisur",
                 "drehung", "neigung", "figur", "gesicht_sichtbar", "gesicht"],
}

PROMPT_1 = """Du sortierst Anime-Screenshots für eine Zeichenreferenz. Antworte nur mit JSON nach Schema.
Betrachte die größte, vorderste Figur.

brauchbar: true nur, wenn eine Anime-Figur deutlich und ausreichend groß zu sehen ist.
false bei: fast nur Hintergrund oder Landschaft, Figur winzig oder stark verdeckt, unscharf,
überwiegend Text, leeres oder einfarbiges Bild. grund: kurze Begründung in wenigen Wörtern.

""" + ANSICHT_TEXT + """

figur: Rahmen um die ganze Figur (Kopf mit allen Haaren und der sichtbare Körper).
gesicht: Rahmen um das Gesicht von Stirn bis Kinn (ohne Haare). Ist kein Gesicht zu sehen,
gesicht_sichtbar false und gesicht [0,0,0,0].

Rahmen als [x1, y1, x2, y2], normiert auf 0 bis 1000 (0,0 = links oben, 1000,1000 = rechts unten).
frisur: wenige Wörter, z. B. "Zopf", "kurz, wuschelig", "Pony, glatt"."""

MERKMALE = ["auge_links", "auge_rechts", "mund", "nase", "haare", "ohr"]
SCHEMA_2 = {
    "type": "object",
    "properties": {
        "drehung": {"type": "string", "enum": DREHUNG},
        "neigung": {"type": "string", "enum": NEIGUNG},
        "merkmale": {
            "type": "array",
            "items": {"type": "object",
                      "properties": {"typ": {"type": "string", "enum": MERKMALE}, "box": BOX},
                      "required": ["typ", "box"]},
        },
    },
    "required": ["drehung", "neigung", "merkmale"],
}

PROMPT_2 = """Das ist der vergrößerte Kopf einer Anime-Figur. Antworte nur mit JSON nach Schema.

""" + ANSICHT_TEXT + """

merkmale: Rahmen für jedes sichtbare Teil: auge_links (Auge auf der linken Bildseite), auge_rechts,
mund, nase, haare (die ganze Frisur), ohr. Nur aufführen, was wirklich zu sehen ist; bei Anime ist die
Nase oft nur ein kleiner Strich oder Punkt, auch den bitte einrahmen.
Rahmen als [x1, y1, x2, y2], normiert auf 0 bis 1000 bezogen auf DIESES Bild."""


def ollama(url, model, prompt, schema, img_bytes, timeout):
    body = {"model": model, "stream": False, "think": False, "format": schema, "options": {"temperature": 0},
            "messages": [{"role": "user", "content": prompt, "images": [base64.b64encode(img_bytes).decode()]}]}
    req = urllib.request.Request(url.rstrip("/") + "/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(json.load(r)["message"]["content"])


def jpeg(im, q=90):
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q); return buf.getvalue()


def valid(b):
    return isinstance(b, list) and len(b) == 4 and 0 <= b[0] < b[2] <= 1000 and 0 <= b[1] < b[3] <= 1000


def ansicht(s):
    """Drehung und Neigung aus einer Modellantwort, nur gültige Werte."""
    d, n = s.get("drehung"), s.get("neigung")
    return {"drehung": d if d in DREHUNG else None, "neigung": n if n in NEIGUNG else None}


def analyse(path, a):
    with Image.open(path) as raw:
        im = ImageOps.exif_transpose(raw).convert("RGB")
    im.thumbnail((a.max_side, a.max_side))
    if a.spiegeln:
        im = ImageOps.mirror(im)
    W, H = im.size
    std = ImageStat.Stat(im.convert("L").resize((64, 64))).stddev[0]
    res = {"bild": [W, H], "streuung": round(std, 1)}
    if std < a.min_std:
        res.update(brauchbar=False, grund="fast einfarbig (Streuung %.1f)" % std, merkmale=[])
        return res

    s1 = ollama(a.ollama, a.model, PROMPT_1, SCHEMA_1, jpeg(im), a.timeout)
    res.update({k: s1.get(k) for k in ["brauchbar", "grund", "art", "personen", "geschlecht", "haarlaenge", "frisur"]})
    res["figur_box"] = s1["figur"] if valid(s1.get("figur")) else None
    res["ansicht_ganz"] = ansicht(s1)
    res["ansicht"] = dict(res["ansicht_ganz"], quelle="ganz")
    merkmale = []
    g = s1.get("gesicht")
    if s1.get("gesicht_sichtbar") and valid(g):
        merkmale.append({"typ": "gesicht", "box": g})
        # Kopfausschnitt: Gesicht großzügig erweitern, nach oben mehr wegen der Haare
        gw, gh = g[2] - g[0], g[3] - g[1]
        cx1, cx2 = max(0, g[0] - gw * .8), min(1000, g[2] + gw * .8)
        cy1, cy2 = max(0, g[1] - gh * 1.1), min(1000, g[3] + gh * .5)
        crop = im.crop((round(cx1 / 1000 * W), round(cy1 / 1000 * H), round(cx2 / 1000 * W), round(cy2 / 1000 * H)))
        if min(crop.size) >= 32:
            if max(crop.size) < 768:  # kleine Köpfe vergrößern, damit das Modell Details erkennt
                f = 768 / max(crop.size); crop = crop.resize((round(crop.width * f), round(crop.height * f)), Image.LANCZOS)
            s2 = ollama(a.ollama, a.model, PROMPT_2, SCHEMA_2, jpeg(crop), a.timeout)
            res["ansicht_kopf"] = ansicht(s2)
            if res["ansicht_kopf"]["drehung"]:
                res["ansicht"] = dict(res["ansicht_kopf"], quelle="kopf")
            sx, sy = (cx2 - cx1) / 1000, (cy2 - cy1) / 1000
            for m in s2.get("merkmale") or []:
                b = m.get("box")
                if not valid(b): continue
                merkmale.append({"typ": m["typ"], "box": [round(cx1 + b[0] * sx), round(cy1 + b[1] * sy),
                                                         round(cx1 + b[2] * sx), round(cy1 + b[3] * sy)]})
            res["kopf_ausschnitt"] = [round(cx1), round(cy1), round(cx2), round(cy2)]
    res["merkmale"] = merkmale
    d, n = res["ansicht"]["drehung"], res["ansicht"]["neigung"]
    if d:  # Ableitung für ältere App-Versionen, keine Messung
        res["kopf"] = {"yaw": YAW[d], "pitch": PITCH.get(n, 0), "roll": 0, "quelle": "kategorie"}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", default="ergebnis.jsonl")
    ap.add_argument("--ollama", default="http://192.168.178.135:11434")
    ap.add_argument("--model", default="qwen3.5:9b")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-side", type=int, default=1280)
    ap.add_argument("--min-std", type=float, default=10.0, help="Unter dieser Helligkeitsstreuung gilt ein Bild als einfarbig")
    ap.add_argument("--spiegeln", action="store_true", help="Bilder waagerecht spiegeln (Gegenprobe für die Stabilität)")
    a = ap.parse_args()

    out = pathlib.Path(a.out); done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                if not r.get("fehler"): done.add(r["datei"])
            except Exception: pass
    bilder = sorted(p for p in pathlib.Path(a.dir).rglob("*")
                    if p.suffix.lower() in EXT and not p.name.startswith(".") and "_aussortiert" not in p.parts)
    if a.limit: bilder = bilder[:a.limit]
    offen = [p for p in bilder if str(p) not in done]
    print(f"{len(bilder)} Bilder, {len(offen)} offen, Modell {a.model}" + (", gespiegelt" if a.spiegeln else ""), file=sys.stderr)

    in_folge = 0
    with out.open("a", encoding="utf-8") as f:
        for i, p in enumerate(offen, 1):
            t0 = time.time(); rec = {"datei": str(p), "modell": a.model, "version": VERSION, "gespiegelt": a.spiegeln}
            try:
                rec.update(ergebnis=analyse(p, a), fehler=None)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, OSError) as e:
                rec.update(ergebnis=None, fehler=f"{type(e).__name__}: {e}")
            rec["sekunden"] = round(time.time() - t0, 1)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            e = rec["ergebnis"] or {}
            an = e.get("ansicht") or {}
            info = rec["fehler"] or (f"{'ok ' if e.get('brauchbar') else 'AUS'} {e.get('art')} "
                                     f"{an.get('drehung')}/{an.get('neigung')} "
                                     f"{[m['typ'] for m in e.get('merkmale', [])]} {e.get('grund') or ''}")
            print(f"[{i}/{len(offen)}] {p.name}: {rec['sekunden']} s, {info}", file=sys.stderr)
            in_folge = in_folge + 1 if (rec["fehler"] and "URLError" in rec["fehler"]) else 0
            if in_folge >= 3:
                print("Ollama dreimal nicht erreichbar, Abbruch. Neustart macht weiter.", file=sys.stderr); sys.exit(2)


if __name__ == "__main__":
    main()
