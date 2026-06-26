"""config.py — configuration & security.

A single place for: loading .env without an extra dependency, the team password,
shared constants and paths. Imported by all other backend modules as a
dependency-free leaf module (avoids cycles).
"""
import hmac
import os
from pathlib import Path

HERE = Path(__file__).parent
TRUTH = HERE / "data" / "truth.json"
FRONTEND = HERE.parent / "frontend"


def _load_dotenv(path):
    """Loads KEY=VALUE lines from backend/.env (without an extra dependency).
    Already-set real environment variables take precedence (setdefault)."""
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
# No default password: if QE_TEAM_PASSWORD is unset, TEAM_PW is empty and check_pw
# always fails (fail closed) — team features are disabled rather than guarded by a
# known default. Set the variable in .env (dev) or via -e (deploy) to enable them.
TEAM_PW = os.environ.get("QE_TEAM_PASSWORD", "").strip()

# "Spiders" that are NOT real content crawlers but WLO migration/import.
WLO_SPIDERS = {"wirlernenonline_spider", "wirlernenonline_gsheet_spider"}


def _auto_refresh_hour():
    """Local-time hour (0–23) for the optional nightly data refresh; None disables it.
    Configured via QE_AUTO_REFRESH_HOUR (e.g. "3"); invalid/unset means off."""
    raw = os.environ.get("QE_AUTO_REFRESH_HOUR", "").strip()
    return int(raw) if raw.isdigit() and 0 <= int(raw) <= 23 else None


AUTO_REFRESH_HOUR = _auto_refresh_hour()


def check_pw(pw: str | None, header_pw: str | None) -> bool:
    # Constant-time compare to avoid leaking the password via response timing.
    token = (pw or header_pw or "").strip()
    return bool(TEAM_PW) and hmac.compare_digest(token.encode("utf-8"), TEAM_PW.encode("utf-8"))
