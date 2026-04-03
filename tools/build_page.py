"""
build_page.py
Creates a WordPress page and populates it with LumoKit blocks in order.

Usage:
    python tools/build_page.py .tmp/[client]_page.json

Page spec format:
    {
      "title":  "Hem",
      "slug":   "hem",
      "blocks": [
        "lumo/hero-section",
        "lumo/services-row",
        "lumo/contact-form"
      ]
    }
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/pages"


def build_page(spec_path: str) -> None:
    path = Path(spec_path)
    if not path.exists():
        print(f"[ERROR] File not found: {spec_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    if not spec.get("title") or not spec.get("blocks"):
        print("[ERROR] Page spec must contain 'title' and 'blocks'.")
        sys.exit(1)

    print(f"[INFO] Building page '{spec['title']}' with {len(spec['blocks'])} block(s)...")

    response = requests.post(
        ENDPOINT,
        json=spec,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK]   {data.get('message')}")
        print(f"       Page URL: {data.get('page_url')}")
        print(f"       Edit URL: {data.get('edit_url')}")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/build_page.py <path_to_page_spec.json>")
        sys.exit(1)

    build_page(sys.argv[1])
