# Hero — PREMIUM-variant

> ⚠️ **Detta är PREMIUM-versionen** av hero-komponenten, baserad på alvsjotandvard.
> För BASIC-klienter: utgå från patricia-teles' hero istället (`clients/patricia-teles/build_bundle.py` → `build_hero()`).
> Premium-element nedan (Ring-knapp, region-badge, recensions-widget, video-toggle, multiple medaljer) ska **inte** läggas in i basic-sajter utan att kunden har köpt premium-paket.
> Se [CLAUDE.md → Klient-tiers](../../CLAUDE.md) och memory `feedback_premium_features_scope`.

## Syfte

Sajtens första intryck. Full-bleed sektion (oftast 100vh) med bakgrundsbild eller -video, headline + ingress + USPs + minst en CTA. Konverteringspunkten.

Used på: startsida (alltid), ibland landningssidor som "akut-tandvård" etc. Behandlingssidor använder oftast en lättare variant: se [treatment-hero.md](treatment-hero.md) (separat mönster).

## Anatomi

Obligatoriskt:
- **Bakgrund** — bild eller video (full-bleed, object-cover, scrim/overlay för läsbarhet)
- **Eyebrow** — kort etikett ovanför rubriken (ex. "Modern tandvård · 2 min från pendeln · Älvsjö")
- **Headline** — H1, stor display-font, ev. med italic-accent på sista raden
- **Ingress** — kort beskrivande paragraf (1-2 meningar)
- **USP-punchlines** — 3-4 säljpunkter (per `feedback_hero_punchlines.md`)
- **CTA-knapp(ar)** — minst en, "Boka tid" eller motsvarande
- **Scrim/overlay** — semi-transparent lager för text-läsbarhet (per `feedback_hero_text_readability.md`)

Optional men vanligt:
- **Telefon-CTA / Ring-knapp** — bredvid bok-knappen (tel:-länk)
- **Medaljer / certifieringar** — top-right (desktop) / corner (mobile)
- **Region-badge** — t.ex. "På uppdrag av Region Stockholm"
- **Recensions-widget** — Trustindex stars + score
- **Stats-rad** — siffror under hero ("X år", "Y kunder")

## HTML-skeleton

```html
<section class="hero-bleed">
  <!-- Bakgrund: bild + ev. video-toggle -->
  <div class="hb-bg" style="background-image:url('{{HARDCODED_URL}}');"></div>
  <video class="hb-bg-video hb-bg-video--desktop" autoplay muted loop playsinline>
    <source src="{{video_desktop}}" type="video/mp4">
  </video>
  <video class="hb-bg-video hb-bg-video--mobile" autoplay muted loop playsinline>
    <source src="{{video_mobile}}" type="video/mp4">
  </video>
  <div class="hb-overlay"></div>   <!-- Scrim -->

  <!-- Top-rad: eyebrow + medaljer (desktop) -->
  <div class="hb-top">
    <div class="hb-top-inner">
      <span class="hb-top-left">{{eyebrow}}</span>
    </div>
    <div class="hb-top-medals hb-medals-desktop">
      <!-- medaljer som <a><img></a> -->
    </div>
  </div>

  <!-- Huvudinnehåll: grid 60/40 (vänster: text, höger: CTAs + widgets) -->
  <div class="hb-content container-wide">
    <div class="hb-left">
      <h1 class="hb-headline">
        Trygg tandvård.<br>
        <span class="hb-headline-accent">Hela familjen.</span>
      </h1>
      <p class="hb-ingress">{{ingress}}</p>
    </div>
    <div class="hb-right">
      <!-- Mobil-medaljer (corner) -->
      <div class="hb-medals hb-medals-mobile hb-medals-mobile-corner">
        <!-- ... -->
      </div>

      <!-- CTA-knappar -->
      <div class="hb-buttons">
        <a href="#tdl-booking-widget" class="btn btn-light btn-lg">
          <svg>...</svg>Boka tid
        </a>
        <a href="tel:+46812854555" class="btn btn-lg hb-ring">
          <svg>...</svg>Ring oss
        </a>
      </div>

      <!-- Bottom-rad: recensioner + region-badge -->
      <div class="hb-bottom-row">
        <div class="hb-review-widget">[trustindex data-widget-id=...]</div>
        <img class="hb-region-badge" src="..." alt="...">
      </div>
    </div>
  </div>

  <!-- Stats-rad (desktop, under content) -->
  <div class="hb-stats hb-stats-desktop container-wide">
    <div><span class="hb-stat-lbl">{{stat_1_text}}</span></div>
    <div><span class="hb-stat-lbl">{{stat_2_text}}</span></div>
    <div><span class="hb-stat-lbl">{{stat_3_text}}</span></div>
    <div><span class="hb-stat-lbl">{{stat_4_text}}</span></div>
  </div>
</section>
```

## ACF-schema (typiska fält)

| Fält | Typ | Roll | Default |
|---|---|---|---|
| `eyebrow` | text | Etikett ovanför H1 | "Modern X · Y · Plats" |
| `ingress` | textarea | 1-2 meningar | (beskrivning av kliniken/verksamheten) |
| `stat_1_text` ... `stat_4_text` | text | 4 USP-rader | "Gratis för barn", "Akut hjälp idag", ... |
| `hero_video_desktop` | text (URL) | MP4 desktop | "" |
| `hero_video_mobile` | text (URL) | MP4 mobil | "" |

**Viktigt:** Bakgrundsbilden hårdkodas i `html_template`, inte via ACF-fält. Se `feedback_image_changes.md` — Bridge ignorerar ACF-image-fält vid omrendering.

## CSS-mönster (essentiella regler)

```css
/* Full-bleed grunden */
.hero-bleed {
  position: relative; min-height: 100vh;
  display: grid; grid-template-rows: auto 1fr auto;
  overflow: hidden;
}
.hero-bleed .hb-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  z-index: 0;
}
.hero-bleed .hb-overlay {
  position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(180deg,
    rgba(0,0,0,.45) 0%, rgba(0,0,0,.35) 50%, rgba(0,0,0,.65) 100%);
}
.hero-bleed > :not(.hb-bg):not(.hb-bg-video):not(.hb-overlay) {
  position: relative; z-index: 2;
}

/* Content-grid 60/40 desktop, stack mobile */
.hero-bleed .hb-content {
  display: grid; grid-template-columns: 1.4fr 1fr;
  gap: 64px; padding: 96px 0 80px;
}
@media (max-width: 900px) {
  .hero-bleed .hb-content { grid-template-columns: 1fr; }
}

/* Medaljer-positionering (desktop top-right, mobile corner) */
.hero-bleed .hb-medals-desktop { display: flex; }
.hero-bleed .hb-medals-mobile { display: none; }
@media (max-width: 900px) {
  .hero-bleed .hb-medals-desktop { display: none; }
  .hero-bleed .hb-medals-mobile-corner {
    position: absolute; top: 16px; right: 16px; z-index: 11;
  }
}
```

## Varianter

| Klient | Varianter använda |
|---|---|
| alvsjotandvard | Bild + video-toggle, Ring-knapp, region-badge, recensioner i bottom-row |
| patricia-teles | (att kartlägga) |

**Varianter att överväga per klient:**
- Headline med eller utan italic-accent på sista raden
- CTA-mängd: 1 (bara boka) vs 2 (boka + ring) vs 3 (+ chat)
- Stats: med eller utan (vissa kunder har ingen kvantifierbar USP)
- Video vs bara bild
- Region-badge: bara om aktuellt (offentligt uppdrag)

## Fallgropar

- **Hero-text MÅSTE vara extremt läsbar** — se `feedback_hero_text_readability.md`. Aldrig kompromissa scrim/overlay för "subtil design".
- **Hero-punchlines är obligatoriska** — `feedback_hero_punchlines.md`. 3-4 stycken, pink check-ikon + kort text. ALDRIG hero utan dem.
- **Bakgrundsbilder hårdkodas i template** — `feedback_image_changes.md`. Bridge skriver inte tillbaka ACF-image-värden vid rerender.
- **Ring/tel-knappar måste vara klickbara länkar** — `feedback_contact_values_clickable.md`. `<a href="tel:+46...">`, inte `<button>`.
- **Mobil-medaljer i corner** — på små skärmar tar de annars för mycket plats i content.
- **JS-kommentarer i template** — använd `/* */`, aldrig `//` (collapse() rensar radbrytningar — se `feedback_js_comments_in_collapse.md`).

## Källkods-referens

Mest mogen implementation: `clients/alvsjotandvard/build_bundle.py` → funktion `build_hero()`.

CSS: `clients/alvsjotandvard/build_bundle.py` → `LAYOUT_CSS`-strängen, sök `.hero-bleed`.

För att kopiera till ny klient: pulla live `lumo/hero` från alvsjotandvard via `tools/pull_from_wp.py lumo/hero --save --client alvsjotandvard` och anpassa.
