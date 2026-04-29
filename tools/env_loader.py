"""
env_loader.py
Centralised .env resolution for LumoKit tools.

Fallback chain (first match wins):
  1. --env <path>          explicit flag anywhere in sys.argv
  2. clients/<client>/.env inferred from a bundle path arg (e.g. .tmp/ostra-bageriet_bundle.json)
  3. <ROOT>/.env           project-root default
"""

import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def _explicit_env_flag() -> Path | None:
    """Return the path passed via --env <path>, removing both tokens from sys.argv."""
    for i, arg in enumerate(sys.argv):
        if arg == "--env" and i + 1 < len(sys.argv):
            path = Path(sys.argv[i + 1])
            del sys.argv[i : i + 2]
            return path if path.is_absolute() else ROOT / path
    return None


def _client_env_from_bundle() -> Path | None:
    """
    Scan sys.argv for a bundle path like .tmp/<client>_bundle.json and
    resolve clients/<client>/.env if it exists.
    """
    bundle_pattern = re.compile(r"([a-z0-9][a-z0-9_-]*)_bundle\.json$", re.I)
    for arg in sys.argv[1:]:
        m = bundle_pattern.search(arg)
        if m:
            candidate = ROOT / "clients" / m.group(1) / ".env"
            if candidate.exists():
                return candidate
    return None


def load_env() -> Path:
    """
    Resolve and load the correct .env file.
    Returns the path that was loaded.
    """
    env_file = (
        _explicit_env_flag()
        or _client_env_from_bundle()
        or ROOT / ".env"
    )
    load_dotenv(env_file)
    return env_file
