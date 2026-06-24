# WLO Quellenerschliessung — App

Übersicht über alle WLO-Quellen **und** Erzeugung von Quellensteckbriefen, für
**Datengeber, Datennehmer und Team**. Kombiniert bestehende kuratierte Listen
mit aktuellen API-Daten zu **einer Datenwahrheit** — mit Feld-Provenienz und
serverseitiger Trennung öffentlicher vs. interner Informationen.

## Was die App zeigt

Zwei Bereiche (Tabs): **📚 Quellen** und **📊 Statistiken**.

- **Übersicht** aller Quellen mit Filter (Art, Fach, Bildungsstufe, OER,
  Mindest-Inhaltszahl, **„nur Quellendatensatz"**, „nur mit Feld-Profil"),
  Volltextsuche und **Mehrfachauswahl** (Kacheln ankreuzen, „Seite auswählen").
- **Steckbrief** je Quelle:
  - *Grund- & Qualitätsinfos* (Titel, URL, Beschreibung, Lizenz, OER, Fächer,
    Bildungsstufen, Inhaltstyp, Inhaltsanzahl) — **jedes Feld mit Herkunfts-Tag**.
  - *Metadaten-Erzeugung* (für ~53 Crawler-Quellen): pro Feld ob aktiv und **wie
    erzeugt** (gescraped / hard-coded / via Mapping / LRMI / WP-JSON …).
  - *Interner Bereich* (🔒 nur mit Team-Passwort): Entwicklervermerke, genauer
    Crawl-/Erschließungsstatus, GitHub, Node-ID, replicationsource etc.
- **PDF-Steckbriefe** (jsPDF, WLO-Branding: Farbbalken-Header, Logo, EU/BMBF-
  Footer, Abschnitts-Tabellen + Feld-Erzeugungs-Tabelle) — **aus einer oder
  mehreren gewählten Quellen** in einem PDF. Wählbare Optionen in der Auswahl-
  Leiste: **Vorlage** (Standard ausführlich / Kompakt 1 Seite), **Vorschaubilder
  einbinden** (Thumbnail je Quelle, CORS-frei über `/api/thumb`-Proxy),
  **einzelne Dateien statt kombiniert** und – mit Team-Login – **interne Infos**.
- **Tabellen-PDF** (Quellenübersicht, Querformat) der aktuellen Filtermenge und
  **Statistik-PDF** (alle Verteilungen) — Buttons in der Export-Leiste.
- **Statistiken** (eigener Bereich, in Abschnitte gruppiert): Überblick-KPIs
  (u. a. **Inhalte WLO gesamt** ≈318k vs. **einer Quelle zuordenbar** ≈305k,
  **Bezugsquellen gesamt** distinct); **Herkunft** Quelldatensatz↔Bezugsquelle
  als Überschneidungs-Grafik; Inhaltsmengen; **Crawler nach Typ** + Metadaten-
  Erzeugung nach Methode + **Metadatenfelder: wie oft aktiv**; Datenabdeckung;
  Top-Listen. Die **Zuordnungs-Sicherheit** ist nur mit Team-Login sichtbar.
- **Maschinenlesbarer Export**: gesamte Filtermenge oder Auswahl als **CSV**
  (Semikolon, UTF-8 BOM) oder **JSON** (`/api/export.csv` · `/api/export.json`).
- **Footer** mit **Impressum / Datenschutz** als **In-App-Seiten** (scrollbares
  Overlay; Inhalt 1:1 von wirlernenonline.de übernommen, edu-sharing.net e.V.).

## Datenwahrheit — wie kombiniert wird

Eine kanonische „Quelle" je realer Quelle, gejoint über mehrere Schlüssel
(Präzedenz):

| Schlüssel | verbindet |
|---|---|
| Spider-Name (`general_identifier`/`replicationsource` ↔ `Crawler(Spider)` ↔ Skohub) | Crawler-Steckbrief ↔ Quelldatensatz ↔ Vocab-Name |
| `publisher_combined` / dominanter Spider-Publisher | Quelldatensatz ↔ Bezugsquelle ↔ Inhaltszahl |
| `nodeId` / Korrekturliste | Identität, Whitelist/Blacklist |

**Regeln, die saubere Daten erzeugen:**
- Bezugsquelle eines Crawlers = **dominanter Publisher seines Contents**
  (Platzhalter „WirLernenOnline" wird verworfen).
- `wirlernenonline_spider` ist **keine** Crawler-Bindung, sondern Knoten-Herkunft
  der Altmigration → nicht als Crawler gewertet.
- Inhaltszahl je Bezugsquelle wird nur **einmal** (am Primär-Record) verbucht;
  weitere Quelldatensätze derselben Bezugsquelle = **Zweit-Datensatz** (0 Inhalte,
  Flag) → keine Doppelzählung.
- Jeder öffentliche Wert trägt seine **Provenienz** (`WLO-API`, `datencrawler.csv`,
  `WLO-API (Facette)`).

**Eingebundene Quellen:** Live-API (Quelldatensätze, Bezugsquellen-/Spider-Facetten),
`datencrawler.csv` (Crawler-Steckbriefe + Feld-Erzeugung, aus Team4-Excel),
`quellen_korrektur.csv` (Whitelist/Blacklist), Skohub-Vokabular, dominanter
Publisher je Spider (aus der Analyse).

## Filterlogik „Art der Quelle" & Provenienz-Marker

Eine Quelle kann auf mehreren Wegen an einen Crawler gebunden sein. Zwei Felder am
Quelldatensatz sind entscheidend — und sie meinen **nicht** dasselbe:

- **`ccm:general_identifier`** = die **echte Crawler-Bindung** (technischer Spider, z. B. `bpb_spider`).
- **`ccm:replicationsource`** = die **Knoten-Herkunft** — oft der Migrationsmarker
  `wirlernenonline_spider`, manchmal ein echter Spider oder eine Legacy-Vocab-URI.

**Kernregel:** Die effektive Bindung ist **immer das Feld, das NICHT
`wirlernenonline_spider` ist** (`general_identifier` hat Vorrang, sonst
`replicationsource ≠ wirlernenonline_spider`). Ein Quelldatensatz ist eine **echte
Quelle**, wenn **`LRT = Quelle` ODER eine echte Bindung** vorliegt — **unabhängig**
davon, ob er über die Datenmigration eingespielt wurde (`replicationsource =
wirlernenonline_spider` heißt nur „migriert", nicht „kein echter Datensatz").

**Filter „Art der Quelle" (End-User, Default = Crawler)** — frei mit Fach/Stufe/
Lizenz/… kombinierbar (Backend verknüpft per **UND**):

| Option | Kriterium |
|---|---|
| Crawler (Spider) | `kind=crawler`, ohne WLO-Migrations-Spider |
| mit Quelldatensatz | `has_node=true` |
| Quelldatensatz + Bezugsquelle | `has_node=true` & `has_bezugsquelle=true` |
| nur Bezugsquelle (ohne Datensatz) | `has_node=false` & `has_bezugsquelle=true` |

**Prüf-/Herkunfts-Filter — nur nach Team-Login** (Fehlerkontrolle): WLO-Daten­übernahme
(`wlo_migration`) · über alte Verschlagwortung gebunden / „Legacy" (`LEGACY_BINDUNG`) ·
Datensatz ohne Typ „Quelle" / mis-getaggt (`TYP_NICHT_QUELLE`) · aussortiert
(`BLACKLIST`). Diese technischen Marker bleiben am Steckbrief als **Badge** sichtbar,
sind aber **kein** End-User-Filter. Die Statistik-Seite greift „Art der Quelle" als
Balkengrafik auf; die Provenienz-Marker erscheinen im Team-Bereich.

**Provenienz-Marker (Badges, öffentlich)** — an jeder Quelle sichtbar (Kachel + Steckbrief):
- **🔄 Datenmigration (WLO)** — über die Alt-Migration eingespielt.
- **🏷️ Legacy-Bindung** — Bindung über eine Legacy-Vocab-Quelle statt eines technischen Spiders.
- **⚠ Inhaltstyp ≠ Quelle** — echte Quelle, aber LRT≠Quelle (Korrektur-Kandidat in edu-sharing, z. B. bpb).

**Blacklist (Kuration in `quellen_korrektur.csv`):** Offensichtliche **Einzelmaterialien**
(Serien-Episoden wie „Extra en español | Folge X", Einzeltopics, Klexikon-Personen-
Artikel, Einzelvideos, einzelne Tests wie „Test - Mozart") und Dubletten werden als
`blacklist` markiert. Sie sind **keine Quellen** und werden daher **standardmäßig aus der
Quellenliste ausgeblendet** (Endpoint-Default; `show_blacklist=true` oder Filter
„aussortiert (Blacklist)" zeigt sie wieder). Heuristik: echte Bindung **+ 0 Inhalte** +
Titel-Muster (Folge/Episode/Test/„| Wir lernen online"/„- alpha Lernen" …) → manuell
geprüft. Echte Quellen (Portale, Datenbanken, YouTube-**Kanäle**) bleiben erhalten.

Volle Herleitung, Befunde und Kreuztabellen: [`SPIDER-GESAMTBILD.md`](SPIDER-GESAMTBILD.md).

## Sicherheit (öffentlich vs. intern)

Die Trennung ist **serverseitig**: öffentliche Endpoints liefern das `internal`-
Objekt **nie** aus. Interne Felder nur über Detail-Endpoint **mit gültigem
Team-Passwort** (Header `X-Team-Password` oder `?pw=`). Die Public/Internal-
Zuordnung steht zentral in [`backend/field_policy.py`](backend/field_policy.py).

- **Team-Login** (Passwort) schaltet interne Felder frei und schützt
  `/api/admin/reload`.
- **Live-Refresh** (`POST /jobs/refresh`, Button „🔄 Aktualisieren") ist
  **öffentlich** — er aktualisiert nur den Snapshot aus der öffentlichen WLO-API
  und gibt keine internen Daten preis (Concurrency-Guard gegen Parallel-Läufe).

## Konfiguration (`.env`)

Das Team-Passwort kommt aus der Umgebungsvariable **`QE_TEAM_PASSWORD`**
(Default `wlo-intern`). Lokal am einfachsten über eine `.env`-Datei im
`backend/`-Ordner — die App lädt sie beim Start (ohne Zusatz-Abhängigkeit;
echte Shell-Variablen haben Vorrang):

```bash
cp backend/.env.example backend/.env
# backend/.env:  QE_TEAM_PASSWORD=mein-passwort
```

Alternativ per Shell: `setx QE_TEAM_PASSWORD "…"` (dauerhaft) oder
`$env:QE_TEAM_PASSWORD="…"` (Sitzung). `.env` ist über `.gitignore`
ausgeschlossen; `backend/.env.example` ist die committebare Vorlage.

## Start

```bash
PY="C:/Users/jan/miniconda3/python.exe"
cd backend
"$PY" -m pip install -r requirements.txt        # einmalig
cp .env.example .env                            # Team-Passwort setzen (optional)
"$PY" truth.py                                   # baut data/truth.json
"$PY" -m uvicorn app:app --host 127.0.0.1 --port 8080
# -> http://127.0.0.1:8080  (Frontend)   ·   /docs (API)
```

Team-Login in der UI: oben rechts „🔒 Team-Login", Passwort `wlo-intern`.

## Tests

```bash
cd backend
"$PY" -m pip install -r requirements-dev.txt     # pytest + httpx (einmalig)
"$PY" -m pytest                                   # Unit + API-Integration + Golden-Snapshots
```

Die Tests laufen gegen das vorhandene `data/truth.json` und erzwingen ein bekanntes
Team-Passwort (unabhängig von `.env`). Die **Golden-Snapshots** (`tests/golden/`)
pinnen die exakte JSON-Ausgabe der Statistik-/Listen-Endpoints; nach einer
**bewussten** Verhaltens-/Datenänderung neu erzeugen mit
`"$PY" tests/golden/_generate.py`.

## Daten aktualisieren (Live-Refresh)

**Direkt in der App:** nach Team-Login oben rechts **„🔄 Aktualisieren"** — startet
einen Hintergrund-Job, der die Live-/Facetten-Daten neu abruft und `truth.json`
neu baut (~2 Min, Fortschrittsanzeige). Der Datenstand erscheint im Header.

Technisch:
```
POST /jobs/refresh   (Team-Passwort) → fetcher.refresh_all() + truth.main() + reload
GET  /jobs/latest    → Fortschritt/Status
```

`fetcher.py` zieht: Bezugsquellen-/Spider-Facette, alle Quelldatensätze,
dominanten Publisher je Spider, Skohub-Vokabular. **Nicht** überschrieben werden
`datencrawler.csv` und `quellen_korrektur.csv` (manuell gepflegt).

Ausführliche Erläuterung der Datenzusammenführung: **[DATENINTEGRATION.md](DATENINTEGRATION.md)**.

## Architektur

Jedes Modul hat **eine** Verantwortung (ein Grund, sich zu ändern):

```
quellenerschliessung-app/
├── backend/                  # FastAPI; Fachmodule mit je einer Verantwortung
│   ├── app.py                # Web-Layer: dünne Routen + Middleware + Thumb-Proxy
│   ├── config.py             # Konfiguration, Team-Passwort, Konstanten, Pfade
│   ├── store.py              # In-Memory-Datenhaltung (lädt data/truth.json)
│   ├── views.py              # Public/Internal-Serialisierung (Trust-Boundary)
│   ├── filtering.py          # Filterlogik der Quellenliste (rein)
│   ├── stats.py              # Statistik-Aggregation (/api/stats[/full|/team])
│   ├── refresh.py            # Live-Refresh als Hintergrund-Job
│   ├── field_policy.py       # EINE Stelle: welche Felder public vs. internal
│   ├── truth.py              # Datenwahrheit-Engine: Join/Records -> data/truth.json
│   ├── truth_loaders.py      # Einlesen aller Eingaben (CSV/JSON/Live-Caches)
│   ├── truth_text.py         # Text-Normalisierung & Parser-Helfer (rein)
│   ├── tests/                # pytest: Unit + API-Integration + Golden-Snapshots
│   ├── data/inputs/*.csv     # kuratierte Eingaben (gebündelt für Container-Refresh)
│   └── data/truth.json       # generierter Datensnapshot (versioniert)
├── Dockerfile · .dockerignore   # Serving-Container (API + Frontend)
├── .github/workflows/           # CI: Tests → Build & Push zu Docker Hub
└── frontend/                 # No-Build-SPA: index.html + styles.css + 7 klassische Skripte
    ├── core.js   # DOM-Helfer, State, API-Client, Toast (Basis)
    ├── list.js   # Filter, Kacheln, Auswahl, Karten-Menü
    ├── detail.js # Steckbrief-Ansicht
    ├── pdf.js    # PDF-Erzeugung (jsPDF)
    ├── export.js # CSV/JSON-Export
    ├── stats.js  # Statistik-Ansicht + Charts
    └── main.js   # Ansichtswechsel, Login, Refresh, Verdrahtung, Init (zuletzt geladen)
```

Die Frontend-Skripte sind **klassische Skripte** (kein Build-Schritt) und werden in
`index.html` per `<script defer>` in dieser Reihenfolge geladen (`core` zuerst,
`main` zuletzt) — sie teilen sich denselben globalen Scope.

**Stack-Begründung:** FastAPI (wie bestehendes `wlo-quellenliste-api`) + No-Build-
Frontend → läuft ohne Angular-Toolchain, ist leicht wartbar und später als
Web-Component einbettbar. Die Datenwahrheit ist als reiner Build-Schritt
(`truth.json`) entkoppelt und unabhängig vom Frontend nutzbar.

## Deployment (Docker & Docker Hub)

Ein **einzelner Container** liefert API **und** Frontend aus dem mitgelieferten
Datensnapshot (`backend/data/truth.json`) aus.

```bash
docker build -t quellensteckbriefe .
docker run -p 8080:8080 -e QE_TEAM_PASSWORD=mein-passwort quellensteckbriefe
# -> http://127.0.0.1:8080
```

- **Datensnapshot:** `backend/data/truth.json` ist bewusst **versioniert** — der
  Container-Build benötigt sie (regenerieren mit `python truth.py` auf einem
  Rechner mit den Eingabe-Repos, dann Image neu bauen). Die kuratierten CSVs
  liegen für den In-Container-Refresh gebündelt unter `backend/data/inputs/`.
- **Live-Refresh im Container:** holt Facetten/Quelldatensätze erneut von der
  öffentlichen WLO-API und baut `truth.json` im **ephemeren** Container-Dateisystem
  neu (Crawler-Profile/Blacklist bleiben dank der gebündelten CSVs erhalten); die
  Aktualisierung gilt **bis zum Neustart**. Für persistente Daten ein Volume mounten:
  `-v $PWD/data:/app/quellenerschliessung-app/backend/data`.
- **Secret:** `QE_TEAM_PASSWORD` wird **nicht** ins Image gebacken — zur Laufzeit
  per `-e` übergeben (Default sonst `wlo-intern`).

**CI → Docker Hub** ([`.github/workflows/docker-publish.yml`](.github/workflows/docker-publish.yml)):
Push auf `main` oder ein Tag `v*` löst aus → erst **Tests**, dann **Build & Push**.
Nötige Repository-Secrets:

| Secret | Inhalt |
|---|---|
| `DOCKERHUB_USERNAME` | Docker-Hub-Benutzername |
| `DOCKERHUB_TOKEN` | Docker-Hub Access-Token (Account → Security) |

Image: `<DOCKERHUB_USERNAME>/quellensteckbriefe` (Tags: `latest`, Branchname,
Kurz-SHA, SemVer bei `v*`-Tags). Image-Name bei Bedarf im Workflow anpassen.

**Nicht im Repo** (`.gitignore`): `.env` (Team-Passwort!), `__pycache__/`,
`.pytest_cache/`. **Versioniert** bleiben `truth.json`, die Input-CSVs und die
Golden-Snapshots (von Build bzw. Tests benötigt).

## Offene Erweiterungen

- Team4-Excel-Detail (KI-Check Rechtliches, Vereinbarungs-Details) zusätzlich zu
  `datencrawler.csv` einlesen.
- Live-Refresh als Hintergrund-Job (wie `wlo-quellenliste-api` `/jobs/refresh`).
- ID-only-Quelldatensätze (nicht such-sichtbar) per Node-API nachladen.
