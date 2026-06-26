"""Golden-snapshot guard: the complex endpoints must produce the same JSON
(data + structure) as the committed snapshots. Two fields legitimately change on
every data refresh and are normalized out before comparing, so a refresh (incl.
the nightly auto-refresh) does not break the suite: the build timestamp
(`generatedAt`) and the preview-URL cache-buster (`dontcache=<n>`). Regenerate the
expected files deliberately with `python tests/golden/_generate.py`."""
import json
import re
from pathlib import Path

import pytest

GOLDEN = Path(__file__).parent / "golden"


def _normalize(obj):
    """Drop volatile values (build timestamp, preview cache-buster) so the snapshots
    pin the data and structure, not values that change on every refresh."""
    if isinstance(obj, dict):
        return {k: ("<ts>" if k == "generatedAt" else _normalize(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(v) for v in obj]
    if isinstance(obj, str):
        return re.sub(r"dontcache=\d+", "dontcache=X", obj)
    return obj

# (filename, path, needs_team_password) — mirrors golden/_generate.py
CASES = [
    ("stats.json", "/api/stats", False),
    ("stats_full.json", "/api/stats/full", False),
    ("stats_team.json", "/api/stats/team", True),
    ("meta_filters.json", "/api/meta/filters", False),
    ("sources_crawler.json",
     "/api/sources?kind=crawler&exclude_wlo=true&page_size=10&sort=contentCount&order=desc", False),
    ("sources_blacklist.json", "/api/sources?flag=BLACKLIST&page_size=10", False),
    ("sources_spider_real.json",
     "/api/sources?spider_real=true&page_size=10&sort=contentCount&order=desc", False),
    ("export_crawler.json", "/api/export.json?kind=crawler", False),
]


@pytest.mark.parametrize("fn,path,needs_pw", CASES, ids=[c[0] for c in CASES])
def test_endpoint_matches_golden(client, team_pw, fn, path, needs_pw):
    headers = {"X-Team-Password": team_pw} if needs_pw else {}
    live = client.get(path, headers=headers).json()
    expected = json.loads((GOLDEN / fn).read_text(encoding="utf-8"))
    assert _normalize(live) == _normalize(expected)
