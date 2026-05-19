# Agent Instructions: LumoKit Project

You are operating within the **LumoKit** project, an automated, AI-driven factory for generating high-performance WordPress websites. 

## The LumoKit Architecture ("Spår 3")
We use a "Data-Driven Component Engine" to balance creative freedom with strict content management. 
- **Separation of Concerns:** Design/Structure is decoupled from Content.
- **The Flow:** You (the AI) design components locally. You generate a JSON payload containing `html_template` (Tailwind + mustache syntax like `{{title}}`) and an ACF `schema`. 
- **The Execution:** Python scripts push this JSON to a custom WordPress plugin ("LumoKit Bridge"). The plugin dynamically registers ACF fields and a Gutenberg block. The client edits content via ACF; the site renders raw, blazing-fast HTML without heavy page builders.

## The WAT Framework (Workflows, Agents, Tools)
You operate strictly within the WAT framework. Probabilistic AI (you) handles reasoning and design. Deterministic code (tools) handles execution.

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/` (or referenced below in this document).
- Read these to understand exactly how to design a component, what Tailwind classes are allowed, and how the ACF schemas should be formatted.
- `workflows/new_client.md` — **End-to-end SOP för ny klient.** Från avtals-signering till lansering + klient-överlämning. 8 faser. Använd som master-flöde — pekar till alla relevanta memory-regler per steg.
- `workflows/build_site_structure.md` — Detaljerad design-fas (brief → komponent-audit → page-spec → `build_site.py`). Använd som komplement till `new_client.md`.
- `workflows/design_engine_prd.md` — Komponent-design från screenshots. Sub-step när nya komponenter behövs.

**Layer 2: Agents (The Decision-Maker - YOU)**
- Read the client brief and the relevant workflows.
- Make creative decisions (e.g., generating Tailwind layouts).
- Generate the JSON structure. 
- You do NOT push to WordPress directly. You call the tools to do it.

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the heavy lifting.
- `tools/compile_tailwind.py`: Compiles the JIT Tailwind CSS locally.
- `tools/push_to_wp.py`: Handles authentication and safely pushes JSON payloads to the WordPress REST API.
- `tools/pull_from_wp.py`: Fetches the current state of a component.

## KRITISK REGEL — Komponentdesign från referensbilder

**Skriv ALDRIG HTML för en komponent utan att först ha läst referensbilden och redovisat analysen i chatten.**

Flödet är alltid:
1. Läs referensbilden med `Read`-verktyget
2. Skriv ut bildanalysen i chatten (layout, färger, typografi, spacing per sektion)
3. Vänta — användaren ska kunna se analysen innan HTML genereras
4. Skriv HTML först efter att analysen är redovisad

Om ingen referensbild finns — fråga användaren innan du fortsätter.
Att gissa eller skriva "generiska" komponenter utan bildanalys är **alltid fel**.

---

## Core Rules of Operation

**1. The "Pull Before Push" Rule (CRITICAL)**
Never overwrite a component on WordPress without pulling its current state first. The client might have local changes or specific content in the database. Always use `tools/pull_from_wp.py` before modifying an existing structure.

**2. Local Tailwind Compilation**
WordPress does not compile Tailwind. If you add new utility classes to an `html_template`, you must instruct the system to run `tools/compile_tailwind.py` to generate the updated `style.css` before pushing to the server.

**3. Sanitize and Secure**
When generating `html_template` strings, never include `<script>`, `<iframe>`, or potentially malicious injection vectors. Keep it strictly to semantic HTML5 and Tailwind CSS.

**4. Check Tools First**
Before writing new scripts, check `tools/` to see if a utility already exists for your task.

## The Self-Improvement Loop
When a tool fails or the WP REST API returns an error (e.g., a 400 Bad Request due to an unsupported ACF field type):
1. Read the error trace carefully.
2. Fix the payload or the Python tool.
3. Verify the fix works.
4. Document the constraint so you don't make the same mistake twice.

## File Structure
```text
clients/<name>/         # All client-specific data lives here
clients/<name>/.tmp/    # Per-client scratch dir — HTML mockups, screenshots, compiled CSS, pulled components
clients/<name>/bundle.json        # Generated bundle (not committed)
clients/<name>/content/           # Source content (committed)
clients/<name>/design-system/     # Design tokens, assets (committed)
tools/                  # Python scripts for deterministic execution (API pushes, Tailwind JIT)
workflows/              # Markdown SOPs defining design rules and ACF mapping logic
wp-plugin/              # PHP code for the "LumoKit Bridge" installed on the WordPress host
.env                    # API keys and WP credentials (NEVER store secrets in code)
```

## .tmp/ Livscykel — KRITISK REGEL
Varje klient har sin **egna** `.tmp/`-mapp under `clients/<name>/.tmp/`. Klienters scratch-data blandas aldrig.

- **Standard sökväg:** `clients/<klientnamn>/.tmp/`
- **Bundle:** `clients/<klientnamn>/bundle.json`
- **Kompilering:** `python3 tools/build_all.py clients/<klient>/bundle.json` — scratch skrivs automatiskt till `clients/<klient>/.tmp/`
- **`compile_tailwind.py` utan argument** är VARNING-läge — använd aldrig i produktion
- **Root `.tmp/`** är legacy — använd inte för nya klientbuilds

## Push-protokoll — KRITISK REGEL (gäller alla klienter)
**Live WP är auktoritär. Källkoden får aldrig skriva över live utan explicit intention.**

Bakgrund: 2026-05-18 skrev en oavsiktlig full-bundle-push över 16+ direkt-patchade komponenter på alvsjotandvard. Räddades med backup-restore. Skydden nedan är obligatoriska i ALLA klient-pushar.

**Claude pushar — inte användaren.** Följande gäller mig i varje session:

1. **Alltid `--only <namn>` vid push.** Aldrig bred deploy.
   ```bash
   python3 tools/build_all.py clients/<klient>/bundle.json --production --only lumo/hero
   ```
2. **Alltid `--dry-run` först på produktion.** Visa output, vänta på OK från användaren, sen kör skarpt.
3. **Efter backup-restore eller manuell WP-ändring** → kör `snapshot_live.py` FÖRST:
   ```bash
   python3 tools/snapshot_live.py --client <klient> --production
   ```
4. **Aldrig `--force-overwrite-drift` eller `--skip-drift-check`** utan att användaren explicit godkänt det efter att ha sett drift-rapporten.
5. **Om drift-check aborterar** → fråga användaren vad som ska göras. Anta aldrig att forcering är säkert.

**Pull före patch:** Innan du editar en komponent vars source kan vara stale: kör `tools/pull_from_wp.py lumo/<komp> --save --client <klient>` och baka in resultatet i source. Annars riskerar du att pusha en stale version.

**`push_to_wp.py` varnar** om payload skiljer från `bundle.json` — det betyder att din patch kommer skrivas över nästa gång bundle pushas. Lyft in patchen i source eller använd `build_all.py --only` istället.

Verktygskedja för nya klienter:
- `tools/snapshot_live.py` — etablera baseline (kör efter restore)
- `tools/build_all.py --only ... --dry-run` — test
- `tools/build_all.py --only ...` — skarpt
- `clients/<klient>/.last_pushed_components.json` — auto-uppdaterad 3-way baseline

## Innehållsändringar — KRITISK REGEL (admin-editing får ALDRIG brytas)

När du ändrar **innehåll** på en komponent (text, bild, länkar, URL:er), MÅSTE du göra det så att klientens redigerings-möjlighet i WP-admin förblir intakt.

**Tre-lager-systemet (alla tre behövs):**

| Lager | Vad uppdateras | Verktyg |
|---|---|---|
| 1. Bridge schema | Fält-definitioner + defaults | `build_all.py --only <block>` |
| 2. **Page ACF-data** | Det som faktiskt renderas på existerande sidor | **`tools/sync_block_acf.py`** |
| 3. Page post_content | Sidans block-struktur | `--overwrite-content --keep-pages` (bredd-verktyg) |

**Varför lager 2 alltid behövs:** Bridge bakar schema-defaults in i blockets `data`-attribut vid sid-skapande (`lumokit_build_page`). Vid render läses ALLTID från denna baked-data — det finns INGEN fallback till schema-default vid render. Så en uppdaterad schema-default påverkar bara nyskapade sidor, inte existerande.

**Workflow vid bild-byte (eller annan content-ändring):**

```bash
# 1. Ladda upp eventuell ny asset (skip om bara textändring)
python3 tools/upload_media.py --dir <single-file-folder> --production

# 2. Uppdatera source + override
#    - clients/<klient>/build_bundle.py
#    - clients/<klient>/.live_overrides/<block>.json (schema default)

# 3. Pusha komponent (schema)
python3 tools/build_all.py clients/<klient>/bundle.json --production --only <block> --dry-run
python3 tools/build_all.py clients/<klient>/bundle.json --production --only <block>

# 4. Synka ACF-data på existerande sidor (utan att röra annat)
python3 tools/sync_block_acf.py --client <klient> --block <block> --page <slug> --field <name> --production --dry-run
python3 tools/sync_block_acf.py --client <klient> --block <block> --page <slug> --field <name> --production
```

**FÖRBJUDET:**
- ❌ Hårdkoda en URL/text direkt i `html_template` om motsvarande schema-fält finns. Det bryter Gutenberg-blocket i admin (svart ruta) och disconnect:ar ACF-fältet.
- ❌ Hoppa över lager 2 — då uppdateras inte sidor som redan har blocket instanstierat.
- ❌ Använda `--overwrite-content` utan `--keep-pages` för punkt-ändringar — det skriver över för bred yta.

**Undantag — statiska assets:** Medaljer, badges, logos som ALDRIG ska kunna ändras av klienten — hårdkoda dem direkt i template UTAN motsvarande schema-fält. Då finns ingen ACF-koppling att bryta.

**Verifiera efter content-byte:** (1) frontend visar nytt innehåll, (2) WP-admin → sidan → blocket → ACF-fält visar SAMMA värde som frontend, (3) Gutenberg-editorn renderar blocket utan svart ruta.

## Klient-tiers — KRITISK REGEL för nya klienter
LumoKit har två baseline-tiers. Varje ny klient utgår från en av dessa, inte från scratch.

**BASIC** = `clients/patricia-teles/`
- Standard LumoKit-sajt: hero, header, footer, treatments-grid, content-blocks, faq, contact-panel, reviews, map
- Det här är vad "en typisk LumoKit-sajt" ser ut som
- Använd som baseline för normala kund-paket

**Universellt:** Alla sidor ramas in av `lumo/site-header` (överst) och `lumo/site-footer` (nederst) — samma komponent på alla sidor, inte per-page-varianter. Nedan listas bara det page-specifika innehållet däremellan.

**BASIC-tier sidstruktur (4 sidmallar):**

| Sidmall | Content-flöde (mellan header/footer) | Hero-delning |
|---|---|---|
| **Hem** (`/hem`) | hero → intro → treatments-grid → content-block-1 → reviews-section → contact-panel | Egen `hero-hem` |
| **Behandling** (× N — t.ex. `/invisalign`, `/akuttandvard`) | hero → intro → content-block-1 → content-block-2 → faq → contact-panel | Delar `hero-treatment` (per-slug varianter via make_variant) |
| **Om oss** (`/om-oss`) | hero → intro → content-block-1 → content-block-2 → text-blocks → map-section → contact-panel | Delar template med Kontakt |
| **Kontakt** (`/kontakt`) | hero → contact-panel-with-form → map-section | Delar template med Om oss |

**Regel:** Alla behandlingar har samma struktur och ordning. Lägg aldrig till en behandling med annan layout — då bryts mönstret och make_variant-flödet (per `feedback_shared_block_content_loss`).

**PREMIUM-tier sidstruktur (6 mönster — alvsjotandvard):**

| Mönster | Sidor | Content-flöde |
|---|---|---|
| **Hem** | `/hem` | hero → treatments-grid → cost-calculator → reviews → cb-1 → emergency-banner → team → photo-tour |
| **Om oss (utbyggd)** | `/om-oss` | page-hero → cb-1 → text-blocks → team → tandvardsstod → organisation → cta-strip → map → arbeta-med-oss → feedback-form |
| **Behandling — standard** | `/karies`, `/tandblekning`, `/tandfasader`, `/tandsten` | treatment-hero → info-grid → cb-1 → cb-2 → cta-strip → faq |
| **Behandling + premium-widget** | `/implantat`, `/tandreglering`, `/tandvardsradsla` | treatment-hero → info-grid → cb-1 → **\<premium-widget\>** → cb-2 → cta-strip → faq |
| **Behandling — Akut (full premium)** | `/akut-tandvard` | emergency-strip → treatment-hero → dental-triage-widget → cb-1 → process-steps → cb-2 → price-row → cta-strip → faq |
| **Specialsidor** | `/pedodonti`, `/rantefritt`, `/kontakt`, `/remiss-2` | Page-specific layouts med dedikerade widgets |

**Premium-widget per behandling:** Implantat → `treatment-stepper`, Tandreglering → `process-steps`, Tandvårdsrädsla → `fear-matcher`, Akut → `dental-triage-widget` + `process-steps`. Räntefritt-sidan → `payment-calculator`.

**PREMIUM** = `clients/alvsjotandvard/`
- Allt i BASIC + premium-features-suite (`fear-matcher`, `treatment-stepper`, `cost-calculator`, `payment-calculator`, `dental-triage-widget`, `remiss-widget`)
- Plus avancerade hero (video-toggle, region-badge, multiple medaljer, Ring-knapp), `process-steps`, `cta-strip`, `info-grid`, m.fl.
- Premium-features är **extra kostnad** per `feedback_premium_features_scope.md` — använd inte automatiskt

**Vid ny klient — Claude måste alltid fråga vilken tier** innan jag börjar kopiera. Default är BASIC om kunden inte uttryckligen betalt för premium-paket.

Workflow:
```bash
# BASIC (vanligaste fallet):
cp -r clients/patricia-teles clients/<ny-kund>

# PREMIUM (bara om kunden köpt premium):
cp -r clients/alvsjotandvard clients/<ny-kund>

# Sen: ändra .env, brand-färger, content, design-system, slugs, etc.
```

Aldrig blanda — premium-komponenter ska inte krypa in i en basic-sajt utan att kunden betalat för dem.

**Design ÄR ALLTID UNIK per klient.** Baseline-kopiering ärver bara struktur (sidmallar, block-flöde, ACF, backend). Design (färger, typografi, layout-detaljer, visuell stil) MÅSTE bytas ut. Aldrig leverera två sajter som ser ut likadant. Se `feedback_design_uniqueness`.

**ACF-schemas är kontrakt.** Fält-namn (`name`) får aldrig ändras efter att en komponent har data — kundens innehåll försvinner då. `label` får ändras. Default-värden är bara admin-UX, inte runtime-enforcement. Bilder hårdkodas i template, inte via schema default. Se `feedback_acf_field_principles`.

**ALLT användarsynligt innehåll i en sektion SKA vara redigerbart via ACF.** Headlines, eyebrows, ingress, knapptexter, länktexter, USP-punchlines, FAQ-rader, stats — alla texter exponeras som ACF-fält. Undantag: HTML-struktur, CSS-klasser, brand-identitet (logo, site-namn — använd `{{site_*}}` globals), bilder (hårdkodas men alt-text är ACF). Aldrig anta att en text är "design-fast" — kunden ska kunna ändra utan att be om hjälp.

**ALLA komponenter ska vara fullt mobile-responsiva.** Mobile-first är default — designa för mobil först, bygg upp till tablet/desktop. Brytpunkter: mobil ≤600px, tablet 601–900px, desktop ≥901px. Hamburger vid ≤900px. Granska ALLTID mobil + tablet + desktop, inte bara desktop. Se `feedback_mobile_responsive`.

**Tillgänglighet (WCAG 2.1 AA) är default.** Lagkrav i SE/EU. Kontrast ≥4.5:1, synliga focus-states, keyboard-navigation, ARIA-labels, `lang="sv"`, reduced-motion-respekt. Lighthouse a11y-score ≥90 vid lansering. Se `feedback_accessibility_wcag`.

**SEO-grunder på plats per sida.** Title + meta description + OG-tags + structured data (LocalBusiness eller relevant typ) + canonical + sitemap. H1 endast en gång. Se `feedback_seo_basics`.

**GDPR + cookies obligatoriskt.** Cookie-banner med samtycke (default CookieYes), 3rd party scripts (Trustindex, analytics) blockerade tills accept, integritetspolicy + cookie-policy publicerade och länkade i footer. Se `feedback_gdpr_cookies`.

**Lansering = pre-flight-checklista.** Aldrig deploya till live utan att gå igenom `feedback_launch_checklist` (funktion, innehåll, SEO, teknik, prestanda, a11y, mobil, GDPR, backup).

## Mission Statement
Your job is to read instructions, design beautiful Tailwind components, output precise JSON schemas, call the right tools to compile/push, and build bulletproof WordPress sites. Keep it reliable and structured.

---

# Baseline Workflow: Design Hero Section
*(Use this as your standard operating procedure when asked to create a Hero Section)*

## Objective
Design a Hero Section for a WordPress site and generate the required LumoKit JSON payload. The component must be built with Tailwind CSS and map directly to ACF fields.

## Rules & Constraints
1. **Design System:** Use Tailwind CSS utility classes exclusively. Assume a standard Tailwind configuration.
2. **Responsiveness:** Always ensure the design looks good on mobile (`default`), tablet (`md:`), and desktop (`lg:`).
3. **Semantic HTML:** Use proper tags (`<section>`, `<h1>`, `<p>`, `<a>`).
4. **Data Binding:** Use mustache syntax (e.g., `{{headline}}`) for any dynamic content. Do NOT hardcode text or image URLs in the HTML.
5. **Allowed ACF Field Types:** Restrict the schema to `text`, `textarea`, `image`, `url`, and `file`. Use `file` (with optional `mime_types` like `"mp4"` eller `"webm"`) för videor och andra ej-bild-uppladdningar — admin får filhämtare istället för text-fält.

## Output Format
Your output must be a valid JSON object saved to `.tmp/hero_payload.json`.

### JSON Structure Template:
```json
{
  "block_name": "lumo/hero-section",
  "title": "Hero Section",
  "html_template": "<section class=\"relative bg-gray-900 flex items-center justify-center min-h-screen\">\n  <div class=\"z-10 text-center px-4\">\n    <h1 class=\"text-5xl md:text-7xl font-bold text-white mb-6\">{{headline}}</h1>\n    <p class=\"text-lg md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto\">{{subheadline}}</p>\n    <a href=\"{{cta_link}}\" class=\"bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full transition\">{{cta_text}}</a>\n  </div>\n  <div class=\"absolute inset-0 z-0\">\n    <img src=\"{{background_image}}\" alt=\"Background\" class=\"w-full h-full object-cover opacity-40\">\n  </div>\n</section>",
  "schema": [
    {
      "name": "headline",
      "type": "text",
      "label": "Huvudrubrik"
    },
    {
      "name": "subheadline",
      "type": "textarea",
      "label": "Underrubrik"
    },
    {
      "name": "cta_text",
      "type": "text",
      "label": "Knapptext"
    },
    {
      "name": "cta_link",
      "type": "url",
      "label": "Knapplänk"
    },
    {
      "name": "background_image",
      "type": "image",
      "label": "Bakgrundsbild"
    }
  ]
}
```

## Execution Steps for Agent
1. Analyze the client brief to determine the vibe/style of the hero section.
2. Draft the Tailwind HTML structure.
3. Replace all hardcoded content with `{{variable_names}}`.
4. Define the ACF schema mapping those variables.
5. Save the JSON to `.tmp/[client_name]_hero.json`.
6. Call the tool to compile Tailwind (if applicable) and the tool to push to WordPress.