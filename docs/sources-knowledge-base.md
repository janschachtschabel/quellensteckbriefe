# Sources in WLO — Knowledge Base & Presentation Template

> **Purpose:** Foundation for a detailed presentation about *sources* in WLO/edu-sharing.
> It explains the terminology, the data representation, the bindings/links, the problems
> of accurate and consistent data management — and also considers future needs (e.g. AI
> usage permission) as well as measures for a cleaner implementation.
>
> **Audience:** Editorial team, metadata/data-model owners, development, management.
>
> **How to use this template:** Each `##` heading ≈ one slide block. The bullet points
> are slide content; the body text and the *speaker note/discussion* boxes are narration.
> Numbers are a **snapshot** (as of 2026-06-24, can be updated live) and illustrative.

**Contents**
1. [What this is about (management summary)](#0-management-summary)
2. [What is a source — and how does it differ from content?](#1-was-ist-eine-quelle)
3. [How are sources represented? (Overview)](#2-wie-werden-quellen-abgebildet)
4. [Quelldatensätze](#3-quelldatensaetze)
5. [Bezugsquelle](#4-bezugsquelle)
6. [Erschließungsweg & Spider/Crawler](#5-erschliessungsweg-spider)
7. [Data representation: field map](#6-datenabbildung-felder-map)
8. [Where does the truth of the information live?](#7-wo-liegt-die-wahrheit)
9. [Problem catalogue](#8-problemkatalog)
10. [Future needs: AI, rights, usage permissions](#9-zukunft-ki-rechte)
11. [Why corrections are only partially possible](#10-warum-korrektur-schwer-ist)
12. [Proposals: a clean target state](#11-vorschlaege)
13. [Appendix: glossary, field reference, numbers snapshot](#12-anhang)

---

<a id="0-management-summary"></a>
## 0. What this is about (management summary)

**Core message:** In WLO, a "source" is **not a clearly defined, firmly anchored object**,
but is represented in **several, parallel and partly contradictory ways**
(Quelldatensatz, Bezugsquelle, Spider/Erschließungsweg). There are **no enforcing
workflows** and **no fixed bindings** — fields are assigned freely. This leads to
**inconsistent data management**: duplicates, missing or incorrect typing, loose or
incorrect links, records that are hard to correct.

**Why this matters:**
- *Search and filter quality* (users can only unreliably find "all content of a source").
- *Transparency & statistics* (how many pieces of content does a source really have?).
- *Legal certainty* (upcoming requirements: AI usage permission, TDM reservation §44b, license check).
- *Maintainability* (corrections are currently laborious or blocked).

> 🎤 *Speaker note:* The presentation does not intend to assign blame — the diversity has grown
> historically (migrations, different crawler generations, free editorial work). The goal is a
> **shared understanding** and a **roadmap** towards fixed bindings and clear definitions.

---

<a id="1-was-ist-eine-quelle"></a>
## 1. What is a source — and how does it differ from content?

**Working definition (preliminary):**
> A **source** is the *origin/provider context* of a piece of content — the place from which an
> educational material originates or that provides it (portal, platform, database, publisher,
> institution, channel, individual author).
> A piece of **content** is the individual educational material itself (video, worksheet, learning path,
> explanation, course …).

**Source vs. content — the distinction:**

| | Source | Content |
|---|---|---|
| What | Provider/origin | individual material |
| Example | "Bundeszentrale für politische Bildung" | "Dossier Erinnerungsorte" |
| Granularity | aggregated (many pieces of content) | atomic (one material) |
| Purpose | ordering, origin, inheritance | learning use |

> 💬 **Open discussion (deliberately not conclusively resolved):** What exactly is the "source"
> in the case of **platforms**? Examples where the community is divided:
> - **YouTube** as a platform vs. an **individual YouTube channel** vs. the **publisher/author** behind the channel.
> - **OERSI / media libraries** (which already aggregate many providers themselves) — is the source OERSI or the original provider?
> - **Publisher vs. product** (e.g. "Deutsche Welle" vs. the course "Nicos Weg").
>
> → **The term "source" is not conclusively defined.** This is the *root* of many
> downstream problems: without a clear, shared definition, consistency cannot be enforced.

**Consequence for the presentation:** First clarify the definition (governance), then the technology.

---

<a id="2-wie-werden-quellen-abgebildet"></a>
## 2. How are sources represented? (Overview)

Today, sources are represented via **three mechanisms that exist side by side**, which
overlap but are not congruent:

```
        ┌──────────────────────────────────────────────────────────┐
        │                        SOURCE                            │
        └──────────────────────────────────────────────────────────┘
               │                     │                     │
   (1) Quelldatensatz        (2) Bezugsquelle      (3) Erschließungsweg
   = content with            = publisher keyword    = Spider/Crawler binding
     content type "source"     (free text on content) (general_identifier /
   (own ccm:io object)                                  replicationsource)
```

| Mechanism | Where stored | Carries | Mandatory? |
|---|---|---|---|
| **Quelldatensatz** | own `ccm:io` object (content type = source) | metadata, Bezugsquelle, Spider | no, freely creatable |
| **Bezugsquelle** | free-text field on content **and** Quelldatensätze | source name (as tag) | no, encouraged |
| **Erschließungsweg/Spider** | fields on Quelldatensatz/content | crawler/import origin | no, inconsistent |

> 🎤 *Speaker note:* None of the three paths is complete on its own. Only their **combination**
> yields a picture — but it is precisely this combination that is currently loose, manual and error-prone.

---

<a id="3-quelldatensaetze"></a>
## 3. Quelldatensätze

**Definition:** A **Quelldatensatz** (source dataset) is a normal piece of content (`ccm:io`) whose **content type
(LRT) = "source"**. It represents the source as its own object in the system.

**Properties / what it can hold:**
- complete **metadata** (title, description, URL, license, subjects, educational levels, author …)
- **Bezugsquelle** (publisher tag, see section 4)
- **Spider/Erschließung binding** (see section 5)
- preview image, quality features

**What Quelldatensätze are used for:**
- **Metadata inheritance during crawling** — the crawler can reuse/inherit fields of the
  Quelldatensatz for the generated content.
- **Ordering instrument** — structuring the content sets (often additionally in folders).
- **Visualization for users** — the source becomes visible as its own, discoverable object.

**Important limitations (current state):**
- A Quelldatensatz **can be regarded as content** — but: **you cannot filter "by
  content"** to cleanly separate sources from genuine learning materials (there is no
  reliable distinguishing feature beyond the freely settable LRT).
- **Freely creatable** — there are **no workflows in the editorial process that enforce
  or encourage creation.** Consequence: Quelldatensätze are created inconsistently, incompletely, sometimes not at all.

> ⚠️ **Rule that is not enforced today:** If the content type "source" is set,
> *no further content types may be set* (otherwise the record is a source *and*
> content at the same time → not distinguishable). Today exactly such mixed records exist.

---

<a id="4-bezugsquelle"></a>
## 4. Bezugsquelle

**Definition:** The **Bezugsquelle** (acquisition source) is the **second way** to represent a source:
a **freely assignable keyword** with the **name of the source**, attached to content (and
Quelldatensätze).
*(edu-sharing field: `ccm:oeh_publisher_combined`.)*

**Properties:**
- **Freely assignable** (free text) — no controlled vocabulary.
- **Usable in the search box** — users can search by the Bezugsquelle.
- **Connection source ↔ content:** By **tagging the content** with the Bezugsquelle,
  **statements about the number of content items** become possible ("source X has N pieces of content") and a bridge between
  source and its content is established.
- This way the **Bezugsquelle is attached in two places**:
  1. on the **content** (→ countable set of content per source),
  2. on the **Quelldatensätze** (→ connects the Quelldatensatz with "its" publisher name).
- **Curation masks**: At the end of the content curation masks there are fields that
  **encourage but do not enforce** entering the Bezugsquelle.

**Logic (today, simplified):**
- Content of a Bezugsquelle is merged via the **identically worded free text**
  (normalization across lower/upper case and spaces, but no ID).
- The **number of content items per Bezugsquelle** comes from the search facet over the publisher field.

> ⚠️ **Weakness due to free text:** "Wikipedia", "Wikipedia – Die freie Enzyklopädie",
> "Wikipedia (deutschsprachige Ausgabe)" are three *different* Bezugsquellen, although
> the same source is meant. Without an ID, **duplicates and scatter** arise.

---

<a id="5-erschliessungsweg-spider"></a>
## 5. Erschließungsweg & Spider/Crawler

In addition to the content-related source, the **Erschließungsweg** (path of acquisition) plays a role: **how** did a
piece of content get into the system?

**Automated acquisition / data imports (crawlers)** are connected to Quelldatensätze
(and content) as **Spider tags**. Fields used:

| Field | On which object | Meaning |
|---|---|---|
| `ccm:general_identifier` | **Quelldatensatz** | crawler/Spider binding of the source |
| `ccm:replicationsource` | **content** | origin/Erschließungsweg of the individual piece of content |

**Further observations (current state):**
- Content sets are usually additionally structured separately in **folders**.
- **Spider/Crawler can reuse the metadata of the content record** (inheritance, see section 3).
- **`wirlernenonline_spider`** is *not* a real crawler, but a **migration marker** —
  it appears on objects that were imported via the WLO data migration.
- **Legacy sources**: There are still **lists with old sources** (vocabulary/Skohub URIs,
  form `…/vocabs/sources/<uuid>`). **Meaning and origin are partly unclear** — and it is
  open *which of them are still actively used in the system.*
- **Data migrations** were partly **stored as sources** (see problem catalogue).
- **Real Spider/Crawler are only a fraction**: Of all "source-like" entries, only
  a minority is bound via a real, active crawler.

> ❗ **Inconsistent field usage:** `general_identifier` and `replicationsource` are **not
> always set consistently and correctly** — partly incorrect field usage, partly missing, partly
> migration marker instead of real binding.

> ❗ **Missing machine-readable field provenance:** There is **no machine-readable information**
> about **how** a field was created during content generation (hardcoded / scraped by the crawler
> / generated by WLO / manual). This makes trust, audit and correction enormously difficult.

---

<a id="6-datenabbildung-felder-map"></a>
## 6. Data representation: field map

**Concept → field → object → logic** (simplified representation; verify the exact `ccm:` keys against the
MDS schema):

| Concept | Field (edu-sharing) | On object | Logic / note |
|---|---|---|---|
| Content | `ccm:io` (object type) | — | every material |
| Content type / LRT | Learning Resource Type (`ccm:oeh_lrt_aggregated`) | content | value **"source"** ⇒ Quelldatensatz |
| Quelldatensatz | (LRT = "source") | content | own object, represents the source |
| Bezugsquelle | `ccm:oeh_publisher_combined` | content **+** Quelldatensatz | free-text tag, search facet → number of content items |
| Spider binding | `ccm:general_identifier` | Quelldatensatz | crawler/source binding |
| Erschließung origin | `ccm:replicationsource` | content | crawler name **or** migration marker **or** legacy vocab URI |
| Migration marker | `replicationsource = wirlernenonline_spider` | content/Quelldatensatz | **no** real crawler binding |
| Legacy source | `replicationsource = …/vocabs/sources/<uuid>` | content | old vocabulary entry, meaning partly unclear |

**Derived rule "real binding":**
> A source is **genuinely crawler/Spider-bound** if
> `general_identifier` is set **OR** `replicationsource ≠ wirlernenonline_spider`.
> (Only `replicationsource = wirlernenonline_spider` = pure migration, **no** real binding.)

**Three views that must be brought together:**
1. **GitHub crawler code** (which Spiders exist technically)
2. **Live fields** (`replicationsource`/`general_identifier` on the objects)
3. **Vocabulary/Skohub** (human names of the legacy sources)

> 🎤 *Speaker note:* The "data truth" only emerges through the **join** of these three views —
> and it is precisely this join that is today neither anchored in the system nor enforced.

---

<a id="7-wo-liegt-die-wahrheit"></a>
## 7. Where does the truth of the information live?

**Quantitative picture (snapshot, illustrative):**
- **Quelldatensätze** (content type = source, search-visible): ~**1,300**
- **distinct Bezugsquellen** (publisher tags): ~**3,500**
- **Overlap** Quelldatensatz ↔ Bezugsquelle: only a **fraction** (~700 clean
  primary assignments; the rest are secondary records, blacklist duplicates or pure tags)
- **Real crawlers/Spiders:** only ~**50** active — the vast majority of "sources" is *not*
  bound via a running crawler.

→ **There is no single "place of truth".** Quelldatensatz, Bezugsquelle and Spider
each paint an *incomplete, partly contradictory* picture.

**Core inconsistencies:**
- **Quelldatensätze are not always recognizable as such** (content type "source" missing) — *or*
  **content is incorrectly marked as Quelldatensätze.** There are **no aids/tools for
  differentiation** that automatically support this.
- **For Spiders** a wide range of problems:
  - missing link between Quelldatensatz and Spider,
  - data migrations that are stored as sources,
  - the field logic (where the Spider is "attached") is not implemented consistently.
- **Sources that are hard to delimit:** With **bulk acquisitions** (e.g. many **YouTube channels**
  or **RSS feeds**) it is hard to say what the "one" source is.
  → A **platform field** could help to cleanly separate unclear assignments between e.g. *YouTube*
  (platform) and a *YouTube channel* (provider).
- **Bezugsquellen with only one or hardly any content** — usually **not a real source**, but
  a tagging artifact or single material.
- **Duplicates** on several levels: same **titles**, same **URL**, same/similar
  **description texts**.
- **A single piece of content represents an entire Bezugsquelle** (system effect): If a
  Bezugsquelle had no clean Quelldatensatz, a randomly first-processed *single piece of content*
  "inherited" the entire content count of the Bezugsquelle (e.g. a grammar explanation as
  "Wikipedia", a single course as "Deutsche Welle"). → shows how loose the binding is.

---

<a id="8-problemkatalog"></a>
## 8. Problem catalogue (compact)

| # | Problem | Effect | Level |
|---|---|---|---|
| P1 | "Source" not conclusively defined | no enforceable consistency | Governance |
| P2 | Three parallel representation paths, not congruent | contradictory views | Model |
| P3 | Free-text Bezugsquelle (no ID) | duplicates, scatter | Model |
| P4 | No enforcing workflows when creating/tagging | incomplete/missing data | Process |
| P5 | Source vs. content not distinguishable (LRT free, mixed types) | incorrect typing | Model/Process |
| P6 | Spider fields used inconsistently/incorrectly | loose/incorrect binding | Data |
| P7 | Migration (`wirlernenonline_spider`) as "source" | pseudo-sources | Data |
| P8 | Legacy vocabulary sources of unclear meaning | legacy burden in the system | Data |
| P9 | No machine-readable field provenance | no audit/trust | Model |
| P10 | Bulk acquisition (YouTube/RSS) hard to delimit | unclear source | Model |
| P11 | Bezugsquellen with ~0 content | tagging artifacts | Data |
| P12 | Duplicates (title/URL/description) | multiple counting, fuzziness | Data |
| P13 | Incomplete/erroneous metadata on the Quelldatensatz | poor quality/inheritance | Data |
| P14 | Correction blocked by Spider binding | errors remain | Process/Technical |

---

<a id="9-zukunft-ki-rechte"></a>
## 9. Future needs: AI, rights, usage permissions

The source is the **natural anchor point for legal and usage-related metadata** —
many rights apply per provider, not per individual piece of content. Upcoming needs:

- **AI usage permission / usage permissions:** May the content of a source be used for AI training,
  RAG/retrieval, generation? (explicit, machine-readable permission per source)
- **TDM reservation (§ 44b UrhG):** machine-readable opt-out/opt-in for text-and-data-mining use.
- **`robots.txt` / terms of service / terms of use / license check / API terms of use:** today
  partly captured in the crawler profile, but **not anchored in a structured way at the source** and
  **not inherited**.
- **Provenance of the rights statement:** where does the permission come from (provider declaration, editorial
  review, license file)?

> 🎤 *Discussion:* These fields must reside **at the source**, be **machine-readable** and be
> **inherited** to the content — otherwise every AI pipeline must check per individual piece of content, which does not
> scale. A prerequisite for this is a **stable, unambiguous source** (see proposals).

**Cross-cutting:** Here too, the current problems (incomplete/erroneous
metadata on the Quelldatensatz, loose binding) block the clean storage of rights/AI information.

---

<a id="10-warum-korrektur-schwer-ist"></a>
## 10. Why corrections are only partially possible

- **Spider binding blocks editing:** Quelldatensätze that are bound to a Spider/Crawler
  are **write-protected/blocked** — corrections to metadata, type or Bezugsquelle
  are then not readily possible. *Errors remain.*
- **Duplicate/dependent records:** A correction in one place (content) does not automatically
  propagate to the Quelldatensatz or the Bezugsquelle, and vice versa.
- **No differentiation tools:** Without automatic support, every correction must be checked
  manually (source vs. content, duplicate vs. real source).
- **Legacy/migration:** With migrated or legacy vocabulary sources it is often unclear *whether* and
  *how* corrections may be made without breaking other links.

> ⚠️ **Core tension:** The Spider binding protects automated data from accidental
> overwriting — but at the same time prevents necessary editorial corrections. This is a
> **rights/workflow design problem**, not a pure data problem.

---

<a id="11-vorschlaege"></a>
## 11. Proposals: a clean target state

Based on the current state — structured into **quick wins**, **structural measures** and
**governance**. Each measure addresses concrete problems (P#).

### A. Governance / definition (prerequisite for everything)
1. **Define "source" bindingly** — including the platform question (YouTube vs. channel vs.
   publisher, aggregators like OERSI). Decision tree + examples. *(P1, P10)*
2. **Codify the differentiation rule:** LRT "source" is **exclusive** (no further
   content types). *(P5)*

### B. Fixed bindings instead of free text (structural)
3. Introduce a **source register with stable IDs** (controlled vocabulary): each source = one
   entry with ID, name, URL, platform type. Bezugsquelle and Spider bind to **this ID**
   instead of free text. *(P3, P11, P12)* — eliminates duplicates and scatter at the root.
4. **Fixed binding Quelldatensatz ↔ content ↔ Spider** via the register ID (reference instead of
   identically worded string). *(P2, P6)*
5. Add a **platform field** (platform vs. provider/channel) to cleanly represent bulk acquisitions.
   *(P10)*

### C. Machine-readable provenance & rights
6. Store **field provenance in machine-readable form**: per field "how created" (hardcoded / crawler /
   WLO-generated / manual / inherited). *(P9)* — basis for audit and trust.
7. **Rights/AI schema at the source** (inheritable): AI usage permission, TDM reservation §44b,
   robots.txt, terms of service, license check, API terms — structured, with provenance. *(future, §9)*

### D. Workflow & rights
8. **Enforcing/encouraging workflows** in the editorial process: when creating a Quelldatensatz,
   mandatory/suggested fields (Bezugsquelle, platform, rights); for content, demand the Bezugsquelle
   more strongly. *(P4, P13)*
9. **Decouple Spider binding from write protection:** **allow** editorial correction of metadata/type/
   Bezugsquelle without losing the automated origin (e.g. an "editorially
   overwritten" marker + provenance). *(P14)* — addresses the correction blockade directly.

### E. Tools / ongoing maintenance
10. **Differentiation/validation tools:** heuristics/checks for "content incorrectly marked as
    source" and "source without content type", mixed types, Bezugsquellen with ~0 content. *(P5, P11)*
    → *Partly implemented:* The app's **team data-check filter** hides sorted-out and
    secondary records by default (clean customer view) and flags for review:
    secondary records (473), mixed types/mistagging (274), suspected duplicates via URL/title
    (112), Bezugsquelle with single content (2,104), Quelldatensatz without Bezugsquelle (169),
    thin metadata (87), incomplete binding (12). A team statistics chart
    "data problems" is congruent (1:1) with these filter options.
11. **Duplicate detection + merge workflow** (title/URL/description similarity, optionally
    embedding-supported as a *pre-sorting* with a human final decision). *(P12)*
12. **Legacy/migration cleanup:** inventory of the `…/vocabs/sources/<uuid>` sources and the
    `wirlernenonline_spider` legacy burdens — what stays, what gets mapped, what gets decommissioned. *(P7, P8)*

### Prioritization (proposal)
| Horizon | Measures | Effect |
|---|---|---|
| **Immediate** | 1, 2, 10, 11 | clarity + making errors visible |
| **Medium** | 3, 4, 5, 6, 9 | fixed bindings, correctable, auditable |
| **Strategic** | 7, 8, 12 | rights/AI-capable, sustainable maintenance |

> 🎤 *Closing speaker note:* The greatest leverage lies in **fixed bindings via a
> source register with IDs** (B) and **decoupling the correction blockade** (D9). Both make
> the system *consistently correctable* — the prerequisite for being able to store rights and AI information (§9)
> reliably at all.

---

<a id="12-anhang"></a>
## 12. Appendix

### Glossary
- **Content** — individual educational material (`ccm:io`).
- **Source** — origin/provider of a piece of content (term not yet conclusively defined).
- **Quelldatensatz** — content with content type "source"; represents the source as an object.
- **Bezugsquelle** — free-text publisher tag (`ccm:oeh_publisher_combined`) on content/Quelldatensatz.
- **Spider/Crawler** — automated acquisition; binds via `general_identifier` /
  `replicationsource`.
- **Migration marker** — `replicationsource = wirlernenonline_spider`; no real crawler binding.
- **Legacy source** — old vocabulary entry `…/vocabs/sources/<uuid>`.
- **Real binding** — `general_identifier` set OR `replicationsource ≠ wirlernenonline_spider`.
- **Secondary record** — a further record of the same Bezugsquelle (avoids double counting).
- **Duplicate** — multiple entries of the same source (title/URL/description).

### Field reference (verify against MDS)
| Field | Object | Purpose |
|---|---|---|
| `ccm:oeh_lrt_aggregated` (LRT) | content | content type; value "source" = Quelldatensatz |
| `ccm:oeh_publisher_combined` | content + Quelldatensatz | Bezugsquelle (free text) |
| `ccm:general_identifier` | Quelldatensatz | Spider/Crawler binding |
| `ccm:replicationsource` | content | Erschließung origin (crawler/migration/legacy) |

### Numbers snapshot (as of 2026-06-24, illustrative, can be updated live)
**Raw — all records (incl. sorted-out & secondary records):**
- total source records: ~4,219 · real crawlers (excl. WLO migration Spider): ~53
- distinct Bezugsquellen (search facet): ~3,579 · real Spider/Crawler binding (gi OR rs≠wlo): ~90–130
- WLO migration: ~197 · legacy vocab binding: ~33 · mis-tagged (binding, but LRT≠source): ~2
- content assignable to a source: ~304,800 · WLO prod total: ~318,650

**Visible in the "type of source" filtering** (sorted-out/blacklist always off; secondary records
are independent *objects* with a shared Bezugsquelle tag, only consolidated in the tag view):
- all sources: **3,721** (default, tag view) · of which crawlers ~69
- **with Quelldatensatz (object view): 1,242** — counts the QD nodes incl. secondary records (≈ API ~1,300, previously incorrectly 824)
- **with Bezugsquelle (tag view): 3,558** — distinct Bezugsquellen, ≤ 3,579 facet (previously incorrectly 3,976)
- overlap (QD ∩ BQ, object view): **1,087**
- Key: the same Bezugsquelle can have several independent Quelldatensätze (e.g. "YouTube" = 47 channels) → as objects they count individually (1,242), as a tag distinct (3,558). Each list shows in small print "N hidden".

**Team data check — markers** (only visible in the team filter; selectively turn off the hiding):
- secondary records: ~473 · Bezugsquelle with 1 content item: ~2,104 · thin metadata: ~87 ·
  incomplete binding: ~12 · sorted out (blacklist): ~80

> These numbers come from the data-truth engine of the source-profiles app
> (join of live API facets, crawler profiles, correction lists and vocabulary).
> Methodology & details: see `spider-landscape.md` and `data-integration.md`.

---

*This file is a **template/knowledge base**: sections = slide blocks, bullet points =
slide content, "speaker note/discussion" boxes = narration. Update the numbers before a live presentation.*
