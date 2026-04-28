"""
compile_tailwind.py
Compiles Tailwind CSS from a specific bundle (or all .tmp/*.json as fallback)
and pushes the resulting stylesheet to WordPress via the LumoKit REST API.

Usage:
    python tools/compile_tailwind.py .tmp/myclient_bundle.json   ← recommended
    python tools/compile_tailwind.py                              ← scans all .tmp/*.json

Requirements:
    - Node.js + npx must be installed
    - tailwindcss must be available: npm install -D tailwindcss (run once in tools/)
    - .env must contain WP_URL, WP_USERNAME, WP_APP_PASSWORD
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
TMP_DIR = ROOT / ".tmp"

load_dotenv(ROOT / ".env")

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

STYLES_ENDPOINT = f"{WP_URL}/wp-json/lumokit/v1/styles"


def extract_templates(bundle_path: Path | None = None) -> str:
    """Extract html_templates from a specific bundle file, or all .tmp/*.json as fallback.

    Always pass a specific bundle_path to avoid cross-client CSS contamination.
    """
    if bundle_path:
        payload_files = [bundle_path]
        print(f"[INFO] Compiling CSS from: {bundle_path.name}")
    else:
        payload_files = list(TMP_DIR.glob("*.json"))
        if not payload_files:
            print("[ERROR] No JSON payload files found in .tmp/")
            sys.exit(1)
        print(f"[WARN] No bundle specified — scanning all {len(payload_files)} file(s) in .tmp/")
        print(f"       Pass a specific bundle to avoid CSS from unrelated clients.")

    html_parts = []
    for path in payload_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Single-component format
            if "html_template" in data:
                html_parts.append(data["html_template"])
            # Bundle format — extract from nested components array
            elif "components" in data:
                for component in data["components"]:
                    if "html_template" in component:
                        html_parts.append(component["html_template"])
        except Exception as e:
            print(f"[WARN]  Skipping {path.name}: {e}")

    print(f"[INFO] Extracted templates from {len(html_parts)} component(s).")
    return "\n".join(html_parts)


def compile_css(html: str) -> str:
    """Write templates to a temp file and run Tailwind JIT compilation."""
    templates_file = TMP_DIR / "templates.html"
    output_file    = TMP_DIR / "lumokit.css"

    with open(templates_file, "w", encoding="utf-8") as f:
        f.write(html)

    print("[INFO] Running Tailwind compiler...")

    result = subprocess.run(
        [
            "npx", "tailwindcss",
            "--config", str(TOOLS_DIR / "tailwind.config.js"),
            "-i",       str(TOOLS_DIR / "tailwind.input.css"),
            "-o",       str(output_file),
            "--minify",
        ],
        capture_output=True,
        text=True,
        cwd=str(TOOLS_DIR),
    )

    if result.returncode != 0:
        print("[ERROR] Tailwind compilation failed:")
        print(result.stderr)
        sys.exit(1)

    with open(output_file, "r", encoding="utf-8") as f:
        css = f.read()

    # Prepend Google Fonts + Material Symbols imports so fonts load on all LumoKit pages.
    # CSS @import must appear before any other rules.
    font_imports = (
        "@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800"
        "&family=Inter:wght@300;400;500;600&display=swap');\n"
        "@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:"
        "opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');\n"
        ".material-symbols-outlined{"
        "font-family:'Material Symbols Outlined';font-weight:normal;font-style:normal;"
        "font-size:1em;line-height:1;letter-spacing:normal;text-transform:none;"
        "display:inline-block;white-space:nowrap;word-wrap:normal;direction:ltr;"
        "font-variation-settings:'FILL' 0,'wght' 300,'GRAD' 0,'opsz' 24;"
        "vertical-align:middle;}\n"
    )
    css = font_imports + css

    print(f"[INFO] Compiled CSS: {len(css):,} bytes.")
    return css


def push_css(css: str) -> None:
    """Push compiled CSS to WordPress via the LumoKit REST API."""
    print(f"[INFO] Pushing stylesheet to {STYLES_ENDPOINT} ...")

    response = requests.post(
        STYLES_ENDPOINT,
        json={"css": css},
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK]   {data.get('message')}")
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    bundle_path = None
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        p = Path(args[0])
        if not p.exists():
            print(f"[ERROR] Bundle not found: {p}")
            sys.exit(1)
        bundle_path = p

    html = extract_templates(bundle_path)
    css  = compile_css(html)
    push_css(css)
