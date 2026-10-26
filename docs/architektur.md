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
