"""Golden-snapshot guard: the complex endpoints must produce byte-for-byte the
same JSON after the modularization refactor as before it. Regenerate the
expected files deliberately with `python tests/golden/_generate.py`."""
import json
from pathlib import Path

import pytest

GOLDEN = Path(__file__).parent / "golden"

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
    assert live == expected
