"""
field_policy.py
===============
Zentrale Richtlinie: welche Informationen sind OEFFENTLICH (Datengeber /
Datennehmer) und welche INTERN (nur per Passwort fuer Teammitglieder).

Grundsatz (laut Auftrag):
  - Oeffentlich: Grund- + Qualitaetsinfos (Lizenz, OER, Fach, Stufe, URL,
    Inhaltszahl) UND wie Metadaten erzeugt wurden (Feld-Provenienz der Crawler).
  - Intern: interne Entwicklervermerke zu Crawlern und deren *genauer*
    Betriebs-Status.

Diese Datei ist die EINE Stelle, an der die Trennung gepflegt wird.
"""

# --- Crawler-Basisspalten aus datencrawler.csv -----------------------------
# Oeffentlich nutzbare Steckbrief-Felder (fuer Datengeber/Datennehmer)
CRAWLER_PUBLIC_BASE = {
    "Titel": "titel",
    "Url": "url",
    "Bezugsquelle": "bezugsquelle",
    "Urheber": "urheber",
    # Rechts-/KI-Nutzungs-Felder der QUELLE selbst (Basis der KI-Nutzungs-Einschaetzung)
    "robots.txt": "robotsTxt",
    "TDM Hinweis ( §44b)": "tdmHinweis",
    "AGB / Nutzungsbedingungen": "agb",
    "Lizenz Check": "lizenzCheck",
    "API Nutzungsbedingungen": "apiNutzung",
}

# Interne Felder – NUR fuer Teammitglieder (Passwort)
CRAWLER_INTERNAL_BASE = {
    "Crawler (Spider)": "spider",
    "Prio": "prio",
    "Crawler-Type": "crawlerType",
    "Zustand": "zustand",                  # genauer Betriebs-Status -> intern
    "Spider Bemerkungen": "spiderBemerkungen",
    "Einschätzung KI & Erschließung": "kiEinschaetzung",
    "Bemerkung/Status": "bemerkungStatus",
    "Prod letzter Crawl": "prodLetzterCrawl",
    "Staging letzter Crawl": "stagingLetzterCrawl",
    "Häufigkeit": "haeufigkeit",
    "Anzahl Prod": "anzahlProd",
    "Anzahl Staging": "anzahlStaging",
    "Quelldatensatz (Prod)": "quelldatensatzProd",
    "Hinweis zu Quellendatensatz": "hinweisQuelldatensatz",
    "Export to OER Berlin": "exportOerBerlin",
    "GitHub": "github",
    # Vertrags-/Vereinbarungsstatus = WLO-interne Geschaeftsinfo -> NUR intern
    "Vereinb. neu": "Vertrag/Vereinbarung",
    "Vereinb. alt": "Vereinbarung (alt)",
}

# --- Live-API-Felder (Quelldatensatz) --------------------------------------
# Oeffentlich
NODE_PUBLIC = {
    "title": "Titel",
    "wwwUrl": "URL",
    "description": "Beschreibung",
    "license": "Lizenz",
    "oer": "OER",
    "subjects": "Faecher",
    "educationalContext": "Bildungsstufen",
    "oehLrt": "Inhaltstypen",
    "language": "Sprache",
    "keywords": "Schlagworte",
    "contentCount": "Inhaltsanzahl",
}
# Intern (genauer Erschliessungs-/Workflow-Status, Roh-Provenienz)
NODE_INTERNAL = {
    "editorialStatus": "Erschliessungsstatus (genau)",
    "wfStatus": "Workflow-Status",
    "replicationSource": "replicationsource (Knoten-Herkunft)",
    "generalIdentifier": "general_identifier (Crawler-Bindung)",
    "nodeId": "Node-ID",
    "modified": "zuletzt geaendert",
}


def coarse_erschliessung(content_count: int, has_node: bool) -> str:
    """Oeffentliche, grobe Erschliessungs-Aussage (ohne internen Status-Code)."""
    if content_count and content_count > 0:
        return "im Bestand verfuegbar"
    if has_node:
        return "Quelle erfasst, (noch) keine Inhalte"
    return "nur als Bezugsquelle bekannt"


# Welche Flags duerfen oeffentlich gezeigt werden?
# Provenienz-Marker (WLO_MIGRATION/LEGACY_BINDUNG/TYP_NICHT_QUELLE) sind oeffentlich,
# damit man an jeder Quelle sieht, WIE sie gebunden/eingespielt ist (Transparenz).
PUBLIC_FLAGS = {"FACETS_ONLY", "OER", "KEINE_URL", "ZWEITDATENSATZ",
                "WLO_MIGRATION", "LEGACY_BINDUNG", "TYP_NICHT_QUELLE"}
INTERNAL_FLAGS = {"FEHLTAGGING", "BLACKLIST", "WHITELIST", "DUBLETTE_VERDACHT",
                  "INHALT_VERDACHT", "PUB_INKONSISTENT"}
