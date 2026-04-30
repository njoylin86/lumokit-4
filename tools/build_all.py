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
import time
from datetime import datetime
from pathlib import Path

import requests
from env_loader import ROOT, load_env

load_env()

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
WP_ENV          = os.getenv("WP_ENV", "development").strip().lower()

COMPONENTS_ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/components"
SITE_ENDPOINT       = f"{WP_URL}/wp-json/lumokit/v1/site"
SETTINGS_ENDPOINT   = f"{WP_URL}/wp-json/lumokit/v1/settings"
OPTIONS_ENDPOINT    = f"{WP_URL}/wp-json/lumokit/v1/options"
SNIPPETS_ENDPOINT   = f"{WP_URL}/wp-json/lumokit/v1/snippets"


def retry_post(url: str, payload: dict, max_attempts: int = 3, **kwargs) -> requests.Response:
    """POST with exponential backoff on connection errors and timeouts."""
    for attempt in range(1, max_attempts + 1):
        try:
            return requests.post(url, json=payload, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == max_attempts:
                raise
            wait = 2 ** attempt
            print(f"  [RETRY] {type(e).__name__} — retrying in {wait}s ({attempt}/{max_attempts})...")
            time.sleep(wait)


def load_deploy_state(state_path: Path) -> dict:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_deploy_state(state_path: Path, state: dict) -> None:
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


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

    try:
        response = retry_post(
            COMPONENTS_ENDPOINT,
            component,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            timeout=30,
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"  [ERROR] Could not reach {WP_URL} after 3 attempts: {e}")
        return False

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
    allowed_keys = {"platform", "trustindex_script", "booking_widget_id",
                    "site_reviews_score", "site_reviews_testimonials", "site_booking_api_key"}
    payload = {k: v for k, v in config.items() if k in allowed_keys}

    if not payload:
        return

    try:
        response = retry_post(SETTINGS_ENDPOINT, payload,
                              auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"  [ERROR] Could not reach {WP_URL}: {e}")
        return

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
    try:
        response = retry_post(OPTIONS_ENDPOINT, settings,
                              auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"  [ERROR] Could not reach {WP_URL}: {e}")
        return
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
        try:
            response = retry_post(SNIPPETS_ENDPOINT, snippet,
                                  auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"  [ERROR] Could not reach {WP_URL}: {e}")
            continue
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK]   Snippet '{snippet.get('title')}': {data.get('message', 'saved')}")
        else:
            print(f"  [ERROR] HTTP {response.status_code} for snippet '{snippet.get('title')}'")
            try:
                print(f"         {response.json()}")
            except Exception:
                print(f"         {response.text}")


def build_site(site_name: str, pages: list, extra_menu_items: list | None = None) -> None:
    spec = {"site_name": site_name, "pages": pages}
    if extra_menu_items:
        spec["extra_menu_items"] = extra_menu_items

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


def print_mode_banner(overwrite_content: bool, keep_pages: set, force: bool) -> None:
    """Always show what mode we're running in so the user can't forget the flags."""
    print()
    print("=" * 72)
    print(" LUMOKIT BUILD — KOM IHÅG VAD DU GÖR")
    print("=" * 72)
    if not overwrite_content:
        print(" Läge: SÄKERT (default)")
        print("   ✓ Komponenter + CSS pushas")
        print("   ✓ Sidornas innehåll lämnas ORÖRT (kundens redigeringar är säkra)")
        print()
        print(" Vill du faktiskt skriva över sidornas innehåll? Lägg till:")
        print("   --overwrite-content                          → skriv över alla sidor")
        print("   --overwrite-content --keep-pages hem,kontakt → skriv över utom dessa")
    else:
        print(" Läge: ⚠️  OVERWRITE-CONTENT — SKRIVER ÖVER SIDOR")
        print("   ✓ Komponenter + CSS pushas")
        print("   ⚠️ Sidornas innehåll RADERAS och ersätts av bundle:n")
        if keep_pages:
            print(f"   ✓ Undantag (--keep-pages): {', '.join(sorted(keep_pages))}")
        if force:
            print("   ⚠️ --force aktivt → ingen JA-prompt")
        else:
            print("   → JA-prompt visas innan pages skrivs över")
    print("=" * 72)
    print()


def build_all(bundle_path: str, allow_production: bool = False,
              overwrite_content: bool = False, force: bool = False,
              keep_pages: set | None = None, resume: bool = False) -> None:
    check_env_guard(allow_production)
    keep_pages = keep_pages or set()
    print_mode_banner(overwrite_content, keep_pages, force)

    path = Path(bundle_path).resolve()
    if not path.exists():
        print(f"[ERROR] File not found: {bundle_path}")
        sys.exit(1)

    # Deploy state lives in the same dir as the bundle (clients/<name>/.tmp/ or legacy .tmp/)
    state_path = path.parent / "deploy_state.json"
    state = load_deploy_state(state_path) if resume else {}
    if resume and state:
        already_ok = [k for k, v in state.get("components", {}).items() if v.get("status") == "ok"]
        print(f"[RESUME] Found deploy state — {len(already_ok)} component(s) already deployed, skipping.")

    # --- Pre-deploy validation --------------------------------------------
    print("[VALIDATE] Kör bundle-validering...")
    from validate_bundle import validate_bundle
    if not validate_bundle(path, strict=False):
        print("\n[ABORTED] Åtgärda felen ovan innan deploy.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    site_name        = bundle.get("site_name")
    components       = bundle.get("components", [])
    pages            = bundle.get("pages", [])
    platform_config  = bundle.get("platform_config")
    global_settings  = bundle.get("global_settings")
    snippets         = bundle.get("snippets", [])
    extra_menu_items = bundle.get("extra_menu_items", [])

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
        component_state = state.get("components", {})
        for component in components:
            block_name = component.get("block_name", "unknown")
            if resume and component_state.get(block_name, {}).get("status") == "ok":
                print(f"  [SKIP]  {block_name} (already deployed)")
                continue
            ok = push_component(component)
            component_state[block_name] = {
                "status": "ok" if ok else "failed",
                "at": datetime.now().isoformat(timespec="seconds"),
            }
            save_deploy_state(state_path, {"bundle": path.name, "components": component_state})
            if not ok:
                failed.append(block_name)

        if failed:
            print(f"\n[ERROR] {len(failed)} component(s) failed: {failed}")
            print(f"        Deploy state saved to {state_path.relative_to(ROOT)}")
            print(f"        Fix errors and re-run with --resume to skip successful components.")
            sys.exit(1)
    else:
        print(f"\n[{step}/{total_steps}] No components in bundle — skipping component push.")

    # --- Step 2: Build site -----------------------------------------------
    step += 1
    if not overwrite_content:
        print(f"\n[{step}/{total_steps}] Page sync SKIPPED (default). "
              f"Components/CSS pushed; sidornas innehåll är orört.")
        print(f"        Vill du skriva över sidornas innehåll: lägg till --overwrite-content")
    else:
        if keep_pages:
            kept = [p for p in pages if p.get("slug") in keep_pages]
            pages = [p for p in pages if p.get("slug") not in keep_pages]
            if kept:
                print(f"\n[INFO] --keep-pages preserved {len(kept)} page(s) from overwrite: "
                      f"{', '.join(p.get('slug') for p in kept)}")

        slugs = [p.get("slug") for p in pages]
        print(f"\n[WARN] OVERWRITE-CONTENT är aktivt. Följande {len(pages)} sida(or) kommer "
              f"skrivas över på {WP_URL}:")
        for s in slugs:
            print(f"        - /{s}/")
        print(f"        Eventuella ändringar gjorda i WP Admin på dessa sidor förloras.")

        if not force:
            try:
                resp = input("        Skriva 'JA' för att fortsätta (annat avbryter): ").strip()
            except EOFError:
                resp = ""
            if resp != "JA":
                print("[ABORTED] Page sync avbruten. Components/CSS pushas redan.")
                # Continue with CSS step below
                pages = []

        if pages:
            print(f"\n[{step}/{total_steps}] Building site '{site_name}' with {len(pages)} page(s)...")
            build_site(site_name, pages, extra_menu_items=extra_menu_items)

    # --- Step 3: Compile & push CSS from this bundle only -----------------
    print(f"\n[CSS] Compiling Tailwind CSS from {Path(bundle_path).name} ...")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "compile_tailwind.py"), str(path)],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("[WARN] CSS compilation failed — push styles manually with compile_tailwind.py")

    # --- Step 4: Record what was deployed -------------------------------
    bundle_dir = Path(bundle_path).resolve().parent
    deployed_log = bundle_dir / ".deployed.json"
    bridge_version = "unknown"
    try:
        v = requests.get(f"{WP_URL}/wp-json/lumokit/v1/version", timeout=10).json()
        bridge_version = v.get("bridge_version", "unknown")
    except Exception:
        pass

    record = {
        "deployed_at": datetime.now().isoformat(timespec="seconds"),
        "bundle":      str(Path(bundle_path).name),
        "wp_url":      WP_URL,
        "bridge_version": bridge_version,
        "overwrite_content": overwrite_content,
        "site_name":   site_name,
    }
    deployed_log.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    print(f"\n[LOG] Wrote {deployed_log.relative_to(ROOT)}")

    print(f"\n[DONE] {site_name} is live (bridge v{bridge_version}).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/build_all.py <bundle.json> [flags]")
        print()
        print("  Default: pushar BARA komponenter + CSS. Sidornas innehåll lämnas orört.")
        print()
        print("  --overwrite-content    Skriv över sidornas innehåll. Visar varning + frågar JA.")
        print("                         Eventuella WP Admin-redigeringar går förlorade.")
        print("  --keep-pages slug,..   Vid --overwrite-content: behåll dessa sidor orörda.")
        print("  --force                Hoppa över JA-prompten (för automation/CI).
  --resume               Hoppa över komponenter som redan lyckades i föregående körning.")
        print("  --production           Tillåt push mot WP_ENV=production.")
        sys.exit(1)

    args = sys.argv[1:]
    bundle_path = args[0]
    allow_production = "--production" in args
    overwrite_content = "--overwrite-content" in args
    force = "--force" in args
    resume = "--resume" in args
    keep_pages: set = set()
    if "--keep-pages" in args:
        idx = args.index("--keep-pages")
        if idx + 1 < len(args):
            keep_pages = {s.strip() for s in args[idx + 1].split(",") if s.strip()}

    build_all(bundle_path, allow_production=allow_production,
              overwrite_content=overwrite_content, force=force,
              keep_pages=keep_pages, resume=resume)
