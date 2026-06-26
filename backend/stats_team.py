"""stats_team.py — internal team statistics (/api/stats/team).

Data problems, origin (Quelldatensatz↔Bezugsquelle), spider reconciliation and
field fill levels. Pure function over (records, meta) — no web/IO
dependency; intended for the team only (server-side password-protected).
"""
from collections import Counter

from stats_common import _FUELL_KI, _FUELL_META


def compute_stats_team(recs, meta):
    """Negative/data-problem statistics + origin + spider reconciliation. Team only."""
    flags = Counter()
    conf = Counter()
    nur_quelle = schnitt = nur_bq = 0
    schnitt_sauber = schnitt_zweit = schnitt_black = 0
    gi = wlo_migr = both_fields = 0
    sb_gi = sb_rs = sb_both = sb_bothdiff = 0
    sb_onlyrs_wlo = sb_onlyrs_spider = sb_onlyrs_named = 0
    bq_u5 = 0
    url_c = Counter(); title_c = Counter()
    prov = {}                       # source -> Counter(field -> count)
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
            if (r.get("contentCount") or 0) < 5: bq_u5 += 1
        elif has_node and has_bq:
            schnitt += 1
            _fl = r.get("flags", [])
            if "BLACKLIST" in _fl:
                schnitt_black += 1          # possible duplicate (correction list)
            elif "ZWEITDATENSATZ" in _fl:
                schnitt_zweit += 1          # additional record of the same Bezugsquelle
            else:
                schnitt_sauber += 1         # clean first assignment (≈ old value)
        elif has_node and not has_bq:
            nur_quelle += 1
        intr = r.get("internal", {})
        g = str(intr.get("general_identifier", "")); rs = str(intr.get("replicationsource", ""))
        if g and "spider" in g.lower(): gi += 1
        if rs == "wirlernenonline_spider": wlo_migr += 1
        if g and rs: both_fields += 1
        # Spider binding broken down (general_identifier vs. replicationsource)
        g2 = g.strip(); rs2 = rs.strip()
        if g2: sb_gi += 1
        if rs2: sb_rs += 1
        if g2 and rs2:
            sb_both += 1
            if g2 != rs2: sb_bothdiff += 1
        elif rs2:                                       # ONLY replicationsource (no gi)
            if rs2 == "wirlernenonline_spider": sb_onlyrs_wlo += 1
            elif rs2.endswith("_spider"): sb_onlyrs_spider += 1   # real spider, only via rs!
            else: sb_onlyrs_named += 1                  # legacy vocab name (real source)
        u = idn.get("url") or r["public"].get("URL", "")
        if u: url_c[u] += 1
        nm = (r["name"] or "").strip().lower()
        if nm: title_c[nm] += 1
        # Fill levels: metadata per Quelldatensatz, AI/legal notes per crawler profile
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
        # Assignment confidence (team only): high/medium/low depending on linkage state
        "confidence": dict(conf),
        # Origin of the sources (intersection Quelldatensatz ↔ Bezugsquelle)
        "herkunft": {
            "quelldatensaetzeGesamt": meta["withNode"],
            "nurQuelldatensatz_ohneBezugsquelle": nur_quelle,
            "schnittmenge_QuelldatensatzUndBezugsquelle": schnitt,
            "nurBezugsquelle_ohneQuelldatensatz": nur_bq,
            # Breakdown of the intersection (explains 1,165 vs. old value ~660–700)
            "schnittmenge_sauber": schnitt_sauber,
            "schnittmenge_zweitDatensatz": schnitt_zweit,
            "schnittmenge_blacklist": schnitt_black,
        },
        # Spider reconciliation: general_identifier (on the Quelldatensatz) vs. migration
        "spider": {
            "mitCrawlerBindung_generalIdentifier": gi,
            "ausWloAltmigration_replicationsource": wlo_migr,
            "beideFelderGesetzt": both_fields,
        },
        # Spider binding complete: general_identifier ↔ replicationsource
        "spiderBindung": {
            "mitGeneralIdentifier": sb_gi,
            "mitReplicationsource": sb_rs,
            "beide": sb_both,
            "beideUnterschiedlich": sb_bothdiff,
            "nurGeneralIdentifier": sb_gi - sb_both,
            "nurReplicationsource": sb_rs - sb_both,
            "nurRs_wloMigration": sb_onlyrs_wlo,        # pure WLO migration (no real crawler)
            "nurRs_echterSpider": sb_onlyrs_spider,     # real spider ONLY via replicationsource
            "nurRs_legacyName": sb_onlyrs_named,        # legacy vocab source (real)
            # real crawler/source binding = general_identifier OR replicationsource != WLO
            "echteBindungGesamt": sb_gi + sb_onlyrs_spider + sb_onlyrs_named,
        },
        # Data problems — aligned 1:1 with the team filter (each key = one flag=<NAME>
        # option), so the chart and the filter always show the same set by construction.
        "probleme": {
            "mischTypen_fehltagging": flags.get("FEHLTAGGING", 0),
            "zweitDatensaetze": flags.get("ZWEITDATENSATZ", 0),
            "bezugsquelleEinzelinhalt": flags.get("BQ_EINZELINHALT", 0),
            "dublettenVerdacht": flags.get("DUBLETTE_VERDACHT", 0),
            "metadatenDuenn": flags.get("METADATEN_DUENN", 0),
            "blacklist": flags.get("BLACKLIST", 0),
            "quelldatensatzOhneBezugsquelle": flags.get("QD_OHNE_BEZUGSQUELLE", 0),
            "bindungUnvollstaendig": flags.get("BINDUNG_UNVOLLSTAENDIG", 0),
            "typNichtQuelle": flags.get("TYP_NICHT_QUELLE", 0),
            "bezugsquelleOhneQuelldatensatz": flags.get("BQ_OHNE_QD", 0),
            "ohneStatus": flags.get("OHNE_STATUS", 0),
            "statusInkonsistent": flags.get("STATUS_INKONSISTENT", 0),
            "nichtPubliziert": flags.get("NICHT_PUBLIZIERT", 0),
            "spiderUneindeutig": flags.get("SPIDER_UNEINDEUTIG", 0),
            # extra context + detail for the dedicated duplicate cards (not in the bar list)
            "bezugsquellenUnter5Inhalte": bq_u5,
            "doppelteUrl": dup(url_c),
            "doppelteTitel": dup(title_c),
        },
        # Information origin: which field comes from which source
        "feldHerkunft": [
            {"quelle": s, "gesamt": sum(c.values()),
             "felder": [{"feld": f, "anzahl": n} for f, n in c.most_common(25)]}
            for s, c in sorted(prov.items(), key=lambda x: -sum(x[1].values()))
        ],
        # Fill levels (team): how complete are the metadata and AI/legal-note fields?
        "feldFuellstand": {
            "metadatenBasis": node_n, "kiBasis": ki_base,
            "metadaten": feld_meta, "ki": feld_ki,
        },
    }
