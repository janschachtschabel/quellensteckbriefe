# Quellen in WLO — Wissensbasis & Präsentationsvorlage

> **Zweck:** Grundlage für eine ausführliche Präsentation über *Quellen* in WLO/edu-sharing.
> Sie erklärt die Begriffe, die Datenabbildung, die Bindungen/Verknüpfungen, die Probleme
> der genauen und konsistenten Datenhaltung — und denkt zukünftige Bedarfe (z. B. KI-
> Nutzungserlaubnis) sowie Maßnahmen für eine sauberere Umsetzung mit.
>
> **Zielgruppe:** Redaktion, Metadaten-/Datenmodell-Verantwortliche, Entwicklung, Leitung.
>
> **So nutzt du diese Vorlage:** Jede `##`-Überschrift ≈ ein Folien-Block. Die Stichpunkte
> sind Folien-Inhalt, der Fließtext und die *Sprechernotiz/Diskussion*-Kästen sind Narration.
> Zahlen sind ein **Snapshot** (Stand 2026-06-24, live aktualisierbar) und illustrativ.

**Inhalt**
1. [Worum es geht (Management-Summary)](#0-management-summary)
2. [Was ist eine Quelle — und was unterscheidet sie von Inhalten?](#1-was-ist-eine-quelle)
3. [Wie werden Quellen abgebildet? (Überblick)](#2-wie-werden-quellen-abgebildet)
4. [Quelldatensätze](#3-quelldatensaetze)
5. [Bezugsquelle](#4-bezugsquelle)
6. [Erschließungsweg & Spider/Crawler](#5-erschliessungsweg-spider)
7. [Datenabbildung: Felder-Map](#6-datenabbildung-felder-map)
8. [Wo liegt die Wahrheit der Infos?](#7-wo-liegt-die-wahrheit)
9. [Problemkatalog](#8-problemkatalog)
10. [Zukünftige Bedarfe: KI, Rechte, Nutzungsfreigaben](#9-zukunft-ki-rechte)
11. [Warum man nur bedingt korrigieren kann](#10-warum-korrektur-schwer-ist)
12. [Vorschläge: ein sauberer Ziel-Zustand](#11-vorschlaege)
13. [Anhang: Glossar, Feld-Referenz, Zahlen-Snapshot](#12-anhang)

---

<a id="0-management-summary"></a>
## 0. Worum es geht (Management-Summary)

**Kernaussage:** „Quelle" ist in WLO **kein eindeutig definiertes, fest verankertes Objekt**,
sondern wird auf **mehreren, parallelen und teils widersprüchlichen Wegen** abgebildet
(Quelldatensatz, Bezugsquelle, Spider/Erschließungsweg). Es gibt **keine erzwingenden
Workflows** und **keine festen Bindungen** — Felder werden frei vergeben. Das führt zu
**inkonsistenter Datenhaltung**: Dubletten, fehlende oder falsche Typisierung, lose oder
falsche Verknüpfungen, schwer korrigierbare Datensätze.

**Warum das wichtig ist:**
- *Such- und Filterqualität* (Nutzer finden „alle Inhalte einer Quelle" nur unzuverlässig).
- *Transparenz & Statistik* (wie viele Inhalte hat eine Quelle wirklich?).
- *Rechtssicherheit* (kommende Anforderungen: KI-Nutzungserlaubnis, TDM-Vorbehalt §44b, Lizenz-Check).
- *Pflegbarkeit* (Korrekturen sind heute aufwändig oder blockiert).

> 🎤 *Sprechernotiz:* Die Präsentation will nicht Schuld zuweisen — die Vielfalt ist historisch
> gewachsen (Migrationen, verschiedene Crawler-Generationen, freie Redaktion). Ziel ist ein
> **gemeinsames Verständnis** und ein **Fahrplan** zu festen Bindungen und klaren Definitionen.

---

<a id="1-was-ist-eine-quelle"></a>
## 1. Was ist eine Quelle — und was unterscheidet sie von Inhalten?

**Arbeitsdefinition (vorläufig):**
> Eine **Quelle** ist der *Herkunfts-/Anbieter-Kontext* eines Inhalts — die Stelle, von der ein
> Bildungsmaterial stammt bzw. die es bereitstellt (Portal, Plattform, Datenbank, Verlag,
> Institution, Kanal, Einzelautor:in).
> Ein **Inhalt** ist das einzelne Bildungsmaterial selbst (Video, Arbeitsblatt, Lernpfad,
> Erklärung, Kurs …).

**Quelle vs. Inhalt — die Abgrenzung:**

| | Quelle | Inhalt |
|---|---|---|
| Was | Anbieter/Herkunft | einzelnes Material |
| Beispiel | „Bundeszentrale für politische Bildung" | „Dossier Erinnerungsorte" |
| Granularität | aggregiert (viele Inhalte) | atomar (ein Material) |
| Zweck | Ordnung, Herkunft, Vererbung | Lernnutzung |

> 💬 **Offene Diskussion (bewusst nicht abschließend geklärt):** Was genau ist die „Quelle"
> bei **Plattformen**? Beispiele, bei denen die Community uneinig ist:
> - **YouTube** als Plattform vs. ein **einzelner YouTube-Kanal** vs. der **Herausgeber/Urheber** hinter dem Kanal.
> - **OERSI / Mediatheken** (aggregieren selbst schon viele Anbieter) — ist die Quelle OERSI oder der ursprüngliche Anbieter?
> - **Verlag vs. Produkt** (z. B. „Deutsche Welle" vs. der Kurs „Nicos Weg").
>
> → **Der Begriff „Quelle" ist nicht abschließend definiert.** Das ist die *Wurzel* vieler
> Folgeprobleme: Ohne klare, geteilte Definition lässt sich Konsistenz nicht erzwingen.

**Konsequenz für die Präsentation:** Erst Definition klären (Governance), dann Technik.

---

<a id="2-wie-werden-quellen-abgebildet"></a>
## 2. Wie werden Quellen abgebildet? (Überblick)

Quellen werden heute über **drei nebeneinander existierende Mechanismen** abgebildet, die sich
überschneiden, aber nicht deckungsgleich sind:

```
        ┌──────────────────────────────────────────────────────────┐
        │                        QUELLE                            │
        └──────────────────────────────────────────────────────────┘
               │                     │                     │
   (1) Quelldatensatz        (2) Bezugsquelle      (3) Erschließungsweg
   = Inhalt mit              = Publisher-Schlagwort  = Spider/Crawler-Bindung
     Inhaltstyp „Quelle"       (Freitext am Inhalt)    (general_identifier /
   (eigenes ccm:io-Objekt)                              replicationsource)
```

| Mechanismus | Wo gespeichert | Trägt | Pflicht? |
|---|---|---|---|
| **Quelldatensatz** | eigenes `ccm:io`-Objekt (Inhaltstyp = Quelle) | Metadaten, Bezugsquelle, Spider | nein, frei anlegbar |
| **Bezugsquelle** | Freitext-Feld an Inhalten **und** Quelldatensätzen | Quellenname (als Tag) | nein, gefördert |
| **Erschließungsweg/Spider** | Felder an Quelldatensatz/Inhalt | Crawler-/Import-Herkunft | nein, inkonsequent |

> 🎤 *Sprechernotiz:* Keiner der drei Wege ist allein vollständig. Erst ihre **Kombination**
> ergibt ein Bild — aber genau diese Kombination ist heute lose, manuell und fehleranfällig.

---

<a id="3-quelldatensaetze"></a>
## 3. Quelldatensätze

**Definition:** Ein **Quelldatensatz** ist ein normaler Inhalt (`ccm:io`), dessen **Inhaltstyp
(LRT) = „Quelle"** ist. Er repräsentiert die Quelle als eigenes Objekt im System.

**Eigenschaften / was er aufnehmen kann:**
- vollständige **Metadaten** (Titel, Beschreibung, URL, Lizenz, Fächer, Bildungsstufen, Urheber …)
- **Bezugsquelle** (Publisher-Tag, s. Abschnitt 4)
- **Spider-/Erschließungs-Bindung** (s. Abschnitt 5)
- Vorschaubild, Qualitätsmerkmale

**Wozu Quelldatensätze genutzt werden:**
- **Metadatenvererbung beim Crawlen** — der Crawler kann Felder des Quelldatensatzes an die
  erzeugten Inhalte nachnutzen/vererben.
- **Ordnungsinstrument** — Strukturierung der Inhaltsmengen (oft zusätzlich in Ordnern).
- **Visualisierung für Nutzer:innen** — die Quelle wird als eigenes, auffindbares Objekt sichtbar.

**Wichtige Einschränkungen (Ist-Stand):**
- Ein Quelldatensatz **kann als Inhalt betrachtet werden** — aber: **man kann nicht „nach
  Inhalten" filtern**, um Quellen sauber von echten Lernmaterialien zu trennen (es fehlt ein
  verlässliches Unterscheidungsmerkmal jenseits des frei setzbaren LRT).
- **Frei anlegbar** — es gibt **keine Workflows in der Redaktion, die das Anlegen erzwingen
  oder fördern.** Folge: Quelldatensätze entstehen uneinheitlich, unvollständig, teils gar nicht.

> ⚠️ **Regel, die heute nicht erzwungen wird:** Wenn der Inhaltstyp „Quelle" gesetzt ist,
> *dürfen keine weiteren Inhaltstypen* gesetzt sein (sonst ist der Datensatz Quelle *und*
> Inhalt zugleich → nicht differenzierbar). Heute existieren genau solche Misch-Datensätze.

---

<a id="4-bezugsquelle"></a>
## 4. Bezugsquelle

**Definition:** Die **Bezugsquelle** ist die **zweite Möglichkeit**, eine Quelle abzubilden:
ein **frei vergebbares Schlagwort** mit dem **Namen der Quelle**, das an Inhalten (und
Quelldatensätzen) hängt.
*(edu-sharing-Feld: `ccm:oeh_publisher_combined`.)*

**Eigenschaften:**
- **Frei vergebbar** (Freitext) — kein kontrolliertes Vokabular.
- **Im Suchschlitz verwendbar** — Nutzer:innen können nach der Bezugsquelle suchen.
- **Verbindung Quelle ↔ Inhalte:** Durch das **Tagging der Inhalte** mit der Bezugsquelle werden
  **Aussagen zur Inhaltsanzahl** möglich („Quelle X hat N Inhalte") und eine Brücke zwischen
  Quelle und ihren Inhalten geschlagen.
- So **hängt die Bezugsquelle an zwei Stellen**:
  1. an den **Inhalten** (→ zählbare Inhaltsmenge je Quelle),
  2. an den **Quelldatensätzen** (→ verbindet den Quelldatensatz mit „seinem" Publisher-Namen).
- **Kurationsmasken**: Am Ende der Inhalts-Kurationsmasken gibt es Felder, die den Eintrag der
  Bezugsquelle **fördern, aber nicht erzwingen.**

**Logik (heute, vereinfacht):**
- Inhalte einer Bezugsquelle werden über den **gleichlautenden Freitext** zusammengeführt
  (Normalisierung über Klein-/Groß-/Leerzeichen, aber keine ID).
- Die **Inhaltsanzahl je Bezugsquelle** stammt aus der Such-Facette über das Publisher-Feld.

> ⚠️ **Schwäche durch Freitext:** „Wikipedia", „Wikipedia – Die freie Enzyklopädie",
> „Wikipedia (deutschsprachige Ausgabe)" sind drei *verschiedene* Bezugsquellen, obwohl
> dieselbe Quelle gemeint ist. Ohne ID entstehen **Dubletten und Streuung**.

---

<a id="5-erschliessungsweg-spider"></a>
## 5. Erschließungsweg & Spider/Crawler

Zusätzlich zur inhaltlichen Quelle spielt der **Erschließungsweg** eine Rolle: **wie** kam ein
Inhalt ins System?

**Automatisierte Erschließung / Datenimporte (Crawler)** werden als **Spider-Tags** mit
Quelldatensätzen (und Inhalten) verbunden. Genutzte Felder:

| Feld | An welchem Objekt | Bedeutung |
|---|---|---|
| `ccm:general_identifier` | **Quelldatensatz** | Crawler-/Spider-Bindung der Quelle |
| `ccm:replicationsource` | **Inhalt** | Herkunft/Erschließungsweg des einzelnen Inhalts |

**Weitere Beobachtungen (Ist-Stand):**
- Inhaltsmengen werden in der Regel zusätzlich in **Ordnern** extra strukturiert.
- **Spider/Crawler können die Metadaten des Inhaltsdatensatzes nachnutzen** (Vererbung, s. Abschnitt 3).
- **`wirlernenonline_spider`** ist *kein* echter Crawler, sondern ein **Migrationsmarker** —
  er steht an Objekten, die über die WLO-Datenmigration eingespielt wurden.
- **Legacy-Quellen**: Es existieren noch **Listen mit alten Quellen** (Vokabular-/Skohub-URIs,
  Form `…/vocabs/sources/<uuid>`). **Bedeutung und Herkunft sind teils unklar** — und es ist
  offen, *welche davon noch aktiv im System gebraucht werden.*
- **Datenmigrationen** wurden teils **als Quellen hinterlegt** (s. Problemkatalog).
- **Echte Spider/Crawler sind nur ein Bruchteil**: Von allen „quellenartigen" Einträgen ist nur
  eine Minderheit über einen echten, aktiven Crawler gebunden.

> ❗ **Inkonsequente Feldnutzung:** `general_identifier` und `replicationsource` werden **nicht
> immer konsequent und richtig** gesetzt — teils falsche Feldnutzung, teils fehlend, teils
> Migrationsmarker statt echter Bindung.

> ❗ **Fehlende maschinenlesbare Feld-Provenienz:** Es gibt **keine maschinenlesbare Information**
> darüber, **wie** ein Feld bei der Inhaltsgenerierung erzeugt wurde (hartcodiert / vom Crawler
> gescraped / von WLO generiert / manuell). Das erschwert Vertrauen, Audit und Korrektur enorm.

---

<a id="6-datenabbildung-felder-map"></a>
## 6. Datenabbildung: Felder-Map

**Konzept → Feld → Objekt → Logik** (vereinfachte Abbildung; exakte `ccm:`-Schlüssel gegen das
MDS-Schema gegenprüfen):

| Konzept | Feld (edu-sharing) | Am Objekt | Logik / Hinweis |
|---|---|---|---|
| Inhalt | `ccm:io` (Objekttyp) | — | jedes Material |
| Inhaltstyp / LRT | Learning-Resource-Type (`ccm:oeh_lrt_aggregated`) | Inhalt | Wert **„Quelle"** ⇒ Quelldatensatz |
| Quelldatensatz | (LRT = „Quelle") | Inhalt | eigenes Objekt, repräsentiert die Quelle |
| Bezugsquelle | `ccm:oeh_publisher_combined` | Inhalt **+** Quelldatensatz | Freitext-Tag, Such-Facette → Inhaltsanzahl |
| Spider-Bindung | `ccm:general_identifier` | Quelldatensatz | Crawler-/Quell-Bindung |
| Erschließungs-Herkunft | `ccm:replicationsource` | Inhalt | Crawler-Name **oder** Migrationsmarker **oder** Legacy-Vocab-URI |
| Migrationsmarker | `replicationsource = wirlernenonline_spider` | Inhalt/Quelldatensatz | **keine** echte Crawler-Bindung |
| Legacy-Quelle | `replicationsource = …/vocabs/sources/<uuid>` | Inhalt | alter Vokabular-Eintrag, Bedeutung teils unklar |

**Abgeleitete Regel „echte Bindung":**
> Eine Quelle ist **echt crawler-/spider-gebunden**, wenn
> `general_identifier` gesetzt ist **ODER** `replicationsource ≠ wirlernenonline_spider`.
> (Nur `replicationsource = wirlernenonline_spider` = reine Migration, **keine** echte Bindung.)

**Drei Sichten, die zusammengeführt werden müssen:**
1. **GitHub-Crawler-Code** (welche Spider existieren technisch)
2. **Live-Felder** (`replicationsource`/`general_identifier` an den Objekten)
3. **Vokabular/Skohub** (menschliche Namen der Legacy-Quellen)

> 🎤 *Sprechernotiz:* Die „Datenwahrheit" entsteht erst durch den **Join** dieser drei Sichten —
> und genau dieser Join ist heute weder im System verankert noch erzwungen.

---

<a id="7-wo-liegt-die-wahrheit"></a>
## 7. Wo liegt die Wahrheit der Infos?

**Mengenbild (Snapshot, illustrativ):**
- **Quelldatensätze** (Inhaltstyp = Quelle, such-sichtbar): ~**1.300**
- **distinkte Bezugsquellen** (Publisher-Tags): ~**3.500**
- **Überschneidung** Quelldatensatz ↔ Bezugsquelle: nur ein **Bruchteil** (~700 saubere
  Erst-Zuordnungen; der Rest sind Zweit-Datensätze, Blacklist-Dubletten oder reine Tags)
- **Echte Crawler/Spider:** nur ~**50** aktive — die große Mehrheit der „Quellen" ist *nicht*
  über einen laufenden Crawler gebunden.

→ **Es gibt keinen einzelnen „Ort der Wahrheit".** Quelldatensatz, Bezugsquelle und Spider
zeichnen jeweils ein *unvollständiges, teils widersprüchliches* Bild.

**Kern-Inkonsistenzen:**
- **Quelldatensätze sind nicht immer als solche erkennbar** (Inhaltstyp „Quelle" fehlt) — *oder*
  **Inhalte werden fälschlich als Quelldatensätze markiert.** Es gibt **keine Hilfen/Tools zur
  Differenzierung**, die das automatisch stützen.
- **Bei Spidern** eine breite Palette an Problemen:
  - fehlende Verknüpfung von Quelldatensatz und Spider,
  - Datenmigrationen, die als Quellen hinterlegt sind,
  - die Feldlogik (wo der Spider „dranhängt") wird nicht konsequent umgesetzt.
- **Schwer abgrenzbare Quellen:** Bei **Sammelerschließungen** (z. B. viele **YouTube-Kanäle**
  oder **RSS-Feeds**) ist schwer zu sagen, was die „eine" Quelle ist.
  → Ein **Plattform-Feld** könnte helfen, unklare Zuweisungen zwischen z. B. *YouTube*
  (Plattform) und einem *YouTube-Kanal* (Anbieter) sauber zu trennen.
- **Bezugsquellen mit nur einem oder kaum Inhalten** — meist **keine echte Quelle**, sondern
  ein Tagging-Artefakt oder Einzelmaterial.
- **Dubletten** auf mehreren Ebenen: gleiche **Titel**, gleiche **URL**, gleiche/ähnliche
  **Beschreibungstexte**.
- **Ein Einzelinhalt repräsentiert eine ganze Bezugsquelle** (System-Effekt): Hatte eine
  Bezugsquelle keinen sauberen Quell-Datensatz, „erbte" ein zufällig zuerst verarbeiteter
  *Einzelinhalt* die gesamte Inhaltszahl der Bezugsquelle (z. B. eine Grammatik-Erklärung als
  „Wikipedia", ein einzelner Kurs als „Deutsche Welle"). → zeigt, wie lose die Bindung ist.

---

<a id="8-problemkatalog"></a>
## 8. Problemkatalog (kompakt)

| # | Problem | Wirkung | Ebene |
|---|---|---|---|
| P1 | „Quelle" nicht abschließend definiert | keine erzwingbare Konsistenz | Governance |
| P2 | Drei parallele Abbildungswege, nicht deckungsgleich | widersprüchliche Sichten | Modell |
| P3 | Freitext-Bezugsquelle (keine ID) | Dubletten, Streuung | Modell |
| P4 | Keine erzwingenden Workflows beim Anlegen/Taggen | unvollständige/fehlende Daten | Prozess |
| P5 | Quelle vs. Inhalt nicht differenzierbar (LRT frei, Mischtypen) | falsche Typisierung | Modell/Prozess |
| P6 | Spider-Felder inkonsequent/falsch genutzt | lose/falsche Bindung | Daten |
| P7 | Migration (`wirlernenonline_spider`) als „Quelle" | Scheinquellen | Daten |
| P8 | Legacy-Vokabular-Quellen unklarer Bedeutung | Altlasten im System | Daten |
| P9 | Keine maschinenlesbare Feld-Provenienz | kein Audit/Vertrauen | Modell |
| P10 | Sammelerschließung (YouTube/RSS) schwer abgrenzbar | unklare Quelle | Modell |
| P11 | Bezugsquellen mit ~0 Inhalten | Tagging-Artefakte | Daten |
| P12 | Dubletten (Titel/URL/Beschreibung) | Mehrfachzählung, Unschärfe | Daten |
| P13 | Unvollständige/fehlerhafte Metadaten am Quelldatensatz | schlechte Qualität/Vererbung | Daten |
| P14 | Korrektur blockiert durch Spider-Bindung | Fehler bleiben stehen | Prozess/Technik |

---

<a id="9-zukunft-ki-rechte"></a>
## 9. Zukünftige Bedarfe: KI, Rechte, Nutzungsfreigaben

Die Quelle ist der **natürliche Ankerpunkt für rechtliche und nutzungsbezogene Metadaten** —
viele Rechte gelten pro Anbieter, nicht pro Einzelinhalt. Kommende Bedarfe:

- **KI-Nutzungserlaubnis / Nutzungsfreigaben:** Darf der Inhalt einer Quelle für KI-Training,
  RAG/Retrieval, Generierung genutzt werden? (explizite, maschinenlesbare Freigabe pro Quelle)
- **TDM-Vorbehalt (§ 44b UrhG):** maschinenlesbarer Opt-out/Opt-in zur Text-und-Data-Mining-Nutzung.
- **`robots.txt` / AGB / Nutzungsbedingungen / Lizenz-Check / API-Nutzungsbedingungen:** heute
  teils im Crawler-Steckbrief erfasst, aber **nicht strukturiert an der Quelle** verankert und
  **nicht vererbt**.
- **Provenienz der Rechteangabe:** woher stammt die Freigabe (Anbieter-Erklärung, redaktionelle
  Prüfung, Lizenz-Datei)?

> 🎤 *Diskussion:* Diese Felder müssen **an der Quelle** liegen, **maschinenlesbar** sein und an
> die Inhalte **vererbt** werden — sonst muss jede KI-Pipeline pro Einzelinhalt prüfen, was nicht
> skaliert. Voraussetzung dafür ist eine **stabile, eindeutige Quelle** (s. Vorschläge).

**Querschnitt:** Auch hier blockieren die heutigen Probleme (unvollständige/fehlerhafte
Metadaten am Quelldatensatz, lose Bindung) die saubere Ablage von Rechte-/KI-Infos.

---

<a id="10-warum-korrektur-schwer-ist"></a>
## 10. Warum man nur bedingt korrigieren kann

- **Spider-Bindung blockiert die Bearbeitung:** Quelldatensätze, die an Spider/Crawler gebunden
  sind, sind **schreibgeschützt/blockiert** — Korrekturen an Metadaten, Typ oder Bezugsquelle
  sind dann nicht ohne Weiteres möglich. *Fehler bleiben stehen.*
- **Doppelte/abhängige Datensätze:** Eine Korrektur an einer Stelle (Inhalt) schlägt nicht
  automatisch auf den Quelldatensatz oder die Bezugsquelle durch und umgekehrt.
- **Keine Differenzierungs-Tools:** Ohne automatische Unterstützung muss jede Korrektur manuell
  geprüft werden (Quelle vs. Inhalt, Dublette vs. echte Quelle).
- **Legacy/Migration:** Bei migrierten oder Legacy-Vokabular-Quellen ist oft unklar, *ob* und
  *wie* korrigiert werden darf, ohne andere Verknüpfungen zu brechen.

> ⚠️ **Kernspannung:** Die Spider-Bindung schützt automatisierte Daten vor versehentlichem
> Überschreiben — verhindert aber zugleich notwendige redaktionelle Korrekturen. Das ist ein
> **Rechte-/Workflow-Designproblem**, kein reines Datenproblem.

---

<a id="11-vorschlaege"></a>
## 11. Vorschläge: ein sauberer Ziel-Zustand

Basierend auf dem Ist-Stand — gegliedert in **Quick Wins**, **strukturelle Maßnahmen** und
**Governance**. Jede Maßnahme adressiert konkrete Probleme (P#).

### A. Governance / Definition (Voraussetzung für alles)
1. **„Quelle" verbindlich definieren** — inklusive der Plattform-Frage (YouTube vs. Kanal vs.
   Herausgeber, Aggregatoren wie OERSI). Entscheidungsbaum + Beispiele. *(P1, P10)*
2. **Differenzierungsregel festschreiben:** LRT „Quelle" ist **exklusiv** (keine weiteren
   Inhaltstypen). *(P5)*

### B. Feste Bindungen statt Freitext (strukturell)
3. **Quellen-Register mit stabilen IDs** einführen (kontrolliertes Vokabular): jede Quelle = ein
   Eintrag mit ID, Name, URL, Plattform-Typ. Bezugsquelle und Spider binden an **diese ID**
   statt an Freitext. *(P3, P11, P12)* — beseitigt Dubletten und Streuung an der Wurzel.
4. **Feste Bindung Quelldatensatz ↔ Inhalte ↔ Spider** über die Register-ID (Referenz statt
   gleichlautender String). *(P2, P6)*
5. **Plattform-Feld** ergänzen (Plattform vs. Anbieter/Kanal), um Sammelerschließungen sauber
   abzubilden. *(P10)*

### C. Maschinenlesbare Provenienz & Rechte
6. **Feld-Provenienz maschinenlesbar** ablegen: je Feld „wie erzeugt" (hardcoded / crawler /
   WLO-generiert / manuell / vererbt). *(P9)* — Basis für Audit und Vertrauen.
7. **Rechte-/KI-Schema an der Quelle** (vererbbar): KI-Nutzungserlaubnis, TDM-Vorbehalt §44b,
   robots.txt, AGB, Lizenz-Check, API-Bedingungen — strukturiert, mit Provenienz. *(Zukunft, §9)*

### D. Workflow & Rechte
8. **Erzwingende/fördernde Workflows** in der Redaktion: beim Anlegen eines Quelldatensatzes
   Pflicht-/Vorschlagsfelder (Bezugsquelle, Plattform, Rechte); beim Inhalt die Bezugsquelle
   stärker einfordern. *(P4, P13)*
9. **Spider-Bindung entkoppeln vom Schreibschutz:** redaktionelle Korrektur an Metadaten/Typ/
   Bezugsquelle **erlauben**, ohne die automatisierte Herkunft zu verlieren (z. B. „redaktionell
   überschrieben"-Marker + Provenienz). *(P14)* — adressiert die Korrektur-Blockade direkt.

### E. Werkzeuge / laufende Pflege
10. **Differenzierungs-/Validierungs-Tools:** Heuristiken/Checks für „Inhalt fälschlich als
    Quelle" und „Quelle ohne Inhaltstyp", Misch-Typen, Bezugsquellen mit ~0 Inhalten. *(P5, P11)*
    → *Teils umgesetzt:* Der **Team-Datenprüfungs-Filter** der App blendet aussortierte und
    Zweit-Datensätze standardmäßig aus (saubere Kundensicht) und markiert zur Sichtung:
    Zweit-Datensätze (473), Misch-Typen/Fehltagging (274), Dubletten-Verdacht via URL/Titel
    (112), Bezugsquelle mit Einzelinhalt (2.104), Quelldatensatz ohne Bezugsquelle (169),
    dünne Metadaten (87), unvollständige Bindung (12). Eine Team-Statistik-Grafik
    „Datenprobleme" ist deckungsgleich (1:1) mit diesen Filteroptionen.
11. **Dubletten-Erkennung + Merge-Workflow** (Titel/URL/Beschreibung-Ähnlichkeit, optional
    Embedding-gestützt als *Vorsortierung* mit menschlicher Endentscheidung). *(P12)*
12. **Legacy-/Migrations-Bereinigung:** Inventur der `…/vocabs/sources/<uuid>`-Quellen und der
    `wirlernenonline_spider`-Altlasten — was bleibt, was wird gemappt, was wird stillgelegt. *(P7, P8)*

### Priorisierung (Vorschlag)
| Horizont | Maßnahmen | Effekt |
|---|---|---|
| **Sofort** | 1, 2, 10, 11 | Klarheit + Sichtbarmachen der Fehler |
| **Mittel** | 3, 4, 5, 6, 9 | feste Bindungen, korrigierbar, auditierbar |
| **Strategisch** | 7, 8, 12 | Rechte/KI-fähig, nachhaltige Pflege |

> 🎤 *Schluss-Sprechernotiz:* Die größte Hebelwirkung haben **feste Bindungen über ein
> Quellen-Register mit IDs** (B) und das **Entkoppeln der Korrektur-Blockade** (D9). Beides macht
> das System *konsistent korrigierbar* — die Voraussetzung dafür, Rechte- und KI-Infos (§9)
> überhaupt verlässlich ablegen zu können.

---

<a id="12-anhang"></a>
## 12. Anhang

### Glossar
- **Inhalt** — einzelnes Bildungsmaterial (`ccm:io`).
- **Quelle** — Herkunft/Anbieter eines Inhalts (Begriff noch nicht abschließend definiert).
- **Quelldatensatz** — Inhalt mit Inhaltstyp „Quelle"; repräsentiert die Quelle als Objekt.
- **Bezugsquelle** — Freitext-Publisher-Tag (`ccm:oeh_publisher_combined`) an Inhalt/Quelldatensatz.
- **Spider/Crawler** — automatisierte Erschließung; bindet über `general_identifier` /
  `replicationsource`.
- **Migrationsmarker** — `replicationsource = wirlernenonline_spider`; keine echte Crawler-Bindung.
- **Legacy-Quelle** — alter Vokabular-Eintrag `…/vocabs/sources/<uuid>`.
- **Echte Bindung** — `general_identifier` gesetzt ODER `replicationsource ≠ wirlernenonline_spider`.
- **Zweit-Datensatz** — weiterer Datensatz derselben Bezugsquelle (vermeidet Doppelzählung).
- **Dublette** — mehrfacher Eintrag derselben Quelle (Titel/URL/Beschreibung).

### Feld-Referenz (gegen MDS gegenprüfen)
| Feld | Objekt | Zweck |
|---|---|---|
| `ccm:oeh_lrt_aggregated` (LRT) | Inhalt | Inhaltstyp; Wert „Quelle" = Quelldatensatz |
| `ccm:oeh_publisher_combined` | Inhalt + Quelldatensatz | Bezugsquelle (Freitext) |
| `ccm:general_identifier` | Quelldatensatz | Spider-/Crawler-Bindung |
| `ccm:replicationsource` | Inhalt | Erschließungs-Herkunft (Crawler/Migration/Legacy) |

### Zahlen-Snapshot (Stand 2026-06-24, illustrativ, live aktualisierbar)
**Roh — alle Records (inkl. aussortierte & Zweit-Datensätze):**
- Quellen-Records gesamt: ~4.219 · echte Crawler (ohne WLO-Migrations-Spider): ~53
- distinkte Bezugsquellen (Such-Facette): ~3.579 · echte Spider-/Crawler-Bindung (gi ODER rs≠wlo): ~90–130
- WLO-Migration: ~197 · Legacy-Vocab-Bindung: ~33 · mis-getaggt (Bindung, aber LRT≠Quelle): ~2
- Inhalte einer Quelle zuordenbar: ~304.800 · WLO-Prod gesamt: ~318.650

**Sichtbar in der „Art der Quelle"-Filterung** (aussortierte/Blacklist immer aus; Zweit-Datensätze
sind eigenständige *Objekte* mit geteiltem Bezugsquelle-Tag, nur in der Tag-Sicht zusammengefasst):
- alle Quellen: **3.721** (Default, Tag-Sicht) · davon Crawler ~69
- **mit Quelldatensatz (Objekt-Sicht): 1.242** — zählt die QD-Nodes inkl. Sekundär-Datensätze (≈ API ~1.300, vorher fälschlich 824)
- **mit Bezugsquelle (Tag-Sicht): 3.558** — distinkte Bezugsquellen, ≤ 3.579 Facette (vorher fälschlich 3.976)
- Überschneidung (QD ∩ BQ, Objekt-Sicht): **1.087**
- Schlüssel: dieselbe Bezugsquelle kann mehrere eigenständige Quelldatensätze haben (z. B. „YouTube" = 47 Kanäle) → als Objekte zählen sie einzeln (1.242), als Tag distinkt (3.558). Jede Liste zeigt klein „N ausgeblendet".

**Team-Datenprüfung — Marker** (nur im Team-Filter sichtbar; blenden die Ausblendung gezielt aus):
- Zweit-Datensätze: ~473 · Bezugsquelle mit 1 Inhalt: ~2.104 · dünne Metadaten: ~87 ·
  unvollständige Bindung: ~12 · aussortiert (Blacklist): ~80

> Diese Zahlen stammen aus der Datenwahrheit-Engine der Quellensteckbriefe-App
> (Join aus Live-API-Facetten, Crawler-Steckbriefen, Korrekturlisten und Vokabular).
> Methodik & Details: siehe `SPIDER-GESAMTBILD.md` und `DATENINTEGRATION.md`.

---

*Diese Datei ist eine **Vorlage/Wissensbasis**: Abschnitte = Folien-Blöcke, Stichpunkte =
Folien-Inhalt, „Sprechernotiz/Diskussion"-Kästen = Narration. Zahlen vor einer Live-Präsentation
aktualisieren.*
