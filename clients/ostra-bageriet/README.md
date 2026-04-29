# Östra Bageriet

Bageri. LumoKit-byggd sajt.

## Live
<!-- URL fylls i när WP-instansen är satt -->

## Struktur
```
ostra-bageriet/
├── build_bundle.py      ← bundle-generator (komponenter + sidor)
├── content/
│   ├── text/lumo-content.json   ← sidinnehåll
│   ├── image/                   ← bilder lokalt (innan upload till WP)
│   └── _media_manifest.json     ← filename → WP {id, source_url}
├── design-system/       ← brand colors, typografi, logga, referensbilder
└── bundle.json          ← genererad output
```

## Bygga & pusha
Från repo-roten:
```bash
# 1. Ladda upp ev. nya bilder till WP
python3 tools/upload_media.py --dir clients/ostra-bageriet/content/image --manifest clients/ostra-bageriet/content/_media_manifest.json

# 2. Generera bundle från innehåll + manifest
python3 clients/ostra-bageriet/build_bundle.py

# 3. Pusha bundle till WP
python3 tools/build_all.py clients/ostra-bageriet/bundle.json
```

## Widgets
<!-- Fyll i när WP Admin → LumoKit → Inställningar är konfigurerat -->
