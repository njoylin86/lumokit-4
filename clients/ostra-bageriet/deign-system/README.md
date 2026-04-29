# Östra Bageriet Design System

A modern, fresh design system for **Östra Bageriet — café, catering & smörgåsar med orientalisk inspiration**, located in the waiting hall of Östra Station in Stockholm.

## What this is

Östra Bageriet is a small, high-energy bakery and café tucked inside a Stockholm commuter station. Their menu is a beautiful collision of two food cultures: classic Swedish bakery and café fare (kanelbullar, frallor, lattes from Löfbergs), and bright Middle-Eastern-inspired cooking (mezé, falafel, halloumi wraps, bulgur and quinoa salads, tarator, vinbladsdolmar). They run a counter for grab-and-go, a small dine-in space, and a catering operation.

This design system gives a designer or AI agent everything needed to produce on-brand interfaces, marketing material, menus, and prototypes for them.

## Brand direction (vs. the old website)

The reference web design we were given (`scraps/webdesign.webp`) leaned on dark backgrounds, cream/peach panels, and an orange CTA. The current logo is brown + gold on cream. **We deliberately moved away from a brown-dominant palette** to feel modern and fresh while staying compatible with the existing logo. The system pairs:

- **Skog** (forest green) — the new primary. Herbal, fresh, food-positive.
- **Saffran** (saffron orange) — the spice accent that bridges Sweden and the Middle East and holds CTA energy.
- **Cream / Paper** — warm flour-dusted neutrals that let the logo's browns and golds sit comfortably without dominating.

The result is closer in feel to a contemporary specialty café (think Bröd & Salt, Fabrique, Levant Beirut) than a traditional konditori.

## Sources

- **Codebase / asset pack**: `ostra-bageriet/` (mounted folder). Contains the logo, the reference web design (`webdesign.webp`), `contact.txt`, `menu_price_list.txt`, and 11 high-quality food/coffee photographs.
- **Reference web design**: `ostra-bageriet/webdesign.webp` — used purely for layout cues (hero pattern, menu grid, testimonial strip, map footer). Colors deliberately diverge per the brief.
- **Menu**: full prices and item descriptions in `ostra-bageriet/menu_price_list.txt`. A formatted copy is reflected in the UI kit.
- **Contact**: Drottning Kristinas väg 1, 114 28 Stockholm (Östra stations vänthall) · 08-612 50 50 · 073-99 38 704 · Fkuorie@hotmail.com.

## Index — what's in this project

| Path | Purpose |
|---|---|
| `README.md` | This file. Brand context, content & visual foundations, iconography. |
| `SKILL.md` | Skill manifest so this folder doubles as a Claude Code skill. |
| `colors_and_type.css` | All design tokens — colors, type, spacing, radii, shadows, typography classes. Import this in every artifact. |
| `assets/logo.png` | The official Östra Bageriet logo (brown/gold roundel). |
| `assets/food/` | Curated, named food + drink photography. |
| `preview/` | Small HTML cards that populate the Design System tab. |
| `ui_kits/website/` | High-fidelity recreation of the marketing website with reusable JSX components. |
| `scraps/` | Raw inputs — the original webdesign reference and the un-renamed photo dump. Kept for traceability; do not link from production artifacts. |

## CONTENT FUNDAMENTALS

**Language.** Swedish first, with Middle-Eastern food terms left in their native form (mezé, halloumi, tarator, kibbe, vinbladsdolmar, labneh). English appears only as a secondary layer for travellers/students. Never translate dish names — "Mezetallrik" stays "Mezetallrik".

**Voice.** Warm, direct, a little proud. We're a small family-run place inside a busy station, not a chain — copy should feel hand-written, not corporate. Short sentences. No exclamation marks unless quoting a customer. The owner's voice is steady and welcoming, never loud.

**Casing.** Sentence case throughout. Headlines like "Färska smörgåsar varje morgon", never "Färska Smörgåsar Varje Morgon". The only ALL CAPS we allow is the eyebrow micro-label (8–12 letters, tracked +0.18em).

**Pronouns.** "Vi" (we) for the bakery, "du" (you) for the customer — never "ni" (formal you). It should read like the person behind the counter is talking to you. Example: *"Vi bakar varje morgon. Kom förbi innan 09 om du vill ha varma frallor."*

**Numbers & prices.** Always with the colon-dash format Swedes expect: `70:-` for ordinary, `60:-` for student. Use tabular numerals (the `.ob-price` class). Never write "70 kr" in product copy — `:-` is the local convention and reinforces neighbourhood feel.

**Tags & labels we use.** "Studentpris", "Vegan", "Glutenfri", "Veg", "Nytt", "Dagens", "Färskt idag", "Catering". All sentence-case except where they're tag-style chips (then small caps via tracking).

**Tone examples.**
- Hero: *"Bakat på morgonen. Serverat hela dagen."*
- Section header: *"Smörgåsar med smak av två hav"* (a deliberate nod to Sweden + the Mediterranean/Levant).
- CTA: *"Beställ catering"*, *"Se dagens meny"*, *"Hitta hit"* — verbs first, always concrete.
- Testimonial framing: *"Stamkunderna säger"* — never "What our customers say".
- Empty state: *"Inget i kassen ännu — börja med en macka."*

**Emoji.** Used sparingly in menu copy as section markers only (🥖 Bröd, 🥗 Sallader, 🌯 Wraps, ☕ Drycker — these come from the original menu source) and never inside body sentences or marketing copy. Treat them like printer's dingbats, not internet exclamations.

**Things we don't do.** Hashtags. Forced positivity ("amazing!", "delicious!"). Marketing-speak ("artisanal", "curated", "elevated"). English idioms in Swedish copy. Generic stock phrases ("freshly baked goodness").

## VISUAL FOUNDATIONS

**Color application.**
- 60% of any surface is a neutral cream (`--ob-bg` or `--ob-paper`).
- 30% is reserved for photography (food images do most of the colour work).
- ~10% is brand pigment: Skog green for primary actions and section accents, Saffran for highlight tags / hero CTA / handwritten flourishes.
- Brown/wheat from the logo are reserved for the logo itself and rare wood-grain or kraft accents — never page backgrounds.
- Pomegranate red (`--ob-granat`) is used at most once per screen, as a "Nytt" or limited-time marker.

**Typography.**
- **Playfair Display** for display + headlines. Echoes the curvy serif of the logo's "Bageriet" wordmark. Weights 600/700, slight negative tracking, line-height 1.0–1.1.
- **DM Sans** for everything else — body, UI, prices, navigation. Geometric but warm.
- **Caveat** strictly for handwritten flourishes: "Färskt idag", "Studentpris", a chef's signature on the about page. No more than one Caveat element per viewport.
- Tabular numerals on every price and quantity (`font-variant-numeric: tabular-nums lining-nums`).

**Spacing.** 4px base scale. Cards use 24/32px internal padding. Section vertical rhythm is 96px desktop / 56px mobile. Don't crowd.

**Backgrounds.**
- Default: solid cream `--ob-bg`.
- Section breaks: alternate `--ob-bg-alt` (toasted cream) — never an image.
- Hero / "the dark slab": `--ob-stone-900` with full-bleed food photo at ~85% opacity, no overlay gradient. Imagery is the protagonist.
- Subtle paper texture is allowed (8–12% opacity grain), never colour gradients on backgrounds.

**Imagery vibe.** Warm, slightly moody, low-key key light, wooden boards or charcoal stoneware. Pomegranate reds and citrus yellows pop against the dark surfaces. Always real food, never illustrations of food. We do **not** use cool/blue food photography or bright flat-lit Instagram styling.

**Borders & dividers.** 1px hairlines in `--ob-border` (warm stone, not grey). For emphasis use 2px in `--ob-skog-300`. Never dotted, never coloured drop shadows around buttons.

**Corner radii.** Three sizes do 95% of the work: 8px for chips/inputs, 14px for cards, 22px for hero blocks and image frames. Pills (999px) for filter tags only. No mixing 4px and 24px in the same composition.

**Cards.** Cream `--ob-paper` surface, 14px radius, `--ob-shadow-2`, 1px `--ob-border`. Hover lifts to `--ob-shadow-3` and translates Y -2px. No coloured borders, no gradient borders.

**Shadows.** Three-tier system in `colors_and_type.css`. All shadows are warm-tinted (rgba of `--ob-ink`, not pure black). The `--ob-shadow-warm` is reserved for the saffran CTA.

**Animation.**
- Default ease: `cubic-bezier(0.32, 0.72, 0, 1)` (a soft custom ease, slightly past-the-end).
- Default duration: 200ms for hover, 320ms for layout shifts, 600ms for entrance.
- Page sections fade + translate Y(12px) into view, never slide from the side.
- No bouncy springs, no parallax, no auto-playing carousels. The dough rises slowly.

**Hover states.** Buttons and links shift 4–6% darker (use `--ob-primary-hover`). Cards lift via shadow upgrade + 2px translate. Image cards crossfade into a 1.03x zoom over 600ms — the only place we scale images.

**Press states.** 1px translate-Y down, shadow drops one tier. No colour change beyond that.

**Focus.** `--ob-ring-focus` (3px Skog 28% alpha ring) on all interactive elements. Never remove the outline.

**Transparency & blur.** Reserved for the sticky top nav (cream at 80% with 12px backdrop-blur on scroll). We do not use frosted glass anywhere else.

**Layout rules.**
- Max content width 1200px on the marketing site.
- Grid is 12-col with 24px gutters desktop, 4-col on mobile.
- The logo lives top-left, never centre-aligned in hero.
- Sticky elements: only the primary nav. No sticky CTAs, no chat bubbles.
- Photos are framed with 22px radius and a 2% inner shadow to seat them into the cream — never a hard rectangle on cream.

**Buttons.**
- Primary: Skog green fill, cream text, 14px radius.
- Accent: Saffran fill, white text, used only for the single hero CTA per screen.
- Ghost: transparent, Skog 1.5px outline, Skog text.
- Hand: text-only with a Caveat micro-label above ("Stamkunder beställer →") — used sparingly.

## ICONOGRAPHY

Östra Bageriet's source assets contain **no icon system** — there are no SVGs, no icon font, no Lucide/Heroicons references in their material. The only original brand glyphs are the wheat ear and steaming coffee cup that live inside the logo itself.

For UI work we substitute **[Lucide Icons](https://lucide.dev)** via CDN (`https://unpkg.com/lucide@latest`). Lucide's stroke-based, slightly soft style sits well next to the Playfair display type and the warm cream surfaces.

Rules for using Lucide here:
- Stroke width: **1.75** by default (slightly heavier than Lucide default 2 reads better on cream).
- Size: 18px in body copy, 20px in nav, 24px in feature blocks, 32px in empty states.
- Color: inherit `currentColor` so icons follow text color. Never coloured icons except Saffran on the hero CTA.
- Never fill — always stroke. The brand has no filled icons.

When a category in the menu needs an icon (Bröd, Sallader, Wraps, Drycker, Bakverk), prefer the **emoji from the source menu** (🥖🥗🌯☕🧁) at the section-divider scale (32px+) — they came from the menu copy itself and feel handwritten. **Never** use emoji inside body text or buttons.

If a custom glyph is ever needed (a wheat-ear divider, a steaming-cup bullet) it should be a single-stroke SVG drawn in `--ob-skog-500` at 1.75 stroke, matching Lucide's silhouette. We have not pre-drawn any.

> **Substitution flag:** We are using Lucide as a substitute icon set because the brand has no native icon system. Once Östra picks a direction (or commissions a custom set) this should be revisited.

> **Font flag:** We are using **Playfair Display, DM Sans, and Caveat from Google Fonts** as substitutes — the brand has no specified type system. The wordmark in the logo is bespoke. Once a real type system is chosen these can be swapped.
