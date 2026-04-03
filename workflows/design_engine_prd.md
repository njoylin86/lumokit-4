# LumoKit Design Engine — Master PRD
**Metodik:** Vision-to-Code  
**Ramverk:** WAT (Workflows · Agents · Tools)  
**Status:** Aktiv regelbok — används vid varje komponentgenerering

---

## Syfte

Detta dokument definierar den exakta process Agenten (Claude) ska följa varje gång en referensbild laddas upp. En screenshot ska räcka — ingen ytterligare instruktion krävs. Resultatet ska vara en **visuellt identisk** implementation av designen, pushad till WordPress och redo att fyllas med innehåll.

Avvik **aldrig** från dessa faser. Hoppa **inte** över steg.

---

## Fas 1: Input & Setup

### 1.1 Ta emot inputs
En screenshot räcker. Om en kundbrief medföljer, använd den för ton och namngivning. Om inte — härled allt från bilden.

### 1.2 Identifiera och lista alla sektioner
Gå igenom hela bilden uppifrån och ned. Lista **varje synlig sektion** och ge den ett blocknamn innan du börjar koda något:

```
1. lumo/hero-section
2. lumo/services-row
3. lumo/content-image
...
```

### 1.3 Namnge output-filer
```
.tmp/[klientnamn]_[komponent].json
```

---

## Fas 2: Pixelnoggrann Bildanalys

**Målet är identisk återgivning — inte en "liknande" design.**

Analysera bilden systematiskt för varje sektion. Skriv ned alla värden i din reasoning innan du skriver HTML.

### 2.1 Elementordning (KRITISK)
Läs av varje elements position i bilden **uppifrån och ned, vänster till höger**. Skriv ned ordningen explicit:

```
Sektion: Hero
1. H1 "Webbyrå Stockholm"
2. Label "ADS, SEO OCH WEBBDESIGN"  ← under H1, inte ovanför
3. Brödtext
4. CTA-knapp
5. Illustration (höger kolumn)
```

DOM-ordningen ska matcha den visuella ordningen exakt. Gissa aldrig.

### 2.2 Färger — exakta värden
Identifiera varje färg och dess exakta hex-värde så nära som möjligt. Mappa sedan till Tailwind. Om ingen Tailwind-klass matchar inom rimlig tolerans, använd inline `style="color:#XXXXXX"`.

| Element | Hex (uppskattat) | Tailwind-klass |
|---|---|---|
| Bakgrund | #e0f7fa | bg-cyan-100 |
| H1 text | #111827 | text-gray-900 |
| Muted text | #6b7280 | text-gray-500 |
| Accent/knapp | #f472b6 | bg-pink-400 |

### 2.3 Typografi — exakta proportioner
Mät varje textelements relativa storlek mot sidan:

- **H1:** Hur stor är den relativt brödtexten? → `text-5xl` / `text-6xl` / `text-7xl`
- **Font-weight:** Normal, medium, semibold, bold, extrabold?
- **Letter-spacing:** Är det tracking-wide, tracking-widest (versaler med luft)?
- **Line-height:** Tight, normal, relaxed?
- **Versaler:** Är texten uppercase?
- **Font-familj:** Är det en Google Font? Identifiera vilken och importera den via `<link>` i `html_template`.

### 2.4 Spacing — exakta avstånd
Uppskatta padding och margin relativt till sektionens höjd/bredd:

- Sektionens vertikala padding: liten (`py-8`), mellan (`py-16`), stor (`py-24`)?
- Avstånd mellan element: tätt (`gap-2`), normalt (`gap-6`), luftigt (`gap-12`)?
- Innehållets max-bredd: smal (`max-w-3xl`), standard (`max-w-6xl`), full?

### 2.5 Layout & Proportioner
- Hur många kolumner? Exakt kolumnbredd (50/50, 40/60, 33/66)?
- Hur är elementen vertikalt justerade (top, center, bottom)?
- Hur staplas det på mobil?

### 2.6 Knappar & Interaktiva element
Analysera varje knapp noggrant:
- Fylld (`bg-*`) eller outline (`border-*`)?
- Border-tjocklek (1px, 2px)?
- Border-radius (ingen, `rounded-lg`, `rounded-full`)?
- Text-transform (uppercase, normal)?
- Padding (kompakt, normal, generös)?

### 2.7 Kort, bilder & dekorativa element
- Har kort `border`, `shadow`, `rounded-*`?
- Vilken `object-fit` används för bilder (cover, contain)?
- Finns det gradient-overlays eller opacity på bilder?

---

## Fas 3: HTML-generering

### 3.1 Regler

1. **Semantisk HTML5** — `<section>`, `<h1>`–`<h3>`, `<p>`, `<a>`, `<ul>`, `<li>`, `<img>`.
2. **Inga `<script>`- eller `<iframe>`-taggar** — blockeras av LumoKit Bridge.
3. **Tailwind för layout och spacing.** För färg, border och typografi på `<a>`-taggar och knappar: använd alltid inline `style` — WordPress-teman skriver annars över Tailwind.
4. **Responsivitet är obligatoriskt** — mobil (default), tablet (`md:`), desktop (`lg:`).
5. **Elementordning följer Fas 2.1 exakt** — ingen kreativ omtolkning.
6. **Google Fonts** — om en specifik font identifieras, importera den överst i `html_template`:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
   ```

### 3.2 Kvalitetskontroll — jämför mot bilden
Innan du går till Fas 4, gå igenom denna checklista:

- [ ] Elementordningen matchar bilden uppifrån och ned?
- [ ] Färgerna stämmer (bakgrund, text, accent)?
- [ ] Knappens stil stämmer (fylld/outline, rundning)?
- [ ] Kolumnproportioner stämmer (50/50 etc.)?
- [ ] Typografins storlek och vikt stämmer?
- [ ] Spacing känns identisk med bilden?
- [ ] Responsivitet hanterad?

---

## Fas 4: Data-mappning (ACF) & JSON-generering

### 4.1 Identifiera dynamiska fält
Allt innehåll en klient kan vilja redigera:
- All text (rubriker, brödtext, knapptexter, labels)
- Alla bild-URL:er
- Alla länk-URL:er

Statiska strukturelement (divar, SVG-ikoner) är inte dynamiska.

### 4.2 Namnge variabler (snake_case, engelska)

| Innehåll | Variabelnamn |
|---|---|
| Huvudrubrik | `headline` |
| Underrubrik | `subheadline` |
| Brödtext | `body_text` |
| Knapptext | `cta_text` |
| Knapplänk | `cta_link` |
| Bakgrundsbild | `background_image` |
| Kortbild | `card_image` |
| Kortitel | `card_title` |

För repeterande element: `feature_1_title`, `feature_2_title` etc.

### 4.3 Default-värden (obligatoriskt)
Varje fält i schemat **måste** ha ett `default`-värde. Defaults ska vara kontextuella — baserade på texten och innehållet som faktiskt syns i referensbilden, inte generiska placeholders som "Lorem ipsum".

```json
{
  "name": "headline",
  "type": "text",
  "label": "Huvudrubrik",
  "default": "Webbyrå Stockholm"
}
```

För `image`-fält, sätt `default` till en `placehold.co`-URL med dimensioner som passar komponenten:
- Hero/bakgrundsbild: `https://placehold.co/1200x800`
- Kortbild (kvadrat): `https://placehold.co/600x600`
- Bred sektionsbild: `https://placehold.co/1200x600`
- Profilbild: `https://placehold.co/400x400`

### 4.4 Tillåtna ACF-fälttyper

| Innehållstyp | ACF-typ |
|---|---|
| Kort text | `text` |
| Längre text | `textarea` |
| Bild | `image` |
| Länk | `url` |

### 4.4 JSON-format
```json
{
  "block_name": "lumo/[komponent-namn]",
  "title": "[Visningsnamn]",
  "html_template": "[HTML på en rad med \\n och escapade \\\"]",
  "schema": [
    { "name": "headline", "type": "text", "label": "Huvudrubrik" }
  ]
}
```

### 4.5 Spara och pusha
1. Spara varje komponent till `.tmp/[klientnamn]_[komponent].json`
2. `python3 tools/push_to_wp.py .tmp/[fil].json` — för varje komponent
3. `python3 tools/compile_tailwind.py` — kompilera och pusha CSS
4. Skapa en page spec-fil `.tmp/[klientnamn]_page.json` med alla block i rätt ordning:
   ```json
   {
     "title": "[Sidans titel]",
     "slug": "[url-slug]",
     "blocks": [
       "lumo/hero-section",
       "lumo/services-row",
       "lumo/contact-form"
     ]
   }
   ```
5. `python3 tools/build_page.py .tmp/[klientnamn]_page.json` — skapar sidan i WordPress
6. Bekräfta `[OK]` och presentera `page_url` för användaren.

---

## Snabbreferens

```
SCREENSHOT
      ↓
FAS 1: Lista alla sektioner
      ↓
FAS 2: Pixelnoggrann analys (ordning, färger, typografi, spacing, knappar)
      ↓
FAS 3: HTML (Tailwind + inline style för knappar, responsivt)
      ↓
      Kvalitetskontroll mot bilden
      ↓
FAS 4: ACF-mappning → JSON → push → compile CSS
```

---

*Detta dokument är Agentens primära regelbok. Uppdatera det när nya constraints upptäcks.*
