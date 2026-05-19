# LumoKit Pattern-katalog

Denna katalog är **inte** primärkällan för komponentmönster. Det är **klientkoden** som är mönstret:

- **BASIC-baseline** → `clients/patricia-teles/build_bundle.py`
- **PREMIUM-baseline** → `clients/alvsjotandvard/build_bundle.py`

Se [CLAUDE.md → Klient-tiers](../../CLAUDE.md) för regler om hur baselines används vid ny klient.

## Vad katalogen INTE är

- Inte ett kod-bibliotek (för tidigt — bara 2 mogna klienter)
- Inte en fullständig komponent-dokumentation (det skulle drifta ur synk med koden)
- Inte en ersättning för att läsa `patricia-teles/build_bundle.py` när du startar ny klient

## Vad katalogen ÄR

Plats för **specifika anteckningar om enskilda komponenter** när det finns något icke-trivialt att förklara — t.ex. varianter, gotchas eller premium-tillägg som behöver extra dokumentation.

## Aktuella docs

- [`hero-premium.md`](hero-premium.md) — Premium-hero-varianten från alvsjotandvard. Ring-knapp + region-badge + recensions-widget + video-toggle + medaljer. **Bara för PREMIUM-tier-klienter.** Basic-klienter använder den enklare hero som ligger i patricia-teles.

## Workflow vid ny klient

```bash
# 1. Bestäm tier med användaren (default: BASIC)
# 2. Kopiera baseline
cp -r clients/patricia-teles clients/<ny-kund>      # BASIC
# eller
cp -r clients/alvsjotandvard clients/<ny-kund>      # PREMIUM (bara om köpt)

# 3. Anpassa per klient:
#    - clients/<ny-kund>/.env  (nytt WP_URL, credentials)
#    - clients/<ny-kund>/build_bundle.py  (brand-färger, fonts, content)
#    - clients/<ny-kund>/design-system/  (logotyp, design-tokens)
#    - clients/<ny-kund>/content/  (bilder, copy)

# 4. Etablera drift-baseline för nya klientens WP:
python3 tools/snapshot_live.py --client <ny-kund>

# 5. Bygg + pusha (alltid --only, alltid --dry-run först — se CLAUDE.md)
```

## Memory-regler (gäller alla komponenter)

Innan du designar/editar någon komponent, läs:

- `feedback_image_changes` — hardkoda bild-URLs i template
- `feedback_widgets_no_parent_css` — wrappers får aldrig override widget-styling
- `feedback_shared_block_content_loss` — använd make_variant() per slug, ej page_defaults
- `feedback_js_comments_in_collapse` — `/* */` i template-JS, aldrig `//`
- `feedback_contact_values_clickable` — tel/mail/maps som länkar
- `feedback_mobile_hamburger_nav` — ≤900px = hamburger
- `feedback_logo_links_to_home` — logga är `<a href="/">`
- `feedback_widget_placement` — Score (hero), Reviews (sektion), Booking (auto)
- `feedback_hero_text_readability` — hero-overlay kräver scrim
- `feedback_hero_punchlines` — hero ALLTID 3-4 USP-punchlines
- `feedback_premium_features_scope` — premium = extra kostnad, ej standardpaket
- `feedback_client_tiers` — BASIC/PREMIUM-distinktion, fråga alltid
