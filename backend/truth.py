"""truth.py — Datenwahrheit-Engine (Zusammenfuehrung).

Fuehrt ALLE bekannten Informationsquellen zu einer kanonischen Quell-Sicht
zusammen ("eine Datenwahrheit") mit Feld-Provenienz und Public/Internal-Trennung.
Die Eingaben werden von truth_loaders gelesen, die Helfer kommen aus truth_text;
dieses Modul enthaelt nur noch die Join-/Record-Bau-Logik und den Build-Einstieg.

Eingaben (Details siehe truth_loaders):
  * Live-API-Caches (quellen_nodes.json, Facetten, vocab_sources.json)
  * Kuratiert (datencrawler.csv, quellen_korrektur.csv)

Ausgabe:
  data/truth.json                   kanonische Records (public + internal getrennt)

Join-Schluessel (Praezedenz):
  1. Spider-Name  (general_identifier / replicationsource <-> Crawler(Spider) <-> Vocab)
  2. publisher_combined (Bezugsquelle)
  3. nodeId / Korrekturliste
"""
from __future__ import annotations
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import field_policy as fp
from truth_loaders import (
    DATENCRAWLER,
    KORREKTUR,
    RAW,
    load_bq_previews,
    load_crawler_profiles,
    load_facet,
    load_korrektur,
    load_nodes,
    load_spider_top_publisher,
    load_vocab,
)
from truth_text import (
    IGNORE_SPIDERS,
    PLACEHOLDER_BQ,
    _is_junk_bq,
    _node_id_from_url,
    _norm,
    _resolve_rs,
    spider_vocab_name,
)

HERE = Path(__file__).parent
DATA = HERE / "data"; DATA.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Datenwahrheit zusammenfuehren
# ---------------------------------------------------------------------------
def build():
    profiles = load_crawler_profiles()
    nodes = load_nodes()
    bq_facet = load_facet("bezugsquellen")
    sp_facet = load_facet("spider")
    vocab = load_vocab()
    korr = load_korrektur()
    spider_top_pub = load_spider_top_publisher()
    bq_prev = load_bq_previews()

    bq_norm = {_norm(k): k for k in bq_facet}

    # Indizes
    nodes_by_spider = defaultdict(list)
    nodes_by_id = {}
    for n in nodes:
        nodes_by_id[n["nodeId"]] = n
        if n["crawlerSpider"]:
            nodes_by_spider[n["crawlerSpider"]].append(n)

    used_nodes = set()
    used_bq = set()
    records = []

    def pick_node(cands):
        if not cands:
            return None
        return sorted(cands, key=lambda n: (n["nodeId"] in used_nodes,  # ungenutzte zuerst
                                            -len(n["description"]), -len(n["subjects"])))[0]

    # --- A) Crawler-Records (Spider als Anker) -----------------------------
    for spider, prof in profiles.items():
        node = pick_node(nodes_by_spider.get(spider, []))
        if node is None:
            # such-unsichtbarer Quelldatensatz: Node-ID aus CSV-Link nutzen
            nid = _node_id_from_url(prof.get("internal", {}).get("quelldatensatzProd", ""))
            if nid and nid in nodes_by_id and nid not in used_nodes:
                node = nodes_by_id[nid]
        bq_from_csv = prof["public"].get("bezugsquelle", "")
        if _is_junk_bq(bq_from_csv):
            bq_from_csv = ""
        top_pub = spider_top_pub.get(spider, "")
        bq = ""
        # Praezedenz: dominanter Publisher des Crawler-Contents (echte Datenwahrheit)
        if top_pub and _norm(top_pub) in bq_norm:
            bq = bq_norm[_norm(top_pub)]
        elif bq_from_csv and _norm(bq_from_csv) in bq_norm and _norm(bq_from_csv) not in PLACEHOLDER_BQ:
            bq = bq_norm[_norm(bq_from_csv)]
        elif node and node["publisher"] and _norm(node["publisher"]) in bq_norm \
                and _norm(node["publisher"]) not in PLACEHOLDER_BQ:
            bq = bq_norm[_norm(node["publisher"])]
        elif top_pub:
            bq = top_pub
        elif bq_from_csv and _norm(bq_from_csv) not in PLACEHOLDER_BQ:
            bq = bq_from_csv
        content = sp_facet.get(spider, 0) or (bq_facet.get(bq, 0) if bq else 0)
        if node:
            used_nodes.add(node["nodeId"])
        if bq:
            used_bq.add(_norm(bq))
        records.append(make_record("crawler", spider, prof, node, bq, content, vocab, korr, bq_prev))

    # --- B) Quelldatensatz-Records (ohne Crawler-Profil) -------------------
    for n in nodes:
        if n["nodeId"] in used_nodes:
            continue
        # Zusatz-Knoten eines bereits vertretenen Crawlers -> konsolidieren
        if n["crawlerSpider"] and n["crawlerSpider"] in profiles:
            used_nodes.add(n["nodeId"])
            continue
        used_nodes.add(n["nodeId"])
        sp = n["crawlerSpider"]
        has_spider = bool(sp)
        bq = ""
        secondary = False
        if n["publisher"] and _norm(n["publisher"]) in bq_norm:
            bq = bq_norm[_norm(n["publisher"])]
            if _norm(bq) in used_bq:
                # Inhaltszahl dieser Bezugsquelle ist bereits an einem Primaer-
                # Record verbucht -> dieser Knoten ist ein Zweit-Datensatz.
                secondary = True
            else:
                used_bq.add(_norm(bq))
        content = 0 if secondary else (bq_facet.get(bq, 0) if bq else 0)
        prof = profiles.get(sp) if has_spider else None
        kind = "crawler" if has_spider else "manuell"
        rec = make_record(kind, sp if has_spider else n["nodeId"], prof, n, bq, content, vocab, korr, bq_prev)
        if secondary:
            rec["flags"].append("ZWEITDATENSATZ")
            rec["erschliessung"] = f"Zweit-Datensatz (Inhalte unter Bezugsquelle '{bq}')"
            rec["confidence"] = "medium"
        records.append(rec)

    # --- C) Bezugsquellen-only (Facette ohne Quelldatensatz) ---------------
    for bq, cnt in bq_facet.items():
        if _is_junk_bq(bq) or _norm(bq) in used_bq:
            continue
        records.append({
            "id": "bq:" + _norm(bq), "kind": "bezugsquelle", "name": bq,
            "identity": {"bezugsquelle": bq, "nodeId": "", "spider": "", "spiderVocabName": "", "url": ""},
            "contentCount": cnt,
            "previewUrl": bq_prev.get(_norm(bq), ""),
            "erschliessung": fp.coarse_erschliessung(cnt, False),
            "public": {"Bezugsquelle": bq, "Inhaltsanzahl": cnt},
            "internal": {},
            "fieldGeneration": [],
            "provenance": {"Bezugsquelle": "WLO-API (Facette)", "Inhaltsanzahl": "WLO-API (Facette)"},
            "flags": ["FACETS_ONLY"],
            "confidence": "low",
        })

    return records


def make_record(kind, anchor, prof, node, bq, content, vocab, korr, bq_prev=None):
    bq_prev = bq_prev or {}
    node_title = node["title"] if node and node["title"] else ""
    prof_titel = prof["public"].get("titel") if prof else ""
    if kind == "crawler":
        name = bq or node_title or prof_titel or anchor
    else:  # manuell / sonst: Datensatz-Titel ist der Quellenname
        name = node_title or bq or prof_titel or anchor
    spider = prof["spider"] if prof else (node["crawlerSpider"] if node else "")
    # Effektive Bindung: ist kein general_identifier gesetzt, aber replicationsource
    # ist NICHT wirlernenonline_spider, dann ist das die echte Spider-/Quell-Bindung.
    if not spider and node:
        rs = node.get("replicationSource", "")
        if rs and rs not in IGNORE_SPIDERS:
            spider = rs
    public, prov = {}, {}

    def setp(k, v, src):
        if v not in (None, "", [], False):
            public[k] = v
            prov[k] = src

    if node:
        setp("Titel", node["title"], "WLO-API")
        setp("URL", node["wwwUrl"], "WLO-API")
        setp("Beschreibung", node["description"], "WLO-API")
        setp("Lizenz", node["license"], "WLO-API")
        setp("OER", node["oer"], "WLO-API")
        setp("Faecher", node["subjects"], "WLO-API")
        setp("Bildungsstufen", node["educationalContext"], "WLO-API")
        setp("Inhaltstypen", node["oehLrt"], "WLO-API")
        setp("Zielgruppe", node.get("targetGroup"), "WLO-API")
        setp("Alter", node.get("ageRange"), "WLO-API")
        setp("Sprache", node["language"], "WLO-API")
        setp("Sprachniveau", node.get("languageLevel"), "WLO-API")
        setp("Zielsprache", node.get("languageTarget"), "WLO-API")
        setp("Lehrplanbezug", node.get("curriculum"), "WLO-API")
        setp("FSK", node.get("fsk"), "WLO-API")
        setp("Schlagworte", node["keywords"], "WLO-API")
        setp("Urheber", node.get("author"), "WLO-API")     # Live-Autor bevorzugt
    if prof:
        pp = prof["public"]
        setp("URL", pp.get("url") or public.get("URL", ""), prov.get("URL", "datencrawler.csv"))
        if "Urheber" not in public:                         # CSV nur als Fallback
            setp("Urheber", pp.get("urheber"), "datencrawler.csv")
        setp("robots.txt", pp.get("robotsTxt"), "datencrawler.csv")
        setp("TDM-Hinweis (§44b)", pp.get("tdmHinweis"), "datencrawler.csv")
        setp("AGB/Nutzungsbedingungen", pp.get("agb"), "datencrawler.csv")
        setp("Lizenz-Check", pp.get("lizenzCheck"), "datencrawler.csv")
        setp("API-Nutzungsbedingungen", pp.get("apiNutzung"), "datencrawler.csv")
    setp("Bezugsquelle", bq, "WLO-API (Facette)")
    setp("Inhaltsanzahl", content, "WLO-API (Facette)")

    internal = {}
    if prof:
        for k, v in prof["internal"].items():
            if v:
                internal[k] = v
    if node:
        internal.update({
            "Erschliessungsstatus (genau)": node["editorialStatus"],
            "Workflow-Status": node["wfStatus"],
            "Node-ID": node["nodeId"],
            "replicationsource": _resolve_rs(node["replicationSource"], vocab),
            "general_identifier": node["generalIdentifier"],
            "zuletzt geaendert": node["modified"],
        })
        k = korr.get(node["nodeId"])
        if k:
            internal["Korrekturliste"] = k["liste"] or "—"

    flags = []
    if node and node["multiType"]:
        flags.append("FEHLTAGGING")
    if node:
        kk = korr.get(node["nodeId"])
        if kk and kk["liste"]:
            flags.append(kk["liste"].upper())
        # Provenienz-Marker (öffentlich, als Badges):
        if node.get("replicationSource", "") == "wirlernenonline_spider":
            flags.append("WLO_MIGRATION")           # über die WLO-Datenmigration eingespielt
        if spider and spider.startswith("http"):
            flags.append("LEGACY_BINDUNG")           # Bindung via Legacy-Vocab-URI (kein technischer Spider)
        if spider and not any("quelle" in str(x).lower() for x in node.get("oehLrt", [])):
            flags.append("TYP_NICHT_QUELLE")         # echte Bindung, aber LRT ≠ Quelle (mis-getaggt)
    if not node:
        flags.append("FACETS_ONLY")
    if public.get("OER"):
        flags.append("OER")

    vocab_name = spider_vocab_name(spider, vocab) if spider else ""

    return {
        "id": (("crawler:" + spider) if kind == "crawler" and spider else
               ("node:" + node["nodeId"]) if node else ("x:" + str(anchor))),
        "kind": kind,
        "name": name,
        "identity": {
            "bezugsquelle": bq, "nodeId": node["nodeId"] if node else "",
            "spider": spider, "spiderVocabName": vocab_name,
            "url": public.get("URL", ""),
        },
        "contentCount": content,
        "previewUrl": (node["previewUrl"] if node and node.get("previewUrl") else bq_prev.get(_norm(bq), "")),
        "quality": node.get("quality", {}) if node else {},
        "erschliessung": fp.coarse_erschliessung(content, bool(node)),
        "public": public,
        "internal": internal,
        "fieldGeneration": prof["fieldGeneration"] if prof else [],
        "fieldActiveCount": prof["fieldActiveCount"] if prof else 0,
        "provenance": prov,
        "flags": flags,
        "confidence": "high" if (node and (spider or bq)) else ("medium" if node or bq else "low"),
    }


def main():
    records = build()
    # nach Inhaltsmenge sortieren
    records.sort(key=lambda r: -(r.get("contentCount") or 0))
    cmeta = {}
    if RAW and (RAW / "cache_meta.json").exists():
        try:
            cmeta = json.loads((RAW / "cache_meta.json").read_text(encoding="utf-8"))
        except Exception:
            cmeta = {}
    meta = {
        "total": len(records),
        "byKind": {k: sum(1 for r in records if r["kind"] == k) for k in ("crawler", "manuell", "bezugsquelle")},
        "withFieldProfile": sum(1 for r in records if r.get("fieldGeneration")),
        "withNode": sum(1 for r in records if r["identity"]["nodeId"]),
        # Inhalte, die einer Quelle (Crawler/Quelldatensatz/manuell) zugeordnet sind
        "totalContents": sum(r.get("contentCount") or 0 for r in records if r["kind"] != "bezugsquelle"),
        # echte WLO-Prod-Gesamtzahl ALLER Inhalte (Facetten-pagination.total, via fetcher)
        "wloProdContent": cmeta.get("wloProdContentTotal"),
        # Datenstand = Zeitpunkt des Live-Abrufs (fetcher), nicht des truth-Builds
        "generatedAt": cmeta.get("fetchedAt") or time.strftime("%Y-%m-%d %H:%M"),
    }
    (DATA / "truth.json").write_text(json.dumps({"meta": meta, "records": records}, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2), file=sys.stderr)
    print(f"Inputs: nodes={'ok' if RAW else 'FEHLT'} crawler={DATENCRAWLER and DATENCRAWLER.name} "
          f"korrektur={KORREKTUR and KORREKTUR.name}", file=sys.stderr)
    return meta


if __name__ == "__main__":
    main()
