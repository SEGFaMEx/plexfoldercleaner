# PlexFolderCleaner 🎬

Ein intelligentes Hintergrund-Tool zur automatischen Bereinigung von Plex-Medienordnern. Es sorgt dafür, dass deine Mediathek sauber bleibt, indem es Ordner ohne relevante Videoinhalte automatisch entfernt.

## 🚀 Features

- **Hintergrundbetrieb**: Läuft unauffällig in der Windows Taskleiste (System Tray).
- **Intelligente Analyse**: Durchsucht Unterordner rekursiv nach Videodateien.
- **Größenschwellenwert**: Löscht Ordner nur, wenn keine Videodatei über einer definierten Größe (z.B. 200MB oder 1GB) gefunden wurde.
- **System Tray Integration**:
  - **Blaues Icon**: Programm aktiv und scannt.
  - **Rotes Icon**: Programm pausiert.
  - **Menü**: Pause/Fortsetzen, Konfiguration live neu laden, Beenden.
- **Sicherheitsmodus (Dry-Run)**: Teste das Tool gefahrlos – es zeigt im Log an, was gelöscht würde, ohne echten Datenverlust.
- **Auto-Config**: Erstellt beim ersten Start automatisch eine `config.ini`, falls diese fehlt.
- **Detailliertes Logging**: Alle Aktionen werden in der `cleaner.log` festgehalten.

## 🛠️ Installation & Setup

### Option 1: Als .exe (Empfohlen)
1. Lade dir die `PlexCleaner.exe` herunter (oder baue sie selbst, siehe unten).
2. Starte die Datei. Beim ersten Start wird eine `config.ini` im selben Ordner erstellt.
3. Öffne die `config.ini` und trage deine Pfade ein (z.B. `folder1 = F:\Filme`).
4. Setze `dry_run = false`, sobald du sicher bist, dass die richtigen Ordner erkannt werden.

### Option 2: Als Python-Skript
1. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```
2. Starte das Skript:
   ```bash
   python plex_cleaner.py
   ```

## ⚙️ Konfiguration (config.ini)

Die Einstellungen können jederzeit in der `config.ini` angepasst werden:

```ini
[Settings]
folder1 = F:\Filme           # Erster zu überwachender Ordner
folder2 = F:\Serien          # Zweiter zu überwachender Ordner
min_video_size_gb = 0.2      # Mindestgröße (hier 200MB)
check_interval_minutes = 60  # Scan-Intervall
dry_run = true               # Sicherheitsmodus (true = kein Löschen)
enable_log_file = true       # Log-Datei schreiben (true/false)
max_log_size_mb = 1.0        # Max. Größe der Logdatei (einzelne Datei)
```

## 📦 Build Instructions (.exe erstellen)

Falls du die `.exe` selbst erstellen möchtest:
1. Starte die `build_exe.bat`.
2. Das Tool nutzt `PyInstaller`, um eine einzelne, konsolenlose Datei im Ordner `dist/` zu erstellen.

## 💡 Tipp: Autostart
Um das Tool bei jedem Windows-Start automatisch zu laden:
1. Drücke `Win + R`.
2. Gib `shell:startup` ein.
3. Erstelle eine Verknüpfung der `PlexCleaner.exe` in diesem Ordner.

---
*Erstellt für eine saubere Plex-Erfahrung. Nutze den Dry-Run Modus mit Bedacht!*
