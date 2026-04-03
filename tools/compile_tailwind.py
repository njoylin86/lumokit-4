"""
compile_tailwind.py
Compiles Tailwind CSS from all local component payloads and pushes the
resulting stylesheet to WordPress via the LumoKit REST API.

Usage:
    python tools/compile_tailwind.py

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


def extract_templates() -> str:
    """Read all .tmp/*.json payloads and concatenate their html_templates."""
    payload_files = list(TMP_DIR.glob("*.json"))

    if not payload_files:
        print("[ERROR] No JSON payload files found in .tmp/")
        sys.exit(1)

    html_parts = []
    for path in payload_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "html_template" in data:
                html_parts.append(data["html_template"])
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
    html = extract_templates()
    css  = compile_css(html)
    push_css(css)
