# WLO Quellenerschliessung — Serving-Container (API + Frontend in einem Image).
#
# Das Image serviert den mitgelieferten Datensnapshot (backend/data/truth.json)
# samt Frontend. Der Live-Refresh (/jobs/refresh) holt die Facetten/Quelldatensätze
# erneut von der öffentlichen WLO-API und baut truth.json im (ephemeren) Container-
# Dateisystem neu — dafür sind die kuratierten CSVs unter backend/data/inputs/
# eingebettet, sodass Crawler-Profile und Blacklist erhalten bleiben.
FROM python:3.12-slim

# Nicht-root-Benutzer; /app gehört ihm, damit der Refresh-Job seine Caches
# (ROOT/quellen-analyse/raw == /app/quellen-analyse/raw) anlegen kann.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app/quellenerschliessung-app/backend

# Abhängigkeiten zuerst — eigener Layer für besseren Build-Cache.
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App-Code, Datensnapshot und Frontend.
COPY backend/ /app/quellenerschliessung-app/backend/
COPY frontend/ /app/quellenerschliessung-app/frontend/

RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1
# QE_TEAM_PASSWORD bewusst NICHT gesetzt (kein Secret im Image) — zur Laufzeit
# via `-e QE_TEAM_PASSWORD=…` übergeben. Ohne diese Variable sind die Team-Funktionen
# deaktiviert (fail closed; es gibt KEIN Default-Passwort).
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/stats', timeout=3)"

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
