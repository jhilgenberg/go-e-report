# go-e Charger Auswertungstool
![image](https://i.imgur.com/RlLaqX8.png)

Ein benutzerfreundliches Tool zur Auswertung und Dokumentation von Ladevorgängen an go-e Wallboxen. Das Tool ermöglicht die Erstellung detaillierter Monatsberichte für die Abrechnung von Dienstwagenladungen.

## Features

- 📊 Automatische Datenabfrage über die go-e Charger API (lokal oder cloud-basiert)
- 📅 Flexible Zeitraumauswahl (Tages- und Monatsansicht)
- 📈 Visualisierung der Ladedaten mit übersichtlichen Diagrammen
- 💰 Automatische Kostenberechnung basierend auf kWh-Preis
- 📄 Professionelle PDF-Berichterstellung
- 🚗 Verwaltung von Mitarbeiter- und Fahrzeugdaten
- 💾 Speicherung von Einstellungen für wiederkehrende Nutzung

## Installation

#### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

#### API-Aktivierung in der go-e Wallbox
⚠️ **Wichtig**: Bevor Sie das Tool nutzen können, muss die API in Ihrer go-e Wallbox aktiviert werden:

1. Öffnen Sie die go-e Charger App
2. Navigieren Sie zu: Einstellungen → Verbindung → API Einstellungen
3. Hier können Sie wählen zwischen:
   - **Lokale HTTP API**: Für die Nutzung im lokalen Netzwerk
   - **Cloud API**: Für die Nutzung über das Internet
   
   Sie können auch beide APIs aktivieren, das Tool wird dann automatisch zur Cloud API wechseln, falls die lokale API nicht erreichbar ist.

4. Für die Cloud API:
   - Erstellen Sie einen API-Schlüssel im selben Menü
   - Notieren Sie sich die Seriennummer Ihres Geräts (zu finden unter: Einstellungen → Über → Hardwareinformationen)

Bei der ersten Ausführung werden Sie nach den grundlegenden Einstellungen gefragt:
- Für lokale API:
  - IP-Adresse der Wallbox (Base URL der API, z.B. http://192.168.1.100)
- Für Cloud API:
  - Seriennummer des Geräts
  - API-Schlüssel
- Allgemein:
  - Strompreis pro kWh

Diese Einstellungen werden gespeichert und können später in den Programmeinstellungen angepasst werden.

#### Installationsschritte

1. Laden Sie das Repository herunter:
```bash
git clone https://github.com/jhilgenberg/go-e-report.git
cd go-e-report
```

2. Installieren Sie die erforderlichen Abhängigkeiten:
```bash
pip install -r requirements.txt
```

3. Starten Sie das Programm:
```bash
python main.py
```