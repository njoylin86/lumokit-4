# Östra Bageriet · Website UI kit

A high-fidelity recreation of the marketing + ordering website for Östra Bageriet, structured as small, reusable JSX components.

## Files

- `index.html` — interactive demo of the homepage. Loads tokens, components, and renders an `<App />` with a working menu category filter and add-to-cart flow.
- `components.jsx` — Nav, Hero, SectionHeader, CategoryStrip, MenuCard, FeatureRow, PricingTier, Testimonial, Cart, Footer.
- `styles.css` — UI-kit styling that builds on `colors_and_type.css` tokens.

## What works (and what's a mock)

- ✅ Sticky nav with active route highlight.
- ✅ Category filter (Bröd, Sallader, Wraps, Drycker, Bakverk).
- ✅ Add-to-cart with stepper, sticky cart drawer, total in `:-` with tabular numerals.
- ✅ Catering pricing tiers + testimonials.
- ⚠️ Search, payment, login — not implemented; visual only.
- ⚠️ Map footer from the original reference is replaced with an address block (we have no real map data).

## Visual references used

- Reference layout: `scraps/webdesign.webp` (we kept the structure: hero → category strip → menu grid → catering tiers → quotes → footer; replaced its dark/orange palette with cream/Skog/Saffran).
- Imagery: `assets/food/*` — real photos from Östra Bageriet's source pack.
- Logo: `assets/logo.png`.
