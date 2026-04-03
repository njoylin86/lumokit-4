# LumoKit Design Engine — Master PRD
**Metodik:** Vision-to-Code  
**Ramverk:** WAT (Workflows · Agents · Tools)  
**Status:** Aktiv regelbok — används vid varje komponentgenerering

---

## Syfte

Detta dokument definierar den exakta process Agenten (Claude) ska följa varje gång en referensbild och en kundbrief laddas upp. Resultatet av processen är alltid ett färdigt LumoKit JSON-payload redo att pushas till WordPress via `tools/push_to_wp.py`.

Avvik **aldrig** från dessa faser. Hoppa **inte** över steg.

---

## Fas 1: Input & Setup

### 1.1 Ta emot inputs
Agenten kräver två inputs innan arbetet börjar:

| Input | Format | Krävs |
|---|---|---|
| Referensbild | PNG / JPG / WebP (mockup eller inspirationsbild) | Ja |
| Kundbrief | Fritext (varumärke, ton, syfte, målgrupp) | Ja |

Om något av dessa saknas — **stanna och fråga användaren** innan du fortsätter.

### 1.2 Identifiera komponenten
Bestäm komponenttyp baserat på bilden:
- Är det en hel sektion (Hero, Features, Testimonials, CTA, Footer)?
- Är det ett enskilt UI-element (Card, Button, Nav)?

Namnge komponenten enligt konventionen `lumo/[komponent-namn]` (kebab-case, t.ex. `lumo/hero-section`, `lumo/feature-grid`).

### 1.3 Skapa output-fil
Bestäm filnamnet för payloaden:
```
.tmp/[klientnamn]_[komponent].json
```
Exempel: `.tmp/acme_hero.json`

---

## Fas 2: Analys & Design Tokens

Använd din vision-förmåga för att noggrant analysera referensbilden. Extrahera följande designtokens **innan** du skriver en rad HTML.

### 2.1 Färgpalett
Identifiera de dominerande färgerna i bilden. Mappa varje färg till närmaste Tailwind-ekvivalent.

**Procedur:**
1. Identifiera bakgrundsfärg(er) → mappa till Tailwind `bg-*`
2. Identifiera primär textfärg → mappa till Tailwind `text-*`
3. Identifiera accentfärg (knappar, highlights) → mappa till Tailwind `bg-*` / `border-*`
4. Identifiera sekundär textfärg (subtext, labels) → mappa till Tailwind `text-*`

**Output-format (internt, skriv i din reasoning):**
```
background:   bg-gray-950
text-primary: text-white
accent:       bg-blue-600
text-muted:   text-gray-400
```

Om bilden använder en anpassad färg som inte har en nära Tailwind-ekvivalent (< 15% avvikelse), använd närmaste match. Dokumentera avvikelsen i en kommentar i JSON-filen.

### 2.2 Typografisk hierarki
Analysera textelement i bilden:

| Nivå | Vad du tittar på | Tailwind-klasser |
|---|---|---|
| H1 / Huvudrubrik | Storlek, vikt, radavstånd | `text-5xl font-bold leading-tight` |
| H2 / Underrubrik | Storlek, vikt | `text-2xl font-semibold` |
| Brödtext | Storlek, färg, radavstånd | `text-base text-gray-300 leading-relaxed` |
| Label / Tag | Storlek, versaler, spacing | `text-xs uppercase tracking-widest` |

Välj alltid från Tailwinds standardskala. Gissa inte — basera storleksvalen på proportionerna i bilden.

### 2.3 Spacing & Layout
- **Padding/margin:** Uppskatta gutter och inre padding. Mappa till Tailwind spacing-skala (`p-4`, `py-16`, `gap-8` etc.)
- **Layout-typ:** Är det Flexbox eller Grid? Hur många kolumner? Hur staplas det på mobil?
- **Max-bredd:** Har innehållet ett `max-w-*`-container?

### 2.4 Border & Rundning
- Knappar: `rounded`, `rounded-full`, `rounded-lg`?
- Kort/boxar: Har de `border`, `shadow`, `rounded-xl`?

### 2.5 Spara tokens lokalt (i reasoning)
Sammanfatta alla tokens i ett block i din reasoning-process innan du går till Fas 3. Detta säkerställer enhetlighet genom hela komponenten.

---

## Fas 3: Tailwind-kodning

### 3.1 Regler för HTML-generering

1. **Enbart semantisk HTML5.** Använd `<section>`, `<article>`, `<header>`, `<nav>`, `<h1>`–`<h3>`, `<p>`, `<a>`, `<ul>`, `<li>`, `<img>`, `<figure>`.
2. **Inga `<script>`- eller `<iframe>`-taggar** — någonsin. Dessa blockeras av LumoKit Bridge.
3. **Enbart Tailwind utility-klasser** för all styling. Inga inline `style=""`-attribut.
4. **Responsivitet är obligatoriskt.** Varje komponent måste fungera på tre breakpoints:
   - Mobil (default, ingen prefix)
   - Tablet (`md:`)
   - Desktop (`lg:`)
5. **Hårdkoda innehållet i detta steg.** Skriv riktiga exempeltexter och bild-URL:er i HTML:en. Det är lättare att verifiera layouten och sedan abstrahera i Fas 4.
6. **Följ designtokens från Fas 2 exakt.** Avvik inte kreativt från referensbilden om inte kundbriefet kräver det.

### 3.2 Komponentstruktur (mall)
```html
<section class="[bakgrund] [padding]">
  <div class="max-w-6xl mx-auto px-4 [layout]">
    <!-- Innehåll här -->
  </div>
</section>
```

Anpassa strukturen efter komponenttypen, men behåll alltid ett `max-w-*`-wrapper för innehållet.

### 3.3 Kvalitetskontroll innan Fas 4
Kontrollera mentalt:
- [ ] Ser layouten rätt ut på mobil (single-column)?
- [ ] Ser layouten rätt ut på desktop (multi-column om bilden visar det)?
- [ ] Är färgerna i linje med tokens från Fas 2?
- [ ] Är typografin proportionerlig mot referensbilden?
- [ ] Finns det inga hårdkodade `style`-attribut?

---

## Fas 4: Data-mappning (ACF) & JSON-generering

### 4.1 Identifiera dynamiska fält
Gå igenom HTML:en från Fas 3 och markera **allt innehåll som en klient kan vilja redigera:**
- All text (rubriker, brödtext, knapptexter, labels)
- Alla bild-URL:er
- Alla länk-URL:er

Statiska strukturelement (layout-divar, ikoner inbakade i SVG) behöver **inte** bli dynamiska fält.

### 4.2 Namnge variabler
Använd beskrivande, snake_case-namn på engelska:

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

För repeterande element (t.ex. tre feature-kort), använd suffix: `feature_1_title`, `feature_1_icon`, `feature_2_title`, etc.

### 4.3 Ersätt hårdkodat innehåll med mustache-syntax
Byt ut varje hårdkodat värde mot `{{variabelnamn}}`:

```html
<!-- Innan -->
<h1 class="text-5xl font-bold text-white">Välkommen till Acme</h1>

<!-- Efter -->
<h1 class="text-5xl font-bold text-white">{{headline}}</h1>
```

För `<img>`-taggar, ersätt `src`-attributet:
```html
<img src="{{background_image}}" alt="Background" class="w-full h-full object-cover">
```

### 4.4 Tillåtna ACF-fälttyper
Använd **enbart** dessa fälttyper i schemat:

| Innehållstyp | ACF-typ |
|---|---|
| Kort text (rubrik, label, knapptext) | `text` |
| Längre text (brödtext, beskrivning) | `textarea` |
| Bild-URL | `image` |
| Länk-URL | `url` |

Använd **aldrig** `wysiwyg`, `repeater`, `flexible_content` eller andra avancerade typer — de stöds inte av LumoKit Bridge v1.

### 4.5 Generera JSON-payload
Sätt ihop det slutgiltiga JSON-objektet:

```json
{
  "block_name": "lumo/[komponent-namn]",
  "title": "[Komponentens visningsnamn]",
  "html_template": "[HTML-strängen med {{variabler}}, escaped med \\n för radbrytningar]",
  "schema": [
    {
      "name": "[variabelnamn]",
      "type": "[text|textarea|image|url]",
      "label": "[Läsbart namn på svenska]"
    }
  ]
}
```

**Regler för `html_template`-strängen:**
- Hela HTML:en ska vara på **en rad** med `\n` för radbrytningar.
- Inga riktiga radbrytningar inuti JSON-strängen (ogiltigt JSON).
- Dubbelcitattecken inuti HTML-attribut måste escapas: `\"`.

### 4.6 Spara och pusha
1. Spara JSON till `.tmp/[klientnamn]_[komponent].json`
2. Kör: `python tools/push_to_wp.py .tmp/[klientnamn]_[komponent].json`
3. Bekräfta `[OK]`-respons med `post_id`
4. Vid fel: Läs felmeddelandet, korrigera payload eller tool, försök igen. Dokumentera felet enligt Self-Improvement Loop i CLAUDE.md.

---

## Snabbreferens: Fas-översikt

```
INPUT (Bild + Brief)
      ↓
FAS 1: Setup        → Identifiera komponent, namnge output-fil
      ↓
FAS 2: Tokens       → Extrahera färger, typografi, spacing, rundning
      ↓
FAS 3: HTML         → Bygg responsiv Tailwind-layout med hårdkodat innehåll
      ↓
FAS 4: ACF-mappning → Abstrahera till {{variabler}}, bygg schema, spara JSON
      ↓
PUSH               → python tools/push_to_wp.py .tmp/[fil].json
```

---

*Detta dokument är Agentens primära regelbok för komponentgenerering. Uppdatera det när nya constraints eller fälttyper upptäcks.*
