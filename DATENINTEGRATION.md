# Datenintegration der Quellensteckbriefe-App

_Wie die App alle Informationsquellen zu einer „Datenwahrheit" zusammenführt,
welche Daten sie verwendet, wie sie aktualisiert werden und wie öffentliche von
internen Informationen getrennt sind._

---

## 1. Überblick in einem Bild

```
  LIVE (WLO-Produktion, abrufbar)            STATISCH (manuell gepflegt)
  ─────────────────────────────────         ───────────────────────────────
  • Bezugsquellen-Facette                    • datencrawler.csv
    (ccm:oeh_publisher_combined + Counts)      (Crawler-Steckbriefe + Feld-
  • Spider-Facette                             Erzeugung, ~53 Crawler)
    (ccm:replicationsource + Counts)         • quellen_korrektur.csv
  • Quelldatensätze (LRT=Quelle, volle MD)     (Whitelist/Blacklist)
  • dominanter Publisher je Spider           • Skohub-Vokabular (Quell-Namen)
            │                                          │
            ▼  fetcher.py (Live-Abruf)                 │
   raw/*.json  +  data/replication_publisher_gap.csv   │
            └──────────────┬───────────────────────────┘
                           ▼  truth.py  (6 Join-/Bereinigungs-Regeln)
                   data/truth.json   ← kanonische Quell-Records
                           ▼  app.py (FastAPI, nur lesend)
                   /api/...  →  Frontend (Kacheln, Steckbriefe, Statistik)
```

**Kernidee:** Eine **kanonische „Quelle" je realer Quelle**, zusammengesetzt aus
mehreren Quellen, mit **Feld-Provenienz** (woher kommt jeder Wert) und
**Public/Internal-Trennung**.

---

## 2. Welche Daten werden verwendet?

| # | Datenquelle | Art | Was sie beiträgt | Frische |
|---|---|---|---|---|
| 1 | **Bezugsquellen-Facette** `ccm:oeh_publisher_combined` | live (API) | Liste aller Bezugsquellen + **Inhaltsanzahl** je BQ | bei Refresh |
| 2 | **Spider-Facette** `ccm:replicationsource` | live (API) | aktive Crawler + Inhaltsanzahl je Crawler | bei Refresh |
| 3 | **Quelldatensätze** (`ccm:io`, LRT=Quelle) | live (API) | Titel, URL, Beschreibung, Lizenz, OER, Fach, Stufe, Sprache, Keywords, Vorschaubild, `general_identifier`, Erschließungsstatus … | bei Refresh |
| 3b | **versteckte Quelldatensätze** (Node-API, ID aus CSV-Spalte „Quelldatensatz (Prod)") | live (API, 1 Call/ID) | Metadaten + **Vorschaubild** für Crawler, deren Quelldatensatz NICHT such-sichtbar ist (anderer LRT, z. B. bpb) → `extra_nodes.json` | bei Refresh |
| 4 | **dominanter Publisher je Spider** | live (API, 1 Call/Spider) | „echte" Bezugsquelle eines Crawlers (statt Platzhalter) | bei Refresh |
| 5 | **datencrawler.csv** | statisch (Team4-Excel-Export) | Crawler-Steckbrief: Recht (robots.txt, TDM §44b, AGB, Lizenz-Check), Urheber + **109 Feld-Erzeugungs-Status** je Crawler; intern: Zustand, Bemerkungen, GitHub, Crawl-Daten, Vertrag | manuell |
| 6 | **quellen_korrektur.csv** | statisch (kuratiert) | Whitelist/Blacklist (Dublette/„keine echte Quelle"), Node↔BQ-Overrides | manuell |
| 7 | **Skohub-Vokabular** `…/vocabs/sources` | live (selten) | Klarnamen für URI-Legacy-Spider | bei Refresh |

> Quellen 1–4 + 7 sind **live abrufbar** (Refresh-Job). Quellen 5–6 sind
> **manuelle Pflege** und werden vom Refresh **nicht** überschrieben.

---

## 3. Die Zusammenführung (Datenwahrheit) — `truth.py`

Eine kanonische Quelle entsteht durch Join über mehrere Schlüssel
(Präzedenz von oben nach unten):

| Join-Schlüssel | verbindet |
|---|---|
| **Spider-Name** (`general_identifier` am Quelldatensatz ↔ `Crawler (Spider)` in datencrawler.csv ↔ Skohub) | Crawler-Steckbrief ↔ Quelldatensatz ↔ Vocab-Name |
| **`publisher_combined`** (bzw. dominanter Spider-Publisher) | Quelldatensatz ↔ Bezugsquelle ↔ Inhaltsanzahl |
| **nodeId** | Korrekturliste (Whitelist/Blacklist), Identität |

### Drei Arten kanonischer Records
1. **Crawler-Quelle** — Anker = Spider; vereint datencrawler.csv-Steckbrief +
   passenden Quelldatensatz + Bezugsquelle + Inhaltsanzahl.
2. **Manuelle Quelle** — Anker = Quelldatensatz ohne Crawler-Bindung.
3. **Nur Bezugsquelle** — Facette ohne eigenen Quelldatensatz (Schlagwort + Count).

### Sechs Regeln, die saubere Daten erzeugen
1. **Crawler-Bezugsquelle = dominanter Publisher** seines Contents (Regel/Quelle 4).
   Der Migrations-Platzhalter „WirLernenOnline" wird dabei **verworfen**.
2. **`wirlernenonline_spider` ist keine Crawler-Bindung**, sondern die Herkunft
   des Datensatz-Knotens (Alt-Migration) → zählt nicht als Crawler. Die echte
   Bindung steht in `general_identifier`.
3. **Konsolidierung je Spider:** Mehrere Quelldatensätze desselben Crawlers →
   **ein** Record (bester Knoten), keine Karten-Dubletten.
4. **Inhaltsanzahl je Bezugsquelle nur 1×** (am Primär-Record). Weitere
   Datensätze derselben BQ = **Zweit-Datensatz** (0 Inhalte, Flag) → keine
   Doppelzählung.
5. **URI-Legacy-Spider** werden über das Skohub-Vokabular zu Klarnamen aufgelöst.
6. **Korrekturliste**: Blacklist-Knoten werden markiert (Dublette/„keine echte
   Quelle"), Whitelist bevorzugt.

### Feld-Provenienz
Jeder öffentliche Wert trägt seine Herkunft, sichtbar im Steckbrief als Tag:
`WLO-API` · `WLO-API (Facette)` · `datencrawler.csv`. So ist transparent, ob ein
Wert aus der Live-API oder aus der kuratierten Liste stammt.

---

## 4. Aktualisierung — Live-Refresh

Die App liefert einen **vorausberechneten Snapshot** (`truth.json`) aus
(schnell, kein API-Call pro Request). Aktualisiert wird über einen
**Hintergrund-Job**:

```
[UI] 🔄 Aktualisieren  (nur Team-Login)
   └─ POST /jobs/refresh         (Passwort nötig)
        └─ fetcher.refresh_all()  : Facetten → Quelldatensätze → Publisher/Spider → Vocab
        └─ truth.main()           : baut data/truth.json neu (+ generatedAt-Zeitstempel)
        └─ _load()                : lädt den Snapshot in den Speicher
   └─ GET /jobs/latest            : Fortschritt (Prozent + Meldung), Polling im Frontend
```

- Dauer ~2 Min (v. a. 119 Spider-Einzelabfragen für die dominanten Publisher).
- Der **Datenstand** (`generatedAt`) wird im Header als „Datenstand: …" angezeigt.
- Manuelle Alternative: `truth.py` direkt laufen lassen, dann
  `POST /api/admin/reload`.
- **Nicht** live aktualisiert: `datencrawler.csv` und `quellen_korrektur.csv`
  (manuelle Pflege).

---

## 5. Öffentlich vs. intern

Die Trennung ist **serverseitig** (zentral in `field_policy.py`); öffentliche
Endpoints liefern interne Felder **nie** aus.

| Öffentlich (Datengeber/Datennehmer) | Intern (Team-Passwort) |
|---|---|
| Grundinfos (Titel, URL, Beschreibung, Fach, Stufe, Inhaltsanzahl, Vorschaubild) | Entwicklervermerke, **genauer Zustand**, Crawl-Daten, GitHub |
| Lizenz/OER + **KI-Nutzung & Recht** (robots.txt, TDM §44b, AGB, Lizenz-Check) | genauer **Erschließungsstatus**, Workflow-Status, Node-ID, replicationsource |
| **Metadaten-Erzeugung** je Crawler-Feld (gescraped/hard-coded/gemappt …) | **Vertrag/Vereinbarung** (ob WLO einen Vertrag hat) |

Refresh-/Reload-Endpoints sind ebenfalls passwortgeschützt.

---

## 6. Dateien

```
backend/
  fetcher.py        # Live-Abruf (Facetten, Quelldatensätze, Publisher/Spider, Vocab)
  truth.py          # Datenwahrheit-Engine → data/truth.json (+ generatedAt)
  field_policy.py   # EINE Stelle: public vs. internal
  app.py            # FastAPI: Lese-API + /jobs/refresh + /jobs/latest + Auth
  data/truth.json   # Snapshot (generiert)
quellen-analyse/    # gemeinsame Caches (raw/*.json, data/replication_publisher_gap.csv)
```

Für die fachliche Hintergrund-Analyse (Datenqualität, Dubletten, Begriffe) siehe
`quellen-analyse/BERICHT-Quellen-Datenlandschaft.md`.
