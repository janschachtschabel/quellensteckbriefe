"""refresh.py — Live-Daten-Refresh als Hintergrund-Job.

Oeffentlich zugaenglich (kein Team-Login): aktualisiert nur den Snapshot aus der
oeffentlichen WLO-API, baut die Datenwahrheit neu und laedt sie in den Speicher.
Ein Concurrency-Guard (Lock) verhindert parallele Laeufe.
"""
import threading
import time

import fetcher
import store
import truth

_JOB = {"status": "idle", "percent": 0, "message": "", "error": None,
        "startedAt": None, "finishedAt": None, "meta": None}
_JOB_LOCK = threading.Lock()


def _run_refresh():
    try:
        _JOB.update(status="running", percent=0, message="Start …", error=None,
                    startedAt=time.strftime("%Y-%m-%d %H:%M:%S"), finishedAt=None)
        fetcher.refresh_all(lambda p, m: _JOB.update(percent=int(p), message=m))
        _JOB.update(percent=96, message="Datenwahrheit neu bauen …")
        meta = truth.main()                 # baut data/truth.json
        store.load()                        # in-memory neu laden
        _JOB.update(status="done", percent=100, message="Fertig.",
                    meta=meta, finishedAt=time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:                   # noqa: BLE001
        _JOB.update(status="error", error=str(e), message=f"Fehler: {e}",
                    finishedAt=time.strftime("%Y-%m-%d %H:%M:%S"))


def start():
    # Concurrency-Guard: wiederholte Klicks während eines Laufs sind No-Ops.
    with _JOB_LOCK:
        if _JOB["status"] == "running":
            return {"status": "running", "percent": _JOB["percent"], "message": _JOB["message"]}
        _JOB.update(status="running", percent=0, message="Start …", error=None,
                    startedAt=time.strftime("%Y-%m-%d %H:%M:%S"))
    threading.Thread(target=_run_refresh, daemon=True).start()
    return {"status": "started"}


def status():
    return _JOB
