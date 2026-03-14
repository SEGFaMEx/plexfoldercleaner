@echo off
echo Installiere Abhaengigkeiten...
pip install -r requirements.txt

echo Baue die Executable...
pyinstaller --noconsole --onefile --name "PlexCleaner" --icon=NONE plex_cleaner.py

echo.
echo Fertig! Die Datei befindet sich im 'dist' Ordner.
echo Kopiere die 'config.ini' in den 'dist' Ordner bevor du die .exe startest.
pause
