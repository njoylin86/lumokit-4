# Ny klient — input jag behöver från dig

Tvåfas-flöde: bygget startar med minimum input, deployment-detaljer kommer senare.

```
FAS 1 — BYGG     → design system + content
                   ↓
                   Claude bygger mot dev-WP, du granskar + godkänner

FAS 2 — DEPLOYA  → WP-creds, domän, e-mail, redirects
                   ↓
                   Claude lanserar enligt launch-checklist
```

---

## FAS 1 — För att börja bygga

### Tier
- [ ] **BASIC** eller **PREMIUM** (om PREMIUM: vilka features ingår)

### Design system
- [ ] Logotyp (helst vektor)
- [ ] Brand-färger (HEX)
- [ ] Fonts (eller känsla — "modern sans", "klassisk serif")
- [ ] Tonalitet (formell/avslappnad)
- [ ] Ev. referenssajter du gillar visuellt

### Content
- [ ] Verksamhet (bransch, USP, om kunden)
- [ ] Lista vilka sidor som ska skapas (t.ex. hem, om-oss, kontakt, tandimplantat, invisalign, akuttandvard)
- [ ] Copy per sida (eller punktform, jag skriver utkast)
- [ ] Bilder
- [ ] Recensioner / Trustindex widget-ID om finns

> Jag väljer mall själv baserat på tier + sidans syfte. Frågar bara om en sida är ovanlig eller om jag behöver mappa en behandling till specifik premium-widget.

### Kontrollpunkt
- [ ] Mockup klar — du granskar och godkänner innan dekomponering

---

## Arkitektur-regler — FÖLJ STRIKT från första byggesteget

### CSS-pipeline (KRITISKT — annars uppstår samma friktion som på alvsjotandvard)

**Regel:** Custom CSS levereras via `bundle["snippets"]`. ALDRIG som `<style>`-block inuti en komponents `html_template`.

När du kopierar baseline-mall för ny klient (BASIC från `patricia-teles`, PREMIUM från `alvsjotandvard`):

**Första migrerings-steget innan content fylls i:**

1. Splitta `build_site_header(tokens_css)` → två funktioner i `build_bundle.py`:
   ```python
   def build_layout_css(tokens_css: str) -> str:
       """Returnerar all CSS (tokens + LAYOUT_CSS + header-variants + hero-bg + inactive).
       Får INTE innehålla mustache — kör inte genom Bridge:s resolver."""
       # ... header_variant_css, header_light_override, hero_bg_css, inactive_css ...
       return f"{tokens_css}\n{LAYOUT_CSS}\n{header_variant_css}\n{header_light_override}\n{hero_bg_css}\n{inactive_css}"

   def build_site_header() -> dict:
       # ... HTML only, no <style> block in html_template ...
       return {"block_name": "lumo/site-header", "html_template": ..., "schema": [...]}
   ```

2. I `main()`:
   ```python
   tokens_css = TOKENS_FILE.read_text(encoding="utf-8")
   layout_css = build_layout_css(tokens_css)
   site_header = build_site_header()
   ```

3. I bundle-dict:
   ```python
   bundle = {
       ...,
       "components": [...],
       "snippets": [
           {"name": "lumokit-layout", "type": "css", "code": layout_css},
       ],
       ...
   }
   ```

4. Verifiera: gör `git grep '"<style>"' clients/<klient>/build_bundle.py` — ska returnera tomt.

**Varför:** `compile_tailwind.py` plockar redan upp `snippets[type=css]` och prependar till Tailwind-output. Bridge:n servar via `<style id="lumokit-styles">` i `<head>`. En CSS-edit = en file change + en push. Ingen override-sync, ingen drift mellan source/live.

**Konsekvens av att hoppa över detta steg:** Varje framtida CSS-edit kräver ~60 sekunder och dubbla edits istället för ~20 sekunder + en edit. Drift mellan source/override skapar mysterious bugs (se `feedback_live_overrides_mechanism`).

Se `project_css_refactor.md` för full bakgrund och historik.

### Andra arkitektur-regler
- Inga `<style>`-block i NÅGON komponents `html_template`. Punkt.
- Bilder hardcodas inte i komponenters template — använd `{{site_url}}/wp-content/uploads/...` mustache så domänbyte fungerar
- Mustache-syntax används inte i snippets (de körs inte genom resolvern)

---

## FAS 2 — För att lansera

### Teknik
- [ ] WP-URL + credentials (från templweb)
- [ ] Domän + registrator
- [ ] Befintlig sajt (om migration → gamla URL:er för redirects)
- [ ] E-mail-konto som tar emot kontaktformulär
- [ ] Bokningssystem (TDL/Boxmedia/inget)
- [ ] Analytics-krav

### Kontrollpunkter
- [ ] Pre-flight klar — du godkänner go-live
- [ ] Final smoke-test efter DNS-omkoppling — allt OK?

---

**Mål:** I slutändan ska FAS 1 kunna automatiseras helt — design system + content går in via formulär, AI bygger autonomt. Per `project_vision`.
