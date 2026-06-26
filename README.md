# WLO Source Cataloguing — App

Overview of all WLO sources **and** generation of source profiles, for
**data providers, data consumers, and the team**. Combines existing curated lists
with current API data into **a single source of truth** — with per-field provenance
and server-side separation of public vs. internal information.

## What the App Shows

Two areas (tabs): **📚 Sources** and **📊 Statistics**.

- **Overview** of all sources with filters (type, subject, educational level, OER,
  minimum content count, **"dataset only"**, "with field profile only"),
  full-text search, and **multi-selection** (tick tiles, "select page").
- **Profile** per source:
  - *Basic & quality info* (title, URL, description, license, OER, subjects,
    educational levels, content type, content count) — **each field with an origin tag**.
  - *Metadata generation* (for ~53 crawler sources): per field, whether it is active and **how
    it is generated** (scraped / hard-coded / via mapping / LRMI / WP-JSON …).
  - *Internal area* (🔒 team password required): developer notes, detailed
    crawl/cataloguing status, GitHub, node ID, replicationsource, etc.
- **PDF profiles** (jsPDF, WLO branding: colour-bar header, logo, EU/BMBF
  footer, section tables + field-generation table) — **from one or
  several selected sources** in a single PDF. Selectable options in the selection
  bar: **template** (default detailed / compact 1 page), **include preview images**
  (thumbnail per source, CORS-free via the `/api/thumb` proxy),
  **individual files instead of combined**, and — with team login — **internal info**.
- **Table PDF** (source overview, landscape) of the current filter set and
  **statistics PDF** (all distributions) — buttons in the export bar.
- **Statistics** (its own area, grouped into sections): overview KPIs
  (including **total WLO content** ≈318k vs. **assignable to a source** ≈305k,
  **total Bezugsquellen** distinct); **origin** Quelldatensatz↔Bezugsquelle
  as an overlap chart; content volumes; **crawlers by type** + metadata
  generation by method + **metadata fields: how often active**; data coverage;
  top lists. The **assignment confidence** is visible only with team login.
- **Machine-readable export**: the entire filter set or selection as **CSV**
  (semicolon, UTF-8 BOM) or **JSON** (`/api/export.csv` · `/api/export.json`).
- **Footer** with **legal notice / privacy policy** as **in-app pages** (scrollable
  overlay; content taken verbatim from wirlernenonline.de, edu-sharing.net e.V.).

## Source of Truth — How Data Is Combined

One canonical "source" per real-world source, joined across multiple keys
(in order of precedence):

| Key | Connects |
|---|---|
| Spider name (`general_identifier`/`replicationsource` ↔ `Crawler(Spider)` ↔ Skohub) | Crawler profile ↔ Quelldatensatz ↔ vocab name |
| `publisher_combined` / dominant Spider publisher | Quelldatensatz ↔ Bezugsquelle ↔ content count |
| `nodeId` / correction list | Identity, whitelist/blacklist |

**Rules that produce clean data:**
- A crawler's Bezugsquelle = the **dominant publisher of its content**
  (the placeholder "WirLernenOnline" is discarded).
- `wirlernenonline_spider` is **not** a crawler binding but the node origin
  of the legacy migration → not counted as a crawler.
- The content count per Bezugsquelle is recorded only **once** (on the primary record);
  further Quelldatensätze of the same Bezugsquelle = **secondary dataset** (0 content,
  flagged) → no double-counting.
- Every public value carries its **provenance** (`WLO-API`, `datencrawler.csv`,
  `WLO-API (Facette)`).

**Integrated sources:** live API (Quelldatensätze, Bezugsquellen/Spider facets),
`datencrawler.csv` (crawler profiles + field generation, from the Team4 Excel),
`quellen_korrektur.csv` (whitelist/blacklist), Skohub vocabulary, dominant
publisher per Spider (from the analysis).

## Filter Logic "Source Type" & Provenance Markers

A source can be bound to a crawler in several ways. Two fields on the
Quelldatensatz are decisive — and they do **not** mean the same thing:

- **`ccm:general_identifier`** = the **real crawler binding** (technical Spider, e.g. `bpb_spider`).
- **`ccm:replicationsource`** = the **node origin** — often the migration marker
  `wirlernenonline_spider`, sometimes a real Spider or a legacy vocab URI.

**Core rule:** The effective binding is **always the field that is NOT
`wirlernenonline_spider`** (`general_identifier` takes precedence, otherwise
`replicationsource ≠ wirlernenonline_spider`). A Quelldatensatz is a **real
source** if **`LRT = Quelle` OR a real binding** is present — **regardless**
of whether it was imported via the data migration (`replicationsource =
wirlernenonline_spider` only means "migrated", not "not a real dataset").

**Filter "Source Type" (end user, default = crawler)** — freely combinable with subject/level/
license/… (the backend joins them with **AND**):

| Option | Criterion |
|---|---|
| Crawler (Spider) | `kind=crawler`, excluding the WLO migration Spider |
| with Quelldatensatz | `has_node=true` |
| Quelldatensatz + Bezugsquelle | `has_node=true` & `has_bezugsquelle=true` |
| Bezugsquelle only (without dataset) | `has_node=false` & `has_bezugsquelle=true` |

**Team data-check filter — only after team login** (`#f-pruef`; never an end-user
filter, so the "source type" filter above always stays clean). Two groups:

- *Data problems:* secondary datasets / duplicates (`ZWEITDATENSATZ`) and sorted-out
  non-sources (`BLACKLIST`) — both hidden from the default list (see below) · Bezugsquelle
  with a single content item (`BQ_EINZELINHALT`) · duplicate suspicion, shared URL/title
  (`DUBLETTE_VERDACHT`) · mixed content types, Quelle + others (`FEHLTAGGING`) · thin
  metadata, core fields missing (`METADATEN_DUENN`) · source dataset without a Bezugsquelle
  (`QD_OHNE_BEZUGSQUELLE`) · incomplete binding, crawler without dataset
  (`BINDUNG_UNVOLLSTAENDIG`) · real source but type ≠ Quelle (`TYP_NICHT_QUELLE`).
- *Origin / binding:* WLO data import (`wlo_migration`) · bound via old tagging
  (`LEGACY_BINDUNG`).

Each option maps to one `flag=<NAME>` criterion that **bypasses the default hide**, so
the team can inspect even otherwise-hidden records. The data-problem flags are internal
review markers (not shown as public badges). The team statistics page carries a
"Datenprobleme" bar chart that is **1:1 with these filter options** (each bar is the same
count and retrievable as the matching `flag=<NAME>`), so chart and filter never drift.

**Provenance markers (badges, public)** — visible on every source (tile + profile):
- **🔄 Data migration (WLO)** — imported via the legacy migration.
- **🏷️ Legacy binding** — bound via a legacy vocab source rather than a technical Spider.
- **⚠ Content type ≠ Quelle** — a real source, but LRT≠Quelle (correction candidate in edu-sharing, e.g. bpb).

**Blacklist (curation in `quellen_korrektur.csv`):** Obvious **individual materials**
(series episodes such as "Extra en español | Episode X", single topics, Klexikon person
articles, single videos, individual tests such as "Test - Mozart") and duplicates are
marked as `blacklist`. They are **not sources** and are therefore **always hidden from
the source list by default** (listed in [`field_policy.py`](backend/field_policy.py)
`HIDDEN_BY_DEFAULT`). **Secondary datasets** (`ZWEITDATENSATZ`) are treated differently:
they are distinct source-dataset *objects* that merely share a Bezugsquelle tag (e.g. 47
different YouTube channels all tagged "YouTube"), **not** real duplicates. They are
collapsed only in the default and Bezugsquelle (tag) view — where they would over-count
distinct Bezugsquellen — but **shown in the Quelldatensatz (object) view**
(`has_node=true`), which therefore counts ~1.242 datasets, not ~824. Each list view
reports how many records it hides — **broken down** by blacklist and secondary datasets —
as a small "N ausgeblendet (… aussortiert + … Mehrfach-Datensätze)" note, so the displayed
count can be reconciled with the raw data (`hidden: {total, blacklist, zweitDatensatz}` in
the API). The team data-check filter (or `show_blacklist=true`) reveals every category.
Heuristic: real binding **+ 0 content** +
title pattern (Folge/Episode/Test/"| Wir lernen online"/"- alpha Lernen" …) → manually
checked. Real sources (portals, databases, YouTube **channels**) are kept.

Full derivation, findings, and cross-tabulations: [`SPIDER-GESAMTBILD.md`](SPIDER-GESAMTBILD.md).

## Security (Public vs. Internal)

The separation is **server-side**: public endpoints **never** return the `internal`
object. Internal fields require team authorization — in the browser via an **httpOnly
session cookie** issued by `POST /api/auth` (the password is sent once and **never stored
client-side**, so XSS cannot read the session), or for API clients/tests via the
`X-Team-Password` header / `?pw=`. The public/internal assignment is defined centrally in
[`backend/field_policy.py`](backend/field_policy.py).

- **Team login** (password) unlocks internal fields and protects
  `/api/admin/reload`.
- **Live refresh** (`POST /jobs/refresh`, the team-only "🔄 Refresh" button)
  **requires the team password** — it triggers expensive live API calls. A
  concurrency guard prevents parallel runs; an optional nightly run is configurable
  (see `QE_AUTO_REFRESH_HOUR` below).
- **Error protocol** (`GET /api/protokoll.md`, the team-only "📋 Fehler-Protokoll" button):
  a Markdown report quantifying every per-record data problem with one Handlungsempfehlung per
  category **and a concrete per-case fix hint where the data allows it** — which core fields are
  missing, which content types to strip, which record to merge a secondary into, and per duplicate
  cluster which source to keep (✅) vs. remove (🗑). Plus a metadata fill-rate section and a note on
  the structural problems that need governance rather than per-record detection.
  Every rubric maps 1:1 to a record flag, so the team **Datenprüfung** filter (`flag=<NAME>`)
  and the team Datenprobleme chart cover the exact same categories — including missing/inconsistent
  editorial status, not-published-in-search, ambiguous spider binding (general_identifier ≠
  replicationsource), and publisher Bezugsquellen without a source dataset
  (built in [`backend/protokoll.py`](backend/protokoll.py)).
- **No default password** — if `QE_TEAM_PASSWORD` is unset, team features stay disabled
  (fail closed). It is a single shared secret compared in **constant time**; use a
  **high-entropy value** and, for public deployments, add login **rate-limiting via a
  reverse proxy** (the app itself does not rate-limit).
- **Single process:** data is held in memory per process, so run **one** Uvicorn worker —
  a refresh reloads only the current process (multi-worker would need a shared signal).

## Configuration (`.env`)

The team password comes from the environment variable **`QE_TEAM_PASSWORD`**.
There is **no default**: if it is unset, team features fail closed (login always
fails, internal data stays hidden) rather than being guarded by a known password.
Locally, the simplest approach is a `.env` file in the `backend/` folder — the app
loads it at startup (no extra dependency; real shell variables take precedence):

```bash
cp backend/.env.example backend/.env
# backend/.env:  QE_TEAM_PASSWORD=my-password
```

Alternatively via the shell: `setx QE_TEAM_PASSWORD "…"` (persistent) or
`$env:QE_TEAM_PASSWORD="…"` (session). `.env` is excluded via `.gitignore`;
`backend/.env.example` is the committable template.

**Optional nightly refresh:** set **`QE_AUTO_REFRESH_HOUR`** (0–23, local time,
e.g. `3`) to run the live refresh automatically once a day; unset disables it.

## Getting Started

```bash
PY="C:/Users/jan/miniconda3/python.exe"
cd backend
"$PY" -m pip install -r requirements.txt        # once
cp .env.example .env                            # set team password (optional)
"$PY" truth.py                                   # builds data/truth.json
"$PY" -m uvicorn app:app --host 127.0.0.1 --port 8080
# -> http://127.0.0.1:8080  (frontend)   ·   /docs (API)
```

Team login in the UI: top right "🔒 Team login" — the password is whatever you set
in `QE_TEAM_PASSWORD` (no default; if unset, team features stay disabled).

## Tests

```bash
cd backend
"$PY" -m pip install -r requirements-dev.txt     # pytest + httpx (once)
"$PY" -m pytest                                   # unit + API integration + golden snapshots
```

The tests run against the existing `data/truth.json` and enforce a known
team password (independent of `.env`). The **golden snapshots** (`tests/golden/`)
pin the exact JSON output of the statistics/list endpoints; after a
**deliberate** behaviour/data change, regenerate them with
`"$PY" tests/golden/_generate.py`.

## Updating Data (Live Refresh)

**Directly in the app:** after team login, top right **"🔄 Refresh"** — starts
a background job that re-fetches the live/facet data and rebuilds `truth.json`
(~2 min, with a progress indicator). The data timestamp appears in the header.

**Automatically (optional):** set `QE_AUTO_REFRESH_HOUR` (0–23, local time) to run the
same background job once a day — see [Configuration](#configuration-env). It reuses the
same concurrency-guarded path, so the manual and nightly runs never collide.

Technically:
```
POST /jobs/refresh   (team password) → fetcher.refresh_all() + truth.main() + reload
GET  /jobs/latest    → progress/status
```

`fetcher.py` pulls: the Bezugsquellen/Spider facet, all Quelldatensätze,
the dominant publisher per Spider, the Skohub vocabulary. **Not** overwritten are
`datencrawler.csv` and `quellen_korrektur.csv` (maintained manually).

Detailed explanation of the data integration: **[DATENINTEGRATION.md](DATENINTEGRATION.md)**.

## Architecture

Each module has **one** responsibility (a single reason to change):

```
quellenerschliessung-app/
├── backend/                  # FastAPI; domain modules with one responsibility each
│   ├── app.py                # Web layer: thin routes + middleware + thumb proxy
│   ├── config.py             # Configuration, team password, constants, paths
│   ├── store.py              # In-memory data store (loads data/truth.json)
│   ├── views.py              # Public/internal serialisation (trust boundary)
│   ├── filtering.py          # Filter logic for the source list (pure)
│   ├── stats.py              # Statistics aggregation (/api/stats[/full|/team])
│   ├── refresh.py            # Live refresh as a background job (+ nightly scheduler)
│   ├── session.py            # Short-lived team sessions (httpOnly cookie)
│   ├── field_policy.py       # ONE place: which fields are public vs. internal
│   ├── truth.py              # Source-of-truth engine: join/records -> data/truth.json
│   ├── truth_loaders.py      # Reads all inputs (CSV/JSON/live caches)
│   ├── truth_text.py         # Text normalisation & parser helpers (pure)
│   ├── tests/                # pytest: unit + API integration + golden snapshots
│   ├── data/inputs/*.csv     # curated inputs (bundled for container refresh)
│   └── data/truth.json       # generated data snapshot (versioned)
├── Dockerfile · .dockerignore   # serving container (API + frontend)
├── .github/workflows/           # CI: tests → build & push to Docker Hub
└── frontend/                 # No-build SPA: index.html + styles.css + 7 classic scripts
    ├── core.js   # DOM helpers, state, API client, toast (base)
    ├── list.js   # filters, tiles, selection, card menu
    ├── detail.js # profile view
    ├── pdf.js    # PDF generation (jsPDF)
    ├── export.js # CSV/JSON export
    ├── stats.js  # statistics view + charts
    └── main.js   # view switching, login, refresh, wiring, init (loaded last)
```

The frontend scripts are **classic scripts** (no build step) and are loaded in
`index.html` via `<script defer>` in this order (`core` first,
`main` last) — they share the same global scope.

**Rationale for the stack:** FastAPI (like the existing `wlo-quellenliste-api`) + a no-build
frontend → runs without an Angular toolchain, is easy to maintain, and can later be embedded
as a web component. The source of truth is decoupled as a pure build step
(`truth.json`) and can be used independently of the frontend.

## Deployment (Docker & Docker Hub)

A **single container** serves both the API **and** the frontend from the bundled
data snapshot (`backend/data/truth.json`).

```bash
docker build -t quellensteckbriefe .
docker run -p 8080:8080 -e QE_TEAM_PASSWORD=my-password quellensteckbriefe
# -> http://127.0.0.1:8080
```

- **Data snapshot:** `backend/data/truth.json` is deliberately **versioned** — the
  container build requires it (regenerate with `python truth.py` on a
  machine that has the input repos, then rebuild the image). The curated CSVs
  are bundled under `backend/data/inputs/` for the in-container refresh.
  Build switch `QE_RENAME_UNREP_BQ` (default `1` = variant A): Bezugsquellen
  without their own Quelldatensatz are listed under the Bezugsquelle name via the
  representative single item; `QE_RENAME_UNREP_BQ=0 python truth.py` = variant B
  (primary preference only, no renaming).
- **Live refresh in the container:** re-fetches facets/Quelldatensätze from the
  public WLO API and rebuilds `truth.json` in the **ephemeral** container filesystem
  (crawler profiles/blacklist are preserved thanks to the bundled CSVs); the
  update lasts **until the next restart**. For persistent data, mount a volume:
  `-v $PWD/data:/app/quellenerschliessung-app/backend/data`.
- **Secret:** `QE_TEAM_PASSWORD` is **not** baked into the image — pass it at runtime
  via `-e`. Without it, team features fail closed (there is no known-default password).

**CI → Docker Hub** ([`.github/workflows/docker-publish.yml`](.github/workflows/docker-publish.yml)):
A push to `main` or a `v*` tag triggers it → first **tests**, then **build & push**.
Required repository secrets:

| Secret | Content |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token (Account → Security) |

Image: `<DOCKERHUB_USERNAME>/quellensteckbriefe` (tags: `latest`, branch name,
short SHA, SemVer for `v*` tags). Adjust the image name in the workflow if needed.

**Not in the repo** (`.gitignore`): `.env` (team password!), `__pycache__/`,
`.pytest_cache/`. **Kept versioned** are `truth.json`, the input CSVs, and the
golden snapshots (required by the build and the tests respectively).

**Server deployment (Debian 13 + Docker Compose):** a ready-made `docker-compose.yml`,
sample `.env`, and step-by-step instructions under [`deploy/`](deploy/).

## Open Extensions

- Additionally read the Team4 Excel details (AI legal review, agreement details)
  alongside `datencrawler.csv`.
- Load ID-only Quelldatensätze (not search-visible) via the Node API.
