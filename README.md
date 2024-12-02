# go-e Charger Auswertungstool
![image](https://i.imgur.com/RlLaqX8.png)

Ein benutzerfreundliches Tool zur Auswertung und Dokumentation von Ladevorgängen an go-e Wallboxen. Das Tool ermöglicht die Erstellung detaillierter Monatsberichte für die Abrechnung von Dienstwagenladungen.

## Features

- 📊 Automatische Datenabfrage über die go-e Charger API
- 📅 Flexible Zeitraumauswahl (Tages- und Monatsansicht)
- 📈 Visualisierung der Ladedaten mit übersichtlichen Diagrammen
- 💰 Automatische Kostenberechnung basierend auf kWh-Preis
- 📄 Professionelle PDF-Berichterstellung
- 🚗 Verwaltung von Mitarbeiter- und Fahrzeugdaten
- 💾 Speicherung von Einstellungen für wiederkehrende Nutzung

## Installation

### API-Aktivierung in der go-e Wallbox

⚠️ **Wichtig**: Bevor Sie das Tool nutzen können, muss die lokale HTTP-API in Ihrer go-e Wallbox aktiviert werden:
1. Öffnen Sie die go-e Charger App
2. Navigieren Sie zu: Einstellungen → Verbindung → API Einstellungen
3. Aktivieren Sie die "Lokale HTTP API"

Bei der ersten Ausführung werden Sie nach den grundlegenden Einstellungen gefragt, wie:
- IP-Adresse der Wallbox (Base URL der API bspw. http://192.168.1.100)
- Strompreis pro kWh

Diese Einstellungen werden gespeichert und können später in den Programmeinstellungen angepasst werden.

### Option 1: Ausführbare Datei (Empfohlen)

1. Laden Sie die neueste Version der EXE-Datei aus dem [Release-Bereich](https://github.com/jhilgenberg/go-e-report/releases) herunter
2. Führen Sie die heruntergeladene EXE-Datei aus
3. Folgen Sie den Anweisungen zur Erstkonfiguration

### Option 2: Installation über Python

#### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

#### Installationsschritte

1. Laden Sie das Repository herunter:
```bash
git clone https://github.com/jhilgenberg/go-e-report.git
cd goe-charger-tool
```

2. Installieren Sie die erforderlichen Abhängigkeiten:
```bash
pip install -r requirements.txt
```

3. Starten Sie das Programm:
```bash
python main.py
```