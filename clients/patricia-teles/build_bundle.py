"""
build_patricia_bundle.py
Decomposes the approved Patricia Teles HTML mockups (build_design_html.py) into
LumoKit components and emits a single bundle JSON ready for build_all.py.

Inputs:
  .tmp/content/text/lumo-content.json
  .tmp/content/_media_manifest.json
  .tmp/Design system/colors_and_type.css
  .tmp/Design system/assets/logo.svg

Output:
  .tmp/patricia_teles_bundle.json

Usage:
  python3 tools/build_patricia_bundle.py
  python3 tools/build_all.py .tmp/patricia_teles_bundle.json
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote_plus

# Paths are anchored to this client directory — keeps everything self-contained
# under clients/patricia-teles/ so factory and other clients aren't entangled.
CLIENT_DIR    = Path(__file__).resolve().parent
ROOT          = CLIENT_DIR.parent.parent  # repo root, only used for cross-tool calls
CONTENT_FILE  = CLIENT_DIR / "content" / "text" / "lumo-content.json"
MANIFEST_FILE = CLIENT_DIR / "content" / "_media_manifest.json"
TOKENS_FILE   = CLIENT_DIR / "design-system" / "colors_and_type.css"
LOGO_FILE     = CLIENT_DIR / "design-system" / "assets" / "logo.svg"
OUT_FILE      = CLIENT_DIR / "bundle.json"

# Static fallback address for the embedded map iframe. The site_address token
# can't be URL-encoded inside an iframe src dynamically, so we hardcode the
# encoded form here and the editable address text shows separately.
PATRICIA_ADDRESS_ENCODED = quote_plus("Jakobsbergsgatan 8, 4tr, 11144 Stockholm")


# ---------------------------------------------------------------------------
# CSS  ── stolen verbatim from build_design_html.py
# Concatenates colors_and_type.css + the layout CSS embedded in page_shell().
# This is the entire stylesheet for the site, inlined into site-header.
# ---------------------------------------------------------------------------

LAYOUT_CSS = """
/* Hard guard against horizontal overflow caused by third-party widgets or
   stray wide elements. The viewport is the absolute width — nothing scrolls
   sideways and no white gap appears next to the hero. */
html, body { overflow-x: hidden; max-width: 100vw; }

/* Layout helpers used across the page mockups */
.page { background: var(--bg); color: var(--fg); }
.container { max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px; }
.eyebrow {
  font-family: var(--font-sans); font-size: var(--fs-eyebrow); font-weight: 500;
  text-transform: uppercase; letter-spacing: var(--tracking-eyebrow);
  color: var(--fg-accent); margin-bottom: 16px; display: inline-block;
}
.btn-primary {
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: #fff; background: var(--blush-500); border: none;
  padding: 15px 30px; border-radius: var(--radius-sm); cursor: pointer;
  text-decoration: none; display: inline-block; white-space: nowrap;
  box-shadow: 0 8px 22px rgba(212, 136, 158, 0.30), 0 2px 4px rgba(212,136,158,0.15);
  transition: background var(--dur-fast) var(--ease-standard),
              box-shadow var(--dur-fast) var(--ease-standard),
              transform var(--dur-fast) var(--ease-standard);
}
.btn-primary:hover {
  background: var(--blush-600); color: #fff; text-decoration: none;
  box-shadow: 0 10px 28px rgba(181, 106, 130, 0.40), 0 2px 6px rgba(181,106,130,0.20);
  transform: translateY(-1px);
}
.btn-ghost {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--ink-700); background: transparent; border: 1px solid var(--ink-700);
  padding: 13px 28px; border-radius: var(--radius-sm); cursor: pointer;
  text-decoration: none; display: inline-block;
}
.btn-ghost:hover { background: var(--blush-50); color: var(--ink-700); text-decoration: none; }
.btn-row { display: flex; flex-wrap: wrap; gap: 12px; }

/* Header */
.site-header {
  position: sticky; top: 0; z-index: 50; background: #fff;
  border-bottom: 1px solid var(--border);
}
/* Push sticky header below WP admin bar when logged in. */
.admin-bar .site-header { top: 32px; }
@media (max-width: 782px) {
  .admin-bar .site-header { top: 46px; }
}
.site-header .inner {
  position: relative;
  max-width: 1280px; margin: 0 auto; padding: 18px 32px;
  display: flex; justify-content: space-between; align-items: center;
}
.site-header .logo {
  display: inline-flex; align-items: center; text-decoration: none;
  color: var(--ink-700);
}
.site-header .logo svg { height: 60px; width: auto; display: block; }
.site-header nav { display: flex; align-items: center; gap: 28px; }
.site-header nav a, .site-header nav .menu-item a {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--ink-700); text-decoration: none;
}
.site-header nav a:hover { color: var(--blush-600); }
.site-header nav a.btn-primary,
.site-header nav a.btn-primary:visited { color: #fff !important; }
.site-header nav a.btn-primary:hover { color: #fff !important; }
.site-header nav ul { list-style: none; padding: 0; margin: 0; display: flex; gap: 28px; align-items: center; }
/* Desktop dropdown for sub-menu items (children of "menu-item-has-children") */
.site-header nav li { position: relative; }
.site-header nav li.menu-item-has-children > a::after {
  content: "▾"; margin-left: 6px; font-size: 10px; opacity: 0.7;
}
.site-header nav .sub-menu {
  display: none; position: absolute; top: 100%; left: 0;
  background: #fff; border: 1px solid var(--border);
  box-shadow: 0 12px 28px rgba(20,20,20,0.10);
  padding: 8px 0; margin-top: 8px;
  min-width: 220px; flex-direction: column; gap: 0;
  border-radius: 8px; z-index: 60;
}
/* Invisible bridge so the cursor can travel from parent to submenu without
   the hover dropping. */
.site-header nav li.menu-item-has-children::after {
  content: ""; position: absolute; left: 0; right: 0;
  top: 100%; height: 12px; background: transparent;
}
.site-header nav li:hover > .sub-menu,
.site-header nav li:focus-within > .sub-menu { display: flex; }
.site-header nav .sub-menu li { width: 100%; }
.site-header nav .sub-menu a {
  display: block; padding: 10px 18px; white-space: nowrap;
  font-size: 11px; letter-spacing: 0.18em;
  transition: background var(--dur-fast) var(--ease-standard),
    color var(--dur-fast) var(--ease-standard);
}
.site-header nav .sub-menu a:hover {
  background: var(--blush-50); color: var(--blush-600);
}

/* Hamburger toggle */
.site-header .nav-toggle { display: none; }
.site-header .hamburger {
  display: none; width: 44px; height: 44px; cursor: pointer;
  align-items: center; justify-content: center; flex-direction: column;
  gap: 5px; border-radius: 8px; transition: background var(--dur-fast) var(--ease-standard);
}
.site-header .hamburger:hover { background: var(--blush-50); }
.site-header .hamburger span {
  display: block; width: 24px; height: 2px; background: var(--ink-700);
  border-radius: 2px; transition: transform var(--dur-fast) var(--ease-standard),
    opacity var(--dur-fast) var(--ease-standard);
}
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(2) { opacity: 0; }
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Footer */
.site-footer { background: #fff; border-top: 1px solid var(--border); padding: 72px 0 32px; }
.site-footer .columns {
  max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px;
  display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.2fr; gap: 56px;
  align-items: start;
}
.site-footer .brand .logo { opacity: 0.85; display: inline-block; }
.site-footer .brand .logo svg { height: 56px; width: auto; display: block; }
.site-footer .brand .tagline {
  font-family: var(--font-serif); font-size: 17px; font-style: italic;
  color: var(--fg-muted); margin: 18px 0 0; line-height: 1.45; max-width: 30ch;
}
.site-footer h4 {
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--blush-600); margin: 0 0 18px;
}
.site-footer ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.site-footer ul a { font-family: var(--font-sans); font-size: 14px; color: var(--ink-600); text-decoration: none; transition: color var(--dur-fast) var(--ease-standard); }
.site-footer ul a:hover { color: var(--blush-600); }
.site-footer .contact a { font-family: var(--font-sans); font-size: 14px; color: var(--ink-600); text-decoration: none; line-height: 1.5; }
.site-footer .contact a:hover { color: var(--blush-600); }
.site-footer .contact .row { margin-bottom: 12px; }
.site-footer .contact .row .label .ico { color: var(--blush-500); display: inline-flex; vertical-align: -3px; margin-right: 4px; }
.site-footer .contact .row .label .ico svg { width: 14px; height: 14px; }
.site-footer .contact .row .label {
  display: block; font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.18em; color: var(--fg-muted); margin-bottom: 4px;
}
.site-footer .legal {
  max-width: var(--maxw-content); margin: 56px auto 0; padding: 24px 32px 0;
  border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
  font-family: var(--font-sans); font-size: 11px; color: var(--fg-muted);
  letter-spacing: 0.08em; text-transform: uppercase;
}
.site-footer .legal a { color: var(--fg-muted); text-decoration: none; }
.site-footer .legal a:hover { color: var(--blush-600); }
.site-footer .legal nav { display: flex; gap: 24px; flex-wrap: wrap; }

/* Sections */
section.surface-white { background: #fff; padding: var(--space-9) 0; }
section.surface-blush { background: var(--blush-50); padding: var(--space-9) 0; }
section.surface-paper { background: var(--paper); padding: 80px 0; }

/* Hero */
.hero { position: relative; padding: 0; overflow: hidden; background: var(--blush-50); }

/* Reserve space for the Trustindex score widget so its async load doesn't
   push other content. Roughly the badge's natural height. */
.hero .caption .hero-score { min-height: 56px; }

/* Quick onload fade (350ms) — masks the brief font-swap moment.
   Short enough to feel responsive, long enough to feel polished. */
.hero { opacity: 0; transition: opacity 350ms ease-out; }
body.lumo-loaded .hero { opacity: 1; }
/* Failsafe — never leave hero hidden if JS fails */
@keyframes lumo-show-hero { to { opacity: 1; } }
.hero { animation: lumo-show-hero 0s linear 800ms forwards; }
.hero .halo { position: absolute; left: 0; right: 0; bottom: 0; height: 96px; background: var(--blush-50); z-index: 0; }
.hero .frame {
  position: relative; max-width: none; margin: 0; height: 720px;
  overflow: hidden; border-radius: 0; z-index: 1;
}
.hero .frame img { width: 100%; height: 100%; object-fit: cover; display: block; }
/* Home page hero: align photo to the right so the subject doesn't get cropped off.
   Subtle cool/desaturate filter neutralizes a yellow color cast in the photo. */
body.home .hero .frame img {
  object-position: right center;
  filter: hue-rotate(-8deg) saturate(0.82) brightness(1.02);
}
.hero .frame::after {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(10,10,10,0.20) 0%, rgba(10,10,10,0.40) 35%, rgba(10,10,10,0.75) 80%, rgba(10,10,10,0.85) 100%);
  pointer-events: none;
}
.hero .caption {
  position: absolute; left: 0; right: 0; bottom: 0; z-index: 2;
  max-width: 1320px; margin: 0 auto; padding: 0 80px 64px;
  box-sizing: border-box;
}
.hero .caption .eyebrow { color: #fff; opacity: 0.9; }
.hero .caption .hero-score { margin: 22px 0 0; text-align: left; display: flex; justify-content: flex-start; }
.hero .caption .hero-score:empty { display: none; }
/* Trustindex injects a full-width container with white bg behind a 245px badge,
   creating a white gap on the right. Shrink the container to fit content and
   override centering. ONLY positional/layout properties — never colors/typography. */
.hero .caption .hero-score .ti-widget-container {
  text-align: left !important; width: fit-content !important; max-width: 100% !important;
}
.hero .caption .hero-score .ti-widget { width: fit-content !important; max-width: 100% !important; }
.hero .caption .hero-score > * { margin-left: 0 !important; margin-right: auto !important; }
.hero .caption h1 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(40px, 4.6vw, 64px); line-height: 1.05;
  letter-spacing: -0.02em; color: #fff; margin: 0 0 14px; max-width: 720px;
}
.hero .caption .ingress {
  font-family: var(--font-sans); font-size: 17px; line-height: 1.55;
  color: rgba(255,255,255,0.9); margin: 0 0 22px; max-width: 540px;
}
.hero .bulletins { list-style: none; padding: 0; margin: 0 0 30px; display: flex; flex-direction: column; gap: 10px; }
.hero .bulletins li {
  font-family: var(--font-sans); font-size: 17px; font-weight: 500;
  color: rgba(255,255,255,0.97);
  display: flex; align-items: center; gap: 12px;
}
/* Check icon as ::before — keeps the icon out of the text content so
   `:empty` correctly hides cleared bullets. SVG is encoded inline as data URL. */
.hero .bulletins li::before {
  content: "";
  flex-shrink: 0; width: 20px; height: 20px;
  background-color: var(--blush-500);
  -webkit-mask-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><path d='M20 6L9 17l-5-5'/></svg>");
  mask-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><path d='M20 6L9 17l-5-5'/></svg>");
  -webkit-mask-size: contain; mask-size: contain;
  -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
}
/* Hide bulletin completely when the field was cleared in WP Admin. */
.hero .bulletins li:empty { display: none; }
/* Auto-hide standalone fields cleared in WP Admin so sections collapse cleanly. */
.hero .caption h1:empty,
.hero .caption .ingress:empty,
.hero .caption .eyebrow:empty,
.intro h2:empty,
.intro .ingress:empty,
.content-block h2:empty,
.content-block .text p:empty,
.text-blocks .item:has(h3:empty),
.faq details:has(summary:empty) { display: none; }
.hero .buttons { display: flex; gap: 12px; flex-wrap: wrap; }
.hero .buttons .btn-ghost { color: #fff; border-color: rgba(255,255,255,0.7); }
.hero .buttons .btn-ghost:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* Intro */
.intro { padding: 96px 0 0; text-align: center; }
.intro h2 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(30px, 3vw, 44px); line-height: 1.2;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 auto 18px; max-width: 720px;
}
.intro .ingress {
  font-family: var(--font-sans); font-size: 17px; line-height: 1.65;
  color: var(--fg); margin: 0 auto; max-width: 600px;
}

/* Treatments grid */
.treatments { padding: 80px 0; }
.treatments .eyebrow { display: block; margin-bottom: 28px; text-align: center; }
.treatments .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.treatments .card {
  position: relative; aspect-ratio: 1; border-radius: var(--radius-sm);
  overflow: hidden; display: block; text-decoration: none;
  transition: transform var(--dur-base) var(--ease-out);
}
.treatments .card:hover { transform: translateY(-2px); }
.treatments .card img { width: 100%; height: 100%; object-fit: cover; }
.treatments .card .overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.45) 100%);
}
.treatments .card .label {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-sans); font-size: 12px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: #fff; text-align: center; padding: 20px; line-height: 1.3;
}
/* Arrow indicator on card hover — hint that the card is clickable. */
.treatments .card .card-arrow {
  position: absolute; bottom: 16px; right: 16px;
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(255,255,255,0.95); color: var(--ink-700);
  display: inline-flex; align-items: center; justify-content: center;
  opacity: 0; transform: translateY(4px);
  transition: opacity var(--dur-fast) var(--ease-standard),
    transform var(--dur-fast) var(--ease-standard);
}
.treatments .card:hover .card-arrow { opacity: 1; transform: translateY(0); }

/* Content blocks */
.content-block { padding: 96px 0; }
.content-block .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: center; }
.content-block.mirror .grid > .text { order: 2; }
.content-block.mirror .grid > .img { order: 1; }
.content-block h2 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 24px;
}
.content-block .text p {
  font-family: var(--font-sans); font-size: 16px; line-height: 1.7;
  color: var(--fg); margin: 0 0 18px; max-width: 54ch;
}
.content-block .text strong { color: var(--ink-700); font-weight: 600; }
.content-block .img {
  width: 100%; aspect-ratio: 4/5; overflow: hidden;
  border-radius: var(--radius-sm); background: var(--blush-100);
}
.content-block .img img { width: 100%; height: 100%; object-fit: cover; }
.content-block .buttons { margin-top: 32px; }

/* Text blocks */
.text-blocks { padding: 96px 0; background: #fff; }
.text-blocks .inner { max-width: 860px; margin: 0 auto; padding: 0 32px; }
.text-blocks .item { padding: 36px 0; border-top: 1px solid var(--border); }
.text-blocks .item:first-child { border-top: none; padding-top: 0; }
.text-blocks .item:empty { display: none; }
.text-blocks h3 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: 26px; line-height: 1.2; letter-spacing: -0.01em;
  color: var(--ink-700); margin: 0 0 14px;
}
.text-blocks .item p {
  font-family: var(--font-sans); font-size: 16px; line-height: 1.7;
  color: var(--fg); margin: 0; max-width: 60ch;
}
.text-blocks .item strong { color: var(--ink-700); font-weight: 600; }
.text-blocks .item .eyebrow { display: block; margin-bottom: 8px; }

/* Contact panel */
.contact-panel { background: var(--blush-200); padding: 96px 0; }
.contact-panel .inner {
  max-width: 1100px; margin: 0 auto; padding: 0 32px;
  display: grid; grid-template-columns: 1fr 1.4fr; gap: 80px;
}
.contact-panel h3 {
  font-family: var(--font-sans); font-size: 18px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.18em; color: var(--ink-700);
  margin: 0 0 22px;
}
.contact-panel .line {
  font-family: var(--font-sans); font-size: 14px; color: var(--blush-700); margin-bottom: 8px;
  display: flex; align-items: center; gap: 10px;
}
.contact-panel .line a { color: var(--blush-700); text-decoration: underline; text-underline-offset: 3px; }
.contact-panel .line .ico {
  flex-shrink: 0; color: var(--blush-500);
  display: inline-flex; align-items: center; justify-content: center;
}
.contact-panel .line .ico svg { display: block; }
.contact-panel .row {
  display: flex; justify-content: space-between; padding: 6px 0;
  font-family: var(--font-sans); font-size: 14px; color: var(--ink-600);
  text-transform: uppercase; letter-spacing: 0.06em; max-width: 280px;
}
.contact-panel .row .day { color: var(--fg-muted); }
.contact-panel .hours { white-space: pre-line; font-family: var(--font-sans); font-size: 14px; color: var(--ink-600); line-height: 1.9; }
.contact-panel .intro-text { font-family: var(--font-sans); font-size: 15px; line-height: 1.65; color: var(--ink-600); margin: 0 0 24px; max-width: 520px; }

/* Map section */
.map-section { padding: 96px 0; background: #fff; }
.map-section .inner { max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px; text-align: center; }
.map-section .eyebrow { display: inline-block; margin-bottom: 16px; }
.map-section h2 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 14px;
}
.map-section .ingress {
  font-family: var(--font-sans); font-size: 16px; line-height: 1.65;
  color: var(--fg); margin: 0 auto 36px; max-width: 540px;
}
.map-section .map-frame {
  position: relative; width: 100%; aspect-ratio: 16/9;
  border-radius: var(--radius-sm); overflow: hidden;
  border: 1px solid var(--border); background: var(--paper);
}
.map-section .map-frame iframe {
  position: absolute; inset: 0; width: 100%; height: 100%; border: 0;
  display: block; background: transparent;
}

/* FAQ */
.faq { padding: 96px 0; background: var(--paper); }
.faq .inner { max-width: 860px; margin: 0 auto; padding: 0 32px; }
.faq .eyebrow { display: block; text-align: center; }
.faq h2 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); text-align: center;
  margin: 0 0 48px;
}
.faq details { border-top: 1px solid var(--border); padding: 22px 0; }
.faq details:last-of-type { border-bottom: 1px solid var(--border); }
.faq details:has(summary:empty) { display: none; }
.faq summary {
  list-style: none; cursor: pointer;
  font-family: var(--font-sans); font-size: 17px; font-weight: 500;
  color: var(--ink-700); display: flex; justify-content: space-between; align-items: center;
}
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: "+"; color: var(--blush-600); font-size: 22px; font-weight: 300; }
.faq details[open] summary::after { content: "−"; }
.faq details p { font-family: var(--font-sans); font-size: 15px; line-height: 1.7; color: var(--fg); margin: 14px 0 0; max-width: 60ch; }

/* Reviews */
.reviews-section { padding: 96px 0; background: var(--blush-50); }
.reviews-section .inner { max-width: var(--maxw-content); margin: 0 auto; padding: 0 32px; text-align: center; }
.reviews-section h2 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 14px;
}
.reviews-section .ingress {
  font-family: var(--font-sans); font-size: 16px; line-height: 1.65;
  color: var(--fg); margin: 0 auto 36px; max-width: 540px;
}

/* Contact panel — when paired with a form, give the form the wider column. */
.contact-panel-with-form .inner { grid-template-columns: 1fr 1.2fr; }
.contact-panel-with-form .cf-info h3 { color: var(--ink-700); }
.contact-panel-with-form .cf-form { background: #fff; padding: 32px; border-radius: var(--radius-sm); }

/* Contact form */
.contact-form-section { padding: 96px 0; background: #fff; }
.contact-form-section .inner {
  max-width: 1100px; margin: 0 auto; padding: 0 32px;
  display: grid; grid-template-columns: 1fr 1.2fr; gap: 64px;
  align-items: start;
}
.contact-form-section .cf-text h2 {
  font-family: var(--font-serif); font-weight: 500;
  font-size: clamp(28px, 2.6vw, 40px); line-height: 1.15;
  letter-spacing: -0.02em; color: var(--ink-700); margin: 0 0 14px;
}
.contact-form-section .cf-text .ingress {
  font-family: var(--font-sans); font-size: 16px; line-height: 1.65;
  color: var(--ink-600); margin: 0 0 16px; max-width: 38ch;
}
.cf-form { display: flex; flex-direction: column; gap: 18px; }
.cf-field { display: flex; flex-direction: column; gap: 6px; }
.cf-field label {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--ink-600);
}
.cf-field .cf-optional { text-transform: none; letter-spacing: 0; color: var(--fg-muted); font-weight: 400; }
.cf-field input, .cf-field textarea {
  font-family: var(--font-sans); font-size: 15px; color: var(--ink-700);
  background: #fff; border: 1px solid var(--ink-100);
  border-radius: var(--radius-sm); padding: 14px 16px;
  transition: border-color var(--dur-fast) var(--ease-standard),
    box-shadow var(--dur-fast) var(--ease-standard);
  width: 100%; box-sizing: border-box;
}
.cf-field input:focus, .cf-field textarea:focus {
  outline: none; border-color: var(--blush-500);
  box-shadow: 0 0 0 3px rgba(212, 136, 158, 0.15);
}
.cf-field textarea { resize: vertical; min-height: 120px; line-height: 1.5; }
.cf-honeypot { position: absolute; left: -9999px; opacity: 0; pointer-events: none; }
.cf-submit { align-self: flex-start; margin-top: 8px; }
.cf-submit:disabled { opacity: 0.6; cursor: wait; }
.cf-status { font-family: var(--font-sans); font-size: 14px; min-height: 22px; }
.cf-status.sending { color: var(--ink-500); }
.cf-status.success { color: var(--success); }
.cf-status.error { color: var(--danger); }

/* Responsive */
@media (max-width: 900px) {
  .content-block .grid { grid-template-columns: 1fr; gap: 32px; }
  .content-block.mirror .grid > .text { order: 1; }
  .content-block.mirror .grid > .img { order: 2; }
  .treatments .grid { grid-template-columns: repeat(2, 1fr); }
  .contact-panel .inner { grid-template-columns: 1fr; gap: 48px; }
  .contact-form-section .inner { grid-template-columns: 1fr; gap: 32px; }
  .hero .frame { height: 740px; }
  .hero .caption { padding: 0 32px 40px; }
  .hero .caption h1 { font-size: clamp(32px, 7vw, 44px); }
  .site-footer .columns { grid-template-columns: 1fr 1fr; gap: 40px; }
  .site-footer .brand { grid-column: 1 / -1; margin-bottom: 8px; }

  .site-header .hamburger { display: flex; }
  .site-header nav {
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
  }
  .site-header nav ul { flex-direction: column; gap: 0; align-items: stretch; }
  /* Mobile: sub-menus expand inline under parent (no hover/click), indented. */
  .site-header nav .sub-menu {
    display: flex !important; position: static; box-shadow: none; border: none;
    padding: 4px 0 8px; min-width: 0; background: transparent; border-radius: 0;
  }
  .site-header nav .sub-menu li a {
    padding: 10px 4px 10px 24px !important;
    font-size: 10px !important; letter-spacing: 0.18em;
    color: var(--ink-500); border-bottom: none !important;
    text-transform: uppercase;
  }
  .site-header nav .sub-menu li a::before {
    content: "›"; margin-right: 8px; color: var(--blush-500); font-weight: 600;
  }
  .site-header nav li.menu-item-has-children > a::after { content: ""; }
  .site-header .nav-toggle:checked ~ nav {
    max-height: 640px; opacity: 1; pointer-events: auto;
    padding: 12px 24px 28px;
  }
  .site-header nav a, .site-header nav ul li a {
    padding: 16px 4px; border-bottom: 1px solid var(--border);
    font-size: 12px; display: block;
  }
  .site-header nav ul li:last-child a { border-bottom: none; }
  .site-header nav a.btn-primary {
    margin-top: 14px; padding: 14px 20px; text-align: center;
    border-bottom: none; border-radius: 999px;
  }

  /* Tablet: behåll horisontell padding på alla containrar/wrappers — section
     rules ovan använder shorthand `padding: Npx 0` som annars skulle nollställa
     left/right. Placeras SIST så longhand vinner cascade-kampen. */
  .container,
  .text-blocks .inner,
  .contact-panel .inner,
  .faq .inner,
  .map-section .inner,
  .reviews-section .inner,
  .contact-form-section .inner {
    padding-left: 32px; padding-right: 32px;
  }
}
@media (max-width: 600px) {
  .site-header .inner { padding: 14px 20px; }
  .site-header .logo svg { height: 46px; }

  /* Apply consistent horizontal padding to all content containers on mobile.
     Hero is excluded — it has its own caption padding and full-bleed photo. */
  .hero .frame { height: 680px; border-radius: 0; }
  .hero .caption { padding: 0 24px 32px; }
  .hero .caption h1 { font-size: clamp(38px, 9vw, 48px); line-height: 1.05; margin-bottom: 14px; }
  .hero .caption .ingress { font-size: 15px; margin-bottom: 18px; }
  .hero .bulletins { margin-bottom: 24px; gap: 8px; }
  .hero .bulletins { gap: 12px; }
  .hero .bulletins li { font-size: 18px; font-weight: 500; }
  .hero .bulletins li::before { width: 22px; height: 22px; }
  .hero .buttons { justify-content: center; }
  .hero .buttons .btn-row { width: 100%; justify-content: center; gap: 10px; }
  .hero .buttons .btn-primary, .hero .buttons .btn-ghost {
    flex: 1 1 0; text-align: center; padding: 15px 20px; font-size: 14px;
    min-width: 0;
  }
  /* Center CTA buttons inside content sections on mobile (hero handled separately above). */
  .content-block .btn-row,
  .content-block .buttons,
  .text-blocks .btn-row,
  .contact-panel .btn-row,
  .map-section .btn-row,
  .reviews-section .btn-row,
  .intro .btn-row { justify-content: center; }
  .hero .buttons .btn-ghost { background: rgba(255,255,255,0.95); color: var(--ink-700); border-color: rgba(255,255,255,0.95); }
  .hero .buttons .btn-ghost:hover { background: #fff; color: var(--ink-900); }
  .hero .caption .hero-score { justify-content: center; text-align: center; }
  .hero .caption .hero-score > * { margin-left: auto !important; margin-right: auto !important; }
  .intro { padding: 64px 0 0; }
  .treatments { padding: 56px 0; }
  .treatments .grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .content-block { padding: 64px 0; }
  .text-blocks { padding: 64px 0; }
  .contact-panel { padding: 64px 0; }
  .faq { padding: 64px 0; }
  .map-section { padding: 64px 0; }
  .map-section .map-frame { aspect-ratio: 4/5; }
  .reviews-section { padding: 64px 0; }
  .site-footer { padding: 56px 0 24px; }
  .site-footer .columns { grid-template-columns: 1fr; gap: 36px; padding: 0 24px; }
  .site-footer .legal { flex-direction: column; align-items: flex-start; gap: 14px; margin-top: 36px; padding: 24px 24px 0; }
  .site-footer .legal nav { gap: 18px; }

  /* Horizontal padding on every content container — placed LAST so the longhand
     overrides any earlier `padding: Npx 0` shorthand on the section rules. */
  .container,
  .text-blocks .inner,
  .contact-panel .inner,
  .faq .inner,
  .map-section .inner,
  .reviews-section .inner,
  .contact-form-section .inner {
    padding-left: 20px; padding-right: 20px;
  }
}
"""

CHECK_ICON = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20 6L9 17l-5-5"/></svg>'
)

# Stroked outline icons matching the LumoKit aesthetic. All use currentColor so
# they inherit text color where they're placed.
ICON_PHONE = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 '
    '19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 '
    '2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 '
    '9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 '
    '2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
)
ICON_MAIL = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>'
    '<polyline points="22,6 12,13 2,6"/></svg>'
)
ICON_PIN = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
    '<circle cx="12" cy="10" r="3"/></svg>'
)
ICON_CLOCK = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>'
)
ICON_ARROW = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12,5 19,12 12,19"/></svg>'
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collapse(html: str) -> str:
    """Collapse multi-line HTML to a single line (newlines -> space, trim runs)."""
    # Preserve newlines inside <style> by replacing them with spaces first.
    out = " ".join(html.split())
    return out


def img_url(manifest: dict, image_id: str) -> str:
    if not image_id:
        return ""
    if image_id in manifest:
        return manifest[image_id]["source_url"]
    return ""


def make_variant(base_component: dict, suffix: str, content: dict, title_suffix: str = "") -> dict:
    """Clone a base component with a new block_name and bake content into schema defaults.

    `suffix` becomes appended to the block_name (e.g. 'hem' -> lumo/hero-hem).
    `content` is a dict of {field_name: value} that overrides the field's `default`.
    Fields not present in `content` keep whatever default the base component has.
    """
    import copy
    variant = copy.deepcopy(base_component)
    base_name = variant["block_name"]  # e.g. lumo/hero
    variant["block_name"] = f"{base_name}-{suffix}"
    if title_suffix:
        variant["title"] = f"{variant['title']} – {title_suffix}"
    for field in variant["schema"]:
        if field["name"] in content:
            field["default"] = content[field["name"]]
    return variant


# ---------------------------------------------------------------------------
# Component templates
# ---------------------------------------------------------------------------

def build_site_header_component(tokens_css: str, logo_svg: str) -> dict:
    # Preconnect + preload — laddar Google Fonts parallellt med HTML så att
    # Cormorant Garamond + Outfit hinner vara klara innan första paint.
    font_preload = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Outfit:wght@400;500;600&display=swap">
"""
    style_block = f"<style>\n{tokens_css}\n{LAYOUT_CSS}\n</style>"
    onload_script = """<script>
(function(){
  var done = false;
  function reveal(){ if (done) return; done = true; document.body.classList.add('lumo-loaded'); }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(reveal);
  if (document.readyState !== 'loading') { reveal(); }
  else document.addEventListener('DOMContentLoaded', reveal);
  setTimeout(reveal, 600);
})();
</script>"""
    html = f"""
{font_preload}
{style_block}
{onload_script}
<header class="site-header">
  <div class="inner">
    <a href="/" class="logo" aria-label="{{{{site_company_name}}}}">{logo_svg}</a>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-hidden="true">
    <label for="nav-toggle" class="hamburger" aria-label="Öppna meny">
      <span></span><span></span><span></span>
    </label>
    <nav>
      {{{{lumokit-primary}}}}
      <a href="#tdl-booking-widget" class="btn-primary" style="padding:12px 22px;">Boka tid</a>
    </nav>
  </div>
</header>
"""
    return {
        "block_name": "lumo/site-header",
        "title": "Sidhuvud",
        "html_template": collapse(html),
        "schema": [
            {"name": "lumokit-primary", "type": "nav_menu", "label": "Primär meny"},
        ],
    }


def build_site_footer_component(logo_svg: str) -> dict:
    html = f"""
<footer class="site-footer">
  <div class="columns">
    <div class="brand">
      <a href="/" class="logo" aria-label="{{{{site_company_name}}}}">{logo_svg}</a>
      <p class="tagline">{{{{tagline}}}}</p>
    </div>
    <div class="treatments-col">
      <h4>Behandlingar</h4>
      <ul>
        <li><a href="/tandimplantat">Tandimplantat</a></li>
        <li><a href="/invisalign">Invisalign</a></li>
        <li><a href="/akuttandvard">Akuttandvård</a></li>
        <li><a href="/basundersokning">Basundersökning</a></li>
        <li><a href="/allman-tandvard">Allmän tandvård</a></li>
        <li><a href="/tandvardsradsla">Tandvårdsrädsla</a></li>
      </ul>
    </div>
    <div>
      <h4>Sajt</h4>
      <ul>
        <li><a href="/">Hem</a></li>
        <li><a href="/om-oss">Om oss</a></li>
        <li><a href="/kontakt">Kontakt</a></li>
        <li><a href="#tdl-booking-widget">Boka tid</a></li>
      </ul>
    </div>
    <div class="contact">
      <h4>Kontakt</h4>
      <div class="row">
        <span class="label"><span class="ico">{ICON_PHONE}</span> Telefon</span>
        <a href="tel:{{{{site_phone}}}}">{{{{site_phone}}}}</a>
      </div>
      <div class="row">
        <span class="label"><span class="ico">{ICON_MAIL}</span> E-post</span>
        <a href="mailto:{{{{site_email}}}}">{{{{site_email}}}}</a>
      </div>
      <div class="row">
        <span class="label"><span class="ico">{ICON_PIN}</span> Besöksadress</span>
        <a href="https://maps.google.com/?q={PATRICIA_ADDRESS_ENCODED}" target="_blank" rel="noopener">{{{{site_address}}}}</a>
      </div>
    </div>
  </div>
  <div class="legal">
    <div>{{{{copyright_text}}}}</div>
    <nav>
      <a href="/integritetspolicy">Integritetspolicy</a>
      <a href="/cookies">Cookies</a>
    </nav>
  </div>
</footer>
"""
    return {
        "block_name": "lumo/site-footer",
        "title": "Sidfot",
        "html_template": collapse(html),
        "schema": [
            {"name": "tagline", "type": "textarea", "label": "Footer-beskrivning",
             "default": "Modern tandvård i centrala Stockholm — för en frisk mun och ett strålande leende."},
            {"name": "copyright_text", "type": "text", "label": "Copyright-text",
             "default": "© 2026 Patricia Teles"},
        ],
    }


def build_hero_component() -> dict:
    """Universal hero. Bulletins are individual fields so empty ones can hide."""
    bulletins_html = ""
    for i in range(1, 5):
        bulletins_html += f"""<li>{{{{bulletin_{i}}}}}</li>"""

    html = f"""
<section class="hero">
  <div class="halo"></div>
  <div class="frame"><img src="{{{{hero_image}}}}" alt=""/></div>
  <div class="caption">
    <div class="eyebrow">{{{{eyebrow}}}}</div>
    <h1>{{{{headline}}}}</h1>
    <p class="ingress">{{{{ingress}}}}</p>
    <ul class="bulletins">{bulletins_html}</ul>
    <div class="buttons">
      <div class="btn-row">
        <a href="#tdl-booking-widget" class="btn-primary">{{{{cta_primary_text}}}}</a>
        <a href="{{{{cta_secondary_link}}}}" class="btn-ghost">{{{{cta_secondary_text}}}}</a>
      </div>
    </div>
    <div class="hero-score">{{{{site_reviews_score}}}}</div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/hero",
        "title": "Hero",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow", "type": "text", "label": "Etikett"},
            {"name": "headline", "type": "text", "label": "Huvudrubrik"},
            {"name": "ingress", "type": "textarea", "label": "Ingress"},
            {"name": "bulletin_1", "type": "text", "label": "Bullet 1"},
            {"name": "bulletin_2", "type": "text", "label": "Bullet 2"},
            {"name": "bulletin_3", "type": "text", "label": "Bullet 3"},
            {"name": "bulletin_4", "type": "text", "label": "Bullet 4"},
            {"name": "cta_primary_text", "type": "text", "label": "Primär CTA-text", "default": "Boka tid"},
            {"name": "cta_secondary_text", "type": "text", "label": "Sekundär CTA-text", "default": "Ring oss"},
            {"name": "cta_secondary_link", "type": "url", "label": "Sekundär CTA-länk", "default": "tel:{{site_phone}}"},
            {"name": "hero_image", "type": "image", "label": "Bakgrundsbild"},
        ],
    }


def build_intro_component() -> dict:
    html = """
<section class="intro container">
  <span class="eyebrow">{{eyebrow}}</span>
  <h2>{{h2}}</h2>
  <p class="ingress">{{body}}</p>
</section>
"""
    return {
        "block_name": "lumo/intro",
        "title": "Intro",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow", "type": "text", "label": "Etikett"},
            {"name": "h2", "type": "text", "label": "Rubrik"},
            {"name": "body", "type": "textarea", "label": "Brödtext"},
        ],
    }


def build_treatments_grid_component() -> dict:
    cards = ""
    for i in range(1, 7):
        cards += (
            f'<a href="{{{{card_{i}_url}}}}" class="card">'
            f'<img src="{{{{card_{i}_image}}}}" alt="{{{{card_{i}_name}}}}"/>'
            f'<div class="overlay"></div>'
            f'<div class="label">{{{{card_{i}_name}}}}</div>'
            f'<span class="card-arrow" aria-hidden="true">{ICON_ARROW}</span>'
            f'</a>'
        )

    html = f"""
<section class="treatments container">
  <span class="eyebrow">{{{{title}}}}</span>
  <div class="grid">{cards}</div>
</section>
"""
    schema = [{"name": "title", "type": "text", "label": "Sektionstitel", "default": "Våra behandlingar"}]
    for i in range(1, 7):
        schema.append({"name": f"card_{i}_name", "type": "text", "label": f"Kort {i} – namn"})
        schema.append({"name": f"card_{i}_image", "type": "image", "label": f"Kort {i} – bild"})
        schema.append({"name": f"card_{i}_summary", "type": "textarea", "label": f"Kort {i} – kort text"})
        schema.append({"name": f"card_{i}_url", "type": "url", "label": f"Kort {i} – länk"})

    return {
        "block_name": "lumo/treatments-grid",
        "title": "Behandlingar – grid",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_content_block_component(block_name: str, title: str, mirror: bool) -> dict:
    cls = "content-block container" + (" mirror" if mirror else "")
    html = f"""
<section class="{cls}">
  <div class="grid">
    <div class="text">
      <span class="eyebrow">{{{{eyebrow}}}}</span>
      <h2>{{{{h2}}}}</h2>
      <div>{{{{body}}}}</div>
      <div class="buttons">
        <div class="btn-row">
          <a href="{{{{cta_link}}}}" class="btn-primary">{{{{cta_text}}}}</a>
        </div>
      </div>
    </div>
    <div class="img"><img src="{{{{image}}}}" alt=""/></div>
  </div>
</section>
"""
    return {
        "block_name": block_name,
        "title": title,
        "html_template": collapse(html),
        "schema": [
            {"name": "image", "type": "image", "label": "Bild"},
            {"name": "eyebrow", "type": "text", "label": "Etikett"},
            {"name": "h2", "type": "text", "label": "Rubrik"},
            {"name": "body", "type": "textarea", "label": "Brödtext (HTML tillåten)"},
            {"name": "cta_text", "type": "text", "label": "CTA-text", "default": "Boka tid"},
            {"name": "cta_link", "type": "url", "label": "CTA-länk", "default": "#tdl-booking-widget"},
        ],
    }


def build_text_blocks_component() -> dict:
    items = ""
    for i in range(1, 4):
        items += f'<div class="item"><span class="eyebrow">{{{{block_{i}_eyebrow}}}}</span><h3>{{{{block_{i}_h3}}}}</h3><div>{{{{block_{i}_body}}}}</div></div>'
    html = f"""
<section class="text-blocks">
  <div class="inner">{items}</div>
</section>
"""
    schema = []
    for i in range(1, 4):
        schema.append({"name": f"block_{i}_eyebrow", "type": "text", "label": f"Block {i} – etikett"})
        schema.append({"name": f"block_{i}_h3", "type": "text", "label": f"Block {i} – rubrik"})
        schema.append({"name": f"block_{i}_body", "type": "textarea", "label": f"Block {i} – text"})
    return {
        "block_name": "lumo/text-blocks",
        "title": "Textblock (2-3 kolumner)",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_contact_panel_component() -> dict:
    html = f"""
<section class="contact-panel">
  <div class="inner">
    <div>
      <span class="eyebrow">Telefon &amp; e-post</span>
      <h3>{{{{heading}}}}</h3>
      <p class="intro-text">{{{{intro_text}}}}</p>
      <div class="line"><span class="ico">{ICON_PHONE}</span><a href="tel:{{{{site_phone}}}}">{{{{site_phone}}}}</a></div>
      <div class="line"><span class="ico">{ICON_MAIL}</span><a href="mailto:{{{{site_email}}}}">{{{{site_email}}}}</a></div>
      <div class="line" style="margin-top:18px;"><span class="ico">{ICON_PIN}</span><a href="https://maps.google.com/?q={PATRICIA_ADDRESS_ENCODED}" target="_blank" rel="noopener">{{{{site_address}}}}</a></div>
    </div>
    <div>
      <span class="eyebrow"><span class="ico">{ICON_CLOCK}</span> När vi har öppet</span>
      <h3>Öppettider</h3>
      <div class="hours">{{{{opening_hours}}}}</div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/contact-panel",
        "title": "Kontaktpanel",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "Kontakta oss"},
            {"name": "intro_text", "type": "textarea", "label": "Introtext",
             "default": "Vi finns här för att svara på dina frågor och hjälpa dig med tidsbokning."},
            {"name": "opening_hours", "type": "textarea", "label": "Öppettider",
             "default": "Mån–Fre  08–18\nLördag  09–16\nSöndag  Stängt"},
        ],
    }


def build_faq_component() -> dict:
    rows = ""
    for i in range(1, 7):
        rows += f'<details><summary>{{{{q_{i}}}}}</summary><p>{{{{a_{i}}}}}</p></details>'
    html = f"""
<section class="faq">
  <div class="inner">
    <span class="eyebrow">Vanliga frågor</span>
    <h2>{{{{heading}}}}</h2>
    {rows}
  </div>
</section>
"""
    schema = [{"name": "heading", "type": "text", "label": "Rubrik", "default": "Frågor och svar"}]
    for i in range(1, 7):
        schema.append({"name": f"q_{i}", "type": "text", "label": f"Fråga {i}"})
        schema.append({"name": f"a_{i}", "type": "textarea", "label": f"Svar {i}"})
    return {
        "block_name": "lumo/faq",
        "title": "FAQ",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_map_section_component() -> dict:
    html = f"""
<section class="map-section">
  <div class="inner">
    <span class="eyebrow">Hitta hit</span>
    <h2>{{{{heading}}}}</h2>
    <p class="ingress">{{{{intro_text}}}}</p>
    <div class="map-frame">
      <iframe src="https://maps.google.com/maps?q={PATRICIA_ADDRESS_ENCODED}&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen title="Karta — Patricia Teles"></iframe>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/map-section",
        "title": "Kartsektion",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "Vägbeskrivning till kliniken"},
            {"name": "intro_text", "type": "textarea", "label": "Introtext",
             "default": "Du hittar oss centralt i Stockholm. Boka en tid eller kom in och hälsa på."},
        ],
    }


def build_reviews_section_component() -> dict:
    html = """
<section class="reviews-section">
  <div class="inner">
    <span class="eyebrow">Recensioner</span>
    <h2>{{heading}}</h2>
    <p class="ingress">{{intro_text}}</p>
    <div>{{site_reviews_testimonials}}</div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/reviews-section",
        "title": "Recensioner",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "Vad våra patienter säger"},
            {"name": "intro_text", "type": "textarea", "label": "Introtext",
             "default": "Verkliga upplevelser från riktiga patienter."},
        ],
    }


def build_contact_panel_with_form_component() -> dict:
    html = f"""
<section class="contact-panel contact-panel-with-form">
  <div class="inner">
    <div class="cf-info">
      <span class="eyebrow">Kontakta oss</span>
      <h3>{{{{heading}}}}</h3>
      <p class="intro-text">{{{{intro_text}}}}</p>
      <div class="line"><span class="ico">{ICON_PHONE}</span><a href="tel:{{{{site_phone}}}}">{{{{site_phone}}}}</a></div>
      <div class="line"><span class="ico">{ICON_MAIL}</span><a href="mailto:{{{{site_email}}}}">{{{{site_email}}}}</a></div>
      <div class="line" style="margin-top:18px;"><span class="ico">{ICON_PIN}</span><a href="https://maps.google.com/?q={PATRICIA_ADDRESS_ENCODED}" target="_blank" rel="noopener">{{{{site_address}}}}</a></div>
      <div class="line" style="margin-top:24px;"><span class="eyebrow" style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span class="ico">{ICON_CLOCK}</span> Öppettider</span><span class="hours">{{{{opening_hours}}}}</span></div>
    </div>
    <form class="cf-form" data-lumo-contact-form>
      <div class="cf-field">
        <label for="cf-name">Namn</label>
        <input type="text" id="cf-name" name="name" autocomplete="name" required>
      </div>
      <div class="cf-field">
        <label for="cf-email">E-post</label>
        <input type="email" id="cf-email" name="email" autocomplete="email" required>
      </div>
      <div class="cf-field">
        <label for="cf-phone">Telefon <span class="cf-optional">(valfri)</span></label>
        <input type="tel" id="cf-phone" name="phone" autocomplete="tel">
      </div>
      <div class="cf-field">
        <label for="cf-message">Meddelande</label>
        <textarea id="cf-message" name="message" rows="5" required></textarea>
      </div>
      <input type="text" name="website" class="cf-honeypot" tabindex="-1" autocomplete="off">
      <button type="submit" class="cf-submit btn-primary">Skicka meddelande</button>
      <div class="cf-status" role="status"></div>
    </form>
  </div>
</section>
<script>
(function(){{
  var form = document.querySelector('[data-lumo-contact-form]');
  if (!form) return;
  form.addEventListener('submit', function(e){{
    e.preventDefault();
    var status = form.querySelector('.cf-status');
    var btn = form.querySelector('.cf-submit');
    var data = {{ name: form.name.value, email: form.email.value, phone: form.phone.value, message: form.message.value, website: form.website.value }};
    btn.disabled = true; status.textContent = 'Skickar...'; status.className = 'cf-status sending';
    fetch('/wp-json/lumokit/v1/contact', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(data) }})
      .then(function(r){{return r.json().then(function(j){{return {{ok:r.ok,j:j}}}})}})
      .then(function(res){{
        if (res.ok && res.j.success) {{ status.textContent = 'Tack! Vi återkommer så snart vi kan.'; status.className = 'cf-status success'; form.reset(); }}
        else {{ status.textContent = (res.j && res.j.message) || 'Något gick fel. Försök igen eller ring oss.'; status.className = 'cf-status error'; }}
      }}).catch(function(){{ status.textContent = 'Något gick fel. Försök igen eller ring oss.'; status.className = 'cf-status error'; }})
      .finally(function(){{ btn.disabled = false; }});
  }});
}})();
</script>
"""
    return {
        "block_name": "lumo/contact-panel-with-form",
        "title": "Kontaktpanel + formulär",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "Kontakta oss"},
            {"name": "intro_text", "type": "textarea", "label": "Introtext",
             "default": "Fyll i formuläret eller hör av dig direkt — vi svarar inom kort."},
            {"name": "opening_hours", "type": "textarea", "label": "Öppettider",
             "default": "Mån–Fre  08–18\nLördag  09–16\nSöndag  Stängt"},
        ],
    }


def build_contact_form_component() -> dict:
    html = """
<section class="contact-form-section">
  <div class="inner">
    <div class="cf-text">
      <span class="eyebrow">Skriv till oss</span>
      <h2>{{heading}}</h2>
      <p class="ingress">{{intro_text}}</p>
    </div>
    <form class="cf-form" data-lumo-contact-form>
      <div class="cf-field">
        <label for="cf-name">Namn</label>
        <input type="text" id="cf-name" name="name" autocomplete="name" required>
      </div>
      <div class="cf-field">
        <label for="cf-email">E-post</label>
        <input type="email" id="cf-email" name="email" autocomplete="email" required>
      </div>
      <div class="cf-field">
        <label for="cf-phone">Telefon <span class="cf-optional">(valfri)</span></label>
        <input type="tel" id="cf-phone" name="phone" autocomplete="tel">
      </div>
      <div class="cf-field">
        <label for="cf-message">Meddelande</label>
        <textarea id="cf-message" name="message" rows="5" required></textarea>
      </div>
      <input type="text" name="website" class="cf-honeypot" tabindex="-1" autocomplete="off">
      <button type="submit" class="cf-submit btn-primary">Skicka meddelande</button>
      <div class="cf-status" role="status"></div>
    </form>
  </div>
</section>
<script>
(function(){
  var form = document.querySelector('[data-lumo-contact-form]');
  if (!form) return;
  form.addEventListener('submit', function(e){
    e.preventDefault();
    var status = form.querySelector('.cf-status');
    var btn = form.querySelector('.cf-submit');
    var data = {
      name: form.name.value, email: form.email.value,
      phone: form.phone.value, message: form.message.value,
      website: form.website.value
    };
    btn.disabled = true; status.textContent = 'Skickar...'; status.className = 'cf-status sending';
    fetch('/wp-json/lumokit/v1/contact', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(data)
    }).then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j}})})
      .then(function(res){
        if (res.ok && res.j.success) {
          status.textContent = 'Tack! Vi återkommer så snart vi kan.';
          status.className = 'cf-status success';
          form.reset();
        } else {
          status.textContent = (res.j && res.j.message) || 'Något gick fel. Försök igen eller ring oss.';
          status.className = 'cf-status error';
        }
      }).catch(function(){
        status.textContent = 'Något gick fel. Försök igen eller ring oss.';
        status.className = 'cf-status error';
      }).finally(function(){ btn.disabled = false; });
  });
})();
</script>
"""
    return {
        "block_name": "lumo/contact-form",
        "title": "Kontaktformulär",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "Skicka ett meddelande"},
            {"name": "intro_text", "type": "textarea", "label": "Introtext",
             "default": "Fyll i formuläret så hör vi av oss inom kort. Föredrar du att ringa? Vi svarar på {{site_phone}}."},
        ],
    }


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

HERO_EYEBROW = {
    "hem": "Patricia Teles · Stockholm",
    "om-oss": "Om oss",
    "kontakt": "Kontakt",
}
HERO_H1_OVERRIDE = {
    "hem": "Modern tandvård i centrala Stockholm",
    "om-oss": "Människorna bakom Patricia Teles",
    "kontakt": "Kom i kontakt med oss",
}


def hero_content(page: dict, manifest: dict) -> dict:
    s = page["sections"]["hero"]
    slug = page["slug"]
    bullets = (s.get("bulletins") or []) + ["", "", "", ""]
    return {
        "eyebrow": HERO_EYEBROW.get(slug, "Behandling"),
        "headline": HERO_H1_OVERRIDE.get(slug, s.get("h1", "")),
        "ingress": s.get("ingress", ""),
        "bulletin_1": bullets[0],
        "bulletin_2": bullets[1],
        "bulletin_3": bullets[2],
        "bulletin_4": bullets[3],
        "cta_primary_text": "Boka tid",
        "cta_secondary_text": "Ring oss",
        "cta_secondary_link": "tel:{{site_phone}}",
        "hero_image": img_url(manifest, s.get("bg_image_id", "")),
    }


def intro_content(page: dict) -> dict:
    s = page["sections"].get("intro", {})
    return {
        "eyebrow": "Översikt",
        "h2": s.get("h2", ""),
        "body": s.get("ingress", ""),
    }


def cb1_content(page: dict, manifest: dict, eyebrow: str = "Vår klinik") -> dict:
    b = page["sections"].get("content_block_1", {})
    return {
        "image": img_url(manifest, b.get("image_1_id", "")),
        "eyebrow": eyebrow,
        "h2": b.get("h2", ""),
        "body": b.get("text_html", ""),
        "cta_text": "Boka tid",
        "cta_link": "#tdl-booking-widget",
    }


def cb2_content(page: dict, manifest: dict, eyebrow: str = "Så jobbar vi") -> dict:
    b = page["sections"].get("content_block_2", {})
    # cb2 in source data has no image — fall back to image_2_id from cb1
    cb1 = page["sections"].get("content_block_1", {})
    image = img_url(manifest, cb1.get("image_2_id", ""))
    body = b.get("text_html", "")
    if b.get("h3") and b.get("subtext_html"):
        body += f"<h3 style='margin-top:24px;font-family:var(--font-sans);font-size:18px;text-transform:uppercase;letter-spacing:0.18em;'>{b['h3']}</h3>{b['subtext_html']}"
    return {
        "image": image,
        "eyebrow": eyebrow,
        "h2": b.get("h2", ""),
        "body": body,
        "cta_text": "Boka tid",
        "cta_link": "#tdl-booking-widget",
    }


def treatments_grid_content(page: dict, manifest: dict) -> dict:
    items = page["sections"].get("treatments_section", []) or []
    out = {"title": "Våra behandlingar"}
    # Determine slug from link to find image_id
    slug_to_image = {
        "tandimplantat": "tandimplantat-bg.jpg",
        "invisalign": "invisalign-bg.jpg",
        "akuttandvard": "akuttandvard-bg.jpg",
        "basundersokning": "basundersokning-bg.jpg",
        "allman-tandvard": "allman-tandvard-bg.jpg",
        "tandvardsradsla": "tandvardsradsla-bg.jpg",
    }
    for i, it in enumerate(items[:6], start=1):
        link = (it.get("link", "") or "").lstrip("/")
        img_key = it.get("image_id") or ""
        if img_key not in manifest:
            img_key = slug_to_image.get(link, "")
        out[f"card_{i}_name"] = it.get("title", "")
        out[f"card_{i}_image"] = img_url(manifest, img_key)
        out[f"card_{i}_summary"] = ""
        out[f"card_{i}_url"] = "/" + link if link else "#"
    return out


def text_blocks_content(page: dict) -> dict:
    blocks = page["sections"].get("text_blocks", []) or []
    out = {}
    for i in range(1, 4):
        b = blocks[i - 1] if i - 1 < len(blocks) else {}
        out[f"block_{i}_eyebrow"] = ""
        out[f"block_{i}_h3"] = b.get("h3", "")
        out[f"block_{i}_body"] = b.get("text_html", "")
    return out


def faq_content(page: dict) -> dict:
    items = page["sections"].get("faq", []) or []
    out = {"heading": "Frågor och svar"}
    for i in range(1, 7):
        b = items[i - 1] if i - 1 < len(items) else {}
        out[f"q_{i}"] = b.get("question", "")
        out[f"a_{i}"] = b.get("answer", "")
    return out


def contact_panel_content(page: dict) -> dict:
    s = page["sections"].get("contact_block", {})
    return {
        "heading": s.get("h2", "Kontakta oss") or "Kontakta oss",
        "intro_text": (
            # strip HTML for the textarea field; keep first sentence
            s.get("text_html", "")
             .replace("<p>", "").replace("</p>", "")
             .replace("<strong>", "").replace("</strong>", "")
             if s else "Vi finns här för att svara på dina frågor och hjälpa dig med tidsbokning."
        ),
        "opening_hours": "Mån–Fre  08–18\nLördag  09–16\nSöndag  Stängt",
    }


# ---------------------------------------------------------------------------
# Build pages
# ---------------------------------------------------------------------------

def build_site(content: dict, manifest: dict, base_components: dict) -> tuple[list, list]:
    """Returns (variant_components, pages).

    For each page, builds one variant component per page-specific block. Variant
    block names are `<base>-<slug>` (e.g. `lumo/hero-hem`). Shared components
    (site-header, site-footer) are referenced unchanged.
    """
    pages_in = {p["slug"]: p for p in content["pages"]}
    variants: list = []
    out_pages: list = []
    seen_names: set = set()

    def add(base_key: str, suffix: str, content_overrides: dict, title_suffix: str = "") -> str:
        v = make_variant(base_components[base_key], suffix, content_overrides, title_suffix)
        if v["block_name"] in seen_names:
            return v["block_name"]
        seen_names.add(v["block_name"])
        variants.append(v)
        return v["block_name"]

    default_hours = "Mån–Fre  08–18\nLördag  09–16\nSöndag  Stängt"
    default_contact = {
        "heading": "Kontakta oss",
        "intro_text": "Vi finns här för att svara på dina frågor och hjälpa dig med tidsbokning.",
        "opening_hours": default_hours,
    }

    # --- Hem ---
    hem = pages_in["hem"]
    blocks = [
        "lumo/site-header",
        add("hero", "hem", hero_content(hem, manifest), "Hem"),
        add("intro", "hem", intro_content(hem), "Hem"),
        add("treatments-grid", "hem", treatments_grid_content(hem, manifest), "Hem"),
        add("content-block-1", "hem", cb1_content(hem, manifest, eyebrow="Vår klinik"), "Hem"),
        add("reviews-section", "hem", {
            "heading": "Vad våra patienter säger",
            "intro_text": "Verkliga upplevelser från riktiga patienter.",
        }, "Hem"),
        add("contact-panel", "hem", default_contact, "Hem"),
        "lumo/site-footer",
    ]
    out_pages.append({"title": "Hem", "slug": "hem", "menu_label": None, "blocks": blocks})

    # --- Om oss ---
    om = pages_in["om-oss"]
    blocks = [
        "lumo/site-header",
        add("hero", "om-oss", hero_content(om, manifest), "Om oss"),
        add("intro", "om-oss", {
            "eyebrow": "Vår filosofi",
            "h2": "Tandvård med hjärta och precision",
            "body": "Vi tror på en tandvård där varje patient är i centrum.",
        }, "Om oss"),
        add("content-block-1", "om-oss", cb1_content(om, manifest, eyebrow="Om oss"), "Om oss"),
        add("content-block-2", "om-oss", {
            "image": img_url(manifest, om["sections"].get("content_block_1", {}).get("image_2_id", "")),
            "eyebrow": "Trygghet",
            "h2": "Trygghet för dig med tandvårdsrädsla",
            "body": "<p>Vi förstår att tandvårdsrädsla är vanligt, och vi är specialiserade på att möta dig med <strong>extra omtanke och förståelse</strong>. Vi tar oss extra tid, förklarar varje steg noggrant och anpassar behandlingen efter din takt.</p>",
            "cta_text": "Läs mer",
            "cta_link": "/tandvardsradsla",
        }, "Om oss"),
        add("text-blocks", "om-oss", text_blocks_content(om), "Om oss"),
        add("map-section", "om-oss", {
            "heading": "Kom förbi vår klinik",
            "intro_text": "Du hittar oss centralt i Stockholm. Boka en tid eller kom in och hälsa på.",
        }, "Om oss"),
        add("contact-panel", "om-oss", default_contact, "Om oss"),
        "lumo/site-footer",
    ]
    out_pages.append({"title": "Om oss", "slug": "om-oss", "menu_label": "Om oss", "blocks": blocks})

    # --- Kontakt ---
    k = pages_in["kontakt"]
    blocks = [
        "lumo/site-header",
        add("hero", "kontakt", hero_content(k, manifest), "Kontakt"),
        add("contact-panel-with-form", "kontakt", {
            "heading": "Kontakta oss",
            "intro_text": "Fyll i formuläret eller hör av dig direkt — vi svarar inom kort.",
            "opening_hours": "Mån–Fre  08–18\nLördag  09–16\nSöndag  Stängt",
        }, "Kontakt"),
        add("map-section", "kontakt", {
            "heading": "Vägbeskrivning till kliniken",
            "intro_text": "Du hittar oss centralt i Stockholm.",
        }, "Kontakt"),
        "lumo/site-footer",
    ]
    out_pages.append({"title": "Kontakt", "slug": "kontakt", "menu_label": "Kontakt", "blocks": blocks})

    # --- 6 treatment pages ---
    treatment_slugs = ["tandimplantat", "invisalign", "akuttandvard",
                       "basundersokning", "allman-tandvard", "tandvardsradsla"]
    treatment_menu_labels = {
        "tandimplantat": "Tandimplantat",
        "invisalign": "Invisalign",
        "akuttandvard": "Akuttandvård",
        "basundersokning": "Basundersökning",
        "allman-tandvard": "Allmän tandvård",
        "tandvardsradsla": "Tandvårdsrädsla",
    }
    for slug in treatment_slugs:
        page = pages_in[slug]
        blocks = [
            "lumo/site-header",
            add("hero", slug, hero_content(page, manifest), slug),
            add("intro", slug, intro_content(page), slug),
            add("content-block-1", slug, cb1_content(page, manifest, eyebrow="Behandling"), slug),
            add("content-block-2", slug, cb2_content(page, manifest, eyebrow="Processen"), slug),
            add("faq", slug, faq_content(page), slug),
            add("contact-panel", slug, {
                "heading": "Kontakta oss",
                "intro_text": "Har du frågor om behandlingen? Vi hjälper dig gärna.",
                "opening_hours": default_hours,
            }, slug),
            "lumo/site-footer",
        ]
        out_pages.append({
            "title": page["sections"]["hero"]["h1"],
            "slug": slug,
            "menu_label": treatment_menu_labels[slug],
            "menu_parent": "Behandlingar",
            "blocks": blocks,
        })

    # Reorder: hem, om-oss, [treatments under Behandlingar], kontakt
    order = ["hem", "om-oss"] + treatment_slugs + ["kontakt"]
    by_slug = {p["slug"]: p for p in out_pages}
    out_pages = [by_slug[s] for s in order if s in by_slug]

    return variants, out_pages


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    content = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    tokens_css = TOKENS_FILE.read_text(encoding="utf-8")
    logo_svg = LOGO_FILE.read_text(encoding="utf-8") if LOGO_FILE.exists() else "Patricia Teles"

    settings = content.get("settings", {})

    site_header = build_site_header_component(tokens_css, logo_svg)
    site_footer = build_site_footer_component(logo_svg)

    base_components = {
        "hero": build_hero_component(),
        "intro": build_intro_component(),
        "treatments-grid": build_treatments_grid_component(),
        "content-block-1": build_content_block_component("lumo/content-block-1", "Innehållsblock 1 (bild vänster)", mirror=False),
        "content-block-2": build_content_block_component("lumo/content-block-2", "Innehållsblock 2 (bild höger)", mirror=True),
        "text-blocks": build_text_blocks_component(),
        "contact-panel": build_contact_panel_component(),
        "faq": build_faq_component(),
        "map-section": build_map_section_component(),
        "reviews-section": build_reviews_section_component(),
        "contact-form": build_contact_form_component(),
        "contact-panel-with-form": build_contact_panel_with_form_component(),
    }

    variants, pages = build_site(content, manifest, base_components)

    bundle = {
        "site_name": "Patricia Teles",
        # NOTE: site_reviews_score, site_reviews_testimonials and site_booking_api_key
        # are deliberately NOT included here. Pushing them as empty strings would wipe
        # the values the user has set in WP Admin → LumoKit → Inställningar. Those
        # settings are managed manually (or via dedicated push). Bundle pushes ONLY
        # the platform identifier.
        "platform_config": {
            "platform": "boxmedia",
        },
        "global_settings": {
            "site_company_name": settings.get("company_name", "Patricia Teles"),
            "site_phone": settings.get("company_phone", ""),
            "site_email": settings.get("company_email", ""),
            "site_address": settings.get("company_address", ""),
        },
        "components": [site_header, site_footer] + variants,
        "pages": pages,
        "extra_menu_items": [],
    }

    OUT_FILE.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")

    size = OUT_FILE.stat().st_size
    print(f"[OK] Wrote {OUT_FILE.relative_to(ROOT)}")
    print(f"     Components: {len(bundle['components'])}")
    print(f"     Pages:      {len(bundle['pages'])}")
    print(f"     Size:       {size:,} bytes")


if __name__ == "__main__":
    main()
