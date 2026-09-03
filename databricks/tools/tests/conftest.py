"""Put the tools directory on sys.path so tests import modules by bare name.

The tools are scripts, not an installed package: they are run as
`.venv/bin/python databricks/tools/build_decks.py`. This keeps the test
imports matching how the tools are actually invoked.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
