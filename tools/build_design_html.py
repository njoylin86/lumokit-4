"""
build_design_html.py
Generates standalone HTML page mockups for review BEFORE component decomposition.
Inputs:
  .tmp/content/text/lumo-content.json   — content per page
  .tmp/content/_media_manifest.json     — image filename -> WP url
  .tmp/Design system/colors_and_type.css — design tokens (inlined into <style>)

Outputs to .tmp/:
  hem_design.html
  om-oss_design.html
  kontakt_design.html
  tandimplantat_design.html  (representative treatment page)

Usage:
  python3 tools/build_design_html.py

These are static review artifacts. After approval we decompose them into LumoKit components.
"""

import json
import re
from pathlib import Path
from urllib.parse import quote_plus


def tel_link(number: str, label: str | None = None,
             cls: str = "", style: str = "") -> str:
    """<a href="tel:..."> — strips spaces/dashes from href, keeps human-readable label."""
    if not number:
        return ""
    href = "tel:" + re.sub(r"[^\d+]", "", number)
    cls_attr   = f' class="{cls}"' if cls else ""
    style_attr = f' style="{style}"' if style else ""
    return f'<a href="{href}"{cls_attr}{style_attr}>{label or number}</a>'


def email_link(email: str, label: str | None = None,
               cls: str = "", style: str = "") -> str:
    if not email:
        return ""
    cls_attr   = f' class="{cls}"' if cls else ""
    style_attr = f' style="{style}"' if style else ""
    return f'<a href="mailto:{email}"{cls_attr}{style_attr}>{label or email}</a>'


def address_link(address: str, label: str | None = None,
                 cls: str = "", style: str = "") -> str:
    if not address:
        return ""
    href = f"https://maps.google.com/?q={quote_plus(address)}"
    cls_attr   = f' class="{cls}"' if cls else ""
    style_attr = f' style="{style}"' if style else ""
    return f'<a href="{href}" target="_blank" rel="noopener"{cls_attr}{style_attr}>{label or address}</a>'

ROOT = Path(__file__).resolve().parent.parent


def _resolve_tmp(client: str | None) -> Path:
    if client:
        return ROOT / "clients" / client / ".tmp"
    return ROOT / ".tmp"

REPRESENTATIVE_TREATMENT_SLUG = "tandimplantat"

# Generic page-name-as-H1 ("Hem", "Om oss", "Kontakt") makes weak hero copy.
# These overrides give a proper brand-led headline for the mockup; the client
# can override per page via lumo-content.json once content is finalised.
HERO_H1_OVERRIDE = {
    "hem":     "Modern tandvård i centrala Stockholm",
    "om-oss":  "Människorna bakom Patricia Teles",
    "kontakt": "Kom i kontakt med oss",
}
HERO_EYEBROW = {
    "hem":     "Patricia Teles · Stockholm",
    "om-oss":  "Om oss",
    "kontakt": "Kontakt",
}


def load(tmp: Path) -> tuple[dict, dict, str, str, str]:
    content   = json.loads((tmp / "content" / "text" / "lumo-content.json").read_text(encoding="utf-8"))
    manifest  = json.loads((tmp / "content" / "_media_manifest.json").read_text(encoding="utf-8"))
    tokens    = (tmp / "Design system" / "colors_and_type.css").read_text(encoding="utf-8")
    logo_full_path = tmp / "Design system" / "assets" / "logo.svg"
    logo_mark_path = tmp / "Design system" / "assets" / "logo-mark.svg"
    logo_full = logo_full_path.read_text(encoding="utf-8") if logo_full_path.exists() else ""
    logo_mark = logo_mark_path.read_text(encoding="utf-8") if logo_mark_path.exists() else ""
    return content, manifest, tokens, logo_full, logo_mark


def img_url(manifest: dict, image_id: str | None) -> str:
    if not image_id:
        return ""
    if image_id in manifest:
        return manifest[image_id]["source_url"]
    base = image_id.replace(".jpg", "")
    for alt in (f"{base}-bg.jpg", f"{base}.jpg", f"{base}-image-1.jpg"):
        if alt in manifest:
            return manifest[alt]["source_url"]
    return ""


def page_shell(title: str, body: str, tokens: str, settings: dict,
               logo_full: str = "", logo_mark: str = "",
               treatments: list | None = None) -> str:
    company = settings.get("company_name", "Patricia Teles")
    address = settings.get("company_address", "")
    phone   = settings.get("company_phone", "")
    email   = settings.get("company_email", "")
    header_logo = logo_full or company
    footer_logo = logo_full or company

    treatments_html = ""
    if treatments:
        items = "".join(
            f'<li><a href="{t["slug"]}_design.html">{t["title"]}</a></li>'
            for t in treatments
        )
        treatments_html = f"<ul>{items}</ul>"

    contact_rows = []
    if phone:
        contact_rows.append(
            f'<div class="row"><span class="label">Telefon</span>{tel_link(phone)}</div>'
        )
    if email:
        contact_rows.append(
            f'<div class="row"><span class="label">E-post</span>{email_link(email)}</div>'
        )
    if address:
        contact_rows.append(
            f'<div class="row"><span class="label">Besöksadress</span>{address_link(address)}</div>'
        )
    contact_html = "".join(contact_rows)

    from datetime import date
    year = date.today().year
    return f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{title} — {company}</title>
<style>
{tokens}

/* Layout helpers used across the page mockups */
.page {{ background: var(--bg); color: var(--fg); }}
.container {{ max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px; }}
.eyebrow {{
  font-family: var(--font-sans); font-size: var(--fs-eyebrow); font-weight: 500;
  text-transform: uppercase; letter-spacing: var(--tracking-eyebrow);
  color: var(--fg-accent); margin-bottom: 16px; display: inline-block;
}}
/* Primary CTA — uses the brand's accent rose so the booking action carries
   a single recognisable color across hero, header, content blocks, etc.
   Slight shadow gives a subtle lift so this button always reads as the
   most actionable element on the page, regardless of context. */
.btn-primary {{
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: #fff; background: var(--blush-500); border: none;
  padding: 15px 30px; border-radius: var(--radius-sm); cursor: pointer;
  text-decoration: none; display: inline-block; white-space: nowrap;
  box-shadow: 0 8px 22px rgba(212, 136, 158, 0.30), 0 2px 4px rgba(212,136,158,0.15);
  transition: background var(--dur-fast) var(--ease-standard),
              box-shadow var(--dur-fast) var(--ease-standard),
              transform var(--dur-fast) var(--ease-standard);
}}
.btn-primary:hover {{
  background: var(--blush-600); color: #fff; text-decoration: none;
  box-shadow: 0 10px 28px rgba(181, 106, 130, 0.40), 0 2px 6px rgba(181,106,130,0.20);
  transform: translateY(-1px);
}}
.btn-ghost {{
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--ink-700); background: transparent; border: 1px solid var(--ink-700);
  padding: 13px 28px; border-radius: var(--radius-sm); cursor: pointer;
  text-decoration: none; display: inline-block;
}}
.btn-ghost:hover {{ background: var(--blush-50); color: var(--ink-700); text-decoration: none; }}
.btn-row {{ display: flex; flex-wrap: wrap; gap: 12px; }}

/* Header */
.site-header {{
  position: sticky; top: 0; z-index: 50; background: #fff;
  border-bottom: 1px solid var(--border);
}}
.site-header .inner {{
  position: relative;
  max-width: 1280px; margin: 0 auto; padding: 18px 32px;
  display: flex; justify-content: space-between; align-items: center;
}}
.site-header .logo {{
  display: inline-flex; align-items: center; text-decoration: none;
  color: var(--ink-700);
}}
.site-header .logo svg {{ height: 60px; width: auto; display: block; }}
.site-header nav {{ display: flex; align-items: center; gap: 28px; }}
.site-header nav a {{
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--ink-700); text-decoration: none;
}}
.site-header nav a:hover {{ color: var(--blush-600); }}
/* CTA in nav must keep white text — override the nav-link color rule. */
.site-header nav a.btn-primary {{ color: #fff; }}
.site-header nav a.btn-primary:hover {{ color: #fff; }}

/* Hamburger — pure-CSS checkbox toggle. Hidden on desktop (>900px). */
.site-header .nav-toggle {{ display: none; }}
.site-header .hamburger {{
  display: none; width: 44px; height: 44px; cursor: pointer;
  align-items: center; justify-content: center; flex-direction: column;
  gap: 5px; border-radius: 8px; transition: background var(--dur-fast) var(--ease-standard);
}}
.site-header .hamburger:hover {{ background: var(--blush-50); }}
.site-header .hamburger span {{
  display: block; width: 24px; height: 2px; background: var(--ink-700);
  border-radius: 2px; transition: transform var(--dur-fast) var(--ease-standard),
    opacity var(--dur-fast) var(--ease-standard);
}}
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(1) {{
  transform: translateY(7px) rotate(45deg);
}}
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(2) {{ opacity: 0; }}
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(3) {{
  transform: translateY(-7px) rotate(-45deg);
}}

/* Footer — multi-column with sitemap, treatments, and contact info. */
.site-footer {{
  background: #fff; border-top: 1px solid var(--border);
  padding: 72px 0 32px;
}}
.site-footer .columns {{
  max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px;
  display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.2fr; gap: 56px;
  align-items: start;
}}
.site-footer .brand .logo {{ opacity: 0.85; display: inline-block; }}
.site-footer .brand .logo svg {{ height: 56px; width: auto; display: block; }}
.site-footer .brand .tagline {{
  font-family: var(--font-serif); font-size: 17px; font-style: italic;
  color: var(--fg-muted); margin: 18px 0 0; line-height: 1.45; max-width: 30ch;
}}
.site-footer h4 {{
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--blush-600); margin: 0 0 18px;
}}
.site-footer ul {{
  list-style: none; padding: 0; margin: 0;
  display: flex; flex-direction: column; gap: 10px;
}}
.site-footer ul a {{
  font-family: var(--font-sans); font-size: 14px;
  color: var(--ink-600); text-decoration: none;
  transition: color var(--dur-fast) var(--ease-standard);
}}
.site-footer ul a:hover {{ color: var(--blush-600); }}
.site-footer .contact a {{
  font-family: var(--font-sans); font-size: 14px;
  color: var(--ink-600); text-decoration: none; line-height: 1.5;
}}
.site-footer .contact a:hover {{ color: var(--blush-600); }}
.site-footer .contact .row {{ margin-bottom: 12px; }}
.site-footer .contact .row .label {{
  display: block; font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.18em; color: var(--fg-muted); margin-bottom: 4px;
}}
.site-footer .legal {{
  max-width: var(--maxw-content); margin: 56px auto 0; padding: 24px 32px 0;
  border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
  font-family: var(--font-sans); font-size: 11px; color: var(--fg-muted);
  letter-spacing: 0.08em; text-transform: uppercase;
}}
.site-footer .legal a {{ color: var(--fg-muted); text-decoration: none; }}
.site-footer .legal a:hover {{ color: var(--blush-600); }}
.site-footer .legal nav {{ display: flex; gap: 24px; flex-wrap: wrap; }}

/* Sections */
section.surface-white {{ background: #fff; padding: var(--space-9) 0; }}
section.surface-blush {{ background: var(--blush-50); padding: var(--space-9) 0; }}
section.surface-paper {{ background: var(--paper); padding: 80px 0; }}

/* Hero (page-level) — full-bleed photo with caption overlaid bottom-left
   on a soft scrim. Blush halo extends below the photo to anchor it visually. */
.hero {{
  position: relative; padding: 0; overflow: hidden;
  background: var(--blush-50);
}}
.hero .halo {{
  position: absolute; left: 0; right: 0; bottom: 0; height: 96px;
  background: var(--blush-50); z-index: 0;
}}
.hero .frame {{
  position: relative; max-width: none; margin: 0; height: 620px;
  overflow: hidden; border-radius: 0; z-index: 1;
}}
.hero .frame img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
/* Strong full-frame scrim — guarantees text contrast regardless of what the
   photo shows. Top is slightly tinted to soften bright-sky / kitchen photos,
   bottom is heavily darkened where the caption sits. */
.hero .frame::after {{
  content: ""; position: absolute; inset: 0;
  background:
    linear-gradient(180deg,
      rgba(10,10,10,0.20) 0%,
      rgba(10,10,10,0.40) 35%,
      rgba(10,10,10,0.75) 80%,
      rgba(10,10,10,0.85) 100%);
  pointer-events: none;
}}
.hero .caption {{
  position: absolute; left: 0; right: 0; bottom: 0; z-index: 2;
  max-width: 1320px; margin: 0 auto; padding: 0 80px 64px;
  box-sizing: border-box;
}}
.hero .caption .eyebrow {{ color: #fff; opacity: 0.9; }}
.hero .caption h1 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(40px, 4.6vw, 64px); line-height: 1.05;
  letter-spacing: -0.02em; color: #fff; margin: 0 0 14px; max-width: 720px;
}}
.hero .caption .ingress {{
  font-family: var(--font-sans); font-size: 17px; line-height: 1.55;
  color: rgba(255,255,255,0.9); margin: 0 0 22px; max-width: 540px;
}}
.hero .bulletins {{
  list-style: none; padding: 0; margin: 0 0 30px;
  display: flex; flex-direction: column; gap: 10px;
}}
.hero .bulletins li {{
  font-family: var(--font-sans); font-size: 17px; font-weight: 500;
  color: rgba(255,255,255,0.97);
  display: flex; align-items: center; gap: 12px;
}}
.hero .bulletins li svg {{
  flex-shrink: 0; color: var(--blush-500); width: 20px; height: 20px;
}}
.hero .buttons {{ display: flex; gap: 12px; flex-wrap: wrap; }}
.hero .buttons .btn-ghost {{ color: #fff; border-color: rgba(255,255,255,0.7); }}
.hero .buttons .btn-ghost:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}

/* Intro (centered short statement) */
.intro {{ padding: 96px 0 0; text-align: center; }}
.intro h2 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(30px, 3vw, 44px); line-height: 1.2;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 auto 18px; max-width: 720px;
}}
.intro .ingress {{
  font-family: var(--font-sans); font-size: 17px; line-height: 1.65;
  color: var(--fg); margin: 0 auto; max-width: 600px;
}}

/* Treatments grid (home) */
.treatments {{ padding: 80px 0; }}
.treatments .eyebrow {{ display: block; margin-bottom: 28px; text-align: center; }}
.treatments .grid {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}}
.treatments .card {{
  position: relative; aspect-ratio: 1; border-radius: var(--radius-sm);
  overflow: hidden; display: block; text-decoration: none;
  transition: transform var(--dur-base) var(--ease-out);
}}
.treatments .card:hover {{ transform: translateY(-2px); }}
.treatments .card img {{ width: 100%; height: 100%; object-fit: cover; }}
.treatments .card .overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.45) 100%);
}}
.treatments .card .label {{
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-sans); font-size: 12px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: #fff; text-align: center; padding: 20px; line-height: 1.3;
}}

/* Content block — text + one large image, text vertically centered */
.content-block {{ padding: 96px 0; }}
.content-block .grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: center;
}}
.content-block h2 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 24px;
}}
.content-block .text p {{
  font-family: var(--font-sans); font-size: 16px; line-height: 1.7;
  color: var(--fg); margin: 0 0 18px; max-width: 54ch;
}}
.content-block .text strong {{ color: var(--ink-700); font-weight: 600; }}
.content-block .img {{
  width: 100%; aspect-ratio: 4/5; overflow: hidden;
  border-radius: var(--radius-sm); background: var(--blush-100);
}}
.content-block .img img {{ width: 100%; height: 100%; object-fit: cover; }}
.content-block .buttons {{ margin-top: 32px; }}

/* Content block 2 — full-width prose with H3 + subtext */
.content-block-2 {{ padding: 96px 0; background: var(--blush-50); }}
.content-block-2 .inner {{ max-width: 860px; margin: 0 auto; padding: 0 32px; text-align: center; }}
.content-block-2 h2 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 24px;
}}
.content-block-2 .text p {{
  font-family: var(--font-sans); font-size: 16px; line-height: 1.75;
  color: var(--fg); margin: 0 auto 18px; max-width: 60ch; text-align: left;
}}
.content-block-2 .buttons {{ margin: 16px 0 56px; display: flex; justify-content: center; }}
.content-block-2 h3 {{
  font-family: var(--font-sans); font-weight: 500;
  font-size: 20px; color: var(--ink-700); margin: 0 0 16px;
  text-transform: uppercase; letter-spacing: 0.18em;
}}
.content-block-2 .subtext {{ text-align: left; max-width: 60ch; margin: 0 auto; }}
.content-block-2 .subtext p,
.content-block-2 .subtext ul {{
  font-family: var(--font-sans); font-size: 15px; line-height: 1.7;
  color: var(--fg);
}}
.content-block-2 .subtext ul {{ list-style: none; padding: 0; margin: 0; }}
.content-block-2 .subtext li {{ padding: 8px 0 8px 22px; position: relative; border-bottom: 1px solid var(--border); }}
.content-block-2 .subtext li::before {{
  content: ""; position: absolute; left: 0; top: 17px;
  width: 12px; height: 1px; background: var(--blush-500);
}}
.content-block-2 .subtext strong {{ color: var(--ink-700); font-weight: 600; }}

/* Text blocks list (om-oss extra prose) */
.text-blocks {{ padding: 96px 0; background: #fff; }}
.text-blocks .inner {{ max-width: 860px; margin: 0 auto; padding: 0 32px; }}
.text-blocks .item {{ padding: 36px 0; border-top: 1px solid var(--border); }}
.text-blocks .item:first-child {{ border-top: none; padding-top: 0; }}
.text-blocks h3 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: 26px; line-height: 1.2; letter-spacing: -0.01em;
  color: var(--ink-700); margin: 0 0 14px;
}}
.text-blocks .item p {{
  font-family: var(--font-sans); font-size: 16px; line-height: 1.7;
  color: var(--fg); margin: 0; max-width: 60ch;
}}
.text-blocks .item strong {{ color: var(--ink-700); font-weight: 600; }}

/* Contact block (form panel) */
.contact-panel {{ background: var(--blush-200); padding: 96px 0; }}
.contact-panel .inner {{
  max-width: 1100px; margin: 0 auto; padding: 0 32px;
  display: grid; grid-template-columns: 1fr 1.4fr; gap: 80px;
}}
.contact-panel h3 {{
  font-family: var(--font-sans); font-size: 18px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.18em; color: var(--ink-700);
  margin: 0 0 22px;
}}
.contact-panel .line {{
  font-family: var(--font-sans); font-size: 14px; color: var(--blush-700); margin-bottom: 8px;
}}
.contact-panel .line a {{ color: var(--blush-700); text-decoration: underline; text-underline-offset: 3px; }}
.contact-panel .row {{
  display: flex; justify-content: space-between; padding: 6px 0;
  font-family: var(--font-sans); font-size: 14px; color: var(--ink-600);
  text-transform: uppercase; letter-spacing: 0.06em; max-width: 280px;
}}
.contact-panel .row .day {{ color: var(--fg-muted); }}
.contact-panel form {{ display: flex; flex-direction: column; gap: 18px; }}
.contact-panel .two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.contact-panel label {{
  font-family: var(--font-sans); font-size: 13px; color: var(--ink-700);
  display: flex; flex-direction: column; gap: 6px;
}}
.contact-panel .req {{ color: var(--blush-600); }}
.contact-panel input, .contact-panel textarea {{
  background: #fff; border: 1px solid transparent; padding: 12px 14px;
  border-radius: var(--radius-sm); font-family: var(--font-sans); font-size: 14px;
  color: var(--ink-700); width: 100%; box-sizing: border-box;
}}
.contact-panel textarea {{ min-height: 120px; }}
.contact-panel button {{
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.22em;
  background: var(--blush-500); color: #fff; border: none;
  padding: 15px 56px; border-radius: var(--radius-sm); cursor: pointer;
  align-self: center; margin-top: 8px;
  box-shadow: 0 8px 22px rgba(212,136,158,0.30), 0 2px 4px rgba(212,136,158,0.15);
  transition: background var(--dur-fast) var(--ease-standard),
              box-shadow var(--dur-fast) var(--ease-standard),
              transform var(--dur-fast) var(--ease-standard);
}}
.contact-panel button:hover {{
  background: var(--blush-600);
  box-shadow: 0 10px 28px rgba(181,106,130,0.40), 0 2px 6px rgba(181,106,130,0.20);
  transform: translateY(-1px);
}}

/* Map section — embedded Google Maps. */
.map-section {{ padding: 96px 0; background: #fff; }}
.map-section .inner {{
  max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px;
  text-align: center;
}}
.map-section .eyebrow {{ display: inline-block; margin-bottom: 16px; }}
.map-section h2 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 14px;
}}
.map-section .ingress {{
  font-family: var(--font-sans); font-size: 16px; line-height: 1.65;
  color: var(--fg); margin: 0 auto 36px; max-width: 540px;
}}
.map-section .map-frame {{
  position: relative; width: 100%; aspect-ratio: 16/9;
  border-radius: var(--radius-sm); overflow: hidden;
  border: 1px solid var(--border);
  /* Soft map-style placeholder shown until iframe loads (or if blocked
     when previewed from file://). Replaced visually by the iframe content
     once it renders on a real https origin. */
  background:
    linear-gradient(135deg, rgba(212,136,158,0.06) 0%, rgba(180,180,180,0.04) 100%),
    repeating-linear-gradient(0deg, rgba(0,0,0,0.04) 0px, rgba(0,0,0,0.04) 1px, transparent 1px, transparent 48px),
    repeating-linear-gradient(90deg, rgba(0,0,0,0.04) 0px, rgba(0,0,0,0.04) 1px, transparent 1px, transparent 48px),
    var(--paper);
}}
.map-section .map-frame::before {{
  content: ""; position: absolute; left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  width: 36px; height: 36px;
  background: var(--blush-500);
  clip-path: path("M18 0 C8 0 0 8 0 18 C0 28 18 36 18 36 C18 36 36 28 36 18 C36 8 28 0 18 0 Z");
  opacity: 0.85;
}}
.map-section .map-frame::after {{
  content: ""; position: absolute; left: 50%; top: 50%;
  transform: translate(-50%, -50%) translateY(-3px);
  width: 10px; height: 10px; border-radius: 999px;
  background: #fff;
}}
.map-section .map-frame iframe {{
  position: absolute; inset: 0; width: 100%; height: 100%; border: 0;
  display: block; background: transparent; z-index: 2;
}}
.map-section .actions {{ margin-top: 24px; }}

/* FAQ (treatment pages) */
.faq {{ padding: 96px 0; background: var(--paper); }}
.faq .inner {{ max-width: 860px; margin: 0 auto; padding: 0 32px; }}
.faq .eyebrow {{ display: block; text-align: center; }}
.faq h2 {{
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); text-align: center;
  margin: 0 0 48px;
}}
.faq details {{
  border-top: 1px solid var(--border); padding: 22px 0;
}}
.faq details:last-of-type {{ border-bottom: 1px solid var(--border); }}
.faq summary {{
  list-style: none; cursor: pointer;
  font-family: var(--font-sans); font-size: 17px; font-weight: 500;
  color: var(--ink-700); display: flex; justify-content: space-between; align-items: center;
}}
.faq summary::-webkit-details-marker {{ display: none; }}
.faq summary::after {{ content: "+"; color: var(--blush-600); font-size: 22px; font-weight: 300; }}
.faq details[open] summary::after {{ content: "−"; }}
.faq details p {{
  font-family: var(--font-sans); font-size: 15px; line-height: 1.7;
  color: var(--fg); margin: 14px 0 0; max-width: 60ch;
}}

/* Responsive */
@media (max-width: 900px) {{
  .content-block .grid {{ grid-template-columns: 1fr; gap: 32px; }}
  .treatments .grid {{ grid-template-columns: repeat(2, 1fr); }}
  .contact-panel .inner {{ grid-template-columns: 1fr; gap: 48px; }}
  .hero .frame {{ height: 640px; }}
  .hero .caption {{ padding: 0 32px 40px; }}
  .hero .caption h1 {{ font-size: clamp(32px, 7vw, 44px); }}
  .site-footer .columns {{ grid-template-columns: 1fr 1fr; gap: 40px; }}
  .site-footer .brand {{ grid-column: 1 / -1; margin-bottom: 8px; }}

  /* Tablet + mobile: replace inline nav (incl. Boka tid CTA) with hamburger drawer. */
  .site-header .hamburger {{ display: flex; }}
  .site-header nav {{
    position: absolute; top: 100%; left: 0; right: 0;
    flex-direction: column; align-items: stretch; gap: 0;
    background: #fff; border-bottom: 1px solid var(--border);
    box-shadow: 0 12px 28px rgba(20,20,20,0.10);
    padding: 8px 24px 24px;
    max-height: 0; overflow: hidden; opacity: 0;
    transition: max-height var(--dur-base) var(--ease-standard),
      opacity var(--dur-base) var(--ease-standard),
      padding var(--dur-base) var(--ease-standard);
    pointer-events: none;
  }}
  .site-header .nav-toggle:checked ~ nav {{
    max-height: 480px; opacity: 1; pointer-events: auto;
    padding: 12px 24px 28px;
  }}
  .site-header nav a {{
    padding: 16px 4px; border-bottom: 1px solid var(--border);
    font-size: 12px;
  }}
  .site-header nav a:last-child {{ border-bottom: none; }}
  .site-header nav a.btn-primary {{
    margin-top: 14px; padding: 14px 20px; text-align: center;
    border-bottom: none; border-radius: 999px;
  }}
}}
@media (max-width: 600px) {{
  .site-header .inner {{ padding: 14px 20px; }}
  .site-header .logo svg {{ height: 46px; }}

  .hero .frame {{ height: 560px; border-radius: 0; }}
  .hero .caption {{ padding: 0 24px 32px; }}
  .hero .caption h1 {{ font-size: clamp(38px, 9vw, 48px); line-height: 1.05; margin-bottom: 14px; }}
  .hero .caption .ingress {{ font-size: 15px; margin-bottom: 18px; }}
  .hero .bulletins {{ margin-bottom: 24px; gap: 8px; }}
  .hero .bulletins li {{ font-size: 15px; }}
  .hero .bulletins li svg {{ width: 18px; height: 18px; }}
  .hero .buttons .btn-row {{ flex-direction: row; justify-content: center; flex-wrap: wrap; gap: 10px; }}
  .hero .buttons .btn-primary, .hero .buttons .btn-ghost {{ text-align: center; padding: 13px 20px; font-size: 14px; }}
  /* Ghost button on mobile sits over bright photo areas — flip to solid white
     so the contrast is reliable regardless of what's behind it. */
  .hero .buttons .btn-ghost {{
    background: rgba(255,255,255,0.95); color: var(--ink-700);
    border-color: rgba(255,255,255,0.95);
  }}
  .hero .buttons .btn-ghost:hover {{
    background: #fff; color: var(--ink-900);
  }}

  .intro {{ padding: 64px 0 0; }}
  .treatments {{ padding: 56px 0; }}
  .treatments .grid {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }}
  .content-block {{ padding: 64px 0; }}
  .content-block-2 {{ padding: 64px 0; }}
  .text-blocks {{ padding: 64px 0; }}
  .contact-panel {{ padding: 64px 0; }}
  .contact-panel .two {{ grid-template-columns: 1fr; gap: 14px; }}
  .faq {{ padding: 64px 0; }}
  .map-section {{ padding: 64px 0; }}
  .map-section .map-frame {{ aspect-ratio: 4/5; }}

  .site-footer {{ padding: 56px 0 24px; }}
  .site-footer .columns {{
    grid-template-columns: 1fr; gap: 36px; padding: 0 24px;
  }}
  .site-footer .brand {{ text-align: left; }}
  .site-footer .legal {{
    flex-direction: column; align-items: flex-start; gap: 14px;
    margin-top: 36px; padding: 24px 24px 0;
  }}
  .site-footer .legal nav {{ gap: 18px; }}

  section.surface-white, section.surface-blush, section.surface-paper {{ padding: 64px 0; }}
}}
</style>
</head>
<body class="page">
<header class="site-header">
  <div class="inner">
    <a href="hem_design.html" class="logo" aria-label="{company}">{header_logo}</a>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-hidden="true">
    <label for="nav-toggle" class="hamburger" aria-label="Öppna meny">
      <span></span><span></span><span></span>
    </label>
    <nav>
      <a href="hem_design.html">Hem</a>
      <a href="om-oss_design.html">Om oss</a>
      <a href="tandimplantat_design.html">Behandlingar</a>
      <a href="kontakt_design.html">Kontakt</a>
      <a href="#tdl-booking-widget" class="btn-primary" style="padding:12px 22px;">Boka tid</a>
    </nav>
  </div>
</header>
{body}
<footer class="site-footer">
  <div class="columns">
    <div class="brand">
      <a href="hem_design.html" class="logo" aria-label="{company}">{footer_logo}</a>
      <p class="tagline">Modern tandvård i centrala Stockholm — för en frisk mun och ett strålande leende.</p>
    </div>
    <div class="treatments-col">
      <h4>Behandlingar</h4>
      {treatments_html}
    </div>
    <div>
      <h4>Sajt</h4>
      <ul>
        <li><a href="hem_design.html">Hem</a></li>
        <li><a href="om-oss_design.html">Om oss</a></li>
        <li><a href="kontakt_design.html">Kontakt</a></li>
        <li><a href="#tdl-booking-widget">Boka tid</a></li>
      </ul>
    </div>
    <div class="contact">
      <h4>Kontakt</h4>
      {contact_html}
    </div>
  </div>
  <div class="legal">
    <div>© {year} {company}</div>
    <nav>
      <a href="#">Integritetspolicy</a>
      <a href="#">Cookies</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def render_buttons(buttons: dict, settings: dict) -> str:
    if not buttons:
        return ""
    out = ['<div class="btn-row">']
    style_map = {"boka": "btn-primary", "ring": "btn-ghost"}
    phone_clean = re.sub(r"[^\d+]", "", settings.get("company_phone", ""))
    for key, btn in buttons.items():
        title = btn.get("title", "")
        url   = btn.get("url", "#")
        url   = url.replace("{{company_phone}}", phone_clean) \
                   .replace("{{site_phone}}", phone_clean)
        cls   = style_map.get(key, "btn-ghost")
        out.append(f'<a href="{url}" class="{cls}">{title}</a>')
    out.append("</div>")
    return "\n".join(out)


CHECK_ICON = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20 6L9 17l-5-5"/></svg>'
)


def render_hero(hero: dict, manifest: dict, settings: dict,
                page_slug: str | None = None,
                eyebrow: str | None = None) -> str:
    bg = img_url(manifest, hero.get("bg_image_id", ""))

    headline = HERO_H1_OVERRIDE.get(page_slug, hero.get("h1", ""))
    eyebrow_text = eyebrow or HERO_EYEBROW.get(page_slug)
    eyebrow_html = f'<div class="eyebrow">{eyebrow_text}</div>' if eyebrow_text else ""

    bullets = hero.get("bulletins") or []
    bullets_html = ""
    if bullets:
        items = "".join(f"<li>{CHECK_ICON}<span>{b}</span></li>" for b in bullets)
        bullets_html = f'<ul class="bulletins">{items}</ul>'

    return f"""
<section class="hero">
  <div class="halo"></div>
  <div class="frame"><img src="{bg}" alt="{hero.get('alt','')}"/></div>
  <div class="caption">
    {eyebrow_html}
    <h1>{headline}</h1>
    <p class="ingress">{hero.get('ingress','')}</p>
    {bullets_html}
    <div class="buttons">{render_buttons(hero.get('buttons',{}), settings)}</div>
  </div>
</section>"""


def render_intro(intro: dict) -> str:
    return f"""
<section class="intro container">
  <h2>{intro.get('h2','')}</h2>
  <p class="ingress">{intro.get('ingress','')}</p>
</section>"""


def render_treatments_grid(items: list, manifest: dict) -> str:
    cards = []
    for it in items:
        url = img_url(manifest, it.get("image_id", ""))
        cards.append(f"""
      <a href="{it.get('link','#')}_design.html" class="card">
        <img src="{url}" alt="{it.get('title','')}"/>
        <div class="overlay"></div>
        <div class="label">{it.get('title','')}</div>
      </a>""")
    return f"""
<section class="treatments container">
  <span class="eyebrow">Våra behandlingar</span>
  <div class="grid">{''.join(cards)}</div>
</section>"""


def render_content_block_1(block: dict, manifest: dict, settings: dict) -> str:
    img1 = img_url(manifest, block.get("image_1_id", ""))
    return f"""
<section class="content-block container">
  <div class="grid">
    <div class="text">
      <h2>{block.get('h2','')}</h2>
      {block.get('text_html','')}
      <div class="buttons">{render_buttons(block.get('buttons',{}), settings)}</div>
    </div>
    <div class="img"><img src="{img1}" alt="{block.get('image_1_alt','')}"/></div>
  </div>
</section>"""


def render_content_block_2(block: dict, settings: dict) -> str:
    return f"""
<section class="content-block-2">
  <div class="inner">
    <h2>{block.get('h2','')}</h2>
    <div class="text">{block.get('text_html','')}</div>
    <div class="buttons">{render_buttons(block.get('buttons',{}), settings)}</div>
    <h3>{block.get('h3','')}</h3>
    <div class="subtext">{block.get('subtext_html','')}</div>
  </div>
</section>"""


def render_text_blocks(blocks: list) -> str:
    items = []
    for b in blocks:
        items.append(f"""
    <div class="item">
      <h3>{b.get('h3','')}</h3>
      {b.get('text_html','')}
    </div>""")
    return f"""
<section class="text-blocks">
  <div class="inner">{''.join(items)}</div>
</section>"""


def render_contact_block(block: dict, settings: dict) -> str:
    phone = settings.get("company_phone", "")
    email = settings.get("company_email", "")
    address = settings.get("company_address", "")
    intro_html = block.get("text_html", "") if block else ""
    intro_h2 = block.get("h2", "") if block else "Kontakta oss"
    return f"""
<section class="contact-panel">
  <div class="inner">
    <div>
      <span class="eyebrow">Telefon &amp; e-post</span>
      <h3>{intro_h2}</h3>
      <div class="line">{tel_link(phone)}</div>
      <div class="line">{email_link(email)}</div>
      <div class="line" style="margin-top:18px;">{address_link(address)}</div>
      <h3 style="margin-top:48px;">Öppettider</h3>
      <div class="row"><span class="day">Mån–Fre</span><span>08–18</span></div>
      <div class="row"><span class="day">Lördag</span><span>09–16</span></div>
      <div class="row"><span class="day">Söndag</span><span>Stängt</span></div>
    </div>
    <div>
      <h3 style="text-align:center;margin-bottom:28px;">Skicka en förfrågan</h3>
      <form>
        <div class="two">
          <label>Förnamn <span class="req">*</span><input required/></label>
          <label>Efternamn <span class="req">*</span><input required/></label>
        </div>
        <div class="two">
          <label>E-post <span class="req">*</span><input type="email" required/></label>
          <label>Telefon <span class="req">*</span><input required/></label>
        </div>
        <label>Ditt meddelande <span class="req">*</span><textarea required></textarea></label>
        <button type="submit">Skicka</button>
      </form>
    </div>
  </div>
</section>"""


def render_map_section(settings: dict, eyebrow: str = "Hitta hit",
                       heading: str | None = None,
                       ingress: str | None = None) -> str:
    address = settings.get("company_address", "")
    if not address:
        return ""
    embed_src = f"https://maps.google.com/maps?q={quote_plus(address)}&output=embed"
    heading = heading or f"Hitta till oss på {address.split(',')[0]}"
    ingress_html = f'<p class="ingress">{ingress}</p>' if ingress else ""
    map_link = address_link(address, "Öppna i Google Maps", cls="btn-ghost")
    return f"""
<section class="map-section">
  <div class="inner">
    <span class="eyebrow">{eyebrow}</span>
    <h2>{heading}</h2>
    {ingress_html}
    <div class="map-frame">
      <iframe src="{embed_src}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen title="Karta — {address}"></iframe>
    </div>
    <div class="actions">{map_link}</div>
  </div>
</section>"""


def render_faq(items: list) -> str:
    rows = []
    for f in items:
        rows.append(f"""
    <details>
      <summary>{f.get('question','')}</summary>
      <p>{f.get('answer','')}</p>
    </details>""")
    return f"""
<section class="faq">
  <div class="inner">
    <span class="eyebrow">Vanliga frågor</span>
    <h2>Frågor och svar</h2>
    {''.join(rows)}
  </div>
</section>"""


# ----------------------------------------------------------------------------

def build_home(page: dict, manifest: dict, settings: dict) -> str:
    s = page["sections"]
    return "\n".join([
        render_hero(s["hero"], manifest, settings, page_slug=page["slug"]),
        render_intro(s["intro"]),
        render_treatments_grid(s["treatments_section"], manifest),
        render_content_block_1(s["content_block_1"], manifest, settings),
        render_content_block_2(s["content_block_2"], settings),
    ])


def build_about(page: dict, manifest: dict, settings: dict) -> str:
    s = page["sections"]
    return "\n".join([
        render_hero(s["hero"], manifest, settings, page_slug=page["slug"], eyebrow="Om oss"),
        render_content_block_1(s["content_block_1"], manifest, settings),
        render_text_blocks(s["text_blocks"]),
        render_map_section(
            settings,
            eyebrow="Besök oss",
            heading="Kom förbi vår klinik",
            ingress="Du hittar oss centralt i Stockholm. Boka en tid eller kom in och hälsa på.",
        ),
    ])


def build_contact(page: dict, manifest: dict, settings: dict) -> str:
    s = page["sections"]
    return "\n".join([
        render_hero(s["hero"], manifest, settings, page_slug=page["slug"], eyebrow="Kontakt"),
        render_contact_block(s.get("contact_block", {}), settings),
        render_map_section(
            settings,
            eyebrow="Hitta hit",
            heading="Vägbeskrivning till kliniken",
        ),
    ])


def build_treatment(page: dict, manifest: dict, settings: dict) -> str:
    s = page["sections"]
    return "\n".join([
        render_hero(s["hero"], manifest, settings, page_slug=page["slug"], eyebrow="Behandling"),
        render_intro(s["intro"]),
        render_content_block_1(s["content_block_1"], manifest, settings),
        render_content_block_2(s["content_block_2"], settings),
        render_faq(s.get("faq", [])),
    ])


BUILDERS = {
    "home":      build_home,
    "about":     build_about,
    "contact":   build_contact,
    "treatment": build_treatment,
}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate HTML mockups for client review.")
    parser.add_argument("--client", help='Client name, e.g. "ostra-bageriet". Reads from clients/<name>/.tmp/')
    args = parser.parse_args()

    tmp = _resolve_tmp(args.client)
    out_dir = tmp
    print(f"[INFO] Reading from: {tmp.relative_to(ROOT)}")

    content, manifest, tokens, logo_full, logo_mark = load(tmp)
    settings = content.get("settings", {})

    # Build a list of treatment pages for the footer column
    treatments = [
        {"slug": p["slug"], "title": p.get("sections", {}).get("hero", {}).get("h1", p["slug"].title())}
        for p in content.get("pages", []) if p.get("type") == "treatment"
    ]

    pages_to_render = {
        "home":      "hem_design.html",
        "about":     "om-oss_design.html",
        "contact":   "kontakt_design.html",
        "treatment": f"{REPRESENTATIVE_TREATMENT_SLUG}_design.html",
    }

    rendered = []
    for page in content["pages"]:
        ptype = page.get("type")
        if ptype not in pages_to_render:
            continue
        if ptype == "treatment" and page["slug"] != REPRESENTATIVE_TREATMENT_SLUG:
            continue
        body = BUILDERS[ptype](page, manifest, settings)
        title = page.get("sections", {}).get("hero", {}).get("h1", page["slug"].title())
        html = page_shell(title, body, tokens, settings,
                          logo_full=logo_full, logo_mark=logo_mark,
                          treatments=treatments)
        out_path = out_dir / pages_to_render[ptype]
        out_path.write_text(html, encoding="utf-8")
        rendered.append((page["slug"], out_path))

    print(f"[OK] Generated {len(rendered)} HTML mockup(s):")
    for slug, path in rendered:
        print(f"  {slug:20s} -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
