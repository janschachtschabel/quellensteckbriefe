"""Shared pytest fixtures.

These are *characterization* tests: they pin the behavior the app has today so
the modularization refactor can be proven behavior-preserving. They run against
the real data/truth.json snapshot, which is the strongest available oracle.

The team password is forced to a known value *before* importing the app, so the
public/internal security tests are deterministic and never depend on the real
secret in backend/.env.
"""
import os
import sys
from pathlib import Path

import pytest

# Must be set before `import app` (app reads QE_TEAM_PASSWORD at import time).
TEAM_PW = "test-team-pw"
os.environ["QE_TEAM_PASSWORD"] = TEAM_PW

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import app as app_module  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # The context manager fires FastAPI startup -> loads data/truth.json.
    with TestClient(app_module.app) as c:
        yield c


@pytest.fixture(scope="session")
def records(client):
    """Real records loaded into memory by startup (depends on `client` so the
    startup hook has run)."""
    return app_module._DATA["records"]


@pytest.fixture(scope="session")
def meta(client):
    return app_module._DATA["meta"]


@pytest.fixture(scope="session")
def team_pw():
    return TEAM_PW
