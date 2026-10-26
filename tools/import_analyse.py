#!/usr/bin/env python3
"""Analyse-Ergebnisse an die Einträge der App-Sammlung hängen (Feld analyse), Zuordnung per Dateiname.

Ablauf (Claude führt die Datenbankschritte über das Artefakt-Datenbankwerkzeug aus):
1. Sammlung lesen: Collection "refs" mit out_dir in einen Ordner speichern (je Eintrag <id>.json)
   und die Versionsnummern aus der Liste als JSON ablegen: {"<id>": <version>, ...}
2. python3 import_analyse.py --in ergebnis3.jsonl --refs db/refs --versionen versionen.json --out import/
3. Die erzeugten batch_*.json als Schreibvorgänge "batch" ausführen (je höchstens 50 Einträge).

Jeder Eintrag wird vollständig geschrieben ("set"): alle Felder wie gelesen, nur analyse ersetzt.
So bleiben keine Felder einer älteren Analyse stehen. Gespiegelte Läufe werden abgelehnt.
Nur Standardbibliothek.
"""
import argparse, json, pathlib, sys

FELDER = ["brauchbar", "grund", "art", "personen", "geschlecht", "haarlaenge", "frisur", "figur_box",
          "ansicht", "ansicht_ganz", "ansicht_kopf", "kopf", "kopf_ausschnitt", "merkmale", "bild", "streuung"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--refs", required=True, help="Ordner mit den gelesenen Einträgen (<id>.json)")
    ap.add_argument("--versionen", required=True, help="JSON {id: version} aus der gelesenen Liste")
    ap.add_argument("--out", required=True)
    ap.add_argument("--collection", default="refs")
    a = ap.parse_args()

    ergebnisse = {}
    for z in pathlib.Path(a.inp).read_text(encoding="utf-8").splitlines():
        if not z.strip(): continue
        r = json.loads(z)
        if r.get("gespiegelt"):
            sys.exit(f"{r['datei']}: gespiegelter Lauf, nicht importieren (Rahmen wären seitenverkehrt).")
        if r.get("fehler") or not r.get("ergebnis"): continue
        e = r["ergebnis"]
        an = {k: e[k] for k in FELDER if k in e}
        an.update(modell=r.get("modell"), version=r.get("version"))
        ergebnisse[pathlib.Path(r["datei"]).name] = an  # spätere Zeilen gewinnen

    versionen = json.loads(pathlib.Path(a.versionen).read_text(encoding="utf-8"))
    out = pathlib.Path(a.out); (out / "docs").mkdir(parents=True, exist_ok=True)
    writes, ohne, gesehen = [], [], set()
    for p in sorted(pathlib.Path(a.refs).glob("*.json")):
        doc_id, doc = p.stem, json.loads(p.read_text(encoding="utf-8"))
        name = doc.get("name") or ""
        if name not in ergebnisse:
            ohne.append(name or f"({doc_id}, ohne Namen)"); continue
        if doc_id not in versionen:
            sys.exit(f"{doc_id}: keine Version bekannt, Liste neu lesen.")
        gesehen.add(name)
        doc["analyse"] = ergebnisse[name]
        ziel = out / "docs" / f"{doc_id}.json"
        ziel.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        writes.append({"op": "set", "collection": a.collection, "doc_id": doc_id,
                       "file_path": str(ziel.resolve()), "if_version": versionen[doc_id]})

    for i in range(0, len(writes), 50):
        (out / f"batch_{i // 50 + 1}.json").write_text(json.dumps(writes[i:i + 50], ensure_ascii=False, indent=1), encoding="utf-8")
    fehlend = sorted(set(ergebnisse) - gesehen)
    print(f"{len(writes)} Einträge vorbereitet in {(len(writes) + 49) // 50} Batch-Datei(en).")
    print(f"Ohne Ergebnis (bleiben unverändert): {len(ohne)}" + (": " + ", ".join(ohne) if ohne else ""))
    print(f"Ergebnisse ohne Eintrag in der App: {len(fehlend)}" + (": " + ", ".join(fehlend) if fehlend else ""))


if __name__ == "__main__":
    main()
