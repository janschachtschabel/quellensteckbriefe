"""app.py — source-indexing API (web layer).

Thin FastAPI routes over the data truth (data/truth.json). The actual
logic lives in the domain modules:
  config     configuration, team password, constants, paths
  store      in-memory data holding (truth.json)
  views      public/internal serialization (server-side separation)
  filtering  filter logic of the source list
  stats      statistics aggregation
  refresh    live-data refresh (background job)

Security: PUBLIC endpoints NEVER expose the internal fields. Internal
fields (developer notes, exact status) only with the correct team password
(env QE_TEAM_PASSWORD; unset => team features disabled, fail closed).

Endpoints:
  GET  /api/stats
  GET  /api/sources            (list, filtered, public)
  GET  /api/sources/{id}       (detail; with ?pw=/header incl. internal)
  GET  /api/meta/filters       (filter options)
  POST /api/auth               (check password)
  /                            (frontend)
"""
import csv
import io
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import requests

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

import protokoll
import refresh
import session
import stats as stats_mod
import stats_team as stats_team_mod
from config import AUTO_REFRESH_HOUR, FRONTEND, check_pw as _check_pw
from filtering import filter_records as _filter_records, hidden_breakdown as _hidden_breakdown
from store import _DATA, load as _load
from views import (
    EXPORT_COLS as _EXPORT_COLS,
    flat as _flat,
    full_view as _full_view,
    public_view as _public_view,
)

@asynccontextmanager
async def _lifespan(app):
    _load()                                      # load data/truth.json into memory
    refresh.start_scheduler(AUTO_REFRESH_HOUR)   # optional nightly refresh (daemon; no-op if unset)
    yield


app = FastAPI(title="WLO Quellenerschliessung", version="1.0.0", lifespan=_lifespan)
# Public read-only data tool: any origin may query the API. allow_credentials stays at its
# default (False) and team auth uses a custom header (no cookies), so "*" does not enable
# cross-site credentialed requests; the app's own frontend is same-origin anyway.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def _cache_headers(request, call_next):
    """Cache policy: API/job responses are never cached (they change on refresh — no stale
    data from a browser/proxy); static assets are revalidated so no stale JS loads after a
    deploy."""
    resp = await call_next(request)
    p = request.url.path
    if p.startswith("/api/") or p.startswith("/jobs/"):
        resp.headers["Cache-Control"] = "no-store"
    elif p.startswith("/vendor/"):
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"   # versioned libs
    elif p == "/" or p.endswith((".js", ".css", ".html", ".svg")):
        resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    return resp


# ---------------------------------------------------------------------------
# Read endpoints (public)
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
    # Breakdown of the records this view hides by default, so the displayed count can be
    # reconciled with the raw data: blacklist (always hidden) + secondary datasets
    # (collapsed in the tag/default view, shown in the Quelldatensatz/object view).
    # An explicit flag/show_blacklist query hides nothing.
    hidden = {"total": 0, "blacklist": 0, "zweitDatensatz": 0}
    if not flag and not show_blacklist:
        full = _filter_records(
            _DATA["records"], q, kind, oer, subject, level, min_count,
            has_node, only_field_profile, license_, language, lrt, flag,
            has_bezugsquelle, spider_real, wlo_migration, exclude_wlo, True,
            has_spider=has_spider)
        hidden = _hidden_breakdown(full, has_node)
    skip = (page - 1) * page_size
    items = [_public_view(r) for r in out[skip: skip + page_size]]
    return {"total": total, "hidden": hidden, "page": page, "pageSize": page_size,
            "pages": max(1, (total + page_size - 1) // page_size), "items": items}


def team_auth(request: Request,
              pw: str | None = Query(None),
              x_team_password: str | None = Header(None)) -> bool:
    """Team authorization: a valid session cookie OR the team password (header/query).
    The browser uses the httpOnly session cookie (so the password is never stored client
    side); API clients and tests may still send the X-Team-Password header / ?pw=."""
    return session.valid(request.cookies.get(session.COOKIE)) or _check_pw(pw, x_team_password)


@app.get("/api/sources/{source_id:path}")
def source_detail(source_id: str, is_team: bool = Depends(team_auth)):
    r = _DATA["byId"].get(source_id)
    if not r:
        raise HTTPException(404, "Quelle nicht gefunden.")
    return _full_view(r) if is_team else _public_view(r)


@app.post("/api/auth")
def auth(request: Request, response: Response,
         pw: str | None = Query(None), x_team_password: str | None = Header(None)):
    """Log in with the team password and receive an httpOnly session cookie."""
    if not _check_pw(pw, x_team_password):
        raise HTTPException(403, "Falsches Passwort.")
    token = session.issue()
    # Secure flag when the request arrived over HTTPS (directly or via a TLS proxy).
    secure = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
    response.set_cookie(session.COOKIE, token, max_age=session.TTL,
                        httponly=True, samesite="strict", secure=secure)
    return {"ok": True}


@app.post("/api/logout")
def logout(request: Request, response: Response):
    session.revoke(request.cookies.get(session.COOKIE))
    response.delete_cookie(session.COOKIE)
    return {"ok": True}


@app.get("/api/auth/status")
def auth_status(request: Request):
    """Whether the current session cookie is a valid team login (drives the team UI)."""
    return {"team": session.valid(request.cookies.get(session.COOKIE))}


@app.post("/api/admin/reload")
def reload_data(is_team: bool = Depends(team_auth)):
    if not is_team:
        raise HTTPException(403, "Nur intern.")
    _load()
    return {"ok": True, "meta": _DATA["meta"]}


# ---------------------------------------------------------------------------
# Live-data refresh (background job; team login required — it triggers expensive
# live API calls). A nightly run can be configured via QE_AUTO_REFRESH_HOUR.
# ---------------------------------------------------------------------------
@app.post("/jobs/refresh")
def jobs_refresh(is_team: bool = Depends(team_auth)):
    if not is_team:
        raise HTTPException(403, "Team-Login erforderlich.")
    return refresh.start()


@app.get("/jobs/latest")
def jobs_latest():
    return refresh.status()


# ---------------------------------------------------------------------------
# Extensive statistics
# ---------------------------------------------------------------------------
@app.get("/api/stats/full")
def stats_full():
    return stats_mod.compute_stats_full(_DATA["records"], _DATA["meta"])


@app.get("/api/stats/team")
def stats_team(is_team: bool = Depends(team_auth)):
    """Negative/data-problem statistics + origin + spider reconciliation. Team only."""
    if not is_team:
        raise HTTPException(403, "Nur intern (Team-Passwort nötig).")
    return stats_team_mod.compute_stats_team(_DATA["records"], _DATA["meta"])


# ---------------------------------------------------------------------------
# Export (machine-readable)
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
    """Filtered records from the query parameters — the ONE filter source of the
    export routes, so that JSON/CSV export matches the list view exactly
    (same parameter set as /api/sources, just without sorting/pagination)."""
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


@app.get("/api/protokoll.md")
def protokoll_md(is_team: bool = Depends(team_auth)):
    """Team-only Markdown protocol: data problems quantified, per case, with a fix per category."""
    if not is_team:
        raise HTTPException(403, "Nur intern (Team-Login nötig).")
    md = protokoll.build_protokoll(_DATA["records"], _DATA["meta"])
    return Response(md, media_type="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=fehler-protokoll.md"})


@app.post("/api/sources/batch")
def sources_batch(ids: list[str] = Body(..., embed=True), is_team: bool = Depends(team_auth)):
    """Multiple records for PDF generation (public; internal with team session/password)."""
    out = []
    for i in ids[:100]:
        r = _DATA["byId"].get(i)
        if r:
            out.append(_full_view(r) if is_team else _public_view(r))
    return {"items": out}


# ---------------------------------------------------------------------------
# Preview-image proxy (for PDF embedding) — circumvents the CORS canvas taint:
# the browser cannot draw external edu-sharing thumbnails onto a canvas without
# tainting it; via this same-origin proxy jsPDF.addImage works.
# Only WLO hosts allowed (not an open proxy).
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
        if len(_THUMB_CACHE) < 2000:        # simple upper bound against unbounded growth
            _THUMB_CACHE[url] = cached
    content, ct = cached
    return Response(content=content, media_type=ct,
                    headers={"Cache-Control": "public, max-age=86400"})


# Mount the frontend last
if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
