# Sketch Help

Drehbarer Konstruktionskopf als Perspektivhilfe fürs Zeichnen. Der Kopf wird gedreht,
geneigt und gekippt, mit Hilfslinien nach der Loomis-Methode (Mittellinie, Augen-, Brauen-,
Nasen- und Mundlinie, Seitenkreis, Kiefer) und als PNG mit transparentem Hintergrund
exportiert, um ihn in Procreate als Ebene einzufügen.

Dazu kommt eine Sammlung eigener Anime-Screenshots: Zu jedem Bild ist der Kopfwinkel
gespeichert, und die App zeigt zur aktuellen Drehung die ähnlichsten Beispiele, auch
gespiegelt.

## Stand

| Bereich | Stand |
|---|---|
| Kopfmodell | Stil stufenlos realistisch ↔ Anime ↔ Chibi (rastet bei Anime ein), Augen einstellbar |
| Hilfslinien | Achsen, Gesichtslinien, Seitenkreis, Gitter, verdeckte Linien gestrichelt, Box mit Fluchtlinien |
| Schattierung | aus, weich, Cel (zweistufig), Lichtrichtung einstellbar |
| Export | PNG nur Linien oder mit Fläche, transparenter Hintergrund |
| Beispiele | Upload, Winkel per Overlay zuordnen, Abgleich inkl. Spiegelung, Galerie |
| Übung | Zufallswinkel, Zeitlimit, Auflösen |
| Anime-Figur | 3D-Figur (VRM) im selben Winkel: daneben, darunter oder allein; Mimik, Blick, Linienzeichnung; eigene VRM ladbar |
| Beispiele | Eigene Bilder mit Analyse (Schlagworte, Ausschnitte für Augen/Mund/Nase/Haare), Filter Geschlecht/Haarlänge |
| Posen | Lieblings-Posen mit Namen speichern |
| Technik | Three.js 0.185 (ES-Module), `@pixiv/three-vrm` 3.5.5, per jsDelivr |
| Laufzeit | Claude-Artefakt (Speicher: Artefakt-Assets und -Datenbank) |

## Aufbau

```
app/index.html     Die App in einer Datei (Three.js r128 per CDN)
TODO.md            Offene Aufgaben, nach Reihenfolge
CHANGELOG.md       Änderungen je Version
docs/roadmap.md    Geplante Ausbaustufen
docs/architektur.md  Zielbild mit Raspberry Pi und Bildanalyse auf dem PC
tools/analyse.py       Bildanalyse per Ollama: brauchbar, Schlagworte, Ansicht (Drehung/Neigung), Rahmen
tools/vergleich.py     Stabilität: zwei Läufe vergleichen (auch gegen einen gespiegelten Lauf)
tools/import_analyse.py  Analyse per Dateiname an die Einträge der App hängen
tools/analyse_test.py  Alter Testlauf (Lauf 1 und 2), nur noch zum Nachvollziehen
tools/box_report.py    Prüfbericht: erkannte Bildbereiche als Rahmen über den Bildern
```

`app/index.html` ist derzeit als Artefakt-Seite geschrieben: Der Rahmen (`<!doctype>`,
`<head>`, `<body>`) wird vom Artefakt ergänzt. Für den Betrieb auf dem Pi bekommt die
Datei einen eigenen Rahmen (siehe Roadmap, Stufe 3).

## Figur und Lizenz

Die eingebaute Figur ist `VRM1_Constraint_Twist_Sample.vrm` aus dem Repository
[pixiv/three-vrm](https://github.com/pixiv/three-vrm), © pixiv Inc., VRM Public License 1.0
(laut eingebetteten Metadaten: Weitergabe und Veränderung erlaubt, kein Namensvermerk nötig).
Sie liegt nicht im Repo (`*.vrm` ist ausgeschlossen), sondern im Artefakt als Base64-Text
(`figur/pixiv-sample.vrm.txt`), weil Artefakte keine `.vrm`-Dateien ausliefern.

## Lokal testen

Die Seite braucht einen HTTP-Server (ES-Module), z. B. `python3 -m http.server` im Ordner `app/`.
Den Platzhalter `__VRM_URL__` in `app/index.html` beim Veröffentlichen durch den Pfad zur Figur ersetzen,
`__VRM_B64__` durch `true` (Base64-Text) oder `false` (rohe .vrm).
