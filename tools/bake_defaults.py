"""
bake_defaults.py
For each page in a bundle, find ACF block fields that are missing from the
saved post_content data but have a non-empty default in the schema. Bake those
defaults into the page as actual saved values. Fields that already have a saved
value are never touched.

After patching all pages, removes the `default` key from every schema field in
the bundle so the site relies on real saved values going forward.

Usage:
    python3 tools/bake_defaults.py clients/patricia-teles/bundle.json [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import re
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

BLOCK_RE = re.compile(
    r'(<!-- wp:acf/([\w-]+) )(\{.*?\})( /-->)',
    re.DOTALL,
)

SKIP_FIELDS = {"lumo_html_override"}


def fetch_page(slug: str) -> dict | None:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/pages",
        params={"slug": slug, "context": "edit"},
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=15,
    )
    if not r.ok:
        return None
    pages = r.json()
    return pages[0] if pages else None


def update_page(page_id: int, raw_content: str) -> bool:
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/pages/{page_id}",
        json={"content": raw_content},
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=15,
    )
    return r.ok


def resolve_image_id(url: str) -> int | None:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/media",
        params={"search": Path(url).name},
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=15,
    )
    if r.ok:
        for item in r.json():
            if item.get("source_url") == url or item.get("slug") in url:
                return item["id"]
    return None


def build_schema_defaults(schema: list) -> dict[str, tuple[str, str]]:
    """Return {field_name: (default_value, field_type)} for fields with non-empty defaults."""
    result = {}
    for field in schema:
        name = field.get("name", "")
        default = field.get("default", "")
        ftype = field.get("type", "text")
        if name and default:
            result[name] = (default, ftype)
    return result


def patch_block_data(
    block_slug: str,
    attrs: dict,
    defaults: dict[str, tuple[str, str]],
    dry_run: bool,
) -> tuple[dict, list[str]]:
    """
    Add missing fields to attrs['data'] using defaults.
    Returns (updated_attrs, list_of_patched_field_names).
    """
    data = attrs.get("data", {})
    if isinstance(data, list):
        return attrs, []

    slug_prefix = block_slug.replace("-", "_")
    patched = []

    for field_name, (default_val, ftype) in defaults.items():
        if field_name in SKIP_FIELDS:
            continue
        if field_name in data and data[field_name] not in ("", None, False):
            continue  # already has a value — skip

        if ftype == "image":
            # Resolve URL → attachment ID
            attachment_id = resolve_image_id(default_val)
            if not attachment_id:
                print(f"    [SKIP] {field_name}: image not found in media library ({default_val})")
                continue
            value_to_bake = attachment_id
        else:
            value_to_bake = default_val

        field_key = f"field_lumo_{block_slug}_{field_name}"
        data[field_name] = value_to_bake
        data[f"_{field_name}"] = field_key
        patched.append(field_name)

    attrs["data"] = data
    return attrs, patched


def process_page(
    slug: str,
    title: str,
    block_names: list[str],
    schema_map: dict[str, list],
    dry_run: bool,
) -> bool:
    page = fetch_page(slug)
    if not page:
        print(f"  [SKIP] Page not found: {slug}")
        return True

    page_id = page["id"]
    raw = page["content"]["raw"]
    any_patched = False
    total_patched = []

    def replace_block(m: re.Match) -> str:
        nonlocal any_patched
        prefix, block_slug, attrs_str, suffix = m.group(1), m.group(2), m.group(3), m.group(4)
        full_block_name = f"lumo/{block_slug}"

        schema = schema_map.get(full_block_name)
        if not schema:
            return m.group(0)  # not our component — leave alone

        try:
            attrs = json.loads(attrs_str)
        except json.JSONDecodeError:
            return m.group(0)

        defaults = build_schema_defaults(schema)
        if not defaults:
            return m.group(0)

        updated_attrs, patched = patch_block_data(block_slug, attrs, defaults, dry_run)

        if patched:
            any_patched = True
            total_patched.extend([f"{block_slug}.{f}" for f in patched])
            new_attrs_str = json.dumps(updated_attrs, ensure_ascii=False, separators=(",", ":"))
            return f"{prefix}{new_attrs_str}{suffix}"

        return m.group(0)

    new_raw = BLOCK_RE.sub(replace_block, raw)

    if not any_patched:
        print(f"  {slug}: nothing to patch")
        return True

    print(f"  {slug}: patching {len(total_patched)} field(s): {', '.join(total_patched)}")

    if dry_run:
        print(f"    [DRY RUN] would update page id={page_id}")
        return True

    ok = update_page(page_id, new_raw)
    if ok:
        print(f"    [OK] page {page_id} updated")
    else:
        print(f"    [ERROR] failed to update page {page_id}")
    return ok


def strip_defaults_from_bundle(bundle_path: Path) -> None:
    with open(bundle_path, encoding="utf-8") as f:
        bundle = json.load(f)

    stripped = 0
    for comp in bundle.get("components", []):
        for field in comp.get("schema", []):
            if "default" in field:
                del field["default"]
                stripped += 1

    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Removed 'default' from {stripped} schema field(s) in {bundle_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bake schema defaults into WP page content.")
    parser.add_argument("bundle", help="Path to bundle.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    if WP_ENV == "production":
        print("[BLOCKED] WP_ENV=production. Re-run with WP_ENV=staging or development.")
        sys.exit(1)

    bundle_path = Path(args.bundle)
    if not bundle_path.exists():
        print(f"[ERROR] Bundle not found: {bundle_path}")
        sys.exit(1)

    with open(bundle_path, encoding="utf-8") as f:
        bundle = json.load(f)

    # Build schema lookup: block_name → schema list
    schema_map: dict[str, list] = {
        comp["block_name"]: comp.get("schema", [])
        for comp in bundle.get("components", [])
    }

    print(f"Target: {WP_URL}")
    print(f"Bundle: {bundle_path}\n")

    all_ok = True
    for page in bundle.get("pages", []):
        slug = page["slug"]
        title = page.get("title", slug)
        blocks = page.get("blocks", [])
        print(f"Page: {title} ({slug})")
        ok = process_page(slug, title, blocks, schema_map, args.dry_run)
        all_ok = all_ok and ok

    if not all_ok:
        print("\n[WARN] Some pages failed. Fix errors before stripping defaults.")
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Defaults would be stripped from bundle.json after a real run.")
        return

    strip_defaults_from_bundle(bundle_path)
    print("Done.")


if __name__ == "__main__":
    main()
