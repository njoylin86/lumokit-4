# Patricia Teles — Design System

A clean, calming, and highly accessible design system for **Patricia Teles, DDS**, a modern dental clinic. The visual language focuses on **trust, hygiene, and soft geometry** to reduce dental anxiety, paired with a sharper, more contemporary edge than typical clinical sites.

> Live target site: `patriciatelesdds.com`
> Pages planned: Hem · Kontakt · Om oss · Tandimplantat · Invisalign · Akuttandvård · Basundersökning · Allmän tandvård · Tandvårdsrädsla

## Sources & references

- **Brief** — `inspiration/brief.txt` (original notes from client)
- **Visual inspiration** — `inspiration/inspiration.png` (Haga Tandläkeri, https://www.hagatandlakeri.se/) — used for color palette, type styling, margins, and pacing.
- **Direction** — Per client: keep the soft pinks and confident graphite ink, keep the typographic style and breathing room. Push it **sharper and more modern** than the original.

The clinic is positioned in Sweden (operates in Swedish), and the system supports Swedish copy by default.

---

## Index

| File / Folder | Purpose |
|---|---|
| `colors_and_type.css` | All CSS variables: colors, type scale, spacing, radii, shadows, motion, plus base element styles. |
| `fonts/` | Webfonts used (currently loaded via Google Fonts CDN — see Type below). |
| `assets/` | Logos, photography, illustrations, brand visuals. |
| `inspiration/` | Source brief and reference imagery. |
| `preview/` | Cards rendered into the Design System tab. |
| `ui_kits/marketing-site/` | Hi-fi recreation of the Patricia Teles marketing website. |
| `SKILL.md` | Cross-compatible Agent Skill manifest. |

---

## Brand at a glance

- **Name:** Patricia Teles, DDS
- **Voice:** Warm, professional, reassuring. Speaks to anxious patients without being saccharine.
- **Visual:** Soft blush + white surfaces, graphite ink, modern serif headlines, geometric sans body.
- **Mood:** Hygienic, calm, editorial. Less "tech startup," more "modern wellness clinic."

---

## Content fundamentals

### Voice & tone
- **Language:** Swedish first. English is acceptable as secondary, but treat Swedish as canonical (so terms like *Behandlingar*, *Kontakt*, *Boka tid* are first-class).
- **Person:** Uses **"vi"** (we) when speaking as the clinic, **"du"** (you) addressing the patient. Friendly but never overly casual — closer to a thoughtful letter than a chat message.
- **Tone:** Calm, factual, reassuring. The clinic acknowledges that dental anxiety is real (note that *Tandvårdsrädsla* — fear of dentistry — is a primary navigation item). Copy should never minimize or joke about discomfort.
- **Sentence length:** Medium. Never wall-of-text. Short opening sentence, then a clear, slightly longer second line.
- **Imperatives** are gentle: *"Boka tid"* (Book a time), *"Läs mer"* (Read more), *"Skicka in förfrågan"* (Send inquiry) — direct but soft.

### Casing rules
- **Display headings:** Sentence case for serif headlines (`Haga Tandläkeri`, `Digital konsultation`).
- **Section labels (eyebrows):** ALL CAPS, generously letter-spaced — used for the small section markers like `TELEFON & E-POST`, `ÖPPETIDER`, `KONTAKTA OSS`.
- **Buttons:** ALL CAPS, letter-spaced, e.g. `BOKA TID`, `LÄS MER`, `SKICKA`.
- **Body & nav:** Title case for nav items (`Behandlingar`, `Om oss`), normal sentence case for body copy.

### Vibe & signal phrases
- "Varmt välkommen till oss!" — sign-off warmth, unmistakably brand voice.
- "Vi strävar alltid efter naturligt vackra resultat." — confidence + restraint.
- Treatment names are spaced caps inside the visual cards (`ALLMÄN TANDVÅRD`, `INVISALIGN`).

### What to avoid
- ❌ Emoji — never. Not in copy, not in UI.
- ❌ Exclamation overload. One per page max, usually in the closing line.
- ❌ Marketing buzzwords ("revolutionary," "next-gen") — utterly off-brand.
- ❌ Clinical jargon without translation. If you must use a term, briefly explain it.
- ❌ Casual contractions in Swedish. Stay slightly formal.

### Examples
- ✅ *"Vi har ett stort fokus på estetisk tandvård och stor erfarenhet av blekning, ICON-behandling och fasadbyggnad."*
- ✅ *"För oss är varje individ unik. Att lyssna på och se varje person vi möter är därför av största vikt."*
- ❌ *"Get the smile of your dreams!! 😁 Book now!!!"*

---

## Visual foundations

### Colors
The palette is built around a **warm blush** family (the dominant brand color) and a **graphite ink** family for type and primary actions. Pure white provides hygienic separation. Supporting hues (mint, sky, lilac, rose) appear only inside treatment-card photography; they are accent props, not UI tokens.

| Role | Token | Hex | Notes |
|---|---|---|---|
| Page tint | `--blush-50` | `#fdf5f8` | Background wash on hero / form sections |
| Form panel | `--blush-200` | `#f6d7e0` | The pink contact panel |
| Accent rose | `--blush-500` | `#d4889e` | Subtle accents, eyebrow ink |
| Link active | `--blush-600` | `#b56a82` | Hover/active link color |
| Body ink | `--ink-600` | `#323232` | Primary body text |
| Heading ink | `--ink-700` | `#1f1f1f` | Headlines + primary button bg |
| Surface | `--white` | `#ffffff` | Card/panel base |
| Star | `--star` | `#f5c136` | Review stars (sole "vivid" accent) |

Photography rule: warm, soft, never cool/clinical. Skin tones, smiles, neutral interiors, clinical equipment shot at close range with shallow DOF.

### Typography
- **Display & H1/H2 — Cormorant Garamond.** Editorial modern serif. Light/medium weights only. Tight tracking on display sizes.
- **Body, H3/H4, UI, eyebrows — Outfit.** Geometric humanist sans. Friendly without being cute. Use weight 400 for body, 500 for UI, 600 for emphasis.
- **No mono is used in user-facing surfaces** (only for code/devtools).

> ⚠️ **Font substitution flag:** The original Haga Tandläkeri site uses bespoke Wix fonts (likely Avenir Next + a transitional serif). We're substituting **Outfit** and **Cormorant Garamond** from Google Fonts — the closest tonal match available freely. Please supply licensed font files (Avenir Next, Sailec, or similar) if you'd like exact parity.

Eyebrow labels use 11px Outfit 500, uppercase, +0.22em letter-spacing — this is the strongest **typographic signature** of the brand.

### Spacing & rhythm
- 4px base grid, scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128.
- Sections are extremely airy: 96–128px vertical padding between major blocks.
- Content max-width 1180px, prose max-width ~62ch.

### Backgrounds
- Solid washes only — `#ffffff` / `#fdf5f8` / `#f6d7e0`. No gradients in chrome.
- **Photography is always full-bleed** when used as a hero or treatment card. Never floats on a card with shadow.
- Pink "halo" technique: pages alternate white sections with `--blush-50` washed sections. Hero photography slightly overlaps the next color band — the only "layering" the system uses.
- **No textures, no repeating patterns, no illustrations as background.**

### Animation
- Subtle and slow. `--dur-base: 240ms`, easing `cubic-bezier(0.2, 0.7, 0.2, 1)`.
- Default interactions: **fade + 4px translate-y** on enter, simple **opacity** on hover.
- No bounces, no springs, no parallax. The brand is calm — motion follows.

### Hover & press states
- **Links:** color shifts from ink → `--blush-600`; underline color follows.
- **Primary buttons (dark):** bg shifts `--ink-700` → `--ink-900`. No transform.
- **Ghost buttons:** bg fills with `--blush-50`.
- **Cards:** subtle `--shadow-md` lift on hover (desktop only). No scale.
- **Press:** opacity 0.92, no shrink.

### Borders, shadows, elevation
- Borders are **1px solid** in `--border` (`#ececec`) or `--border-soft` (blush). Used sparingly — most separation is via whitespace.
- Shadow scale (`--shadow-xs` → `--shadow-lg`) is **soft and gray**, never tinted. Cards use `--shadow-sm` at rest and `--shadow-md` on hover.
- Inputs use a 1px bottom-border or full 1px border, no inner shadow.

### Corner radii
- **Sharp by default.** The brand uses `--radius-sm` (4px) on cards and inputs — closer to the original Haga site's near-square treatment.
- Buttons: `--radius-sm` rectangles (lifted from the inspiration's hard-edged dark CTA).
- `--radius-pill` reserved for badges and image cards on the treatment grid.
- **No fully circular avatars in chrome.** Use square-with-radius.

### Layout rules
- Single column hero with full-bleed photography.
- Treatment grid: 4-column desktop, 2-column tablet, 1-column mobile. Square 1:1 cards with photo-as-bg + spaced-caps title.
- Forms: stacked single column on small viewports, two-column inputs on desktop.
- Footer is centered, low-key, type-only.
- The header is **fixed/sticky** and uses 100% white — no transparency or blur.

### Transparency & blur
- Almost never. The system relies on solid surfaces for clinical clarity.
- One exception: text on photography uses a 0–20% black scrim if necessary for contrast.

### Imagery vibe
- Warm, soft, often slightly desaturated.
- Close crops of smiles, dental tools shot like still life, calm interior shots.
- People look genuine, not stock-y. Never grinning at camera teeth-out.
- No filters, no grain, no duotone. Color treatments live inside treatment-card backgrounds (mint/sky/lilac), not as effects.

---

## Iconography

The original Haga Tandläkeri site barely uses iconography — that restraint is part of the brand. Patricia Teles will follow suit.

- **Primary icons:** [Lucide](https://lucide.dev) — light, 1.5px stroke, rounded ends. Loaded via CDN: `https://unpkg.com/lucide@latest/dist/umd/lucide.js`.
- **Stroke weight:** 1.5px standard, 1.25px on small (16px) sizes.
- **Use cases:** chevrons, arrows, social icons (Instagram, Facebook), small UI affordances (clock for hours, phone, mail). Never decorative.
- **No icons on buttons** unless paired with `aria-label` only. Buttons are word-led.
- **Logo:** see `assets/logo.svg` — a simple geometric wordmark + monogram mark.
- **Emoji & unicode:** never used as icons in UI or copy. The single allowed exception is the **★** glyph for review stars (rendered in `--star`).

> ⚠️ The original Haga site uses Wix's proprietary icon set. Lucide is our substitute — same hairline stroke quality. If a specific icon is missing, do not improvise an SVG; ask the designer to source one.

---

## Skill manifest

This system also functions as an Agent Skill — see `SKILL.md` for the cross-compatible manifest. When invoked, an agent should read this README first and explore `colors_and_type.css` and `ui_kits/` for component-level reference.
