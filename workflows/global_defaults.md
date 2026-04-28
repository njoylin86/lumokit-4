# LumoKit — Globala standardinstruktioner

Dessa regler gäller för **alla** klientbyggen om inget annat anges i klientens brief.
De styr tekniska och kvalitetsmässiga krav — aldrig det visuella utfallet.
Det visuella bestäms alltid av klientens egna referensbilder.

Läs detta dokument i Step 1 av `build_site_structure.md` innan bildanalysen påbörjas.

---

## Obligatoriska fält i lumo/site-header

`lumo/site-header` **måste alltid** ha ett `nav_menu`-fält i schemat med `name: "lumokit-primary"`.
Utan det renderas menyn aldrig — `{{lumokit-primary}}` ersätts inte av plugin:et.

```json
{ "name": "lumokit-primary", "type": "nav_menu", "label": "Primär meny" }
```

Kontrollera att detta fält finns varje gång en ny header genereras.

---

## Google-resurser

**Google Fonts** — importeras via `@import` i `<style>`-taggen i `lumo/site-header`:
```html
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
body, body * { font-family: 'Inter', sans-serif !important; }
body h1, body h2, body h3 { font-family: 'Nunito', sans-serif !important; }
</style>
```

**Google Icons (Material Symbols)** — enda tillåtna undantaget från no-class-regeln.
Importeras i `<style>`-taggen i `lumo/site-header`:
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
```
Används i HTML med `class="material-symbols-outlined"`:
```html
<span class="material-symbols-outlined" style="font-size:24px;color:#e07820;">tooth</span>
```
Stilsättning (storlek, färg) görs alltid via inline `style` på span-elementet.
Hitta ikonnamn på: fonts.google.com/icons

---

## Styling

- Använd **alltid** inline `style="..."` — aldrig Tailwind-klasser i `class=""`
- Använd `clamp()` för typografistorlekar, inte fasta px-värden
- Använd `display:grid` eller `display:flex` med inline styles för layouts
- **Font:** Identifieras från referensbilderna i Step 1. Om fonten inte går att identifiera med säkerhet — välj en Google Font som passar designens stil (se tabell i `build_site_structure.md`). Defaulta ALDRIG blint till Inter.
- **Font-override:** Importera vald font och lägg `@import` + `body,body *{font-family:'...',sans-serif!important;}` i `<style>`-taggen i `lumo/site-header`. WordPress-teman skriver annars över fonten. Detta gäller header-komponenten för varje ny klient.

## HTML

- Semantisk HTML5: `<section>`, `<header>`, `<footer>`, `<nav>`, `<h1>`–`<h3>`, `<p>`, `<a>`, `<ul>`, `<li>`, `<img>`
- Inga `<script>`- eller `<iframe>`-taggar
- Alla dynamiska fält använder mustache-syntax: `{{fältnamn}}`

## Globala kontaktuppgifter — ALDRIG per-sida ACF-fält

Telefon, adress, e-post, öppettider och sociala medier är alltid globala värden från ACF Options Page. Lägg **aldrig** till dessa som fält i ett komponents schema — använd mustache-variablerna direkt i `html_template`.

| Mustache-variabel | Innehåll |
|---|---|
| `{{site_phone}}` | Telefonnummer |
| `{{site_address}}` | Adress |
| `{{site_email}}` | E-postadress |
| `{{site_opening_hours}}` | Öppettider |
| `{{site_company_name}}` | Företagsnamn |

| `{{site_facebook}}` | Facebook-URL |
| `{{site_instagram}}` | Instagram-URL |
| `{{site_linkedin}}` | LinkedIn-URL |
| `{{site_twitter}}` | Twitter/X-URL |
| `{{site_tiktok}}` | TikTok-URL |
| `{{site_youtube}}` | YouTube-URL |

| `{{site_reviews_score}}` | Betygswidget — stjärnor/score (renderad HTML från shortcode) |
| `{{site_reviews_testimonials}}` | Kundrecensioner/testimonials (renderad HTML från shortcode) |
| `{{site_booking_api_key}}` | API-nyckel för bokningswidgeten |

**`{{site_booking_api_key}}`** — injiceras **automatiskt** på alla sidor ovanför footern som `<div id="tdl-booking-widget">`. Lägg aldrig till detta manuellt i en komponent.

**`{{site_reviews_score}}`** och **`{{site_reviews_testimonials}}`** — injiceras **aldrig** automatiskt. Placera manuellt i rätt komponent i designen där respektive widget ska visas.

Länkformat:
```html
<a href="tel:{{site_phone}}">{{site_phone}}</a>
<a href="mailto:{{site_email}}">{{site_email}}</a>
<a href="{{site_instagram}}" target="_blank">Instagram</a>
```

---

## ACF-fält

- Tillåtna typer: `text`, `textarea`, `image`, `url`, `nav_menu`
- Alla fält utom `image` och `nav_menu` ska ha ett `default`-värde
- Fältnamn ska vara lowercase med understreck: `hero_headline`, inte `HeroHeadline`

## Övrigt

- Max-bredd för innehåll: `72rem` (motsvarar 1152px)
- Sidmarginaler: minst `24px` på vardera sida
- Inga externa JavaScript-bibliotek

---

*Uppdatera detta dokument när nya globala regler etableras.*
