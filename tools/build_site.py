"""
build_site.py
Creates all pages and a nav menu from a site spec JSON file.

Usage:
    python tools/build_site.py .tmp/[client]_site.json

Site spec format:
    {
      "site_name": "Boxmedia",
      "pages": [
        {
          "title":      "Hem",
          "slug":       "hem",
          "menu_label": "Start",
          "blocks":     ["lumo/hero-section", "lumo/services-row"]
        },
        {
          "title":      "Kontakt",
          "slug":       "kontakt",
          "menu_label": "Kontakt",
          "blocks":     ["lumo/contact-form"]
        }
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
WP_ENV          = os.getenv("WP_ENV", "development").strip().lower()

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/site"


def check_env_guard(allow_production: bool) -> None:
    """Block accidental writes to production unless --production flag is passed."""
    if WP_ENV == "production" and not allow_production:
        print(f"[BLOCKED] WP_ENV is set to 'production' in .env")
        print(f"          Target: {WP_URL}")
        print(f"          Refusing to build without explicit --production flag.")
        print(f"          If you are sure, re-run with: --production")
        sys.exit(1)
    if WP_ENV == "production" and allow_production:
        print(f"[WARN] Building on PRODUCTION: {WP_URL}")


def build_site(spec_path: str, allow_production: bool = False) -> None:
    check_env_guard(allow_production)

    path = Path(spec_path)
    if not path.exists():
        print(f"[ERROR] File not found: {spec_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    if not spec.get("site_name") or not spec.get("pages"):
        print("[ERROR] Site spec must contain 'site_name' and 'pages'.")
        sys.exit(1)

    print(f"[INFO] Building site '{spec['site_name']}' with {len(spec['pages'])} page(s)...")

    response = requests.post(
        ENDPOINT,
        json=spec,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=60,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK]   {data.get('message')}")
        for page in data.get("pages", []):
            print(f"       {page.get('message')} → {page.get('page_url')}")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/build_site.py <path_to_site_spec.json> [--production]")
        sys.exit(1)

    allow_production = "--production" in sys.argv
    build_site(sys.argv[1], allow_production=allow_production)
