# Kopfdreher

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
| Kopfmodell | Stil stufenlos realistisch ↔ Anime ↔ Chibi, Hals, Nase, Augen, Ohren |
| Hilfslinien | Achsen, Gesichtslinien, Seitenkreis, Gitter, verdeckte Linien gestrichelt, Box mit Fluchtlinien |
| Schattierung | aus, weich, Cel (zweistufig), Lichtrichtung einstellbar |
| Export | PNG nur Linien oder mit Fläche, transparenter Hintergrund |
| Beispiele | Upload, Winkel per Overlay zuordnen, Abgleich inkl. Spiegelung, Galerie |
| Übung | Zufallswinkel, Zeitlimit, Auflösen |
| Laufzeit | Claude-Artefakt (Speicher: Artefakt-Assets und -Datenbank) |

## Aufbau

```
app/index.html     Die App in einer Datei (Three.js r128 per CDN)
docs/roadmap.md    Geplante Ausbaustufen
docs/architektur.md  Zielbild mit Raspberry Pi und Bildanalyse auf dem PC
```

`app/index.html` ist derzeit als Artefakt-Seite geschrieben: Der Rahmen (`<!doctype>`,
`<head>`, `<body>`) wird vom Artefakt ergänzt. Für den Betrieb auf dem Pi bekommt die
Datei einen eigenen Rahmen (siehe Roadmap, Stufe 3).
