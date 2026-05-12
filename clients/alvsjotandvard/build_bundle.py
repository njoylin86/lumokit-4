"""
build_bundle.py  —  Älvsjö Tandvård
Faithfully ports the approved HTML mockups (components.jsx + hero.jsx)
into LumoKit components. Design is NOT derived from Patricia Teles.

Output: clients/alvsjotandvard/bundle.json

Usage:
  python3 clients/alvsjotandvard/build_bundle.py
  python3 tools/build_all.py clients/alvsjotandvard/bundle.json --production
"""

from __future__ import annotations
import copy, json
from pathlib import Path
from urllib.parse import quote_plus

CLIENT_DIR  = Path(__file__).resolve().parent
ROOT        = CLIENT_DIR.parent.parent
TOKENS_FILE = CLIENT_DIR / "design-system" / "alvsjotandvard_ds" / "styles.css"
OUT_FILE    = CLIENT_DIR / "bundle.json"

ADDRESS_ENC = quote_plus("Prästgårdsgränd 4, 125 44 Älvsjö")

# ── Header-variant ──────────────────────────────────────────────────────────
# True  = svart header (ink-700, vit logga)
# False = vit header (vit bakgrund, färglogga)
DARK_HEADER = True

# Logo URLs — coloured version for header, white version for footer
LOGO_COLOR = "https://alvsjotandvard.se/wp-content/uploads/2020/12/Alvsjo-tandvard-logo-farg.png"
LOGO_WHITE = "https://alvsjotandvard.se/wp-content/uploads/2020/12/Alvsjo-tandvard-logo-vit.png"

# ---------------------------------------------------------------------------
# Inline SVG icons (stroke-based, Lucide style)
# ---------------------------------------------------------------------------
def ico(path_d, size=16, sw=1.5):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" style="display:inline-block;vertical-align:middle;flex-shrink:0;">'
        f'{path_d}</svg>'
    )

ICO_PHONE = ico('<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>')
ICO_PIN   = ico('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>')
ICO_MAIL  = ico('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>')
ICO_CLOCK = ico('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>')

# ---------------------------------------------------------------------------
# Layout CSS — appended after tokens from styles.css.
# Ports the inline styles from components.jsx/hero.jsx into proper classes.
# ---------------------------------------------------------------------------
LAYOUT_CSS = r"""
/* ── Overflow guard ─────────────────────────────────────────────── */
html, body { overflow-x: clip; max-width: 100vw; }

/* ── Containers ─────────────────────────────────────────────────── */
.container-wide {
  max-width: var(--maxw-wide); margin: 0 auto;
  padding-left: var(--gutter); padding-right: var(--gutter);
}
.section  { padding: var(--space-10) 0; }

/* ── Buttons ────────────────────────────────────────────────────── */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 10px;
  padding: 16px 28px; font-family: var(--font-sans); font-size: 13px;
  font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase;
  text-decoration: none; border: 1px solid transparent;
  border-radius: var(--radius-sm); white-space: nowrap;
  transition: all var(--dur-base) var(--ease-standard); cursor: pointer; line-height: 1;
}
.btn-primary { background: var(--ink-700); color: var(--white); border-color: var(--ink-700); }
.btn-primary:hover { background: var(--ink-900); color: var(--white); }
.btn-ghost { background: transparent; color: var(--ink-700); border-color: var(--ink-700); }
.btn-ghost:hover { background: var(--blush-50); color: var(--ink-700); }
.btn-light { background: var(--white); color: var(--ink-700); border-color: transparent; }
.btn-light:hover { background: var(--blush-50); }
.btn-sm { padding: 10px 18px; font-size: 11px; }
.btn-lg { padding: 22px 36px; font-size: 13px; }

/* ── Topstrip ───────────────────────────────────────────────────── */
.site-topstrip {
  background: var(--ink-700); color: rgba(255,255,255,0.85);
  font-family: var(--font-sans); font-size: 12px; letter-spacing: 0.04em;
}
.site-topstrip .ts-inner {
  max-width: var(--maxw-wide); margin: 0 auto;
  padding: 0 var(--gutter);
  display: flex; align-items: center; justify-content: space-between;
  height: 38px;
}
.site-topstrip a { color: rgba(255,255,255,0.85); text-decoration: none; }
.site-topstrip a:hover { color: var(--white); }
.site-topstrip .ts-left,
.site-topstrip .ts-right { display: flex; align-items: center; gap: 20px; }
.site-topstrip .ts-sep { opacity: 0.3; }

/* ── Header ─────────────────────────────────────────────────────── */
.site-header {
  position: sticky; top: 0; z-index: 50;
  background: var(--ink-700); border-bottom: 1px solid rgba(255,255,255,0.08);
}
.admin-bar .site-header { top: 32px; }
@media (max-width: 782px) { .admin-bar .site-header { top: 46px; } }
.site-header .sh-inner {
  position: relative; max-width: var(--maxw-wide); margin: 0 auto;
  padding: 0 var(--gutter); height: 78px;
  display: flex; align-items: center; justify-content: space-between;
}
.site-header .logo { display: inline-flex; align-items: center; text-decoration: none; }
.site-header .logo img { height: 57px; width: auto; display: block; }
.site-header nav { display: flex; align-items: center; gap: 32px; }
.site-header nav a, .site-header nav .menu-item a {
  font-family: var(--font-sans); font-size: 14px; font-weight: 500;
  color: rgba(255,255,255,0.85) !important; text-decoration: none;
  transition: color var(--dur-fast) var(--ease-standard);
}
.site-header nav a:hover, .site-header nav .menu-item a:hover { color: var(--white) !important; }
.site-header nav a.btn, .site-header nav a.btn:visited { background: var(--white) !important; color: var(--ink-700) !important; border-color: var(--white) !important; }
.site-header nav a.btn:hover { background: var(--blush-50) !important; color: var(--ink-700) !important; }
.site-header nav ul { list-style: none; padding: 0; margin: 0; display: flex; gap: 32px; align-items: center; }
.site-header nav li { position: relative; }
.site-header nav li.menu-item-has-children > a::after { content: "▾"; margin-left: 5px; font-size: 10px; opacity: 0.6; }
.site-header nav .sub-menu {
  display: none; position: absolute; top: 100%; left: 0;
  background: var(--ink-700); border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 12px 32px rgba(0,0,0,0.25);
  padding: 8px 0; margin-top: 8px; min-width: 220px;
  flex-direction: column; gap: 0; border-radius: 4px; z-index: 60;
}
.site-header nav li.menu-item-has-children::after {
  content: ""; position: absolute; left: 0; right: 0; top: 100%; height: 12px; background: transparent;
}
.site-header nav li:hover > .sub-menu,
.site-header nav li:focus-within > .sub-menu { display: flex; }
.site-header nav .sub-menu li { width: 100%; }
.site-header nav .sub-menu a {
  display: block; padding: 10px 18px; font-size: 13px; white-space: nowrap;
  transition: background var(--dur-fast) var(--ease-standard), color var(--dur-fast) var(--ease-standard);
}
.site-header nav .sub-menu a:hover { background: rgba(255,255,255,0.08); color: var(--white); }

/* Hamburger (mobile) */
.site-header .nav-toggle { display: none; }
.site-header .hamburger {
  display: none; width: 44px; height: 44px; cursor: pointer;
  align-items: center; justify-content: center; flex-direction: column;
  gap: 5px; border-radius: 4px; transition: background var(--dur-fast) var(--ease-standard);
}
.site-header .hamburger:hover { background: var(--blush-50); }
.site-header .hamburger span {
  display: block; width: 24px; height: 2px; background: var(--white); border-radius: 2px;
  transition: transform var(--dur-fast) var(--ease-standard), opacity var(--dur-fast) var(--ease-standard);
}
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(2) { opacity: 0; }
.site-header .nav-toggle:checked ~ .hamburger span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

/* ── Hero (HeroBleed) ───────────────────────────────────────────── */
.hero-bleed {
  position: relative; min-height: min(82vh, 820px);
  background: var(--ink-700); display: flex; flex-direction: column;
  justify-content: flex-end; overflow: hidden;
}
.hero-bleed .hb-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center; background-repeat: no-repeat;
  filter: saturate(1.05) brightness(0.75);
}
.hero-bleed .hb-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(20,20,18,0.55) 0%, rgba(20,20,18,0.30) 35%, rgba(20,20,18,0.88) 100%);
}
.hero-bleed .hb-top {
  position: absolute; top: 48px; left: 0; right: 0; z-index: 2;
}
.hero-bleed .hb-top-inner {
  max-width: var(--maxw-wide); margin: 0 auto; padding: 0 var(--gutter);
  display: flex; justify-content: space-between; align-items: center;
  color: var(--white);
}
.hero-bleed .hb-top-left {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: rgba(255,255,255,0.85);
}
.hero-bleed .hb-top-right {
  display: flex; align-items: center; gap: 10px; color: var(--white);
}
.hb-medals { display: flex; gap: 12px; align-items: center; }
.hb-top-medals {
  display: flex; gap: 12px; align-items: center;
  max-width: var(--maxw-wide); margin: 12px auto 0;
  padding: 0 var(--gutter);
}
.hb-medals-mobile { display: none; flex-direction: row; gap: 12px; margin-top: 8px; }
.hb-medal-link { display: block; flex-shrink: 0; }
.hb-medal-link img { width: 100px; height: auto; object-fit: contain; transition: transform 0.2s; }
.hb-medal-link:hover img { transform: scale(1.04); }
.hb-stats-mobile-row { display: contents; }
.hb-review-widget { margin-top: 16px; }
.hero-bleed .hb-review-widget {
  margin-top: 16px;
}
.hero-bleed .hb-stars { color: #f5c136; font-size: 14px; }
.hero-bleed .hb-score { font-size: 13px; font-weight: 500; }
.hero-bleed .hb-count { font-size: 12px; opacity: 0.7; }
.hero-bleed .hb-content {
  position: relative; z-index: 2;
  max-width: var(--maxw-wide); margin: 0 auto; padding: 0 var(--gutter);
  padding-top: 96px; padding-bottom: 0;
  color: var(--white);
  display: grid; grid-template-columns: 1.5fr 1fr; gap: 80px; align-items: end;
}
.hero-bleed .hb-headline {
  font-family: var(--font-serif); font-weight: 300;
  font-size: clamp(56px, 7.5vw, 124px); line-height: 0.95;
  letter-spacing: -0.03em; color: var(--white);
  margin: 0 0 32px; max-width: 14ch;
}
.hero-bleed .hb-headline-accent { color: var(--blush-300); font-style: italic; }
.hero-bleed .hb-ingress {
  font-family: var(--font-sans); font-size: 17px; line-height: 1.55;
  color: rgba(255,255,255,0.85); margin: 0; max-width: 48ch;
}
.hero-bleed .hb-right {
  display: flex; flex-direction: column; gap: 16px; align-items: flex-start;
}
.hero-bleed .hb-link {
  color: var(--white); font-size: 13px; font-weight: 500;
  letter-spacing: 0.14em; text-transform: uppercase;
  text-decoration: none;
  border-bottom: 1px solid rgba(255,255,255,0.4); padding-bottom: 4px;
}
.hero-bleed .hb-link:hover { border-bottom-color: var(--white); }
.hb-stats-mobile { display: none !important; }
.hero-bleed .hb-stats {
  position: relative; z-index: 2;
  max-width: var(--maxw-wide); margin: 0 auto; padding: 0 var(--gutter);
  margin-top: 80px; padding-top: 56px; padding-bottom: 56px;
  border-top: 1px solid rgba(255,255,255,0.2);
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px;
  color: var(--white);
}
.hero-bleed .hb-stat-val {
  font-family: var(--font-serif); font-weight: 300;
  font-size: 52px; line-height: 1; letter-spacing: -0.02em;
  color: var(--sage-300); display: block; margin-bottom: 6px;
}
.hero-bleed .hb-stat-lbl {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: rgba(255,255,255,0.7); display: block;
}

/* ── Treatments ─────────────────────────────────────────────────── */
.treatments-section { background: var(--white); }
.treatments-hdr {
  display: grid; grid-template-columns: 1fr auto;
  align-items: end; gap: 32px;
  margin-bottom: 56px; padding-bottom: 32px;
  border-bottom: 1px solid var(--border);
}
.treatments-hdr h2 { max-width: 20ch; margin: 8px 0 0; }
.treatments-hdr-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.treatments-hdr-meta p { max-width: 32ch; text-align: right; margin: 0; font-size: var(--fs-small); color: var(--fg-muted); }
.treatments-hdr-link {
  font-size: 13px; font-weight: 500; letter-spacing: 0.08em;
  text-transform: uppercase; text-decoration: none;
  color: var(--ink-700); border-bottom: 1px solid var(--ink-700); padding-bottom: 2px;
}
.treatments-hdr-link:hover { color: var(--blush-600); border-bottom-color: var(--blush-600); }
.treatments-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.treatment-card {
  position: relative; aspect-ratio: 1 / 1.05;
  background: var(--white); overflow: hidden;
  display: block; text-decoration: none;
}
.treatment-card .tc-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center; background-repeat: no-repeat;
  filter: saturate(0.85);
  transition: transform 480ms var(--ease-standard), filter 480ms var(--ease-standard);
}
.treatment-card:hover .tc-bg { transform: scale(1.03); filter: saturate(1); }
.treatment-card .tc-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(20,20,18,0.05) 0%, rgba(20,20,18,0.75) 100%);
  transition: background 480ms var(--ease-standard);
}
.treatment-card:hover .tc-overlay {
  background: linear-gradient(180deg, rgba(20,20,18,0.0) 0%, rgba(20,20,18,0.88) 100%);
}
.treatment-card .tc-top {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
}
.treatment-card .tc-badge {
  display: inline-flex; align-items: center; gap: 5px; flex-shrink: 0;
  padding: 4px 8px; background: var(--danger); color: var(--white);
  font-size: 9px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
}
.treatment-card .tc-badge-dot {
  width: 5px; height: 5px; border-radius: 50%; background: var(--white);
}
.treatment-card .tc-body {
  position: absolute; inset: 0; z-index: 2; padding: 28px;
  color: var(--white); display: flex; flex-direction: column; justify-content: space-between;
}
.treatment-card .tc-count {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  letter-spacing: 0.22em; text-transform: uppercase; opacity: 0.85;
}
.treatment-card .tc-name {
  font-family: var(--font-serif); font-weight: 400;
  font-size: 28px; line-height: 1.1; letter-spacing: -0.02em;
  color: var(--white); margin: 0 0 8px;
}

/* ── Reviews ────────────────────────────────────────────────────── */
.reviews-section { background: var(--blush-50); }
.reviews-hdr {
  display: grid; grid-template-columns: 1.2fr 1fr; gap: 80px;
  align-items: end; margin-bottom: 64px;
}
.reviews-hdr h2 { max-width: 15ch; margin: 8px 0 0; }
.reviews-google-box {
  background: var(--white); padding: 28px;
  display: grid; grid-template-columns: auto 1fr; gap: 20px;
  align-items: center; border: 1px solid var(--border);
}
.reviews-google-g {
  width: 56px; height: 56px; background: var(--white);
  border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-sans); font-size: 26px; font-weight: 500; color: #4285F4;
}
.reviews-google-score {
  font-family: var(--font-serif); font-size: 36px; font-weight: 400;
  color: var(--ink-700); line-height: 1;
}
.reviews-google-stars { color: var(--star); font-size: 14px; margin-left: 10px; }
.reviews-google-label { font-size: 12px; color: var(--fg-muted); margin-top: 4px; }
.reviews-widget-wrap { margin-top: 8px; }

/* ── About ──────────────────────────────────────────────────────── */
.about-section { background: var(--white); }
.about-grid {
  display: grid; grid-template-columns: 1fr 1.1fr;
  gap: 96px; align-items: center;
}
.about-text h2 { margin-bottom: 32px; }
.about-text .lead { margin-bottom: 24px; max-width: 44ch; }
.about-text p { margin-bottom: 32px; max-width: 52ch; color: var(--ink-500); }
.about-img {
  width: 100%; aspect-ratio: 4 / 5; overflow: hidden;
}

/* ── Emergency banner ───────────────────────────────────────────── */
.emergency-banner {
  background: var(--ink-700); color: var(--white);
  padding: var(--space-9) 0; position: relative; overflow: hidden;
}
.emergency-inner {
  display: grid; grid-template-columns: auto 1fr auto;
  gap: 56px; align-items: center;
}
.eb-24-block {
  display: flex; flex-direction: column; gap: 4px;
  padding-right: 56px; border-right: 1px solid rgba(255,255,255,0.15);
}
.eb-label {
  font-family: var(--font-sans); font-size: 10px; font-weight: 500;
  letter-spacing: 0.22em; text-transform: uppercase; color: var(--blush-300);
}
.eb-number {
  font-family: var(--font-serif); font-size: 64px; font-weight: 300;
  letter-spacing: -0.04em; line-height: 1; color: var(--white);
}
.eb-text h2 {
  color: var(--white); font-size: clamp(28px, 2.4vw, 40px); margin-bottom: 12px;
}
.eb-text p { color: rgba(255,255,255,0.7); max-width: 52ch; margin: 0; font-size: 16px; }
.eb-text strong { color: var(--white); }
.eb-cta { display: flex; flex-direction: column; gap: 12px; min-width: 220px; }
.eb-phone {
  display: flex; align-items: center; gap: 12px;
  font-family: var(--font-serif); font-size: 28px; font-weight: 400;
  color: var(--white); text-decoration: none; letter-spacing: -0.01em;
}
.eb-phone svg { opacity: 0.7; }

/* ── Team ───────────────────────────────────────────────────────── */
.team-section { background: var(--paper); }
.team-hdr {
  display: grid; grid-template-columns: 1fr 1fr; align-items: end;
  gap: 48px; margin-bottom: 64px; padding-bottom: 32px;
  border-bottom: 1px solid var(--border);
}
.team-hdr h2 { max-width: 16ch; margin: 8px 0 0; }
.team-hdr-right {
  display: flex; flex-direction: column; align-items: flex-end; gap: 16px;
}
.team-hdr-right p { max-width: 40ch; margin: 0; text-align: right; font-size: 15px; }
.team-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 24px;
}
.team-member { display: flex; flex-direction: column; gap: 14px; }
.team-member:has(.team-name:empty) { display: none; }
.team-photo {
  aspect-ratio: 4/5; background-size: cover;
  background-position: center; background-repeat: no-repeat;
  filter: saturate(0.9);
}
.team-name {
  font-size: 14px; font-weight: 600; color: var(--ink-700);
  margin-bottom: 4px; line-height: 1.3;
}
.team-role {
  font-size: 11px; color: var(--blush-600);
  letter-spacing: 0.08em; text-transform: uppercase; font-weight: 500;
}

/* ── PhotoTour ──────────────────────────────────────────────────── */
.photo-tour { background: var(--white); }
.pt-hdr {
  display: grid; grid-template-columns: 1fr auto;
  align-items: end; gap: 48px; margin-bottom: 56px;
}
.pt-hdr h2 { max-width: 18ch; margin: 8px 0 0; }
.pt-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 180px; gap: 16px;
}
.pt-tile {
  position: relative; overflow: hidden; background: var(--ink-100);
}
.pt-tile-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  filter: saturate(0.85);
  transition: transform 600ms var(--ease-standard);
}
.pt-tile:hover .pt-tile-bg { transform: scale(1.04); }
.pt-tile .pt-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(20,20,18,0) 50%, rgba(20,20,18,0.55) 100%);
}
.pt-label {
  position: absolute; left: 20px; bottom: 18px; color: var(--white);
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  letter-spacing: 0.22em; text-transform: uppercase;
}

/* ── Footer (DARK) ──────────────────────────────────────────────── */
.site-footer { background: var(--ink-700); color: var(--white); padding-top: 0; }
.footer-partners { padding: 56px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
.footer-top {
  display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 64px; margin-bottom: 72px;
}
.footer-brand-logo { height: 56px; width: auto; display: block; margin-bottom: 20px; margin-left: -4px; }
.footer-contact { display: flex; flex-direction: column; gap: 14px; font-size: 14px; color: rgba(255,255,255,0.7); max-width: 280px; }
.footer-contact-row { display: flex; gap: 10px; align-items: flex-start; }
.footer-contact-row svg { color: var(--blush-300); margin-top: 2px; }
.footer-contact a { color: var(--white); text-decoration: none; display: flex; align-items: center; gap: 10px; }
.footer-contact a:hover { color: var(--blush-300); }
.footer-contact a svg { color: var(--blush-300); }
.footer-col-title {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--blush-300); margin-bottom: 20px;
}
.footer-col ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.footer-col ul a { color: rgba(255,255,255,0.75); text-decoration: none; font-size: 14px; }
.footer-col ul a:hover { color: var(--white); }
.footer-hours {
  display: grid; grid-template-columns: repeat(7, 1fr);
  padding: 24px 0;
  border-top: 1px solid rgba(255,255,255,0.12);
  border-bottom: 1px solid rgba(255,255,255,0.12);
}
.footer-day {
  display: flex; flex-direction: column; gap: 4px; padding: 0 16px;
  border-left: 1px solid rgba(255,255,255,0.08);
}
.footer-day:first-child { border-left: none; padding-left: 0; }
.footer-day-name {
  font-size: 10px; font-weight: 500; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--blush-300);
}
.footer-day-hours { font-size: 13px; color: var(--white); }
.footer-legal {
  display: flex; justify-content: space-between; align-items: center;
  padding: 32px 0; font-size: 12px; color: rgba(255,255,255,0.5);
}
.footer-legal a { color: rgba(255,255,255,0.5); text-decoration: none; }
.footer-legal a:hover { color: var(--white); }
.footer-legal-links { display: flex; align-items: center; gap: 24px; }

/* ── Responsive ─────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .site-topstrip { display: none; }
  .site-header .hamburger { display: flex; }
  .header-style-toggle-mobile { display: flex !important; color: rgba(255,255,255,0.85); }
  html.header-light .header-style-toggle-mobile { color: var(--ink-600) !important; }
  .site-header nav {
    position: absolute; top: 100%; left: 0; right: 0;
    flex-direction: column; align-items: stretch; gap: 0;
    background: var(--ink-700); border-bottom: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 12px 28px rgba(0,0,0,0.3);
    max-height: 0; overflow: hidden; opacity: 0;
    transition: max-height var(--dur-base) var(--ease-standard),
      opacity var(--dur-base) var(--ease-standard),
      padding var(--dur-base) var(--ease-standard);
    pointer-events: none; padding: 0 24px;
  }
  .site-header .nav-toggle:checked ~ nav {
    max-height: 640px; opacity: 1; pointer-events: auto; padding: 12px 24px 28px;
  }
  .site-header nav ul { flex-direction: column; gap: 0; align-items: stretch; }
  .site-header nav .sub-menu {
    display: flex !important; position: static; box-shadow: none; border: none;
    padding: 4px 0 8px; min-width: 0; background: transparent; border-radius: 0;
  }
  .site-header nav .sub-menu li a { padding: 10px 4px 10px 24px !important; font-size: 12px !important; }
  .site-header nav li.menu-item-has-children > a::after { content: ""; }
  .site-header nav a, .site-header nav ul li a {
    padding: 16px 4px; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 14px; display: block;
    color: rgba(255,255,255,0.85) !important;
  }
  .site-header nav a:hover, .site-header nav ul li a:hover { color: var(--white) !important; }
  .site-header nav ul li:last-child a { border-bottom: none; }
  .site-header nav a.btn { margin-top: 14px; padding: 14px 20px; text-align: center; border-bottom: none; }
  .hero-bleed .hb-top { display: none; }
  .hero-bleed .hb-content { grid-template-columns: 1fr; gap: 24px; padding-top: 48px; }
  .hero-bleed .hb-review-widget { position: static; margin-top: 12px; }
  .hero-bleed .hb-right { padding-bottom: 32px; }
  .hb-stats-desktop { display: none !important; }
  .hb-medals-desktop { display: none !important; }
  .hb-medals-mobile { display: flex !important; }
  .hb-medals-mobile { display: flex !important; }
  .hb-medals-mobile .hb-medal-link img { width: 64px; }
  .hero-bleed .hb-stats-mobile {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr);
    border-top: 1px solid rgba(255,255,255,0.2); border-bottom: 1px solid rgba(255,255,255,0.2);
    margin: 0 !important; padding: 12px 0 !important;
    position: static; max-width: none;
  }
  .hero-bleed .hb-stats-mobile .hb-stat-val { font-size: 22px; }
  .hero-bleed .hb-stats-mobile .hb-stat-lbl { font-size: 9px; }
  .hero-bleed .hb-stats { grid-template-columns: repeat(2, 1fr); margin-top: 32px; }
  .treatments-grid { grid-template-columns: repeat(2, 1fr); }
  .treatments-hdr { grid-template-columns: 1fr; }
  .treatments-hdr-meta { align-items: flex-start; }
  .treatments-hdr-meta p { text-align: left; }
  .reviews-hdr { grid-template-columns: 1fr; gap: 32px; }
  .about-grid { grid-template-columns: 1fr; gap: 48px; }
  .emergency-inner { grid-template-columns: 1fr; gap: 32px; }
  .eb-24-block { padding-right: 0; border-right: none; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 32px; }
  .team-grid { grid-template-columns: repeat(3, 1fr); }
  .pt-grid { grid-template-columns: repeat(6, 1fr); }
  .footer-top { grid-template-columns: 1fr 1fr; gap: 48px; }
  .footer-hours { grid-template-columns: repeat(4, 1fr); }
  .footer-hours .footer-day:nth-child(5),
  .footer-hours .footer-day:nth-child(6),
  .footer-hours .footer-day:nth-child(7) { display: none; }
}
@media (max-width: 600px) {
  .site-header .sh-inner { padding: 0 20px; }
  .site-header .logo img { height: 44px; }
  .hero-bleed { min-height: 580px; }
  .hero-bleed .hb-headline { font-size: clamp(40px, 10vw, 48px); }
  .hero-bleed .hb-ingress { font-size: 15px; }
  .hero-bleed .hb-content { padding-top: 32px; gap: 20px; }
  .hero-bleed .hb-stats { grid-template-columns: repeat(2, 1fr); padding-bottom: 32px; margin-top: 24px; }
  .hero-bleed .hb-stat-val { font-size: 28px; }
  .hero-bleed .hb-stat-lbl { font-size: 10px; }
  .treatments-hdr { margin-bottom: 28px; padding-bottom: 20px; }
  .treatments-grid { grid-template-columns: repeat(2, 1fr); }
  .treatment-card { aspect-ratio: 3 / 4; }
  .treatment-card .tc-body { padding: 16px 18px; }
  .treatment-card .tc-name { font-size: 18px; }
  .about-img { aspect-ratio: 3 / 2; }
  .team-grid { grid-template-columns: repeat(2, 1fr); }
  .team-hdr { grid-template-columns: 1fr; }
  .team-hdr-right { align-items: flex-start; }
  .team-hdr-right p { text-align: left; }
  .pt-grid { grid-template-columns: repeat(2, 1fr); grid-auto-rows: 140px; }
  .pt-tile { grid-column: span 1 !important; grid-row: span 1 !important; }
  .pt-label { font-size: 9px; letter-spacing: 0.1em; left: 12px; bottom: 12px; }
  .footer-top { grid-template-columns: 1fr; gap: 36px; }
  .footer-hours { grid-template-columns: 1fr 1fr; row-gap: 20px; }
  .footer-hours .footer-day:nth-child(5),
  .footer-hours .footer-day:nth-child(6),
  .footer-hours .footer-day:nth-child(7) { display: flex; }
  .footer-hours .footer-day:nth-child(odd) { border-left: none; padding-left: 0; }
  .footer-legal { flex-direction: column; align-items: flex-start; gap: 16px; padding: 24px 0; }
}

/* ── TreatmentHero ──────────────────────────────────────────────── */
.treatment-hero { background:var(--cream); height:660px; border-bottom:1px solid var(--border); overflow:hidden; }
.treatment-hero .th-inner { max-width:var(--maxw-wide); margin:0 auto; padding:40px var(--gutter); height:100%; }
.treatment-hero .th-grid { display:grid; grid-template-columns:1.15fr 1fr; gap:64px; align-items:stretch; height:500px; }
.treatment-hero .th-left { display:flex; flex-direction:column; justify-content:space-between; }
.treatment-hero h1 { font-family:var(--font-serif); font-weight:300; font-size:clamp(44px,5.5vw,96px); line-height:0.95; letter-spacing:-0.035em; color:var(--ink-700); max-width:14ch; margin-top:0; }
.treatment-hero h1 em { font-style:italic; color:var(--sage-600); font-weight:300; }
.treatment-hero .th-lead { max-width:44ch; margin-bottom:24px; color:var(--ink-500); font-size:17px; }
.treatment-hero .th-bullets { display:grid; grid-template-columns:1fr 1fr; gap:10px 24px; padding-top:20px; margin-bottom:28px; border-top:1px solid var(--border); }
.treatment-hero .th-bullet { display:flex; align-items:baseline; gap:10px; font-size:13px; font-weight:500; color:var(--ink-600); }
.treatment-hero .th-num { font-size:10px; color:var(--sage-600); letter-spacing:0.14em; flex-shrink:0; }
.treatment-hero .th-right { position:relative; }
.treatment-hero .th-photo { position:absolute; inset:0; background-size:cover; background-position:center; filter:saturate(0.9); background-color:var(--blush-100); }
.treatment-hero .th-stat { position:absolute; left:-28px; bottom:28px; background:var(--ink-700); color:var(--white); padding:24px 28px; max-width:260px; box-shadow:0 24px 60px rgba(0,0,0,0.18); }
.treatment-hero .th-stat-label { font-size:10px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; color:var(--sage-300); margin-bottom:10px; }
.treatment-hero .th-stat-value { font-family:var(--font-serif); font-weight:300; font-size:clamp(40px,4vw,56px); line-height:0.95; letter-spacing:-0.03em; margin-bottom:8px; }
.treatment-hero .th-stat-sub { font-size:12px; color:rgba(255,255,255,0.7); line-height:1.5; }

/* ── PageHero (Barnspecialist — ingen foto) ─────────────────────── */
.page-hero { background:var(--cream); padding:96px 0; border-bottom:1px solid var(--border); }
.page-hero .ph-grid { display:grid; grid-template-columns:1.3fr 1fr; gap:80px; align-items:center; }
.page-hero h1 { font-family:var(--font-serif); font-weight:300; font-size:clamp(64px,7.5vw,132px); line-height:0.95; letter-spacing:-0.035em; color:var(--ink-700); max-width:14ch; margin:0; }
.page-hero h1 em { font-style:italic; color:var(--sage-600); font-weight:300; }
.page-hero .ph-right { padding-bottom:16px; }
.page-hero .ph-lead { max-width:40ch; margin-bottom:32px; color:var(--ink-500); }
.page-hero .ph-bullets { display:grid; grid-template-columns:1fr 1fr; gap:14px; padding-top:24px; border-top:1px solid var(--border); margin-bottom:40px; }
.page-hero .ph-bullet { display:flex; align-items:baseline; gap:10px; font-size:16px; font-weight:500; color:var(--ink-700); }
.page-hero .ph-num { font-size:13px; color:var(--sage-600); letter-spacing:0.14em; flex-shrink:0; }

/* ── CTAStrip ───────────────────────────────────────────────────── */
.cta-strip { background:var(--ink-700); color:var(--white); padding:80px 0; }
.cta-strip .cs-grid { display:grid; grid-template-columns:1.3fr 1fr; gap:48px; align-items:center; }
.cta-strip h2 { color:var(--white); margin-bottom:16px; max-width:18ch; }
.cta-strip .cs-sub { color:rgba(255,255,255,0.7); max-width:46ch; font-size:16px; }
.cta-strip .cs-actions { display:flex; gap:12px; justify-self:end; flex-wrap:wrap; }
.btn-white-ghost { background:transparent; color:var(--white); border-color:rgba(255,255,255,0.4); }
.btn-white-ghost:hover { background:rgba(255,255,255,0.1); color:var(--white); }

/* ── FactStrip (Barnspecialist) ─────────────────────────────────── */
.fact-strip { background:var(--white); padding:64px 0; }
.fact-strip .fs-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--border); border:1px solid var(--border); }
.cb-section { padding:0 0 96px; }
.cb-grid { display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:center; }
.cb-grid--mirror .cb-text { order:2; }
.cb-grid--mirror .cb-img  { order:1; }
.cb-grid--normal .cb-text { order:1; }
.cb-grid--normal .cb-img  { order:2; }
.cb-img { width:100%; aspect-ratio:4/5; overflow:hidden; border-radius:var(--radius-sm); background:var(--blush-100); }
.fact-strip .fs-cell { background:var(--white); padding:36px 28px; }
.fact-strip .fs-value { font-family:var(--font-serif); font-weight:300; font-size:48px; line-height:1; letter-spacing:-0.03em; color:var(--ink-700); margin-bottom:14px; }
.fact-strip .fs-label { font-size:14px; color:var(--ink-500); line-height:1.5; }

/* ── Contact Grid ───────────────────────────────────────────────── */
.contact-grid { background:var(--white); padding:var(--space-10) 0; }
.contact-grid .cg-inner { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--border); border:1px solid var(--border); }
.contact-grid .cg-card { background:var(--white); padding:40px 36px; display:flex; flex-direction:column; gap:14px; }
.contact-grid .cg-card a { text-decoration:none; color:inherit; }
.contact-grid .cg-h { font-family:var(--font-serif); font-weight:400; font-size:28px; line-height:1.2; letter-spacing:-0.02em; color:var(--ink-700); }
.contact-grid .cg-sub { font-size:14px; color:var(--ink-600); }
.contact-grid .cg-note { margin-top:auto; padding-top:20px; border-top:1px solid var(--border); font-size:13px; color:var(--ink-500); line-height:1.5; }

/* ── Map + Hours Block ──────────────────────────────────────────── */
.map-hours { background:var(--cream); padding:var(--space-10) 0; }
.map-hours .mh-grid { display:grid; grid-template-columns:1.5fr 1fr; gap:48px; align-items:stretch; }
.map-hours .mh-map { background:var(--sage-50); min-height:480px; position:relative; overflow:hidden; border:1px solid var(--border); }
.map-hours .mh-map svg { position:absolute; inset:0; width:100%; height:100%; }
.map-hours .mh-badge { position:absolute; left:24px; bottom:24px; background:var(--white); padding:12px 16px; font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:var(--ink-700); border:1px solid var(--border); text-decoration:none; }
.map-hours .mh-hours { background:var(--white); padding:40px; border:1px solid var(--border); display:flex; flex-direction:column; }
.map-hours .mh-row { display:flex; justify-content:space-between; align-items:baseline; padding:14px 0; border-bottom:1px solid var(--border); }
.map-hours .mh-row:last-of-type { border-bottom:none; }
.map-hours .mh-day { font-size:14px; color:var(--ink-600); }
.map-hours .mh-time { font-family:var(--font-serif); font-size:17px; font-weight:400; color:var(--ink-700); letter-spacing:-0.01em; }
.map-hours .mh-time.closed { color:var(--fg-muted); }
.map-hours .mh-note { margin-top:28px; padding:20px 0 0; border-top:1px solid var(--border); font-size:13px; line-height:1.6; color:var(--ink-500); }

/* ── Contact Form ───────────────────────────────────────────────── */
.contact-form-section { background:var(--white); padding:var(--space-10) 0; }
.contact-form-section .cf-grid { display:grid; grid-template-columns:1fr 1.4fr; gap:80px; align-items:center; }
.contact-form-section h2 { max-width:14ch; margin-bottom:24px; }
.lumo-contact-form { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.lumo-contact-form label { display:flex; flex-direction:column; gap:8px; }
.lumo-contact-form label.full { grid-column:1/-1; }
.lumo-contact-form .lbl { font-family:var(--font-sans); font-size:11px; font-weight:500; letter-spacing:0.14em; text-transform:uppercase; color:var(--ink-600); }
.lumo-contact-form input,
.lumo-contact-form textarea { padding:14px 16px; border:1px solid var(--border); background:var(--white); font-family:var(--font-sans); font-size:15px; color:var(--ink-700); resize:vertical; outline:none; }
.lumo-contact-form input:focus,
.lumo-contact-form textarea:focus { border-color:var(--sage-600); }
.lumo-contact-form .cf-submit { grid-column:1/-1; justify-self:start; }
.lumo-form-msg { grid-column:1/-1; font-size:14px; color:#c0392b; min-height:20px; }
.lumo-form-success { font-family:var(--font-serif); font-size:24px; color:var(--ink-700); line-height:1.5; padding:40px 0; }

@media (max-width: 900px) {
  .treatment-hero { height:auto; }
  .treatment-hero .th-grid { grid-template-columns:1fr; height:auto; }
  .treatment-hero .th-right { display:none; }
  .page-hero .ph-grid { grid-template-columns:1fr; gap:40px; }
  .cta-strip .cs-grid { grid-template-columns:1fr; }
  .cta-strip .cs-actions { justify-self:start; }
  .fact-strip .fs-grid { grid-template-columns:repeat(2,1fr); }
  .cb-grid { grid-template-columns:1fr; gap:40px; }
  .cb-grid--mirror .cb-text, .cb-grid--normal .cb-text { order:1; }
  .cb-grid--mirror .cb-img,  .cb-grid--normal .cb-img  { order:2; }
  .cb-img { aspect-ratio:3/2; }
  .cb-section { padding:56px 0; }
  .contact-grid .cg-inner { grid-template-columns:1fr; gap:0; }
  .contact-grid .cg-card { border-bottom:1px solid var(--border); }
  .contact-grid .cg-card:last-child { border-bottom:none; }
  .map-hours .mh-grid { grid-template-columns:1fr; }
  .map-hours .mh-map { min-height:280px; }
  .contact-form-section .cf-grid { grid-template-columns:1fr; gap:40px; }
}
@media (max-width: 600px) {
  .treatment-hero .th-bullets { grid-template-columns:1fr; }
  .page-hero { padding:56px 0; }
  .page-hero h1 { font-size:clamp(40px,11vw,72px); }
  .page-hero .ph-bullets { grid-template-columns:1fr; gap:10px; }
  .page-hero .ph-right .btn { width:100%; justify-content:center; }
  .eb-cta { min-width:0; }
  .eb-phone { font-size:22px; }
  .fact-strip .fs-grid { grid-template-columns:1fr; }
  .contact-grid .cg-card { padding:28px 20px; }
  .lumo-contact-form { grid-template-columns:1fr; }
  .lumo-contact-form label.full { grid-column:1/-1; }
  .map-hours .mh-map { min-height:220px; }
  .map-hours .mh-hours { padding:24px 20px; }
}

/* ── Om oss — TextBlocks ────────────────────────────────────────── */
.tb-section { background:var(--cream); padding:var(--space-10) 0; }
.tb-hdr { margin-bottom:64px; padding-bottom:32px; border-bottom:1px solid var(--border); }
.tb-hdr .eyebrow { margin-bottom:16px; }
.tb-hdr h2 { max-width:24ch; margin:0; }
.tb-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:64px 80px; }
.tb-block { display:flex; flex-direction:column; gap:16px; }
.tb-num { font-size:11px; font-weight:500; letter-spacing:0.22em; text-transform:uppercase; color:var(--sage-600); }
.tb-block h3 { font-family:var(--font-serif); font-weight:400; font-size:clamp(20px,1.8vw,28px); line-height:1.2; letter-spacing:-0.02em; color:var(--ink-700); max-width:22ch; margin:0; }
.tb-block p { font-size:15px; line-height:1.7; color:var(--ink-500); margin:0; }

/* ── Om oss — Organisation ──────────────────────────────────────── */
.org-section { background:var(--cream); padding:var(--space-10) 0; }
.org-hdr { margin-bottom:64px; padding-bottom:32px; border-bottom:1px solid var(--border); }
.org-hdr .eyebrow { margin-bottom:16px; }
.org-hdr h2 { max-width:28ch; margin:0; }
.org-grid { display:grid; grid-template-columns:1.2fr 1fr; gap:80px; align-items:start; }
.org-lead { font-size:17px; line-height:1.7; color:var(--ink-500); max-width:46ch; margin:0 0 40px; }
.org-benefits { display:flex; flex-direction:column; margin-bottom:0; }
.org-benefit { display:flex; gap:16px; align-items:baseline; padding:14px 0; border-bottom:1px solid var(--border); font-size:15px; color:var(--ink-600); }
.org-benefit-num { font-size:10px; font-weight:600; letter-spacing:0.18em; color:var(--sage-600); flex-shrink:0; }
.org-form-wrap { background:var(--white); padding:40px 36px; border:1px solid var(--border); }
.org-form-wrap .eyebrow { margin-bottom:20px; }

/* ── Om oss — Arbeta med oss ────────────────────────────────────── */
.arbeta-section { background:var(--ink-700); color:var(--white); padding:var(--space-10) 0; }
.arbeta-hdr { margin-bottom:64px; padding-bottom:32px; border-bottom:1px solid rgba(255,255,255,0.15); }
.arbeta-hdr .eyebrow { color:var(--sage-300); margin-bottom:16px; }
.arbeta-hdr h2 { color:var(--white); max-width:28ch; margin:0; }
.arbeta-grid { display:grid; grid-template-columns:1.2fr 1fr; gap:80px; }
.arbeta-lead { font-size:17px; line-height:1.7; color:rgba(255,255,255,0.8); max-width:48ch; margin:0 0 40px; }
.arbeta-list-hdr { font-size:11px; font-weight:500; letter-spacing:0.18em; text-transform:uppercase; color:var(--sage-300); margin-bottom:20px; }
.arbeta-items { display:flex; flex-direction:column; margin-bottom:48px; }
.arbeta-item { display:flex; gap:16px; align-items:baseline; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.1); font-size:15px; color:rgba(255,255,255,0.85); }
.arbeta-item-num { font-size:10px; font-weight:600; letter-spacing:0.18em; color:var(--sage-300); flex-shrink:0; }
.arbeta-actions { display:flex; gap:12px; flex-wrap:wrap; }
.arbeta-reqs { display:flex; flex-direction:column; gap:12px; margin-bottom:40px; }
.arbeta-req { display:flex; gap:14px; align-items:baseline; font-size:14px; color:rgba(255,255,255,0.8); line-height:1.5; }
.arbeta-req-dot { width:6px; height:6px; border-radius:50%; background:var(--sage-400); flex-shrink:0; margin-top:6px; }
.arbeta-tools { display:flex; flex-direction:column; gap:8px; }
.arbeta-tool { font-size:13px; color:rgba(255,255,255,0.6); padding:10px 16px; background:rgba(255,255,255,0.06); }

/* ── Om oss — Feedback ──────────────────────────────────────────── */
.feedback-section { background:var(--cream); padding:var(--space-10) 0; }
.feedback-grid { display:grid; grid-template-columns:1fr 1.4fr; gap:80px; align-items:start; }
.feedback-eyebrow { margin-bottom:16px; }
.feedback-grid h2 { max-width:18ch; margin-bottom:24px; }
.feedback-lead { font-size:16px; line-height:1.7; color:var(--ink-500); max-width:40ch; margin:0 0 32px; }
.feedback-prize { font-size:14px; color:var(--ink-500); line-height:1.7; margin:0; }
.feedback-form-wrap { background:var(--white); padding:48px 40px; border:1px solid var(--border); }

@media (max-width: 900px) {
  .tb-grid { grid-template-columns:1fr; gap:48px; }
  .org-grid { grid-template-columns:1fr; gap:48px; }
  .arbeta-grid { grid-template-columns:1fr; gap:48px; }
  .feedback-grid { grid-template-columns:1fr; gap:48px; }
  .feedback-form-wrap { padding:32px 24px; }
}
@media (max-width: 600px) {
  .arbeta-actions { flex-direction:column; }
  .arbeta-actions .btn { width:100%; justify-content:center; }
}

/* ── Partners strip (i footern) ─────────────────────────────────── */
.footer-partners .ps-eyebrow {
  text-align: center;
  font-family: var(--font-sans);
  font-size: 22px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.45);
  margin-bottom: 36px;
}
.footer-partners .ps-logos {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 40px 56px;
}
.footer-partners .ps-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.55;
  transition: opacity 0.25s ease;
}
.footer-partners .ps-logo:hover { opacity: 1; }
.footer-partners .ps-logo img {
  height: 88px;
  width: auto;
  max-width: 320px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}
.footer-partners .ps-logo.ps-logo-round img {
  height: 128px;
  border-radius: 50%;
  filter: none;
  opacity: 1;
}
.footer-partners .ps-logo.ps-logo-round { opacity: 0.75; }
.footer-partners .ps-logo.ps-logo-round:hover { opacity: 1; }
/* Natural-color logos — no invert, screen blend hides any white bg */
.footer-partners .ps-logo.ps-logo-natural { opacity: 0.9; }
.footer-partners .ps-logo.ps-logo-natural:hover { opacity: 1; }
.footer-partners .ps-logo.ps-logo-natural img {
  filter: none;
  mix-blend-mode: screen;
}
@media (max-width: 600px) {
  .footer-partners { padding: 40px 0; }
  .footer-partners .ps-logos { gap: 20px 32px; }
  .footer-partners .ps-logo img { height: 44px; }
  .footer-partners .ps-logo.ps-logo-round img { height: 64px; }
}
"""

# ---------------------------------------------------------------------------
# Behandlingar som är aktiva (publika). Övriga sätts till draft i WP.
# ---------------------------------------------------------------------------
ACTIVE_TREATMENTS: set[str] = {
    "akut-tandvard",
}

# ---------------------------------------------------------------------------
# Per-page hero data (from approved mockups in design-system/)
# ---------------------------------------------------------------------------
TREATMENT_HERO_DATA: dict[str, dict] = {
    "akut-tandvard": {
        "eyebrow":      "N° 01 — Akuttandvård",
        "title":        "Snabb hjälp",
        "title_italic": "när det gör ont.",
        "ingress":      "När olyckan är framme eller värken slår till behöver du snabb och trygg hjälp. Vi finns här för att lindra smärtan och åtgärda problemet — oftast redan samma dag.",
        "bullets":      ["Akuttider varje dag", "Oftast samma dag", "Erfaren expertis", "Centralt i Älvsjö"],
        "stat_label":   "Genomsnittlig väntetid",
        "stat_value":   "< 4 tim",
        "stat_sub":     "från första samtal till lindring för 9 av 10 akuta patienter.",
        "cta_title":    "Behöver du hjälp nu?",
        "cta_sub":      "Ring oss direkt — vi reserverar akuttider varje dag och hjälper dig ofta samma dag. 08 — 12 85 45 55.",
    },
    "implantat": {
        "eyebrow":      "N° 02 — Tandimplantat",
        "title":        "Permanenta tänder.",
        "title_italic": "För livet.",
        "ingress":      "Ett tandimplantat är den mest naturliga ersättningen för en förlorad tand — det ser ut, känns och fungerar precis som din egna tand. Vi planerar och utför hela behandlingen på plats.",
        "bullets":      ["3D-planering med CBCT", "Specialistteam på plats", "Räntefri delbetalning", "Livslång hållbarhet"],
        "stat_label":   "Lyckad integrering",
        "stat_value":   "96 %",
        "stat_sub":     "efter 10 år — meta-analys av 18 kliniska studier (PubMed 2019).",
        "cta_title":    "Boka implantatrådgivning",
        "cta_sub":      "Ring 08-12 85 45 55 eller boka online. Vi bedömer din situation kostnadsfritt vid konsultationsbesöket.",
    },
    "karies-hal-i-tanden": {
        "eyebrow":      "N° 03 — Karies · Hål i tanden",
        "title":        "Snabb lagning —",
        "title_italic": "utan obehag.",
        "ingress":      "Karies är världens vanligaste sjukdom och kan drabba alla. Med modern kompositteknik lagar vi hål skonsamt, estetiskt och hållbart — och vi ser alltid till att du är bekväm under hela behandlingen.",
        "bullets":      ["Skonsamteknik", "Estetisk komposit", "Ingen smärta", "Snabb behandling"],
        "stat_label":   "Behandlingstid",
        "stat_value":   "20–45",
        "stat_sub":     "minuter för en standardfyllning.",
        "cta_title":    "Har du ont eller misstänker hål?",
        "cta_sub":      "Boka en tid idag — ju tidigare vi behandlar, desto enklare och billigare ingreppet. Ring 08-12 85 45 55.",
    },
    "tandblekning": {
        "eyebrow":      "N° 04 — Tandblekning",
        "title":        "Ljusare leende.",
        "title_italic": "Snabbt och säkert.",
        "ingress":      "Professionell tandblekning ger upp till 8–10 nyanser ljusare tänder — utan att skada emaljens struktur. Vi erbjuder klinikblekning, hemblekning och kombinationsmetoden.",
        "bullets":      ["Säkert & skonsamt", "Synligt resultat direkt", "Individuell anpassning", "Klinik & hemblekning"],
        "stat_label":   "Ljusare i snitt",
        "stat_value":   "7",
        "stat_sub":     "nyanser med professionell klinikblekning, enligt kliniska studier.",
        "cta_title":    "Boka en blekningskonsultation",
        "cta_sub":      "Vi bedömer dina tänder och rekommenderar rätt metod för dig. Ring 08-12 85 45 55 eller boka online.",
    },
    "tandfasader-veneers": {
        "eyebrow":      "N° 05 — Tandfasader · Veneers",
        "title":        "Ditt drömleende —",
        "title_italic": "skräddarsytt.",
        "ingress":      "Tandfasader (veneers) är tunna porslinsskal som limmas på tandens framsida. De döljer missfärgningar, ojämnheter och mellanrum — och ger ett harmoniskt, naturligt leende.",
        "bullets":      ["Porslin & komposit", "Digitalt smile design", "Långvarig estetik", "Minimal preparation"],
        "stat_label":   "Hållbarhet",
        "stat_value":   "15–20",
        "stat_sub":     "år för porslinsfaner med god munhygien.",
        "cta_title":    "Boka en konsultation om tandfasader",
        "cta_sub":      "Vi skapar en digital preview av ditt leende — utan kostnad vid konsultationsbesöket. Ring 08-12 85 45 55.",
    },
    "tandreglering-stockholm": {
        "eyebrow":      "N° 06 — Tandreglering · Invisalign",
        "title":        "Raka tänder.",
        "title_italic": "Utan byglar.",
        "ingress":      "Vi är certifierade Invisalign-leverantörer. Med klara, avtagbara skenor rätar vi ut dina tänder diskret och effektivt — anpassat till ditt vardagliga liv.",
        "bullets":      ["Certifierat Invisalign-team", "Digital 3D-planering", "Avtagbar — äter som vanligt", "Räntefri delbetalning"],
        "stat_label":   "Behandlingstid",
        "stat_value":   "6–24",
        "stat_sub":     "månader med Invisalign.",
        "cta_title":    "Boka en gratis Invisalign-konsultation",
        "cta_sub":      "Vi tar ett digitalt avtryck och visar dig ditt potentiella slutresultat — utan kostnad. Ring 08-12 85 45 55.",
    },
    "tandsten-tandhygienist": {
        "eyebrow":      "N° 07 — Tandsten · Tandhygienist",
        "title":        "Professionell rengöring —",
        "title_italic": "grunden för allt.",
        "ingress":      "Regelbunden tandhygienistbehandling är det mest effektiva sättet att förebygga karies, tandlossning och dålig andedräkt. Våra erfarna tandhygienister rengör noggrant och ger dig verktygen för hemvård.",
        "bullets":      ["Ultraljudsrengöring", "Individuell riskbedömning", "Kostnadsfri för barn", "Ingen remiss krävs"],
        "stat_label":   "Rekommenderat intervall",
        "stat_value":   "6–12",
        "stat_sub":     "månader för de flesta vuxna.",
        "cta_title":    "Boka tandhygienistbesök",
        "cta_sub":      "Förebyggande vård är alltid billigare än behandling. Boka online eller ring 08-12 85 45 55.",
    },
    "tandvardsradsla": {
        "eyebrow":      "N° 08 — Tandvårdsrädsla",
        "title":        "Du bestämmer",
        "title_italic": "takten.",
        "ingress":      "Vi möter dagligen patienter med tandvårdsrädsla — från mild oro till svår fobi. Vår erfarenhet är att alla kan komma till en punkt där tandvård känns hanterbar. Vi börjar där du är, inte där vi tycker du borde vara.",
        "bullets":      ["Ingen dömande miljö", "Stop-signal alltid gäller", "Extra tid per patient", "Eventuellt lugnande"],
        "stat_label":   "Av befolkningen",
        "stat_value":   "50 %+",
        "stat_sub":     "uppger någon grad av oro inför tandläkarbesök.",
        "cta_title":    "Ta det första steget — vi möter dig där du är",
        "cta_sub":      "Ring 08-12 85 45 55 och berätta om din rädsla. Vi lyssnar, anpassar och skapar ett besök som fungerar för just dig.",
    },
}

BARNSPECIALIST_DATA = {
    "eyebrow":      "N° 09 — Barnspecialist · Pedodonti",
    "title":        "Trygg tandvård",
    "title_italic": "från första tanden.",
    "ingress":      "På Älvsjö Pedodonti möter vi barn och unga upp till 23 år med specialistkompetens. Vi skapar trygga och positiva tandvårdsupplevelser, anpassade efter varje individs behov och känslor.",
    "bullets":      ["Specialist för barn", "Trygga upplevelser", "Korta väntetider", "Region Stockholm"],
    "cta_title":    "Behöver ditt barn specialistvård?",
    "cta_sub":      "Vi tar emot remisser via Muntra. Är du osäker — ring oss på 08-12 85 45 55 så hjälper vi dig vidare.",
}

KONTAKT_CTA_DATA = {
    "cta_title": "Behöver du akut hjälp?",
    "cta_sub":   "Ring oss direkt — vi gör vårt bästa för att ge dig en tid samma dag.",
}

PARTNERS = [
    {"name": "Nattvandrarna",           "url": "https://swordfish.templweb.com/wp-content/uploads/2026/05/Rund-Banner_2_SKS2025-1-300x300-1.png",   "round": True,  "natural": False, "link": "https://nattvandrarna.se/"},
    {"name": "Region Stockholm",        "url": "https://swordfish.templweb.com/wp-content/uploads/2026/05/Pa-uppdrag-av_vit-300x77-1.png",           "round": False, "natural": False, "link": "https://www.vardguiden.se/"},
    {"name": "Älvsjö Pedodonti",        "url": "https://swordfish.templweb.com/wp-content/uploads/2026/05/Pedodonti-logo-2023-v2-300x106-1.png",     "round": False, "natural": False, "link": "https://www.alvsjotandvard.se/barnspecialist/"},
    {"name": "UNICEF",                  "url": "https://swordfish.templweb.com/wp-content/uploads/2026/05/alvsjo-tandvard-unicef2025.jpg",            "round": False, "natural": True,  "link": "https://unicef.se/"},
    {"name": "Älvsjö AIK",              "url": "https://swordfish.templweb.com/wp-content/uploads/2026/05/alvsjo_aik_emblem_fotboll_vit-text-liten.png", "round": False, "natural": True, "link": "http://alvsjoaik.se"},
]


def build_partners_logos_html() -> str:
    logos = ""
    for p in PARTNERS:
        if p["round"]:
            cls = "ps-logo ps-logo-round"
        elif p["natural"]:
            cls = "ps-logo ps-logo-natural"
        else:
            cls = "ps-logo"
        logos += (
            f'<a href="{p["link"]}" class="{cls}" target="_blank" rel="noopener" aria-label="{p["name"]}">'
            f'<img src="{p["url"]}" alt="{p["name"]}" loading="lazy">'
            f'</a>'
        )
    return logos

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def collapse(html: str) -> str:
    return " ".join(html.split())

# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

def build_site_header(tokens_css: str) -> dict:
    font_preload = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Outfit:wght@400;500;600&display=swap">
"""
    header_variant_css = "" if DARK_HEADER else """
.site-header { background: var(--white) !important; border-bottom: 1px solid var(--border) !important; }
.site-header nav a, .site-header nav .menu-item a { color: var(--ink-600) !important; }
.site-header nav a:hover, .site-header nav .menu-item a:hover { color: var(--blush-600) !important; }
.site-header nav a.btn, .site-header nav a.btn:visited { background: var(--ink-700) !important; color: var(--white) !important; border-color: var(--ink-700) !important; }
.site-header nav a.btn:hover { background: var(--ink-900) !important; color: var(--white) !important; }
.site-header nav .sub-menu { background: var(--white) !important; border-color: var(--border) !important; box-shadow: 0 12px 32px rgba(20,20,18,0.10) !important; }
.site-header nav .sub-menu a:hover { background: var(--blush-50) !important; color: var(--blush-600) !important; }
.site-header .hamburger span { background: var(--ink-700) !important; }
@media (max-width: 900px) {
  .site-header nav { background: var(--white) !important; border-bottom-color: var(--border) !important; }
  .site-header nav a, .site-header nav ul li a { color: var(--ink-600) !important; border-bottom-color: var(--border) !important; }
  .site-header nav a:hover, .site-header nav ul li a:hover { color: var(--blush-600) !important; }
}
"""
    header_logo = LOGO_WHITE if DARK_HEADER else LOGO_COLOR
    header_light_override = """
html.header-light .site-header { background: var(--white) !important; border-bottom: 1px solid var(--border) !important; }
html.header-light .site-header nav a, html.header-light .site-header nav .menu-item a { color: var(--ink-600) !important; }
html.header-light .site-header nav a:hover, html.header-light .site-header nav .menu-item a:hover { color: var(--blush-600) !important; }
html.header-light .site-header nav a.btn, html.header-light .site-header nav a.btn:visited { background: var(--ink-700) !important; color: var(--white) !important; border-color: var(--ink-700) !important; }
html.header-light .site-header nav a.btn:hover { background: var(--ink-900) !important; }
html.header-light .site-header nav .sub-menu { background: var(--white) !important; border-color: var(--border) !important; box-shadow: 0 12px 32px rgba(20,20,18,0.10) !important; }
html.header-light .site-header nav .sub-menu a:hover { background: var(--blush-50) !important; color: var(--blush-600) !important; }
html.header-light .site-header .hamburger span { background: var(--ink-700) !important; }
@media (max-width: 900px) {
  html.header-light .site-header nav { background: var(--white) !important; border-bottom-color: var(--border) !important; }
  html.header-light .site-header nav a, html.header-light .site-header nav ul li a { color: var(--ink-600) !important; border-bottom-color: var(--border) !important; }
}
"""
    style_block = f"<style>\n{tokens_css}\n{LAYOUT_CSS}\n{header_variant_css}\n{header_light_override}\n</style>"
    onload_js = """<script>
(function(){
  var done=false;
  function r(){if(done)return;done=true;document.body.classList.add('lumo-loaded');}
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(r);
  if(document.readyState!=='loading'){r();}else document.addEventListener('DOMContentLoaded',r);
  setTimeout(r,600);
})();
// Contact form handler
document.addEventListener('submit',function(e){
  var form=e.target.closest('.lumo-contact-form');
  if(!form)return;
  e.preventDefault();
  var btn=form.querySelector('[type=submit]');
  var msg=form.querySelector('.lumo-form-msg');
  if(msg)msg.textContent='';
  btn.disabled=true;btn.textContent='Skickar…';
  var fn=form.querySelector('[name=fornamn]');
  var en=form.querySelector('[name=efternamn]');
  var data={
    name:((fn?fn.value:'')+' '+(en?en.value:'')).trim(),
    email:(form.querySelector('[name=email]')||{}).value||'',
    phone:(form.querySelector('[name=phone]')||{}).value||'',
    message:(form.querySelector('[name=arende]')||{}).value||''
  };
  fetch('/wp-json/lumokit/v1/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
    .then(function(r){return r.json();})
    .then(function(j){
      if(j.success){form.innerHTML='<p class="lumo-form-success">Tack! Vi återkommer inom en arbetsdag.</p>';}
      else{if(msg)msg.textContent=j.message||'Något gick fel. Försök igen.';btn.disabled=false;btn.textContent='Skicka meddelande →';}
    })
    .catch(function(){if(msg)msg.textContent='Nätverksfel. Försök igen.';btn.disabled=false;btn.textContent='Skicka meddelande →';});
});
</script>"""

    html = f"""
{font_preload}
{style_block}
<script>(function(){{var h=localStorage.getItem('hdr');if(h==='0'){{document.documentElement.classList.add('header-light');document.addEventListener('DOMContentLoaded',function(){{document.querySelectorAll('.hdr-toggle-label').forEach(function(b){{b.textContent='○ White';}});var b=document.getElementById('header-style-toggle');if(b)b.textContent='○ White';}});}}}})();</script>
{onload_js}
<div class="site-topstrip">
  <div class="ts-inner">
    <div class="ts-left">
      <span style="display:flex;align-items:center;gap:6px;">{ICO_PIN} {{{{site_address}}}} <span class="ts-sep">·</span> 2 min från pendeln</span>
      <span class="ts-sep">·</span>
      <span style="display:flex;align-items:center;gap:6px;">{ICO_CLOCK} Öppet vardagar {{{{site_hours_monday}}}}</span>
    </div>
    <div class="ts-right">
      <a href="https://minatider.alvsjotandvard.se/?src=site">Mina tider</a>
      <span class="ts-sep">·</span>
      <button id="header-style-toggle" onclick="(function(){{var h=document.documentElement;var isLight=h.classList.toggle('header-light');localStorage.setItem('hdr',isLight?'0':'1');document.getElementById('header-style-toggle').textContent=isLight?'○ White':'● Black';document.querySelectorAll('.hdr-toggle-label').forEach(function(b){{b.textContent=isLight?'○ White':'● Black';}});}})()" style="background:none;border:none;color:rgba(255,255,255,0.85);font-size:12px;cursor:pointer;padding:0;letter-spacing:0.04em;font-family:inherit;">● Black</button>
      <span class="ts-sep">·</span>
      <a href="/remiss-2">Remiss</a>
      <span class="ts-sep">·</span>
      <a href="tel:{{{{site_phone}}}}" style="display:flex;align-items:center;gap:6px;">{ICO_PHONE} {{{{site_phone}}}}</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="sh-inner">
    <a href="/" class="logo" aria-label="Älvsjö Tandvård">
      <img src="{LOGO_COLOR}" alt="Älvsjö Tandvård">
    </a>
    <button class="header-style-toggle-mobile" onclick="(function(){{var h=document.documentElement;var isLight=h.classList.toggle('header-light');localStorage.setItem('hdr',isLight?'0':'1');document.querySelectorAll('.hdr-toggle-label').forEach(function(b){{b.textContent=isLight?'○ White':'● Black';}});}})()" style="display:none;background:none;border:none;font-size:16px;cursor:pointer;padding:4px 8px;"><span class="hdr-toggle-label">● Black</span></button>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-hidden="true">
    <label for="nav-toggle" class="hamburger" aria-label="Öppna meny">
      <span></span><span></span><span></span>
    </label>
    <nav>
      {{{{lumokit-primary}}}}
      <a href="#tdl-booking-widget" class="btn btn-primary btn-sm">Boka tid</a>
    </nav>
  </div>
</header>
"""
    return {
        "block_name": "lumo/site-header",
        "title": "Sidhuvud",
        "html_template": collapse(html),
        "schema": [{"name": "lumokit-primary", "type": "nav_menu", "label": "Primär meny"}],
    }


def build_hero() -> dict:
    html = """
<section class="hero-bleed">
  <div class="hb-bg" style="background-image:url({{hero_image}});"></div>
  <div class="hb-overlay"></div>

  <div class="hb-top">
    <div class="hb-top-inner">
      <span class="hb-top-left">{{eyebrow}}</span>
    </div>
    <div class="hb-top-medals hb-medals-desktop">
      <a href="https://www.tandlakare.se/klinik/stockholm/alvsjo-tandvard/" target="_blank" rel="noopener" class="hb-medal-link">
        <img src="https://swordfish.templweb.com/wp-content/uploads/2026/05/medal_gold-2025.webp" alt="Rekommenderad klinik 2025 – Tandläkare.se">
      </a>
      <a href="https://www.tandlakare.se/klinik/stockholm/alvsjo-tandvard/" target="_blank" rel="noopener" class="hb-medal-link">
        <img src="https://swordfish.templweb.com/wp-content/uploads/2026/05/medal_pink-2023.webp" alt="Rekommenderad klinik 2023 – Tandläkare.se">
      </a>
    </div>
  </div>

  <div class="hb-content container-wide">
    <div class="hb-left">
      <h1 class="hb-headline">Trygg tandvård.<br><span class="hb-headline-accent">Hela familjen.</span></h1>
      <p class="hb-ingress">{{ingress}}</p>
    </div>
    <div class="hb-right">
      <div class="hb-stats hb-stats-mobile">
        <div><span class="hb-stat-val">{{stat_1_val}}</span><span class="hb-stat-lbl">{{stat_1_lbl}}</span></div>
        <div><span class="hb-stat-val">{{stat_2_val}}</span><span class="hb-stat-lbl">{{stat_2_lbl}}</span></div>
        <div><span class="hb-stat-val">{{stat_3_val}}</span><span class="hb-stat-lbl">{{stat_3_lbl}}</span></div>
        <div><span class="hb-stat-val">{{stat_4_val}}</span><span class="hb-stat-lbl">{{stat_4_lbl}}</span></div>
      </div>
      <a href="#tdl-booking-widget" class="btn btn-light btn-lg" style="width:100%;">Boka tid online</a>
      <a href="/akut-tandvard" class="hb-link">Akuttandvård samma dag →</a>
      <div class="hb-review-widget">[trustindex data-widget-id=0771e9d71a88743f97661278b10]</div>
      <div class="hb-medals hb-medals-mobile">
        <a href="https://www.tandlakare.se/klinik/stockholm/alvsjo-tandvard/" target="_blank" rel="noopener" class="hb-medal-link">
          <img src="https://swordfish.templweb.com/wp-content/uploads/2026/05/medal_gold-2025.webp" alt="Rekommenderad klinik 2025 – Tandläkare.se">
        </a>
        <a href="https://www.tandlakare.se/klinik/stockholm/alvsjo-tandvard/" target="_blank" rel="noopener" class="hb-medal-link">
          <img src="https://swordfish.templweb.com/wp-content/uploads/2026/05/medal_pink-2023.webp" alt="Rekommenderad klinik 2023 – Tandläkare.se">
        </a>
      </div>
    </div>
  </div>

  <div class="hb-stats hb-stats-desktop container-wide">
    <div><span class="hb-stat-val">{{stat_1_val}}</span><span class="hb-stat-lbl">{{stat_1_lbl}}</span></div>
    <div><span class="hb-stat-val">{{stat_2_val}}</span><span class="hb-stat-lbl">{{stat_2_lbl}}</span></div>
    <div><span class="hb-stat-val">{{stat_3_val}}</span><span class="hb-stat-lbl">{{stat_3_lbl}}</span></div>
    <div><span class="hb-stat-val">{{stat_4_val}}</span><span class="hb-stat-lbl">{{stat_4_lbl}}</span></div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/hero",
        "title": "Hero",
        "html_template": collapse(html),
        "schema": [
            {"name": "hero_image",  "type": "image",    "label": "Bakgrundsbild", "default": "https://swordfish.templweb.com/wp-content/uploads/2026/05/hero-1.jpg"},
            {"name": "eyebrow",     "type": "text",     "label": "Etikett",       "default": "Modern tandvård · 2 min från pendeln · Älvsjö"},
            {"name": "ingress",     "type": "textarea", "label": "Ingress",       "default": "Från första undersökningen till implantat och Invisalign — en nyrenoverad klinik mitt i Älvsjö där varje besök är utformat för att du ska känna dig lugn och omhändertagen."},
            {"name": "stat_1_val",  "type": "text",     "label": "Stat 1 – värde",  "default": "Gratis"},
            {"name": "stat_1_lbl",  "type": "text",     "label": "Stat 1 – etikett","default": "Barn t.o.m. 19"},
            {"name": "stat_2_val",  "type": "text",     "label": "Stat 2 – värde",  "default": "Idag"},
            {"name": "stat_2_lbl",  "type": "text",     "label": "Stat 2 – etikett","default": "Akut hjälp"},
            {"name": "stat_3_val",  "type": "text",     "label": "Stat 3 – värde",  "default": "6 dagar"},
            {"name": "stat_3_lbl",  "type": "text",     "label": "Stat 3 – etikett","default": "Öppet i veckan"},
            {"name": "stat_4_val",  "type": "text",     "label": "Stat 4 – värde",  "default": "0% ränta"},
            {"name": "stat_4_lbl",  "type": "text",     "label": "Stat 4 – etikett","default": "Delbetalning"},
        ],
    }


BASE_IMG = "https://swordfish.templweb.com/wp-content/uploads/2026/05/"

def build_treatments_grid() -> dict:
    TREATMENTS = [
        ("Akuttandvård",            "Tider samma dag",    True,  "/akut-tandvard",           "t-akut.jpg"),
        ("Implantat",               "Specialistteam",     False, "/implantat",               "t-implantat.jpg"),
        ("Karies / Hål i tanden",   "Allmäntandvård",     False, "/karies-hal-i-tanden",     "t-karies.jpg"),
        ("Tandblekning",            "Klinik & hemma",     False, "/tandblekning",             "t-tandblekning.jpg"),
        ("Tandfasader / Veneers",   "Estetisk tandvård",  False, "/tandfasader-veneers",      "t-tandfasader.jpg"),
        ("Tandreglering",           "Invisalign",         False, "/tandreglering-stockholm",  "t-tandreglering.jpg"),
        ("Tandsten / Tandhygienist","Förebyggande vård",  False, "/tandsten-tandhygienist",   "t-tandsten.jpg"),
        ("Tandvårdsrädsla",         "Lugnande vård",      False, "/tandvardsradsla",          "t-tandradsla.jpg"),
    ]

    cards_html = ""
    for i, (name, count, badge, href, img) in enumerate(TREATMENTS, start=1):
        badge_html = (
            f'<div class="tc-badge"><span class="tc-badge-dot"></span>Öppet nu</div>'
            if badge else ""
        )
        cards_html += f"""
<a href="{{{{card_{i}_url}}}}" class="treatment-card">
  <div class="tc-bg" style="background-image:url({{{{card_{i}_image}}}});"></div>
  <div class="tc-overlay"></div>
  <div class="tc-body">
    <div class="tc-top">
      <div class="tc-count">{{{{card_{i}_count}}}}</div>
      {badge_html}
    </div>
    <div><div class="tc-name">{{{{card_{i}_name}}}}</div></div>
  </div>
</a>"""

    html = f"""
<section class="treatments-section section">
  <div class="container-wide">
    <div class="treatments-hdr">
      <div>
        <div class="eyebrow">01 / Behandlingar</div>
        <h2>Ett komplett utbud, under ett tak.</h2>
      </div>
      <div class="treatments-hdr-meta">
        <p>Från regelbunden tandvård till specialistbehandlingar — alltid utförda på plats av våra egna tandläkare.</p>
        <a href="#tdl-booking-widget" class="treatments-hdr-link">Till bokningskalendern →</a>
      </div>
    </div>
    <div class="treatments-grid">{cards_html}</div>
  </div>
</section>
"""
    schema = []
    for i, (name, count, _, href, img) in enumerate(TREATMENTS, start=1):
        schema.append({"name": f"card_{i}_name",  "type": "text",  "label": f"Kort {i} – namn",      "default": name})
        schema.append({"name": f"card_{i}_count", "type": "text",  "label": f"Kort {i} – kategori",  "default": count})
        schema.append({"name": f"card_{i}_image", "type": "image", "label": f"Kort {i} – bild",      "default": BASE_IMG + img})
        schema.append({"name": f"card_{i}_url",   "type": "url",   "label": f"Kort {i} – länk",      "default": href})

    return {
        "block_name": "lumo/treatments-grid",
        "title": "Behandlingar – grid",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_reviews_section() -> dict:
    html = """
<section class="reviews-section section">
  <div class="container-wide">
    <div class="reviews-hdr">
      <div>
        <div class="eyebrow">02 / Patientomdömen</div>
        <h2>{{heading}}</h2>
      </div>
    </div>
    <div class="reviews-widget-wrap">{{site_reviews_testimonials}}</div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/reviews-section",
        "title": "Recensioner",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "<span style=\"font-style:italic;\">Tusentals</span> nöjda patienter i Stockholm."},
        ],
    }


def build_about() -> dict:
    html = """
<section class="about-section section">
  <div class="container-wide">
    <div class="about-grid">
      <div class="about-text">
        <div class="eyebrow" style="margin-bottom:16px;">03 / Om kliniken</div>
        <h2>{{heading}}</h2>
        <p class="lead">{{lead_text}}</p>
        <p>{{body}}</p>
        <a href="/om-oss" class="btn btn-ghost">Läs mer om oss</a>
      </div>
      <div class="about-img">
        <img src="{{about_image}}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;">
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/about",
        "title": "Om kliniken",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik",
             "default": "Trygghet och kvalitet för ditt leende."},
            {"name": "lead_text", "type": "textarea", "label": "Ingress",
             "default": "Vår nyrenoverade och luftiga klinik på Prästgårdsgränd 4 erbjuder en lugn, modern miljö där vi tar hand om dig och din familj med professionalism och värme."},
            {"name": "body", "type": "textarea", "label": "Brödtext",
             "default": "För de yngre familjemedlemmarna har vi även Älvsjö Pedodonti, en specialistenhet för barn och unga upp till 23 år. Vi är anslutna till Försäkringskassan och erbjuder räntefri delbetalning."},
            {"name": "about_image", "type": "image", "label": "Bild",
             "default": "https://swordfish.templweb.com/wp-content/uploads/2026/05/undersok.jpg"},
        ],
    }


def build_emergency_banner() -> dict:
    html = f"""
<section class="emergency-banner" id="emergency">
  <div class="container-wide">
    <div class="emergency-inner">
      <div class="eb-24-block">
        <span class="eb-label">Akut</span>
        <span class="eb-number">Samma dag</span>
      </div>
      <div class="eb-text">
        <h2>Akut tandvärk? Vi prioriterar dig samma dag.</h2>
        <p>Ring oss direkt på <strong>{{{{site_phone}}}}</strong> om du behöver omedelbar hjälp. Vi prioriterar akuta patienter och strävar efter att erbjuda dig en tid samma dag.</p>
      </div>
      <div class="eb-cta">
        <a href="tel:{{{{site_phone}}}}" class="eb-phone">{ICO_PHONE} {{{{site_phone}}}}</a>
        <a href="#tdl-booking-widget" class="btn btn-light btn-sm">Boka akuttid →</a>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/emergency-banner",
        "title": "Akutbanner",
        "html_template": collapse(html),
        "schema": [],
    }


def build_team() -> dict:
    MEMBERS = [
        ("Adel",       "VD · Tandhygienist"),
        ("Aslan",      "Tandläkare"),
        ("Mike",       "Tandläkare"),
        ("Ghiyas",     "Tandläkare"),
        ("Airo",       "Tandläkare"),
        ("Bindu",      "Tandläkare"),
        ("Ashfa",      "Tandläkare"),
        ("Aleksandra", "Tandläkare"),
        ("Arezoo",     "Tandläkare"),
        ("Loren",      "Tandläkare"),
        ("Marcel",     "Tandläkare"),
        ("Ahmed",      "Tandhygienist"),
        ("Sibel",      "Reception · Tandhygienist"),
        ("Badeel",     "Tandsköterska"),
        ("Evin",       "Tandsköterska"),
        ("Erika",      "Tandsköterska"),
        ("Maxim",      "Ekonomi"),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
    ]

    members_html = ""
    for i, (name, role) in enumerate(MEMBERS, start=1):
        members_html += f"""
<article class="team-member">
  <div class="team-photo" style="background-image:url({{{{member_{i}_photo}}}});"></div>
  <div>
    <div class="team-name">{{{{member_{i}_name}}}}</div>
    <div class="team-role">{{{{member_{i}_role}}}}</div>
  </div>
</article>"""

    html = f"""
<section class="team-section section" id="team">
  <div class="container-wide">
    <div class="team-hdr">
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">04 / Teamet</div>
        <h2>Erfarna och engagerade — för ditt leende.</h2>
      </div>
      <div class="team-hdr-right">
        <p>Tandläkare, tandhygienister och tandsköterskor som brinner för din munhälsa. Vi vidareutbildar oss kontinuerligt och möter dig alltid med tid, lugn och förståelse.</p>
        <a href="/om-oss" class="btn btn-ghost">Lär känna oss</a>
      </div>
    </div>
    <div class="team-grid">{members_html}</div>
  </div>
</section>
"""
    schema = []
    for i, (name, role) in enumerate(MEMBERS, start=1):
        slug = name.lower()
        photo_default = f"{BASE_IMG}staff-{slug}.jpg" if name else ""
        schema.append({"name": f"member_{i}_name",  "type": "text",  "label": f"Person {i} – namn",  "default": name})
        schema.append({"name": f"member_{i}_role",  "type": "text",  "label": f"Person {i} – roll",  "default": role})
        field = {"name": f"member_{i}_photo", "type": "image", "label": f"Person {i} – foto"}
        if photo_default:
            field["default"] = photo_default
        schema.append(field)

    return {
        "block_name": "lumo/team",
        "title": "Team",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_photo_tour() -> dict:
    # 5 tiles in a 12-column masonry layout
    TILES = [
        ("tile_1", "Receptionen",       "span 7", "span 3", "reception.jpg"),
        ("tile_2", "Behandlingsrum 04", "span 5", "span 2", "clinic-room-1.jpg"),
        ("tile_3", "Röntgenavdelning",  "span 5", "span 1", "intraoral-rontgen.jpg"),
        ("tile_4", "Sterilcentral",     "span 5", "span 2", "clinic-detail-1.jpg"),
        ("tile_5", "Operationsrum",     "span 7", "span 2", "clinic-room-2.jpg"),
    ]

    tiles_html = ""
    for key, label_default, cols, rows, img in TILES:
        tiles_html += f"""
<div class="pt-tile" style="grid-column:{cols};grid-row:{rows};">
  <div class="pt-tile-bg" style="background-image:url({{{{pt_{key}_image}}}});"></div>
  <div class="pt-overlay"></div>
  <div class="pt-label">{{{{pt_{key}_label}}}}</div>
</div>"""

    html = f"""
<section class="photo-tour section">
  <div class="container-wide">
    <div class="pt-hdr">
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">05 / Klinikens lokaler</div>
        <h2>{{{{heading}}}}</h2>
      </div>
    </div>
    <div class="pt-grid">{tiles_html}</div>
  </div>
</section>
"""
    schema = [{"name": "heading", "type": "text", "label": "Rubrik", "default": "14 behandlingsrum. 1 200 m² över två våningar."}]
    for key, label_default, _, _, img in TILES:
        schema.append({"name": f"pt_{key}_image", "type": "image", "label": f"{label_default} – bild", "default": BASE_IMG + img})
        schema.append({"name": f"pt_{key}_label", "type": "text",  "label": f"{label_default} – text", "default": label_default})

    return {
        "block_name": "lumo/photo-tour",
        "title": "Fotogalleri – kliniken",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_site_footer() -> dict:
    hours = [
        ("Måndag",  "{{site_hours_monday}}"),
        ("Tisdag",  "{{site_hours_tuesday}}"),
        ("Onsdag",  "{{site_hours_wednesday}}"),
        ("Torsdag", "{{site_hours_thursday}}"),
        ("Fredag",  "{{site_hours_friday}}"),
        ("Lördag",  "{{site_hours_saturday}}"),
        ("Söndag",  "{{site_hours_sunday}}"),
    ]
    hours_html = "".join(
        f'<div class="footer-day"><span class="footer-day-name">{d}</span><span class="footer-day-hours">{h}</span></div>'
        for d, h in hours
    )

    partners_logos = build_partners_logos_html()

    html = f"""
<footer class="site-footer">
  <div class="footer-partners">
    <div class="container-wide">
      <p class="ps-eyebrow">Vi stödjer &amp; samarbetar med</p>
      <div class="ps-logos">{partners_logos}</div>
    </div>
  </div>
  <div class="container-wide" style="padding-top:96px;">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="{LOGO_WHITE}" alt="Älvsjö Tandvård" class="footer-brand-logo">
        <div class="footer-contact">
          <div class="footer-contact-row">{ICO_PIN}<div>{{{{site_address}}}}</div></div>
          <a href="tel:{{{{site_phone}}}}">{ICO_PHONE} {{{{site_phone}}}}</a>
          <a href="mailto:{{{{site_email}}}}" style="color:rgba(255,255,255,0.7);">{ICO_MAIL} {{{{site_email}}}}</a>
        </div>
      </div>
      <div class="footer-col">
        <div class="footer-col-title">Behandlingar</div>
        <ul>
          <li><a href="/akut-tandvard">Akuttandvård</a></li>
          <li><a href="/implantat">Implantat</a></li>
          <li><a href="/karies-hal-i-tanden">Karies / Hål</a></li>
          <li><a href="/tandblekning">Tandblekning</a></li>
          <li><a href="/tandfasader-veneers">Tandfasader</a></li>
          <li><a href="/tandreglering-stockholm">Tandreglering</a></li>
          <li><a href="/tandsten-tandhygienist">Tandsten</a></li>
          <li><a href="/tandvardsradsla">Tandvårdsrädsla</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <div class="footer-col-title">Kliniken</div>
        <ul>
          <li><a href="/om-oss">Om oss</a></li>
          <li><a href="/pedodonti">Barnspecialist</a></li>
          <li><a href="/lista-dig">Lista dig</a></li>
          <li><a href="/remiss-2">Remiss</a></li>
          <li><a href="/kampanjer">Kampanjer</a></li>
          <li><a href="/rantefritt">Räntefri delbetalning</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <div class="footer-col-title">Patient</div>
        <ul>
          <li><a href="#tdl-booking-widget">Boka tid</a></li>
          <li><a href="https://minatider.alvsjotandvard.se/?src=site">Mina tider</a></li>
          <li><a href="/kontakt">Kontakt</a></li>
          <li><a href="/kontakt">Hitta hit</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-hours">{hours_html}</div>

    <div class="footer-legal">
      <div>{{{{copyright_text}}}}</div>
      <div class="footer-legal-links">
        <a href="/integritetspolicy">Integritetspolicy</a>
        <a href="/cookies">Cookies</a>
        <a href="/personalinggang">Personalingång</a>
      </div>
    </div>
  </div>
</footer>
"""
    return {
        "block_name": "lumo/site-footer",
        "title": "Sidfot",
        "html_template": collapse(html),
        "schema": [
            {"name": "copyright_text", "type": "text", "label": "Copyright",
             "default": "© 2026 Älvsjö Tandvård AB · Org.nr 559089-8598"},
        ],
    }


# ---------------------------------------------------------------------------
# Subpage components (shared across treatment/info pages)
# ---------------------------------------------------------------------------

def build_contact_panel() -> dict:
    html = f"""
<section style="background:var(--blush-200);padding:96px 0;">
  <div class="container-wide">
    <div style="display:grid;grid-template-columns:1fr 1.4fr;gap:80px;">
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">Kontakt</div>
        <h3 style="font-family:var(--font-sans);font-size:18px;font-weight:500;text-transform:uppercase;letter-spacing:0.18em;color:var(--ink-700);margin:0 0 22px;">{{{{heading}}}}</h3>
        <p style="font-family:var(--font-sans);font-size:15px;line-height:1.65;color:var(--ink-600);margin:0 0 24px;max-width:520px;">{{{{intro_text}}}}</p>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div style="display:flex;align-items:center;gap:10px;font-size:14px;color:var(--blush-700);">{ICO_PHONE}<a href="tel:+46812854555" style="color:var(--blush-700);">{{{{site_phone}}}}</a></div>
          <div style="display:flex;align-items:center;gap:10px;font-size:14px;color:var(--blush-700);">{ICO_MAIL}<a href="mailto:{{{{site_email}}}}" style="color:var(--blush-700);">{{{{site_email}}}}</a></div>
          <div style="display:flex;align-items:center;gap:10px;font-size:14px;color:var(--blush-700);margin-top:8px;">{ICO_PIN}<a href="https://maps.google.com/?q={ADDRESS_ENC}" target="_blank" rel="noopener" style="color:var(--blush-700);">{{{{site_address}}}}</a></div>
        </div>
      </div>
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">Öppettider</div>
        <div style="white-space:pre-line;font-family:var(--font-sans);font-size:14px;color:var(--ink-600);line-height:1.9;">{{{{site_opening_hours}}}}</div>
      </div>
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
        ],
    }


def build_faq() -> dict:
    rows = "".join(
        f'<details><summary>{{{{q_{i}}}}}</summary><p>{{{{a_{i}}}}}</p></details>'
        for i in range(1, 7)
    )
    html = f"""
<section style="padding:96px 0;background:var(--paper);">
  <div style="max-width:860px;margin:0 auto;padding:0 var(--gutter);">
    <div class="eyebrow" style="display:block;text-align:center;margin-bottom:16px;">Vanliga frågor</div>
    <h2 style="font-family:var(--font-serif);font-weight:500;font-size:clamp(28px,2.6vw,40px);line-height:1.15;letter-spacing:-0.02em;color:var(--ink-700);text-align:center;margin:0 0 48px;">{{{{heading}}}}</h2>
    <style>
      .lumo-faq details{{border-top:1px solid var(--border);padding:22px 0;}}
      .lumo-faq details:last-of-type{{border-bottom:1px solid var(--border);}}
      .lumo-faq details:has(summary:empty){{display:none;}}
      .lumo-faq summary{{list-style:none;cursor:pointer;font-family:var(--font-sans);font-size:17px;font-weight:500;color:var(--ink-700);display:flex;justify-content:space-between;align-items:center;}}
      .lumo-faq summary::-webkit-details-marker{{display:none;}}
      .lumo-faq summary::after{{content:"+";color:var(--blush-600);font-size:22px;font-weight:300;}}
      .lumo-faq details[open] summary::after{{content:"−";}}
      .lumo-faq details p{{font-family:var(--font-sans);font-size:15px;line-height:1.7;color:var(--fg);margin:14px 0 0;max-width:60ch;}}
    </style>
    <div class="lumo-faq">{rows}</div>
  </div>
</section>
"""
    schema = [{"name": "heading", "type": "text", "label": "Rubrik", "default": "Frågor och svar"}]
    for i in range(1, 7):
        schema += [
            {"name": f"q_{i}", "type": "text",     "label": f"Fråga {i}"},
            {"name": f"a_{i}", "type": "textarea",  "label": f"Svar {i}"},
        ]
    return {
        "block_name": "lumo/faq",
        "title": "FAQ",
        "html_template": collapse(html),
        "schema": schema,
    }


def build_treatment_hero(slug: str) -> dict:
    d = TREATMENT_HERO_DATA[slug]
    b = d["bullets"]
    html = f"""
<section class="treatment-hero">
  <div class="th-inner">
    <div class="eyebrow" style="margin-bottom:20px;color:var(--sage-600);">{{{{eyebrow}}}}</div>
    <div class="th-grid">
      <div class="th-left">
        <h1>{{{{title}}}} <em>{{{{title_italic}}}}</em></h1>
        <div>
          <p class="lead th-lead">{{{{ingress}}}}</p>
          <div class="th-bullets">
            <div class="th-bullet"><span class="th-num">01</span>{{{{bullet_1}}}}</div>
            <div class="th-bullet"><span class="th-num">02</span>{{{{bullet_2}}}}</div>
            <div class="th-bullet"><span class="th-num">03</span>{{{{bullet_3}}}}</div>
            <div class="th-bullet"><span class="th-num">04</span>{{{{bullet_4}}}}</div>
          </div>
          <div style="display:flex;gap:12px;">
            <a href="#tdl-booking-widget" class="btn btn-primary">Boka tid</a>
            <a href="tel:+46812854555" class="btn btn-ghost">Ring oss</a>
          </div>
        </div>
      </div>
      <div class="th-right">
        <div class="th-photo" style="background-image:url({{{{hero_image}}}});"></div>
        <div class="th-stat">
          <div class="th-stat-label">{{{{stat_label}}}}</div>
          <div class="th-stat-value">{{{{stat_value}}}}</div>
          <div class="th-stat-sub">{{{{stat_sub}}}}</div>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": f"lumo/treatment-hero-{slug}",
        "title": f"Treatment Hero – {d['eyebrow']}",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",      "type": "text",     "label": "Etikett",       "default": d["eyebrow"]},
            {"name": "title",        "type": "text",     "label": "Rubrik",        "default": d["title"]},
            {"name": "title_italic", "type": "text",     "label": "Rubrik (kursiv)","default": d["title_italic"]},
            {"name": "ingress",      "type": "textarea", "label": "Ingress",       "default": d["ingress"]},
            {"name": "bullet_1",     "type": "text",     "label": "Punkt 1",       "default": b[0]},
            {"name": "bullet_2",     "type": "text",     "label": "Punkt 2",       "default": b[1]},
            {"name": "bullet_3",     "type": "text",     "label": "Punkt 3",       "default": b[2]},
            {"name": "bullet_4",     "type": "text",     "label": "Punkt 4",       "default": b[3]},
            {"name": "hero_image",   "type": "image",    "label": "Foto (höger)"},
            {"name": "stat_label",   "type": "text",     "label": "Stat: etikett", "default": d["stat_label"]},
            {"name": "stat_value",   "type": "text",     "label": "Stat: värde",   "default": d["stat_value"]},
            {"name": "stat_sub",     "type": "text",     "label": "Stat: förklaring","default": d["stat_sub"]},
        ],
    }


def build_page_hero_info() -> dict:
    """Shared hero template for info pages: Om oss, Kontakt, Barnspecialist."""
    html = """
<section class="page-hero">
  <div class="container-wide">
    <div class="eyebrow" style="margin-bottom:32px;color:var(--sage-600);">{{eyebrow}}</div>
    <div class="ph-grid">
      <h1>{{title}}<br><em>{{title_italic}}</em></h1>
      <div class="ph-right">
        <p class="lead ph-lead">{{ingress}}</p>
        <div class="ph-bullets">
          <div class="ph-bullet"><span class="ph-num">01</span>{{bullet_1}}</div>
          <div class="ph-bullet"><span class="ph-num">02</span>{{bullet_2}}</div>
          <div class="ph-bullet"><span class="ph-num">03</span>{{bullet_3}}</div>
          <div class="ph-bullet"><span class="ph-num">04</span>{{bullet_4}}</div>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <a href="{{cta_1_href}}" class="btn btn-primary btn-lg">{{cta_1_text}}</a>
          <a href="{{cta_2_href}}" class="btn btn-ghost btn-lg">{{cta_2_text}}</a>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/page-hero-info",
        "title": "Page Hero – Info (delad mall)",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",      "type": "text",     "label": "Etikett (t.ex. N° 02 — Om oss)"},
            {"name": "title",        "type": "text",     "label": "Rubrik"},
            {"name": "title_italic", "type": "text",     "label": "Rubrik (kursiv del)"},
            {"name": "ingress",      "type": "textarea", "label": "Ingress"},
            {"name": "bullet_1",     "type": "text",     "label": "Punkt 1"},
            {"name": "bullet_2",     "type": "text",     "label": "Punkt 2"},
            {"name": "bullet_3",     "type": "text",     "label": "Punkt 3"},
            {"name": "bullet_4",     "type": "text",     "label": "Punkt 4"},
            {"name": "cta_1_text",   "type": "text",     "label": "Knapp 1 – text"},
            {"name": "cta_1_href",   "type": "text",     "label": "Knapp 1 – länk"},
            {"name": "cta_2_text",   "type": "text",     "label": "Knapp 2 – text"},
            {"name": "cta_2_href",   "type": "text",     "label": "Knapp 2 – länk"},
        ],
    }


def build_page_hero_barnspecialist() -> dict:
    d = BARNSPECIALIST_DATA
    b = d["bullets"]
    html = f"""
<section class="page-hero">
  <div class="container-wide">
    <div class="eyebrow" style="margin-bottom:32px;color:var(--sage-600);">{{{{eyebrow}}}}</div>
    <div class="ph-grid">
      <h1>{{{{title}}}} <em>{{{{title_italic}}}}</em></h1>
      <div class="ph-right">
        <p class="lead ph-lead">{{{{ingress}}}}</p>
        <div class="ph-bullets">
          <div class="ph-bullet"><span class="ph-num">01</span>{{{{bullet_1}}}}</div>
          <div class="ph-bullet"><span class="ph-num">02</span>{{{{bullet_2}}}}</div>
          <div class="ph-bullet"><span class="ph-num">03</span>{{{{bullet_3}}}}</div>
          <div class="ph-bullet"><span class="ph-num">04</span>{{{{bullet_4}}}}</div>
        </div>
        <div style="display:flex;gap:12px;">
          <a href="#tdl-booking-widget" class="btn btn-primary btn-lg">Boka tid</a>
          <a href="tel:+46812854555" class="btn btn-ghost btn-lg">Ring oss</a>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/page-hero-barnspecialist",
        "title": "Page Hero – Barnspecialist",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",      "type": "text",     "label": "Etikett",        "default": d["eyebrow"]},
            {"name": "title",        "type": "text",     "label": "Rubrik",         "default": d["title"]},
            {"name": "title_italic", "type": "text",     "label": "Rubrik (kursiv)","default": d["title_italic"]},
            {"name": "ingress",      "type": "textarea", "label": "Ingress",        "default": d["ingress"]},
            {"name": "bullet_1",     "type": "text",     "label": "Punkt 1",        "default": b[0]},
            {"name": "bullet_2",     "type": "text",     "label": "Punkt 2",        "default": b[1]},
            {"name": "bullet_3",     "type": "text",     "label": "Punkt 3",        "default": b[2]},
            {"name": "bullet_4",     "type": "text",     "label": "Punkt 4",        "default": b[3]},
        ],
    }


def build_fact_strip_barnspecialist() -> dict:
    cells = "".join(
        f'<div class="fs-cell"><div class="fs-value">{{{{val_{i}}}}}</div><div class="fs-label">{{{{label_{i}}}}}</div></div>'
        for i in range(1, 5)
    )
    return {
        "block_name": "lumo/fact-strip-barnspecialist",
        "title": "Fact Strip – Barnspecialist",
        "html_template": f'<section class="fact-strip"><div class="container-wide"><div class="fs-grid">{cells}</div></div></section>',
        "schema": [
            {"name": "val_1",   "type": "text", "label": "Fakt 1 – värde",  "default": "19 år"},
            {"name": "label_1", "type": "text", "label": "Fakt 1 – text",   "default": "Gratis tandvård för barn och unga upp till 19 år."},
            {"name": "val_2",   "type": "text", "label": "Fakt 2 – värde",  "default": "23 år"},
            {"name": "label_2", "type": "text", "label": "Fakt 2 – text",   "default": "Specialistvård via Älvsjö Pedodonti upp till 23 år."},
            {"name": "val_3",   "type": "text", "label": "Fakt 3 – värde",  "default": "Region"},
            {"name": "label_3", "type": "text", "label": "Fakt 3 – text",   "default": "Vi arbetar på uppdrag av Region Stockholm."},
            {"name": "val_4",   "type": "text", "label": "Fakt 4 – värde",  "default": "Muntra"},
            {"name": "label_4", "type": "text", "label": "Fakt 4 – text",   "default": "Vi tar emot remisser via Muntra."},
        ],
    }


def build_page_hero_kontakt() -> dict:
    html = """
<section class="page-hero">
  <div class="container-wide">
    <div class="eyebrow" style="margin-bottom:32px;color:var(--sage-600);">N° 04 — Kontakt</div>
    <div class="ph-grid">
      <h1>Mitt i Älvsjö, <em>2 min från pendeln.</em></h1>
      <div class="ph-right">
        <p class="lead ph-lead">Vi finns här för dig — för rutinundersökning eller akut hjälp. Välkommen till en modern klinik där du känner dig sedd.</p>
        <div class="ph-bullets">
          <div class="ph-bullet"><span class="ph-num">01</span>Prästgårdsgränd 4</div>
          <div class="ph-bullet"><span class="ph-num">02</span>2 min från pendeln</div>
          <div class="ph-bullet"><span class="ph-num">03</span>08-12 85 45 55</div>
          <div class="ph-bullet"><span class="ph-num">04</span>Öppet måndag–lördag</div>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <a href="#kontaktformular" class="btn btn-primary btn-lg">Skriv till oss</a>
          <a href="tel:+46812854555" class="btn btn-ghost btn-lg">Ring oss</a>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/page-hero-kontakt",
        "title": "Page Hero – Kontakt",
        "html_template": collapse(html),
        "schema": [],
    }


def build_contact_grid() -> dict:
    html = f"""
<section class="contact-grid">
  <div class="container-wide">
    <div class="eyebrow" style="margin-bottom:16px;">Kontakt</div>
    <h2 style="margin-bottom:40px;">{{{{heading}}}}</h2>
    <div class="cg-inner">
      <div class="cg-card">
        <div class="eyebrow">Adress</div>
        <a href="https://maps.google.com/?q={ADDRESS_ENC}" target="_blank" rel="noopener" class="cg-h">{{{{site_address}}}}</a>
        <div class="cg-sub">{{{{address_sub}}}}</div>
        <div class="cg-note">{{{{address_note}}}}</div>
      </div>
      <div class="cg-card">
        <div class="eyebrow">Telefon</div>
        <a href="tel:+46812854555" class="cg-h">{{{{site_phone}}}}</a>
        <div class="cg-sub">{{{{phone_sub}}}}</div>
        <div class="cg-note">{{{{phone_note}}}}</div>
      </div>
      <div class="cg-card">
        <div class="eyebrow">E-post</div>
        <a href="mailto:{{{{site_email}}}}" class="cg-h">{{{{site_email}}}}</a>
        <div class="cg-sub">{{{{email_sub}}}}</div>
        <div class="cg-note">{{{{email_note}}}}</div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/contact-grid",
        "title": "Kontaktgrid",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading",      "type": "text",     "label": "Rubrik",               "default": "Hur når du oss?"},
            {"name": "address_sub",  "type": "text",     "label": "Adress – undertext",   "default": "125 44 Älvsjö"},
            {"name": "address_note", "type": "textarea", "label": "Adress – not",         "default": "2 min från pendeltågsstationen · Intill Vårdcentralen · Hiss"},
            {"name": "phone_sub",    "type": "text",     "label": "Telefon – undertext",  "default": "Tidsbokning · akuta besvär"},
            {"name": "phone_note",   "type": "textarea", "label": "Telefon – not",        "default": "Vi prioriterar akuta patienter — ring tidigt för bästa tid samma dag."},
            {"name": "email_sub",    "type": "text",     "label": "E-post – undertext",   "default": "Svar inom 1 arbetsdag"},
            {"name": "email_note",   "type": "textarea", "label": "E-post – not",         "default": "För remisser, fakturafrågor och allmänna ärenden."},
        ],
    }


def build_map_hours_kontakt() -> dict:
    hours = [
        ("Måndag",  "{{site_hours_monday}}"),
        ("Tisdag",  "{{site_hours_tuesday}}"),
        ("Onsdag",  "{{site_hours_wednesday}}"),
        ("Torsdag", "{{site_hours_thursday}}"),
        ("Fredag",  "{{site_hours_friday}}"),
        ("Lördag",  "{{site_hours_saturday}}"),
        ("Söndag",  "{{site_hours_sunday}}"),
    ]
    rows = "".join(
        f'<div class="mh-row"><span class="mh-day">{d}</span>'
        f'<span class="mh-time">{h}</span></div>'
        for d, h in hours
    )
    html = f"""
<section class="map-hours" id="hitta-till-oss">
  <div class="container-wide">
    <div class="eyebrow" style="margin-bottom:16px;">Hitta till oss</div>
    <h2 style="margin-bottom:40px;">{{{{heading}}}}</h2>
    <div class="mh-grid">
      <div class="mh-map">
        <iframe src="https://maps.google.com/maps?q={ADDRESS_ENC}&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen title="Karta — Älvsjö Tandvård" style="position:absolute;inset:0;width:100%;height:100%;border:0;display:block;"></iframe>
      </div>
      <div class="mh-hours">
        <div class="eyebrow" style="margin-bottom:20px;">Öppettider</div>
        {rows}
        <div class="mh-note">{{{{emergency_note}}}}</div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/map-hours-kontakt",
        "title": "Karta + Öppettider",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading",        "type": "text",     "label": "Rubrik",    "default": "Mitt i Älvsjö, 2 min från pendeln."},
            {"name": "emergency_note", "type": "textarea", "label": "Akut-text", "default": "<strong style=\"color:var(--ink-700);\">Akut?</strong> Ring 08-12 85 45 55 så snart som möjligt — vi gör vårt bästa för att ge dig en tid samma dag."},
        ],
    }


def build_contact_form() -> dict:
    html = """
<section class="contact-form-section" id="kontaktformular">
  <div class="container-wide">
    <div class="cf-grid">
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">Skriv till oss</div>
        <h2>{{heading}}</h2>
        <p style="font-size:15px;color:var(--ink-500);max-width:40ch;line-height:1.7;">{{intro}}</p>
      </div>
      <form class="lumo-contact-form" novalidate>
        <input type="text" name="website" style="display:none;" tabindex="-1" autocomplete="off">
        <label><span class="lbl">Förnamn</span><input type="text" name="fornamn" required></label>
        <label><span class="lbl">Efternamn</span><input type="text" name="efternamn" required></label>
        <label class="full"><span class="lbl">E-post</span><input type="email" name="email" required></label>
        <label class="full"><span class="lbl">Telefon</span><input type="tel" name="phone"></label>
        <label class="full"><span class="lbl">Ärende</span><textarea name="arende" rows="5" required></textarea></label>
        <p class="lumo-form-msg"></p>
        <div class="cf-submit">
          <button type="submit" class="btn btn-primary">Skicka meddelande →</button>
        </div>
      </form>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/contact-form",
        "title": "Kontaktformulär",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text",     "label": "Rubrik",   "default": "Inte akut? Skriv så hörs vi av."},
            {"name": "intro",   "type": "textarea", "label": "Brödtext", "default": "Vi svarar inom en arbetsdag. För akuta besvär, ring oss istället på 08-12 85 45 55."},
        ],
    }


def build_text_blocks_om_oss() -> dict:
    html = """
<section class="tb-section">
  <div class="container-wide">
    <div class="tb-hdr">
      <div class="eyebrow">{{eyebrow}}</div>
      <h2>{{heading}}</h2>
    </div>
    <div class="tb-grid">
      <article class="tb-block">
        <div class="tb-num">01</div>
        <h3>{{block_1_h3}}</h3>
        <p>{{block_1_body}}</p>
      </article>
      <article class="tb-block">
        <div class="tb-num">02</div>
        <h3>{{block_2_h3}}</h3>
        <p>{{block_2_body}}</p>
      </article>
      <article class="tb-block">
        <div class="tb-num">03</div>
        <h3>{{block_3_h3}}</h3>
        <p>{{block_3_body}}</p>
      </article>
      <article class="tb-block">
        <div class="tb-num">04</div>
        <h3>{{block_4_h3}}</h3>
        <p>{{block_4_body}}</p>
      </article>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/text-blocks-om-oss",
        "title": "Textblock – Om oss",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",    "type": "text",     "label": "Etikett",       "default": "Så arbetar vi"},
            {"name": "heading",    "type": "text",     "label": "Rubrik",        "default": "Fyra principer som vägleder varje besök."},
            {"name": "block_1_h3", "type": "text",     "label": "Block 1 – rubrik",    "default": "Vår filosofi och approach till tandvård"},
            {"name": "block_1_body","type":"textarea", "label": "Block 1 – text",      "default": "På Älvsjö Tandvård bygger vår filosofi på att se hela människan, inte bara tänderna. Vi tror på vikten av att skapa en förtroendefull relation där du känner dig trygg att ställa frågor och dela dina funderingar. Vår approach innebär att vi alltid börjar med att lyssna, för att sedan tillsammans med dig skapa en individuell behandlingsplan som möter dina unika behov och förväntningar."},
            {"name": "block_2_h3", "type": "text",     "label": "Block 2 – rubrik",    "default": "Teamet — bakgrund och kompetens"},
            {"name": "block_2_body","type":"textarea", "label": "Block 2 – text",      "default": "Vårt team består av erfarna och engagerade tandläkare, tandhygienister och tandsköterskor som brinner för ditt leende och din munhälsa. Vi arbetar kontinuerligt med att vidareutveckla vår kompetens och hålla oss uppdaterade med de senaste forskningsrönen och teknikerna inom tandvården."},
            {"name": "block_3_h3", "type": "text",     "label": "Block 3 – rubrik",    "default": "Kliniken — miljö och utrustning"},
            {"name": "block_3_body","type":"textarea", "label": "Block 3 – text",      "default": "Vår klinik är inte bara nyrenoverad och estetiskt tilltalande, den är också utrustad med den senaste tekniken. Vi erbjuder digital scanning för avtryck, panoramaröntgen och CBCT för detaljerade 3D-bilder av dina käkar — exakta diagnoser och noggranna behandlingsplaner."},
            {"name": "block_4_h3", "type": "text",     "label": "Block 4 – rubrik",    "default": "Trygghet vid tandvårdsrädsla"},
            {"name": "block_4_body","type":"textarea", "label": "Block 4 – text",      "default": "Vi förstår att tandvårdsrädsla är vanligt och möter dig med extra tid och förståelse. Vi börjar alltid med ett lugnt samtal där du får berätta om dina tidigare erfarenheter. Vi anpassar tempot helt efter dig, erbjuder pauser och förklarar varje steg tydligt."},
        ],
    }


def build_organisation_om_oss() -> dict:
    benefits = "".join(
        f'<div class="org-benefit"><span class="org-benefit-num">0{i}</span>{{{{benefit_{i}}}}}</div>'
        for i in range(1, 6)
    )
    html = f"""
<section class="org-section" id="organisation">
  <div class="container-wide">
    <div class="org-hdr">
      <div class="eyebrow">Organisation</div>
      <h2>{{{{heading}}}}</h2>
    </div>
    <div class="org-grid">
      <div>
        <p class="org-lead">{{{{lead}}}}</p>
        <div class="eyebrow" style="margin-bottom:20px;">Ta del av företagsförmånerna ni också</div>
        <div class="org-benefits">{benefits}</div>
      </div>
      <div class="org-form-wrap">
        <div class="eyebrow">Kontakta oss</div>
        <form class="lumo-contact-form" novalidate style="margin-top:20px;">
          <input type="text" name="website" style="display:none;" tabindex="-1" autocomplete="off">
          <label class="full"><span class="lbl">Firmatecknare</span><input type="text" name="fornamn" required placeholder="För- och efternamn"></label>
          <label class="full"><span class="lbl">E-post</span><input type="email" name="email" required placeholder="foretagets@email.se"></label>
          <label class="full"><span class="lbl">Telefon</span><input type="tel" name="phone" required placeholder="08-XXX XX XX"></label>
          <label class="full"><span class="lbl">Organisationsnummer</span><input type="text" name="arende" required placeholder="556XXX-XXXX"></label>
          <p class="lumo-form-msg"></p>
          <div class="cf-submit"><button type="submit" class="btn btn-primary">Skicka förfrågan</button></div>
        </form>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/organisation-om-oss",
        "title": "Organisation – Företagstandvård",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading",    "type": "text",     "label": "Rubrik",      "default": "Företagstandvård — en förmån som gör skillnad."},
            {"name": "lead",       "type": "textarea", "label": "Ingress",     "default": "Det finns många fördelar med att erbjuda tandvård till sina medarbetare. Intresserad av att veta mer? Fyll i kontaktformuläret så återkommer vi med allt du behöver veta."},
            {"name": "benefit_1",  "type": "text",     "label": "Förmån 1",   "default": "Stärk dina medarbetares hälsa utan extra kostnad"},
            {"name": "benefit_2",  "type": "text",     "label": "Förmån 2",   "default": "Få förmånliga priser på tandvård"},
            {"name": "benefit_3",  "type": "text",     "label": "Förmån 3",   "default": "Inga kötider — snabba tider för era medarbetare"},
            {"name": "benefit_4",  "type": "text",     "label": "Förmån 4",   "default": "Vi erbjuder tider även efter ordinarie arbetstider"},
            {"name": "benefit_5",  "type": "text",     "label": "Förmån 5",   "default": "Gör dig till en mer attraktiv arbetsgivare"},
        ],
    }


def build_arbeta_med_oss() -> dict:
    offers = "".join(
        f'<div class="arbeta-item"><span class="arbeta-item-num">0{i}</span>{{{{offer_{i}}}}}</div>'
        for i in range(1, 6)
    )
    reqs = "".join(
        f'<div class="arbeta-req"><span class="arbeta-req-dot"></span>{{{{req_{i}}}}}</div>'
        for i in range(1, 8)
    )
    tools = "".join(
        f'<div class="arbeta-tool">{{{{tool_{i}}}}}</div>'
        for i in range(1, 5)
    )
    html = f"""
<section class="arbeta-section" id="arbeta-med-oss">
  <div class="container-wide">
    <div class="arbeta-hdr">
      <div class="eyebrow">Arbeta med oss</div>
      <h2>{{{{heading}}}}</h2>
    </div>
    <div class="arbeta-grid">
      <div>
        <p class="arbeta-lead">{{{{lead}}}}</p>
        <div class="arbeta-list-hdr">Vi erbjuder bland annat</div>
        <div class="arbeta-items">{offers}</div>
        <div class="arbeta-actions">
          <a href="mailto:{{{{site_email}}}}" class="btn btn-light btn-lg">Skicka ansökan</a>
          <a href="tel:{{{{site_phone}}}}" class="btn btn-white-ghost btn-lg">Ring oss</a>
        </div>
      </div>
      <div>
        <div class="arbeta-list-hdr">Vi söker dig som har</div>
        <div class="arbeta-reqs">{reqs}</div>
        <div class="arbeta-list-hdr">Systemen vi använder</div>
        <div class="arbeta-tools">{tools}</div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/arbeta-med-oss",
        "title": "Arbeta med oss",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text",     "label": "Rubrik",   "default": "Vi söker duktiga och ambitiösa kollegor."},
            {"name": "lead",    "type": "textarea", "label": "Ingress",  "default": "Älvsjö Tandvård växer och vi söker tandläkare, tandhygienister och tandsköterskor som vill vara med på resan. Vår vision är att erbjuda all tandvård inom alla inriktningar under samma tak — i nyrenoverade, luftiga lokaler mitt i Älvsjö."},
            {"name": "offer_1", "type": "text", "label": "Erbjudande 1", "default": "Kirurgi och implantatbehandlingar"},
            {"name": "offer_2", "type": "text", "label": "Erbjudande 2", "default": "Tandreglering och Invisalign"},
            {"name": "offer_3", "type": "text", "label": "Erbjudande 3", "default": "Digital scanning och CBCT"},
            {"name": "offer_4", "type": "text", "label": "Erbjudande 4", "default": "Barnspecialisttandvård"},
            {"name": "offer_5", "type": "text", "label": "Erbjudande 5", "default": "Panoramaröntgen"},
            {"name": "req_1",   "type": "text", "label": "Krav 1",       "default": "Yrkeslegitimation från Socialstyrelsen"},
            {"name": "req_2",   "type": "text", "label": "Krav 2",       "default": "Erfarenhet"},
            {"name": "req_3",   "type": "text", "label": "Krav 3",       "default": "Flytande svenska i både tal och skrift"},
            {"name": "req_4",   "type": "text", "label": "Krav 4",       "default": "Passion för yrket"},
            {"name": "req_5",   "type": "text", "label": "Krav 5",       "default": "Ambition att utvecklas"},
            {"name": "req_6",   "type": "text", "label": "Krav 6",       "default": "God kommunikativ förmåga"},
            {"name": "req_7",   "type": "text", "label": "Krav 7",       "default": "Stresstålig — behålla lugnet under stressiga situationer"},
            {"name": "tool_1",  "type": "text", "label": "Verktyg 1",    "default": "Journalsystem: Muntra"},
            {"name": "tool_2",  "type": "text", "label": "Verktyg 2",    "default": "Röntgenprogram: DentalEye"},
            {"name": "tool_3",  "type": "text", "label": "Verktyg 3",    "default": "Maskinell rens: WaveOne"},
            {"name": "tool_4",  "type": "text", "label": "Verktyg 4",    "default": "Implantatsystem: Implant Direct / Straumann"},
        ],
    }


def build_feedback_form_om_oss() -> dict:
    html = """
<section class="feedback-section" id="hjalp-oss-bli-bast">
  <div class="container-wide">
    <div class="feedback-grid">
      <div>
        <div class="eyebrow feedback-eyebrow">Hjälp oss bli bäst</div>
        <h2>{{heading}}</h2>
        <p class="feedback-lead">{{body}}</p>
        <p class="feedback-prize">{{prize_note}}</p>
      </div>
      <div class="feedback-form-wrap">
        <form class="lumo-contact-form" novalidate>
          <input type="text" name="website" style="display:none;" tabindex="-1" autocomplete="off">
          <label class="full"><span class="lbl">E-post <span style="font-weight:400;opacity:0.6;">(valfritt)</span></span><input type="email" name="email" placeholder="din@email.se"></label>
          <label class="full"><span class="lbl">Ämne</span><input type="text" name="fornamn" required placeholder="Vad gäller din feedback?"></label>
          <label class="full"><span class="lbl">Meddelande</span><textarea name="arende" rows="5" required placeholder="Berätta vad du tyckte om ditt besök…"></textarea></label>
          <p class="lumo-form-msg"></p>
          <div class="cf-submit"><button type="submit" class="btn btn-primary btn-lg">Skicka feedback</button></div>
        </form>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/feedback-form-om-oss",
        "title": "Feedbackformulär – Om oss",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading",    "type": "text",     "label": "Rubrik",      "default": "Vi vill bli bäst — och det kräver din hjälp."},
            {"name": "body",       "type": "textarea", "label": "Brödtext",    "default": "Dina synpunkter är ovärderliga, speciellt de som handlar om saker vi kan bli bättre på. Genom att dela med dig av din upplevelse hjälper du oss att förbättra vården för alla våra patienter."},
            {"name": "prize_note", "type": "text",     "label": "Pristext",    "default": "Som tack för din feedback har du chansen att bli utvald för en kostnadsfri eltandborste."},
        ],
    }


def build_cta_strip_om_oss() -> dict:
    html = """
<section class="cta-strip">
  <div class="container-wide cs-grid">
    <div>
      <h2>{{heading}}</h2>
      <p class="cs-sub">{{sub}}</p>
    </div>
    <div class="cs-actions">
      <a href="#tdl-booking-widget" class="btn btn-light btn-lg">Boka tid</a>
      <a href="tel:+46812854555" class="btn btn-white-ghost btn-lg">08 — 12 85 45 55</a>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/cta-strip-om-oss",
        "title": "CTA-strip – Om oss",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text",     "label": "Rubrik",  "default": "Välkommen till oss."},
            {"name": "sub",     "type": "textarea", "label": "Undertext","default": "Ring 08-12 85 45 55 eller boka online. Vi tar emot nya patienter och prioriterar akuta besvär."},
        ],
    }


def build_remiss_widget() -> dict:
    html = """
<section style="background:var(--cream);min-height:60vh;padding:var(--space-10) 0;">
  <div class="container-wide">
    <div class="eyebrow" style="margin-bottom:24px;">Remiss</div>
    <h1 style="font-family:var(--font-serif);font-weight:400;font-size:clamp(32px,3vw,52px);line-height:1.15;letter-spacing:-0.02em;color:var(--ink-700);margin:0 0 48px;">Skicka en remiss till oss.</h1>
    <div class="muntra-referral-widget" muntra_clinic_id="753"></div>
    <script type="text/javascript" src="https://muntra-dev.github.io/referral-page/index.js"></script>
  </div>
</section>
"""
    return {
        "block_name": "lumo/remiss-widget",
        "title": "Remissformulär (Muntra)",
        "html_template": collapse(html),
        "schema": [],
    }


def build_cta_strip(slug: str) -> dict:
    if slug == "barnspecialist":
        d = BARNSPECIALIST_DATA
    elif slug == "kontakt":
        d = KONTAKT_CTA_DATA
    else:
        d = TREATMENT_HERO_DATA[slug]
    html = f"""
<section class="cta-strip">
  <div class="container-wide">
    <div class="cs-grid">
      <div>
        <h2>{{{{cta_title}}}}</h2>
        <p class="cs-sub">{{{{cta_sub}}}}</p>
      </div>
      <div class="cs-actions">
        <a href="#tdl-booking-widget" class="btn btn-light btn-lg">Boka tid</a>
        <a href="tel:+46812854555" class="btn btn-white-ghost btn-lg">08 — 12 85 45 55</a>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": f"lumo/cta-strip-{slug}",
        "title": f"CTA Strip – {slug.replace('-', ' ').title()}",
        "html_template": collapse(html),
        "schema": [
            {"name": "cta_title", "type": "text",     "label": "CTA-rubrik", "default": d["cta_title"]},
            {"name": "cta_sub",   "type": "textarea", "label": "CTA-text",   "default": d["cta_sub"]},
        ],
    }


def build_content_block(block_name: str, title: str, mirror: bool) -> dict:
    text_order = "2" if mirror else "1"
    img_order  = "1" if mirror else "2"
    html = f"""
<section class="cb-section" style="background:var(--white);">
  <div class="container-wide">
    <div class="cb-grid cb-grid--{'mirror' if mirror else 'normal'}">
      <div class="cb-text">
        <div class="eyebrow" style="margin-bottom:16px;">{{{{eyebrow}}}}</div>
        <h2 style="font-family:var(--font-serif);font-weight:500;font-size:clamp(28px,2.6vw,40px);line-height:1.15;letter-spacing:-0.02em;color:var(--ink-700);margin:0 0 24px;">{{{{h2}}}}</h2>
        <div style="font-family:var(--font-sans);font-size:16px;line-height:1.7;color:var(--fg);">{{{{body}}}}</div>
        <div style="margin-top:32px;display:flex;gap:12px;flex-wrap:wrap;">
          <a href="{{{{cta_link}}}}" class="btn btn-primary">{{{{cta_text}}}}</a>
        </div>
      </div>
      <div class="cb-img">
        <img src="{{{{image}}}}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;">
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": block_name,
        "title": title,
        "html_template": collapse(html),
        "schema": [
            {"name": "image",    "type": "image",    "label": "Bild"},
            {"name": "eyebrow",  "type": "text",     "label": "Etikett"},
            {"name": "h2",       "type": "text",     "label": "Rubrik"},
            {"name": "body",     "type": "textarea", "label": "Brödtext (HTML tillåten)"},
            {"name": "cta_text", "type": "text",     "label": "CTA-text", "default": "Boka tid"},
            {"name": "cta_link", "type": "url",      "label": "CTA-länk", "default": "#tdl-booking-widget"},
        ],
    }


def build_map_section() -> dict:
    html = f"""
<section id="hitta-till-oss" style="padding:96px 0;background:var(--white);">
  <div class="container-wide" style="text-align:center;">
    <div class="eyebrow" style="display:inline-block;margin-bottom:16px;">Hitta hit</div>
    <h2 style="font-family:var(--font-serif);font-weight:500;font-size:clamp(28px,2.6vw,40px);line-height:1.15;letter-spacing:-0.02em;color:var(--ink-700);margin:0 0 14px;">{{{{heading}}}}</h2>
    <p style="font-family:var(--font-sans);font-size:16px;line-height:1.65;color:var(--fg);margin:0 auto 36px;max-width:540px;">{{{{intro_text}}}}</p>
    <div style="position:relative;width:100%;aspect-ratio:16/9;border-radius:var(--radius-sm);overflow:hidden;border:1px solid var(--border);">
      <iframe src="https://maps.google.com/maps?q={ADDRESS_ENC}&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen title="Karta — Älvsjö Tandvård" style="position:absolute;inset:0;width:100%;height:100%;border:0;display:block;"></iframe>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/map-section",
        "title": "Kartsektion",
        "html_template": collapse(html),
        "schema": [
            {"name": "heading", "type": "text", "label": "Rubrik", "default": "Hitta till oss"},
            {"name": "intro_text", "type": "textarea", "label": "Introtext",
             "default": "Vi ligger vid Prästgårdsgränd 4 i Älvsjö — bara 2 minuter från Älvsjö pendeltågsstation."},
        ],
    }


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def make_variant(base: dict, suffix: str, overrides: dict, title_sfx: str = "") -> dict:
    v = copy.deepcopy(base)
    v["block_name"] = f"{v['block_name']}-{suffix}"
    if title_sfx:
        v["title"] = f"{v['title']} – {title_sfx}"
    for field in v["schema"]:
        if field["name"] in overrides:
            field["default"] = overrides[field["name"]]
    return v


def build_site(bases: dict) -> tuple[list, list]:
    variants, pages = [], []
    seen: set = set()

    def add(key: str, suffix: str, overrides: dict = {}, title_sfx: str = "") -> str:
        v = make_variant(bases[key], suffix, overrides, title_sfx)
        if v["block_name"] not in seen:
            seen.add(v["block_name"])
            variants.append(v)
        return v["block_name"]

    # ── Hem ────────────────────────────────────────────────────────────────
    blocks = [
        "lumo/site-header",
        "lumo/hero",           # single global hero (no variant needed)
        "lumo/treatments-grid",
        "lumo/reviews-section",
        "lumo/about",
        "lumo/emergency-banner",
        "lumo/team",
        "lumo/photo-tour",
        "lumo/site-footer",
    ]
    pages.append({"title": "Hem", "slug": "hem", "menu_label": None, "blocks": blocks})

    # ── Om oss ─────────────────────────────────────────────────────────────
    blocks = [
        "lumo/site-header",
        "lumo/page-hero-info",
        add("content-block-1", "om-oss", {
            "eyebrow": "Vårt uppdrag",
            "h2": "Din tandhälsa — vårt uppdrag, din trygghet.",
            "body": "<p>På Älvsjö Tandvård är vår vision att erbjuda en tandvårdsupplevelse där du känner dig helt trygg och sedd, oavsett ditt behov. Vår <strong>nyrenoverade klinik</strong> på Prästgårdsgränd 4, bara ett stenkast från Älvsjö pendeltågsstation, är designad för att vara ljus, luftig och tillgänglig — med hiss för din bekvämlighet.</p><p>Hos oss hittar du ett brett spektrum av tandvårdstjänster, från <strong>allmäntandvård och förebyggande vård</strong> för hela familjen, till mer avancerade behandlingar som <strong>tandimplantat</strong> och <strong>osynlig tandreglering med Invisalign</strong>. Vi är anslutna till Försäkringskassan och erbjuder räntefri delbetalning.</p>",
            "cta_text": "Boka tid",
            "cta_link": "#tdl-booking-widget",
        }, "Om oss"),
        "lumo/text-blocks-om-oss",
        "lumo/team",
        "lumo/organisation-om-oss",
        add("map-section", "om-oss", {"heading": "Hitta till kliniken"}, "Om oss"),
        "lumo/arbeta-med-oss",
        "lumo/feedback-form-om-oss",
        "lumo/cta-strip-om-oss",
        "lumo/site-footer",
    ]
    pages.append({"title": "Om oss", "slug": "om-oss", "menu_label": "Om oss", "blocks": blocks})

    # ── Kontakt ────────────────────────────────────────────────────────────
    blocks = [
        "lumo/site-header",
        "lumo/page-hero-info",
        "lumo/cta-strip-kontakt",
        "lumo/contact-grid",
        "lumo/map-hours-kontakt",
        "lumo/contact-form",
        "lumo/site-footer",
    ]
    pages.append({"title": "Kontakt", "slug": "kontakt", "menu_label": "Kontakt", "blocks": blocks})

    # ── Remiss ─────────────────────────────────────────────────────────────
    blocks = ["lumo/site-header", "lumo/remiss-widget", "lumo/site-footer"]
    pages.append({"title": "Remiss", "slug": "remiss-2", "menu_label": None, "blocks": blocks})

    # ── Behandlingssidor ────────────────────────────────────────────────────
    treatment_pages = [
        ("akut-tandvard",           "Akuttandvård",             "Behandlingar", "Akuttandvård i Älvsjö — tid samma dag"),
        ("implantat",               "Implantat",                "Behandlingar", "Tandimplantat i Älvsjö"),
        ("karies-hal-i-tanden",     "Karies / Hål i tanden",    "Behandlingar", "Karies och hål i tanden"),
        ("tandblekning",            "Tandblekning",             "Behandlingar", "Tandblekning i Älvsjö"),
        ("tandfasader-veneers",     "Tandfasader / Veneers",    "Behandlingar", "Tandfasader och veneers i Älvsjö"),
        ("tandreglering-stockholm", "Tandreglering",            "Behandlingar", "Tandreglering och Invisalign"),
        ("tandsten-tandhygienist",  "Tandsten / Tandhygienist", "Behandlingar", "Tandstensbehandling och tandhygienist"),
        ("tandvardsradsla",         "Tandvårdsrädsla",          "Behandlingar", "Tandvård för rädda patienter"),
    ]

    for slug, menu_label, parent, h1 in treatment_pages:
        d = TREATMENT_HERO_DATA[slug]
        blocks = [
            "lumo/site-header",
            f"lumo/treatment-hero-{slug}",
            add("content-block-1", slug, {
                "eyebrow": "Behandling", "h2": d["title"] + " " + d["title_italic"],
                "body": f"<p>{d['ingress']}</p>",
            }, menu_label),
            add("faq", slug, {"heading": "Frågor och svar"}, menu_label),
            f"lumo/cta-strip-{slug}",
            add("contact-panel", slug, {
                "heading": "Kontakta oss",
                "intro_text": "Har du frågor om behandlingen? Vi hjälper dig gärna.",
            }, menu_label),
            "lumo/site-footer",
        ]
        active = slug in ACTIVE_TREATMENTS
        p = {
            "title": h1, "slug": slug, "blocks": blocks,
            "menu_label": menu_label if active else None,
            "menu_parent": parent if active else None,
            "status": "publish" if active else "draft",
        }
        pages.append(p)

    # ── Barnspecialist (PageHero + FactStrip) ───────────────────────────────
    db = BARNSPECIALIST_DATA
    blocks = [
        "lumo/site-header",
        "lumo/page-hero-info",
        "lumo/fact-strip-barnspecialist",
        add("content-block-1", "barnspecialist", {
            "eyebrow": "Älvsjö Pedodonti",
            "h2":      "Anpassad specialistvård med omtanke.",
            "body":    "<p>Älvsjö Pedodonti är vår specialistklinik för <strong>barn och unga upp till 23 års ålder</strong>. Vi arbetar på uppdrag av Region Stockholm och tar emot remisser via Muntra för att säkerställa expertis och trygg vård för ditt barn.</p><p>För en trygg upplevelse erbjuder vi <strong>lustgas, lugnande medel (Midazolam) och i särskilda fall narkosbehandling</strong>. Tandvård är alltid <strong>gratis för barn och ungdomar upp till 19 år</strong>.</p>",
            "cta_text": "Skicka remiss",
            "cta_link": "/remiss-2",
        }, "Barnspecialist"),
        add("faq", "barnspecialist", {
            "heading": "Frågor från föräldrar.",
            "q_1": "Vilka kan få specialisttandvård hos Älvsjö Pedodonti?",
            "a_1": "Älvsjö Pedodonti är en specialistklinik för barn och unga upp till 23 år. Vi tar emot remisser via Muntra och arbetar på uppdrag av Region Stockholm för att erbjuda specialistvård.",
            "q_2": "Vad gör ni om mitt barn är rädd för tandläkaren?",
            "a_2": "Vi möter rädda barn med extra tålamod och anpassad omsorg. Vårt team är specialiserat på psykologisk omvårdnad och erbjuder vid behov lustgas, lugnande medel eller narkos för en trygg upplevelse.",
            "q_3": "Kostar tandvården något för barn?",
            "a_3": "Nej, hos Älvsjö Tandvård är all tandvård alltid gratis för barn och ungdomar upp till 19 år. Det gäller både allmäntandvård och specialisttandvård på remiss.",
        }, "Barnspecialist"),
        "lumo/cta-strip-barnspecialist",
        add("contact-panel", "barnspecialist", {
            "heading": "Kontakta oss",
            "intro_text": "Har du frågor om barnspecialistvård? Vi hjälper dig gärna.",
        }, "Barnspecialist"),
        "lumo/site-footer",
    ]
    pages.append({"title": "Barnspecialist (Pedodonti) i Älvsjö", "slug": "pedodonti",
                  "menu_label": "Barnspecialist", "blocks": blocks})

    return variants, pages


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    tokens_css = TOKENS_FILE.read_text(encoding="utf-8")

    # Global components (no variants)
    site_header  = build_site_header(tokens_css)
    site_footer  = build_site_footer()
    hero         = build_hero()
    treatments   = build_treatments_grid()
    reviews      = build_reviews_section()
    about        = build_about()
    emergency    = build_emergency_banner()
    team         = build_team()
    photo_tour   = build_photo_tour()

    bases = {
        "hero":            hero,
        "content-block-1": build_content_block("lumo/content-block-1", "Innehållsblock", False),
        "contact-panel":   build_contact_panel(),
        "faq":             build_faq(),
        "map-section":     build_map_section(),
    }

    # Treatment hero + CTA strip per page
    treatment_heroes = [build_treatment_hero(slug) for slug in TREATMENT_HERO_DATA]
    cta_strips = [build_cta_strip(slug) for slug in list(TREATMENT_HERO_DATA) + ["barnspecialist", "kontakt"]]
    page_hero_info = build_page_hero_info()
    barnspecialist_comps = [build_page_hero_barnspecialist(), build_fact_strip_barnspecialist()]
    kontakt_comps = [build_page_hero_kontakt(), build_contact_grid(), build_map_hours_kontakt(), build_contact_form()]
    remiss_comp   = build_remiss_widget()
    om_oss_comps  = [
        build_text_blocks_om_oss(),
        build_organisation_om_oss(),
        build_arbeta_med_oss(),
        build_feedback_form_om_oss(),
        build_cta_strip_om_oss(),
    ]

    variants, pages = build_site(bases)

    # All global components + base contact/faq/map (not used on hem directly, but registered)
    global_components = [
        site_header, site_footer,
        hero, treatments, reviews, about, emergency, team, photo_tour,
        page_hero_info,
        *treatment_heroes, *cta_strips, *barnspecialist_comps, *kontakt_comps, *om_oss_comps, remiss_comp,
    ]

    bundle = {
        "site_name": "Älvsjö Tandvård",
        "platform_config": {"platform": "boxmedia"},
        "global_settings": {
            "site_company_name":  "Älvsjö Tandvård",
            "site_phone":         "08 – 12 85 45 55",
            "site_email":         "boka@alvsjotandvard.se",
            "site_address":       "Prästgårdsgränd 4, Älvsjö",
            "site_opening_hours": (
                "Måndag–Torsdag  07:00 – 20:00\n"
                "Fredag          07:00 – 17:00\n"
                "Lördag          09:00 – 15:00\n"
                "Söndag          Stängt"
            ),
            "site_hours_monday":    "07:00 – 20:00",
            "site_hours_tuesday":   "07:00 – 20:00",
            "site_hours_wednesday": "07:00 – 20:00",
            "site_hours_thursday":  "07:00 – 20:00",
            "site_hours_friday":    "07:00 – 17:00",
            "site_hours_saturday":  "09:00 – 15:00",
            "site_hours_sunday":    "Stängt",
            "site_booking_api_key": "f45e488e-9f0f-429b-8850-f729922f24c6",
        },
        "components": global_components + variants,
        "pages": pages,
        "extra_menu_items": [
            {"label": "Om kliniken",       "url": "/om-oss/",                       "parent": "Om oss"},
            {"label": "Vi som jobbar",     "url": "/om-oss/#team",                    "parent": "Om oss"},
            {"label": "Organisation",      "url": "/om-oss/#organisation",           "parent": "Om oss"},
            {"label": "Hitta till oss",    "url": "/om-oss/#hitta-till-oss",         "parent": "Om oss"},
            {"label": "Arbeta med oss",    "url": "/om-oss/#arbeta-med-oss",         "parent": "Om oss"},
            {"label": "Hjälp oss bli bäst","url": "/om-oss/#hjalp-oss-bli-bast",    "parent": "Om oss"},
        ],
    }

    OUT_FILE.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    size = OUT_FILE.stat().st_size
    print(f"[OK] Wrote {OUT_FILE.relative_to(ROOT)}")
    print(f"     Components: {len(bundle['components'])}")
    print(f"     Pages:      {len(bundle['pages'])}")
    print(f"     Size:       {size:,} bytes")


if __name__ == "__main__":
    main()
