"""
push_wpcode.py
Manages WP Code snippets via the LumoKit Bridge REST API.

Usage:
    # Push / upsert a snippet from a JSON file
    python tools/push_wpcode.py .tmp/gtm_snippet.json

    # List all LumoKit-managed snippets on the site
    python tools/push_wpcode.py --list

JSON payload format:
{
    "title":    "Google Tag Manager",
    "code":     "<script>...</script>",
    "location": "site_wide_header",
    "type":     "html",
    "active":   true
}

Supported locations (WP Code built-ins):
    site_wide_header    — <head> on every page
    site_wide_footer    — before </body> on every page
    after_post          — after post content
    before_post         — before post content
    (any custom location slug registered in WP Code Pro)

Supported types: html, php, css, js
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

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/snippets"
AUTH     = (WP_USERNAME, WP_APP_PASSWORD)


def check_env_guard(allow_production: bool) -> None:
    if WP_ENV == "production" and not allow_production:
        print(f"[BLOCKED] WP_ENV is set to 'production' in .env")
        print(f"          Target: {WP_URL}")
        print(f"          Re-run with: --production")
        sys.exit(1)
    if WP_ENV == "production" and allow_production:
        print(f"[WARN] Pushing to PRODUCTION: {WP_URL}")


def list_snippets() -> None:
    response = requests.get(ENDPOINT, auth=AUTH, timeout=30)
    if response.status_code == 200:
        snippets = response.json()
        if not snippets:
            print("[INFO] No LumoKit-managed snippets found.")
            return
        print(f"{'ID':<6} {'Active':<8} {'Location':<25} {'Title'}")
        print("-" * 70)
        for s in snippets:
            active = "Yes" if s.get("active") else "No"
            print(f"{s['id']:<6} {active:<8} {s.get('location',''):<25} {s['title']}")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        print(response.text)
        sys.exit(1)


def push(payload_path: str, allow_production: bool = False) -> None:
    check_env_guard(allow_production)

    path = Path(payload_path)
    if not path.exists():
        print(f"[ERROR] File not found: {payload_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    required = {"title", "code"}
    missing  = required - payload.keys()
    if missing:
        print(f"[ERROR] Payload missing required fields: {missing}")
        sys.exit(1)

    # Apply defaults
    payload.setdefault("location", "site_wide_header")
    payload.setdefault("type", "html")
    payload.setdefault("active", True)

    print(f"[INFO] Pushing snippet '{payload['title']}' → {payload['location']} ...")

    response = requests.post(ENDPOINT, json=payload, auth=AUTH, timeout=30)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK]   {data.get('message')} (id={data.get('id')}, active={data.get('active')})")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--list" in args:
        list_snippets()
    elif not args or args[0].startswith("--"):
        print("Usage:")
        print("  python tools/push_wpcode.py <payload.json> [--production]")
        print("  python tools/push_wpcode.py --list")
        sys.exit(1)
    else:
        allow_production = "--production" in args
        push(args[0], allow_production=allow_production)
