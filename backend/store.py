"""store.py — In-Memory-Datenhaltung.

Lädt die Datenwahrheit (data/truth.json) einmalig in den Speicher und indiziert
sie nach id. `_DATA` wird in-place aktualisiert, damit andere Module, die es
importiert haben, dieselbe Referenz behalten.
"""
import json

from config import TRUTH

_DATA = {"meta": {}, "records": [], "byId": {}}


def load():
    if not TRUTH.exists():
        raise RuntimeError("data/truth.json fehlt – erst truth.py laufen lassen.")
    d = json.loads(TRUTH.read_text(encoding="utf-8"))
    _DATA["meta"] = d["meta"]
    _DATA["records"] = d["records"]
    _DATA["byId"] = {r["id"]: r for r in d["records"]}
