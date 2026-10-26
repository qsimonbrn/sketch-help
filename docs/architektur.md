# Architektur: Zielbild mit Raspberry Pi und PC

Stand: 26.10.2026. Entwurf, noch nicht umgesetzt.

## Rollen

| Gerät | Aufgabe | Begründung |
|---|---|---|
| Raspberry Pi 4B (192.168.178.80) | Bildordner, Datenbank, Warteschlange, App ausliefern | Läuft dauerhaft; gemessen: 3,7 GB RAM (gut 1 GB frei), 559 GB frei auf `/mnt/usb-hdd`, Samba-Freigabe `usb-share` vorhanden, Tailscale aktiv |
| PC mit Ollama | Bildanalyse mit lokalem Vision-Modell | Ein Vision-Modell passt nicht in den freien Speicher des Pi und wäre dort für ca. 2000 Bilder viel zu langsam |
| iPad / Mac | App im Browser | Zu Hause über das Heimnetz, unterwegs über Tailscale |

## Ablauf

1. Bilder landen per Samba in einem Ordner auf der USB-Platte, als Unterordner der bestehenden Freigabe `usb-share`: `/mnt/usb-hdd/sketch-help/bilder/` (die Platte ist die Samsung 870 QVO SSD, der Pfadname ist historisch).
2. Ein Dienst auf dem Pi bemerkt neue Dateien, legt Vorschaubilder an (Pillow) und trägt sie
   mit Status „neu“ in SQLite ein.
3. Ein Worker auf dem Pi schickt neue Bilder an Ollama auf dem PC, sobald der PC erreichbar ist.
   Ist der PC aus, bleibt die Warteschlange stehen und läuft beim nächsten Mal weiter.
4. Das Modell liefert strukturiertes JSON (Ollama `format` mit JSON-Schema):
   Art (Kopf/Körper), Geschlecht, Haarlänge, Frisur, sichtbare Merkmale mit Bildbereich
   (Augen, Mund, Nase, Haare, Gesicht), grober Kopfwinkel.
5. Die App liest alles über eine kleine HTTP-API vom Pi. Korrekturen in der App
   (Winkel, Bereiche, Schlagworte) werden als „manuell“ markiert und von späteren
   Analyseläufen nicht überschrieben.

## Datenmodell (Entwurf)

```
bild      id, pfad, sha256, breite, hoehe, art, geschlecht, haarlaenge, frisur,
          yaw, pitch, roll, winkel_quelle (auto|manuell), status, analysiert_am, modell
merkmal   id, bild_id, typ (auge_l|auge_r|mund|nase|haare|gesicht|hand|…),
          x, y, w, h (relativ 0..1), quelle (auto|manuell)
schlagwort  bild_id, wort
```

Bildbereiche werden relativ gespeichert, Ausschnitte rendert die App aus dem Original.
Es entstehen keine Kopien.

## Kopfwinkel: zwei Stufen

| Stufe | Verfahren | Erwartung |
|---|---|---|
| 1 | Vision-Modell schätzt den Winkel direkt | Grob; Genauigkeit unbekannt, muss an 20 bis 50 Bildern gemessen werden |
| 2 | Anime-Gesichtspunkte erkennen und mit `solvePnP` an die Punkte des 3D-Modells der App anpassen | Vermutlich genauer, da rechnerisch an dasselbe Modell gebunden; Trefferquote bei Profil und starker Neigung unbekannt |

Stufe 2 nur, wenn Stufe 1 nicht reicht.

## Offene Punkte

- PC: Ollama 0.40.11 auf 192.168.178.135 (per DHCP, Adresse wechselt; im Router reservieren). Modell `qwen3.5:9b` (9,7B, Q4_K_M) hat die Fähigkeit „vision“, geprüft über `/api/show`.
- Ollama ist im Heimnetz ohne Anmeldung erreichbar. Unkritisch, solange der Port nicht
  nach außen freigegeben wird.
- Umsetzung auf dem Pi gehört ins Raspi-Projekt (neuer Stack, Doku, `pi-guard.sh`).
- Mit dem Umzug ersetzt die Pi-API den Artefakt-Speicher. Die Speicherschicht der App ist
  bereits austauschbar angelegt (Cloud-, Lokal-Adapter); ein Pi-Adapter kommt dazu.

## Testlauf 1 (26.10.2026, 61 Bilder, `qwen3.5:9b`)

| Messung | Ergebnis | Bewertung |
|---|---|---|
| Laufzeit | 8,6 s pro Bild (erstes Bild 40 s, Modell laden) | 2000 Bilder ≈ 4,5 h, als Nachtlauf tragbar |
| Bildformat | 5712×4284 px, 52 von 61 mit EXIF-Drehung 6 (90°) | Das Modell bekommt die Rohpixel, also seitlich liegende Bilder. Vorverarbeitung nötig: EXIF anwenden, auf ca. 1280 px verkleinern |
| Kopfwinkel | Stark gerastert: Drehung fast nur −45/−15/−10/−5/±90, Sicherheit fast immer 0,9 | Keine echte Schätzung, eher Kategorien; Sicherheitswert ohne Aussage |
| Bildbereiche | 98 Rahmen, davon 61× `auge_links`, 36× `auge_rechts`, 1× Mund; kein Gesicht, keine Haare | Für automatisches Zuschneiden so unbrauchbar |
| Schlagworte | Art, Geschlecht, Haarlänge, Frisur plausibel verteilt | Noch nicht gegen Handwerte geprüft |

Folgerungen: erst Vorverarbeitung, dann zweiter Lauf. Für Rahmen und Winkel einen spezialisierten
Anime-Gesichtsdetektor mit Gesichtspunkten prüfen (Rahmen für Gesicht, Augen, Mund direkt aus den Punkten,
Winkel per `solvePnP`), das Vision-Modell nur noch für Schlagworte nutzen.

## Testlauf 2 (mit Vorverarbeitung, 1280 px, EXIF angewendet)

| Messung | Ergebnis |
|---|---|
| Laufzeit | 5,1 s pro Bild (Lauf 1: 8,6 s) |
| Kopfwinkel | Weiter gerastert; 35 von 61 Bildern mit Drehung 0° oder −5°. Abweichung zu Lauf 1 im Median 15°, maximal 175° |
| Bildbereiche | Mehr Arten (Mund 11, Nase 7, Gesicht 5, Haare 2), aber weiter lückenhaft |
| Stabilität | Geschlecht in 50/61, Haarlänge in 42/61 Fällen gleich wie in Lauf 1 |

**Sichtprüfung durch Simon (26.10.2026):** Bericht 2 „sieht echt gut aus, deutlich besser als der erste“
(Schlagworte und Rahmen). Die Vorverarbeitung (EXIF, 1280 px) war der entscheidende Schritt.

## Entscheidung (26.10.2026)

- **Exakte Winkelbeispiele** kommen aus 3D-Anime-Figuren des VRoid-Projekts, die laut zwei unabhängigen
  Quellen (OpenGameArt, Mitsua-Datensatz) unter CC0 stehen: AvatarSample D–G, HairSample männlich/weiblich,
  Basismodelle, Sakurada Fumiriya, Sendagaya Shino. Die App rendert sie im selben Winkel wie den Konstruktionskopf.
  Voraussetzung: Umstieg von Three.js r128 auf eine aktuelle Version mit `@pixiv/three-vrm`.
- **Eigene Bilder** werden nur grob in Ansichten einsortiert (z. B. „¾ links, von unten“), keine Winkelschätzung.
- Handwerte und Gesichtsdetektor sind zurückgestellt.
