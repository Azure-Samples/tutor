"""Path setup for questions tests.

Adds ``apps/`` (namespace package root for ``questions.app.*``) and
``lib/src`` (``tutor_lib``) to ``sys.path`` so that top-level imports
in the test modules resolve correctly.

Environment variables required by ``tutor_lib.config`` are set before
any application module is imported to satisfy Pydantic validation.
"""

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

for _entry in (
    str(_REPO_ROOT / "apps"),
    str(_REPO_ROOT / "apps" / "questions"),
    str(_REPO_ROOT / "lib" / "src"),
):
    if _entry in sys.path:
        sys.path.remove(_entry)
    sys.path.insert(0, _entry)

# Clear any previously loaded 'app' modules to avoid cross-service contamination
for _mod_name in list(sys.modules):
    if _mod_name == "app" or _mod_name.startswith("app."):
        del sys.modules[_mod_name]

# Provide required env vars so tutor_lib.config can be imported at collection time.
os.environ.setdefault("COSMOS_ENDPOINT", "https://localhost:8081/")
os.environ.setdefault("COSMOS_DATABASE", "unit-test-db")
os.environ.setdefault("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
