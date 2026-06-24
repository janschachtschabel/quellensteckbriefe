"""Regenerate golden snapshots of the complex endpoints.

Run this ONLY to intentionally update the expected output (e.g. after a real
data refresh or a deliberate behavior change):

    python tests/golden/_generate.py

test_golden.py compares live responses against these files, so they are the
guard that the modularization refactor did not alter any endpoint output.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QE_TEAM_PASSWORD", "test-team-pw")
BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

# (filename, path, needs_team_password)
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

OUT = Path(__file__).parent
PW = os.environ["QE_TEAM_PASSWORD"]

if __name__ == "__main__":
    with TestClient(app.app) as c:
        for fn, path, needs_pw in CASES:
            headers = {"X-Team-Password": PW} if needs_pw else {}
            resp = c.get(path, headers=headers)
            resp.raise_for_status()
            (OUT / fn).write_text(
                json.dumps(resp.json(), ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8")
            print(f"wrote {fn} ({len(resp.content)} bytes)")
