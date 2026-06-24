# Spider-Gesamtbild — Quellen, Zahlen, Schichten

Stand-Snapshot: 2026-06-17. Reproduzierbar über die im Anhang genannten Abfragen.
Dieses Dokument führt **alle Informationsquellen zu „Spidern" (Crawlern)** zusammen
und erklärt, warum kursierende Spider-Zahlen (46 / 54 / 119 …) auseinandergehen —
sie messen **unterschiedliche Schichten** derselben Landschaft.

---

## 1. Die vier Informationsquellen

| Quelle | Was sie ist | Anzahl | Namensregime |
|---|---|---|---|
| **GitHub** `openeduhub/oeh-search-etl/converter/spiders` | implementierter Crawler-**Code** | **54** `*_spider.py` | technisch (`bpb_spider`) |
| **Live-API** `ccm:replicationsource` (Facette) | Herkunft **am einzelnen Inhalt** | **119** distinct | gemischt |
| **Skohub** `vocabs/sources` | Quell-**Namen** ↔ UUID | **145** Konzepte | menschlich (`DLRG`) |
| **`ccm:general_identifier`** (am Quelldatensatz) | echte Crawler-**Bindung** der Quelle | **38** distinct / 41 Records | technisch |
| **`datencrawler.csv`** (Team4-Pflege) | manuell kuratierte Crawler | **55** | technisch |

**Zwei Namensregime — wichtig:**
- **Technisch** (`*_spider`): GitHub-Code, `general_identifier`, CSV und der „moderne"
  Teil der Live-Herkunft. Direkt untereinander joinbar.
- **Menschlich + UUID** (Skohub): die `sources`-Vokabular-Namen (`DLRG`, `bpb`, …).
  Kein einziges Skohub-prefLabel ist ein technischer `_spider`-Name. Skohub dient
  v. a. dem **Auflösen der Legacy-UUID-Herkünfte** (siehe Schicht 3).

Die **119** Live-`replicationsource`-Werte teilen sich in **45 technische** (`_spider`),
**73 URI-Legacy** (`…/vocabs/sources/<uuid>`) und **1 sonstige**.

---

## 2. Drei Schichten (so lösen sich die widersprüchlichen Zahlen auf)

### 🟢 Schicht 1 — Aktive Crawler (der harte Kern): **45**
Haben GitHub-Code **und** erzeugen Live-Inhalte.
- **38** davon sauber per `general_identifier` an einen Quelldatensatz gebunden.
- **Alle 45** in der Team4-CSV gepflegt.
- **0** Live-Crawler **ohne** GitHub-Code → diese Schicht ist konsistent.

Das ist das „wir gehen von ~46 Spidern aus"-Bauchgefühl — jetzt belegt.

### 🟡 Schicht 2 — Implementiert, aber ruhend: **9**
GitHub-Code, aber **keine** Live-Inhalte:
`sample_spider` (Test), `oeh_spider`, `oeh_rss_spider`, `merlin_spider`,
`sodix_spider`, `zoerr_spider`, `mediothek_pixiothek_spider`,
`materialnetzwerk_spider`, `wirlernenonline_gsheet_spider`.
→ abgeschaltet / leer / Test = Altlast **oder** Potenzial.

### 🔵 Schicht 3 — Legacy-Herkunft (Alt-Migration): **73 URI-Werte**
Inhalte aus der Zeit **vor** der `_spider`-Konvention; Herkunft als
`http://w3id.org/openeduhub/vocabs/sources/<uuid>`.
- **61** über Skohub benennbar, **12 verwaiste UUIDs** (zeigen auf unbekannte /
  entfernte Vokabular-Einträge).

### Sonderfall — `wirlernenonline_spider` (Daten­migration WLO)
**Kein echter Crawler**, sondern der **Migrationsmarker** des Alt-Bestands.
- Hängt an **320 Objekten** (live).
- Davon **196 als Inhaltstyp „Quelle"** (= unsere Migrations-Quelldatensätze),
  **~124 andere Typen** (Tool 45, Webseite 40, Methoden 18, News 9, Bild 6,
  Video/Audio/Buch/Nachschlagewerk je 5 …; 28 Typen gesamt).
- 376 Typ-Treffer auf 320 Objekte → **56 Objekte mehrfach getaggt**.

---

## 3. Crawler-Bindung: `general_identifier` ↔ `replicationsource`

Zwei Felder am Quelldatensatz binden eine Quelle an einen Crawler — und sie meinen
**nicht dasselbe**:
- **`general_identifier`** = die **echte Crawler-Bindung** (technischer Spider, z. B. `bpb_spider`).
- **`replicationsource`** = die **Herkunft des Knotens** — oft der Migrationsmarker
  `wirlernenonline_spider`, manchmal ein echter Spider oder eine Legacy-Vocab-URI.

**Übersicht (Snapshot, je Quelle/Record):**
| | Anzahl |
|---|---|
| mit `general_identifier` | **41** |
| mit `replicationsource` | **287** |
| **beide gesetzt** | **35** |
| ⮑ davon **unterschiedlich** | **35 (= 100 %)** |
| ⮑ davon gleich | 0 |
| nur `general_identifier` | 6 |
| nur `replicationsource` | 252 |

**Befund A — beide gesetzt ⇒ immer unterschiedlich.** In allen 35 Fällen gilt
„echter Spider ↔ Migrationsmarker" (31× `gi=<spider>` / `rs=wirlernenonline_spider`,
4× `gi=<spider>` / `rs=Legacy-URI`). → Bei Doppelbelegung **immer `general_identifier`**
als Crawler werten, nie `replicationsource`.

**Befund B — die Rückrichtung: 86 echte Quellen haben NUR `replicationsource`.**
Von den 252 „nur replicationsource":
| Klasse | Anzahl | echt? |
|---|---|---|
| reine **WLO-Migration** (`wirlernenonline_spider`) | 166 | nein (Migration) |
| **echter Spider** nur via `rs` (`planet_schule_spider`, `zum_spider`, `bne_portal_spider` …) | 52 | **ja** |
| **Legacy-Vocab-Quelle** (Wikipedia, ZUM, Goethe-Institut, Bayerischer Rundfunk …) | 34 | **ja** |

→ Ein **reiner `general_identifier`-Filter (41) übersieht 86 echt gebundene Quellen!**

**Richtige Filter-Regel (Crawler-/Spider-Ansicht):**
> echte Bindung = `general_identifier` gesetzt **ODER** `replicationsource ≠ wirlernenonline_spider`

Das ergibt **127 echt gebundene Quellen** (41 via gi + 52 echter-Spider-nur-rs +
34 Legacy-nur-rs); **166** sind reine Migration. Die `replicationsource`-Legacy-URIs
(`…/vocabs/sources/<uuid>`) werden über das Skohub-Vokabular zu Klarnamen aufgelöst
(33 / 34 auflösbar). Visualisiert im Team-Statistik-Bereich „Spider-Bindung".

**Befund C — der Inhaltstyp (LRT=Quelle) als dritte Dimension.** `gi = echter Spider`
+ `rs = wirlernenonline_spider` ist **kein Widerspruch**, sondern eine **echte Quelle
aus der Datenmigration** (z. B. bpb). Entscheidend ist erst die Kombination mit dem
Inhaltstyp.

*Live-Kreuztabelle der WLO-Migration (`replicationsource = wirlernenonline_spider`, 320 Objekte):*
| `general_identifier` | LRT=Quelle | Anzahl | Bedeutung |
|---|---|---|---|
| echter Spider | **ja** | **31** | echte Quelle, migriert, korrekt getaggt |
| echter Spider | nein | **2** | echte Quelle, migriert, **falsch** getaggt (bpb-Fall, LRT=Webseite) |
| — | ja | **166** | als Quelle getaggt, migriert, **ohne** Crawler-Bindung |
| — | nein | **121** | reine Migrations-Inhalte (keine Quelle) |
| **Summe** | | **320** | **197 Quelle** / 123 nicht-Quelle |

*Vollständige Kreuztabelle aller 1.332 node-gebundenen Quelldatensätze (Snapshot):*
| `general_identifier` | `replicationsource` | LRT=Quelle | Anzahl |
|---|---|---|---|
| — | — | ja | 1.038 |
| — | wirlernenonline (Migration) | ja | 166 |
| — | echter Spider | ja | 52 |
| — | Legacy-Vocab-Name | ja | 34 |
| echter Spider | wirlernenonline (Migration) | ja | 28 |
| echter Spider | — | ja | 6 |
| echter Spider | Legacy-Vocab-Name | ja | 4 |
| echter Spider | wirlernenonline (Migration) | nein | 3 |
| — | — | nein | 1 |

> **Kernregel (final):** Eine Zeile ist ein **echter Quelldatensatz**, wenn
> `LRT = Quelle` **oder** `general_identifier` gesetzt ist — **unabhängig** von
> `replicationsource`. `replicationsource = wirlernenonline_spider` heißt nur
> „über die WLO-Migration eingespielt", **nicht** „kein echter Datensatz". Die
> wenigen mis-getaggten echten Quellen (`gi` gesetzt, aber LRT≠Quelle, z. B. bpb)
> sind die eigentlichen Korrektur-Kandidaten in edu-sharing.

## 4. Abgleich / Datenqualität

| Befund | Zahl | Bewertung |
|---|---|---|
| Live-Crawler ohne GitHub-Code | **0** | ✅ sauber |
| `general_identifier` ↔ GitHub | **38/38 valide** | ✅ sauber |
| CSV ↔ GitHub | **53/55** | ⚠️ 2 Abweichungen |
| CSV-Spider nicht in GitHub | `ki_campus_spider`, `zum_dwu_spider` | ⚠️ vermutlich Umbenennungen (GitHub hat `dwu_spider`) |
| ruhende GitHub-Crawler | **9** | ⚠️ reaktivieren oder dokumentiert stilllegen |
| verwaiste Legacy-UUIDs | **12** | ⚠️ nachpflegen / stilllegen |

---

## 5. Segmente in der App (Filter „Art der Quelle")

Die Datenwahrheit (`truth.json`, **4.229 Records**) lässt sich nach diesen
sinnvollen Kategorien filtern (Snapshot-Zahlen):

| Filter-Label | Kriterium | Anzahl |
|---|---|---|
| **Crawler-Quellen (echte Crawler)** | `kind = crawler`, **ohne** WLO-Spider (`wirlernenonline_spider`, `…_gsheet_spider`) | **53** |
| **nur Spider-gebunden (ohne WLO)** | `general_identifier` gesetzt **ODER** `replicationsource ≠ wirlernenonline_spider` (echte Bindung) | **127** |
| **WLO-Datenmigration** | `replicationsource = wirlernenonline_spider` **oder** Spider ∈ WLO-Set | **199** |
| **nur Quellendatensatz (ohne Bezugsquelle)** | Node, ohne Bezugsquelle | **167** |
| **Quellendatensatz + Bezugsquelle** | Node **und** Bezugsquelle (Schnittmenge) | **1.165** |
| **nur Bezugsquelle (ohne Quelldatensatz)** | Facette ohne Quelldatensatz (= „reine Bezugsquellen") | **2.885** |
| **manuell angelegt** | `kind = manuell` | **1.289** |

> **Bezugsquelle-Zahlen — wichtig:** „nur Bezugsquelle" = **2.885** (reine, ohne
> Quelldatensatz). Die **distinkten Bezugsquellen GESAMT = 3.554** (>3000) ergeben
> sich aus 2.885 reinen **+ 669** Bezugsquellen, die zugleich einen Quelldatensatz
> haben (in „Quellendatensatz + Bezugsquelle"). Beide Zahlen stehen als KPI auf der
> Stats-Seite („reine Bezugsquellen" bzw. „Bezugsquellen gesamt").

> **WLO-Spider als Crawler:** Die `datencrawler.csv` führt `wirlernenonline_spider`
> und `wirlernenonline_gsheet_spider` als Crawler-Zeilen. Das sind **keine echten
> Inhalts-Crawler**, sondern Migration/Import → sie werden aus „echte Crawler"
> ausgeschlossen und unter „WLO-Datenmigration" geführt.

> Hinweis zur Schnittmenge: die 1.165 sind **Datensatz-Einheiten**; in distinkten
> Bezugsquellen sind es **684**, „sauber" (ohne Zweit/Blacklist) **664** — siehe
> Stats-Seite „Quellen & Herkunft".

---

## 6. Reproduktion (Abfragen)

- **GitHub-Liste:** `GET api.github.com/repos/openeduhub/oeh-search-etl/contents/converter/spiders`
  → Dateien `*_spider.py`.
- **Skohub:** `GET https://vocabs.openeduhub.de/w3id.org/openeduhub/vocabs/sources/index.json`
  → `hasTopConcept[]` mit `id` (UUID), `prefLabel.de`.
- **Live-Spider + Counts:** NGSearch-Facette `ccm:replicationsource` (`ngsearchword:["*"]`, `contentType=ALL`).
- **Inhaltstypen eines Spiders:** Kriterium `ccm:replicationsource = <spider>` + Facette
  `ccm:oeh_lrt_aggregated`; `pagination.total` = Objektzahl.
- **Crawler-Bindung:** `ccm:general_identifier` an den Quelldatensätzen (`quellen_nodes.json`).
- **Team4:** `datencrawler.csv`, Spalte `Crawler (Spider)`.

Caches im Repo: `quellen-analyse/raw/cache_facet_spider.json`, `quellen_nodes.json`,
`vocab_sources.json`. Engine: `quellenerschliessung-app/backend/truth.py`.
