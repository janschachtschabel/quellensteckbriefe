"""config.py — Konfiguration & Sicherheit.

Eine Stelle fuer: .env-Laden ohne Zusatz-Abhaengigkeit, Team-Passwort,
gemeinsame Konstanten und Pfade. Wird von allen anderen Backend-Modulen als
abhaengigkeitsfreies Blatt-Modul importiert (vermeidet Zyklen).
"""
import os
from pathlib import Path

HERE = Path(__file__).parent
TRUTH = HERE / "data" / "truth.json"
FRONTEND = HERE.parent / "frontend"


def _load_dotenv(path):
    """Lädt KEY=VALUE-Zeilen aus backend/.env (ohne Zusatz-Abhängigkeit).
    Bereits gesetzte echte Umgebungsvariablen haben Vorrang (setdefault)."""
    try:
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass


_load_dotenv(HERE / ".env")
TEAM_PW = os.environ.get("QE_TEAM_PASSWORD", "wlo-intern").strip()

# „Spider", die KEINE echten Inhalts-Crawler sind, sondern WLO-Migration/Import.
WLO_SPIDERS = {"wirlernenonline_spider", "wirlernenonline_gsheet_spider"}


def check_pw(pw: str | None, header_pw: str | None) -> bool:
    token = (pw or header_pw or "").strip()
    return bool(TEAM_PW) and token == TEAM_PW
