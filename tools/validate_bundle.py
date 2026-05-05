"""
validate_bundle.py
Validates a LumoKit bundle before deploy. Separates hard errors (logic) from
soft warnings (visual/contrast) so that design intent is never overridden by
the tool.

Hard errors  — block deploy, must be fixed:
  - Mustache {{var}} in html_template with no matching schema field
  - Schema field with no matching {{var}} in html_template
  - Forbidden tags: <script>, <iframe>
  - Missing required keys: block_name, title, html_template, schema

Warnings — printed but do not block deploy:
  - Suspected low-contrast class combinations (light text on light bg,
    dark text on dark bg). The human or AI makes the final call.

Usage:
    python tools/validate_bundle.py clients/<client>/bundle.json
    python tools/validate_bundle.py clients/<client>/bundle.json --strict  # warnings become errors
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Contrast heuristics — Tailwind class sets by brightness
# ---------------------------------------------------------------------------

LIGHT_TEXT = {
    "text-white", "text-black/5", "text-black/10",
    *[f"text-{c}-{n}" for c in ("gray", "slate", "zinc", "neutral", "stone") for n in (50, 100, 200)],
}
DARK_TEXT = {
    *[f"text-{c}-{n}" for c in ("gray", "slate", "zinc", "neutral", "stone") for n in (700, 800, 900, 950)],
    "text-black",
}
LIGHT_BG = {
    "bg-white",
    *[f"bg-{c}-{n}" for c in ("gray", "slate", "zinc", "neutral", "stone") for n in (50, 100, 200)],
}
DARK_BG = {
    *[f"bg-{c}-{n}" for c in ("gray", "slate", "zinc", "neutral", "stone") for n in (700, 800, 900, 950)],
    "bg-black",
}

FORBIDDEN_TAGS = re.compile(r"<(script|iframe)[\s>]", re.IGNORECASE)
MUSTACHE_VAR  = re.compile(r"\{\{(\w+)\}\}")
CLASS_ATTR    = re.compile(r'class="([^"]*)"')


def extract_mustache_vars(html: str) -> set[str]:
    return set(MUSTACHE_VAR.findall(html))


def extract_schema_names(schema: list) -> set[str]:
    return {field["name"] for field in schema if "name" in field}


def check_contrast(html: str) -> list[str]:
    """Return list of warning strings for suspected low-contrast class combos."""
    warnings = []
    for m in CLASS_ATTR.finditer(html):
        classes = set(m.group(1).split())
        has_light_text = classes & LIGHT_TEXT
        has_dark_text  = classes & DARK_TEXT
        has_light_bg   = classes & LIGHT_BG
        has_dark_bg    = classes & DARK_BG

        if has_light_text and has_light_bg:
            warnings.append(
                f"  [WARN] Möjlig låg kontrast: ljus text ({', '.join(has_light_text)}) "
                f"på ljus bakgrund ({', '.join(has_light_bg)})"
            )
        if has_dark_text and has_dark_bg:
            warnings.append(
                f"  [WARN] Möjlig låg kontrast: mörk text ({', '.join(has_dark_text)}) "
                f"på mörk bakgrund ({', '.join(has_dark_bg)})"
            )
    return warnings


def validate_component(component: dict) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings) for a single component."""
    errors   = []
    warnings = []

    block_name = component.get("block_name", "<okänt>")

    # Required fields
    for key in ("block_name", "title", "html_template", "schema"):
        if key not in component:
            errors.append(f"  [ERROR] Saknar required fält: '{key}'")

    html   = component.get("html_template", "")
    schema = component.get("schema", [])

    # Forbidden tags — warn only, since some components intentionally use <script> (forms) or <iframe> (maps)
    if FORBIDDEN_TAGS.search(html):
        warnings.append(f"  [WARN] <script> eller <iframe> i html_template — verifiera att det är avsiktligt")

    # Mustache / schema alignment
    # Global Bridge variables — resolved at render time, never part of component schema.
    GLOBAL_VARS = {
        "site_phone", "site_email", "site_address", "site_company_name",
        "site_reviews_score", "site_reviews_testimonials", "site_booking_api_key",
        "site_booking_cta_link", "site_booking_widget_id", "site_trustindex_script",
        "site_opening_hours", "lumokit-primary",
    }
    template_vars  = extract_mustache_vars(html) - GLOBAL_VARS
    schema_names   = extract_schema_names(schema)

    orphan_vars    = template_vars - schema_names
    orphan_fields  = schema_names - template_vars

    for var in sorted(orphan_vars):
        errors.append(f"  [ERROR] {{{{'{var}'}}}} finns i html_template men saknas i schema")

    for field in sorted(orphan_fields):
        warnings.append(f"  [WARN] Schema-fält '{field}' saknar matchande {{{{'{field}'}}}} i html_template")

    # Contrast warnings
    warnings.extend(check_contrast(html))

    return errors, warnings


def validate_bundle(bundle_path: Path, strict: bool = False) -> bool:
    """Validate all components in a bundle. Returns True if deploy can proceed."""
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    components = bundle.get("components", [])
    if not components:
        print("[WARN] Bundle har inga komponenter.")
        return True

    total_errors   = 0
    total_warnings = 0

    print(f"\n[VALIDATE] {bundle_path.name} — {len(components)} komponent(er)\n")

    for component in components:
        block_name = component.get("block_name", "<okänt>")
        errors, warnings = validate_component(component)

        if errors or warnings:
            print(f"  {block_name}")
            for e in errors:
                print(e)
            for w in warnings:
                print(w)
            print()

        total_errors   += len(errors)
        total_warnings += len(warnings)

    # Summary
    print("-" * 60)
    if total_errors == 0 and total_warnings == 0:
        print(f"[OK] Inga fel. Bundlen är redo för deploy.")
        return True

    if total_errors > 0:
        print(f"[FAIL] {total_errors} fel måste åtgärdas före deploy.")
    if total_warnings > 0:
        adj = "blockerar deploy" if strict else "blockerar ej deploy"
        print(f"[WARN] {total_warnings} kontrast-varning(ar) — {adj}.")
        if not strict:
            print("       Granska manuellt. Designbeslut fattas av människa/AI.")

    if strict and total_warnings > 0:
        return False

    return total_errors == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/validate_bundle.py <bundle.json> [--strict]")
        sys.exit(1)

    path   = Path(sys.argv[1])
    strict = "--strict" in sys.argv

    if not path.exists():
        print(f"[ERROR] Filen hittades inte: {path}")
        sys.exit(1)

    ok = validate_bundle(path, strict=strict)
    sys.exit(0 if ok else 1)
