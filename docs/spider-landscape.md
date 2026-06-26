# Spider Landscape — Sources, Numbers, Layers

Snapshot date: 2026-06-17. Reproducible via the queries listed in the appendix.
This document brings together **all information sources on "Spiders" (Crawlers)**
and explains why the spider counts in circulation (46 / 54 / 119 …) diverge —
they measure **different Layers** of the same landscape.

---

## 1. The four information sources

| Source | What it is | Count | Naming regime |
|---|---|---|---|
| **GitHub** `openeduhub/oeh-search-etl/converter/spiders` | implemented crawler **code** | **54** `*_spider.py` | technical (`bpb_spider`) |
| **Live API** `ccm:replicationsource` (facet) | origin **on the individual content item** | **119** distinct | mixed |
| **Skohub** `vocabs/sources` | source **names** ↔ UUID | **145** concepts | human-readable (`DLRG`) |
| **`ccm:general_identifier`** (on the Quelldatensatz) | the source's actual crawler **binding** | **38** distinct / 41 records | technical |
| **`datencrawler.csv`** (Team4-maintained) | manually curated crawlers | **55** | technical |

**Two naming regimes — important:**
- **Technical** (`*_spider`): GitHub code, `general_identifier`, CSV and the "modern"
  part of the live origin. Directly joinable with one another.
- **Human-readable + UUID** (Skohub): the `sources` vocabulary names (`DLRG`, `bpb`, …).
  Not a single Skohub prefLabel is a technical `_spider` name. Skohub mainly serves
  to **resolve the legacy UUID origins** (see Layer 3).

The **119** live `replicationsource` values split into **45 technical** (`_spider`),
**73 URI-legacy** (`…/vocabs/sources/<uuid>`) and **1 other**.

---

## 2. Three Layers (this is how the contradictory numbers resolve)

### 🟢 Layer 1 — Active crawlers (the hard core): **45**
Have GitHub code **and** produce live content.
- **38** of them cleanly bound to a Quelldatensatz via `general_identifier`.
- **All 45** maintained in the Team4 CSV.
- **0** live crawlers **without** GitHub code → this Layer is consistent.

This is the "we assume ~46 spiders" gut feeling — now substantiated.

### 🟡 Layer 2 — Implemented, but dormant: **9**
GitHub code, but **no** live content:
`sample_spider` (test), `oeh_spider`, `oeh_rss_spider`, `merlin_spider`,
`sodix_spider`, `zoerr_spider`, `mediothek_pixiothek_spider`,
`materialnetzwerk_spider`, `wirlernenonline_gsheet_spider`.
→ disabled / empty / test = legacy burden **or** potential.

### 🔵 Layer 3 — Legacy origin (old migration): **73 URI values**
Content from the time **before** the `_spider` convention; origin as
`http://w3id.org/openeduhub/vocabs/sources/<uuid>`.
- **61** nameable via Skohub, **12 orphaned UUIDs** (pointing to unknown /
  removed vocabulary entries).

### Special case — `wirlernenonline_spider` (WLO data migration)
**Not a real crawler**, but the **migration marker** of the legacy holdings.
- Attached to **320 objects** (live).
- Of these, **196 as content type "Quelle"** (= our migration Quelldatensätze),
  **~124 other types** (Tool 45, Webseite 40, Methoden 18, News 9, Bild 6,
  Video/Audio/Buch/Nachschlagewerk 5 each …; 28 types total).
- 376 type hits across 320 objects → **56 objects tagged multiple times**.

---

## 3. Crawler binding: `general_identifier` ↔ `replicationsource`

Two fields on the Quelldatensatz bind a source to a crawler — and they do
**not** mean the same thing:
- **`general_identifier`** = the **actual crawler binding** (technical Spider, e.g. `bpb_spider`).
- **`replicationsource`** = the **origin of the node** — often the migration marker
  `wirlernenonline_spider`, sometimes a real Spider or a legacy vocab URI.

**Overview (snapshot, per source/record):**
| | Count |
|---|---|
| with `general_identifier` | **41** |
| with `replicationsource` | **287** |
| **both set** | **35** |
| ⮑ of which **different** | **35 (= 100 %)** |
| ⮑ of which equal | 0 |
| only `general_identifier` | 6 |
| only `replicationsource` | 252 |

**Finding A — both set ⇒ always different.** In all 35 cases the rule is
"real Spider ↔ migration marker" (31× `gi=<spider>` / `rs=wirlernenonline_spider`,
4× `gi=<spider>` / `rs=legacy URI`). → When doubly assigned, **always treat `general_identifier`**
as the crawler, never `replicationsource`.

**Finding B — the reverse direction: 86 real sources have ONLY `replicationsource`.**
Of the 252 "only replicationsource":
| Class | Count | real? |
|---|---|---|
| pure **WLO migration** (`wirlernenonline_spider`) | 166 | no (migration) |
| **real Spider** only via `rs` (`planet_schule_spider`, `zum_spider`, `bne_portal_spider` …) | 52 | **yes** |
| **legacy vocab source** (Wikipedia, ZUM, Goethe-Institut, Bayerischer Rundfunk …) | 34 | **yes** |

→ A **pure `general_identifier` filter (41) overlooks 86 genuinely bound sources!**

**Correct filter rule (crawler/Spider view):**
> real binding = `general_identifier` set **OR** `replicationsource ≠ wirlernenonline_spider`

This yields **127 genuinely bound sources** (41 via gi + 52 real-Spider-only-rs +
34 legacy-only-rs); **166** are pure migration. The `replicationsource` legacy URIs
(`…/vocabs/sources/<uuid>`) are resolved to clear names via the Skohub vocabulary
(33 / 34 resolvable). Visualized in the team statistics area "Spider binding".

**Finding C — the content type (LRT=Quelle) as a third dimension.** `gi = real Spider`
+ `rs = wirlernenonline_spider` is **not a contradiction**, but a **real source
from the data migration** (e.g. bpb). What matters is only the combination with the
content type.

*Live cross-tabulation of the WLO migration (`replicationsource = wirlernenonline_spider`, 320 objects):*
| `general_identifier` | LRT=Quelle | Count | Meaning |
|---|---|---|---|
| real Spider | **yes** | **31** | real source, migrated, correctly tagged |
| real Spider | no | **2** | real source, migrated, **wrongly** tagged (bpb case, LRT=Webseite) |
| — | yes | **166** | tagged as Quelle, migrated, **without** crawler binding |
| — | no | **121** | pure migration content (not a Quelle) |
| **Total** | | **320** | **197 Quelle** / 123 non-Quelle |

*Complete cross-tabulation of all 1,332 node-bound Quelldatensätze (snapshot):*
| `general_identifier` | `replicationsource` | LRT=Quelle | Count |
|---|---|---|---|
| — | — | yes | 1,038 |
| — | wirlernenonline (migration) | yes | 166 |
| — | real Spider | yes | 52 |
| — | legacy vocab name | yes | 34 |
| real Spider | wirlernenonline (migration) | yes | 28 |
| real Spider | — | yes | 6 |
| real Spider | legacy vocab name | yes | 4 |
| real Spider | wirlernenonline (migration) | no | 3 |
| — | — | no | 1 |

> **Core rule (final):** A row is a **real Quelldatensatz** if
> `LRT = Quelle` **or** `general_identifier` is set — **regardless** of
> `replicationsource`. `replicationsource = wirlernenonline_spider` only means
> "loaded in via the WLO migration", **not** "not a real record". The
> few mis-tagged real sources (`gi` set, but LRT≠Quelle, e.g. bpb)
> are the actual correction candidates in edu-sharing.

## 4. Reconciliation / data quality

| Finding | Number | Assessment |
|---|---|---|
| live crawlers without GitHub code | **0** | ✅ clean |
| `general_identifier` ↔ GitHub | **38/38 valid** | ✅ clean |
| CSV ↔ GitHub | **53/55** | ⚠️ 2 discrepancies |
| CSV spiders not in GitHub | `ki_campus_spider`, `zum_dwu_spider` | ⚠️ presumably renames (GitHub has `dwu_spider`) |
| dormant GitHub crawlers | **9** | ⚠️ reactivate or document as decommissioned |
| orphaned legacy UUIDs | **12** | ⚠️ maintain / decommission |

---

## 5. Segments in the app (filter "Type of source")

The data truth (`truth.json`, **4,229 records**) can be filtered by these
meaningful categories (snapshot numbers):

| Filter label | Criterion | Count |
|---|---|---|
| **Crawler sources (real crawlers)** | `kind = crawler`, **excluding** WLO spiders (`wirlernenonline_spider`, `…_gsheet_spider`) | **53** |
| **Spider-bound only (without WLO)** | `general_identifier` set **OR** `replicationsource ≠ wirlernenonline_spider` (real binding) | **127** |
| **WLO data migration** | `replicationsource = wirlernenonline_spider` **or** Spider ∈ WLO set | **199** |
| **Quelldatensatz only (without Bezugsquelle)** | node, without Bezugsquelle | **167** |
| **Quelldatensatz + Bezugsquelle** | node **and** Bezugsquelle (intersection) | **1,165** |
| **Bezugsquelle only (without Quelldatensatz)** | facet without Quelldatensatz (= "pure Bezugsquellen") | **2,885** |
| **manually created** | `kind = manuell` | **1,289** |

> **Bezugsquelle numbers — important:** "Bezugsquelle only" = **2,885** (pure, without
> Quelldatensatz). The **distinct Bezugsquellen TOTAL = 3,554** (>3000) results
> from 2,885 pure **+ 669** Bezugsquellen that also have a Quelldatensatz
> (in "Quelldatensatz + Bezugsquelle"). Both numbers appear as KPIs on the
> Stats page ("pure Bezugsquellen" and "Bezugsquellen total" respectively).

> **WLO spiders as crawlers:** `datencrawler.csv` lists `wirlernenonline_spider`
> and `wirlernenonline_gsheet_spider` as crawler rows. These are **not real
> content crawlers**, but migration/import → they are excluded from "real crawlers"
> and listed under "WLO data migration".

> Note on the intersection: the 1,165 are **record units**; in distinct
> Bezugsquellen there are **684**, "clean" (without secondary/Blacklist) **664** — see
> Stats page "Sources & Origin".

---

## 6. Reproduction (queries)

- **GitHub list:** `GET api.github.com/repos/openeduhub/oeh-search-etl/contents/converter/spiders`
  → files `*_spider.py`.
- **Skohub:** `GET https://vocabs.openeduhub.de/w3id.org/openeduhub/vocabs/sources/index.json`
  → `hasTopConcept[]` with `id` (UUID), `prefLabel.de`.
- **Live spiders + counts:** NGSearch facet `ccm:replicationsource` (`ngsearchword:["*"]`, `contentType=ALL`).
- **Content types of a spider:** criterion `ccm:replicationsource = <spider>` + facet
  `ccm:oeh_lrt_aggregated`; `pagination.total` = object count.
- **Crawler binding:** `ccm:general_identifier` on the Quelldatensätze (`quellen_nodes.json`).
- **Team4:** `datencrawler.csv`, column `Crawler (Spider)`.

Caches in the repo: `quellen-analyse/raw/cache_facet_spider.json`, `quellen_nodes.json`,
`vocab_sources.json`. Engine: `quellenerschliessung-app/backend/truth.py`.
