#!/bin/bash

# Prüfe, ob .env bereits existiert
if [ -f "../.env" ]; then
    echo "Warnung: .env existiert bereits. Möchten Sie sie überschreiben? (j/n)"
    read -r answer
    if [ "$answer" != "j" ]; then
        echo "Abgebrochen."
        exit 1
    fi
fi

# Kopiere .env.example zu .env
cp env.example ../.env

echo "Neue .env-Datei wurde erstellt. Bitte passen Sie die Werte an."
echo "Wichtige Schritte:"
echo "1. Setzen Sie Ihre API-Keys für Vast.ai und RunPod"
echo "2. Konfigurieren Sie die LLM-API-Keys nach Bedarf"
echo "3. Passen Sie die Batch-Einstellungen an" 