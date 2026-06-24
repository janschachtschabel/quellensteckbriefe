"""views.py — Serialisierung der Records fuer die API.

Setzt die server-seitige Public/Internal-Trennung (siehe field_policy) um und
liefert die flache Export-Sicht (CSV/JSON). Die EINE Stelle, die entscheidet,
welche Felder eine oeffentliche Antwort verlassen.
"""
import field_policy as fp


def public_view(r: dict) -> dict:
    """Record OHNE interne Felder (serverseitige Trennung)."""
    return {
        "id": r["id"], "name": r["name"], "kind": r["kind"],
        "contentCount": r["contentCount"], "erschliessung": r["erschliessung"],
        "identity": {k: v for k, v in r["identity"].items()},
        "public": r["public"], "provenance": r["provenance"],
        "fieldGeneration": r.get("fieldGeneration", []),
        "fieldActiveCount": r.get("fieldActiveCount", 0),
        "previewUrl": r.get("previewUrl", ""),
        "quality": r.get("quality", {}),
        "flags": [f for f in r.get("flags", []) if f in fp.PUBLIC_FLAGS],
        "confidence": r["confidence"],
        "hasInternal": bool(r.get("internal")),
    }


def full_view(r: dict) -> dict:
    v = public_view(r)
    v["internal"] = r.get("internal", {})
    v["flags"] = r.get("flags", [])   # inkl. interne Flags
    return v


EXPORT_COLS = ["id", "name", "kind", "bezugsquelle", "nodeId", "spider", "spiderVocabName",
               "contentCount", "erschliessung", "url", "Lizenz", "OER", "Faecher",
               "Bildungsstufen", "Inhaltstypen", "Sprache", "fieldActiveCount", "flags", "confidence"]


def flat(r: dict) -> dict:
    p = r["public"]; idn = r["identity"]
    return {
        "id": r["id"], "name": r["name"], "kind": r["kind"],
        "bezugsquelle": idn.get("bezugsquelle", ""), "nodeId": idn.get("nodeId", ""),
        "spider": idn.get("spider", ""), "spiderVocabName": idn.get("spiderVocabName", ""),
        "contentCount": r.get("contentCount") or 0, "erschliessung": r.get("erschliessung", ""),
        "url": p.get("URL", ""), "Lizenz": p.get("Lizenz", ""),
        "OER": "ja" if p.get("OER") else "", "Faecher": " | ".join(p.get("Faecher", [])),
        "Bildungsstufen": " | ".join(p.get("Bildungsstufen", [])),
        "Inhaltstypen": " | ".join(p.get("Inhaltstypen", [])),
        "Sprache": p.get("Sprache", ""), "fieldActiveCount": r.get("fieldActiveCount", 0),
        "flags": " | ".join(f for f in r.get("flags", []) if f in fp.PUBLIC_FLAGS),
        "confidence": r.get("confidence", ""),
    }
