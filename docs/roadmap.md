# Roadmap

## Stufe 1: Zeichenhilfen ✔

- [x] Stil stufenlos realistisch ↔ Anime ↔ Chibi
- [x] Galerie „Beispiele zu dieser Drehung“
- [x] Übungsmodus mit Zufallswinkel und Zeitlimit
- [x] Kopf in der Box mit Fluchtlinien
- [x] Lichtrichtung, Cel-Schatten

## Stufe 2: 3D-Anime-Figuren als Beispiele

- [ ] Three.js auf aktuelle Version umstellen (ES-Module), Linien und Materialien portieren
- [ ] VRoid-Figuren (CC0) laden, im selben Winkel wie den Konstruktionskopf zeigen, umschaltbar männlich/weiblich
- [ ] Figur als eigene Ebene exportieren (PNG, transparent)

## Stufe 2b: Modell verfeinern

- [ ] Rumpf mit Schultern und Schlüsselbein, damit Kopfdrehung und Halsansatz zusammen sichtbar werden
- [ ] Eigene Proportionen als Figur-Profil speichern (Augenhöhe, Kinnlänge, Kieferbreite, Augengröße)

## Stufe 3: Pi und Bildanalyse

Siehe [architektur.md](architektur.md).

- [x] Test: 61 Bilder mit `qwen3.5:9b` ausgewertet (zwei Läufe, siehe Architektur)
- [ ] Eigene Bilder grob in Ansichten einsortieren statt Winkel schätzen
- [ ] Stack auf dem Pi: Ordner, SQLite, Vorschaubilder, Warteschlange, API (im Raspi-Projekt)
- [ ] App mit eigenem HTML-Rahmen vom Pi ausliefern, Speicheradapter für die Pi-API
- [ ] Merkmal-Beispiele: Augen, Münder, Nasen, Haare als Ausschnitte, kombinierbar mit dem Kopfwinkel
- [ ] Filter: Geschlecht, Haarlänge, Frisur
- [ ] Zurückgestellt: Kopfwinkel über Gesichtspunkte und `solvePnP`

## Stufe 4: Körper

- [ ] Körperbilder in der Sammlung, verschlagwortet (stehend, sitzend, Hände, Perspektive)
- [ ] Keine eigene 3D-Gliederpuppe: dafür gibt es ausgereifte Apps (z. B. Magic Poser)
