"""
sync_block_acf.py
Sync ACF data on existing block instances to match current schema defaults
(or explicit values). Use after pushing a component change so the new
default actually renders on pages that already had the block.

Background:
    Bridge bakes schema defaults into the block's `data` attribute at page-
    creation time (stored in post_content). At render time it reads from
    that baked data — there is NO fallback to schema default at render.
    So updating a schema default does not affect existing pages.
    This tool patches the baked data on existing pages without touching
    block structure or other blocks' data.

Usage:
    # Sync ALL schema-default values for one block on one page
    python tools/sync_block_acf.py --client alvsjotandvard --block lumo/hero --page hem

    # Sync ALL pages that contain the block
    python tools/sync_block_acf.py --client alvsjotandvard --block lumo/hero --all-pages

    # Only sync specific fields (skip everything else)
    python tools/sync_block_acf.py --client alvsjotandvard --block lumo/hero --page hem \\
        --field hero_image --field ingress

    # Dry-run on production first
    python tools/sync_block_acf.py --client alvsjotandvard --block lumo/hero --page hem \\
        --production --dry-run

Requires lumokit-bridge >= 1.1.0 (sync-block-acf endpoint).
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from env_loader import ROOT, load_env

load_env()

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
WP_ENV          = os.getenv("WP_ENV", "development").strip().lower()

ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/sync-block-acf"


def check_env_guard(allow_production: bool) -> None:
    if WP_ENV == "production" and not allow_production:
        print(f"[BLOCKED] WP_ENV is set to 'production' in .env")
        print(f"          Target: {WP_URL}")
        print(f"          Re-run with --production to confirm.")
        sys.exit(2)
    if WP_ENV == "production" and allow_production:
        print(f"[WARN] Targeting PRODUCTION: {WP_URL}")


def load_block_schema_defaults(bundle_path: Path, block_name: str) -> dict:
    """Returns {field_name: default_value} for all schema fields with a default.
    `{{site_url}}` mustache is resolved against WP_URL so Bridge can do attachment lookup.
    Image fields keep their (resolved) URL — Bridge converts to attachment ID server-side."""
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)
    for comp in bundle.get("components", []):
        if comp.get("block_name") == block_name:
            out = {}
            for field in comp.get("schema", []):
                name = field.get("name")
                default = field.get("default")
                if name and default not in (None, ""):
                    if isinstance(default, str) and "{{site_url}}" in default:
                        default = default.replace("{{site_url}}", WP_URL)
                    out[name] = default
            return out
    raise SystemExit(f"[ERROR] Block '{block_name}' not found in bundle: {bundle_path}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--client", required=True, help='Client name, e.g. "alvsjotandvard".')
    p.add_argument("--block", required=True, help='Block name, e.g. "lumo/hero".')

    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--page", action="append", dest="pages",
                        help="Page slug to update (repeatable, e.g. --page hem --page om-oss).")
    target.add_argument("--all-pages", action="store_true",
                        help="Update every page that contains the block.")

    p.add_argument("--field", action="append", dest="fields",
                   help="Limit sync to specific field name(s). Repeat for multiple. Default = all schema defaults.")
    p.add_argument("--production", action="store_true",
                   help="Allow pushing when WP_ENV=production.")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would change without writing.")
    args = p.parse_args()

    check_env_guard(args.production)

    bundle_path = ROOT / "clients" / args.client / "bundle.json"
    if not bundle_path.exists():
        print(f"[ERROR] Bundle not found: {bundle_path}")
        return 1

    defaults = load_block_schema_defaults(bundle_path, args.block)
    if not defaults:
        print(f"[ERROR] No schema defaults found for {args.block}. Nothing to sync.")
        return 1

    if args.fields:
        missing = [f for f in args.fields if f not in defaults]
        if missing:
            print(f"[ERROR] Fields not in schema defaults: {missing}")
            print(f"        Available fields with defaults: {sorted(defaults.keys())}")
            return 1
        fields_to_send = {f: defaults[f] for f in args.fields}
    else:
        fields_to_send = defaults

    payload = {
        "block_name": args.block,
        "fields":     fields_to_send,
        "dry_run":    args.dry_run,
    }
    if args.pages:
        payload["page_slugs"] = args.pages

    print(f"\n[SYNC] {args.block} → {WP_URL}")
    if args.pages:
        print(f"       Pages: {', '.join(args.pages)}")
    else:
        print(f"       Pages: all containing this block")
    print(f"       Fields ({len(fields_to_send)}): {', '.join(fields_to_send.keys())}")
    if args.dry_run:
        print(f"       Mode:  DRY-RUN")
    print()

    try:
        r = requests.post(
            ENDPOINT,
            json=payload,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            timeout=60,
        )
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return 1

    if r.status_code != 200:
        print(f"[ERROR] HTTP {r.status_code}: {r.text[:500]}")
        return 1

    data = r.json()
    updated   = data.get("updated", [])
    skipped   = data.get("skipped", [])
    unresolved = data.get("unresolved", {}) or {}

    if updated:
        print(f"[OK] Updated {len(updated)} page(s):")
        for u in updated:
            mark = " (DRY-RUN)" if u.get("dry_run") else ""
            err  = f"  ERROR: {u['error']}" if u.get("error") else ""
            fields = ", ".join(u.get("fields_updated", []))
            print(f"    - /{u['slug']} (id={u['page_id']}, blocks={u['blocks_updated']}){mark}")
            print(f"        fields: {fields}{err}")
    else:
        print("[INFO] No pages updated.")

    if skipped:
        print(f"\n[SKIP] {len(skipped)} page(s):")
        for s in skipped:
            print(f"    - /{s['slug']}: {s['reason']}")

    if unresolved:
        print(f"\n[WARN] Could not resolve {len(unresolved)} image URL(s) to attachment IDs:")
        for name, url in unresolved.items():
            print(f"    - {name}: {url}")
        print("       Upload the image via tools/upload_media.py first.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
