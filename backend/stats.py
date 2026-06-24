"""stats.py — Statistik-Aggregation (rein).

Aggregiert die Records zu den Kennzahlen, Verteilungen, Herkunfts- und
Provenienz-Auswertungen der App. Reine Funktionen ueber (records, meta) — keine
Web-/IO-Abhaengigkeit, damit die Zahlen einzeln testbar sind.

  compute_stats           kompakte Kennzahlen (/api/stats)
  compute_filter_options  Filter-Vokabular (/api/meta/filters)
  compute_stats_full      oeffentliche Vollstatistik (/api/stats/full)
  compute_stats_team      interne Statistik + Datenprobleme (/api/stats/team)
"""
from collections import Counter


def _bracket(n):
    if n <= 0: return "0"
    if n < 5: return "1–4"
    if n < 10: return "5–9"
    if n < 50: return "10–49"
    if n < 100: return "50–99"
    if n < 500: return "100–499"
    if n < 1000: return "500–999"
    if n < 10000: return "1k–9.9k"
    return "≥10k"


_HOW_BUCKETS = [
    ("hard-coded", "hard-coded"), ("mapping", "via Mapping"), ("url", "aus URL"),
    ("dom", "aus DOM gescraped"), ("lrmi", "via LRMI"), ("rss", "aus RSS"),
    ("api", "aus API"), ("csv", "aus CSV"), ("trafilatura", "Volltext-Extraktion"),
]


def _how_bucket(how):
    h = (how or "").lower()
    for key, label in _HOW_BUCKETS:
        if key in h:
            return label
    return "aus Quelldaten" if h == "" else "sonstige"


def _ctype_bucket(t):
    """Crawler-Typ (Crawler-Type aus datencrawler.csv) in wenige Klassen normalisieren."""
    h = (t or "").lower()
    if "sitemap" in h:
        return "Webseite (Sitemap)"
    if "rss" in h:
        return "RSS"
    if "api" in h:
        return "API"
    if any(k in h for k in ("csv", "zip", "dump", "import", "sheet")):
        return "Dump/Import"
    if "webseite" in h or "scrap" in h or "website" in h:
        return "Webseite (Scraping)"
    return "Sonstige"


# Felder für die Füllstand-Auswertung (Team): Metadaten am Quelldatensatz +
# KI-/Rechtshinweise aus dem Crawler-Steckbrief. (label, public-Schlüssel)
_FUELL_META = [
    ("Beschreibung", "Beschreibung"), ("Lizenz", "Lizenz"), ("OER", "OER"),
    ("Fächer", "Faecher"), ("Bildungsstufen", "Bildungsstufen"), ("Inhaltstypen", "Inhaltstypen"),
    ("Sprache", "Sprache"), ("Schlagworte", "Schlagworte"), ("Urheber", "Urheber"),
    ("Zielgruppe", "Zielgruppe"), ("Alter", "Alter"), ("Sprachniveau", "Sprachniveau"),
    ("Lehrplanbezug", "Lehrplanbezug"), ("FSK", "FSK"),
]
_FUELL_KI = [
    ("robots.txt", "robots.txt"), ("TDM-Hinweis (§44b)", "TDM-Hinweis (§44b)"),
    ("AGB/Nutzungsbedingungen", "AGB/Nutzungsbedingungen"), ("Lizenz-Check", "Lizenz-Check"),
    ("API-Nutzungsbedingungen", "API-Nutzungsbedingungen"),
]


def compute_stats(recs, meta):
    crawler = [r for r in recs if r["kind"] == "crawler"]
    subj = Counter()
    for r in recs:
        for s in r["public"].get("Faecher", []):
            subj[s] += 1
    return {
        "meta": meta,
        "crawlerWithFieldProfile": sum(1 for r in crawler if r.get("fieldGeneration")),
        "oerCount": sum(1 for r in recs if "OER" in r.get("flags", [])),
        "facetsOnly": sum(1 for r in recs if r["kind"] == "bezugsquelle"),
        "topSubjects": [{"value": k, "count": v} for k, v in subj.most_common(15)],
    }


def compute_filter_options(recs):
    subj, lvl, lic, lang, lrt = Counter(), Counter(), Counter(), Counter(), Counter()
    for r in recs:
        p = r["public"]
        for s in p.get("Faecher", []): subj[s] += 1
        for s in p.get("Bildungsstufen", []): lvl[s] += 1
        for s in p.get("Inhaltstypen", []): lrt[s] += 1
        if p.get("Lizenz"): lic[p["Lizenz"]] += 1
        if p.get("Sprache"): lang[p["Sprache"]] += 1
    return {
        "kinds": ["crawler", "manuell", "bezugsquelle"],
        "subjects": [k for k, _ in subj.most_common(60)],
        "levels": [k for k, _ in lvl.most_common(20)],
        "licenses": [k for k, _ in lic.most_common(20)],
        "languages": [k for k, _ in lang.most_common(20)],
        "lrts": [k for k, _ in lrt.most_common(25)],
    }


def compute_stats_full(recs, meta):
    total = meta["total"]
    BORDER = ["0", "1–4", "5–9", "10–49", "50–99", "100–499", "500–999", "1k–9.9k", "≥10k"]
    cb = Counter(); bqcb = Counter(); subj = Counter(); lvl = Counter(); lic = Counter()
    lang = Counter(); lrt = Counter(); how = Counter(); conf = Counter(); flags = Counter()
    ctype = Counter(); field_active = Counter()
    distinct_bq = set(); bq_with_node = set(); schnitt = 0
    node_cb = Counter(); schnitt_sauber = schnitt_zweit = schnitt_black = schnitt_white = 0
    total_active_fields = crawler_fp = 0
    prev = qual = desc = urlc = oer = 0
    singletons = bq_u5 = quelle_ohne_bq = 0
    for r in recs:
        n = r.get("contentCount") or 0
        cb[_bracket(n)] += 1
        conf[r.get("confidence", "?")] += 1
        fl = r.get("flags", [])
        for f in fl: flags[f] += 1
        if "OER" in fl: oer += 1
        pub = r["public"]; idn = r["identity"]
        for s in pub.get("Faecher", []): subj[s] += 1
        for s in pub.get("Bildungsstufen", []): lvl[s] += 1
        for s in pub.get("Inhaltstypen", []): lrt[s] += 1
        if pub.get("Lizenz"): lic[pub["Lizenz"]] += 1
        if pub.get("Sprache"): lang[pub["Sprache"]] += 1
        if r.get("previewUrl"): prev += 1
        if r.get("quality"): qual += 1
        if pub.get("Beschreibung"): desc += 1
        if pub.get("URL"): urlc += 1
        if r["kind"] == "bezugsquelle":
            bqcb[_bracket(n)] += 1
            if n <= 1: singletons += 1
            if n < 5: bq_u5 += 1
        if idn.get("nodeId") and not idn.get("bezugsquelle"):
            quelle_ohne_bq += 1
        if idn.get("nodeId"):
            node_cb[_bracket(n)] += 1          # Inhaltsmengen-Verteilung je Quelldatensatz
        # Herkunft: Schnittmenge Quelldatensatz <-> Bezugsquelle (distinct zählen)
        bqv = (idn.get("bezugsquelle") or "").strip().lower()
        if bqv:
            distinct_bq.add(bqv)
            if idn.get("nodeId"):
                bq_with_node.add(bqv); schnitt += 1
                # Transparente, exklusive Aufschlüsselung (summiert exakt zu schnitt):
                if "BLACKLIST" in fl:
                    schnitt_black += 1          # mögliche Dublette (Korrekturliste)
                elif "ZWEITDATENSATZ" in fl:
                    schnitt_zweit += 1          # weiterer Datensatz derselben Bezugsquelle
                else:
                    schnitt_sauber += 1         # saubere Erst-Zuordnung
                if "WHITELIST" in fl:
                    schnitt_white += 1
        if r["kind"] == "crawler":
            ct = (r.get("internal") or {}).get("crawlerType", "")
            if ct:
                ctype[_ctype_bucket(ct)] += 1
        if r.get("fieldGeneration"):
            crawler_fp += 1
            total_active_fields += r.get("fieldActiveCount", 0)
            seen_fields = set()
            for fg in r["fieldGeneration"]:
                how[_how_bucket(fg.get("how"))] += 1
                if fg.get("aktiv"):
                    seen_fields.add(fg.get("field", ""))
            # je Feld nur EINMAL pro Crawler zählen → Füllstand (max = Anzahl Crawler)
            for f in seen_fields:
                field_active[f] += 1
    top_crawler = sorted([r for r in recs if r["kind"] == "crawler"],
                         key=lambda r: -(r.get("contentCount") or 0))[:20]
    top_content = sorted(recs, key=lambda r: -(r.get("contentCount") or 0))[:20]
    def lst(c, n=15): return [{"value": k, "count": v} for k, v in c.most_common(n)]
    def pct(x): return round(100 * x / max(1, total), 1)
    bq_total = meta["byKind"]["bezugsquelle"]

    # Inhaltsabdeckung nach Quellentyp (je Gruppe dedupliziert, Gruppen überlappen sich)
    content_by_bq = {}; crawler_content = 0; quelle_bqs = set()
    for r in recs:
        cc = r.get("contentCount") or 0
        idn = r["identity"]; bq = (idn.get("bezugsquelle") or "").strip().lower()
        if r["kind"] == "crawler":
            crawler_content += cc
        if bq:
            if cc > content_by_bq.get(bq, 0):
                content_by_bq[bq] = cc          # je Bezugsquelle nur 1× (Zweit-Datensatz=0)
            if idn.get("nodeId"):
                quelle_bqs.add(bq)
    bq_content = sum(content_by_bq.values())
    quelle_content = sum(c for b, c in content_by_bq.items() if b in quelle_bqs)

    # Quellenverwaltung: SICHTBARE Records (ohne Blacklist) als RECORD-Zahlen —
    # konsistent zum Filter „Art der Quelle" (der Blacklist ebenfalls ausblendet).
    qv_gesamt = qv_node = qv_bq = qv_both = 0
    for r in recs:
        if "BLACKLIST" in r.get("flags", []):
            continue
        qv_gesamt += 1
        idn = r["identity"]
        hn = bool(idn.get("nodeId")); hb = bool(idn.get("bezugsquelle"))
        if hn: qv_node += 1
        if hb: qv_bq += 1
        if hn and hb: qv_both += 1
    return {
        "meta": meta,
        "byKind": meta["byKind"],
        # konsistent zum Filter „Art der Quelle" (sichtbare Records, ohne Blacklist)
        "quellenverwaltung": {
            "gesamt": qv_gesamt, "mitQuelldatensatz": qv_node,
            "mitBezugsquelle": qv_bq, "ueberschneidung": qv_both,
        },
        "confidence": dict(conf),
        "contentBrackets": [{"value": b, "count": cb[b]} for b in BORDER if cb.get(b)],
        "contentBracketsNode": [{"value": b, "count": node_cb[b]} for b in BORDER if node_cb.get(b)],
        "bqSizeBrackets": [{"value": b, "count": bqcb[b]} for b in BORDER if bqcb.get(b)],
        "oer": {"count": oer, "percent": pct(oer)},
        # Übersicht / Schlüsselzahlen
        "totals": {
            "quellenGesamt": total,
            "inhalteGesamt": meta.get("totalContents", 0),
            "quelldatensaetze": meta["withNode"],
            "crawler": meta["byKind"]["crawler"],
            "manuell": meta["byKind"]["manuell"],
            "bezugsquellenOhneQuelle": bq_total,
        },
        # Inhaltsabdeckung nach Quellentyp (Inhalte, die je Typ erreichbar sind)
        "contentCoverage": {
            "bezugsquelle": bq_content,
            "crawler": crawler_content,
            "quelldatensatz": quelle_content,
            "gesamt": meta.get("totalContents", 0),
        },
        # Abdeckung (Anteil der Records mit gefülltem Merkmal)
        "coverage": {
            "vorschaubild": {"count": prev, "percent": pct(prev)},
            "qualitaetsmerkmale": {"count": qual, "percent": pct(qual)},
            "beschreibung": {"count": desc, "percent": pct(desc)},
            "url": {"count": urlc, "percent": pct(urlc)},
        },
        "erschliessung": {
            "mitQuelldatensatz": meta["withNode"],
            "nurBezugsquelle": bq_total,
            "crawler": meta["byKind"]["crawler"],
            "manuell": meta["byKind"]["manuell"],
            "zweitDatensatz": flags.get("ZWEITDATENSATZ", 0),
        },
        # Inhalte: echte WLO-Prod-Gesamtzahl vs. einer Quelle zuordenbar
        "inhalte": {
            "wloProd": meta.get("wloProdContent"),
            "zuordenbar": meta.get("totalContents", 0),
        },
        # Herkunft: Überschneidung Quelldatensatz <-> Bezugsquelle (beide Perspektiven)
        "herkunft": {
            "quelldatensaetzeGesamt": meta["withNode"],
            "quelldatensatzMitBezugsquelle": schnitt,
            "quelldatensatzOhneBezugsquelle": quelle_ohne_bq,
            "bezugsquellenGesamt": len(distinct_bq),
            "bezugsquelleMitQuelldatensatz": len(bq_with_node),
            # distinct-konsistent: gesamt - mit Quelldatensatz (= reine BQ ohne Knoten)
            "bezugsquelleOhneQuelldatensatz": len(distinct_bq) - len(bq_with_node),
            # Schnittmenge aufgeschlüsselt (exklusiv, summiert zu schnitt): saubere
            # Erst-Zuordnungen (≈ alter „660–700"-Wert) + Zweit-Datensätze + Blacklist
            "schnittmengeSauber": schnitt_sauber,
            "schnittmengeZweitdatensatz": schnitt_zweit,
            "schnittmengeBlacklist": schnitt_black,
            "schnittmengeNurEinmalProBezugsquelle": len(bq_with_node),
        },
        # Korrekturliste (kuratiert) – transparent: wie viel wird bereinigt/bevorzugt
        "korrektur": {
            "whitelist": flags.get("WHITELIST", 0),
            "blacklist": flags.get("BLACKLIST", 0),
            "whitelistImSchnitt": schnitt_white,
            "blacklistImSchnitt": schnitt_black,
        },
        # Crawler nach technischem Typ (normalisiert)
        "crawlerByType": lst(ctype, 12),
        # Provenienz-Marker (öffentlich): wie ist eine Quelle gebunden/eingespielt
        "provenienz": {
            "wloMigration": flags.get("WLO_MIGRATION", 0),
            "legacyBindung": flags.get("LEGACY_BINDUNG", 0),
            "misGetaggt": flags.get("TYP_NICHT_QUELLE", 0),
            "zweitDatensatz": flags.get("ZWEITDATENSATZ", 0),
        },
        "fieldGeneration": {
            "crawlerWithProfile": crawler_fp,
            "totalActiveFields": total_active_fields,
            "avgFieldsPerCrawler": round(total_active_fields / max(1, crawler_fp), 1),
            "byMethod": lst(how, 12),
            # je Feld: Anteil der Crawler, die es erzeugen. Deterministisch sortiert
            # (count desc, dann Name) — field_active stammt aus einem set, dessen
            # Iterationsreihenfolge sonst je Prozess variiert.
            "fieldActivity": [{"value": k, "count": v}
                              for k, v in sorted(field_active.items(), key=lambda kv: (-kv[1], kv[0]))[:18]],
        },
        "licenseDistribution": lst(lic, 15),
        "topSubjects": lst(subj, 25),
        "topLevels": lst(lvl, 15),
        "topLanguages": lst(lang, 10),
        "topLrt": lst(lrt, 15),
        "topCrawler": [{"name": r["name"], "count": r.get("contentCount") or 0,
                        "fields": r.get("fieldActiveCount", 0)} for r in top_crawler],
        "topByContent": [{"name": r["name"], "count": r.get("contentCount") or 0,
                          "kind": r["kind"]} for r in top_content],
    }


def compute_stats_team(recs, meta):
    """Negative-/Datenproblem-Statistiken + Herkunft + Spider-Abgleich. Nur Team."""
    flags = Counter()
    conf = Counter()
    nur_quelle = schnitt = nur_bq = 0
    schnitt_sauber = schnitt_zweit = schnitt_black = 0
    gi = wlo_migr = both_fields = 0
    sb_gi = sb_rs = sb_both = sb_bothdiff = 0
    sb_onlyrs_wlo = sb_onlyrs_spider = sb_onlyrs_named = 0
    singletons = bq_u5 = 0
    url_c = Counter(); title_c = Counter()
    unsichtbar_crawler = 0
    prov = {}                       # Quelle -> Counter(Feld -> Anzahl)
    meta_cnt = Counter(); ki_cnt = Counter(); node_n = 0; ki_base = 0
    for r in recs:
        conf[r.get("confidence", "?")] += 1
        for field, src in r.get("provenance", {}).items():
            prov.setdefault(src, Counter())[field] += 1
        for f in r.get("flags", []):
            flags[f] += 1
        idn = r["identity"]; has_node = bool(idn.get("nodeId")); has_bq = bool(idn.get("bezugsquelle"))
        if r["kind"] == "bezugsquelle":
            nur_bq += 1
            n = r.get("contentCount") or 0
            if n <= 1: singletons += 1
            if n < 5: bq_u5 += 1
        elif has_node and has_bq:
            schnitt += 1
            _fl = r.get("flags", [])
            if "BLACKLIST" in _fl:
                schnitt_black += 1          # mögliche Dublette (Korrekturliste)
            elif "ZWEITDATENSATZ" in _fl:
                schnitt_zweit += 1          # weiterer Datensatz derselben Bezugsquelle
            else:
                schnitt_sauber += 1         # saubere Erst-Zuordnung (≈ alter Wert)
        elif has_node and not has_bq:
            nur_quelle += 1
        if r["kind"] == "crawler" and not has_node:
            unsichtbar_crawler += 1
        intr = r.get("internal", {})
        g = str(intr.get("general_identifier", "")); rs = str(intr.get("replicationsource", ""))
        if g and "spider" in g.lower(): gi += 1
        if rs == "wirlernenonline_spider": wlo_migr += 1
        if g and rs: both_fields += 1
        # Spider-Bindung aufgeschlüsselt (general_identifier vs. replicationsource)
        g2 = g.strip(); rs2 = rs.strip()
        if g2: sb_gi += 1
        if rs2: sb_rs += 1
        if g2 and rs2:
            sb_both += 1
            if g2 != rs2: sb_bothdiff += 1
        elif rs2:                                       # NUR replicationsource (kein gi)
            if rs2 == "wirlernenonline_spider": sb_onlyrs_wlo += 1
            elif rs2.endswith("_spider"): sb_onlyrs_spider += 1   # echter Spider, nur via rs!
            else: sb_onlyrs_named += 1                  # Legacy-Vocab-Name (echte Quelle)
        u = idn.get("url") or r["public"].get("URL", "")
        if u: url_c[u] += 1
        nm = (r["name"] or "").strip().lower()
        if nm: title_c[nm] += 1
        # Füllstände: Metadaten je Quelldatensatz, KI-/Rechtshinweise je Crawler-Profil
        pub = r["public"]
        if has_node:
            node_n += 1
            for label, key in _FUELL_META:
                if pub.get(key) not in (None, "", [], False):
                    meta_cnt[label] += 1
            if r.get("previewUrl"): meta_cnt["Vorschaubild"] += 1
            if r.get("quality"): meta_cnt["Qualitätsmerkmale"] += 1
        if r.get("fieldGeneration"):
            ki_base += 1
            for label, key in _FUELL_KI:
                if pub.get(key) not in (None, "", [], False):
                    ki_cnt[label] += 1

    def dup(c):
        groups = {k: v for k, v in c.items() if v > 1}
        return {"gruppen": len(groups), "ueberzaehlig": sum(v - 1 for v in groups.values()),
                "beispiele": [{"wert": k, "anzahl": v} for k, v in sorted(groups.items(), key=lambda x: -x[1])[:8]]}

    meta_order = [lbl for lbl, _ in _FUELL_META] + ["Vorschaubild", "Qualitätsmerkmale"]
    feld_meta = [{"feld": l, "anzahl": meta_cnt.get(l, 0),
                  "prozent": round(100 * meta_cnt.get(l, 0) / max(1, node_n))} for l in meta_order]
    feld_ki = [{"feld": l, "anzahl": ki_cnt.get(l, 0),
                "prozent": round(100 * ki_cnt.get(l, 0) / max(1, ki_base))} for l, _ in _FUELL_KI]

    return {
        "generatedAt": meta.get("generatedAt"),
        # Zuordnungs-Sicherheit (nur Team): hoch/mittel/niedrig je Verknüpfungslage
        "confidence": dict(conf),
        # Herkunft der Quellen (Schnittmenge Quelldatensatz ↔ Bezugsquelle)
        "herkunft": {
            "quelldatensaetzeGesamt": meta["withNode"],
            "nurQuelldatensatz_ohneBezugsquelle": nur_quelle,
            "schnittmenge_QuelldatensatzUndBezugsquelle": schnitt,
            "nurBezugsquelle_ohneQuelldatensatz": nur_bq,
            # Aufschlüsselung der Schnittmenge (erklärt 1.165 vs. alter Wert ~660–700)
            "schnittmenge_sauber": schnitt_sauber,
            "schnittmenge_zweitDatensatz": schnitt_zweit,
            "schnittmenge_blacklist": schnitt_black,
        },
        # Spider-Abgleich: general_identifier (am Quelldatensatz) vs. Migration
        "spider": {
            "mitCrawlerBindung_generalIdentifier": gi,
            "ausWloAltmigration_replicationsource": wlo_migr,
            "beideFelderGesetzt": both_fields,
        },
        # Spider-Bindung vollständig: general_identifier ↔ replicationsource
        "spiderBindung": {
            "mitGeneralIdentifier": sb_gi,
            "mitReplicationsource": sb_rs,
            "beide": sb_both,
            "beideUnterschiedlich": sb_bothdiff,
            "nurGeneralIdentifier": sb_gi - sb_both,
            "nurReplicationsource": sb_rs - sb_both,
            "nurRs_wloMigration": sb_onlyrs_wlo,        # reine WLO-Migration (kein echter Crawler)
            "nurRs_echterSpider": sb_onlyrs_spider,     # echter Spider NUR via replicationsource
            "nurRs_legacyName": sb_onlyrs_named,        # Legacy-Vocab-Quelle (echt)
            # echte Crawler-/Quell-Bindung = general_identifier ODER replicationsource != WLO
            "echteBindungGesamt": sb_gi + sb_onlyrs_spider + sb_onlyrs_named,
        },
        # Datenprobleme (hart)
        "probleme": {
            "mehrfachInhaltstypen_fehltagging": flags.get("FEHLTAGGING", 0),
            "blacklistEintraege": flags.get("BLACKLIST", 0),
            "zweitDatensaetze": flags.get("ZWEITDATENSATZ", 0),
            "bezugsquellenMit1Inhalt": singletons,
            "bezugsquellenUnter5Inhalte": bq_u5,
            "quelldatensaetzeOhneBezugsquelle": nur_quelle,
            "unsichtbareQuellenMitCrawler": unsichtbar_crawler,
            "doppelteUrl": dup(url_c),
            "doppelteTitel": dup(title_c),
        },
        # Informationsherkunft: welches Feld kommt aus welcher Quelle
        "feldHerkunft": [
            {"quelle": s, "gesamt": sum(c.values()),
             "felder": [{"feld": f, "anzahl": n} for f, n in c.most_common(25)]}
            for s, c in sorted(prov.items(), key=lambda x: -sum(x[1].values()))
        ],
        # Füllstände (Team): wie vollständig sind Metadaten- und KI-/Rechtshinweis-Felder?
        "feldFuellstand": {
            "metadatenBasis": node_n, "kiBasis": ki_base,
            "metadaten": feld_meta, "ki": feld_ki,
        },
    }
