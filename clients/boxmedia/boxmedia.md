# Klientprofil: Boxmedia

Boxmedia är en återkommande kund som beställer många webbplatser. Reglerna nedan gäller för **alla** Boxmedia-byggen om inget annat anges.

---

## Bokningsknappar

Alla CTA-knappar med bokningssyfte ska ha `href="#tdl-booking-widget"` hårdkodat direkt i `html_template` — aldrig via JavaScript eller som dynamiskt ACF-fält.

**Bakgrund:** Boxmedia-sajter kör ett TDL/Dentneo-bokningsplugin som injicerar `<div id="tdl-booking-widget">` via `wp_footer` på varje sida. Knappar länkar dit via ren HTML-anchor.

---

## TDL-bokningswidget (testinstansen)

Testinstansen (helaine.templweb.com) kör TDL-pluginet globalt — widgeten syns under varje sida. Om den stör layouten, lägg till följande CSS via `compile_tailwind.py`:

```css
body:has(.wp-block-acf-[block-name]) #tdl-booking-widget {
  display: none !important;
}
```

---

## Behandlingssidor — Hero-standard

Alla behandlingssidor delar **samma komponentmall** (`lumo/behandling-hero`). Layouten är låst — bara innehållet varierar per sida via ACF.

### Struktur (fast för alla behandlingssidor)
1. **Bild** — behandlingsrelaterad bild
2. **Heading** — sidans behandlingsnamn
3. **USP-lista** — 4–5 korta punch lines (separata fält: `usp_1`–`usp_5`, varav `usp_5` är valfritt)
4. **Boka-knapp** — `href="#tdl-booking-widget"` (hårdkodad, se bokningsstandard ovan)
5. **Ring-knapp** — telefonnummer som ACF-fält (`ring_nummer`), visas som `tel:`-länk
6. **Google Reviews** — renderas via shortcode/script, hårdkodas i `html_template` (ej ACF-fält)

### ACF-schema (samma för alla behandlingssidor)
| Fältnamn | Typ | Label |
|---|---|---|
| `bild` | `image` | Behandlingsbild |
| `heading` | `text` | Rubrik |
| `usp_1` | `text` | USP 1 |
| `usp_2` | `text` | USP 2 |
| `usp_3` | `text` | USP 3 |
| `usp_4` | `text` | USP 4 |
| `usp_5` | `text` | USP 5 (valfritt) |
| ~~`ring_nummer`~~ | — | Används **inte** — se nedan |

### Ring-knappen — globalt värde
Telefonnumret hämtas från ACF Options Page (`site_phone`), **inte** som ett per-sida ACF-fält. I `html_template` används `{{site_phone}}` och länken byggs som:

```html
<a href="tel:{{site_phone}}">Ring oss — {{site_phone}}</a>
```

Lägg **inte** till `ring_nummer` i schemat — det globala värdet löses upp automatiskt av pluginet.

### Viktiga regler
- Pusha **en gång** som komponent — återanvänd på alla behandlingssidor. Ändra aldrig per-sida.
- Om layouten behöver ändras, ändra komponenten — alla behandlingssidor uppdateras automatiskt.
- Google Reviews-scriptet/shortcoden hårdkodas direkt i `html_template`, exakt samma på alla sidor.

---

## Övrigt att komma ihåg

- Identifiera Boxmedia-byggen via `lumokit_platform = boxmedia` om det används i bundle-konfigurationen.
- Uppdatera denna fil när nya krav eller preferenser tillkommer.
