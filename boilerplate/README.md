# LumoKit Boilerplate

Återanvändbar WordPress-snapshot för att starta nya klientsajter på 5-10 minuter. Genererar en `.wpress`-fil som du importerar på fresh WP-installationer.

## Innehåll
```
boilerplate/
├── README.md                       ← den här filen
├── mu-plugins/
│   └── lumokit-config.php          ← ACF Pro-licens som mu-plugin (auto-aktiveras)
└── lumokit-boilerplate.wpress      ← snapshot (genereras av dig, inte i git än)
```

## Engångsförberedelse — gör detta EN gång

### 1. Skapa en boilerplate-WP
- Tom WP-installation på extra domän (eller subdomän, t.ex. `boilerplate.lumokit.se`)

### 2. Lägg in mu-plugin
SFTP/Filhanterare → kopiera `boilerplate/mu-plugins/lumokit-config.php` till `wp-content/mu-plugins/lumokit-config.php` på WP-instansen. (Skapa mappen om den inte finns.)

Det aktiverar ACF Pro-licensen automatiskt så fort ACF Pro installeras.

### 3. Installera nödvändiga plugins
WP Admin → Plugins → Lägg till nytt:
- **Advanced Custom Fields PRO** (ladda upp ZIP från advancedcustomfields.com)
- **WP Mail SMTP** (gratis från wp.org)
- **Trustindex Reviews** (gratis från wp.org)
- **All-in-One WP Migration** (gratis — för export/import)
- *(Valfritt)* **TDL/Dentneo booking widget** — om kunden använder det

Aktivera alla.

### 4. Installera LumoKit Bridge
Ladda upp `wp-plugin/lumokit-bridge.php` till `wp-content/plugins/lumokit-bridge/lumokit-bridge.php`. Aktivera i WP Admin → Plugins.

### 5. Konfigurera grundinställningar
- **Inställningar → Permalänkar** → "Inläggsnamn" (`/%postname%/`)
- **Inställningar → Läsning** → låt vara default (`build_all.py` sätter `page_on_front` automatiskt vid första bygge)
- **Theme:** byt till **Blankslate** (sök i Utseende → Teman → Lägg till). Andra minimalistiska teman funkar också men Blankslate är testat.

### 6. Exportera snapshot
- WP Admin → All-in-One WP Migration → **Export**
- Välj **Export to → File**
- När `.wpress`-filen genererats: ladda ner och spara som `boilerplate/lumokit-boilerplate.wpress` i repo:t (gitignored eftersom den kan bli stor — alternativt LFS)

Klart. Nu har du återanvändbar boilerplate.

---

## Skapa ny klientsajt — gör så här varje gång

### 1. Skapa fresh WP
Hosting (templweb / Loopia / etc) → ny tom WP-installation.

### 2. Importera boilerplate
1. WP Admin → Plugins → Lägg till nytt → sök **All-in-One WP Migration** → installera + aktivera
2. WP Admin → All-in-One WP Migration → **Import**
3. Välj `boilerplate/lumokit-boilerplate.wpress`
4. Klicka import → WP skriver över hela installationen
5. Efter import: logga ut + in igen (sessionerna byts)

### 3. Verifiera plugins
WP Admin → Plugins → kolla att dessa är aktiverade:
- ACF Pro (✅ licens auto-aktiverad via mu-plugin)
- WP Mail SMTP
- Trustindex
- LumoKit Bridge

### 4. Skapa klient-mapp i repo
```
clients/ny-klient/
├── content/
│   ├── text/lumo-content.json
│   └── image/
├── design-system/
└── build_bundle.py     ← kopia från clients/patricia-teles/, anpassad
```

### 5. Uppdatera `.env`
```
WP_URL=https://ny-kunds-domän.se
WP_USERNAME=admin@kunden.se
WP_APP_PASSWORD=<application password från WP Admin>
```

### 6. Kör build från repo-roten
```bash
python3 tools/upload_media.py --dir clients/ny-klient/content/image --manifest clients/ny-klient/content/_media_manifest.json
python3 clients/ny-klient/build_bundle.py
python3 tools/build_all.py clients/ny-klient/bundle.json
```

### 7. Sätt widget-keys + form-mejl
WP Admin → LumoKit → Inställningar:
- `site_email` — kundens mottagar-mejl
- `site_reviews_score` — Trustindex-shortcode
- `site_reviews_testimonials` — Trustindex-shortcode
- `site_booking_api_key` — TDL-token (om bokning används)

### 8. Konfigurera SMTP för mejl-leverans
WP Admin → WP Mail SMTP → koppla mot kundens domän-SMTP (uppgifterna får de av sin webhotell-leverantör). Annars hamnar formulärsubmissions i spam.

Klar — klientens sajt är live.

---

## Underhåll

**När du uppdaterar plugin-versioner i boilerplaten:**
1. Gå till boilerplate-WP → Updates → uppdatera plugins
2. Re-exportera `.wpress`
3. Kommitta nya filen i `boilerplate/` (eller LFS)

Gör det max var 2-3:e månad. Säkerhetsuppdateringar är viktigare än absolut färska versioner.
