# Patricia Teles

Tandvårdsklinik i centrala Stockholm (Jakobsbergsgatan 8). LumoKit-byggd sajt.

## Live
https://aurelea.templweb.com (test-instans)

## Struktur
```
patricia-teles/
├── build_bundle.py      ← bundle-generator (komponenter + sidor)
├── content/
│   ├── text/lumo-content.json   ← sidinnehåll
│   ├── image/                   ← bilder lokalt (innan upload till WP)
│   └── _media_manifest.json     ← filename → WP {id, source_url}
├── design-system/       ← brand colors, typografi, logo, referensbilder
└── bundle.json          ← genererad output (committas inte vid behov)
```

## Bygga & pusha
Från repo-roten:
```bash
# 1. Ladda upp ev. nya bilder till WP
python3 tools/upload_media.py --dir clients/patricia-teles/content/image --manifest clients/patricia-teles/content/_media_manifest.json

# 2. Generera bundle från innehåll + manifest
python3 clients/patricia-teles/build_bundle.py

# 3. Pusha bundle till WP
python3 tools/build_all.py clients/patricia-teles/bundle.json
```

## Widgets (sätts i WP Admin → LumoKit → Inställningar)
- `site_reviews_score` = `[trustindex data-widget-id=4f20a8970e226793fc16fb72bda]`
- `site_reviews_testimonials` = `[trustindex data-widget-id=36ebfe170108680b623644e03f4]`
- `site_booking_api_key` = `5b61dbdb-ed62-4618-bca9-522e1139d592`
- `site_booking_treatment_akuttandvard` = `78` (övriga behandlingar — fyll i när IDs finns)
