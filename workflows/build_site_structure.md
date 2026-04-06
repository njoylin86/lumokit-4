# LumoKit Build Site Structure — SOP
**Workflow:** Brief → Site Spec → Pages + Menu  
**Framework:** WAT (Workflows · Agents · Tools)  
**Status:** Active rulebook — used for every new client build

---

## Purpose

This SOP defines the exact sequence the Agent follows to transform a client brief
into a live WordPress site. It begins where `design_engine_prd.md` ends.

Do NOT skip steps. Do NOT proceed to the next step until the current step is complete.

---

## Standard Site Architecture

Every LumoKit site is built on four standard page templates. These are the default
unless the user explicitly requests something different.

| Page | Swedish (default) | English | Slug (sv) | Slug (en) |
|------|-------------------|---------|-----------|-----------|
| Home | Hem | Home | `hem` | `home` |
| About Us | Om oss | About Us | `om-oss` | `about-us` |
| [Offering]* | — | — | `[slug]` | `[slug]` |
| Contact | Kontakt | Contact Us | `kontakt` | `contact` |

**\* "Offering" is a repeatable page template, not a fixed page.** There is one
page per service/treatment/product the client offers. All use the same layout.
There is no separate "services overview" page — the offerings are listed directly
in the menu (or as a dropdown).

The template's label and slug adapt to the client's industry via `site.services_label`:

| Industry | Label (sv) | Label (en) | Slug example |
|----------|-----------|------------|--------------|
| Digital agency | Tjänster | Services | `seo`, `google-ads` |
| Spa / beauty | Behandlingar | Treatments | `ansiktsbehandling`, `massage` |
| Consultant | Lösningar | Solutions | `strategi`, `implementering` |
| Restaurant | Rätter | Dishes | `lunch`, `a-la-carte` |
| Law firm | Områden | Practice Areas | `arbetsratt`, `avtal` |
| Clinic | Behandlingar | Treatments | `tandblekning`, `implantat` |

If `site.services_label` is not set in the brief, derive it from the client's
industry. When in doubt, ask: *"Vad ska tjänstesidorna heta — Tjänster,
Behandlingar, eller något annat?"*

**Menu hierarchy:** Offering pages appear as a dropdown under a parent menu item
labeled with `site.services_label`. Set `menu_parent` on each offering page in
the brief to trigger this:

```json
{ "title": "SEO", "slug": "tjanster/seo", "menu_label": "SEO", "menu_parent": "Tjänster", ... }
```

The plugin creates the parent item (a `#` custom link) automatically on first
encounter. No extra configuration needed. The resulting menu looks like:

```
Start  |  Om oss  |  Tjänster ▾  |  Kontakt
                      ├ Google Ads
                      ├ SEO
                      └ Webbdesign
```

**Language rule:** Swedish is the default. Use English titles/slugs only when
`site.language` is `"en"` in the brief, or the user explicitly requests it.

### Standard blocks per page type

```
Home
  lumo/hero-section          ← always first
  lumo/services-row          ← overview of top 3 services
  [optional extra sections]  ← stats, content+image, cards, etc.
  lumo/contact-form          ← always last

About Us (Om oss)
  lumo/hero-section          ← page hero (simpler headline)
  lumo/expertise-section     ← company story / values
  [optional: lumo/stats-focus, lumo/two-column-cards]
  lumo/contact-form          ← CTA to get in touch

Services overview (Tjänster)
  lumo/hero-section          ← services overview headline
  lumo/services-grid         ← all services listed
  lumo/contact-form          ← CTA

Services sub-page (per service)
  lumo/hero-section          ← service-specific headline with 4 USP punchlines (see standard below)
  lumo/content-image         ← service description + image
  lumo/contact-form          ← CTA

Contact (Kontakt)
  lumo/contact-form          ← primary content
```

These are defaults — adjust based on client's `content_hints`.

### Standard: Treatment page hero (USP punchlines)

Every treatment/service sub-page hero **must** include 4 short USP punchlines between
the headline and the CTA buttons. This is a system-wide standard — not optional.

Visual structure:
```
[Eyebrow label]
[Headline]

✓ Punchline 1
✓ Punchline 2
✓ Punchline 3
✓ Punchline 4

[ Primary CTA ]   [ Secondary CTA ]
```

ACF schema fields for the treatment hero component:
```json
{ "name": "eyebrow",     "type": "text", "label": "Etikett",    "default": "[Client name]" },
{ "name": "headline",    "type": "text", "label": "Rubrik",     "default": "[Treatment name]" },
{ "name": "punchline_1", "type": "text", "label": "USP 1",      "default": "..." },
{ "name": "punchline_2", "type": "text", "label": "USP 2",      "default": "..." },
{ "name": "punchline_3", "type": "text", "label": "USP 3",      "default": "..." },
{ "name": "punchline_4", "type": "text", "label": "USP 4",      "default": "..." },
{ "name": "cta_text",    "type": "text", "label": "Knapptext 1","default": "Boka tid" },
{ "name": "cta_link",    "type": "url",  "label": "Knapplänk 1","default": "#" },
{ "name": "cta_2_text",  "type": "text", "label": "Knapptext 2","default": "Ring oss" },
{ "name": "cta_2_link",  "type": "url",  "label": "Knapplänk 2","default": "#" }
```

USP defaults must be treatment-specific — derived from the client brief or content hints,
never generic ("Lorem ipsum"). Use a `check_circle` Material Symbol icon before each punchline.

**Booking CTA link:** Always use `{{site_booking_cta_link}}` (never a hardcoded `#`) for all
"Boka"-buttons on treatment pages. For Boxmedia clients this resolves to `#tdl-booking-widget`
automatically. For other clients it resolves to `#` unless overridden.

---

## Platform-Specific Integrations

Some integrations are only active when a client uses a specific booking/CRM platform.
Set `"platform"` in the brief to enable them. Leave it out (or `null`) for standard builds.

### Boxmedia (`"platform": "boxmedia"`)

Boxmedia is a dental booking platform. When a client uses Boxmedia:

**What the agent must do:**

- Use `{{site_booking_cta_link}}` on ALL "Boka"-buttons across all components — never hardcode `#` or a URL for booking CTAs

- **Treatment pages (behandlingssidor):** Hero MUST include 4 USP punchlines + 2 CTA buttons (see treatment hero standard above). Use `{{site_booking_cta_link}}` for the primary CTA.

- **All other pages (Hem, Om oss, Kontakt, etc.):** Hero must NOT include punchlines. Simpler hero: eyebrow + headline + (optional) subheadline + single CTA if relevant.

**What the plugin does automatically:**
- `{{site_booking_cta_link}}` resolves to `#tdl-booking-widget` on every page
- Trustindex review widget script is injected globally (set the embed code in WP Admin → LumoKit → Inställningar)
- Boxmedia booking widget div (`id="tdl-booking-widget"`) is injected on all pages before the footer
  (set the widget ID in WP Admin → LumoKit → Inställningar)

**Brief field:**
```json
"platform": "boxmedia"
```

**Bundle field (set by the agent, invisible to the client):**
```json
"platform_config": {
  "platform": "boxmedia",
  "trustindex_script": "<script src='...'></script>",
  "booking_widget_id": "abc123xyz"
}
```

`platform_config` is pushed to `/wp-json/lumokit/v1/settings` before components are built.
It is stored as hidden WP options — never visible in WP Admin. The client sees no trace of it.

No per-page configuration needed. All buttons and widgets update site-wide.

---

## Testing a New Client

Each client gets their own WordPress installation in production. During development,
reset the shared test WP to a clean state before each new client build:

1. Restore the clean WP backup (via WP Admin → Backup plugin, or server snapshot)
2. **Do not regenerate Application Password** — the backup preserves the same user
   and credentials, so `.env` stays valid
3. Verify the LumoKit Bridge plugin is active (WP Admin → Plugins)
4. Proceed to Step 0

Skipping the restore means components from a previous client will persist and
collide with the new client's blocks (same `block_name` = last push wins).

---

## Prerequisites

Before starting, verify:
- [ ] `.env` file exists with `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- [ ] A client brief exists at `.tmp/[client_slug]_brief.json`  
      OR the user has described the client verbally → run Step 0 first

---

## Step 0: Create or Validate the Client Brief

**Trigger:** Run this step only if no `_brief.json` exists yet.

Ask the user for (or derive from context):
1. Business name, slug, domain, industry, tagline
2. Brand colors (primary, secondary, background, text, accent)
3. Fonts (heading, body) — default to `Inter` if unknown
4. Site language: Swedish (`sv`) or English (`en`) — default is `sv`
5. Which services the client offers (names of service sub-pages)
6. Any pages beyond the standard four (Home / About / Services / Contact)
7. Header: logo text/image, nav position
8. Footer: copyright text, footer links
9. Design reference screenshots (optional)

**Pre-populate pages from the standard architecture** (see above). Only ask the user
about pages that deviate from the standard set. Do not ask the user to list
"Hem, Om oss, Tjänster, Kontakt" — those are implied.

Save as `.tmp/[client_slug]_brief.json` using the schema in the **Appendix** below.

**Validation rules:**
- `client.slug` must be lowercase, no spaces, hyphens allowed (`new-client` not `NewClient`)
- Every page must have at least `title`, `slug`, `menu_label`, and one `content_hint`
- `brand.primary_color` must be a valid hex value

---

## Step 1: Analysera referensbilder

**Trigger:** Körs alltid om `design_references` finns i briefen. Hoppa ALDRIG över detta steg.

**Färskt perspektiv — KRITISKT:** Varje klientprojekt analyseras som om det vore det första
någonsin. Ignorera hur tidigare klienter såg ut. Ignorera komponenter som byggts för andra
klienter. Basera ALL design enbart på de referensbilder som hör till denna klient.

Om globala instruktioner finns i `workflows/global_defaults.md` — läs dem först.
De sätter tekniska grundregler (t.ex. inline styles, font-regler) men styr ALDRIG
det visuella utfallet. Det gör enbart referensbilderna.

1. Läs varje fil listad under `design_references` med `Read`-verktyget
2. Redovisa analysen i chatten för varje bild enligt detta format:

```
### [description från design_references] — Bildanalys

Layout:           [kolumner, riktning, proportioner t.ex. "2 kol 40/60, text vänster bild höger"]
Bakgrund:         [hex per sektion, t.ex. "#ffffff hero, #f5f0e8 content, #1a1a1a footer"]
Färgpalett:       [ALLA färger: primär, sekundär, accent, kantfärger, muted text, hover]
Font rubrik:      [familj + stil, t.ex. "serif, troligtvis Playfair Display, bold"]
Font brödtext:    [familj + stil, t.ex. "sans-serif, troligtvis Inter, regular"]
Rubrik:           [storlek, vikt, färg, versaler?, line-height]
Brödtext:         [storlek, färg, line-height]
Letter-spacing:   [finns det spärrad text? var? t.ex. "eyebrow-labels: 0.12em uppercase"]
Knappar:          [fylld/outline, bakgrundsfärg, textfärg, border-radius, text-transform, padding]
Border-radius:    [kort, bilder, inputs: skarp/subtil/rund/pill — ange px-uppskattning]
Sektionsövergång: [skarp kant / skugga / diagonal / ingen separation]
Bildbehandling:   [aspect-ratio, rundade hörn?, gradient-overlay?, opacity?]
Länkstilar:       [understrukna?, färg, font-weight]
Formulär:         [inputfältens bakgrund, kantfärg, radius, label-stil]
Spacing:          [vertikal padding per sektion, gap mellan element]
Övrigt:           [ikoner stil, dividers, dekorativa element, animationer]
```

**Font-identifiering:**
1. Försök identifiera fonten ur bilden. Titta på seriffer, geometri, proportioner.
2. Om du kan identifiera den med rimlig säkerhet → använd den.
3. Om du INTE kan identifiera den → gissa INTE Inter som default. Analysera istället
   designens stil och välj en Google Font som passar:

| Designstil | Rubrikfont | Brödtextfont |
|---|---|---|
| Modern, klinisk, professionell | DM Sans | DM Sans |
| Varm, lokal, tillgänglig | Nunito | Inter |
| Elegant, premium, lyx | Playfair Display | Inter |
| Editorial, journalistisk | Merriweather | Inter |
| Teknisk, startup, digital | Space Grotesk | Inter |
| Klassisk, trygg, traditionell | Lora | Source Sans 3 |

Motivera ditt val i analysen: "Kan inte identifiera exakt font. Designen är varm och
lokal → väljer Nunito för rubriker, Inter för brödtext."

3. Lista vilka **sektioner/block** som finns i varje sida, uppifrån och ned
4. Fortsätt INTE till Step 2 förrän analysen är redovisad

---

## Step 2: Granska befintliga komponenter

Read `existing_components` from the brief. For each page's `content_hints`, decide:

| Status | Meaning | Action |
|--------|---------|--------|
| **REUSE** | An existing component covers this layout exactly | List the block name |
| **ADAPT** | An existing component fits but defaults need changing | Note the block + what to update |
| **NEW** | No existing component matches | Must create in Step 2 |

Build a component map table before proceeding:

```
Page: Hem
  "Hero with headline + CTA"  → REUSE lumo/hero-section
  "Three services overview"   → REUSE lumo/services-row
  "Contact form"              → REUSE lumo/contact-form
```

**Rule:** Always prefer REUSE over NEW. Only create new components when the layout
or structure genuinely differs from all existing components. Three similar columns of
services = REUSE, not NEW.

---

## Step 2: Design New Components (if any)

For each content hint marked **NEW**:

1. Follow `workflows/design_engine_prd.md` completely — all phases.
2. Save each component to `.tmp/[client_slug]_[component_name].json`
3. Push: `python3 tools/push_to_wp.py .tmp/[client_slug]_[component].json`
4. After all NEW components are pushed, compile Tailwind: `python3 tools/compile_tailwind.py`

**Do not proceed to Step 3 until all NEW components are pushed with `[OK]` output.**

For **ADAPT** components: no new file is needed. The client fills in correct content
via ACF admin after the pages are created. Schema defaults will show as placeholders.

---

## Step 3: Generate the Bundle

Generate a single `.tmp/[client_slug]_bundle.json` that contains both the components
and the page spec. This is the primary output format — one file per client build.

```json
{
  "site_name": "<client.name from brief>",
  "components": [
    {
      "block_name": "lumo/block-name",
      "title": "Block Title",
      "html_template": "<section>...</section>",
      "schema": [
        { "name": "field", "type": "text", "label": "Label", "default": "..." }
      ]
    }
  ],
  "pages": [
    {
      "title": "<page.title>",
      "slug": "<page.slug>",
      "menu_label": "<page.menu_label or null>",
      "blocks": ["lumo/block-name"]
    }
  ]
}
```

**Rules:**
- `components` contains only NEW components from Step 2. REUSE/ADAPT blocks are
  already registered in WP — do not re-include them.
- `lumo/site-header` and `lumo/site-footer` are injected globally — **never** add
  them to `pages[].blocks`.
- Order blocks by visual position: hero/banner first, contact/CTA last.
- If there are no new components, `components` can be an empty array `[]`.

---

## Step 4: Execute the Build

```bash
python3 tools/build_all.py .tmp/[client_slug]_bundle.json
```

The tool pushes all components first, then builds all pages and the menu in one run.
Verify each page returns `[OK]` and a `page_url`.

**If a component push fails:** Fix the component in the bundle and re-run.  
**If you get `blocks_not_found`:** The block is listed in `pages` but missing from
`components` and not registered in WP — add it to `components` or push it separately
with `push_to_wp.py`.

**To update a single component later** (without rebuilding the whole site):
```bash
python3 tools/push_to_wp.py .tmp/[client_slug]_[component].json
```

---

## Step 5: Verify and Report

1. Open each `page_url` from the tool output and confirm the page renders
2. Confirm the nav menu is visible and all links work
3. Report to the user:
   - Live page URLs
   - Components that are NEW (client needs to fill content via ACF)
   - Components that are REUSE/ADAPT (schema defaults already populated)
   - WP Admin link for content editing

---

## Step 6: Save the Brief as Handoff Artefact

The `.tmp/[client_slug]_brief.json` is the permanent record for this client.
Do not delete it. It is the source of truth if the client requests changes later.

If the brief was created verbally in Step 0, confirm accuracy with the user before closing.

---

## Quick Reference Flowchart

```
Client brief (.tmp/[slug]_brief.json)
          ↓
Step 1 — Läs referensbilder → redovisa bildanalys i chatten  ← HÅRT GATE
          ↓
Step 2 — Granska befintliga komponenter → REUSE / ADAPT / NEW map
          ↓
Step 3 — Designa NEW komponenter (→ design_engine_prd.md)
          ↓
Step 4 — Generera .tmp/[slug]_bundle.json  (komponenter + sidor i en fil)
          ↓
Step 5 — python3 tools/build_all.py .tmp/[slug]_bundle.json
          ↓
Step 6 — Verifiera sidor + rapportera till användaren
          ↓
Step 7 — Brief sparad som handoff-artefakt
```

---

## File Naming Convention

| File | Pattern | Example |
|------|---------|---------|
| Client brief | `.tmp/[slug]_brief.json` | `.tmp/boxmedia_brief.json` |
| Bundle (primary) | `.tmp/[slug]_bundle.json` | `.tmp/boxmedia_bundle.json` |
| Single component | `.tmp/[slug]_[component].json` | `.tmp/boxmedia_hero.json` |
| Screenshot | `.tmp/[slug]*.png` | `.tmp/boxmedia.se_.png` |

`[slug]` is always `client.slug` from the brief — lowercase, hyphens for multi-word names.

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `blocks_not_found` | Block listed in site spec but not registered in WP | Push component via `push_to_wp.py`, then re-run `build_site.py` |
| `missing_field: site_name` | Site spec malformed | Verify `_site.json` has `site_name` and `pages` keys |
| HTTP 401 | WP credentials wrong or expired | Check `.env`, regenerate Application Password in WP admin |
| `[ERROR] File not found` | Wrong path passed to tool | Check `.tmp/` path is exact, including the `_site` suffix |
| `missing_field: title` | Page spec missing required fields | Each page needs `title` and `blocks` at minimum |

---

## Appendix: Brief Schema

See `.tmp/boxmedia_brief.json` as the living reference example.

Key fields the Agent must populate for the site spec to be correct:

| Brief field | Maps to | Notes |
|-------------|---------|-------|
| `client.name` | `site_name` in site spec | Displayed name |
| `client.slug` | File prefix for all `.tmp/` files | URL-safe, lowercase |
| `pages[].title` | `pages[].title` in site spec | Copied directly |
| `pages[].slug` | `pages[].slug` in site spec | Copied directly |
| `pages[].menu_label` | `pages[].menu_label` in site spec | Copied directly |
| `pages[].content_hints` | Interpreted in Step 1 | Free-form prose → component map |
| `existing_components` | Reuse list checked in Step 1 | Keep up to date as new components are built |

**Forward-compatible fields** (stored in brief, ignored by current tools, used by future tools):
- `pages[].seo` — meta title, description, focus keyword
- `_extensions.contact_form_handler` — form submission endpoint
- `_extensions.languages` — multi-language config
- `_extensions.custom_post_types` — CPT definitions
- `_extensions.analytics` — GTM/GA config

*Update this SOP when new tools or block types are added to LumoKit.*
