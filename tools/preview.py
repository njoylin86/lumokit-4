"""
preview.py
Local preview server for LumoKit component bundles.

Reads a bundle JSON (or single component JSON), extracts all html_template
strings, replaces {{mustache}} variables with readable placeholders, wraps
everything in a full HTML page with Tailwind CDN + Google Fonts, and serves
at http://localhost:3000.

Usage:
    python tools/preview.py .tmp/lumoDental_bundle.json
    python tools/preview.py .tmp/hero_payload.json          # single component
    python tools/preview.py .tmp/lumoDental_bundle.json --port 8080
"""

import http.server
import json
import re
import sys
import webbrowser
from pathlib import Path

PORT = 3000

HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LumoKit Preview — {title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
  <style>
    body {{ margin: 0; font-family: 'Inter', sans-serif; }}
    h1, h2, h3, h4, h5, h6 {{ font-family: 'Space Grotesk', sans-serif; }}
    nav ul {{ list-style: none !important; margin: 0 !important; padding: 0 !important; }}
    nav li {{ display: inline-block !important; position: relative; margin: 0 10px !important; }}
    nav li:first-child {{ margin-left: 0 !important; }}
    nav li:last-child {{ margin-right: 0 !important; }}
    nav a {{ text-decoration: none; color: inherit !important; }}
    nav .sub-menu {{
      display: none !important; position: absolute; top: 100%; left: 0;
      min-width: 180px; padding: 8px 0; z-index: 1000; background: #fff;
      border: 1px solid rgba(0,0,0,0.08); border-radius: 4px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }}
    nav li:hover > .sub-menu {{ display: block !important; }}
    nav .sub-menu li {{ display: block !important; width: 100%; margin: 0 !important; }}
    nav .sub-menu a {{ display: block; padding: 10px 18px; }}
    /* Preview badge */
    #lumokit-preview-badge {{
      position: fixed; bottom: 16px; right: 16px; z-index: 9999;
      background: #1a1a1a; color: #fff; font-family: monospace;
      font-size: 11px; padding: 6px 12px; border-radius: 20px;
      opacity: 0.7; pointer-events: none;
    }}
  </style>
</head>
<body>
{body}
<div id="lumokit-preview-badge">⚡ LumoKit Preview</div>
</body>
</html>
"""

DUMMY_VALUES = {
    "image":    "https://placehold.co/1200x800/E8E3DB/888",
    "url":      "#",
    "textarea": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "text":     "Placeholder text",
    "number":   "42",
    "nav_menu": "",
}

DUMMY_TEXT_BY_NAME = {
    "headline":      "Din starka rubrik här",
    "title":         "Titel",
    "subheadline":   "En kort och träffsäker underrubrik som fångar besökarens uppmärksamhet.",
    "subtitle":      "Underrubrik",
    "description":   "En beskrivande text som förklarar erbjudandet tydligt och engagerande.",
    "body":          "Brödtext — lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "cta_text":      "Kom igång",
    "button_text":   "Läs mer",
    "cta_link":      "#",
    "link":          "#",
    "name":          "Förnamn Efternamn",
    "company":       "Företagsnamnet AB",
    "phone":         "08-123 456 78",
    "email":         "info@example.se",
    "address":       "Exempelgatan 12, 123 45 Stockholm",
    "opening_hours": "Mån–Fre 08–17",
    "label":         "Etikett",
    "tag":           "Kategori",
    "caption":       "Bildtext",
    "quote":         "Ett inspirerande citat som lyfter fram kärnbudskapet.",
    "author":        "Anna Svensson",
    "role":          "VD & Grundare",
    "stat":          "2 400+",
    "stat_label":    "Nöjda kunder",
    "number":        "15",
    "unit":          "år",
}


def replace_mustache(html: str, schema: list) -> str:
    """Replace {{variable}} placeholders with sensible dummy content."""
    # Build field-type map from schema
    field_types = {f["name"]: f.get("type", "text") for f in schema}

    def replacer(match):
        var = match.group(1).strip()
        # Check by name first
        for key, val in DUMMY_TEXT_BY_NAME.items():
            if key in var.lower():
                return val
        # Fall back to type-based dummy
        field_type = field_types.get(var, "text")
        return DUMMY_VALUES.get(field_type, f"[{var}]")

    return re.sub(r"\{\{([^}]+)\}\}", replacer, html)


def extract_blocks(payload: dict) -> list[tuple[str, str, list]]:
    """
    Returns list of (block_name, html_template, schema) tuples.
    Handles both single-component and bundle JSON formats.
    Excludes injected header/footer — they are rendered separately.
    """
    injected = {"lumo/site-header", "lumo/site-footer"}
    blocks = []
    header_html = ""
    footer_html = ""

    if "components" in payload:
        # Bundle format
        components = {c["block_name"]: c for c in payload.get("components", [])}

        # Grab header/footer first
        for name in ["lumo/site-header", "lumo/site-footer"]:
            if name in components:
                c = components[name]
                html = replace_mustache(c.get("html_template", ""), c.get("schema", []))
                if name == "lumo/site-header":
                    header_html = html
                else:
                    footer_html = html

        # Page blocks in order (first page)
        pages = payload.get("pages", [])
        if pages:
            page_blocks = pages[0].get("blocks", [])
            for block_name in page_blocks:
                if block_name in injected:
                    continue
                if block_name in components:
                    c = components[block_name]
                    blocks.append((
                        block_name,
                        replace_mustache(c.get("html_template", ""), c.get("schema", [])),
                        c.get("schema", [])
                    ))
        else:
            # No pages — render all non-injected components
            for c in payload.get("components", []):
                if c["block_name"] in injected:
                    continue
                blocks.append((
                    c["block_name"],
                    replace_mustache(c.get("html_template", ""), c.get("schema", [])),
                    c.get("schema", [])
                ))
    else:
        # Single component format
        blocks.append((
            payload.get("block_name", "component"),
            replace_mustache(payload.get("html_template", ""), payload.get("schema", [])),
            payload.get("schema", [])
        ))

    return header_html, footer_html, blocks


def build_page(payload: dict, source_name: str) -> str:
    header_html, footer_html, blocks = extract_blocks(payload)
    body = header_html + "\n".join(html for _, html, _ in blocks) + footer_html
    title = payload.get("site_name") or payload.get("title") or source_name
    return HTML_WRAPPER.format(title=title, body=body)


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("Usage: python tools/preview.py <bundle.json> [--port 3000]")
        sys.exit(1)

    payload_path = Path(args[0])
    if not payload_path.exists():
        print(f"[ERROR] File not found: {payload_path}")
        sys.exit(1)

    global PORT
    if "--port" in args:
        idx = args.index("--port")
        PORT = int(args[idx + 1])

    with open(payload_path, encoding="utf-8") as f:
        payload = json.load(f)

    page_html = build_page(payload, payload_path.stem)

    # Serve from a temp dir
    import tempfile, os, threading

    tmpdir = tempfile.mkdtemp()
    index_path = os.path.join(tmpdir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(page_html)

    os.chdir(tmpdir)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # suppress request logs

    server = http.server.HTTPServer(("", PORT), QuietHandler)
    print(f"[INFO] Preview server running at http://localhost:{PORT}")
    print(f"       Serving: {payload_path.name}")
    print(f"       Press Ctrl+C to stop.")

    threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped.")


if __name__ == "__main__":
    main()
