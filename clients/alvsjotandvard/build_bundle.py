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
@media (max-width: 782px) { .admin-bar .site-header { top: 46px; } .admin-bar .mobile-nav { padding-top: 124px; } }
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
  padding: 16px 0 8px; min-width: 220px;
  flex-direction: column; gap: 0; border-radius: 4px; z-index: 60;
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
.nav-toggle { display: none; }
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
.nav-toggle:checked ~ .site-header .hamburger span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.nav-toggle:checked ~ .site-header .hamburger span:nth-child(2) { opacity: 0; }
.nav-toggle:checked ~ .site-header .hamburger span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }
/* Mobile nav — hardcoded accordion, shown only at ≤900px */
.mobile-nav { display: none; }
.mn-cb { display: none; }

/* ── Hero (HeroBleed) ───────────────────────────────────────────── */
@keyframes camera-drift {
  0%   { transform: scale(2.0) translate(-8%, 0%); }
  25%  { transform: scale(2.2) translate(-6%, 2%); }
  50%  { transform: scale(2.1) translate(-10%, -2%); }
  75%  { transform: scale(2.3) translate(-7%, -3%); }
  100% { transform: scale(2.0) translate(-9%, 3%); }
}
.hero-bleed {
  position: relative; min-height: min(82vh, 820px);
  background: #050505; display: flex; flex-direction: column;
  justify-content: flex-end; overflow: hidden;
}
.hero-bleed.hero-bg-video::after {
  content: "";
  position: absolute; inset: 0;
  background-image: url('https://upload.wikimedia.org/wikipedia/commons/7/76/1k_Dissolve_Noise_Texture.png');
  opacity: 0.15; mix-blend-mode: overlay; pointer-events: none; z-index: 2;
}
.hero-bleed .hb-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center; background-repeat: no-repeat;
  filter: saturate(1.05) brightness(0.75);
}
.hero-bleed .hb-bg-video {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  object-fit: cover;
  filter: blur(12px) brightness(0.55) contrast(1.5);
  z-index: 1;
  animation: camera-drift 10s ease-in-out infinite alternate;
}
.hero-bleed .hb-bg-video--mobile { display: none; }
.hero-bleed .hb-bg-video--desktop { opacity: 0; pointer-events: none; }
.hero-bleed .hb-overlay {
  position: absolute; inset: 0; z-index: 10;
  background: linear-gradient(180deg, rgba(20,20,18,0.55) 0%, rgba(20,20,18,0.30) 35%, rgba(20,20,18,0.88) 100%);
}
.hero-bleed .hb-top {
  position: absolute; top: 48px; left: 0; right: 0; z-index: 10;
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
  position: relative; z-index: 10;
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
/* Hero bg toggle button — only for logged-in admins */
@keyframes hb-toggle-pulse {
  0%   { transform: scale(1);   opacity: 0.75; }
  100% { transform: scale(2.4); opacity: 0; }
}
.hb-bg-toggle {
  display: none;
  position: absolute; bottom: 16px; right: 16px; z-index: 20;
  font-size: 11px; font-weight: 500; letter-spacing: 0.1em;
  color: #f97316; background: rgba(0,0,0,0.35);
  border: 1px solid rgba(249,115,22,0.5); border-radius: 4px;
  padding: 5px 10px; text-decoration: none; backdrop-filter: blur(4px);
  transition: color 0.2s, background 0.2s;
}
.hb-bg-toggle:hover { color: #fb923c; background: rgba(0,0,0,0.55); }
.hb-bg-toggle { display: block; }
.hb-bg-toggle::after {
  content: '';
  position: absolute;
  inset: -6px;
  border-radius: 8px;
  border: 2px solid rgba(249,115,22,0.8);
  pointer-events: none;
  opacity: 0;
}
.hb-bg-toggle.hb-pulse::after {
  animation: hb-toggle-pulse 1.1s ease-out forwards;
}
.hb-bg-toggle::before,
#header-style-toggle::before {
  content: attr(data-tip);
  position: absolute;
  background: rgba(10,10,10,0.92);
  color: #fff;
  font-size: 11px;
  font-weight: 400;
  line-height: 1.65;
  letter-spacing: 0;
  padding: 10px 13px;
  border-radius: 6px;
  width: 230px;
  white-space: normal;
  text-align: left;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.18s ease;
  z-index: 200;
  backdrop-filter: blur(6px);
}
.hb-bg-toggle::before {
  bottom: calc(100% + 10px);
  right: 0;
}
#header-style-toggle { position: relative; }
#header-style-toggle::before {
  top: calc(100% + 8px);
  left: 0;
}
.hb-bg-toggle:hover::before,
#header-style-toggle:hover::before { opacity: 1; }
.hero-bleed .hb-stats {
  position: relative; z-index: 10;
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

/* ── Coming-soon nav items (endast sidor ej lanserade än) ────────── */
.site-header nav a[href*="/lista-dig"],
.site-header nav a[href*="/rantefritt"],
.site-header nav a[href*="/kampanjer"],
.site-topstrip a[href*="/lista-dig"],
.mobile-nav a[href*="/lista-dig"],
.mobile-nav a[href*="/rantefritt"],
.mobile-nav a[href*="/kampanjer"] {
  opacity: 0.38 !important;
  pointer-events: none !important;
  cursor: default !important;
}
/* Desktop tooltip för ej lanserade sidor */
.site-header nav li:has(> a[href*="/rantefritt"]),
.site-header nav li:has(> a[href*="/kampanjer"]) { position: relative; }
.site-header nav li:has(> a[href*="/rantefritt"])::after,
.site-header nav li:has(> a[href*="/kampanjer"])::after {
  content: "Kommer snart";
  position: absolute; top: calc(100% + 8px); left: 50%; transform: translateX(-50%);
  background: rgba(10,10,10,0.9); color: #fff;
  font-family: var(--font-sans); font-size: 10px; font-weight: 500; letter-spacing: 0.08em;
  padding: 4px 9px; border-radius: 4px; white-space: nowrap;
  opacity: 0; pointer-events: none; z-index: 100; transition: opacity 0.15s ease;
}
.site-header nav li:has(> a[href*="/rantefritt"]):hover::after,
.site-header nav li:has(> a[href*="/kampanjer"]):hover::after { opacity: 1; }
/* Topstrip Lista dig — wrapper span för hover-tooltip */
.nav-cs { position: relative; display: inline-flex; align-items: center; }
.nav-cs::after {
  content: "Kommer snart";
  position: absolute; top: calc(100% + 6px); left: 50%; transform: translateX(-50%);
  background: rgba(10,10,10,0.9); color: #fff;
  font-family: var(--font-sans); font-size: 10px; font-weight: 500; letter-spacing: 0.08em;
  padding: 4px 9px; border-radius: 4px; white-space: nowrap;
  opacity: 0; pointer-events: none; z-index: 100; transition: opacity 0.15s ease;
}
.nav-cs:hover::after { opacity: 1; }
/* Mobil badge för ej lanserade sidor */
.mobile-nav a[href*="/rantefritt"]::after,
.mobile-nav a[href*="/kampanjer"]::after {
  content: "Kommer snart";
  display: inline-block; vertical-align: middle;
  font-size: 9px; letter-spacing: 0.06em; font-weight: 500;
  padding: 2px 6px; border-radius: 3px; margin-left: 10px;
  background: rgba(255,255,255,0.18);
}

/* ── Responsive ─────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .site-topstrip { display: none; }
  .site-header .hamburger { display: flex; }
  .header-style-toggle-mobile { display: flex !important; color: #f97316; }
  html.header-light .header-style-toggle-mobile { color: #ea6c00 !important; }
  /* Hide WP-generated nav on mobile; .mobile-nav takes over */
  .site-header nav { display: none !important; }
  /* Mobile nav drawer */
  .mobile-nav {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: var(--ink-700); overflow-y: auto; z-index: 40;
    padding-top: 78px; flex-direction: column;
  }
  .admin-bar .mobile-nav { padding-top: 110px; }
  .nav-toggle:checked ~ .mobile-nav { display: flex; }
  /* Mobile nav items */
  .mobile-nav .mn-item {
    border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex; flex-direction: column;
  }
  .mobile-nav .mn-top-row { display: flex; align-items: stretch; }
  .mobile-nav .mn-link {
    flex: 1; display: block; padding: 18px 24px;
    font-size: 16px; font-weight: 500; font-family: var(--font-sans);
    color: rgba(255,255,255,0.9) !important; text-decoration: none;
  }
  .mobile-nav .mn-link-label {
    flex: 1; display: block; padding: 18px 24px;
    font-size: 16px; font-weight: 500; font-family: var(--font-sans);
    color: rgba(255,255,255,0.9); cursor: pointer; user-select: none;
  }
  .mobile-nav .mn-arrow {
    flex-shrink: 0; width: 56px;
    display: flex; align-items: center; justify-content: center;
    border-left: 1px solid rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.45); font-size: 22px; cursor: pointer;
    transition: transform 0.2s, color 0.2s; user-select: none;
  }
  .mobile-nav .mn-sub {
    display: none; flex-direction: column;
    padding: 0; margin: 0; background: rgba(0,0,0,0.2);
  }
  .mobile-nav .mn-cb:checked ~ .mn-sub { display: flex; }
  .mobile-nav .mn-cb:checked ~ .mn-top-row .mn-arrow { transform: rotate(90deg); color: var(--white); }
  .mobile-nav .mn-sub a {
    display: block; padding: 13px 24px 13px 40px !important;
    font-size: 13px !important; font-weight: 400 !important; font-family: var(--font-sans);
    color: rgba(255,255,255,0.65) !important; text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin: 0 !important;
  }
  .mobile-nav .mn-sub a:last-child { border-bottom: none; }
  .mobile-nav .mn-item-cta { padding: 20px 24px; border-bottom: none; }
  .mobile-nav .mn-item-cta .btn {
    display: block; text-align: center;
    background: var(--white) !important; color: var(--ink-700) !important;
    border-color: var(--white) !important;
  }
  .mobile-nav .mn-utility {
    display: flex; align-items: center; gap: 16px;
    padding: 12px 24px;
    background: rgba(0,0,0,0.3);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    font-size: 12px; letter-spacing: 0.04em; font-family: var(--font-sans);
  }
  .mobile-nav .mn-utility a {
    color: rgba(255,255,255,0.7) !important; text-decoration: none;
  }
  .mobile-nav .mn-utility a:hover { color: var(--white) !important; }
  .mobile-nav .mn-utility .mn-util-sep { opacity: 0.3; }
  .hero-bleed .hb-top { display: none; }
  /* video: .hb-bg-video--desktop/.hb-bg-video--mobile — byt display:none/block för att aktivera */
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
.treatment-hero .th-mobile-bg { display:none; position:absolute; inset:0; background-size:cover; background-position:center; opacity:0.18; filter:saturate(0.6); }

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
.cb-section { padding:96px 0; }
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

/* ── Emergency Strip ────────────────────────────────────────── */
.emergency-strip { background:var(--sage-600); color:var(--white); padding:10px 0; }
.es-inner { display:flex; align-items:center; justify-content:space-between; gap:32px; flex-wrap:wrap; }
.es-left { display:flex; align-items:center; gap:20px; }
.es-dot { display:inline-flex; width:10px; height:10px; border-radius:50%; background:var(--white); flex-shrink:0;
  box-shadow:0 0 0 4px rgba(255,255,255,0.25); animation:es-pulse 2s ease-in-out infinite; }
@keyframes es-pulse { 0%,100%{ transform:scale(1);opacity:1; } 50%{ transform:scale(1.4);opacity:0.6; } }
.es-label { font-size:11px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; }
.es-serif { font-family:var(--font-serif); font-size:20px; font-weight:400; letter-spacing:-0.01em; }
.es-phone { display:inline-flex; align-items:center; gap:14px; color:var(--white); text-decoration:none;
  font-family:var(--font-serif); font-size:28px; font-weight:400; letter-spacing:-0.02em;
  padding-left:28px; border-left:1px solid rgba(255,255,255,0.3); }
.es-ring { font-size:10px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; font-family:var(--font-sans); }
@media (max-width:700px) { .es-serif { display:none; } .es-phone { border-left:none; padding-left:0; } }

/* ── Triage Grid ────────────────────────────────────────────── */
.triage-grid { background:var(--white); padding:var(--space-10) 0; }
.tg-header { display:grid; grid-template-columns:1fr auto; align-items:end; gap:32px; margin-bottom:56px; padding-bottom:32px; border-bottom:1px solid var(--border); }
.tg-header h2 { max-width:28ch; margin:0; }
.tg-sub { max-width:32ch; text-align:right; margin:0; }
.tg-cards { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--border); border:1px solid var(--border); }
.tg-card { background:var(--white); padding:40px 32px 36px; display:flex; flex-direction:column; gap:14px; min-height:240px; }
.tg-urgency { font-size:10px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; }
.tg-urgency--critical { color:var(--sage-700); }
.tg-urgency--urgent   { color:var(--sage-600); }
.tg-urgency--soon     { color:var(--ink-600); }
.tg-card h3 { font-family:var(--font-serif); font-weight:400; font-size:26px; line-height:1.2; letter-spacing:-0.02em; color:var(--ink-700); max-width:20ch; margin:0; }
.tg-card p  { font-size:14px; line-height:1.65; color:var(--ink-500); margin:0; }

/* ── Process Steps ──────────────────────────────────────────── */
.process-steps { background:var(--cream); padding:var(--space-10) 0; }
.ps-header { margin-bottom:64px; padding-bottom:32px; border-bottom:1px solid var(--border); }
.ps-header .eyebrow { margin-bottom:16px; }
.ps-header h2 { max-width:24ch; margin:0; }
.ps-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:64px; }
.ps-step { display:flex; flex-direction:column; gap:18px; }
.ps-num { font-family:var(--font-serif); font-weight:300; font-size:72px; line-height:1; letter-spacing:-0.03em; color:var(--sage-600); }
.ps-step h3 { font-family:var(--font-serif); font-weight:400; font-size:28px; line-height:1.2; letter-spacing:-0.02em; color:var(--ink-700); margin:0; }
.ps-step p  { font-size:15px; line-height:1.7; color:var(--ink-500); margin:0; }

/* ── Price Row ──────────────────────────────────────────────── */
.price-row { background:var(--white); padding:var(--space-10) 0; }
.price-row .pr-grid { display:grid; grid-template-columns:1fr 1.4fr; gap:80px; align-items:start; }
.price-row h2 { max-width:14ch; margin-bottom:24px; }
.price-row .pr-intro { margin-top:24px; font-size:15px; color:var(--ink-500); line-height:1.7; max-width:36ch; }
.price-row .pr-table { border-top:1px solid var(--border); }
.price-row .pr-row { display:grid; grid-template-columns:1fr auto; gap:24px; padding:22px 0; border-bottom:1px solid var(--border); align-items:baseline; }
.price-row .pr-label { font-size:16px; color:var(--ink-700); }
.price-row .pr-price { font-family:var(--font-serif); font-size:22px; font-weight:400; letter-spacing:-0.01em; color:var(--ink-700); white-space:nowrap; }

/* ── Info Grid — delad sektion-wrapper ──────────────────────── */
.ig-section { background:var(--white); padding:var(--space-10) 0; }
.ig-hdr { margin-bottom:56px; padding-bottom:32px; border-bottom:1px solid var(--border); }
.ig-hdr h2 { max-width:32ch; margin:8px 0 0; font-family:var(--font-serif); font-weight:400; font-size:clamp(28px,2.6vw,40px); line-height:1.15; letter-spacing:-0.02em; color:var(--ink-700); }
.ig-grid { display:grid; gap:1px; background:var(--border); border:1px solid var(--border); }
.ig-grid--3 { grid-template-columns:repeat(3,1fr); }
.ig-grid--4 { grid-template-columns:repeat(4,1fr); }

/* ── Method Comparison (Tandblekning) ───────────────────────── */
.mc-section { background:var(--white); padding:var(--space-10) 0; }
.mc-hdr { margin-bottom:56px; padding-bottom:32px; border-bottom:1px solid var(--border); }
.mc-hdr h2 { max-width:28ch; margin:8px 0 0; font-family:var(--font-serif); font-weight:400; font-size:clamp(28px,2.6vw,40px); line-height:1.15; letter-spacing:-0.02em; color:var(--ink-700); }
.mc-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--border); border:1px solid var(--border); }
.mc-item { background:var(--white); padding:40px 32px; display:flex; flex-direction:column; gap:16px; }
.mc-name-row { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
.mc-name { font-family:var(--font-serif); font-weight:400; font-size:28px; line-height:1.1; letter-spacing:-0.02em; color:var(--ink-700); margin:0; }
.mc-badge { font-size:9px; font-weight:600; letter-spacing:0.14em; text-transform:uppercase; color:var(--sage-600); padding:4px 8px; border:1px solid var(--border); white-space:nowrap; flex-shrink:0; margin-top:4px; }
.mc-meta { display:flex; flex-direction:column; gap:6px; }
.mc-meta-row { display:flex; gap:12px; align-items:baseline; }
.mc-meta-label { font-size:10px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; color:var(--fg-muted); min-width:48px; flex-shrink:0; }
.mc-meta-val { font-family:var(--font-serif); font-size:18px; color:var(--ink-700); letter-spacing:-0.01em; }
.mc-meta-val--accent { color:var(--sage-600); }
.mc-desc { font-size:14px; line-height:1.65; color:var(--ink-500); margin:0; padding-top:16px; border-top:1px solid var(--border); }

/* ── Process Steps 4-column variant ────────────────────────── */
.ps-grid--4 { grid-template-columns:repeat(4,1fr); gap:40px; }

@media (max-width: 900px) {
  .treatment-hero { height:auto; background:var(--ink-700) !important; position:relative; }
  .treatment-hero .th-grid { grid-template-columns:1fr; height:auto; }
  .treatment-hero .th-right { display:none; }
  .treatment-hero .th-mobile-bg { display:block; }
  .treatment-hero .th-inner { position:relative; z-index:1; }
  .treatment-hero h1 { color:var(--white); }
  .treatment-hero h1 em { color:var(--sage-300) !important; }
  .treatment-hero .th-lead { color:rgba(255,255,255,0.75) !important; }
  .treatment-hero .th-bullet { color:rgba(255,255,255,0.85) !important; }
  .treatment-hero .th-bullets { border-top-color:rgba(255,255,255,0.15) !important; }
  .treatment-hero .eyebrow { color:var(--sage-300) !important; }
  .treatment-hero .btn-ghost { color:var(--white); border-color:rgba(255,255,255,0.4); }
  .treatment-hero .btn-ghost:hover { background:rgba(255,255,255,0.1); }
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
  .tg-header { grid-template-columns:1fr; }
  .tg-header h2 { max-width:100%; }
  .tg-sub { text-align:left; max-width:100%; }
  .tg-cards { grid-template-columns:repeat(2,1fr); }
  .tg-card { min-height:auto; }
  .ps-header { margin-bottom:40px; }
  .ps-grid { grid-template-columns:1fr; gap:40px; }
  .ps-grid--4 { grid-template-columns:repeat(2,1fr); }
  .price-row .pr-grid { grid-template-columns:1fr; gap:40px; }
  .ig-grid--3, .ig-grid--4 { grid-template-columns:repeat(2,1fr); }
  .mc-grid { grid-template-columns:1fr; }
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
  .tg-cards { grid-template-columns:1fr; }
  .tg-card { padding:28px 20px; }
  .tg-card h3 { font-size:22px; }
  .ps-num { font-size:56px; }
  .ps-step h3 { font-size:24px; }
  .ps-grid--4 { grid-template-columns:1fr; }
  .price-row .pr-row { grid-template-columns:1fr; gap:4px; }
  .price-row .pr-price { font-size:18px; }
  .ig-grid--3, .ig-grid--4 { grid-template-columns:1fr; }
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
BASE_IMG = "https://swordfish.templweb.com/wp-content/uploads/2026/05/"

ACTIVE_TREATMENTS: set[str] = {
    "akut-tandvard",
    "implantat",
    "karies-hal-i-tanden",
    "tandblekning",
    "tandfasader-veneers",
    "tandreglering-stockholm",
    "tandsten-tandhygienist",
    "tandvardsradsla",
}

# ---------------------------------------------------------------------------
# Per-page hero data (from approved mockups in design-system/)
# ---------------------------------------------------------------------------
TREATMENT_HERO_DATA: dict[str, dict] = {
    "akut-tandvard": {
        "eyebrow":      "Akuttandvård",
        "title":        "Snabb hjälp",
        "title_italic": "när det gör ont.",
        "ingress":      "När olyckan är framme eller värken slår till behöver du snabb och trygg hjälp. Vi finns här för att lindra smärtan och åtgärda problemet — oftast redan samma dag.",
        "bullets":      ["Akuttider varje dag", "Oftast samma dag", "Erfaren expertis", "Centralt i Älvsjö"],
        "stat_label":   "Genomsnittlig väntetid",
        "stat_value":   "< 4 tim",
        "stat_sub":     "från första samtal till lindring för 9 av 10 akuta patienter.",
        "cta_title":    "Behöver du hjälp nu?",
        "cta_sub":      "Ring oss direkt — vi reserverar akuttider varje dag och hjälper dig ofta samma dag. 08 — 12 85 45 55.",
        "image":        "t-akut.jpg",
    },
    "implantat": {
        "eyebrow":      "Tandimplantat",
        "title":        "Permanenta tänder.",
        "title_italic": "För livet.",
        "ingress":      "Ett tandimplantat är den mest naturliga ersättningen för en förlorad tand — det ser ut, känns och fungerar precis som din egna tand. Vi planerar och utför hela behandlingen på plats.",
        "bullets":      ["3D-planering med CBCT", "Specialistteam på plats", "Räntefri delbetalning", "Livslång hållbarhet"],
        "stat_label":   "Lyckad integrering",
        "stat_value":   "96 %",
        "stat_sub":     "efter 10 år — meta-analys av 18 kliniska studier (PubMed 2019).",
        "cta_title":    "Boka implantatrådgivning",
        "cta_sub":      "Ring 08-12 85 45 55 eller boka online. Vi bedömer din situation kostnadsfritt vid konsultationsbesöket.",
        "image":        "t-implantat.jpg",
    },
    "karies-hal-i-tanden": {
        "eyebrow":      "Karies · Hål i tanden",
        "title":        "Snabb lagning —",
        "title_italic": "utan obehag.",
        "ingress":      "Karies är världens vanligaste sjukdom och kan drabba alla. Med modern kompositteknik lagar vi hål skonsamt, estetiskt och hållbart — och vi ser alltid till att du är bekväm under hela behandlingen.",
        "bullets":      ["Skonsamteknik", "Estetisk komposit", "Ingen smärta", "Snabb behandling"],
        "stat_label":   "Behandlingstid",
        "stat_value":   "20–45",
        "stat_sub":     "minuter för en standardfyllning.",
        "cta_title":    "Har du ont eller misstänker hål?",
        "cta_sub":      "Boka en tid idag — ju tidigare vi behandlar, desto enklare och billigare ingreppet. Ring 08-12 85 45 55.",
        "image":        "t-karies.jpg",
    },
    "tandblekning": {
        "eyebrow":      "Tandblekning",
        "title":        "Ljusare leende.",
        "title_italic": "Snabbt och säkert.",
        "ingress":      "Professionell tandblekning ger upp till 8–10 nyanser ljusare tänder — utan att skada emaljens struktur. Vi erbjuder klinikblekning, hemblekning och kombinationsmetoden.",
        "bullets":      ["Säkert & skonsamt", "Synligt resultat direkt", "Individuell anpassning", "Klinik & hemblekning"],
        "stat_label":   "Ljusare i snitt",
        "stat_value":   "7",
        "stat_sub":     "nyanser med professionell klinikblekning, enligt kliniska studier.",
        "cta_title":    "Boka en blekningskonsultation",
        "cta_sub":      "Vi bedömer dina tänder och rekommenderar rätt metod för dig. Ring 08-12 85 45 55 eller boka online.",
        "image":        "t-tandblekning.jpg",
    },
    "tandfasader-veneers": {
        "eyebrow":      "Tandfasader · Veneers",
        "title":        "Ditt drömleende —",
        "title_italic": "skräddarsytt.",
        "ingress":      "Tandfasader (veneers) är tunna porslinsskal som limmas på tandens framsida. De döljer missfärgningar, ojämnheter och mellanrum — och ger ett harmoniskt, naturligt leende.",
        "bullets":      ["Porslin & komposit", "Digitalt smile design", "Långvarig estetik", "Minimal preparation"],
        "stat_label":   "Hållbarhet",
        "stat_value":   "15–20",
        "stat_sub":     "år för porslinsfaner med god munhygien.",
        "cta_title":    "Boka en konsultation om tandfasader",
        "cta_sub":      "Vi skapar en digital preview av ditt leende — utan kostnad vid konsultationsbesöket. Ring 08-12 85 45 55.",
        "image":        "t-tandfasader.jpg",
    },
    "tandreglering-stockholm": {
        "eyebrow":      "Tandreglering · Invisalign",
        "title":        "Raka tänder.",
        "title_italic": "Utan byglar.",
        "ingress":      "Vi är certifierade Invisalign-leverantörer. Med klara, avtagbara skenor rätar vi ut dina tänder diskret och effektivt — anpassat till ditt vardagliga liv.",
        "bullets":      ["Certifierat Invisalign-team", "Digital 3D-planering", "Avtagbar — äter som vanligt", "Räntefri delbetalning"],
        "stat_label":   "Behandlingstid",
        "stat_value":   "6–24",
        "stat_sub":     "månader med Invisalign.",
        "cta_title":    "Boka en gratis Invisalign-konsultation",
        "cta_sub":      "Vi tar ett digitalt avtryck och visar dig ditt potentiella slutresultat — utan kostnad. Ring 08-12 85 45 55.",
        "image":        "t-tandreglering.jpg",
    },
    "tandsten-tandhygienist": {
        "eyebrow":      "Tandsten · Tandhygienist",
        "title":        "Professionell rengöring —",
        "title_italic": "grunden för allt.",
        "ingress":      "Regelbunden tandhygienistbehandling är det mest effektiva sättet att förebygga karies, tandlossning och dålig andedräkt. Våra erfarna tandhygienister rengör noggrant och ger dig verktygen för hemvård.",
        "bullets":      ["Ultraljudsrengöring", "Individuell riskbedömning", "Kostnadsfri för barn", "Ingen remiss krävs"],
        "stat_label":   "Rekommenderat intervall",
        "stat_value":   "6–12",
        "stat_sub":     "månader för de flesta vuxna.",
        "cta_title":    "Boka tandhygienistbesök",
        "cta_sub":      "Förebyggande vård är alltid billigare än behandling. Boka online eller ring 08-12 85 45 55.",
        "image":        "t-tandsten.jpg",
    },
    "tandvardsradsla": {
        "eyebrow":      "Tandvårdsrädsla",
        "title":        "Du bestämmer",
        "title_italic": "takten.",
        "ingress":      "Vi möter dagligen patienter med tandvårdsrädsla — från mild oro till svår fobi. Vår erfarenhet är att alla kan komma till en punkt där tandvård känns hanterbar. Vi börjar där du är, inte där vi tycker du borde vara.",
        "bullets":      ["Ingen dömande miljö", "Stop-signal alltid gäller", "Extra tid per patient", "Eventuellt lugnande"],
        "stat_label":   "Av befolkningen",
        "stat_value":   "50 %+",
        "stat_sub":     "uppger någon grad av oro inför tandläkarbesök.",
        "cta_title":    "Ta det första steget — vi möter dig där du är",
        "cta_sub":      "Ring 08-12 85 45 55 och berätta om din rädsla. Vi lyssnar, anpassar och skapar ett besök som fungerar för just dig.",
        "image":        "t-tandradsla.jpg",
    },
}

# ---------------------------------------------------------------------------
# Per-page content-block-1 and FAQ data for each treatment page
# Keys: cb1_{eyebrow,h2,body,image,cta_text,cta_link}, faq_{heading,q1,a1...q4,a4}
# ---------------------------------------------------------------------------
TREATMENT_PAGE_DATA: dict[str, dict] = {
    "akut-tandvard": {
        "cb1_eyebrow":  "Vad vi gör",
        "cb1_h2":       "Vi lindrar din akuta smärta — och åtgärdar problemet.",
        "cb1_body":     "<p>Akut tandvärk, en skadad tand eller en fyllning som lossnat — situationer som kräver snabb åtgärd. Att dröja med att söka vård kan förvärra problemet och leda till mer komplexa behandlingar.</p><p>Hos Älvsjö Tandvård möter vi dagligen patienter med akuta besvär: <strong>kraftig tandvärk, sprucken eller bruten tand, en tand som slagits loss, förlorade fyllningar eller kronor, samt svullnader och infektioner</strong> i munnen.</p><p>Vårt mål är inte bara att lindra din smärta utan att direkt påbörja den behandling som behövs.</p>",
        "cb1_image":    BASE_IMG + "clinic-1.jpg",
        "cb1_cta_text": "Boka akuttid",
        "cb1_cta_link": "#tdl-booking-widget",
        "cb2_eyebrow":  "Därför Älvsjö Tandvård",
        "cb2_h2":       "Snabbt, tryggt — och nära pendeln.",
        "cb2_body":     '<ul style="padding-left:0;list-style:none;display:flex;flex-direction:column;gap:14px;margin:0;"><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">01</span><span><strong>Snabb hjälp</strong> — ofta tid redan samma dag.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">02</span><span><strong>Flexibla öppettider</strong> — öppet till 20:00 mån–tors och lördagar 09–15.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">03</span><span><strong>Centralt läge</strong> — 2 min från pendelstationen i Älvsjö.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">04</span><span><strong>Trygg miljö</strong> — anpassad även för dig med tandvårdsrädsla.</span></li></ul>',
        "cb2_image":    BASE_IMG + "emergency.jpg",
        "cb2_cta_text": "Boka akuttid",
        "cb2_cta_link": "#tdl-booking-widget",
        "faq_heading":  "Vanliga frågor om akuttandvård.",
        "faq_q_1": "Hur bokar jag en akuttid hos er?",
        "faq_a_1": "Ring oss direkt på 08-12 85 45 55. Vi har avsatta tider för akuta patienter och gör vårt bästa för att du ska få en tid redan samma dag, även på kvällar och lördagar.",
        "faq_q_2": "Vad kostar ett akutbesök?",
        "faq_a_2": "En akut undersökning kostar 575 kr (440 kr för nya patienter). Eventuell behandling prissätts efter undersökningen. Vi följer Folktandvårdens prislista och är anslutna till Försäkringskassan.",
        "faq_q_3": "Har ni öppet för akutbesök på kvällar och helger?",
        "faq_a_3": "Ja — öppet till 20:00 måndag–torsdag och lördagar 09:00–15:00. Ring oss för att boka.",
        "faq_q_4": "Hur hanterar ni patienter med tandvårdsrädsla?",
        "faq_a_4": "Vi möter alla med förståelse och extra tålamod. Berätta om din rädsla när du bokar så anpassar vi besöket.",
    },
    "implantat": {
        "ig_eyebrow": "Varför implantat?",
        "ig_heading": "Den moderna lösningen för saknade tänder.",
        "ig_items": [
            {"val": "98 %",      "desc": "Hög lyckandegräns — lyckad osseointegration efter 10 år (meta-analys, PubMed 2019)."},
            {"val": "3D",        "desc": "CBCT-planering — digital 3D-röntgen för exakt implantatplacering och maximal säkerhet."},
            {"val": "0 %",       "desc": "Räntefri delbetalning — betala i bekväma månadsbelopp utan dolda avgifter."},
            {"val": "Komplett",  "desc": "Allt under ett tak — från konsultation och insättning till färdig krona hos oss."},
        ],
        "cb1_eyebrow":  "Behandlingen",
        "cb1_h2":       "Permanenta tänder som ser och känns helt naturliga.",
        "cb1_body":     "<p>Ett tandimplantat är en titanskruv som placeras i käkbenet och fungerar som tandens rot. Ovanpå skruven monteras en tandkrona som matchar dina egna tänder exakt — i form, färg och funktion.</p><p>Vi utför <strong>3D-planering med CBCT-röntgen</strong> inför alla implantatbehandlingar för maximal precision och säkerhet. Hela förloppet — från konsultation och insättning till färdig krona — sköts på vår klinik, utan remisser vidare.</p>",
        "cb1_image":    BASE_IMG + "tandmodell.jpg",
        "cb1_cta_text": "Boka implantatrådgivning",
        "cb1_cta_link": "#tdl-booking-widget",
        "ps_eyebrow":   "Behandlingens gång",
        "ps_heading":   "Fyra faser — från diagnos till permanent tand.",
        "ps_steps": [
            {"title": "Konsultation & 3D-planering", "desc": "CBCT-röntgen och digitalt avtryck. Vi planerar exakt placering — du ser resultatet innan vi sätter igång."},
            {"title": "Implantatinsättning",         "desc": "Titanskruven placeras i käkbenet under lokalbedövning. Lika smärtfritt som en vanlig tandlagning."},
            {"title": "Läkningstid",                 "desc": "Käkbenet integrerar skruven under 3–6 månader. En tillfällig krona sätts under hela perioden."},
            {"title": "Permanent krona",             "desc": "Den skräddarsydda kronan monteras. Du lämnar kliniken med ett komplett, permanent leende."},
        ],
        "cb2_eyebrow":  "Varför Älvsjö Tandvård",
        "cb2_h2":       "Hela behandlingen — under ett tak.",
        "cb2_body":     '<ul style="padding-left:0;list-style:none;display:flex;flex-direction:column;gap:14px;margin:0;"><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">01</span><span><strong>Specialistteam</strong> — kirurg, tandtekniker och tandsköterska på plats.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">02</span><span><strong>Räntefri delbetalning</strong> — dela upp kostnaden utan extra avgifter.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">03</span><span><strong>Gratis konsultation</strong> — vi bedömer din situation utan kostnad vid första besöket.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">04</span><span><strong>Livslång hållbarhet</strong> — med rätt skötsel varar implantatet ett helt liv.</span></li></ul>',
        "cb2_image":    BASE_IMG + "clinic-room-2.jpg",
        "cb2_cta_text": "Boka implantatrådgivning",
        "cb2_cta_link": "#tdl-booking-widget",
        "pr_eyebrow":   "Pris & ersättning",
        "pr_heading":   "Tydliga priser — utan överraskningar.",
        "pr_intro":     "Vi erbjuder räntefri delbetalning och hjälper dig att kartlägga om din tandvårdsförsäkring täcker delar av kostnaden. Kontakta oss för en exakt offert.",
        "pr_rows": [
            {"label": "Implantatrådgivning (konsultation)", "price": "Gratis"},
            {"label": "Implantatinsättning inkl. CBCT-röntgen", "price": "Från 18 000 kr"},
            {"label": "Kronarbete (laboratorietillverkad)", "price": "Från 8 500 kr"},
            {"label": "Räntefri delbetalning", "price": "Vid större ingrepp"},
        ],
        "faq_heading":  "Vanliga frågor om tandimplantat.",
        "faq_q_1": "Hur lång är behandlingstiden?",
        "faq_a_1": "Från insättning av implantatet till färdig krona tar det vanligtvis 3–6 månader. Käkbenet behöver integrera titanskruven (osseointegration) innan kronan monteras.",
        "faq_q_2": "Ingår tandimplantat i tandvårdsförsäkringen?",
        "faq_a_2": "Tandvårdsbidraget och i vissa fall tandvårdsförsäkringen täcker delar av kostnaden. Vi hjälper dig att kartlägga vad just din försäkring täcker vid konsultationsbesöket.",
        "faq_q_3": "Gör det ont att sätta implantat?",
        "faq_a_3": "Ingreppet görs under lokalbedövning och är för de flesta nästan smärtfritt. Efteråt kan du ha lite ömhet i 2–3 dagar, som hanteras med receptfria smärtstillare.",
        "faq_q_4": "Kan alla få tandimplantat?",
        "faq_a_4": "De flesta vuxna med tillräckligt käkben och god allmänhälsa kan få implantat. Vi bedömer din situation med röntgen och klinisk undersökning — kostnadsfritt vid konsultationsbesöket.",
    },
    "karies-hal-i-tanden": {
        "ig_eyebrow": "Kariesens stadier",
        "ig_heading": "Ju tidigare — desto enklare behandling.",
        "ig_items": [
            {"stage": "Stadium 1", "title": "Initial karies",   "desc": "Mineraltapp i emaljytan utan synligt hål. Behandlas med fluor och kostråd — ingen borr."},
            {"stage": "Stadium 2", "title": "Emaljkaries",      "desc": "Liten skada i emaljens yttre lager. Kräver en liten fyllning under lokalbedövning."},
            {"stage": "Stadium 3", "title": "Dentinkaries",     "desc": "Skadan har nått dentinet under emaljen. Större fyllning — behandla omgående för att undvika nervpåverkan."},
            {"stage": "Stadium 4", "title": "Pulpapåverkan",    "desc": "Karies har nått tandens nerv. Kan kräva rotfyllning eller i värsta fall extraktion."},
        ],
        "cb1_eyebrow":  "Behandlingen",
        "cb1_h2":       "Modern lagning — estetisk, skonsam och hållbar.",
        "cb1_body":     "<p>Karies uppstår när bakterier i munnen omvandlar socker till syra som bryter ned tandens emalj. Ju tidigare vi behandlar, desto mindre ingrepp behövs — och desto lägre kostnad för dig.</p><p>Vi använder <strong>tandfärgad komposit</strong> som ser helt naturlig ut och binder direkt till tandsubstansen. Behandlingen sker under lokalbedövning och tar vanligtvis 20–45 minuter. Röntgen ingår alltid för att utesluta djupare skada.</p>",
        "cb1_image":    BASE_IMG + "intraoral-rontgen.jpg",
        "cb1_cta_text": "Boka tandundersökning",
        "cb1_cta_link": "#tdl-booking-widget",
        "cb2_eyebrow":  "Förebyggande vård",
        "cb2_h2":       "Förebygg karies — med rätt daglig rutin.",
        "cb2_body":     "<p>Den bästa behandlingen mot karies är att förebygga den. Med rätt rutin kan du drastiskt minska risken för nya hål — och hålla dina tänder friska längre.</p><ul style='padding-left:0;list-style:none;display:flex;flex-direction:column;gap:12px;margin:12px 0 0;'><li style='display:flex;gap:12px;'>→<span><strong>Borsta 2 gånger/dag</strong> med fluortandkräm (1 450 ppm).</span></li><li style='display:flex;gap:12px;'>→<span><strong>Använd tandstickor eller tandtråd</strong> varje kväll — mellanrum är kariesrisk nr 1.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Begränsa söta drycker</strong> — det är frekvensen av socker, inte mängden, som skadar.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Regelbundna kontroller</strong> — tidig diagnos är alltid billigare behandling.</span></li></ul>",
        "cb2_image":    BASE_IMG + "utrustning.jpg",
        "cb2_cta_text": "Boka undersökning",
        "cb2_cta_link": "#tdl-booking-widget",
        "faq_heading":  "Frågor om karies och hål i tanden.",
        "faq_q_1": "Hur vet jag om jag har hål i tanden?",
        "faq_a_1": "Vanliga tecken är smärta vid kallt, varmt eller sött, synliga mörkfärgningar eller en känsla av att något saknas i tanden. Tidig karies ger ofta inga symptom — därför är regelbundna kontroller viktiga.",
        "faq_q_2": "Hur länge håller en kompositfyllning?",
        "faq_a_2": "Med god munhygien och regelbundna kontroller håller en kompositfyllning vanligtvis 7–15 år. Vår klinik erbjuder alltid en garanti på utfört arbete.",
        "faq_q_3": "Vad kostar en fyllning?",
        "faq_a_3": "Priset beror på hålets storlek och position. Vi följer Folktandvårdens prislista och är anslutna till Försäkringskassan. Din tandvårdsersättning dras direkt på fakturan.",
        "faq_q_4": "Behöver jag bedövning?",
        "faq_a_4": "Ja, vi använder alltid lokalbedövning vid lagning. Du känner ingenting under behandlingen. Vid ytlig karies kan vi i vissa fall laga utan bedövning om patienten föredrar det.",
    },
    "tandblekning": {
        "ig_eyebrow": "Blekningsmetoder",
        "ig_heading": "Välj rätt metod för ditt leende.",
        "ig_items": [
            {"name": "Klinikblekning",      "badge": "Snabbt resultat",  "time": "60–90 min",        "effect": "Upp till 8 nyanser",  "desc": "Professionellt gel och LED-ljus ger ett omedelbart, intensivt resultat redan samma dag."},
            {"name": "Hemblekning",         "badge": "Skonsamt",         "time": "2–3 veckor",        "effect": "4–6 nyanser",         "desc": "Skräddarsydda skenor och professionellt blekgel — gradvist och skonsamt i din egen takt."},
            {"name": "Kombinationsblekning","badge": "Rekommenderas",    "time": "Klinik + hemkit",   "effect": "Upp till 10 nyanser", "desc": "Klinikblekning kombinerat med hemkittet — det bästa och mest långvariga resultatet."},
        ],
        "cb1_eyebrow":  "Behandlingen",
        "cb1_h2":       "Säker blekning — kontrollerat, snabbt och skonsamt.",
        "cb1_body":     "<p>Professionell tandblekning ger ett märkbart resultat på bara ett besök. Vi erbjuder <strong>klinikblekning</strong> med aktivt gel och LED-ljus, <strong>hemblekning</strong> med skräddarsydda skenor, samt en <strong>kombinationsmetod</strong> för de bästa och mest långvariga resultaten.</p><p>Till skillnad från butiksprodukter är koncentrationen av blekmedlet hos oss optimerad för din tandhälsa — vi säkerställer att emaljen inte skadas och att du inte får onödig tandöverkänslighet.</p>",
        "cb1_image":    BASE_IMG + "undersok.jpg",
        "cb1_cta_text": "Boka blekningskonsultation",
        "cb1_cta_link": "#tdl-booking-widget",
        "cb2_eyebrow":  "Eftervård",
        "cb2_h2":       "Håll resultatet längre — enkla tips.",
        "cb2_body":     "<p>Med rätt eftervård håller ditt blekningsresultat avsevärt längre. Tänderna är lite mer öppna de första 48 timmarna efter blekning — undvik mat och dryck som färgar.</p><ul style='padding-left:0;list-style:none;display:flex;flex-direction:column;gap:12px;margin:12px 0 0;'><li style='display:flex;gap:12px;'>→<span><strong>Undvik kaffe, te, rödvin</strong> de första 48 timmarna efter blekning.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Borsta med fluortandkräm</strong> — stärker emaljen och reducerar känslighet.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Uppfräschning med hemblekning</strong> var 6–12 månader förlänger resultatet markant.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Regelbundna kontroller</strong> håller tänderna vita och friska längre.</span></li></ul>",
        "cb2_image":    BASE_IMG + "clinic-room-1.jpg",
        "cb2_cta_text": "Boka blekningskonsultation",
        "cb2_cta_link": "#tdl-booking-widget",
        "faq_heading":  "Frågor om tandblekning.",
        "faq_q_1": "Hur många nyanser ljusare kan jag bli?",
        "faq_a_1": "Med professionell klinikblekning uppnår de flesta 6–10 nyanser ljusare tänder, beroende på ursprungsfärg och metod. Vi visar dig en realistisk förväntan vid konsultationsbesöket.",
        "faq_q_2": "Är tandblekning säkert?",
        "faq_a_2": "Ja, professionell blekning under tandläkartillsyn är säkert. Vi undersöker alltid tänderna först och avråder vid aktiv karies, spruckna tänder eller allvarlig tandöverkänslighet.",
        "faq_q_3": "Hur länge håller resultatet?",
        "faq_a_3": "Resultatet håller vanligtvis 1–3 år med god munhygien och måttlig konsumtion av kaffé, te och rödvin. En uppfräschning med hemblekning kan förlänga resultatet betydligt.",
        "faq_q_4": "Kan jag bleka om jag har kronor eller faner?",
        "faq_a_4": "Blekmedlet påverkar inte keramik eller komposit — kronor och faner behåller sin ursprungsfärg. Om du planerar att kombinera blekning med kronarbete bör blekning göras först.",
    },
    "tandfasader-veneers": {
        "ig_eyebrow": "När är tandfasader rätt?",
        "ig_heading": "Sex vanliga indikationer för veneers.",
        "ig_items": [
            {"title": "Missfärgade tänder",  "desc": "Permanenta fläckar som inte svarar på blekning — porslin ger en vit, jämn yta för livet."},
            {"title": "Mellanrum",            "desc": "Diasteman som stör leendets harmoni — korrigeras utan tandreglering."},
            {"title": "Ojämna tänder",        "desc": "Längd- och formskillnader som skapar ett obalanserat leende åtgärdas på ett besök."},
            {"title": "Slitna tänder",        "desc": "Förkortade tänder från bruxism eller åldrande återfår form, längd och estetik."},
            {"title": "Lätta skevheter",      "desc": "Roterade eller oregelbundna tänder kan korrigeras optiskt — utan byglar."},
            {"title": "Smile design",         "desc": "Du vill designa ett helt nytt leende från grunden — form, färg och symmetri."},
        ],
        "cb1_eyebrow":  "Behandlingen",
        "cb1_h2":       "Porslinsfaner skräddarsydda för just ditt leende.",
        "cb1_body":     "<p>Tandfasader (veneers) är tunna skal av porslin eller komposit som limmas på tandens framsida. De kan dölja missfärgningar, ojämnheter, mellanrum och lätta skevheter — utan att tanden behöver slipas ner märkbart.</p><p>Processen börjar alltid med ett <strong>digitalt smile design-samtal</strong> där vi visar dig en preview av resultatet innan vi påbörjar behandlingen. Porslinsfaner tillverkas av vårt laboratorium och är både estetiskt och funktionellt hållbara i 15–20 år.</p>",
        "cb1_image":    BASE_IMG + "clinic-room-1.jpg",
        "cb1_cta_text": "Boka konsultation",
        "cb1_cta_link": "#tdl-booking-widget",
        "cb2_eyebrow":  "Processen",
        "cb2_h2":       "Tre steg till ditt drömleende.",
        "cb2_body":     '<ul style="padding-left:0;list-style:none;display:flex;flex-direction:column;gap:14px;margin:0;"><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">01</span><span><strong>Konsultation & smile design</strong> — vi digitalt simulerar ditt nya leende och gör ett fysiskt mock-up i komposit. Du godkänner formen innan vi slipar.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">02</span><span><strong>Preparation & avtryck</strong> — en tunn skiva emalj avlägsnas (0,3–0,5 mm), ett digitalt eller fysiskt avtryck tas och skickas till laboratoriet.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">03</span><span><strong>Cementering</strong> — de färdiga porslinsfanerna limmas permanent på plats. Resultatet är omedelbart och håller 15–20 år.</span></li></ul>',
        "cb2_image":    BASE_IMG + "clinic-1.jpg",
        "cb2_cta_text": "Boka smile design-samtal",
        "cb2_cta_link": "#tdl-booking-widget",
        "faq_heading":  "Frågor om tandfasader och veneers.",
        "faq_q_1": "Hur länge håller porslinsfaner?",
        "faq_a_1": "Med god munhygien och regelbundna kontroller håller porslinsfaner 15–20 år. De är resistenta mot missfärgning och slitage, men undvik att bita i hårda föremål eller knapra is.",
        "faq_q_2": "Behöver tanden slipas?",
        "faq_a_2": "Porslinsfaner kräver att en tunn skiva emalj (0,3–0,5 mm) avlägsnas för att fasaden ska sitta plant. Kompositfaner kan i vissa fall appliceras utan förbehandling.",
        "faq_q_3": "Kan jag se hur resultatet ser ut innan behandlingen?",
        "faq_a_3": "Ja — vi erbjuder alltid ett digitalt smile design-samtal, inklusive ett fysiskt 'mock-up' i komposit, så att du kan godkänna formen och färgen innan vi slipar.",
        "faq_q_4": "Ingår tandfasader i tandvårdsersättningen?",
        "faq_a_4": "Estetiska behandlingar som tandfasader ingår inte i det statliga tandvårdsbidraget, men täcks delvis av en del privata tandvårdsförsäkringar. Vi hjälper dig att kolla dina villkor.",
    },
    "tandreglering-stockholm": {
        "ig_eyebrow": "Invisalign-fördelar",
        "ig_heading": "Raka tänder på dina egna villkor.",
        "ig_items": [
            {"val": "Osynlig",   "desc": "Klara skenor som knappt syns — ingen märker att du behandlas."},
            {"val": "6–24 mån",  "desc": "Kortare behandlingstid än traditionell tandreglering för de flesta fall."},
            {"val": "Avtagbar",  "desc": "Ta av skenorna vid måltider och tandborstning — inga kostbegränsningar."},
            {"val": "98 %",      "desc": "Kliniska studier visar konsekvent hög patientnöjdhet med Invisalign världen över."},
        ],
        "cb1_eyebrow":  "Behandlingen",
        "cb1_h2":       "Invisalign — osynlig tandreglering i din vardag.",
        "cb1_body":     "<p>Vi är <strong>certifierade Invisalign-leverantörer</strong>. Med en serie klara, avtagbara skenor rätas dina tänder ut steg för steg — utan metallbyglar, utan synliga apparater och utan att du behöver ändra dina matvanor.</p><p>Processen börjar med ett digitalt 3D-avtryck och en simulation som visar hur dina tänder rör sig under behandlingen. Du ser slutresultatet redan vid konsultationen — kostnadsfritt.</p>",
        "cb1_image":    BASE_IMG + "clinic-room-2.jpg",
        "cb1_cta_text": "Boka Invisalign-konsultation",
        "cb1_cta_link": "#tdl-booking-widget",
        "ps_eyebrow":   "Behandlingens gång",
        "ps_heading":   "Från digital scan till stabilt leende.",
        "ps_steps": [
            {"title": "Digital scanning",       "desc": "Digitalt 3D-avtryck — ingen mesig massa. Du ser din behandlingsplan och slutresultatet direkt på skärmen."},
            {"title": "Individuella skenor",    "desc": "Dina transparenta skenor tillverkas skräddarsydda av Invisalign. Du byter skenpar var 1–2 vecka."},
            {"title": "Regelbundna kontroller", "desc": "Vi följer upp var 6–8 vecka. De flesta kontrollbesök är korta och problemfria."},
            {"title": "Retention",              "desc": "En tunn, permanent retainstång bakom tänderna håller ditt resultat för livet."},
        ],
        "cb2_eyebrow":  "Varför Invisalign?",
        "cb2_h2":       "Raka tänder som passar ditt liv.",
        "cb2_body":     '<ul style="padding-left:0;list-style:none;display:flex;flex-direction:column;gap:14px;margin:0;"><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">01</span><span><strong>Certifierat team</strong> — vi är certifierade Invisalign-leverantörer med dokumenterad erfarenhet.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">02</span><span><strong>Se resultatet direkt</strong> — vi visar din digitala behandlingsplan och slutresultat redan vid konsultationen.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">03</span><span><strong>Gratis konsultation</strong> — inga dolda kostnader för att se om Invisalign är rätt för dig.</span></li><li style="display:flex;gap:16px;align-items:baseline;"><span style="font-family:var(--font-sans);font-size:11px;font-weight:600;letter-spacing:0.22em;color:var(--sage-600);text-transform:uppercase;flex-shrink:0;min-width:32px;">04</span><span><strong>Räntefri delbetalning</strong> — dela upp kostnaden i månadsbelopp utan ränta.</span></li></ul>',
        "cb2_image":    BASE_IMG + "undersok.jpg",
        "cb2_cta_text": "Boka Invisalign-konsultation",
        "cb2_cta_link": "#tdl-booking-widget",
        "faq_heading":  "Frågor om tandreglering och Invisalign.",
        "faq_q_1": "Hur länge tar Invisalign-behandlingen?",
        "faq_a_1": "Behandlingstiden varierar från 6 månader för enklare fall till 18–24 månader för mer komplexa. En genomsnittlig vuxenpatient är klar på 12–18 månader.",
        "faq_q_2": "Kan alla använda Invisalign?",
        "faq_a_2": "Invisalign passar de flesta vuxna och ungdomar med mild till måttlig oregelbundenhet i bettet. Mycket komplexa fall (t.ex. kraftiga bettavvikelser) kan kräva traditionell tandreglering.",
        "faq_q_3": "Hur länge ska jag ha skenorna på per dag?",
        "faq_a_3": "För optimalt resultat bör du ha skenorna på 20–22 timmar per dygn. Du tar av dem vid måltider och tandborstning.",
        "faq_q_4": "Vad kostar Invisalign?",
        "faq_a_4": "Priset beror på behandlingens komplexitet och längd. Vi erbjuder räntefri delbetalning för att göra behandlingen tillgänglig. Exakt prisuppgift ger vi vid konsultationsbesöket.",
    },
    "tandsten-tandhygienist": {
        "ig_eyebrow": "Varför regelbunden tandrengöring?",
        "ig_heading": "Sex skäl att prioritera tandhygienisten.",
        "ig_items": [
            {"title": "Förebygger tandlossning",  "desc": "Tandsten under tandköttet är den vanligaste orsaken till tandlossning — bort med den innan skadan sker."},
            {"title": "Friskare andedräkt",       "desc": "Bakterier i tandsten ger dålig andedräkt. Professionell rengöring löser grundproblemet, inte bara symptomen."},
            {"title": "Ljusare tänder",           "desc": "Ytmissfärgningar från kaffe, te och vin poleras bort — tänderna återfår sin naturliga lyster."},
            {"title": "Hjärthälsa",               "desc": "Forskning visar samband mellan kronisk tandlossning och hjärt-kärlsjukdom. Friska tandkött = friskare kropp."},
            {"title": "Tidig diagnos",            "desc": "Tandhygienisten identifierar tidiga tecken på karies, slitage och andra problem — innan de blir dyra."},
            {"title": "Individuell rådgivning",   "desc": "Du får en personlig genomgång av din hemvårdsrutin — anpassad efter just dina risker och behov."},
        ],
        "cb1_eyebrow":  "Behandlingen",
        "cb1_h2":       "Professionell rengöring — grunden för friska tänder.",
        "cb1_body":     "<p>Tandsten bildas av plack som mineraliserats och sitter fast på tänderna — det går inte att borsta bort hemma. Regelbunden tandhygienistbehandling är det mest effektiva sättet att förebygga karies, tandlossning och dålig andedräkt.</p><p>Våra <strong>erfarna tandhygienister</strong> använder ultraljudsrengöring och handinstrument för en grundlig rensning, följt av polering och en individuell genomgång av din hemvårdsrutin. Besöket tar 45–60 minuter och är odramatiskt.</p>",
        "cb1_image":    BASE_IMG + "utrustning.jpg",
        "cb1_cta_text": "Boka tandhygienistbesök",
        "cb1_cta_link": "#tdl-booking-widget",
        "cb2_eyebrow":  "Hemvård",
        "cb2_h2":       "Rätt hemvård — grunden mellan besöken.",
        "cb2_body":     "<p>Professionell rengöring var 6–12 månader är grunden — men din dagliga hemvård avgör hur snabbt tandstenen kommer tillbaka. Med rätt rutin räcker ett besök per år för de flesta.</p><ul style='padding-left:0;list-style:none;display:flex;flex-direction:column;gap:12px;margin:12px 0 0;'><li style='display:flex;gap:12px;'>→<span><strong>Borsta 2 minuter, 2 gånger per dag</strong> med fluortandkräm. Elektrisk tandborste är effektivare.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Rengör mellanrummen dagligen</strong> med tandstickor eller tandtråd — det är här tandstenen bildas.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Sköljning med fluorsköljmedel</strong> på kvällen stärker emaljen och minskar kariesrisken.</span></li><li style='display:flex;gap:12px;'>→<span><strong>Drick vatten efter söta drycker</strong> — sänker syran snabbt och skyddar tänderna.</span></li></ul>",
        "cb2_image":    BASE_IMG + "clinic-room-2.jpg",
        "cb2_cta_text": "Boka tandhygienistbesök",
        "cb2_cta_link": "#tdl-booking-widget",
        "faq_heading":  "Frågor om tandsten och tandhygienistbehandling.",
        "faq_q_1": "Hur ofta bör jag besöka tandhygienisten?",
        "faq_a_1": "De flesta vuxna rekommenderas ett besök var 6–12 månad. Din tandhygienist gör en individuell riskbedömning och rekommenderar ett intervall anpassat till din munhälsa.",
        "faq_q_2": "Gör det ont att rengöra tandsten?",
        "faq_a_2": "Ultraljudsrengöring upplevs av de flesta som mild och odramatisk. Vid ömma tandkött eller mycket tandsten kan man uppleva en lätt känslighet — som försvinner direkt efter behandlingen.",
        "faq_q_3": "Ingår tandhygienistbesök i tandvårdsbidraget?",
        "faq_a_3": "Ja, det statliga tandvårdsbidraget (TLV) kan användas till tandhygienistbehandlingar. Beloppet varierar med din ålder — vi informerar om exakt ersättning vid bokningstillfället.",
        "faq_q_4": "Kostar det något för barn?",
        "faq_a_4": "Tandvård är gratis för alla barn och ungdomar upp till 19 år, inklusive tandhygienistbehandlingar.",
    },
    "tandvardsradsla": {
        "ig_eyebrow": "Vår approach",
        "ig_heading": "Sex sätt vi gör besöket hanterbart.",
        "ig_items": [
            {"num": "01", "title": "Dela din rädsla",       "desc": "Berätta när du bokar — vi anpassar hela besöket till din situation och sätter rätt personal."},
            {"num": "02", "title": "Stop-signal",           "desc": "Du har alltid full kontroll. Ett tecken från dig och vi stannar omedelbart, utan frågor."},
            {"num": "03", "title": "Pausa när du vill",     "desc": "Ingenting händer i en takt du inte är bekväm med. Vi jobbar alltid i din rytm, inte vår."},
            {"num": "04", "title": "Gradvis exponering",    "desc": "Vi börjar enkelt — ett samtal, sedan ett kort besök — och bygger upp tryggheten besök för besök."},
            {"num": "05", "title": "Förklarar varje steg",  "desc": "Inga överraskningar. Vi berättar alltid vad vi gör, varför och hur länge innan vi sätter igång."},
            {"num": "06", "title": "Lugnande vid behov",    "desc": "Vid svår rädsla erbjuder vi lugnande medicin (Triazolam) för att göra besöket möjligt."},
        ],
        "cb1_eyebrow":  "Vår approach",
        "cb1_h2":       "Vi skapar tandvård du faktiskt klarar av.",
        "cb1_body":     "<p>Tandvårdsrädsla är vanligare än du tror — och det är inget att skämmas för. Vi möter dagligen patienter med allt från mild oro till svår fobi, och vår erfarenhet är att alla kan nå en punkt där tandvård är hanterbar.</p><p>Hos oss arbetar vi med <strong>stop-signal, extra tid, tydlig kommunikation och — vid behov — lugnande medicin</strong>. Vi börjar alltid i din takt: med ett samtal, sedan ett enkelt besök, och sedan vidare när du känner dig redo.</p>",
        "cb1_image":    BASE_IMG + "clinic-1.jpg",
        "cb1_cta_text": "Ta det första steget",
        "cb1_cta_link": "tel:+46812854555",
        "cb2_eyebrow":  "Kliniken",
        "cb2_h2":       "En miljö designad för att lugna.",
        "cb2_body":     "<p>Vår klinik på Prästgårdsgränd 4 är designad med rädda patienter i åtanke — ljus, luftig och utan den stela klinikkänslan. Ingen väntsal fylld med obekväma intryck, inget onödigt prat om ingrepp.</p><p>Vi arbetar alltid med <strong>lugnande musik, anpassat ljus och en tydlig, lugn kommunikationsstil</strong>. Många av våra patienter med tandvårdsrädsla berättar att bara <em>miljön</em> gör halva jobbet för dem.</p>",
        "cb2_image":    BASE_IMG + "reception.jpg",
        "cb2_cta_text": "Ta det första steget",
        "cb2_cta_link": "tel:+46812854555",
        "faq_heading":  "Frågor om tandvårdsrädsla.",
        "faq_q_1": "Hur gör ni för patienter som är mycket rädda?",
        "faq_a_1": "Vi börjar alltid med ett vanligt samtal — utan undersökning om du inte vill. Vi sätter upp en stop-signal som gäller omedelbart, arbetar i lugnt tempo och förklarar varje steg. Vi erbjuder även lugnande medicin (Triazolam) vid behov.",
        "faq_q_2": "Kan jag få narkos?",
        "faq_a_2": "I de flesta fall behövs inte narkos — lokalanestesi och eventuell lugnande medicin räcker långt. Om narkos behövs remitterar vi till rätt instans och hjälper dig genom hela processen.",
        "faq_q_3": "Måste jag boka speciell tid?",
        "faq_a_3": "Inte nödvändigtvis, men berätta om din rädsla när du bokar. Då avsätter vi extra tid och den personal som är bäst på att bemöta rädda patienter.",
        "faq_q_4": "Vad kostar ett besök för rädda patienter?",
        "faq_a_4": "Priset är detsamma som för alla andra patienter — vi tar inte ut extra för den extra omsorg vi ger. Vi följer Folktandvårdens prislista och är anslutna till Försäkringskassan.",
    },
}

BARNSPECIALIST_DATA = {
    "eyebrow":      "Barnspecialist · Pedodonti",
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
html.header-light .mobile-nav { background: var(--white) !important; }
html.header-light .mobile-nav .mn-item { border-bottom-color: var(--border) !important; }
html.header-light .mobile-nav .mn-link,
html.header-light .mobile-nav .mn-link-label { color: var(--ink-700) !important; }
html.header-light .mobile-nav .mn-arrow { color: var(--ink-400) !important; border-left-color: var(--border) !important; }
html.header-light .mobile-nav .mn-cb:checked ~ .mn-top-row .mn-arrow { color: var(--ink-700) !important; }
html.header-light .mobile-nav .mn-sub { background: var(--blush-50) !important; }
html.header-light .mobile-nav .mn-sub a { color: var(--ink-600) !important; border-bottom-color: var(--border) !important; }
html.header-light .mobile-nav .mn-item-cta .btn { background: var(--ink-700) !important; color: var(--white) !important; border-color: var(--ink-700) !important; }
"""
    hero_bg_css = (
        ".hero-bleed.hero-bg-video .hb-bg { display: none; }\n"
        ".hero-bleed.hero-bg-video .hb-bg-video--desktop { opacity: 1; pointer-events: auto; }\n"
        "@media (max-width: 768px) {"
        " .hero-bleed .hb-bg-video--desktop { display: none; }"
        " .hero-bleed .hb-bg-video--mobile { display: block; opacity: 0; pointer-events: none; }"
        " .hero-bleed.hero-bg-video .hb-bg-video--mobile { opacity: 1; pointer-events: auto; }"
        " }"
    )
    style_block = f"<style>\n{tokens_css}\n{LAYOUT_CSS}\n{header_variant_css}\n{header_light_override}\n{hero_bg_css}\n</style>"
    onload_js = """<script>
(function(){
  var done=false;
  function r(){if(done)return;done=true;document.body.classList.add('lumo-loaded');}
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(r);
  if(document.readyState!=='loading'){r();}else document.addEventListener('DOMContentLoaded',r);
  setTimeout(r,600);
})();
/* Mobile nav — byggs dynamiskt från WP-renderad desktop-nav */
(function(){
  function buildMobileNav(){
    var wpNav=document.querySelector('.site-header nav > ul')||document.querySelector('.site-header nav ul');
    var mob=document.querySelector('.mobile-nav');
    if(!mob)return;
    if(!wpNav){return;}
    if(mob.dataset.built)return;
    mob.dataset.built='1';
    mob.innerHTML='';
    var util=document.createElement('div');util.className='mn-utility';
    [['https://minatider.alvsjotandvard.se/?src=site','Mina tider'],['https://alvsjotandvard.se/lista-dig','Lista dig'],['https://alvsjotandvard.se/remiss-2','Remiss']].forEach(function(pair,i){
      if(i>0){var sep=document.createElement('span');sep.className='mn-util-sep';sep.textContent='·';util.appendChild(sep);}
      var a=document.createElement('a');a.href=pair[0];a.textContent=pair[1];util.appendChild(a);
    });
    mob.appendChild(util);
    var idx=0;
    wpNav.querySelectorAll(':scope > li').forEach(function(li){
      var a=li.querySelector(':scope > a');
      var sub=li.querySelector(':scope > ul');
      if(!a)return;
      var href=(a.getAttribute('href')||'').trim();
      var label=a.textContent.trim();
      var wrap=document.createElement('div');
      if(sub&&sub.children.length){
        idx++;
        var cbId='mn-d'+idx;
        var cb=document.createElement('input');
        cb.type='checkbox';cb.id=cbId;cb.className='mn-cb';cb.setAttribute('aria-hidden','true');
        var row=document.createElement('div');row.className='mn-top-row';
        var pageless=(!href||href==='#'||href===window.location.origin+'/'||href==='/');
        if(pageless){
          var lbl=document.createElement('label');
          lbl.setAttribute('for',cbId);lbl.className='mn-link mn-link-label';lbl.textContent=label;
          row.appendChild(lbl);
        } else {
          var lnk=document.createElement('a');
          lnk.href=href;lnk.className='mn-link';lnk.textContent=label;
          row.appendChild(lnk);
        }
        var arr=document.createElement('label');
        arr.setAttribute('for',cbId);arr.className='mn-arrow';arr.textContent='›';
        row.appendChild(arr);
        var sd=document.createElement('div');sd.className='mn-sub';
        sub.querySelectorAll(':scope > li > a').forEach(function(sa){
          var a2=document.createElement('a');
          a2.href=sa.getAttribute('href')||'#';a2.textContent=sa.textContent.trim();
          sd.appendChild(a2);
        });
        wrap.className='mn-item mn-has-sub';
        wrap.appendChild(cb);wrap.appendChild(row);wrap.appendChild(sd);
      } else {
        wrap.className='mn-item';
        var lnk2=document.createElement('a');
        lnk2.href=href;lnk2.className='mn-link';lnk2.textContent=label;
        wrap.appendChild(lnk2);
      }
      mob.appendChild(wrap);
    });
    var cta=document.createElement('div');cta.className='mn-item mn-item-cta';
    var ca=document.createElement('a');
    ca.href='#tdl-booking-widget';ca.className='btn btn-primary';ca.textContent='Boka tid online';
    cta.appendChild(ca);mob.appendChild(cta);
  }
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',buildMobileNav);
  } else {
    buildMobileNav();
  }
  setTimeout(buildMobileNav,400);
  setTimeout(buildMobileNav,1200);
})();
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
      <button id="header-style-toggle" onclick="(function(){{var h=document.documentElement;var isLight=h.classList.toggle('header-light');localStorage.setItem('hdr',isLight?'0':'1');document.getElementById('header-style-toggle').textContent=isLight?'○ White':'● Black';document.querySelectorAll('.hdr-toggle-label').forEach(function(b){{b.textContent=isLight?'○ White':'● Black';}});}})()" data-tip="Vit navbar ger ett rent och luftigt intryck. Svart matchar sidans detaljer och får loggan att verkligen sticka ut och synas." style="background:none;border:none;color:#f97316;font-size:12px;cursor:pointer;padding:0;letter-spacing:0.04em;font-family:inherit;">● Black</button>
      <span class="ts-sep">·</span>
      <a href="https://minatider.alvsjotandvard.se/?src=site">Mina tider</a>
      <span class="ts-sep">·</span>
      <span class="nav-cs"><a href="/lista-dig">Lista dig</a></span>
      <span class="ts-sep">·</span>
      <a href="/remiss-2">Remiss</a>
      <span class="ts-sep">·</span>
      <a href="tel:{{{{site_phone}}}}" style="display:flex;align-items:center;gap:6px;">{ICO_PHONE} {{{{site_phone}}}}</a>
    </div>
  </div>
</div>
<input type="checkbox" id="nav-toggle" class="nav-toggle" aria-hidden="true">
<header class="site-header">
  <div class="sh-inner">
    <a href="/" class="logo" aria-label="Älvsjö Tandvård">
      <img src="{LOGO_COLOR}" alt="Älvsjö Tandvård">
    </a>
    <button class="header-style-toggle-mobile" onclick="(function(){{var h=document.documentElement;var isLight=h.classList.toggle('header-light');localStorage.setItem('hdr',isLight?'0':'1');document.querySelectorAll('.hdr-toggle-label').forEach(function(b){{b.textContent=isLight?'○ White':'● Black';}});}})()" style="display:none;background:none;border:none;color:#f97316;font-size:16px;cursor:pointer;padding:4px 8px;"><span class="hdr-toggle-label">● Black</span></button>
    <label for="nav-toggle" class="hamburger" aria-label="Öppna meny">
      <span></span><span></span><span></span>
    </label>
    <nav>
      {{{{lumokit-primary}}}}
      <a href="#tdl-booking-widget" class="btn btn-primary btn-sm">Boka tid</a>
    </nav>
  </div>
</header>
<nav class="mobile-nav" aria-label="Mobilmeny"></nav>
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
  <div class="hb-bg" style="background-image:url('{{hero_image}}');"></div>
  <video class="hb-bg-video hb-bg-video--desktop" autoplay muted loop playsinline oncanplay="this.playbackRate=0.75">
    <source src="{{hero_video_desktop_webm}}" type="video/webm">
    <source src="{{hero_video_desktop}}" type="video/mp4">
  </video>
  <video class="hb-bg-video hb-bg-video--mobile" autoplay muted loop playsinline oncanplay="this.playbackRate=0.75">
    <source src="{{hero_video_mobile_webm}}" type="video/webm">
    <source src="{{hero_video_mobile}}" type="video/mp4">
  </video>
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
  <button class="hb-bg-toggle" id="hb-bg-toggle" data-tip="Demo-video — i produktion byts denna ut mot en skräddarsydd film som passar kliniken perfekt.">◼ Bild</button>
  <script>
  (function(){
    var hero = document.querySelector('.hero-bleed');
    var btn  = document.getElementById('hb-bg-toggle');
    var mode = localStorage.getItem('heroBg') || 'image';
    var locked = false;
    function apply(m){
      hero.classList.toggle('hero-bg-video', m==='video');
      btn.textContent = m==='video' ? '◼ Bild' : '▶ Video';
    }
    function pulse(){
      btn.classList.remove('hb-pulse');
      void btn.offsetWidth;
      btn.classList.add('hb-pulse');
    }
    apply(mode);
    setTimeout(function(){ pulse(); setInterval(pulse, 5000); }, 1200);
    btn.addEventListener('click', function(){
      if(locked) return;
      mode = mode==='video' ? 'image' : 'video';
      localStorage.setItem('heroBg', mode);
      apply(mode);
      if(mode==='video'){ locked=true; setTimeout(function(){ locked=false; }, 600); }
    });
  })();
  </script>
</section>
"""
    return {
        "block_name": "lumo/hero",
        "title": "Hero",
        "html_template": collapse(html),
        "schema": [
            {"name": "hero_image",         "type": "image", "label": "Bakgrundsbild",               "default": "https://swordfish.templweb.com/wp-content/uploads/2026/05/hero-1.jpg"},
            {"name": "hero_video_desktop",      "type": "text", "label": "Bakgrundsvideo desktop — MP4-URL", "default": "https://swordfish.templweb.com/wp-content/uploads/2026/05/video_mp_.mp4"},
            {"name": "hero_video_desktop_webm", "type": "text", "label": "Bakgrundsvideo desktop — WebM-URL", "default": ""},
            {"name": "hero_video_mobile",       "type": "text", "label": "Bakgrundsvideo mobil — MP4-URL",    "default": "https://swordfish.templweb.com/wp-content/uploads/2026/05/video_mp_.mp4"},
            {"name": "hero_video_mobile_webm",  "type": "text", "label": "Bakgrundsvideo mobil — WebM-URL",  "default": ""},
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
          <li><a href="/kampanjer">Kampanjer</a></li>
          <li><a href="/rantefritt">Räntefri delbetalning</a></li>
          <li><a href="/kontakt#hitta-till-oss">Hitta hit</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <div class="footer-col-title">Patient</div>
        <ul>
          <li><a href="#tdl-booking-widget">Boka tid</a></li>
          <li><a href="https://minatider.alvsjotandvard.se/?src=site">Mina tider</a></li>
          <li><a href="/lista-dig">Lista dig</a></li>
          <li><a href="/remiss-2">Remiss</a></li>
          <li><a href="/kontakt">Kontakt</a></li>
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


def build_treatment_hero_shared() -> dict:
    """Delad hero-mall för alla behandlingssidor. Per-sida-innehåll sätts via page_defaults i bundle."""
    html = """
<section class="treatment-hero">
  <div class="th-mobile-bg" style="background-image:url({{hero_image}});"></div>
  <div class="th-inner">
    <div class="eyebrow" style="margin-bottom:20px;color:var(--sage-600);">{{eyebrow}}</div>
    <div class="th-grid">
      <div class="th-left">
        <h1>{{title}} <em>{{title_italic}}</em></h1>
        <div>
          <p class="lead th-lead">{{ingress}}</p>
          <div class="th-bullets">
            <div class="th-bullet"><span class="th-num">01</span>{{bullet_1}}</div>
            <div class="th-bullet"><span class="th-num">02</span>{{bullet_2}}</div>
            <div class="th-bullet"><span class="th-num">03</span>{{bullet_3}}</div>
            <div class="th-bullet"><span class="th-num">04</span>{{bullet_4}}</div>
          </div>
          <div style="display:flex;gap:12px;">
            <a href="#tdl-booking-widget" class="btn btn-primary">Boka tid</a>
            <a href="tel:+46812854555" class="btn btn-ghost">Ring oss</a>
          </div>
        </div>
      </div>
      <div class="th-right">
        <div class="th-photo" style="background-image:url({{hero_image}});"></div>
        <div class="th-stat">
          <div class="th-stat-label">{{stat_label}}</div>
          <div class="th-stat-value">{{stat_value}}</div>
          <div class="th-stat-sub">{{stat_sub}}</div>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/treatment-hero",
        "title": "Treatment Hero (delad mall)",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",      "type": "text",     "label": "Etikett"},
            {"name": "title",        "type": "text",     "label": "Rubrik"},
            {"name": "title_italic", "type": "text",     "label": "Rubrik (kursiv)"},
            {"name": "ingress",      "type": "textarea", "label": "Ingress"},
            {"name": "bullet_1",     "type": "text",     "label": "Punkt 1"},
            {"name": "bullet_2",     "type": "text",     "label": "Punkt 2"},
            {"name": "bullet_3",     "type": "text",     "label": "Punkt 3"},
            {"name": "bullet_4",     "type": "text",     "label": "Punkt 4"},
            {"name": "hero_image",   "type": "image",    "label": "Foto (höger)"},
            {"name": "stat_label",   "type": "text",     "label": "Stat: etikett"},
            {"name": "stat_value",   "type": "text",     "label": "Stat: värde"},
            {"name": "stat_sub",     "type": "text",     "label": "Stat: förklaring"},
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
            {"name": "eyebrow",      "type": "text",     "label": "Etikett",                         "default": "Om oss"},
            {"name": "title",        "type": "text",     "label": "Rubrik",                          "default": "Modern tandvård"},
            {"name": "title_italic", "type": "text",     "label": "Rubrik (kursiv del)",             "default": "mitt i Älvsjö."},
            {"name": "ingress",      "type": "textarea", "label": "Ingress",                         "default": "Vi kombinerar specialistkompetens med en omsorgsfull miljö för hela familjen. Hos oss får du trygg, kvalitativ och tillgänglig vård med dig i fokus."},
            {"name": "bullet_1",     "type": "text",     "label": "Punkt 1",                         "default": "Trygg & modern"},
            {"name": "bullet_2",     "type": "text",     "label": "Punkt 2",                         "default": "Omsorgsfull vård"},
            {"name": "bullet_3",     "type": "text",     "label": "Punkt 3",                         "default": "Hela familjen"},
            {"name": "bullet_4",     "type": "text",     "label": "Punkt 4",                         "default": "Centralt i Älvsjö"},
            {"name": "cta_1_text",   "type": "text",     "label": "Knapp 1 – text",                  "default": "Boka tid"},
            {"name": "cta_1_href",   "type": "text",     "label": "Knapp 1 – länk",                  "default": "#tdl-booking-widget"},
            {"name": "cta_2_text",   "type": "text",     "label": "Knapp 2 – text",                  "default": "Kontakta oss"},
            {"name": "cta_2_href",   "type": "text",     "label": "Knapp 2 – länk",                  "default": "/kontakt"},
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
    <div class="eyebrow" style="margin-bottom:32px;color:var(--sage-600);">Kontakt</div>
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


def build_content_block(block_name: str, title: str, mirror: bool, bg: str = "var(--white)") -> dict:
    text_order = "2" if mirror else "1"
    img_order  = "1" if mirror else "2"
    html = f"""
<section class="cb-section" style="background:{bg};">
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


def build_emergency_strip() -> dict:
    """Sage-grön blixtlist ovanför akut-heron — pulserande prick + telefonnummer."""
    html = """
<section class="emergency-strip">
  <div class="container-wide es-inner">
    <div class="es-left">
      <span class="es-dot"></span>
      <span class="es-label">{{tagline}}</span>
      <span class="es-serif">{{message}}</span>
    </div>
    <a href="tel:+46812854555" class="es-phone">
      <span class="es-ring">Ring</span>
      {{phone_display}}
    </a>
  </div>
</section>
"""
    return {
        "block_name": "lumo/emergency-strip",
        "title": "Emergency Strip (akut)",
        "html_template": collapse(html),
        "schema": [
            {"name": "tagline",       "type": "text", "label": "Etikett",        "default": "Akut tandvärk?"},
            {"name": "message",       "type": "text", "label": "Meddelande",     "default": "Vi har ofta tider redan idag."},
            {"name": "phone_display", "type": "text", "label": "Telefon (text)", "default": "08 — 12 85 45 55"},
        ],
    }


def build_dental_triage_widget() -> dict:
    html = """
<section class="dtw-section">
<style>
.dtw-section{background:var(--bg-soft);padding:var(--space-9) 0;border-bottom:1px solid var(--border);}
.dtw-grid{display:grid;grid-template-columns:1fr 1.15fr;gap:80px;align-items:start;}
.dtw-left{position:sticky;top:120px;}
.dtw-trust{display:flex;flex-direction:column;gap:12px;margin-top:32px;}
.dtw-trust-item{display:flex;align-items:flex-start;gap:12px;}
.dtw-trust-dot{width:6px;height:6px;border-radius:50%;background:var(--blush-400);flex-shrink:0;margin-top:6px;}
.dtw-section-hdr{display:grid;grid-template-columns:1fr auto;align-items:end;gap:32px;margin-bottom:48px;padding-bottom:28px;border-bottom:1px solid var(--border);}
.dtw-premium{display:inline-flex;align-items:center;gap:6px;padding:4px 9px;background:rgba(10,10,10,0.88);border:1px solid rgba(249,115,22,0.55);border-radius:4px;color:#f97316;font-size:9px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;position:relative;vertical-align:middle;margin-left:10px;backdrop-filter:blur(4px);cursor:pointer;user-select:none;transition:border-color .2s,color .2s;}
.dtw-premium.dtw-mode-basic{border-color:rgba(120,120,120,0.4);color:var(--fg-subtle);}
.dtw-premium.dtw-mode-basic .dtw-premium-dot{background:var(--fg-subtle);}
.dtw-premium.dtw-mode-basic::before{animation:none;opacity:0;}
.dtw-tooltip{position:absolute;bottom:calc(100% + 12px);left:50%;transform:translateX(-50%);width:280px;background:var(--ink-900);color:var(--white);border-radius:6px;padding:18px 20px;pointer-events:none;opacity:0;transition:opacity .2s ease;white-space:normal;text-transform:none;letter-spacing:0;font-weight:400;z-index:200;box-shadow:0 12px 32px rgba(0,0,0,0.3);}
.dtw-tooltip::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:var(--ink-900);}
.dtw-premium:hover .dtw-tooltip{opacity:1;}
.dtw-premium.dtw-mode-basic .dtw-tooltip{display:none;}
.dtw-tt-title{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,0.5);margin-bottom:12px;}
.dtw-tt-list{list-style:none;padding:0;margin:0 0 14px;display:flex;flex-direction:column;gap:8px;}
.dtw-tt-list li{font-size:12px;line-height:1.5;padding-left:16px;position:relative;color:rgba(255,255,255,0.88);}
.dtw-tt-list li::before{content:'✓';position:absolute;left:0;color:#22c55e;font-size:10px;top:1px;}
.dtw-tt-note{font-size:10px;color:rgba(255,255,255,0.38);border-top:1px solid rgba(255,255,255,0.1);padding-top:10px;line-height:1.5;}
.dtw-premium::before{content:'';position:absolute;inset:-5px;border-radius:5px;border:1.5px solid rgba(249,115,22,0.7);animation:dtw-ring 2.4s ease-out infinite;pointer-events:none;}
.dtw-premium-dot{width:5px;height:5px;border-radius:50%;background:#f97316;flex-shrink:0;}
@keyframes dtw-ring{0%{transform:scale(1);opacity:.7}100%{transform:scale(2.2);opacity:0}}
.dtw-card{background:var(--white);border:1px solid var(--border);box-shadow:var(--shadow-md);padding:clamp(28px,4vw,44px);}
.dtw-prog{margin-bottom:32px;}
.dtw-prog-meta{display:flex;justify-content:space-between;margin-bottom:8px;}
.dtw-prog-track{height:2px;background:var(--border);}
.dtw-prog-fill{height:100%;background:var(--blush-400);transition:width .4s cubic-bezier(.2,.7,.2,1);}
.dtw-opts{display:flex;flex-direction:column;gap:6px;margin-bottom:20px;}
.dtw-opt{display:flex;align-items:center;gap:16px;padding:12px 16px;background:var(--white);border:1px solid var(--border);cursor:pointer;text-align:left;width:100%;transition:border-color .14s,background .14s;font-family:var(--font-sans);}
.dtw-opt:hover{border-color:var(--blush-300);background:var(--blush-50);}
.dtw-opt.sel{border-color:var(--blush-500);background:var(--blush-50);}
.dtw-ind{width:16px;height:16px;border:1.5px solid var(--border-strong);flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all .14s;}
.dtw-ind.radio{border-radius:50%;}
.dtw-opt.sel .dtw-ind{border-color:var(--blush-500);background:var(--blush-500);}
.dtw-opt-lbl{font-size:14px;font-weight:500;color:var(--fg);line-height:1.25;}
.dtw-opt.sel .dtw-opt-lbl{color:var(--fg-strong);}
.dtw-opt-desc{font-size:12px;color:var(--fg-subtle);margin-top:2px;}
.dtw-btn{margin-top:20px;width:100%;padding:10px 18px;border:1px solid transparent;border-radius:4px;font-size:11px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;cursor:pointer;font-family:var(--font-sans);transition:all .2s;}
.dtw-btn.on{background:var(--ink-700);color:var(--white);}
.dtw-btn.on:hover{background:var(--ink-900);}
.dtw-btn.off{background:var(--blush-100);color:var(--blush-300);cursor:not-allowed;}
.dtw-badge{border:1px solid;padding:20px;margin-bottom:20px;display:flex;align-items:flex-start;gap:16px;}
.dtw-badge-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;margin-top:7px;}
.dtw-tips{display:flex;flex-direction:column;gap:1px;background:var(--border);border:1px solid var(--border);margin-bottom:20px;}
.dtw-tip{background:var(--white);padding:16px 20px;display:flex;flex-direction:column;gap:4px;}
.dtw-tip-lbl{font-size:9px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;}
.dtw-tip-txt{font-family:var(--font-serif);font-weight:400;font-size:16px;line-height:1.4;letter-spacing:-.01em;color:var(--fg-strong);}
.dtw-actions{display:flex;flex-direction:column;gap:8px;}
.dtw-actions a{display:block;text-align:center;padding:10px 18px;border-radius:4px;text-decoration:none;font-size:11px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;font-family:var(--font-sans);transition:all .2s;}
.dtw-divider{height:1px;background:var(--border);margin:20px 0;}
.dtw-restart{background:none;border:none;color:var(--fg-subtle);font-size:12px;cursor:pointer;font-family:var(--font-sans);letter-spacing:.04em;padding:0;transition:color .14s;}
.dtw-restart:hover{color:var(--fg-muted);}
.dtw-back{background:none;border:none;padding:0;cursor:pointer;font-size:11px;color:var(--fg-subtle);font-family:var(--font-sans);letter-spacing:.04em;transition:color .14s;}
.dtw-back:hover{color:var(--fg-muted);}
.dtw-part-lbl{font-size:10px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--fg-subtle);margin-bottom:8px;}
.dtw-opts--row{flex-direction:row;}
.dtw-opts--row .dtw-opt{flex:1;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:14px 8px;gap:4px;}
.dtw-opts--row .dtw-ind{display:none;}
.dtw-opts--row .dtw-opt-lbl{font-size:13px;font-weight:600;}
.dtw-opts--row .dtw-opt-desc{font-size:11px;color:var(--fg-subtle);text-align:center;margin-top:0;}
.dtw-analyzing{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 0;gap:20px;}
.dtw-dots{display:flex;gap:7px;}
.dtw-dots span{width:6px;height:6px;border-radius:50%;background:var(--blush-400);animation:dtw-dot 1.2s ease-in-out infinite;}
.dtw-dots span:nth-child(2){animation-delay:.16s;}
.dtw-dots span:nth-child(3){animation-delay:.32s;}
@keyframes dtw-dot{0%,80%,100%{transform:translateY(0);opacity:.25}40%{transform:translateY(-5px);opacity:1}}
@keyframes dtw-slide{from{opacity:0;transform:translateX(18px)}to{opacity:1;transform:translateX(0)}}
@keyframes dtw-up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes dtw-check-pop{0%{transform:scale(.3);opacity:0}65%{transform:scale(1.25);opacity:1}100%{transform:scale(1)}}
@keyframes dtw-check-draw{from{stroke-dashoffset:20}to{stroke-dashoffset:0}}
.dtw-anim-slide{animation:dtw-slide .28s cubic-bezier(.2,.7,.2,1) both;}
.dtw-anim-up{animation:dtw-up .36s cubic-bezier(.2,.7,.2,1) both;}
.dtw-check{animation:dtw-check-pop .22s cubic-bezier(.2,.7,.2,1) both;}
.dtw-check path{stroke-dasharray:20;stroke-dashoffset:0;animation:dtw-check-draw .2s cubic-bezier(.2,.7,.2,1) .04s both;}
@media(max-width:900px){.dtw-grid{grid-template-columns:1fr;gap:40px;}.dtw-left{position:static;}.dtw-section-hdr{grid-template-columns:1fr;gap:16px;}.dtw-section-hdr p{text-align:left;}}
</style>
<div class="container-wide">
  <div class="dtw-section-hdr">
    <div>
      <div style="margin-bottom:12px;display:flex;align-items:center;">
        <span class="eyebrow">{{eyebrow}}</span>
        <span class="dtw-premium" id="dtw-mode-btn" onclick="dtwToggle()"><span class="dtw-premium-dot"></span><span id="dtw-mode-lbl">Premium</span><div class="dtw-tooltip"><div class="dtw-tt-title">Varför Premium?</div><ul class="dtw-tt-list"><li>Patienten vet vad de ska göra — direkt på sidan</li><li>Färre samtal och frågemail till receptionen</li><li>Rätt bokningar — ingen som ringer i onödan</li><li>Sparar tid för både patient och personal</li></ul><div class="dtw-tt-note">Innehållet anpassas helt efter er kliniks önskemål.</div></div></span>
      </div>
      <h2 style="max-width:22ch;">{{heading}}</h2>
    </div>
    <p class="small" id="dtw-subtext" style="max-width:32ch;text-align:right;margin:0;">{{subtext}}</p>
  </div>
  <div class="dtw-grid" id="dtw-body">
    <div class="dtw-left">
      <p style="color:var(--ink-500);font-size:19px;line-height:1.55;margin-bottom:32px;max-width:38ch;">Besvara <em style="color:var(--fg-accent);font-family:var(--font-serif);font-style:italic;font-weight:400;font-size:x-large;">tre korta frågor</em> om dina besvär. Guiden ger en rekommendation direkt — baserad på kliniska riktlinjer.</p>
      <div class="dtw-trust">
        <div class="dtw-trust-item"><div class="dtw-trust-dot"></div><div><div style="font-size:14px;font-weight:500;color:var(--fg-strong);margin-bottom:2px;">{{trust_1_title}}</div><div style="font-size:12px;color:var(--fg-subtle);">{{trust_1_desc}}</div></div></div>
        <div class="dtw-trust-item"><div class="dtw-trust-dot"></div><div><div style="font-size:14px;font-weight:500;color:var(--fg-strong);margin-bottom:2px;">{{trust_2_title}}</div><div style="font-size:12px;color:var(--fg-subtle);">{{trust_2_desc}}</div></div></div>
        <div class="dtw-trust-item"><div class="dtw-trust-dot"></div><div><div style="font-size:14px;font-weight:500;color:var(--fg-strong);margin-bottom:2px;">{{trust_3_title}}</div><div style="font-size:12px;color:var(--fg-subtle);">{{trust_3_desc}}</div></div></div>
      </div>
    </div>
    <div class="dtw-card" id="dtw-root"></div>
  </div>
  <div id="dtw-triage-panel" style="display:none">
    <div class="tg-cards">
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--urgent">Ring idag</div>
        <h3>Kraftig tandvärk</h3>
        <p>Ihållande, värkande smärta som inte ger med sig.</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--urgent">Ring idag</div>
        <h3>Sprucken eller bruten tand</h3>
        <p>Bit eller fall som skadat en tand — även utan smärta.</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--critical">Akut — ring nu</div>
        <h3>Tand som slagits loss</h3>
        <p>Lägg tanden i mjölk eller saliv och kontakta oss direkt.</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--soon">Inom 1–2 dagar</div>
        <h3>Förlorad fyllning eller krona</h3>
        <p>Tanden är känslig men inte alltid smärtsam.</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--urgent">Ring idag</div>
        <h3>Svullnad eller infektion</h3>
        <p>Var- eller vätskebildning, eventuellt feber.</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--critical">Akut — ring nu</div>
        <h3>Käksmärta efter trauma</h3>
        <p>Slag mot ansiktet eller plötslig orörlighet i käken.</p>
      </article>
    </div>
  </div>
</div>
<script>
(function() {
var PHONE = '{{clinic_phone}}';
var BOOKING = '#tdl-booking-widget';
var Qs = [
  {id:'symptom',title:'Vilket är ditt huvudbesär?',sub:'Välj det alternativ som stämmer bäst',type:'single',opts:[
    {id:'pain',lbl:'Smärta eller tandvärk',desc:'Värkande, pulserande eller skarp smärta'},
    {id:'trauma',lbl:'Skada eller olycka',desc:'Slag, fall eller annan yttre påverkan'},
    {id:'swelling',lbl:'Svullnad',desc:'Svullnad i kind, tandkött eller hals'},
    {id:'filling',lbl:'Tappat lagning eller krona',desc:'Lagning, krona eller bro har lossnat'},
    {id:'sensitivity',lbl:'Känslighet',desc:'Ömhet mot kallt, varmt eller sött'},
    {id:'cosmetic',lbl:'Estetik eller rutinkontroll',desc:'Blekning, utseende eller vanlig kontroll'}
  ]},
  {id:'severity',title:'Hur stark är besvären och hur länge har du haft dem?',sub:'Svara på båda delarna nedan',type:'compound',parts:[
    {id:'severity',lbl:'Allvarlighetsgrad',opts:[
      {id:'mild',lbl:'Mild',desc:'Knappt märkbar — stör inte vardagen',color:'#22c55e'},
      {id:'moderate',lbl:'Måttlig',desc:'Påtaglig — påverkar vardagen något',color:'#f59e0b'},
      {id:'severe',lbl:'Stark',desc:'Kraftig — svårt att fungera normalt',color:'#ef4444'}
    ]},
    {id:'duration',lbl:'Hur länge?',layout:'row',opts:[
      {id:'hours',lbl:'I dag',desc:'0–24 timmar'},
      {id:'days',lbl:'Några dagar',desc:'1–7 dagar'},
      {id:'weeks',lbl:'Länge',desc:'Mer än 1 vecka'}
    ]}
  ]},
  {id:'systemics',title:'Har du något av dessa symtom?',sub:'Markera alla som stämmer — eller välj ”Inget av ovanstående”',type:'multi',opts:[
    {id:'fever',lbl:'Feber över 38 °C'},
    {id:'swelling_neck',lbl:'Svullnad mot hals eller käke'},
    {id:'swallowing',lbl:'Svårt att svälja'},
    {id:'breathing',lbl:'Svårt att andas'},
    {id:'none',lbl:'Inget av ovanstående',excl:true}
  ]},
];
var OUTCOMES = {
  emergency_medical:{dot:'#ef4444',bg:'#fef2f2',border:'#fecaca',ew:'Medicinskt akut',lbl:'Ring 112 nu',body:'Dina symtom kan tyda på ett livshotande tillstånd som kräver omedelbar sjukvård — inte tandvård. Andningssvårigheter eller sväljproblem i kombination med dental infektion kan vara livshotande.',tips:[{lbl:'Berätta för operatören',txt:'Säg att det gäller misstänkt dental infektion med andnings- eller sväljbesvär.'},{lbl:'Sitt upprätt',txt:'Lägg dig inte ner — det kan förvärra svullnad mot halsen.'}],actions:[{lbl:'Ring 112',href:'tel:112',primary:true}]},
  emergency_dental:{dot:'#f97316',bg:'#fff7ed',border:'#fed7aa',ew:'Tandvårdsakut',lbl:'Kontakta tandläkare idag',body:'Du bör träffa en tandläkare samma dag. Dina symtom tyder på ett akut tillstånd som kräver snabb behandling. Ring oss direkt — vi har avsatta tider för akuta patienter.',tips:[{lbl:'Om tand slagits loss',txt:'Lägg tanden i mjölk eller saliv — rör inte roten. Tid är avgörande.'},{lbl:'Om kraftig smärta',txt:'Ta receptfria smärtstillande (ibuprofen eller paracetamol) i väntan på tandläkartid.'},{lbl:'Om svullnad',txt:'Kyl utifrån med ispack insvept i handduk — aldrig direkt mot huden.'},{lbl:'Om kliniken är stängd',txt:'Ring 1177 för hänvisning till jourhavande tandläkare.'}],actions:[{lbl:'Ring kliniken',href:'tel:'+PHONE,primary:true}]},
  book_soon:{dot:'#f59e0b',bg:'#fffbeb',border:'#fde68a',ew:'Bör undersökas snart',lbl:'Boka tid inom 1–2 dagar',body:'Ditt tillstånd är inte omedelbart akut men bör undersökas relativt snart. Boka en tid inom de närmaste dagarna för att undvika att bevären förvärras.',tips:[{lbl:'Under tiden',txt:'Undvik att tugga på den berörda sidan tills du fått en tid.'},{lbl:'Vid försämring',txt:'Hör av dig tidigare — vi prioriterar bevär som förvärras.'}],actions:[{lbl:'Boka tid nu',href:BOOKING,primary:true},{lbl:'Ring kliniken',href:'tel:'+PHONE,primary:false}]},
  book_regular:{dot:'var(--blush-400)',bg:'var(--blush-50)',border:'var(--blush-200)',ew:'Inget akut',lbl:'Boka vanlig tid',body:'Dina bevär verkar inte akuta. Boka en vanlig tid för undersökning eller behandling. En tidig kontroll är alltid bättre än att vänta för länge.',tips:[{lbl:'Bra att veta',txt:'En tidig undersökning förhindrar att små problem blir stora — och dyrare.'}],actions:[{lbl:'Boka tid online',href:BOOKING,primary:true}]}
};
function skip(id, a) {
  var sys = a.systemics || [];
  if (id === 'severity') return a.symptom === 'cosmetic';
  if (id === 'systemics') return ['cosmetic','filling','sensitivity'].indexOf(a.symptom) > -1 || a.severity === 'mild';
  return false;
}
function calcTriage(a) {
  var sys = a.systemics || [];
  if (sys.indexOf('breathing') > -1 || sys.indexOf('swallowing') > -1) return 'emergency_medical';
  if (sys.indexOf('fever') > -1 && sys.indexOf('swelling_neck') > -1) return 'emergency_medical';
  if (a.symptom === 'swelling'  && a.severity === 'severe')   return 'emergency_dental';
  if (a.symptom === 'trauma'    && a.severity !== 'mild')     return 'emergency_dental';
  if (a.symptom === 'pain'      && a.severity === 'severe')   return 'emergency_dental';
  if (a.symptom === 'swelling'  && a.severity === 'moderate') return 'emergency_dental';
  if (sys.indexOf('fever') > -1 || sys.indexOf('swelling_neck') > -1) return 'emergency_dental';
  if (a.symptom === 'filling')                                return 'book_soon';
  if (a.severity === 'moderate')                             return 'book_soon';
  if (a.symptom === 'sensitivity' && a.severity === 'severe') return 'book_soon';
  if (a.symptom === 'trauma'      && a.severity === 'mild')   return 'book_soon';
  if (a.duration === 'hours') return 'book_soon';
  return 'book_regular';
}
var state = {answers:{}, qIdx:0, multiSel:[], result:null, analyzing:false, scrolled:false};
function visibleQs() { return Qs.filter(function(q){ return !skip(q.id, state.answers); }); }
function render() {
  var root = document.getElementById('dtw-root');
  if (!root) return;
  var vqs = visibleQs();
  var q = vqs[state.qIdx];
  var total = vqs.length;
  var pct = state.result ? 100 : Math.round((state.qIdx / total) * 100);
  if (state.analyzing) {
    root.innerHTML = '<div class="dtw-analyzing"><div class="dtw-dots"><span></span><span></span><span></span></div><div style="font-size:12px;color:var(--fg-subtle);letter-spacing:.1em;">Analyserar din bedömning</div></div>';
    return;
  }
  if (state.result) {
    var o = OUTCOMES[state.result];
    var tipsHtml = '';
    if (o.tips) {
      tipsHtml = '<div class="dtw-tips">';
      o.tips.forEach(function(t){ tipsHtml += '<div class="dtw-tip"><div class="dtw-tip-lbl" style="color:'+o.dot+'">'+t.lbl+'</div><div class="dtw-tip-txt">'+t.txt+'</div></div>'; });
      tipsHtml += '</div>';
    }
    var actHtml = '<div class="dtw-actions">';
    o.actions.forEach(function(ac) {
      actHtml += '<a href="'+ac.href+'" style="'+(ac.primary ? 'background:var(--ink-700);color:var(--white);' : 'background:transparent;color:var(--ink-700);border:1px solid var(--ink-700);')+'">'+ac.lbl+'</a>';
    });
    actHtml += '</div>';
    root.innerHTML = '<div class="dtw-anim-up">'
      +'<div class="dtw-badge" style="background:'+o.bg+';border-color:'+o.border+'">'
      +'<div class="dtw-badge-dot" style="background:'+o.dot+'"></div>'
      +'<div><div class="eyebrow" style="margin-bottom:8px;">'+o.ew+'</div>'
      +'<h3 style="font-family:var(--font-serif);font-weight:400;font-size:24px;letter-spacing:-.01em;color:var(--fg-strong);">'+o.lbl+'</h3></div></div>'
      +'<p style="font-size:14px;color:var(--fg-muted);line-height:1.7;margin-bottom:20px;">'+o.body+'</p>'
      +tipsHtml+actHtml
      +'<div class="dtw-divider"></div>'
      +'<button class="dtw-restart" onclick="dtwRestart()">← Gör om bedömningen</button>'
      +'</div>';
    return;
  }
  var optsHtml = '';
  var canNext;
  if (q.type === 'compound') {
    q.parts.forEach(function(part, idx) {
      var pOpts = '';
      part.opts.forEach(function(opt) {
        var sel = state.answers[part.id] === opt.id;
        var indHtml = sel
          ? '<div class="dtw-ind radio sel"><svg class="dtw-check" width="9" height="7" viewBox="0 0 9 7" fill="none"><path d="M1 3.5L3 5.5L8 1" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
          : '<div class="dtw-ind radio"></div>';
        var descHtml = opt.desc ? '<div class="dtw-opt-desc">'+opt.desc+'</div>' : '';
        var optStyle = opt.color ? 'border-left:3px solid '+opt.color+';' : '';
        pOpts += '<button class="dtw-opt'+(sel?' sel':'')+'" style="'+optStyle+'" data-oid="'+opt.id+'" data-qid="'+part.id+'" onclick="dtwSelect(this.dataset.oid,false,this.dataset.qid)">'+indHtml+'<div><div class="dtw-opt-lbl">'+opt.lbl+'</div>'+descHtml+'</div></button>';
      });
      var rowCls = part.layout === 'row' ? ' dtw-opts--row' : '';
      optsHtml += (idx>0?'<div style="height:20px"></div>':'')+'<div class="dtw-part-lbl">'+part.lbl+'</div><div class="dtw-opts'+rowCls+'">'+pOpts+'</div>';
    });
    canNext = q.parts.filter(function(p){ return !state.answers[p.id]; }).length === 0;
  } else {
    var isSel = function(id) { return q.type === 'multi' ? state.multiSel.indexOf(id) > -1 : state.answers[q.id] === id; };
    q.opts.forEach(function(opt) {
      var sel = isSel(opt.id);
      var indHtml = sel
        ? '<div class="dtw-ind'+(q.type==='multi'?'':' radio')+' sel"><svg class="dtw-check" width="9" height="7" viewBox="0 0 9 7" fill="none"><path d="M1 3.5L3 5.5L8 1" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        : '<div class="dtw-ind'+(q.type==='multi'?'':' radio')+'"></div>';
      var descHtml = opt.desc ? '<div class="dtw-opt-desc">'+opt.desc+'</div>' : '';
      optsHtml += '<button class="dtw-opt'+(sel?' sel':'')+'" data-oid="'+opt.id+'" data-excl="'+(opt.excl?'1':'0')+'" onclick="dtwSelect(this.dataset.oid,this.dataset.excl==1)">'+indHtml+'<div><div class="dtw-opt-lbl">'+opt.lbl+'</div>'+descHtml+'</div></button>';
    });
    optsHtml = '<div class="dtw-opts">'+optsHtml+'</div>';
    canNext = q.type === 'multi' ? state.multiSel.length > 0 : !!state.answers[q.id];
  }
  var isLast = state.qIdx + 1 === total;
  var backBtn = state.qIdx > 0 ? '<button class="dtw-back" onclick="dtwBack()">← Tillbaka</button>' : '<span></span>';
  root.innerHTML = '<div class="dtw-prog">'
    +'<div class="dtw-prog-meta">'+backBtn+'<span style="font-size:12px;color:var(--fg-subtle);">Fråga '+(state.qIdx+1)+'</span><span style="font-size:12px;color:var(--fg-subtle);">'+pct+'%</span></div>'
    +'<div class="dtw-prog-track"><div class="dtw-prog-fill" style="width:'+pct+'%"></div></div>'
    +'</div>'
    +'<div class="dtw-anim-slide">'
    +'<h3 style="font-family:var(--font-serif);font-weight:400;font-size:24px;letter-spacing:-.01em;color:var(--fg-strong);margin-bottom:8px;">'+q.title+'</h3>'
    +(q.sub ? '<p style="font-size:14px;color:var(--fg-muted);margin-bottom:20px;">'+q.sub+'</p>' : '')
    +'<div class="dtw-opts">'+optsHtml+'</div>'
    +'<button class="dtw-btn '+(canNext?'on':'off')+'" onclick="dtwNext()">'+(isLast?'Se rekommendation':'Nästa')+'</button>'
    +'</div>';
}
window.dtwSelect = function(id, excl, qid) {
  if (!state.scrolled) {
    state.scrolled = true;
    var card = document.getElementById('dtw-root');
    if (card) card.scrollIntoView({behavior:'smooth', block:'center'});
  }
  var vqs = visibleQs();
  var q = vqs[state.qIdx];
  if (q.type === 'compound') {
    state.answers[qid] = id;
  } else if (q.type === 'multi') {
    if (excl) { state.multiSel = ['none']; }
    else {
      var without = state.multiSel.filter(function(x){ return x !== 'none'; });
      var i = without.indexOf(id);
      state.multiSel = i > -1 ? without.filter(function(x){ return x !== id; }) : without.concat([id]);
    }
  } else {
    state.answers[q.id] = id;
  }
  render();
};
window.dtwNext = function() {
  var vqs = visibleQs();
  var q = vqs[state.qIdx];
  var canNext = q.type === 'compound'
    ? q.parts.filter(function(p){ return !state.answers[p.id]; }).length === 0
    : q.type === 'multi' ? state.multiSel.length > 0 : !!state.answers[q.id];
  if (!canNext) return;
  if (q.type === 'multi') state.answers[q.id] = state.multiSel.slice();
  var newVqs = Qs.filter(function(qq){ return !skip(qq.id, state.answers); });
  if (state.qIdx + 1 < newVqs.length) {
    state.qIdx++;
    state.multiSel = [];
    render();
  } else {
    var finalAnswers = state.answers;
    state.analyzing = true;
    render();
    setTimeout(function() {
      state.analyzing = false;
      state.result = calcTriage(finalAnswers);
      render();
    }, 1100);
  }
};
window.dtwToggle = function() {
  var body  = document.getElementById('dtw-body');
  var panel = document.getElementById('dtw-triage-panel');
  var lbl   = document.getElementById('dtw-mode-lbl');
  var btn   = document.getElementById('dtw-mode-btn');
  var sub   = document.getElementById('dtw-subtext');
  if (!body || !panel) return;
  var isPremium = body.style.display !== 'none';
  body.style.display  = isPremium ? 'none' : '';
  panel.style.display = isPremium ? ''     : 'none';
  if (lbl) lbl.textContent = isPremium ? 'Basic' : 'Premium';
  if (btn) btn.classList[isPremium ? 'add' : 'remove']('dtw-mode-basic');
  if (sub) {
    if (!sub.dataset.premium) sub.dataset.premium = sub.textContent;
    sub.textContent = isPremium ? 'Är du osäker — ring oss alltid. Vi prioriterar akuta besvär och hjälper dig vidare på telefon.' : sub.dataset.premium;
  }
};
window.dtwBack = function() {
  if (state.qIdx <= 0) return;
  var vqs = visibleQs();
  var q = vqs[state.qIdx];
  if (q.type === 'compound') {
    q.parts.forEach(function(p){ delete state.answers[p.id]; });
  } else {
    delete state.answers[q.id];
  }
  state.multiSel = [];
  state.qIdx--;
  render();
};
window.dtwRestart = function() {
  state = {answers:{}, qIdx:0, multiSel:[], result:null, analyzing:false, scrolled:false};
  render();
};
render();
})();
</script>
</section>
"""
    return {
        "block_name": "lumo/dental-triage-widget",
        "title": "Dental Triage Widget",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",       "type": "text",     "label": "Etikett",           "default": "Akutbedömning"},
            {"name": "heading",       "type": "text",     "label": "Rubrik",             "default": "Osäker på hur akut det är?"},
            {"name": "subtext",       "type": "text",     "label": "Undertext",          "default": "Tre frågor hjälper dig avgöra om du behöver komma in idag, inom några dagar — eller ringa 112."},
            {"name": "lead",          "type": "textarea", "label": "Lead-text",          "default": "Besvara tre korta frågor om dina besvär. Guiden ger en rekommendation direkt — baserad på kliniska riktlinjer."},
            {"name": "trust_1_title", "type": "text",     "label": "Förtroendepoint 1 rubrik", "default": "Anpassad för tandvårdsbesvär"},
            {"name": "trust_1_desc",  "type": "text",     "label": "Förtroendepoint 1 text",   "default": "Frågorna är utformade av vår kliniska personal."},
            {"name": "trust_2_title", "type": "text",     "label": "Förtroendepoint 2 rubrik", "default": "Ingen inloggning krävs"},
            {"name": "trust_2_desc",  "type": "text",     "label": "Förtroendepoint 2 text",   "default": "Dina svar sparas inte och lämnar inte sidan."},
            {"name": "trust_3_title", "type": "text",     "label": "Förtroendepoint 3 rubrik", "default": "Alltid mänsklig bedömning"},
            {"name": "trust_3_desc",  "type": "text",     "label": "Förtroendepoint 3 text",   "default": "Guiden ersätter inte ett tandläkarbesök."},
            {"name": "clinic_phone",  "type": "text",     "label": "Klinikens telefon",  "default": "0812854555"},
        ],
    }


def build_triage_grid() -> dict:
    # Urgency-färg per position är hårdkodad (klinisk prioritetsordning)
    # Urgency-TEXT och kortens titel + beskrivning är editerbara ACF-fält
    html = """
<section class="triage-grid">
  <div class="container-wide">
    <div class="tg-header">
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">{{eyebrow}}</div>
        <h2>{{heading}}</h2>
      </div>
      <p class="small tg-sub">{{subtext}}</p>
    </div>
    <div class="tg-cards">
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--urgent">{{urgency_1}}</div>
        <h3>{{title_1}}</h3>
        <p>{{desc_1}}</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--urgent">{{urgency_2}}</div>
        <h3>{{title_2}}</h3>
        <p>{{desc_2}}</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--critical">{{urgency_3}}</div>
        <h3>{{title_3}}</h3>
        <p>{{desc_3}}</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--soon">{{urgency_4}}</div>
        <h3>{{title_4}}</h3>
        <p>{{desc_4}}</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--urgent">{{urgency_5}}</div>
        <h3>{{title_5}}</h3>
        <p>{{desc_5}}</p>
      </article>
      <article class="tg-card">
        <div class="tg-urgency tg-urgency--critical">{{urgency_6}}</div>
        <h3>{{title_6}}</h3>
        <p>{{desc_6}}</p>
      </article>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/triage-grid",
        "title": "Triage Grid",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",   "type": "text",     "label": "Etikett",         "default": "Triage · Vad gäller dig?"},
            {"name": "heading",   "type": "text",     "label": "Rubrik",           "default": "Vanliga akuta situationer — och hur snabbt du bör söka."},
            {"name": "subtext",   "type": "textarea", "label": "Undertext",        "default": "Är du osäker — ring oss alltid. Vi prioriterar akuta besvär och hjälper dig vidare på telefon."},
            {"name": "urgency_1", "type": "text",     "label": "Kort 1 – prioritet","default": "Ring idag"},
            {"name": "title_1",   "type": "text",     "label": "Kort 1 – rubrik",  "default": "Kraftig tandvärk"},
            {"name": "desc_1",    "type": "textarea", "label": "Kort 1 – text",    "default": "Ihållande, värkande smärta som inte ger med sig."},
            {"name": "urgency_2", "type": "text",     "label": "Kort 2 – prioritet","default": "Ring idag"},
            {"name": "title_2",   "type": "text",     "label": "Kort 2 – rubrik",  "default": "Sprucken eller bruten tand"},
            {"name": "desc_2",    "type": "textarea", "label": "Kort 2 – text",    "default": "Bit eller fall som skadat en tand — även utan smärta."},
            {"name": "urgency_3", "type": "text",     "label": "Kort 3 – prioritet","default": "Akut — ring nu"},
            {"name": "title_3",   "type": "text",     "label": "Kort 3 – rubrik",  "default": "Tand som slagits loss"},
            {"name": "desc_3",    "type": "textarea", "label": "Kort 3 – text",    "default": "Lägg tanden i mjölk eller saliv och kontakta oss direkt."},
            {"name": "urgency_4", "type": "text",     "label": "Kort 4 – prioritet","default": "Inom 1–2 dagar"},
            {"name": "title_4",   "type": "text",     "label": "Kort 4 – rubrik",  "default": "Förlorad fyllning eller krona"},
            {"name": "desc_4",    "type": "textarea", "label": "Kort 4 – text",    "default": "Tanden är känslig men inte alltid smärtsam."},
            {"name": "urgency_5", "type": "text",     "label": "Kort 5 – prioritet","default": "Ring idag"},
            {"name": "title_5",   "type": "text",     "label": "Kort 5 – rubrik",  "default": "Svullnad eller infektion"},
            {"name": "desc_5",    "type": "textarea", "label": "Kort 5 – text",    "default": "Var- eller vätskebildning, eventuellt feber."},
            {"name": "urgency_6", "type": "text",     "label": "Kort 6 – prioritet","default": "Akut — ring nu"},
            {"name": "title_6",   "type": "text",     "label": "Kort 6 – rubrik",  "default": "Käksmärta efter trauma"},
            {"name": "desc_6",    "type": "textarea", "label": "Kort 6 – text",    "default": "Slag mot ansiktet eller plötslig orörlighet i käken."},
        ],
    }


def build_process_steps() -> dict:
    html = """
<section class="process-steps">
  <div class="container-wide">
    <div class="ps-header">
      <div class="eyebrow" style="margin-bottom:16px;">{{eyebrow}}</div>
      <h2>{{heading}}</h2>
    </div>
    <div class="ps-grid">
      <article class="ps-step">
        <div class="ps-num">01</div>
        <h3>{{step_1_title}}</h3>
        <p>{{step_1_desc}}</p>
      </article>
      <article class="ps-step">
        <div class="ps-num">02</div>
        <h3>{{step_2_title}}</h3>
        <p>{{step_2_desc}}</p>
      </article>
      <article class="ps-step">
        <div class="ps-num">03</div>
        <h3>{{step_3_title}}</h3>
        <p>{{step_3_desc}}</p>
      </article>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/process-steps",
        "title": "Process Steps",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",      "type": "text",     "label": "Etikett"},
            {"name": "heading",      "type": "text",     "label": "Rubrik"},
            {"name": "step_1_title", "type": "text",     "label": "Steg 1 – titel"},
            {"name": "step_1_desc",  "type": "textarea", "label": "Steg 1 – text"},
            {"name": "step_2_title", "type": "text",     "label": "Steg 2 – titel"},
            {"name": "step_2_desc",  "type": "textarea", "label": "Steg 2 – text"},
            {"name": "step_3_title", "type": "text",     "label": "Steg 3 – titel"},
            {"name": "step_3_desc",  "type": "textarea", "label": "Steg 3 – text"},
        ],
    }


def build_price_row() -> dict:
    html = """
<section class="price-row">
  <div class="container-wide">
    <div class="pr-grid">
      <div>
        <div class="eyebrow" style="margin-bottom:16px;">{{eyebrow}}</div>
        <h2>{{heading}}</h2>
        <p class="pr-intro">{{intro}}</p>
      </div>
      <div class="pr-table">
        <div class="pr-row"><div class="pr-label">{{row_1_label}}</div><div class="pr-price">{{row_1_price}}</div></div>
        <div class="pr-row"><div class="pr-label">{{row_2_label}}</div><div class="pr-price">{{row_2_price}}</div></div>
        <div class="pr-row"><div class="pr-label">{{row_3_label}}</div><div class="pr-price">{{row_3_price}}</div></div>
        <div class="pr-row"><div class="pr-label">{{row_4_label}}</div><div class="pr-price">{{row_4_price}}</div></div>
      </div>
    </div>
  </div>
</section>
"""
    return {
        "block_name": "lumo/price-row",
        "title": "Pristabell",
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",     "type": "text",     "label": "Etikett"},
            {"name": "heading",     "type": "text",     "label": "Rubrik"},
            {"name": "intro",       "type": "textarea", "label": "Introtext"},
            {"name": "row_1_label", "type": "text",     "label": "Rad 1 – text"},
            {"name": "row_1_price", "type": "text",     "label": "Rad 1 – pris"},
            {"name": "row_2_label", "type": "text",     "label": "Rad 2 – text"},
            {"name": "row_2_price", "type": "text",     "label": "Rad 2 – pris"},
            {"name": "row_3_label", "type": "text",     "label": "Rad 3 – text"},
            {"name": "row_3_price", "type": "text",     "label": "Rad 3 – pris"},
            {"name": "row_4_label", "type": "text",     "label": "Rad 4 – text"},
            {"name": "row_4_price", "type": "text",     "label": "Rad 4 – pris"},
        ],
    }


def _mst(var: str) -> str:
    """Return {{var}} mustache placeholder."""
    return "{{" + var + "}}"


def _ig_hdr_html(eyebrow_var: str = "eyebrow", heading_var: str = "heading") -> str:
    return (
        f'<div class="ig-hdr">'
        f'<div class="eyebrow" style="margin-bottom:16px;">{_mst(eyebrow_var)}</div>'
        f'<h2 class="ig-heading">{_mst(heading_var)}</h2>'
        f'</div>'
    )


def build_stats_strip(block_name: str, title: str, items: list[dict]) -> dict:
    """Stats strip utan header — Implantat & Tandreglering.
    items: [{"val": ..., "desc": ...}]
    """
    n = len(items)
    cells = ""
    for i, _item in enumerate(items, 1):
        cells += (
            f'<div style="background:var(--white);padding:40px 32px;">'
            f'<div style="font-family:var(--font-serif);font-weight:300;'
            f'font-size:clamp(40px,4vw,64px);line-height:1;letter-spacing:-0.03em;'
            f'color:var(--ink-700);margin-bottom:14px;">{_mst(f"val_{i}")}</div>'
            f'<div style="font-size:14px;color:var(--ink-500);line-height:1.55;">{_mst(f"desc_{i}")}</div>'
            f'</div>'
        )
    html = f"""
<section class="ig-section" style="padding-top:0;">
  <div class="container-wide" style="padding-top:0;">
    <div class="ig-grid ig-grid--{n}" style="border-top:1px solid var(--border);">
      {cells}
    </div>
  </div>
</section>
"""
    schema: list[dict] = []
    for i, item in enumerate(items, 1):
        schema.append({"name": f"val_{i}",  "type": "text",     "label": f"Stat {i} – värde",        "default": item.get("val",  "")})
        schema.append({"name": f"desc_{i}", "type": "textarea", "label": f"Stat {i} – beskrivning",  "default": item.get("desc", "")})
    return {"block_name": block_name, "title": title, "html_template": collapse(html), "schema": schema}


def build_stages_grid(block_name: str, title: str, eyebrow: str, heading: str,
                      items: list[dict]) -> dict:
    """Karies-stadier med färgpunkt per allvarlighetsgrad.
    items: [{"stage": ..., "title": ..., "desc": ...}]
    """
    dot_colors = ["var(--sage-300)", "var(--sage-500)", "var(--sage-600)", "var(--ink-700)"]
    cells = ""
    for i, _item in enumerate(items, 1):
        color = dot_colors[i - 1] if i <= len(dot_colors) else "var(--sage-600)"
        cells += (
            f'<article style="background:var(--white);padding:40px 32px;display:flex;flex-direction:column;gap:14px;">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{color};margin-bottom:6px;"></div>'
            f'<div style="font-size:10px;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:var(--fg-muted);">{_mst(f"stage_{i}")}</div>'
            f'<h3 style="font-family:var(--font-serif);font-weight:400;font-size:24px;line-height:1.2;'
            f'letter-spacing:-0.02em;color:var(--ink-700);margin:0;">{_mst(f"title_{i}")}</h3>'
            f'<p style="font-size:14px;line-height:1.65;color:var(--ink-500);margin:0;">{_mst(f"desc_{i}")}</p>'
            f'</article>'
        )
    html = f"""
<section class="ig-section">
  <div class="container-wide">
    {_ig_hdr_html()}
    <div class="ig-grid ig-grid--4">
      {cells}
    </div>
  </div>
</section>
"""
    schema: list[dict] = [
        {"name": "eyebrow", "type": "text", "label": "Etikett", "default": eyebrow},
        {"name": "heading", "type": "text", "label": "Rubrik",  "default": heading},
    ]
    for i, item in enumerate(items, 1):
        schema.append({"name": f"stage_{i}", "type": "text",     "label": f"Stadium {i} – etikett",    "default": item.get("stage", f"Stadium {i}")})
        schema.append({"name": f"title_{i}", "type": "text",     "label": f"Stadium {i} – rubrik",     "default": item.get("title", "")})
        schema.append({"name": f"desc_{i}",  "type": "textarea", "label": f"Stadium {i} – beskrivning","default": item.get("desc",  "")})
    return {"block_name": block_name, "title": title, "html_template": collapse(html), "schema": schema}


def build_method_comparison(block_name: str, title: str, eyebrow: str, heading: str,
                             items: list[dict]) -> dict:
    """Tandblekning — jämförelse med tid/effekt-rader och badge.
    items: [{"name": ..., "badge": ..., "time": ..., "effect": ..., "desc": ...}]
    """
    cells = ""
    for i, _item in enumerate(items, 1):
        cells += (
            f'<article class="mc-item">'
            f'<div class="mc-name-row">'
            f'<h3 class="mc-name">{_mst(f"m{i}_name")}</h3>'
            f'<span class="mc-badge">{_mst(f"m{i}_badge")}</span>'
            f'</div>'
            f'<div class="mc-meta">'
            f'<div class="mc-meta-row"><span class="mc-meta-label">Tid</span>'
            f'<span class="mc-meta-val">{_mst(f"m{i}_time")}</span></div>'
            f'<div class="mc-meta-row"><span class="mc-meta-label">Effekt</span>'
            f'<span class="mc-meta-val mc-meta-val--accent">{_mst(f"m{i}_effect")}</span></div>'
            f'</div>'
            f'<p class="mc-desc">{_mst(f"m{i}_desc")}</p>'
            f'</article>'
        )
    html = f"""
<section class="mc-section">
  <div class="container-wide">
    <div class="mc-hdr">
      <div class="eyebrow" style="margin-bottom:16px;">{_mst("eyebrow")}</div>
      <h2>{_mst("heading")}</h2>
    </div>
    <div class="mc-grid">
      {cells}
    </div>
  </div>
</section>
"""
    schema: list[dict] = [
        {"name": "eyebrow", "type": "text", "label": "Etikett", "default": eyebrow},
        {"name": "heading", "type": "text", "label": "Rubrik",  "default": heading},
    ]
    for i, item in enumerate(items, 1):
        schema.append({"name": f"m{i}_name",   "type": "text",     "label": f"Metod {i} – namn",    "default": item.get("name",   "")})
        schema.append({"name": f"m{i}_badge",  "type": "text",     "label": f"Metod {i} – badge",   "default": item.get("badge",  "")})
        schema.append({"name": f"m{i}_time",   "type": "text",     "label": f"Metod {i} – tid",     "default": item.get("time",   "")})
        schema.append({"name": f"m{i}_effect", "type": "text",     "label": f"Metod {i} – effekt",  "default": item.get("effect", "")})
        schema.append({"name": f"m{i}_desc",   "type": "textarea", "label": f"Metod {i} – text",    "default": item.get("desc",   "")})
    return {"block_name": block_name, "title": title, "html_template": collapse(html), "schema": schema}


def build_use_cases_grid(block_name: str, title: str, eyebrow: str, heading: str,
                          items: list[dict], cols: int = 3) -> dict:
    """Tandfasader & Tandsten — ren titel+beskrivning utan nummer.
    items: [{"title": ..., "desc": ...}]
    """
    cells = ""
    for i, _item in enumerate(items, 1):
        cells += (
            f'<article style="background:var(--white);padding:40px 32px;display:flex;flex-direction:column;gap:12px;">'
            f'<h3 style="font-family:var(--font-serif);font-weight:400;font-size:24px;line-height:1.2;'
            f'letter-spacing:-0.02em;color:var(--ink-700);margin:0;">{_mst(f"title_{i}")}</h3>'
            f'<p style="font-size:14px;line-height:1.65;color:var(--ink-500);margin:0;">{_mst(f"desc_{i}")}</p>'
            f'</article>'
        )
    html = f"""
<section class="ig-section">
  <div class="container-wide">
    {_ig_hdr_html()}
    <div class="ig-grid ig-grid--{cols}">
      {cells}
    </div>
  </div>
</section>
"""
    schema: list[dict] = [
        {"name": "eyebrow", "type": "text", "label": "Etikett", "default": eyebrow},
        {"name": "heading", "type": "text", "label": "Rubrik",  "default": heading},
    ]
    for i, item in enumerate(items, 1):
        schema.append({"name": f"title_{i}", "type": "text",     "label": f"Punkt {i} – titel",       "default": item.get("title", "")})
        schema.append({"name": f"desc_{i}",  "type": "textarea", "label": f"Punkt {i} – beskrivning", "default": item.get("desc",  "")})
    return {"block_name": block_name, "title": title, "html_template": collapse(html), "schema": schema}


def build_approach_grid(block_name: str, title: str, eyebrow: str, heading: str,
                         items: list[dict], cols: int = 3) -> dict:
    """Tandvårdsrädsla — stora sage-siffror + titel + beskrivning.
    items: [{"num": ..., "title": ..., "desc": ...}]
    """
    cells = ""
    for i, _item in enumerate(items, 1):
        cells += (
            f'<article style="background:var(--white);padding:40px 32px;display:flex;flex-direction:column;gap:12px;">'
            f'<div style="font-family:var(--font-serif);font-weight:300;font-size:48px;line-height:1;'
            f'letter-spacing:-0.03em;color:var(--sage-600);">{_mst(f"num_{i}")}</div>'
            f'<h3 style="font-family:var(--font-serif);font-weight:400;font-size:22px;line-height:1.2;'
            f'letter-spacing:-0.02em;color:var(--ink-700);margin:0;">{_mst(f"title_{i}")}</h3>'
            f'<p style="font-size:14px;line-height:1.65;color:var(--ink-500);margin:0;">{_mst(f"desc_{i}")}</p>'
            f'</article>'
        )
    html = f"""
<section class="ig-section">
  <div class="container-wide">
    {_ig_hdr_html()}
    <div class="ig-grid ig-grid--{cols}">
      {cells}
    </div>
  </div>
</section>
"""
    schema: list[dict] = [
        {"name": "eyebrow", "type": "text", "label": "Etikett", "default": eyebrow},
        {"name": "heading", "type": "text", "label": "Rubrik",  "default": heading},
    ]
    for i, item in enumerate(items, 1):
        schema.append({"name": f"num_{i}",   "type": "text",     "label": f"Punkt {i} – nummer",      "default": item.get("num",   "")})
        schema.append({"name": f"title_{i}", "type": "text",     "label": f"Punkt {i} – titel",       "default": item.get("title", "")})
        schema.append({"name": f"desc_{i}",  "type": "textarea", "label": f"Punkt {i} – beskrivning", "default": item.get("desc",  "")})
    return {"block_name": block_name, "title": title, "html_template": collapse(html), "schema": schema}


def build_process_steps_4(block_name: str, title: str) -> dict:
    """Four-column process steps variant."""
    html = """
<section class="process-steps">
  <div class="container-wide">
    <div class="ps-header">
      <div class="eyebrow" style="margin-bottom:16px;">{{eyebrow}}</div>
      <h2>{{heading}}</h2>
    </div>
    <div class="ps-grid ps-grid--4">
      <article class="ps-step">
        <div class="ps-num">01</div>
        <h3>{{step_1_title}}</h3>
        <p>{{step_1_desc}}</p>
      </article>
      <article class="ps-step">
        <div class="ps-num">02</div>
        <h3>{{step_2_title}}</h3>
        <p>{{step_2_desc}}</p>
      </article>
      <article class="ps-step">
        <div class="ps-num">03</div>
        <h3>{{step_3_title}}</h3>
        <p>{{step_3_desc}}</p>
      </article>
      <article class="ps-step">
        <div class="ps-num">04</div>
        <h3>{{step_4_title}}</h3>
        <p>{{step_4_desc}}</p>
      </article>
    </div>
  </div>
</section>
"""
    return {
        "block_name": block_name,
        "title": title,
        "html_template": collapse(html),
        "schema": [
            {"name": "eyebrow",      "type": "text",     "label": "Etikett"},
            {"name": "heading",      "type": "text",     "label": "Rubrik"},
            {"name": "step_1_title", "type": "text",     "label": "Steg 1 – titel"},
            {"name": "step_1_desc",  "type": "textarea", "label": "Steg 1 – text"},
            {"name": "step_2_title", "type": "text",     "label": "Steg 2 – titel"},
            {"name": "step_2_desc",  "type": "textarea", "label": "Steg 2 – text"},
            {"name": "step_3_title", "type": "text",     "label": "Steg 3 – titel"},
            {"name": "step_3_desc",  "type": "textarea", "label": "Steg 3 – text"},
            {"name": "step_4_title", "type": "text",     "label": "Steg 4 – titel"},
            {"name": "step_4_desc",  "type": "textarea", "label": "Steg 4 – text"},
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
            "image":    "https://swordfish.templweb.com/wp-content/uploads/2026/05/reception.jpg",
            "eyebrow": "Vårt uppdrag",
            "h2": "Din tandhälsa — vårt uppdrag, din trygghet.",
            "body": "<p>På Älvsjö Tandvård är vår vision att erbjuda en tandvårdsupplevelse där du känner dig helt trygg och sedd, oavsett ditt behov. Vår <strong>nyrenoverade klinik</strong> på Prästgårdsgränd 4, bara ett stenkast från Älvsjö pendeltågsstation, är designad för att vara ljus, luftig och tillgänglig — med hiss för din bekvämlighet.</p><p>Hos oss hittar du ett brett spektrum av tandvårdstjänster, från <strong>allmäntandvård och förebyggande vård</strong> för hela familjen, till mer avancerade behandlingar som <strong>tandimplantat</strong> och <strong>osynlig tandreglering med Invisalign</strong>. Vi är anslutna till Försäkringskassan och erbjuder räntefri delbetalning.</p>",
            "cta_text": "Boka tid",
            "cta_link": "#tdl-booking-widget",
        }, "Om oss"),
        "lumo/text-blocks-om-oss",
        "lumo/team",
        "lumo/organisation-om-oss",
        "lumo/cta-strip-om-oss",
        add("map-section", "om-oss", {"heading": "Hitta till kliniken"}, "Om oss"),
        "lumo/arbeta-med-oss",
        "lumo/feedback-form-om-oss",
        "lumo/site-footer",
    ]
    pages.append({"title": "Om oss", "slug": "om-oss", "menu_label": "Om oss", "keep_content": True, "blocks": blocks})

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
        d  = TREATMENT_HERO_DATA[slug]
        pd = TREATMENT_PAGE_DATA[slug]
        b  = d["bullets"]

        # Baka in hero-innehållet i en per-slug variant — aldrig beroende av page_defaults
        hero_v = make_variant(
            bases["treatment-hero"], slug,
            {
                "eyebrow":      d["eyebrow"],
                "title":        d["title"],
                "title_italic": d["title_italic"],
                "ingress":      d["ingress"],
                "bullet_1":     b[0],
                "bullet_2":     b[1],
                "bullet_3":     b[2],
                "bullet_4":     b[3],
                "hero_image":   BASE_IMG + d["image"],
                "stat_label":   d["stat_label"],
                "stat_value":   d["stat_value"],
                "stat_sub":     d["stat_sub"],
            },
            title_sfx=menu_label,
        )
        if hero_v["block_name"] not in seen:
            seen.add(hero_v["block_name"])
            variants.append(hero_v)

        page_defs: dict = {}

        if slug == "akut-tandvard":
            # Per-slug varianter — innehåll inbakat i schema-defaults, aldrig page_defaults
            akut_cb1 = make_variant(bases["content-block-1"], slug, {
                "eyebrow":  pd["cb1_eyebrow"],
                "h2":       pd["cb1_h2"],
                "body":     pd["cb1_body"],
                "image":    pd["cb1_image"],
                "cta_text": pd["cb1_cta_text"],
                "cta_link": pd["cb1_cta_link"],
            }, title_sfx=menu_label)
            if akut_cb1["block_name"] not in seen:
                seen.add(akut_cb1["block_name"]); variants.append(akut_cb1)

            akut_cb2 = make_variant(bases["content-block-2"], slug, {
                "eyebrow":  pd["cb2_eyebrow"],
                "h2":       pd["cb2_h2"],
                "body":     pd["cb2_body"],
                "image":    pd["cb2_image"],
                "cta_text": pd["cb2_cta_text"],
                "cta_link": pd["cb2_cta_link"],
            }, title_sfx=menu_label)
            if akut_cb2["block_name"] not in seen:
                seen.add(akut_cb2["block_name"]); variants.append(akut_cb2)

            akut_ps = make_variant(bases["process-steps"], slug, {
                "eyebrow":      "Så får du snabb hjälp",
                "heading":      "Tre steg — från första samtal till lindring.",
                "step_1_title": "Ring oss",
                "step_1_desc":  "Berätta vad som hänt. Vi prioriterar akuta besvär och bedömer hur snabbt du behöver komma in.",
                "step_2_title": "Samma dag — oftast",
                "step_2_desc":  "Vi har avsatta tider för akuta patienter, även på kvällar och lördagar.",
                "step_3_title": "Lindring + plan",
                "step_3_desc":  "En noggrann undersökning, smärtlindring direkt — och en tydlig behandlingsplan framåt.",
            }, title_sfx=menu_label)
            if akut_ps["block_name"] not in seen:
                seen.add(akut_ps["block_name"]); variants.append(akut_ps)

            akut_pr = make_variant(bases["price-row"], slug, {
                "eyebrow":     "Pris & ersättning",
                "heading":     "Tydliga priser — utan överraskningar.",
                "intro":       "Vi följer Folktandvårdens prislista och är anslutna till Försäkringskassan. Din tandvårdsersättning dras direkt på fakturan.",
                "row_1_label": "Akut undersökning, ny patient",
                "row_1_price": "440 kr",
                "row_2_label": "Akut undersökning, befintlig patient",
                "row_2_price": "575 kr",
                "row_3_label": "Eventuell behandling",
                "row_3_price": "Folktandvårdens prislista",
                "row_4_label": "Räntefri delbetalning",
                "row_4_price": "Vid större ingrepp",
            }, title_sfx=menu_label)
            if akut_pr["block_name"] not in seen:
                seen.add(akut_pr["block_name"]); variants.append(akut_pr)

            akut_faq = make_variant(bases["faq"], slug, {
                "heading": pd["faq_heading"],
                "q_1": pd["faq_q_1"], "a_1": pd["faq_a_1"],
                "q_2": pd["faq_q_2"], "a_2": pd["faq_a_2"],
                "q_3": pd["faq_q_3"], "a_3": pd["faq_a_3"],
                "q_4": pd["faq_q_4"], "a_4": pd["faq_a_4"],
            }, title_sfx=menu_label)
            if akut_faq["block_name"] not in seen:
                seen.add(akut_faq["block_name"]); variants.append(akut_faq)

            blocks = [
                "lumo/site-header",
                "lumo/emergency-strip",
                hero_v["block_name"],
                "lumo/dental-triage-widget",
                akut_cb1["block_name"],
                akut_ps["block_name"],
                akut_cb2["block_name"],
                akut_pr["block_name"],
                f"lumo/cta-strip-{slug}",
                akut_faq["block_name"],
                "lumo/site-footer",
            ]

        else:
            # ── Bygg info-grid-komponent per behandling (visuell variant per sida)
            bn  = f"lumo/info-grid-{slug}"
            ttl = f"Info-grid – {menu_label}"
            if slug in ("implantat", "tandreglering-stockholm"):
                ig = build_stats_strip(bn, ttl, pd["ig_items"])
            elif slug == "karies-hal-i-tanden":
                ig = build_stages_grid(bn, ttl, pd["ig_eyebrow"], pd["ig_heading"], pd["ig_items"])
            elif slug == "tandblekning":
                ig = build_method_comparison(bn, ttl, pd["ig_eyebrow"], pd["ig_heading"], pd["ig_items"])
            elif slug in ("tandfasader-veneers", "tandsten-tandhygienist"):
                ig = build_use_cases_grid(bn, ttl, pd["ig_eyebrow"], pd["ig_heading"], pd["ig_items"])
            elif slug == "tandvardsradsla":
                ig = build_approach_grid(bn, ttl, pd["ig_eyebrow"], pd["ig_heading"], pd["ig_items"])
            else:
                ig = build_info_grid(bn, ttl, pd["ig_eyebrow"], pd["ig_heading"], pd["ig_items"])
            if ig["block_name"] not in seen:
                seen.add(ig["block_name"])
                variants.append(ig)

            # ── Bygg cb1/cb2-varianter per behandling ────────────────────
            cb1 = make_variant(
                bases["content-block-1"], slug,
                {
                    "image":    pd["cb1_image"],
                    "eyebrow":  pd["cb1_eyebrow"],
                    "h2":       pd["cb1_h2"],
                    "body":     pd["cb1_body"],
                    "cta_text": pd["cb1_cta_text"],
                    "cta_link": pd["cb1_cta_link"],
                },
                title_sfx=menu_label,
            )
            if cb1["block_name"] not in seen:
                seen.add(cb1["block_name"])
                variants.append(cb1)

            cb2 = make_variant(
                bases["content-block-2"], slug,
                {
                    "image":    pd["cb2_image"],
                    "eyebrow":  pd["cb2_eyebrow"],
                    "h2":       pd["cb2_h2"],
                    "body":     pd["cb2_body"],
                    "cta_text": pd["cb2_cta_text"],
                    "cta_link": pd["cb2_cta_link"],
                },
                title_sfx=menu_label,
            )
            if cb2["block_name"] not in seen:
                seen.add(cb2["block_name"])
                variants.append(cb2)

            # ── Bygg faq-variant per behandling ──────────────────────────
            faq_v = make_variant(
                bases["faq"], slug,
                {
                    "heading": pd["faq_heading"],
                    "q_1": pd["faq_q_1"], "a_1": pd["faq_a_1"],
                    "q_2": pd["faq_q_2"], "a_2": pd["faq_a_2"],
                    "q_3": pd["faq_q_3"], "a_3": pd["faq_a_3"],
                    "q_4": pd["faq_q_4"], "a_4": pd["faq_a_4"],
                },
                title_sfx=menu_label,
            )
            if faq_v["block_name"] not in seen:
                seen.add(faq_v["block_name"])
                variants.append(faq_v)

            # ── Bygg blocks-lista ─────────────────────────────────────────
            blocks = [
                "lumo/site-header",
                hero_v["block_name"],
                ig["block_name"],
                cb1["block_name"],
            ]

            # Process-steps (4-steg) för implantat & tandreglering
            needs_process = slug in ("implantat", "tandreglering-stockholm")
            if needs_process:
                ps4 = build_process_steps_4(
                    block_name=f"lumo/process-steps-{slug}",
                    title=f"Behandlingssteg – {menu_label}",
                )
                if ps4["block_name"] not in seen:
                    seen.add(ps4["block_name"])
                    variants.append(ps4)
                blocks.append(ps4["block_name"])
                steps = pd["ps_steps"]
                page_defs[ps4["block_name"]] = {
                    "eyebrow": pd["ps_eyebrow"],
                    "heading": pd["ps_heading"],
                    "step_1_title": steps[0]["title"], "step_1_desc": steps[0]["desc"],
                    "step_2_title": steps[1]["title"], "step_2_desc": steps[1]["desc"],
                    "step_3_title": steps[2]["title"], "step_3_desc": steps[2]["desc"],
                    "step_4_title": steps[3]["title"], "step_4_desc": steps[3]["desc"],
                }

            blocks.append(cb2["block_name"])

            # Pristabell för implantat
            if slug == "implantat":
                pr_rows = pd["pr_rows"]
                page_defs["lumo/price-row"] = {
                    "eyebrow":     pd["pr_eyebrow"],
                    "heading":     pd["pr_heading"],
                    "intro":       pd["pr_intro"],
                    "row_1_label": pr_rows[0]["label"], "row_1_price": pr_rows[0]["price"],
                    "row_2_label": pr_rows[1]["label"], "row_2_price": pr_rows[1]["price"],
                    "row_3_label": pr_rows[2]["label"], "row_3_price": pr_rows[2]["price"],
                    "row_4_label": pr_rows[3]["label"], "row_4_price": pr_rows[3]["price"],
                }
                blocks.append("lumo/price-row")

            blocks += [f"lumo/cta-strip-{slug}", faq_v["block_name"], "lumo/site-footer"]

        active = slug in ACTIVE_TREATMENTS
        p = {
            "title": h1, "slug": slug, "blocks": blocks,
            "menu_label": menu_label if active else None,
            "menu_parent": parent if active else None,
            "status": "publish" if active else "draft",
            "page_defaults": page_defs,
        }
        pages.append(p)

    # ── Barnspecialist (PageHero + FactStrip) ───────────────────────────────
    db = BARNSPECIALIST_DATA
    blocks = [
        "lumo/site-header",
        "lumo/page-hero-barnspecialist",
        "lumo/fact-strip-barnspecialist",
        add("content-block-1", "barnspecialist", {
            "image":    "https://swordfish.templweb.com/wp-content/uploads/2026/05/barn-1.jpg",
            "eyebrow": "Älvsjö Pedodonti",
            "h2":      "Anpassad specialistvård med omtanke.",
            "body":    "<p>Älvsjö Pedodonti är vår specialistklinik för <strong>barn och unga upp till 23 års ålder</strong>. Vi arbetar på uppdrag av Region Stockholm och tar emot remisser via Muntra för att säkerställa expertis och trygg vård för ditt barn.</p><p>För en trygg upplevelse erbjuder vi <strong>lustgas, lugnande medel (Midazolam) och i särskilda fall narkosbehandling</strong>. Tandvård är alltid <strong>gratis för barn och ungdomar upp till 19 år</strong>.</p>",
            "cta_text": "Skicka remiss",
            "cta_link": "/remiss-2",
        }, "Barnspecialist"),
        "lumo/cta-strip-barnspecialist",
        add("faq", "barnspecialist", {
            "heading": "Frågor från föräldrar.",
            "q_1": "Vilka kan få specialisttandvård hos Älvsjö Pedodonti?",
            "a_1": "Älvsjö Pedodonti är en specialistklinik för barn och unga upp till 23 år. Vi tar emot remisser via Muntra och arbetar på uppdrag av Region Stockholm för att erbjuda specialistvård.",
            "q_2": "Vad gör ni om mitt barn är rädd för tandläkaren?",
            "a_2": "Vi möter rädda barn med extra tålamod och anpassad omsorg. Vårt team är specialiserat på psykologisk omvårdnad och erbjuder vid behov lustgas, lugnande medel eller narkos för en trygg upplevelse.",
            "q_3": "Kostar tandvården något för barn?",
            "a_3": "Nej, hos Älvsjö Tandvård är all tandvård alltid gratis för barn och ungdomar upp till 19 år. Det gäller både allmäntandvård och specialisttandvård på remiss.",
        }, "Barnspecialist"),
        add("contact-panel", "barnspecialist", {
            "heading": "Kontakta oss",
            "intro_text": "Har du frågor om barnspecialistvård? Vi hjälper dig gärna.",
        }, "Barnspecialist"),
        "lumo/site-footer",
    ]
    pages.append({"title": "Barnspecialist (Pedodonti) i Älvsjö", "slug": "pedodonti",
                  "menu_label": "Barnspecialist", "blocks": blocks})

    # ── Platshållarsidor (ej byggda än) ─────────────────────────────────────
    placeholder = ["lumo/site-header", "lumo/site-footer"]
    pages.append({"title": "Räntefri delbetalning", "slug": "rantefritt",
                  "menu_label": "Räntefritt", "blocks": placeholder})
    pages.append({"title": "Lista dig hos oss",     "slug": "lista-dig",
                  "menu_label": None,          "blocks": placeholder})
    pages.append({"title": "Kampanjer",             "slug": "kampanjer",
                  "menu_label": "Kampanjer",  "blocks": placeholder})

    # Kontakt sist i menyn
    blocks = [
        "lumo/site-header",
        "lumo/page-hero-kontakt",
        "lumo/cta-strip-kontakt",
        "lumo/contact-grid",
        "lumo/map-hours-kontakt",
        "lumo/contact-form",
        "lumo/site-footer",
    ]
    pages.append({"title": "Kontakt", "slug": "kontakt", "menu_label": "Kontakt", "blocks": blocks})

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
        "hero":             hero,
        "treatment-hero":   build_treatment_hero_shared(),
        "content-block-1":  build_content_block("lumo/content-block-1", "Innehållsblock",          mirror=False, bg="var(--white)"),
        "content-block-2":  build_content_block("lumo/content-block-2", "Innehållsblock (speglat)", mirror=True,  bg="var(--cream)"),
        "contact-panel":    build_contact_panel(),
        "faq":              build_faq(),
        "map-section":      build_map_section(),
        "process-steps":    build_process_steps(),
        "price-row":        build_price_row(),
    }

    # CTA strip per page + akut-specifika sektioner
    treatment_hero_shared = bases["treatment-hero"]
    triage_widget    = build_dental_triage_widget()
    triage_grid      = build_triage_grid()
    emergency_strip  = build_emergency_strip()
    process_steps    = bases["process-steps"]
    price_row        = bases["price-row"]
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

    # All global components. Shared treatment-page templates (content-block-1,
    # content-block-2, faq) are registered here so they exist even though
    # they're used on multiple pages — per-page content comes via page_defaults.
    global_components = [
        site_header, site_footer,
        hero, treatments, reviews, about, emergency, team, photo_tour,
        page_hero_info,
        treatment_hero_shared, emergency_strip, triage_widget, triage_grid, process_steps, price_row,
        bases["content-block-1"], bases["content-block-2"], bases["faq"],
        *cta_strips, *barnspecialist_comps, *kontakt_comps, *om_oss_comps, remiss_comp,
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
            {"label": "Om kliniken",            "url": "/om-oss/",                      "parent": "Om oss"},
            {"label": "Vi som jobbar",          "url": "/om-oss/#team",                 "parent": "Om oss"},
            {"label": "Organisation",           "url": "/om-oss/#organisation",         "parent": "Om oss"},
            {"label": "Hitta till oss",         "url": "/om-oss/#hitta-till-oss",       "parent": "Om oss"},
            {"label": "Arbeta med oss",         "url": "/om-oss/#arbeta-med-oss",       "parent": "Om oss"},
            {"label": "Hjälp oss bli bäst",     "url": "/om-oss/#hjalp-oss-bli-bast",  "parent": "Om oss"},
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
