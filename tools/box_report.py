#!/usr/bin/env python3
"""Prüfbericht zum Testlauf: legt die erkannten Bildbereiche als Rahmen über die Bilder.

    python3 box_report.py --in ergebnis.jsonl --out bericht.html

Erzeugt eine HTML-Datei neben den Bildern (relative Pfade), die per Samba im Browser
geöffnet werden kann. Nur Standardbibliothek.
"""
import argparse, html, json, os, pathlib

FARBE = {"gesicht": "#2b7bbe", "auge_links": "#cf3f37", "auge_rechts": "#cf3f37", "mund": "#d98a00",
         "nase": "#7a4cc2", "haare": "#1f9e6e", "ohr": "#a0522d", "hand": "#c2185b", "koerper": "#607d8b"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="ergebnis.jsonl")
    ap.add_argument("--out", default="bericht.html")
    a = ap.parse_args()
    out = pathlib.Path(a.out).resolve()
    rows = [json.loads(l) for l in pathlib.Path(a.inp).read_text(encoding="utf-8").splitlines() if l.strip()]

    karten = []
    for r in rows:
        src = html.escape(os.path.relpath(pathlib.Path(r["datei"]).resolve(), out.parent))
        e = r.get("ergebnis") or {}
        k = e.get("kopf") or {}
        boxen = []
        for m in e.get("merkmale") or []:
            b = m.get("box") or []
            if len(b) != 4: continue
            x1, y1, x2, y2 = [max(0, min(1000, v)) / 10 for v in b]
            c = FARBE.get(m.get("typ"), "#000")
            boxen.append(f'<div class="b" style="left:{x1}%;top:{y1}%;width:{max(0, x2 - x1)}%;height:{max(0, y2 - y1)}%;border-color:{c}">'
                         f'<span style="background:{c}">{html.escape(str(m.get("typ")))}</span></div>')
        info = html.escape(r["fehler"]) if r.get("fehler") else (
            f'{e.get("art")} · {e.get("geschlecht")} · Haare {e.get("haarlaenge")} ({html.escape(str(e.get("frisur")))})<br>'
            f'Kopf: Drehung {k.get("yaw")}° · Neigung {k.get("pitch")}° · Kippung {k.get("roll")}° · Sicherheit {k.get("sicherheit")}<br>'
            f'{r.get("sekunden")} s')
        karten.append(f'<figure><div class="pic"><img src="{src}" alt="">{"".join(boxen)}</div>'
                      f'<figcaption><b>{html.escape(pathlib.Path(r["datei"]).name)}</b><br>{info}</figcaption></figure>')

    sek = [r["sekunden"] for r in rows if not r.get("fehler")]
    kopf = f'{len(rows)} Bilder, {len(rows) - len(sek)} Fehler, Ø {sum(sek) / max(1, len(sek)):.1f} s pro Bild'
    out.write_text(f"""<!doctype html><meta charset="utf-8"><title>Prüfbericht Bildanalyse</title>
<style>body{{font:14px system-ui,sans-serif;margin:16px;background:#f3f5f7;color:#1b252e}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
figure{{margin:0;background:#fff;border:1px solid #ccd6de;border-radius:8px;padding:8px}}
.pic{{position:relative;display:inline-block;max-width:100%}} .pic img{{display:block;max-width:100%}}
.b{{position:absolute;border:2px solid;box-sizing:border-box}} .b span{{position:absolute;left:-2px;top:-18px;color:#fff;font-size:11px;padding:1px 4px;white-space:nowrap}}
figcaption{{font-size:12px;color:#5a6a77;padding-top:6px}}</style>
<h1>Prüfbericht Bildanalyse</h1><p>{kopf}</p><main>{"".join(karten)}</main>""", encoding="utf-8")
    print(f"{out}: {kopf}")


if __name__ == "__main__":
    main()
