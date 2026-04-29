"""
push_to_wp.py
Pushes a LumoKit JSON payload to the WordPress REST API.

Usage:
    python tools/push_to_wp.py .tmp/hero_payload.json

The script reads credentials from the .env file in the project root.
Never hard-code credentials – they live in .env only.
"""

import json
import os
import sys
from pathlib import Path

import requests
from env_loader import ROOT, load_env

# ---------------------------------------------------------------------------
# Load credentials — resolves --env flag, client .env, or root .env
# ---------------------------------------------------------------------------
load_env()

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
WP_ENV          = os.getenv("WP_ENV", "development").strip().lower()

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/components"


def check_env_guard(allow_production: bool) -> None:
    """Block accidental writes to production unless --production flag is passed."""
    if WP_ENV == "production" and not allow_production:
        print(f"[BLOCKED] WP_ENV is set to 'production' in .env")
        print(f"          Target: {WP_URL}")
        print(f"          Refusing to push without explicit --production flag.")
        print(f"          If you are sure, re-run with: --production")
        sys.exit(1)
    if WP_ENV == "production" and allow_production:
        print(f"[WARN] Pushing to PRODUCTION: {WP_URL}")


def push(payload_path: str, allow_production: bool = False) -> None:
    check_env_guard(allow_production)

    # --- Read payload file ------------------------------------------------
    path = Path(payload_path)
    if not path.exists():
        print(f"[ERROR] File not found: {payload_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    required = {"block_name", "title", "html_template", "schema"}
    missing  = required - payload.keys()
    if missing:
        print(f"[ERROR] Payload missing required fields: {missing}")
        sys.exit(1)

    # --- Send POST request -----------------------------------------------
    print(f"[INFO] Pushing '{payload['block_name']}' to {ENDPOINT} ...")

    response = requests.post(
        ENDPOINT,
        json=payload,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )

    # --- Handle response --------------------------------------------------
    if response.status_code == 200:
        data = response.json()
        print(f"[OK]   {data.get('message')} (block_name={data.get('block_name')})")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/push_to_wp.py <path_to_payload.json> [--production]")
        sys.exit(1)

    allow_production = "--production" in sys.argv
    push(sys.argv[1], allow_production=allow_production)
