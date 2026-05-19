"""
push_preview_pages.py
Publicerar mockup-HTML-filer som temporära WordPress-pages via REST API.

Mockupen wrappas i en iframe srcdoc så den är helt isolerad från WP-temat —
ingen risk för CSS-konflikter med klientens tema. Lägger inte upp i menyn.

Användning:
    python tools/push_preview_pages.py
    python tools/push_preview_pages.py --delete         # tar bort tidigare skapade preview-pages

Skapade page-IDs sparas i clients/alvsjotandvard/.tmp/preview_pages.json
så vi kan rensa upp efteråt utan att gissa.
"""

import argparse
import html
import json
import sys
from base64 import b64encode
from pathlib import Path

import os

import requests
from dotenv import load_dotenv

CLIENT_ENV = Path(__file__).resolve().parents[1] / "clients" / "alvsjotandvard" / ".env"
load_dotenv(CLIENT_ENV)

WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

if not (WP_URL and WP_USERNAME and WP_APP_PASSWORD):
    sys.exit("[ERROR] WP_URL, WP_USERNAME och WP_APP_PASSWORD måste finnas i .env")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLIENT_DIR = PROJECT_ROOT / "clients" / "alvsjotandvard"
TMP_DIR = CLIENT_DIR / ".tmp"
DESIGN_CSS = CLIENT_DIR / "design-system" / "alvsjotandvard_ds" / "styles.css"
TRACKER = TMP_DIR / "preview_pages.json"

MOCKUPS = [
    {
        "slug": "preview-stepper",
        "title": "Preview — Behandlingsplan-stepper (Implantat)",
        "file": "treatment-stepper-mockup.html",
    },
    {
        "slug": "preview-trygghet",
        "title": "Preview — Trygghetsmatchning (Tandvårdsrädsla)",
        "file": "fear-matcher-mockup.html",
    },
    {
        "slug": "preview-priser",
        "title": "Preview — Kostnadskalkylator",
        "file": "cost-calculator-mockup.html",
    },
]

AUTH_HEADER = {
    "Authorization": "Basic " + b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode(),
    "Content-Type": "application/json",
}

PAGES_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/pages"


def inline_css(html_str: str) -> str:
    """Byt <link rel='stylesheet' href='../design-system/...'> mot <style>...</style>."""
    css = DESIGN_CSS.read_text(encoding="utf-8")
    needle = '<link rel="stylesheet" href="../design-system/alvsjotandvard_ds/styles.css" />'
    return html_str.replace(needle, f"<style>\n{css}\n</style>")


def build_iframe_wrapper(srcdoc: str, label: str) -> str:
    """Wrap'a hela HTML-dokumentet i en iframe srcdoc med auto-resize."""
    escaped = html.escape(srcdoc, quote=True)
    return f"""<div style="margin:0; padding:0;">
<p style="font-family:system-ui,sans-serif; font-size:13px; color:#666; margin:0 0 12px 0;">
  <strong>{label}</strong> — preview-mockup. Klicka, scrolla och testa interaktiviteten.
</p>
<iframe id="lk-preview-frame" srcdoc="{escaped}"
  style="width:100%; min-height:90vh; border:1px solid #ddd; border-radius:4px; background:#fff; display:block;"
  onload="(function(f){{
    try {{
      var b = f.contentDocument.body;
      var h = f.contentDocument.documentElement;
      var hh = Math.max(b.scrollHeight, h.scrollHeight, b.offsetHeight, h.offsetHeight);
      f.style.height = (hh + 40) + 'px';
    }} catch (e) {{ console.log('resize fail', e); }}
  }})(this)">
</iframe>
</div>"""


def build_page_content(mockup: dict) -> str:
    src_path = TMP_DIR / mockup["file"]
    raw = src_path.read_text(encoding="utf-8")
    inlined = inline_css(raw)
    return build_iframe_wrapper(inlined, mockup["title"])


def load_tracker() -> list:
    if not TRACKER.exists():
        return []
    try:
        return json.loads(TRACKER.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_tracker(data: list) -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    TRACKER.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def delete_existing() -> None:
    existing = load_tracker()
    if not existing:
        print("[INFO] Inga sparade preview-pages att radera.")
        return
    for page in existing:
        url = f"{PAGES_ENDPOINT}/{page['id']}?force=true"
        r = requests.delete(url, headers=AUTH_HEADER, timeout=30)
        if r.status_code in (200, 410):
            print(f"[OK]    Raderad page #{page['id']} ({page['slug']})")
        else:
            print(f"[WARN]  Kunde inte radera #{page['id']}: HTTP {r.status_code} {r.text[:120]}")
    save_tracker([])


def create_or_update(mockup: dict, existing_id: int | None) -> dict:
    content = build_page_content(mockup)
    payload = {
        "title": mockup["title"],
        "slug": mockup["slug"],
        "status": "publish",
        "content": content,
        "comment_status": "closed",
        "ping_status": "closed",
    }

    if existing_id:
        r = requests.post(
            f"{PAGES_ENDPOINT}/{existing_id}",
            json=payload, headers=AUTH_HEADER, timeout=60,
        )
        action = "Uppdaterad"
    else:
        r = requests.post(PAGES_ENDPOINT, json=payload, headers=AUTH_HEADER, timeout=60)
        action = "Skapad"

    if r.status_code not in (200, 201):
        print(f"[ERROR] {mockup['slug']}: HTTP {r.status_code}")
        print(r.text[:500])
        sys.exit(1)

    data = r.json()
    print(f"[OK]    {action} #{data['id']} ({mockup['slug']}) → {data['link']}")
    return {
        "id": data["id"],
        "slug": mockup["slug"],
        "title": mockup["title"],
        "link": data["link"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delete", action="store_true", help="Radera tidigare skapade preview-pages")
    args = ap.parse_args()

    if args.delete:
        delete_existing()
        return

    existing = {p["slug"]: p["id"] for p in load_tracker()}
    results = []
    for m in MOCKUPS:
        results.append(create_or_update(m, existing.get(m["slug"])))

    save_tracker(results)

    print("\n=== Klart — öppna i mobilen ===")
    for r in results:
        print(f"  • {r['title']}")
        print(f"    {r['link']}")
    print(f"\nFör att radera: python tools/push_preview_pages.py --delete")


if __name__ == "__main__":
    main()
