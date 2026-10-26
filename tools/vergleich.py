#!/usr/bin/env python3
"""Stabilität der Analyse: zwei Läufe über dieselben Bilder vergleichen.

    python3 vergleich.py ergebnis3.jsonl ergebnis3_spiegel.jsonl

Ist einer der Läufe mit --spiegeln entstanden, wird dessen Drehung zurückgespiegelt
(¾ rechts ↔ ¾ links, Profil rechts ↔ links), bevor verglichen wird.
Zusätzlich je Lauf: Verteilung der Drehungen und Übereinstimmung Stufe 1 (ganzes Bild)
gegen Stufe 2 (Kopfausschnitt). Nur Standardbibliothek.
"""
import collections, json, pathlib, sys

SPIEGEL = {"dreiviertel_links": "dreiviertel_rechts", "dreiviertel_rechts": "dreiviertel_links",
           "profil_links": "profil_rechts", "profil_rechts": "profil_links"}
FELDER = ["brauchbar", "art", "geschlecht", "haarlaenge"]


def laden(pfad):
    lauf = {}
    for z in pathlib.Path(pfad).read_text(encoding="utf-8").splitlines():
        if not z.strip(): continue
        r = json.loads(z)
        if r.get("fehler") or not r.get("ergebnis"): continue
        lauf[pathlib.Path(r["datei"]).name] = r
    return lauf


def drehung(r, feld="ansicht"):
    d = ((r["ergebnis"].get(feld) or {}).get("drehung"))
    return SPIEGEL.get(d, d) if r.get("gespiegelt") else d


def quote(n, m):
    return f"{n}/{m} ({100 * n / m:.0f} %)" if m else "–"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    A, B = laden(sys.argv[1]), laden(sys.argv[2])
    gemeinsam = sorted(set(A) & set(B))
    print(f"Lauf A: {len(A)} Bilder, Lauf B: {len(B)} Bilder, gemeinsam {len(gemeinsam)}\n")

    for name, lauf in (("A", A), ("B", B)):
        vert = collections.Counter(drehung(r) for r in lauf.values() if r["ergebnis"].get("brauchbar"))
        print(f"Drehungen in {name} (nur brauchbare, gespiegelte zurückgerechnet):",
              ", ".join(f"{k} {v}" for k, v in vert.most_common()))
        beide = [r for r in lauf.values() if (r["ergebnis"].get("ansicht_kopf") or {}).get("drehung")]
        gleich = sum(drehung(r, "ansicht_ganz") == drehung(r, "ansicht_kopf") for r in beide)
        print(f"  Stufe 1 und Stufe 2 einig über die Drehung: {quote(gleich, len(beide))}")
    print()

    print("Übereinstimmung A gegen B:")
    abw = []
    nur_brauchbar = [n for n in gemeinsam if A[n]["ergebnis"].get("brauchbar") and B[n]["ergebnis"].get("brauchbar")]
    for feld in FELDER:
        menge = gemeinsam if feld == "brauchbar" else nur_brauchbar
        g = sum(A[n]["ergebnis"].get(feld) == B[n]["ergebnis"].get(feld) for n in menge)
        print(f"  {feld:<11} {quote(g, len(menge))}")
    for feld, f in (("drehung", lambda r: drehung(r)), ("neigung", lambda r: (r["ergebnis"].get("ansicht") or {}).get("neigung"))):
        g = 0
        for n in nur_brauchbar:
            a, b = f(A[n]), f(B[n])
            if a == b: g += 1
            else: abw.append((n, feld, a, b))
        print(f"  {feld:<11} {quote(g, len(nur_brauchbar))}")

    if abw:
        print("\nAbweichungen bei Drehung und Neigung (Bild, Feld, A, B):")
        for n, feld, a, b in abw:
            print(f"  {n}  {feld}: {a} / {b}")


if __name__ == "__main__":
    main()
