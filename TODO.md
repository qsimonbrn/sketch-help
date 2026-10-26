# TODO

Stand: 26.10.2026, 02:35. Reihenfolge = Vorschlag für die nächsten Sitzungen.
Hintergrund und Messwerte stehen in [docs/architektur.md](docs/architektur.md), der Plan in [docs/roadmap.md](docs/roadmap.md).

## 1. Version 5 auf dem iPad prüfen

Version 5 (Three.js 0.185, Anime-Figur) ist nur lokal mit denselben Bibliotheksversionen getestet,
nicht im echten Artefakt.

- [ ] Seite lädt (Import-Map, Module von jsDelivr)
- [ ] Figur erscheint (14 MB Base64-Text, Ladezeit auf dem iPad?)
- [ ] Modi Daneben / Darunter / Allein, Halsschnitt
- [ ] PNG-Export in allen Modi
- [ ] Bildsammlung und Overlay funktionieren weiter
- [ ] Gespeicherte Einstellungen bleiben erhalten

Falls etwas kaputt ist: Version 4 (Three.js r128) liegt im Verlauf, Commit `426583e`.

## 2. VRoid-CC0-Figuren einbinden

Zwei Quellen nennen sie CC0 ([OpenGameArt](https://opengameart.org/content/vroid-studio-cc0-models),
Mitsua-Datensatz). Gilt nur für AvatarSample D–G, HairSample männlich/weiblich, Basismodelle,
Sakurada Fumiriya, Sendagaya Shino.

- [ ] Lizenz an der offiziellen VRoid-Hilfeseite bestätigen
- [ ] Dateien beschaffen (aus Claudes Umgebung nicht erreichbar; Simon lädt sie herunter)
- [ ] Figurenauswahl in der App, Filter männlich/weiblich
- [ ] Ablage: Artefakt als Base64-Text (max. 16 MB pro Datei) oder auf dem Pi

VRoid-Modelle sind VRM 0.x; `VRMUtils.rotateVRM0` ist schon eingebaut.

## 3. Eigene Bilder grob einsortieren

Testbilder in der App prüfen: Simon lädt die 61 Bilder aus `usb-share/sketch-help/test` in der App hoch
(die App speichert seit Version 7 den Dateinamen). Danach hängt Claude die Analyse aus `ergebnis2.jsonl`
per Dateiname an die Einträge (Feld `analyse`), Simon prüft Schlagworte und Vorschlag in der App.

- [x] 61 Testbilder in der App hochgeladen (Simon)
- [x] Analyse importiert (61 Einträge, Feld `analyse`; 2 ältere Einträge ohne Namen bleiben ohne Analyse)
- [x] Merkmal-Ausschnitte in der App (Augen, Mund, Nase, Haare, Gesicht), sortiert nach Abweichung zur Drehung
- [ ] Rahmen für Mund, Nase, Haare verbessern: zweistufige Analyse (erst Gesicht, dann Teile im Gesichtsausschnitt)
- [ ] Import als Skript ins Repo (`tools/import_analyse.py`), statt von Hand

Testläufe zeigen: `qwen3.5:9b` schätzt keine brauchbaren Winkel. Entscheidung: nur grobe Ansichten.

- [ ] Schema auf Kategorien umstellen: Drehung (frontal, ¾ links/rechts, Profil links/rechts, von hinten),
      Neigung (von oben, Augenhöhe, von unten), Art, Geschlecht, Haarlänge, Frisur
- [ ] Testlauf über die 61 Testbilder; Simon prüft den Bericht
- [ ] Stabilität messen: zwei Läufe, wie oft gleiche Kategorie?
- [ ] App: Beispiele nach Kategorie der aktuellen Drehung zeigen

Laufzeit mit Vorverarbeitung ca. 5 s pro Bild, 2000 Bilder ≈ 3 h.

## 4. Hosting auf dem Pi (im Raspi-Projekt umsetzen)

- [ ] Docker-Stack: App ausliefern, API, SQLite, Vorschaubilder, Warteschlange
- [ ] Bildordner `/mnt/usb-hdd/sketch-help/bilder` (Samsung 870 QVO SSD, Freigabe `usb-share`)
- [ ] Worker schickt Bilder an Ollama auf dem PC (192.168.178.135), wartet, wenn der PC aus ist
- [ ] App mit eigenem HTML-Rahmen, Speicheradapter für die Pi-API
- [ ] Figuren (.vrm) vom Pi ausliefern statt Base64 im Artefakt
- [ ] Zugriff unterwegs über Tailscale

Bekannt: Pi 4B hat nur ca. 1 GB RAM frei. Dateien im Ordner gehören `simon`, schreiben als `sudo -u simon`.

## 5. Modell verfeinern

- [ ] Rumpf mit Schultern und Schlüsselbein am Konstruktionskopf
- [ ] Eigene Proportionen als Profil speichern (Kinnlänge, Kieferbreite; Augen-Regler gibt es schon)
- [x] Augenformen: Oval, Anime, Rund, Mandel, Tsurime, Tareme, Schmal; Iris optional
- [ ] Augenformen an echten Bildern prüfen und nachschärfen (Lidfalte, Wimpernlinie?)
- [ ] Anime-Augen: Standard wurde nach einem Vergleichsbild nach außen verschoben (`eyeX` 0,46), mit weiteren Bildern prüfen

## Simon (offen)

- [ ] PC in der Fritzbox auf 192.168.178.135 reservieren
- [x] `bericht2.html` geprüft: deutlich besser als Lauf 1, sieht gut aus (Bericht in Safari öffnen, die Vorschau lädt keine Bilder)

## Aufräumen auf dem Pi

Testdateien in `/mnt/usb-hdd/sketch-help/`: `test/` (61 Bilder), `tools/`, `.venv/` (47 MB),
`ergebnis*.jsonl`, `bericht*.html`. Bleiben vorerst für weitere Testläufe.
