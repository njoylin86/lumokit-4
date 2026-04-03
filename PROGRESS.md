# LumoKit — Framsteg & Nästa steg

## Vad vi har byggt

Ett AI-drivet system för att generera WordPress-sidor från en screenshot.

### Flödet (fungerar idag)
1. Ladda upp en screenshot → AI analyserar designen
2. Komponenter genereras som JSON och pushas till WordPress
3. Tailwind CSS kompileras och pushas
4. Sidor + nav-meny skapas automatiskt — klart att fylla med riktigt innehåll

### Verktyg
| Script | Vad det gör |
|---|---|
| `tools/push_to_wp.py` | Pushar en komponent till WordPress |
| `tools/compile_tailwind.py` | Kompilerar Tailwind CSS och pushar |
| `tools/build_page.py` | Skapar en enskild sida med block |
| `tools/build_site.py` | Skapar alla sidor + nav-meny i ett kommando |

### WordPress-pluginet
`wp-plugin/lumokit-bridge.php` hanterar allt på serversidan:
- Tar emot komponenter via REST API
- Registrerar Gutenberg-block och ACF-fält dynamiskt
- Injicerar header och footer automatiskt på alla sidor
- Skapar sidor och menyer programmatiskt

---

## Så här startar en ny klient

1. **Ladda upp en screenshot** av designen i chatten
2. **AI:n genererar** alla komponenter och pushar dem
3. **Definiera sidorna** i `.tmp/[klientnamn]_site.json`:
```json
{
  "site_name": "Klientnamn",
  "pages": [
    {
      "title": "Hem",
      "slug": "hem",
      "menu_label": "Start",
      "blocks": ["lumo/hero-section", "lumo/services-row", "lumo/contact-form"]
    }
  ]
}
```
4. **Kör:**
```bash
python3 tools/build_site.py .tmp/[klientnamn]_site.json
```
5. Klart — sidor och meny är skapade. Klienten fyller i innehåll via ACF i WP Admin.

---

## Vad som är kvar att bygga

- [ ] **End-to-end test med ny klient** — testa hela flödet från screenshot till live sida med ett nytt klientnamn
- [ ] **Förbättra nav-styling** — meny-länkarna i headern kan behöva mer polish beroende på design
- [ ] **Mobil-meny** — hamburger-meny för mobil saknas i headern
- [ ] **Fler block-typer** — t.ex. testimonials, pricing, blog-grid

---

## Testsite (Boxmedia)
- **URL:** https://helaine.templweb.com/hem/
- **WP Admin:** https://helaine.templweb.com/wp-admin/
