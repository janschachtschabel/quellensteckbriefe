"""store.py — in-memory data storage.

Loads the data truth (data/truth.json) into memory once and indexes it by id.
`_DATA` is updated in place so that other modules that have imported it keep
the same reference.
"""
import json

from config import TRUTH

_DATA = {"meta": {}, "records": [], "byId": {}}


def load():
    if not TRUTH.exists():
        raise RuntimeError("data/truth.json fehlt – erst truth.py laufen lassen.")
    d = json.loads(TRUTH.read_text(encoding="utf-8"))
    records = d["records"]
    by_id = {r["id"]: r for r in records}     # build the index first (the slow part)
    # then swap the three keys back-to-back, index before records, so a concurrent
    # request never sees new records with a stale index (effectively atomic commit).
    _DATA["meta"] = d["meta"]
    _DATA["byId"] = by_id
    _DATA["records"] = records
