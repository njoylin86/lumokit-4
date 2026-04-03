"""
pull_from_wp.py
Fetches the current state of all (or a specific) LumoKit component from WordPress.

Usage:
    python tools/pull_from_wp.py                        # list all components
    python tools/pull_from_wp.py lumo/hero-section      # print one component
    python tools/pull_from_wp.py lumo/hero-section --save   # save to .tmp/

Per the "Pull Before Push" rule in CLAUDE.md, always run this before modifying
an existing component to avoid overwriting client content.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load credentials from .env (project root)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/components"


def fetch_all() -> list:
    response = requests.get(
        ENDPOINT,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )
    if response.status_code != 200:
        print(f"[ERROR] HTTP {response.status_code}: {response.text}")
        sys.exit(1)
    return response.json()


def pull(block_name: str | None, save: bool) -> None:
    components = fetch_all()

    if not block_name:
        # Just list all registered components
        print(f"[INFO] {len(components)} component(s) registered on {WP_URL}:\n")
        for c in components:
            print(f"  - {c['block_name']}  (id={c['id']}, title='{c['title']}')")
        return

    # Find the requested component
    match = next((c for c in components if c["block_name"] == block_name), None)

    if not match:
        print(f"[ERROR] Component '{block_name}' not found on {WP_URL}.")
        sys.exit(1)

    print(json.dumps(match, indent=2, ensure_ascii=False))

    if save:
        tmp_dir = ROOT / ".tmp"
        tmp_dir.mkdir(exist_ok=True)
        slug     = block_name.replace("/", "-")
        out_path = tmp_dir / f"{slug}_pulled.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(match, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull LumoKit component(s) from WordPress.")
    parser.add_argument("block_name", nargs="?", help='e.g. "lumo/hero-section"')
    parser.add_argument("--save", action="store_true", help="Save result to .tmp/")
    args = parser.parse_args()

    pull(args.block_name, args.save)
