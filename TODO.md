# TODO

Stand: 26.10.2026, v0.12, Analyseskript Version 5. Reihenfolge = Vorschlag für die nächsten Sitzungen.
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

- [x] Lizenz offiziell bestätigt (vroid.pixiv.help, Artikel 4402614652569): CC0 sind HairSample_Male, HairSample_Female,
      β AvatarSample_1–4. AvatarSample_A–C haben eigene Bedingungen. D–G, Sakurada, Sendagaya nennt nur OpenGameArt CC0
- [x] HairSample_Female/_Male über den Pi geladen (`sketch-help/figuren/`), in v0.12 eingebaut (zwei Base64-Teile je Figur)
- [ ] Weitere Figuren nur, wenn ihre Lizenz offiziell belegt ist (β AvatarSample_1–4: Download-Quelle suchen)
- [x] Danbooru-Knopf als Ergänzung (nur Link, nichts gespeichert); Simon prüft auf dem iPad, ob die Seite aufgeht

VRoid-Modelle sind VRM 0.x; `VRMUtils.rotateVRM0` ist schon eingebaut.

## 3. Eigene Bilder grob einsortieren

Testbilder in der App prüfen: Simon hat die damals 61 Bilder aus `usb-share/sketch-help/test` in der App hochgeladen
(die App speichert seit Version 7 den Dateinamen). Danach hat Claude die Analyse aus `ergebnis2.jsonl`
per Dateiname an die Einträge gehängt (Feld `analyse`), Simon prüft Schlagworte und Vorschlag in der App.

- [x] 61 Testbilder in der App hochgeladen (Simon)
- [x] Analyse importiert (61 Einträge, Feld `analyse`; 2 ältere Einträge ohne Namen bleiben ohne Analyse)
- [x] Merkmal-Ausschnitte in der App (Augen, Mund, Nase, Haare, Gesicht), sortiert nach Abweichung zur Drehung
- [x] Testbilder sortiert (Kontaktbogen, Sichtprüfung): 14 unbrauchbar, 7 Duplikate nach `test/_aussortiert/` verschoben, in der App ausgeblendet
- [x] Aussortierte endgültig gelöscht (Pi-Ordner und App)
- [x] `tools/analyse.py` auf grobe Ansichten umgestellt (Version 4, Probelauf mit Ersatzserver); `kopf` wird nur noch aus der Kategorie abgeleitet
- [x] Import als Skript (`tools/import_analyse.py`), Stabilitätsvergleich (`tools/vergleich.py`)
- [x] Lauf 3 über die 40 Bilder und Gegenlauf gespiegelt (26.10.2026), Ergebnis in [docs/architektur.md](docs/architektur.md#testlauf-3-26102026-40-bilder-analyse-version-4-kategorien-statt-winkel):
      Seitenwort des Modells unbrauchbar (nie „links“), Rahmen spiegeln korrekt
- [x] Drehrichtung aus den Rahmen ableiten (Version 5, `--nachberechnen`); Schwelle 0,15 per Kontaktbogen geprüft
- [ ] Grenzfälle „leicht gedreht“: Schwelle ggf. nachschärfen, wenn die App-Beispiele danebenliegen
- [x] Ergebnis importiert (26.10.2026, `ergebnis3_rahmen.jsonl`, 40 Einträge per `import_analyse.py`, gegengelesen);
      Rückweg: `ergebnis2.jsonl` liegt noch auf dem Pi
- [x] Vorzeichen yaw ↔ 3D-Kopf geprüft (−40° blickt wie „¾ links“)
- [ ] „Vorschlag übernehmen“ reagiert bei Simon nicht (26.10.2026); im Nachbau mit echten Daten funktioniert er (+30° → −45°).
      Ursache offen. Danach „Kopf auf diesen Winkel“ mit Analyse-Vorschlag als Rückfall zusammenlegen
- [ ] IMG_0480 (Augen-Nahaufnahme) in der App aussortieren; „brauchbar“ des Modells hat sie durchgelassen
- [ ] App: Bilder auf den Figur-Rahmen zugeschnitten anzeigen (Sammlung, Overlay, Beispiele)
- [ ] Duplikaterkennung verbessern: dHash war unzuverlässig (0483/0484 als ähnlich gemeldet, sind verschiedene Figuren)

Testläufe zeigen: `qwen3.5:9b` schätzt keine brauchbaren Winkel. Entscheidung: nur grobe Ansichten.

- [x] Schema auf Kategorien umstellen: Drehung (frontal, ¾ links/rechts, Profil links/rechts, hinten),
      Neigung (oben, Augenhöhe, unten); in Stufe 1 und Stufe 2, Stufe 2 hat Vorrang
- Stabilität: Zwei gleiche Läufe sagen bei Temperatur 0 nichts aus. Stattdessen Gegenlauf mit gespiegelten
  Bildern (Drehung muss sich umkehren, der Rest gleich bleiben) und Stufe 1 gegen Stufe 2.
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

- [ ] Linienzeichnung der Figur: Punktlinien entlang der Haarsträhnen reduzieren (z. B. Kanten nur aus Tiefe für Haar-Materialien)

- [ ] Rumpf mit Schultern und Schlüsselbein am Konstruktionskopf
- [ ] Eigene Proportionen als Profil speichern (Kinnlänge, Kieferbreite; Augen-Regler gibt es schon)
- [x] Augenformen: Oval, Anime, Rund, Mandel, Tsurime, Tareme, Schmal; Iris optional
- [ ] Augenformen an echten Bildern prüfen und nachschärfen (Lidfalte, Wimpernlinie?)
- [ ] Anime-Augen: Standard wurde nach einem Vergleichsbild nach außen verschoben (`eyeX` 0,46), mit weiteren Bildern prüfen

## 6. Wünsche (Simon, 26.10.2026)

### Hair Generator
- [ ] Haare als eigene Ebene auf dem Konstruktionskopf: Grundform (Haarkappe) plus Strähnen
- [ ] Regler für Haarlänge (kurz bis sehr lang), Pony-Länge, Volumen
- [ ] Frisur-Vorlagen (z. B. kurz/wuschelig, Pony glatt, Zopf, Pferdeschwanz, Twin Tails), dreht perspektivisch mit
- [ ] Optional: passende Haar-Ausschnitte aus der eigenen Sammlung zur gewählten Länge zeigen (Filter Haarlänge gibt es schon)

### Beispielkopf männlich/weiblich
- [ ] Umschalter männlich/weiblich für den Konstruktionskopf (kombinierbar mit dem Stil-Regler realistisch/Anime/Chibi)
- [ ] Unterschiede u. a.: Kiefer breiter und kantiger, Kinn breiter, Hals dicker, Augen schmaler und tiefer, Brauen tiefer und gerader
- [ ] Gesichtsmerkmale einzeln verändern: Kieferbreite, Kinnlänge und -breite, Wangen, Nasengröße und -länge, Mundbreite, Brauenhöhe
  (Augen-Regler gibt es schon; zusammen mit Figur-Profilen aus Punkt 5 speichern)

## Simon (offen)

- [ ] PC in der Fritzbox auf 192.168.178.135 reservieren
- [x] `bericht2.html` geprüft: deutlich besser als Lauf 1, sieht gut aus (Bericht in Safari öffnen, die Vorschau lädt keine Bilder)

## Aufräumen auf dem Pi

Testdateien in `/mnt/usb-hdd/sketch-help/`: `test/` (40 Bilder), `tools/`, `.venv/` (47 MB),
`ergebnis*.jsonl`, `bericht*.html`. Bleiben vorerst für weitere Testläufe.
