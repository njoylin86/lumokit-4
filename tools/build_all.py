"""
build_all.py
Pushes all components and builds the full site from a single bundle JSON file.

Usage:
    python tools/build_all.py .tmp/[client]_bundle.json [--production]

Bundle format:
    {
      "site_name": "Client Name",
      "components": [
        {
          "block_name": "lumo/block-name",
          "title": "Block Title",
          "html_template": "<section>...</section>",
          "schema": [...]
        }
      ],
      "pages": [
        {
          "title": "Hem",
          "slug": "hem",
          "menu_label": null,
          "blocks": ["lumo/block-name"]
        }
      ]
    }
"""

import json
import os
import subprocess
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

COMPONENTS_ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/components"
SITE_ENDPOINT       = f"{WP_URL}/wp-json/lumokit/v1/site"
SETTINGS_ENDPOINT   = f"{WP_URL}/wp-json/lumokit/v1/settings"
OPTIONS_ENDPOINT    = f"{WP_URL}/wp-json/lumokit/v1/options"
SNIPPETS_ENDPOINT   = f"{WP_URL}/wp-json/lumokit/v1/snippets"


def check_env_guard(allow_production: bool) -> None:
    if WP_ENV == "production" and not allow_production:
        print(f"[BLOCKED] WP_ENV is set to 'production' in .env")
        print(f"          Target: {WP_URL}")
        print(f"          Refusing to build without explicit --production flag.")
        print(f"          If you are sure, re-run with: --production")
        sys.exit(1)
    if WP_ENV == "production" and allow_production:
        print(f"[WARN] Building on PRODUCTION: {WP_URL}")


def push_component(component: dict) -> bool:
    required = {"block_name", "title", "html_template", "schema"}
    missing = required - component.keys()
    if missing:
        print(f"  [ERROR] Component missing fields: {missing}")
        return False

    response = requests.post(
        COMPONENTS_ENDPOINT,
        json=component,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"  [OK]   {data.get('message')} (block_name={data.get('block_name')})")
        return True
    else:
        print(f"  [ERROR] HTTP {response.status_code} for '{component.get('block_name')}'")
        try:
            print(f"         {response.json()}")
        except Exception:
            print(f"         {response.text}")
        return False


def push_platform_config(config: dict) -> None:
    """Push platform_config to /settings — stores as hidden WP options."""
    allowed_keys = {"platform", "trustindex_script", "booking_widget_id"}
    payload = {k: v for k, v in config.items() if k in allowed_keys}

    if not payload:
        return

    response = requests.post(
        SETTINGS_ENDPOINT,
        json=payload,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        updated = data.get("updated", [])
        print(f"  [OK]   Platform config set: {', '.join(updated)}")
    else:
        print(f"  [ERROR] HTTP {response.status_code} when pushing platform config")
        try:
            print(f"         {response.json()}")
        except Exception:
            print(f"         {response.text}")


def push_global_settings(settings: dict) -> None:
    response = requests.post(
        OPTIONS_ENDPOINT,
        json=settings,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK]   Global settings set: {', '.join(data.get('updated', []))}")
    else:
        print(f"  [ERROR] HTTP {response.status_code} when pushing global settings")
        try:
            print(f"         {response.json()}")
        except Exception:
            print(f"         {response.text}")


def push_snippets(snippets: list) -> None:
    for snippet in snippets:
        response = requests.post(
            SNIPPETS_ENDPOINT,
            json=snippet,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK]   Snippet '{snippet.get('title')}': {data.get('message', 'saved')}")
        else:
            print(f"  [ERROR] HTTP {response.status_code} for snippet '{snippet.get('title')}'")
            try:
                print(f"         {response.json()}")
            except Exception:
                print(f"         {response.text}")


def build_site(site_name: str, pages: list) -> None:
    spec = {"site_name": site_name, "pages": pages}

    response = requests.post(
        SITE_ENDPOINT,
        json=spec,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=60,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"  [OK]   {data.get('message')}")
        for page in data.get("pages", []):
            print(f"         {page.get('message')} → {page.get('page_url')}")
    else:
        print(f"  [ERROR] HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        sys.exit(1)


def build_all(bundle_path: str, allow_production: bool = False) -> None:
    check_env_guard(allow_production)

    path = Path(bundle_path)
    if not path.exists():
        print(f"[ERROR] File not found: {bundle_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    site_name       = bundle.get("site_name")
    components      = bundle.get("components", [])
    pages           = bundle.get("pages", [])
    platform_config = bundle.get("platform_config")
    global_settings = bundle.get("global_settings")
    snippets        = bundle.get("snippets", [])

    if not site_name or not pages:
        print("[ERROR] Bundle must contain 'site_name' and 'pages'.")
        sys.exit(1)

    total_steps = 2 + (1 if platform_config else 0) + (1 if global_settings else 0) + (1 if snippets else 0)
    step = 0

    # --- Step 0a: Push platform config (hidden, only if present) ----------
    if platform_config:
        step += 1
        print(f"\n[{step}/{total_steps}] Pushing platform config...")
        push_platform_config(platform_config)

    # --- Step 0b: Push global settings (company info etc.) ----------------
    if global_settings:
        step += 1
        print(f"\n[{step}/{total_steps}] Pushing global settings...")
        push_global_settings(global_settings)

    # --- Step 0c: Push snippets (Google Fonts, analytics etc.) -----------
    if snippets:
        step += 1
        print(f"\n[{step}/{total_steps}] Pushing {len(snippets)} snippet(s)...")
        push_snippets(snippets)

    # --- Step 1: Push components ------------------------------------------
    step += 1
    if components:
        print(f"\n[{step}/{total_steps}] Pushing {len(components)} component(s)...")
        failed = []
        for component in components:
            ok = push_component(component)
            if not ok:
                failed.append(component.get("block_name", "unknown"))

        if failed:
            print(f"\n[ERROR] {len(failed)} component(s) failed to push: {failed}")
            print("        Fix the errors above before building the site.")
            sys.exit(1)
    else:
        print(f"\n[{step}/{total_steps}] No components in bundle — skipping component push.")

    # --- Step 2: Build site -----------------------------------------------
    step += 1
    print(f"\n[{step}/{total_steps}] Building site '{site_name}' with {len(pages)} page(s)...")
    build_site(site_name, pages)

    # --- Step 3: Compile & push CSS from this bundle only -----------------
    print(f"\n[CSS] Compiling Tailwind CSS from {Path(bundle_path).name} ...")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "compile_tailwind.py"), str(path)],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("[WARN] CSS compilation failed — push styles manually with compile_tailwind.py")

    print(f"\n[DONE] {site_name} is live.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/build_all.py <path_to_bundle.json> [--production]")
        sys.exit(1)

    allow_production = "--production" in sys.argv
    build_all(sys.argv[1], allow_production=allow_production)
