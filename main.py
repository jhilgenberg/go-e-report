"""
go-e Charger Auswertungstool für die Auswertung und Dokumentation von Ladevorgängen.
Ermöglicht die Erstellung detaillierter Monatsberichte für die Abrechnung.
"""

# Standard Library Imports
import os
import json
import time
import calendar
from datetime import datetime
from io import StringIO

# Third Party Imports
import requests
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import ttk, messagebox


class GoeChargerApp:
    """
    Hauptanwendungsklasse für das go-e Charger Auswertungstool.
    Verwaltet die GUI und Geschäftslogik der Anwendung.
    """

    def __init__(self, root):
        """Initialisiert die Anwendung.

        Args:
            root: Das Hauptfenster der Anwendung
        """
        self.root = root
        self.root.title("go-e Charger Auswertung")
        self.settings_file = "goe_charger_settings.json"
        self.settings = {}

        # Hauptframe mit Padding
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Style konfigurieren
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Section.TFrame', relief='groove', padding=5)
        
        # Menüleiste
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        # Einstellungen Menü
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Einstellungen", menu=settings_menu)
        settings_menu.add_command(label="Konfiguration", command=self.show_settings_dialog)
        
        # Zeitraum Frame
        time_frame = ttk.LabelFrame(main_frame, text="Zeitraum", padding="10")
        time_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Frame für Datum und Monatsauswahl
        date_frame = ttk.Frame(time_frame)
        date_frame.grid(row=0, column=0, columnspan=4, pady=2)
        
        # Monatsauswahl
        month_frame = ttk.Frame(time_frame)
        month_frame.grid(row=0, column=0, pady=5, padx=5)
        
        current_year = datetime.now().year
        years = list(range(current_year - 2, current_year + 1))
        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        
        ttk.Label(month_frame, text="Jahr:", style='Header.TLabel').grid(row=0, column=0, padx=5)
        self.selected_year = ttk.Combobox(month_frame, values=years, width=6)
        self.selected_year.set(current_year)
        self.selected_year.grid(row=0, column=1, padx=5)
        
        ttk.Label(month_frame, text="Monat:", style='Header.TLabel').grid(row=0, column=2, padx=5)
        self.selected_month = ttk.Combobox(month_frame, values=[m[1] for m in months], width=15)
        self.selected_month.set(calendar.month_name[datetime.now().month])
        self.selected_month.grid(row=0, column=3, padx=5)
        
        ttk.Button(month_frame, text="Monat setzen", 
                  command=self.set_month).grid(row=0, column=4, padx=10)
        
        # Datumsauswahl
        date_select_frame = ttk.Frame(time_frame)
        date_select_frame.grid(row=1, column=0, pady=10)
        
        ttk.Label(date_select_frame, text="Von:", style='Header.TLabel').grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(date_select_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='dd.mm.yyyy',  # Deutsches Datumsformat
                                  locale='de_DE')  # Deutsche Lokalisierung
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(date_select_frame, text="Bis:", style='Header.TLabel').grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(date_select_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='dd.mm.yyyy',  # Deutsches Datumsformat
                                locale='de_DE')  # Deutsche Lokalisierung
        self.end_date.grid(row=0, column=3, padx=5)
        
        # Strompreis als StringVar
        self.price = tk.StringVar(value="0.30")
        
        # Fortschrittsbalken
        self.progress_frame = ttk.LabelFrame(main_frame, text="Fortschritt", padding="10")
        self.progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress_bars = {}
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(button_frame, text="Bericht erstellen", 
                  command=self.generate_report).grid(row=0, column=0, padx=5)
        
        # Versteckte Einstellungen
        self.api_type = tk.StringVar()
        self.local_api_url = tk.StringVar()
        self.cloud_api_key = tk.StringVar()
        self.employee = tk.StringVar()
        self.license_plate = tk.StringVar()
        self.serial_number = tk.StringVar()
        
        # Einstellungen laden und ggf. Dialog zeigen
        if not os.path.exists(self.settings_file):
            self.root.after(100, self.show_settings_dialog)  # Dialog nach GUI-Initialisierung zeigen
        else:
            self.load_settings()

    def show_settings_dialog(self):
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Konfiguration")
        settings_dialog.grab_set()
        
        dialog_frame = ttk.Frame(settings_dialog, padding="20")
        dialog_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # API-Auswahl
        api_frame = ttk.LabelFrame(dialog_frame, text="API Konfiguration", padding="10")
        api_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.api_type = tk.StringVar(value=self.settings.get('api_type', 'local'))
        
        ttk.Radiobutton(api_frame, text="Lokale API", 
                        variable=self.api_type, 
                        value="local").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(api_frame, text="Cloud API", 
                        variable=self.api_type, 
                        value="cloud").grid(row=0, column=1, padx=5)
        
        # Lokale API Einstellungen
        local_frame = ttk.LabelFrame(dialog_frame, text="Lokale API Einstellungen", padding="10")
        local_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(local_frame, text="Lokale API-URL:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        local_api_entry = ttk.Entry(local_frame, width=40, textvariable=self.local_api_url)
        local_api_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5)
        
        # Cloud API Einstellungen
        cloud_frame = ttk.LabelFrame(dialog_frame, text="Cloud API Einstellungen", padding="10")
        cloud_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(cloud_frame, text="Seriennummer:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        serial_entry = ttk.Entry(cloud_frame, width=20, textvariable=self.serial_number)
        serial_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(cloud_frame, text="API Key:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W)
        cloud_api_entry = ttk.Entry(cloud_frame, width=40, textvariable=self.cloud_api_key)
        cloud_api_entry.grid(row=1, column=1, columnspan=2, pady=5, padx=5)
        
        # Kosten Frame hinzufügen
        cost_frame = ttk.LabelFrame(dialog_frame, text="Kosten", padding="10")
        cost_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(cost_frame, text="Strompreis (€/kWh):", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        price_entry = ttk.Entry(cost_frame, width=10, textvariable=self.price)
        price_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Mitarbeiter und Kennzeichen
        info_frame = ttk.LabelFrame(dialog_frame, text="Fahrzeug & Fahrer", padding="10")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Mitarbeiter in erste Zeile
        ttk.Label(info_frame, text="Mitarbeiter:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        employee_entry = ttk.Entry(info_frame, width=40, textvariable=self.employee)
        employee_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Kennzeichen in zweite Zeile
        ttk.Label(info_frame, text="Kennzeichen:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W)
        license_entry = ttk.Entry(info_frame, width=15, textvariable=self.license_plate)
        license_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Buttons ans Ende verschieben
        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="Speichern", 
                  command=lambda: self.save_settings_dialog(settings_dialog)).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Abbrechen", 
                  command=settings_dialog.destroy).grid(row=0, column=1, padx=5)

    def save_settings_dialog(self, dialog):
        self.save_settings()
        dialog.destroy()

    def set_month(self):
        try:
            year = int(self.selected_year.get())
            month = [i for i, name in enumerate(calendar.month_name) 
                    if name == self.selected_month.get()][0]
            
            # Ersten und letzten Tag des Monats ermitteln
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, calendar.monthrange(year, month)[1])
            
            # Datum setzen
            self.start_date.set_date(first_day)
            self.end_date.set_date(last_day)
        except (ValueError, IndexError) as e:
            messagebox.showerror("Fehler", "Ungültige Jahr/Monat Kombination")

    def save_settings(self):
        self.settings = {  # Aktualisiere self.settings
            'api_type': self.api_type.get(),
            'local_api_url': self.local_api_url.get(),
            'cloud_api_key': self.cloud_api_key.get(),
            'serial_number': self.serial_number.get(),
            'price': self.price.get(),
            'employee': self.employee.get(),
            'license_plate': self.license_plate.get()
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen: {str(e)}")

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                    self.api_type.set(self.settings.get('api_type', 'local'))
                    self.local_api_url.set(self.settings.get('local_api_url', ''))
                    self.cloud_api_key.set(self.settings.get('cloud_api_key', ''))
                    self.serial_number.set(self.settings.get('serial_number', ''))
                    self.price.set(self.settings.get('price', '0.30'))
                    self.employee.set(self.settings.get('employee', ''))
                    self.license_plate.set(self.settings.get('license_plate', ''))
            else:
                self.settings = {}
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Einstellungen: {str(e)}")
            self.settings = {}

    def update_progress_bars(self, progress_data):
        # Bestehende Fortschrittsbalken löschen
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        self.progress_bars.clear()
        
        # Neue Fortschrittsbalken erstellen
        for i, bar_data in enumerate(progress_data):
            label = ttk.Label(self.progress_frame, text=bar_data.get('name', ''))
            label.grid(row=i, column=0, padx=5)
            
            progress = ttk.Progressbar(self.progress_frame, length=200, mode='determinate')
            progress.grid(row=i, column=1, padx=5)
            progress['value'] = bar_data.get('progress', 0)
            
            self.progress_bars[bar_data.get('name', '')] = progress
        
        self.root.update()

    def fetch_charging_data(self, start_date, end_date):
        try:
            # Bestimme die Base URL und Headers basierend auf API-Typ
            base_url = ""
            headers = {}
            
            if self.api_type.get() == 'cloud':
                # Cloud API
                serial = self.serial_number.get()
                if not serial:
                    raise Exception("Seriennummer ist erforderlich für Cloud API")
                base_url = f"https://{serial}.api.v3.go-e.io"
                headers = {'Authorization': f'Bearer {self.cloud_api_key.get()}'}
            else:
                # Lokale API
                base_url = self.local_api_url.get()
                
            try:
                # Ersten API-Call um die DLL-URL zu bekommen
                dll_response = requests.get(f"{base_url}/api/status?filter=dll", headers=headers)
                if dll_response.status_code != 200:
                    if self.api_type.get() == 'local':
                        # Bei Fehler zur Cloud API wechseln
                        serial = self.serial_number.get()
                        if serial and self.cloud_api_key.get():
                            base_url = f"https://{serial}.api.v3.go-e.io"
                            headers = {'Authorization': f'Bearer {self.cloud_api_key.get()}'}
                            dll_response = requests.get(f"{base_url}/api/status?filter=dll", headers=headers)
                            if dll_response.status_code != 200:
                                raise Exception("Fehler beim Abrufen der DLL-URL (Lokale und Cloud API)")
                        else:
                            raise Exception("Fehler beim Abrufen der DLL-URL und keine Cloud API Konfiguration verfügbar")
                    else:
                        raise Exception("Fehler beim Abrufen der DLL-URL")
                
                dll_data = dll_response.json()
                export_url = dll_data.get('dll')
                if not export_url:
                    raise Exception("Keine DLL-URL in der Antwort gefunden")
                
                # Export-Parameter aus der URL extrahieren
                export_param = export_url.split('?e=')[1]
                
                # Ticket anfordern mit dem Export-Parameter
                ticket_response = requests.get(f"https://data.v3.go-e.io/api/v1/get_ticket?e={export_param}")
                if ticket_response.status_code != 200:
                    raise Exception("Fehler beim Abrufen des Tickets")
                
                ticket_data = ticket_response.json()
                ticket = ticket_data.get('ticket')
                if not ticket:
                    raise Exception("Kein Ticket in der Antwort gefunden")
                
                # Status-Abfrage in Schleife
                max_retries = 30
                retry_count = 0
                while retry_count < max_retries:
                    status_response = requests.get(f"https://data.v3.go-e.io/api/v1/get_status?ticket={ticket}")
                    if status_response.status_code != 200:
                        raise Exception("Fehler beim Abrufen des Status")
                        
                    status_data = status_response.json()
                    
                    # Fortschrittsbalken aktualisieren
                    if 'status' in status_data and 'progressBars' in status_data['status']:
                        self.update_progress_bars(status_data['status']['progressBars'])
                    
                    # Prüfen ob die Daten fertig sind
                    if status_data.get('status', {}).get('message') == "Task finished":
                        csv_data = status_data.get('status', {}).get('csv')
                        if csv_data:
                            # CSV-String in DataFrame umwandeln
                            df = pd.read_csv(StringIO(csv_data), sep=';', decimal=',')
                            
                            # Datum konvertieren und filtern
                            df['Start'] = pd.to_datetime(df['Start'], format='%d.%m.%Y %H:%M:%S')
                            df['Ende'] = pd.to_datetime(df['Ende'], format='%d.%m.%Y %H:%M:%S')
                            
                            mask = (df['Start'].dt.date >= start_date) & (df['Ende'].dt.date <= end_date)
                            filtered_df = df[mask]
                            
                            # Nur benötigte Spalten behalten und nach Datum gruppieren
                            result_df = filtered_df.groupby(df['Start'].dt.date)['Energie [kWh]'].sum().reset_index()
                            result_df.columns = ['Datum', 'Energie_kWh']
                            result_df['Datum'] = result_df['Datum'].astype(str)
                            
                            return result_df
                            
                    time.sleep(2)
                    retry_count += 1
                    
                raise Exception("Timeout beim Warten auf die Daten")
                
            except Exception as e:
                raise Exception(f"API Fehler: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Abrufen der Daten: {str(e)}")
            return None

    def parse_price(self, price_str):
        """Konvertiert einen Preis-String in Float, akzeptiert Komma und Punkt"""
        try:
            # Ersetze Komma durch Punkt und versuche zu konvertieren
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except (ValueError, AttributeError):
            messagebox.showerror("Fehler", "Ungültiger Strompreis. Bitte geben Sie eine Zahl ein (z.B. 0,30 oder 0.30)")
            return None

    def generate_pdf(self, df):
        try:
            price_per_kwh = self.parse_price(self.price.get())
            if price_per_kwh is None:
                return None
            
            class PDF(FPDF):
                def header(self):
                    self.set_font('Arial', 'B', 15)
                    self.cell(0, 8, 'go-e Charger Ladebericht', 0, 1, 'C')
                    self.line(10, 20, 200, 20)
                    self.ln(5)

                def footer(self):
                    self.set_y(-15)
                    self.set_font('Arial', 'I', 8)
                    self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')

            # PDF erstellen
            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Zeitraum
            pdf.set_font("Arial", 'B', 11)
            pdf.set_fill_color(240, 240, 240)
            zeitraum_text = f"Zeitraum: {self.start_date.get_date().strftime('%d.%m.%Y')} - {self.end_date.get_date().strftime('%d.%m.%Y')}"
            pdf.cell(0, 8, zeitraum_text, 0, 1, 'L', fill=True)
            
            # Mitarbeiter und Kennzeichen in einer Zeile
            if self.employee.get().strip() or self.license_plate.get().strip():
                pdf.set_font("Arial", 'B', 11)
                pdf.set_fill_color(240, 240, 240)
                
                if self.employee.get().strip() and self.license_plate.get().strip():
                    mitarbeiter_width = 130
                    kennzeichen_width = 60
                else:
                    mitarbeiter_width = 190
                    kennzeichen_width = 190
                
                if self.employee.get().strip():
                    pdf.cell(mitarbeiter_width, 8, f"Mitarbeiter: {self.employee.get()}", 0, 0, 'L', fill=True)
                
                if self.license_plate.get().strip():
                    if self.employee.get().strip():
                        pdf.cell(kennzeichen_width, 8, f"KFZ: {self.license_plate.get()}", 0, 1, 'L', fill=True)
                    else:
                        pdf.cell(kennzeichen_width, 8, f"KFZ: {self.license_plate.get()}", 0, 1, 'L', fill=True)
                else:
                    pdf.ln()
            
            pdf.ln(2)
            
            # Verbrauchsdiagramm erstellen
            plt.figure(figsize=(10, 4))
            dates = pd.to_datetime(df['Datum'])
            
            # Balkendiagramm statt Liniendiagramm
            plt.bar(dates, df['Energie_kWh'], width=0.8, color='#34495e', alpha=0.7)
            plt.grid(True, linestyle='--', alpha=0.3, axis='y')
            
            # Deutsche Formatierung
            plt.title('Stromverbrauch im Zeitverlauf')
            plt.xlabel('Datum')
            plt.ylabel('Verbrauch (kWh)')
            
            # Datumsformat auf Deutsch setzen
            date_formatter = DateFormatter('%d.%m.%Y')
            plt.gca().xaxis.set_major_formatter(date_formatter)
            plt.xticks(rotation=45, ha='right')
            
            # Layout optimieren
            plt.tight_layout()
            
            # Diagramm speichern
            chart_filename = 'temp_chart.png'
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Diagramm in PDF einfügen
            pdf.image(chart_filename, x=10, y=pdf.get_y(), w=190)
            
            # Temporäre Datei löschen
            try:
                os.remove(chart_filename)
            except:
                pass
            
            pdf.ln(100)  # Platz für das Diagramm
            
            # Tabellenkopf
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(52, 73, 94)
            pdf.set_text_color(255, 255, 255)
            
            # Angepasste Spaltenbreiten für volle Seitenbreite
            page_width = pdf.w - 20  # Seitenbreite minus Ränder
            date_width = page_width * 0.4
            energy_width = page_width * 0.3
            cost_width = page_width * 0.3
            
            # Tabelle zentrieren
            x_offset = 10  # Linker Rand
            
            pdf.set_x(x_offset)
            pdf.cell(date_width, 7, "Datum", 1, 0, 'C', fill=True)
            pdf.cell(energy_width, 7, "kWh", 1, 0, 'C', fill=True)
            pdf.cell(cost_width, 7, "EUR", 1, 1, 'C', fill=True)
            
            # Tabelleninhalt
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(0, 0, 0)
            
            total_energy = 0
            total_cost = 0
            
            row_colors = [(255, 255, 255), (245, 245, 245)]
            
            for i, (_, row) in enumerate(df.iterrows()):
                date_obj = datetime.strptime(row['Datum'], '%Y-%m-%d')
                date = date_obj.strftime('%d.%m.%Y')
                
                energy = row['Energie_kWh']
                cost = energy * price_per_kwh
                
                pdf.set_fill_color(*row_colors[i % 2])
                pdf.set_x(x_offset)
                
                pdf.cell(date_width, 7, date, 1, 0, 'C', fill=True)
                pdf.cell(energy_width, 7, f"{energy:.2f}", 1, 0, 'C', fill=True)
                pdf.cell(cost_width, 7, f"{cost:.2f}", 1, 1, 'C', fill=True)
                
                total_energy += energy
                total_cost += cost
            
            # Zusammenfassung
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(52, 73, 94)
            pdf.set_text_color(255, 255, 255)
            
            summary_label_width = page_width * 0.7
            summary_value_width = page_width * 0.3
            
            pdf.set_x(x_offset)
            pdf.cell(summary_label_width, 7, "Gesamtenergie:", 1, 0, 'L', fill=True)
            pdf.cell(summary_value_width, 7, f"{total_energy:.2f} kWh", 1, 1, 'R', fill=True)
            
            pdf.set_x(x_offset)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(summary_label_width, 7, "Strompreis pro kWh:", 1, 0, 'L', fill=True)
            pdf.cell(summary_value_width, 7, f"{price_per_kwh:.2f} EUR", 1, 1, 'R', fill=True)
            
            pdf.set_x(x_offset)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(summary_label_width, 7, "Gesamtkosten:", 1, 0, 'L', fill=True)
            pdf.cell(summary_value_width, 7, f"{total_cost:.2f} EUR", 1, 1, 'R', fill=True)
            
            # Erstellungsdatum
            pdf.ln(2)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 5, f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", 0, 1, 'R')
            
            filename = f"goe_charger_bericht_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            return filename
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der PDF-Erstellung: {str(e)}")
            return None

    def generate_report(self):
        try:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            
            if start_date > end_date:
                messagebox.showerror("Fehler", "Das Startdatum muss vor dem Enddatum liegen!")
                return
                
            df = self.fetch_charging_data(start_date, end_date)
            if df is not None:
                filename = self.generate_pdf(df)
                messagebox.showinfo("Erfolg", f"Bericht wurde erstellt: {filename}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Berichterstellung: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap('icon.ico')
    app = GoeChargerApp(root)
    root.mainloop() 