#!/usr/bin/env python3
"""Testlauf: Bilder mit einem Vision-Modell über Ollama verschlagworten.

Nur Standardbibliothek, läuft auf Pi, Mac oder PC.

    python3 analyse_test.py --dir ./testbilder --out ergebnis.jsonl \
        --ollama http://192.168.178.134:11434 --model qwen3.5:9b

Je Bild eine JSON-Zeile mit Schlagworten, Kopfwinkel, Merkmal-Bereichen und Laufzeit.
Bereits ausgewertete Bilder werden übersprungen, ein Abbruch kostet also nichts.
"""
import argparse, base64, json, pathlib, sys, time, urllib.request, urllib.error

EXT = {".png", ".jpg", ".jpeg", ".webp"}
MERKMALE = ["gesicht", "auge_links", "auge_rechts", "mund", "nase", "haare", "ohr", "hand", "koerper"]

SCHEMA = {
    "type": "object",
    "properties": {
        "art": {"type": "string", "enum": ["kopf", "oberkoerper", "ganzkoerper", "sonstiges"]},
        "personen": {"type": "integer"},
        "geschlecht": {"type": "string", "enum": ["maennlich", "weiblich", "unklar"]},
        "haarlaenge": {"type": "string", "enum": ["kurz", "mittel", "lang", "unklar"]},
        "frisur": {"type": "string"},
        "kopf": {
            "type": "object",
            "properties": {
                "sichtbar": {"type": "boolean"},
                "yaw": {"type": "number"}, "pitch": {"type": "number"}, "roll": {"type": "number"},
                "sicherheit": {"type": "number"},
            },
            "required": ["sichtbar", "yaw", "pitch", "roll", "sicherheit"],
        },
        "merkmale": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "typ": {"type": "string", "enum": MERKMALE},
                    "box": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
                },
                "required": ["typ", "box"],
            },
        },
    },
    "required": ["art", "personen", "geschlecht", "haarlaenge", "frisur", "kopf", "merkmale"],
}

PROMPT = """Analysiere dieses Anime-Bild für eine Zeichenreferenz. Antworte nur mit JSON nach Schema.
Betrachte nur die größte, vorderste Figur.

Kopfwinkel in Grad, aus Sicht des Betrachters:
- yaw: 0 = Gesicht schaut frontal zum Betrachter. Positiv = Gesicht ist zur rechten Bildseite gedreht,
  negativ = zur linken Bildseite. +90 = Profil, Nase zeigt nach rechts. Bereich -180 bis 180.
- pitch: 0 = auf Augenhöhe. Positiv = Kopf nach unten geneigt, man sieht mehr vom Scheitel (Ansicht von oben).
  Negativ = Kopf nach oben geneigt, man sieht unter das Kinn (Ansicht von unten). Bereich -90 bis 90.
- roll: 0 = Kopf aufrecht. Positiv = Scheitel kippt zur linken Bildseite, negativ = zur rechten Bildseite.
- sicherheit: 0 bis 1, wie sicher du dir beim Winkel bist.

merkmale: Begrenzungsrahmen sichtbarer Teile als [x1, y1, x2, y2], normiert auf 0 bis 1000
(0,0 = links oben, 1000,1000 = rechts unten). auge_links ist das Auge auf der linken Bildseite.
Nur aufführen, was wirklich zu sehen ist.

frisur: wenige Wörter, z. B. "Zopf", "kurz, wuschelig", "Pony, glatt"."""


def call(ollama, model, img_b64, timeout):
    body = {
        "model": model, "stream": False, "think": False, "format": SCHEMA,
        "options": {"temperature": 0},
        "messages": [{"role": "user", "content": PROMPT, "images": [img_b64]}],
    }
    req = urllib.request.Request(ollama.rstrip("/") + "/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    return json.loads(d["message"]["content"]), d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", default="ergebnis.jsonl")
    ap.add_argument("--ollama", default="http://192.168.178.135:11434")
    ap.add_argument("--model", default="qwen3.5:9b")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            try: done.add(json.loads(line)["datei"])
            except Exception: pass

    bilder = sorted(p for p in pathlib.Path(a.dir).rglob("*") if p.suffix.lower() in EXT)
    if a.limit: bilder = bilder[:a.limit]
    offen = [p for p in bilder if str(p) not in done]
    print(f"{len(bilder)} Bilder, {len(offen)} offen, Modell {a.model}", file=sys.stderr)

    with out.open("a", encoding="utf-8") as f:
        for i, p in enumerate(offen, 1):
            t0 = time.time()
            rec = {"datei": str(p), "modell": a.model}
            try:
                res, raw = call(a.ollama, a.model, base64.b64encode(p.read_bytes()).decode(), a.timeout)
                rec.update(ergebnis=res, sekunden=round(time.time() - t0, 1),
                           tokens=raw.get("eval_count"), fehler=None)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as e:
                rec.update(ergebnis=None, sekunden=round(time.time() - t0, 1), fehler=f"{type(e).__name__}: {e}")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            k = (rec["ergebnis"] or {}).get("kopf") or {}
            print(f"[{i}/{len(offen)}] {p.name}: {rec['sekunden']} s, "
                  + (rec["fehler"] or f"yaw {k.get('yaw')} pitch {k.get('pitch')} roll {k.get('roll')}"), file=sys.stderr)


if __name__ == "__main__":
    main()
