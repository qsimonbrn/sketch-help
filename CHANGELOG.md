# Changelog

Versionsnummern entsprechen den Veröffentlichungen des Artefakts.

## Unveröffentlicht

- **Analyse Version 4** (`tools/analyse.py`): grobe Ansichten statt Winkeln, Drehung (frontal, ¾ links/rechts,
  Profil links/rechts, hinten) und Neigung (oben, Augenhöhe, unten). `kopf` nur noch aus der Kategorie
  abgeleitet, damit v0.11 weiter sortiert. Option `--spiegeln` für den Gegenlauf
- **Analyse Version 5:** Drehrichtung aus den Rahmen (Nasenlage, Augengrößen) statt aus dem Modellwort,
  das in Testlauf 3 fast nur „rechts“ kannte; `--nachberechnen` ohne neuen Modelllauf
- `tools/vergleich.py` (Stabilität), `tools/import_analyse.py` (Import per Dateiname statt von Hand)

## v0.11 (26.10.2026)

- **Filter** für Beispiele und Merkmal-Ausschnitte: Geschlecht (weiblich/männlich) und Haarlänge (kurz/mittel/lang)
- **3D-Figur:** Mimik (fröhlich, wütend, traurig, entspannt, überrascht, Augen zu) und Blickrichtung
- **3D-Figur als Linienzeichnung** (Kantenfilter über Tiefe, Flächenrichtung und Helligkeit), auch im PNG-Export.
  Bekannt: feine Punktlinien entlang einzelner Haarsträhnen
- **Lieblings-Posen:** Drehung, Stil und Augen mit Namen merken (im Artefakt geräteübergreifend gespeichert)
- Testbilder bereinigt: 21 von 61 entfernt (14 unbrauchbar, 7 Duplikate), auf dem Pi und in der App

## v0.10

- Bilder aussortieren und zurückholen; Aussortiertes erscheint nicht als Beispiel
- `tools/analyse.py`: zweistufige Analyse (Figur-Rahmen, „brauchbar“, Merkmale im vergrößerten Kopf)

## v0.9

- 3D-Figur standardmäßig aus, Umschalter in der Winkelanzeige, wird erst beim Einschalten geladen
- Beispielbild unten rechts

## v0.8

- Merkmal-Ausschnitte (Augen, Mund, Nase, Haare, Gesicht) nach Kopfdrehung sortiert

## v0.7

- App speichert Dateinamen, zeigt Analyse-Schlagworte und Winkelvorschlag

## v0.6

- Augenformen (Oval, Anime, Rund, Mandel, Tsurime, Tareme, Schmal), Iris

## v0.5

- Umstieg auf Three.js 0.185, 3D-Anime-Figur (VRM) im selben Winkel: daneben, darunter, allein

## v0.4

- Stil-Regler rastet bei Anime ein, Augen anpassbar (Abstand, Größe, Höhe)

## v0.3

- Umbenennung in Sketch Help

## v0.2

- Stil stufenlos realistisch ↔ Anime ↔ Chibi, Beispiel-Galerie, Übungsmodus, Kopf in der Box, Cel-Schatten

## v0.1

- Drehbarer Konstruktionskopf mit Hilfslinien, PNG-Export, Bildsammlung mit Winkelabgleich
