"""app.py — Quellenerschliessungs-API (Web-Layer).

Duenne FastAPI-Routen ueber die Datenwahrheit (data/truth.json). Die eigentliche
Logik liegt in den Fachmodulen:
  config     Konfiguration, Team-Passwort, Konstanten, Pfade
  store      In-Memory-Datenhaltung (truth.json)
  views      Public/Internal-Serialisierung (server-seitige Trennung)
  filtering  Filterlogik der Quellenliste
  stats      Statistik-Aggregation
  refresh    Live-Daten-Refresh (Hintergrund-Job)

Sicherheit: OEFFENTLICHE Endpoints geben NIE die internen Felder aus. Interne
Felder (Entwicklervermerke, genauer Status) nur mit korrektem Team-Passwort
(Env QE_TEAM_PASSWORD, Default 'wlo-intern').

Endpoints:
  GET  /api/stats
  GET  /api/sources            (Liste, gefiltert, public)
  GET  /api/sources/{id}       (Detail; mit ?pw=/Header inkl. intern)
  GET  /api/meta/filters       (Filteroptionen)
  POST /api/auth               (Passwort pruefen)
  /                            (Frontend)
"""
import csv
import io
from urllib.parse import urlparse

import requests

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

import refresh
import stats as stats_mod
from config import FRONTEND, check_pw as _check_pw
from filtering import filter_records as _filter_records
from store import _DATA, load as _load
from views import (
    EXPORT_COLS as _EXPORT_COLS,
    flat as _flat,
    full_view as _full_view,
    public_view as _public_view,
)

app = FastAPI(title="WLO Quellenerschliessung", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def _no_cache_assets(request, call_next):
    """Statische Assets (HTML/JS/CSS/SVG) immer revalidieren lassen, damit nach
    Deploys/Änderungen nicht veraltetes JS aus dem Browser-Cache geladen wird."""
    resp = await call_next(request)
    p = request.url.path
    if p == "/" or p.endswith((".js", ".css", ".html", ".svg")):
        resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    return resp


@app.on_event("startup")
def _startup():
    _load()


# ---------------------------------------------------------------------------
# Lese-Endpoints (oeffentlich)
# ---------------------------------------------------------------------------
@app.get("/api/stats")
def stats():
    return stats_mod.compute_stats(_DATA["records"], _DATA["meta"])


@app.get("/api/meta/filters")
def filters():
    return stats_mod.compute_filter_options(_DATA["records"])


@app.get("/api/sources")
def sources(
    q: str | None = Query(None),
    kind: str | None = Query(None),
    oer: bool | None = Query(None),
    subject: str | None = Query(None),
    level: str | None = Query(None),
    min_count: int = Query(0, ge=0),
    has_node: bool | None = Query(None),
    only_field_profile: bool = Query(False),
    license_: str | None = Query(None, alias="license"),
    language: str | None = Query(None),
    lrt: str | None = Query(None),
    flag: str | None = Query(None),
    has_bezugsquelle: bool | None = Query(None),
    spider_real: bool = Query(False),
    wlo_migration: bool = Query(False),
    exclude_wlo: bool = Query(False),
    show_blacklist: bool = Query(False),
    has_spider: bool | None = Query(None),
    sort: str = Query("contentCount"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
):
    out = _filter_records(_DATA["records"], q, kind, oer, subject, level, min_count,
                          has_node, only_field_profile, license_, language, lrt, flag,
                          has_bezugsquelle, spider_real, wlo_migration, exclude_wlo, show_blacklist,
                          has_spider=has_spider)

    rev = order.lower() != "asc"
    def key(r):
        v = r.get(sort) if sort in ("contentCount", "fieldActiveCount", "name") else r["contentCount"]
        return (v or 0) if isinstance(v, (int, float)) else str(v or "").lower()
    out.sort(key=key, reverse=rev)

    total = len(out)
    skip = (page - 1) * page_size
    items = [_public_view(r) for r in out[skip: skip + page_size]]
    return {"total": total, "page": page, "pageSize": page_size,
            "pages": max(1, (total + page_size - 1) // page_size), "items": items}


@app.get("/api/sources/{source_id:path}")
def source_detail(source_id: str,
                  pw: str | None = Query(None),
                  x_team_password: str | None = Header(None)):
    r = _DATA["byId"].get(source_id)
    if not r:
        raise HTTPException(404, "Quelle nicht gefunden.")
    if _check_pw(pw, x_team_password):
        return _full_view(r)
    return _public_view(r)


@app.post("/api/auth")
def auth(pw: str | None = Query(None), x_team_password: str | None = Header(None)):
    if _check_pw(pw, x_team_password):
        return {"ok": True}
    raise HTTPException(403, "Falsches Passwort.")


@app.post("/api/admin/reload")
def reload_data(pw: str | None = Query(None), x_team_password: str | None = Header(None)):
    if not _check_pw(pw, x_team_password):
        raise HTTPException(403, "Nur intern.")
    _load()
    return {"ok": True, "meta": _DATA["meta"]}


# ---------------------------------------------------------------------------
# Live-Daten-Refresh (Hintergrund-Job; oeffentlich, kein Team-Login noetig)
# ---------------------------------------------------------------------------
@app.post("/jobs/refresh")
def jobs_refresh():
    return refresh.start()


@app.get("/jobs/latest")
def jobs_latest():
    return refresh.status()


# ---------------------------------------------------------------------------
# Umfangreiche Statistiken
# ---------------------------------------------------------------------------
@app.get("/api/stats/full")
def stats_full():
    return stats_mod.compute_stats_full(_DATA["records"], _DATA["meta"])


@app.get("/api/stats/team")
def stats_team(pw: str | None = Query(None), x_team_password: str | None = Header(None)):
    """Negative-/Datenproblem-Statistiken + Herkunft + Spider-Abgleich. Nur Team."""
    if not _check_pw(pw, x_team_password):
        raise HTTPException(403, "Nur intern (Team-Passwort nötig).")
    return stats_mod.compute_stats_team(_DATA["records"], _DATA["meta"])


# ---------------------------------------------------------------------------
# Export (maschinenlesbar)
# ---------------------------------------------------------------------------
def _filtered_rows(
    q: str | None = None, kind: str | None = None, oer: bool | None = None,
    subject: str | None = None, level: str | None = None, min_count: int = 0,
    has_node: bool | None = None, only_field_profile: bool = False,
    license: str | None = None, language: str | None = None, lrt: str | None = None,
    flag: str | None = None, has_bezugsquelle: bool | None = None, spider_real: bool = False,
    wlo_migration: bool = False, exclude_wlo: bool = False, show_blacklist: bool = False,
    has_spider: bool | None = None,
) -> list:
    """Gefilterte Records aus den Query-Parametern — die EINE Filterquelle der
    Export-Routen, damit JSON-/CSV-Export exakt der Listen-Ansicht entsprechen
    (gleicher Parametersatz wie /api/sources, nur ohne Sortierung/Pagination)."""
    return _filter_records(_DATA["records"], q, kind, oer, subject, level, min_count,
                           has_node, only_field_profile, license, language, lrt, flag,
                           has_bezugsquelle, spider_real, wlo_migration, exclude_wlo, show_blacklist,
                           has_spider=has_spider)


@app.get("/api/export.json")
def export_json(rows: list = Depends(_filtered_rows)):
    return JSONResponse([_flat(r) for r in rows],
        headers={"Content-Disposition": "attachment; filename=quellen_export.json"})


@app.get("/api/export.csv")
def export_csv(rows: list = Depends(_filtered_rows)):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_EXPORT_COLS, delimiter=";", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(_flat(r))
    return StreamingResponse(iter(["﻿" + buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=quellen_export.csv"})


@app.post("/api/sources/batch")
def sources_batch(ids: list[str] = Body(..., embed=True),
                  pw: str | None = Query(None),
                  x_team_password: str | None = Header(None)):
    """Mehrere Records für PDF-Erzeugung (public; intern mit Passwort)."""
    full = _check_pw(pw, x_team_password)
    out = []
    for i in ids[:100]:
        r = _DATA["byId"].get(i)
        if r:
            out.append(_full_view(r) if full else _public_view(r))
    return {"items": out}


# ---------------------------------------------------------------------------
# Vorschaubild-Proxy (für PDF-Einbettung) — umgeht den CORS-Canvas-Taint:
# der Browser kann externe edu-sharing-Thumbnails nicht ohne Tainting auf ein
# Canvas zeichnen; über diesen Same-Origin-Proxy klappt jsPDF.addImage.
# Nur WLO-Hosts erlaubt (kein offener Proxy).
# ---------------------------------------------------------------------------
_THUMB_CACHE: dict[str, tuple[bytes, str]] = {}


@app.get("/api/thumb")
def thumb(url: str = Query(..., description="Vorschau-URL (nur *.openeduhub.net)")):
    host = (urlparse(url).hostname or "").lower()
    if not (host == "openeduhub.net" or host.endswith(".openeduhub.net")):
        raise HTTPException(400, "Host nicht erlaubt.")
    cached = _THUMB_CACHE.get(url)
    if cached is None:
        try:
            rr = requests.get(url, timeout=8)
            rr.raise_for_status()
        except Exception:
            raise HTTPException(502, "Vorschau nicht abrufbar.")
        ct = rr.headers.get("Content-Type", "image/jpeg")
        if not ct.startswith("image/"):
            raise HTTPException(415, "Kein Bild.")
        cached = (rr.content, ct)
        if len(_THUMB_CACHE) < 2000:        # simple Obergrenze gegen unbegrenztes Wachstum
            _THUMB_CACHE[url] = cached
    content, ct = cached
    return Response(content=content, media_type=ct,
                    headers={"Cache-Control": "public, max-age=86400"})


# Frontend zuletzt mounten
if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
