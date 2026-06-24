"""filtering.py — Filterlogik fuer die Quellenliste.

Reine Funktion ueber die Records (keine Web-/IO-Abhaengigkeit). Bildet die
Auswahl-Dimensionen des Frontends ab; die Provenienz-Regeln (echte Bindung,
WLO-Migration, Blacklist-Ausblendung) sind hier zentral dokumentiert.
"""
from config import WLO_SPIDERS


def filter_records(recs, q, kind, oer, subject, level, min_count, has_node, only_field_profile,
                   license_=None, language=None, lrt=None, flag=None,
                   has_bezugsquelle=None, spider_real=False, wlo_migration=False, exclude_wlo=False,
                   show_blacklist=False, has_spider=None):
    out = []
    ql = q.lower().strip() if q else None
    for r in recs:
        # Blacklist = aussortierte Nicht-Quellen (Einzelmaterialien/Dubletten): standardmäßig
        # ausblenden, außer der Filter fragt sie explizit an (flag=BLACKLIST oder show_blacklist).
        if "BLACKLIST" in r.get("flags", []) and flag != "BLACKLIST" and not show_blacklist:
            continue
        if kind and r["kind"] != kind:
            continue
        if has_node is not None and bool(r["identity"].get("nodeId")) != has_node:
            continue
        if has_bezugsquelle is not None and bool(r["identity"].get("bezugsquelle")) != has_bezugsquelle:
            continue
        if has_spider is not None and bool(r["identity"].get("spider")) != has_spider:
            continue
        if spider_real:
            _g = str((r.get("internal") or {}).get("general_identifier", "")).strip()
            _rs = str((r.get("internal") or {}).get("replicationsource", "")).strip()
            # echte Bindung = general_identifier ODER replicationsource != wirlernenonline_spider
            if not (_g or (_rs and _rs != "wirlernenonline_spider")):
                continue
        _sp = str(r["identity"].get("spider", "")).strip()
        if exclude_wlo and _sp in WLO_SPIDERS:
            continue
        if wlo_migration and not (
                str((r.get("internal") or {}).get("replicationsource", "")) == "wirlernenonline_spider"
                or _sp in WLO_SPIDERS):
            continue
        if oer is not None and ("OER" in r.get("flags", [])) != oer:
            continue
        if min_count and (r["contentCount"] or 0) < min_count:
            continue
        if only_field_profile and not r.get("fieldGeneration"):
            continue
        if license_ and r["public"].get("Lizenz", "") != license_:
            continue
        if language and r["public"].get("Sprache", "") != language:
            continue
        if lrt and not any(lrt.lower() in s.lower() for s in r["public"].get("Inhaltstypen", [])):
            continue
        if flag and flag not in r.get("flags", []):
            continue
        if subject and not any(subject.lower() in s.lower() for s in r["public"].get("Faecher", [])):
            continue
        if level and not any(level.lower() in s.lower() for s in r["public"].get("Bildungsstufen", [])):
            continue
        if ql:
            hay = " ".join([r["name"], r["identity"].get("bezugsquelle", ""),
                            str(r["public"].get("Beschreibung", "")),
                            " ".join(r["public"].get("Faecher", []))]).lower()
            if ql not in hay:
                continue
        out.append(r)
    return out
