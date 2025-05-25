# backend/Dockerfile

# -----------------------------------------------------------------------------
# Basis-Image: schlankes Python 3.11
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# -----------------------------------------------------------------------------
# Arbeitsverzeichnis im Container
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# 1. Kopiere die Liste aller Python-Abhängigkeiten
# -----------------------------------------------------------------------------
COPY requirements.txt .

# -----------------------------------------------------------------------------
# 2. Installiere alle Abhängigkeiten ohne Cache, um das Image klein zu halten
# -----------------------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# 3. Kopiere den gesamten Anwendungs-Code
# -----------------------------------------------------------------------------
COPY app ./app

# -----------------------------------------------------------------------------
# 4. Öffne den Port, auf dem Uvicorn später lauscht
# -----------------------------------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------------------------------
# 5. Standard-Kommando: Starte Uvicorn mit Reload (für Entwicklungszwecke)
# -----------------------------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#Startet den ASGI-Server Uvicorn auf 0.0.0.0:8000.
#--reload lädt Codeänderungen automatisch nach
#(praktisch in der Entwicklung; im Produktivbetrieb weglassen). FIXIT