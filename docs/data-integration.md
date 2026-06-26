# Data Integration of the Source-Profiles App

_How the app merges all information sources into a single "data truth", which
data it uses, how the data is updated, and how public information is separated
from internal information._

---

## 1. Overview in One Picture

```
  LIVE (WLO production, retrievable)          STATIC (manually maintained)
  ─────────────────────────────────         ───────────────────────────────
  • Bezugsquelle facet                       • datencrawler.csv
    (ccm:oeh_publisher_combined + counts)      (Crawler profiles + field
  • Spider facet                               generation, ~53 Crawlers)
    (ccm:replicationsource + counts)         • quellen_korrektur.csv
  • Quelldatensätze (LRT=Quelle, full MD)      (Whitelist/Blacklist)
  • dominant publisher per Spider            • Skohub vocabulary (source names)
            │                                          │
            ▼  fetcher.py (live retrieval)             │
   raw/*.json  +  data/replication_publisher_gap.csv   │
            └──────────────┬───────────────────────────┘
                           ▼  truth.py  (6 join/cleanup rules)
                   data/truth.json   ← canonical source records
                           ▼  app.py (FastAPI, read-only)
                   /api/...  →  Frontend (tiles, profiles, statistics)
```

**Core idea:** One **canonical "source" per real source**, composed of several
sources, with **field provenance** (where each value comes from) and
**public/internal separation**.

---

## 2. Which Data Is Used?

| # | Data source | Type | What it contributes | Freshness |
|---|---|---|---|---|
| 1 | **Bezugsquelle facet** `ccm:oeh_publisher_combined` | live (API) | List of all Bezugsquellen + **content count** per Bezugsquelle | on refresh |
| 2 | **Spider facet** `ccm:replicationsource` | live (API) | active Crawlers + content count per Crawler | on refresh |
| 3 | **Quelldatensätze** (source datasets) (`ccm:io`, LRT=Quelle) | live (API) | Title, URL, description, license, OER, subject, level, language, keywords, preview image, `general_identifier`, Erschließungsstatus … | on refresh |
| 3b | **hidden Quelldatensätze** (Node API, ID from CSV column "Quelldatensatz (Prod)") | live (API, 1 call/ID) | Metadata + **preview image** for Crawlers whose Quelldatensatz is NOT search-visible (different LRT, e.g. bpb) → `extra_nodes.json` | on refresh |
| 4 | **dominant publisher per Spider** | live (API, 1 call/Spider) | the "real" Bezugsquelle of a Crawler (instead of a placeholder) | on refresh |
| 5 | **datencrawler.csv** | static (Team4 Excel export) | Crawler profile: legal aspects (robots.txt, TDM §44b, terms of service, license check), author + **109 field-generation statuses** per Crawler; internal: state, remarks, GitHub, crawl data, contract | manual |
| 6 | **quellen_korrektur.csv** | static (curated) | Whitelist/Blacklist (duplicate/"not a real source"), Node↔Bezugsquelle overrides | manual |
| 7 | **Skohub vocabulary** `…/vocabs/sources` | live (rarely) | clear names for URI-legacy Spiders | on refresh |

> Sources 1–4 + 7 are **live retrievable** (refresh job). Sources 5–6 are
> **manually maintained** and are **not** overwritten by the refresh.

---

## 3. The Merge (Data Truth) — `truth.py`

A canonical source is created by joining over several keys
(precedence from top to bottom):

| Join key | connects |
|---|---|
| **Spider name** (`general_identifier` on the Quelldatensatz ↔ `Crawler (Spider)` in datencrawler.csv ↔ Skohub) | Crawler profile ↔ Quelldatensatz ↔ vocabulary name |
| **`publisher_combined`** (or the dominant Spider publisher) | Quelldatensatz ↔ Bezugsquelle ↔ content count |
| **nodeId** | correction list (Whitelist/Blacklist), identity |

### Three Kinds of Canonical Records
1. **Crawler source** — anchor = Spider; combines the datencrawler.csv profile +
   matching Quelldatensatz + Bezugsquelle + content count.
2. **Manual source** — anchor = Quelldatensatz without a Crawler binding.
3. **Bezugsquelle only** — facet without its own Quelldatensatz (keyword + count).

### Six Rules That Produce Clean Data
1. **Crawler Bezugsquelle = dominant publisher** of its content (rule/source 4).
   The migration placeholder "WirLernenOnline" is **discarded** in the process.
2. **`wirlernenonline_spider` is not a Crawler binding**, but rather the origin
   of the dataset node (legacy migration) → does not count as a Crawler. The real
   binding is in `general_identifier`.
3. **Consolidation per Spider:** Multiple Quelldatensätze of the same Crawler →
   **one** record (best node), no card duplicates.
4. **Content count per Bezugsquelle only once** (on the primary record). Further
   datasets of the same Bezugsquelle = **secondary dataset** (0 content, flag) → no
   double counting.
5. **URI-legacy Spiders** are resolved to clear names via the Skohub vocabulary.
6. **Correction list**: Blacklist nodes are marked (duplicate/"not a real
   source"), Whitelist is preferred.

### Field Provenance
Every public value carries its origin, visible in the profile as a tag:
`WLO-API` · `WLO-API (facet)` · `datencrawler.csv`. This makes it transparent
whether a value comes from the live API or from the curated list.

---

## 4. Updating — Live Refresh

The app serves a **precomputed snapshot** (`truth.json`)
(fast, no API call per request). Updating happens via a
**background job**:

```
[UI] 🔄 Refresh  (team login only)
   └─ POST /jobs/refresh         (password required)
        └─ fetcher.refresh_all()  : facets → Quelldatensätze → publisher/Spider → vocabulary
        └─ truth.main()           : rebuilds data/truth.json (+ generatedAt timestamp)
        └─ _load()                : loads the snapshot into memory
   └─ GET /jobs/latest            : progress (percent + message), polling in the frontend
```

- Duration ~2 min (mainly 119 individual Spider queries for the dominant publishers).
- The **data state** (`generatedAt`) is shown in the header as "Data state: …".
- Manual alternative: run `truth.py` directly, then
  `POST /api/admin/reload`.
- **Not** updated live: `datencrawler.csv` and `quellen_korrektur.csv`
  (manual maintenance).

---

## 5. Public vs. Internal

The separation is **server-side** (centralized in `field_policy.py`); public
endpoints **never** return internal fields.

| Public (data provider/data consumer) | Internal (team password) |
|---|---|
| Basic info (title, URL, description, subject, level, content count, preview image) | developer notes, **exact state**, crawl data, GitHub |
| License/OER + **AI use & legal aspects** (robots.txt, TDM §44b, terms of service, license check) | exact **Erschließungsstatus**, workflow status, node ID, replicationsource |
| **Metadata generation** per Crawler field (scraped/hard-coded/mapped …) | **contract/agreement** (whether WLO has a contract) |

Refresh/reload endpoints are likewise password-protected.

---

## 6. Files

```
backend/
  fetcher.py        # live retrieval (facets, Quelldatensätze, publisher/Spider, vocabulary)
  truth.py          # data-truth engine → data/truth.json (+ generatedAt)
  field_policy.py   # ONE place: public vs. internal
  app.py            # FastAPI: read API + /jobs/refresh + /jobs/latest + auth
  data/truth.json   # snapshot (generated)
quellen-analyse/    # shared caches (raw/*.json, data/replication_publisher_gap.csv)
```

For the in-depth domain analysis (data quality, duplicates, terminology) see
`quellen-analyse/BERICHT-Quellen-Datenlandschaft.md`.
