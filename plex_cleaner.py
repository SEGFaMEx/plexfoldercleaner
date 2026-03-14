import os
import shutil
import time
import configparser
import logging
import threading
from datetime import datetime
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import sys
from logging.handlers import RotatingFileHandler

# Globale Variablen für die Steuerung
log_file = "cleaner.log"
stop_event = threading.Event()
pause_event = threading.Event() # Wenn gesetzt, wird gewartet
pause_event.set() # Standardmäßig NICHT pausiert (set() bedeutet "darf laufen")

# Setup Logging initial
def setup_logging():
    settings = load_config()
    enable_log = settings.getboolean('enable_log_file', True) if settings else True
    max_mb = float(settings.get('max_log_size_mb', 1.0)) if settings else 1.0
    
    # Bestehende Handler entfernen
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handlers = [logging.StreamHandler()]
    
    if enable_log:
        # backupCount=0 sorgt dafür, dass keine .1, .2 etc. Dateien erstellt werden.
        # Sobald maxBytes erreicht ist, wird die Datei überschrieben/geleert.
        handlers.append(RotatingFileHandler(log_file, maxBytes=int(max_mb * 1024 * 1024), backupCount=0, encoding='utf-8'))
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers
    )

setup_logging()

def create_default_config(path):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'folder1': 'C:\\Dein\\Plex\\Ordner1',
        'folder2': 'C:\\Dein\\Plex\\Ordner2',
        'min_video_size_gb': '1.0',
        'check_interval_minutes': '60',
        'video_extensions': '.mkv, .mp4, .avi, .mov, .wmv, .m4v',
        'dry_run': 'true',
        'enable_log_file': 'true',
        'max_log_size_mb': '1.0'
    }
    with open(path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    logging.info(f"Standard-Config erstellt: {path}")

def load_config():
    config = configparser.ConfigParser()
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(__file__)
        
    config_path = os.path.join(application_path, 'config.ini')
    
    if not os.path.exists(config_path):
        create_default_config(config_path)
    
    try:
        config.read(config_path, encoding='utf-8')
        return config['Settings']
    except Exception as e:
        logging.error(f"Fehler beim Laden der Config: {e}")
        return None

def has_large_video(folder_path, min_size_bytes, extensions):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext.strip().lower()) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size >= min_size_bytes:
                        return True, file, size
                except OSError:
                    pass
    return False, None, 0

def clean_directories():
    if not pause_event.is_set():
        logging.info("Scan pausiert.")
        return

    settings = load_config()
    if not settings:
        return

    folders_to_watch = [settings.get('folder1'), settings.get('folder2')]
    min_size_gb = float(settings.get('min_video_size_gb', 1.0))
    min_size_bytes = min_size_gb * (1024 ** 3)
    extensions = settings.get('video_extensions', '.mkv,.mp4').split(',')
    dry_run = settings.getboolean('dry_run', True)

    if dry_run:
        logging.info("--- DRY RUN MODUS ---")

    for root_folder in folders_to_watch:
        if not root_folder or not os.path.exists(root_folder):
            continue

        logging.info(f"Scanne: {root_folder}")
        try:
            subfolders = [f.path for f in os.scandir(root_folder) if f.is_dir()]
        except Exception:
            continue

        for subfolder in subfolders:
            if stop_event.is_set(): return # Schnellabbruch falls Programm beendet wird
            
            found, filename, size = has_large_video(subfolder, min_size_bytes, extensions)
            if found:
                logging.info(f"BEHALTEN: {os.path.basename(subfolder)} ({filename})")
            else:
                if dry_run:
                    logging.info(f"[DRY-RUN] LÖSCHEN: {os.path.basename(subfolder)}")
                else:
                    logging.info(f"LÖSCHE: {os.path.basename(subfolder)}")
                    try:
                        shutil.rmtree(subfolder)
                    except Exception as e:
                        logging.error(f"Fehler beim Löschen von {subfolder}: {e}")

def cleaner_loop():
    logging.info("Hintergrund-Thread gestartet.")
    while not stop_event.is_set():
        clean_directories()
        
        # Warte auf das Intervall, aber reagiere auf den stop_event
        settings = load_config()
        interval_min = int(settings.get('check_interval_minutes', 60)) if settings else 60
        logging.info(f"Scan fertig. Nächster Scan in {interval_min} Min.")
        
        # In kleinen Schritten schlafen, um schneller auf Exit zu reagieren
        for _ in range(interval_min * 60):
            if stop_event.is_set():
                break
            time.sleep(1)

# --- Tray Icon Funktionen ---

def create_image():
    # Einfaches Icon erstellen: Ein Kreis (Blau = Aktiv, Rot = Pausiert)
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    color = (0, 120, 215) if pause_event.is_set() else (200, 0, 0)
    dc.ellipse([10, 10, 54, 54], fill=color)
    return image

def on_quit(icon, item):
    logging.info("Beenden angefordert...")
    stop_event.set()
    icon.stop()

def on_pause(icon, item):
    if pause_event.is_set():
        pause_event.clear()
        logging.info("Pausiert.")
    else:
        pause_event.set()
        logging.info("Fortgesetzt.")
    icon.icon = create_image() # Icon Farbe aktualisieren

def on_reload(icon, item):
    logging.info("Konfiguration wird neu geladen...")
    setup_logging()
    logging.info("Logging-Einstellungen wurden aktualisiert.")

def setup_tray():
    menu = (
        item('Status: Pausieren/Fortsetzen', on_pause),
        item('Konfiguration neu laden', on_reload),
        item('Beenden', on_quit),
    )
    icon = pystray.Icon("PlexCleaner", create_image(), "Plex Cleaner", menu)
    icon.run()

if __name__ == "__main__":
    logging.info("Plex Folder Cleaner Tray-App startet.")
    
    # Cleaner in separatem Thread starten
    thread = threading.Thread(target=cleaner_loop, daemon=True)
    thread.start()
    
    # Tray Icon im Hauptthread starten (blockiert)
    setup_tray()
