"""truth_text.py — Text-Normalisierung & kleine Parser-/Vokabular-Helfer.

Reine Funktionen (keine I/O): Normalisierung von Namen/URLs, Property-Zugriff auf
edu-sharing-Knoten und Aufloesung von Spider-/Vokabular-Bezeichnern. Gemeinsames
Blatt-Modul fuer truth_loaders und truth (vermeidet Zyklen).
"""
from __future__ import annotations
import re
import unicodedata

# Spider, die KEINE echte Crawler-Bindung sind, sondern Migrations-Herkunft
# des Datensatz-Knotens (wirlernenonline_spider) -> nicht als Crawler ankern.
IGNORE_SPIDERS = {"wirlernenonline_spider"}

PLACEHOLDER_BQ = {"wirlernenonline"}

# Node-ID aus einem Render-/Komponenten-Link (CSV-Spalte 'Quelldatensatz (Prod)')
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def _node_id_from_url(url):
    m = _UUID_RE.search(url or "")
    return m.group(0) if m else ""


def _norm(t):
    t = unicodedata.normalize("NFD", str(t or "").strip().lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t)


def _nurl(u):
    if not u:
        return ""
    u = re.sub(r"^http://", "https://", str(u).strip())
    u = re.sub(r"^(https://)www\.", r"\1", u)
    return u.rstrip("/").lower()


def p1(props, key):
    v = props.get(key)
    if isinstance(v, list):
        return str(v[0]) if v and v[0] not in (None, "") else ""
    return str(v) if v not in (None, "") else ""


def pA(props, key):
    return [str(v) for v in (props.get(key) or []) if v]


def _clean_q(v):
    """Sternchen entfernen (jsPDF/Anzeige), Whitespace normalisieren."""
    v = re.sub(r"[✰★☆⭐]", "", str(v or "")).strip()
    return re.sub(r"\s+", " ", v)


def _age(props):
    """Typische Altersspanne als 'x–y Jahre'; Default 0–99 (= alle) wird ausgelassen."""
    af = p1(props, "ccm:educationaltypicalagerange_from")
    at = p1(props, "ccm:educationaltypicalagerange_to")
    if not af and not at:
        return ""
    if af in ("0", "") and at in ("99", ""):
        return ""
    return f"{af or '?'}–{at or '?'} Jahre"


def _is_junk_bq(bq):
    """Müll-Bezugsquelle (z. B. „0", reine Zahlen, leer) — nicht als Quelle/Name verwenden."""
    s = (bq or "").strip().lower()
    return s in ("", "0", "-", "–", "null", "none", "n/a", "k.a.", "keine") or s.isdigit()


def spider_vocab_name(spider, vocab):
    if spider.startswith("http"):
        return vocab.get(spider.rsplit("/", 1)[-1].lower(), {}).get("label", "")
    return ""


def _resolve_rs(rs, vocab):
    """replicationsource lesbar machen: Legacy-URI (…/vocabs/sources/<uuid>) → Vocab-Name.
    Technische Namen (z. B. bpb_spider) und wirlernenonline_spider bleiben unverändert,
    damit Filter/Statistik weiter darauf prüfen können."""
    s = (rs or "").strip()
    if "vocabs/sources/" in s:
        uid = s.rstrip("/").rsplit("/", 1)[-1].lower()
        return (vocab.get(uid) or {}).get("label") or s
    return s
