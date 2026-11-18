# Event- & Punkte-Dashboard (Demo)

Demo-Dashboard mit fiktiver Datenbank zur Auswertung von Events und Workshops inkl. PDF-Berichten.

## Start

```bash
pip install flask reportlab
python seed_db.py      # erzeugt demo.db (10 Unternehmen, 15 Events, Buchungen)
python app.py          # startet den Server auf http://127.0.0.1:5000
```

Dann im Browser öffnen: http://127.0.0.1:5000

## Datenmodell (SQLite: `demo.db`)

- **companies** — fiktive Unternehmen mit Punktekontingent (200 Punkte)
- **events** — Events & Workshops (z. B. „Workshop Führung im Wandel", „Seminar Verhandlungstraining"), jeweils mit gastgebendem Unternehmen (`host_company_id`) und Punktekosten
- **bookings** — Teilnahmen eines Unternehmens an einem Event; beim gastgebenden Event nehmen zusätzlich Unternehmen als Gäste teil

## Dashboard-Funktionen

- Übersicht aller Unternehmen mit Punktekontingent-Fortschrittsbalken
- Unternehmens-Auswahl per Dropdown oder Freitext-Filter (Unternehmen / Branche)
- Je Unternehmen: Workshops (gehostet + als Gast), Punkte verbraucht / übrig, Events insgesamt, Rolle als Gastgeber
- Tabelle „Gebuchte Events & Workshops" inkl. anderer teilnehmender Unternehmen
- Abschnitt „Teilnahme an Events anderer Unternehmen"
- PDF-Export: Bericht je Unternehmen (`/pdf/company/<id>`) und Gesamtauswertung (`/pdf/overview`)

## Design

Look nach dem Vorbild von proutatwork.de: weißer Grund, kräftiges Magenta (`#ec058c`) als Akzentfarbe, Schwarz/Grau-Typo, zarte Rosa-Akzente (`#faaca8`). Nur das Erscheinungsbild wurde angelehnt — keine Texte oder Logos der Stiftung übernommen.

Alle Daten sind frei erfunden.
