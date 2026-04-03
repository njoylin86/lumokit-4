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
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load credentials from .env (project root, one level up from tools/)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

WP_URL      = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/components"


def push(payload_path: str) -> None:
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
        print("Usage: python tools/push_to_wp.py <path_to_payload.json>")
        sys.exit(1)

    push(sys.argv[1])
