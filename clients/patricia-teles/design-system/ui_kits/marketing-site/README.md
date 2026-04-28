# UI Kit — Patricia Teles Marketing Site

A clickable hi-fi recreation of the Patricia Teles website (`patriciatelesdds.com`), built modularly so components can be reused.

## Files
- `index.html` — entry; renders the homepage with click-thru navigation to other pages.
- `Header.jsx` — sticky top nav with logo, nav links, language flags, dark CTA.
- `Hero.jsx` — full-bleed hero photograph with the soft pink halo wash.
- `TreatmentGrid.jsx` — 4×3 photo card grid for treatments.
- `AboutBlock.jsx` — eyebrow + serif headline + body + ghost CTA.
- `DigitalConsultation.jsx` — pink form panel with stacked fields.
- `Reviews.jsx` — star + quote slider on a split panel.
- `PhotoStrip.jsx` — full-bleed 5-image marquee.
- `Contact.jsx` — pink panel with telephone/hours block + contact form.
- `Footer.jsx` — centered low-key footer with the wordmark + meta.
- `Page.jsx` — wires together a single page and handles client-side route switching.

## Click-thru flow
- Click any treatment card → opens the *Behandling* detail view.
- Click "BOKA TID" → opens a confirmation modal.
- Click "Om oss" → opens the about page.
- Click "Kontakt" → scrolls to contact panel.

## Source of truth
All visual decisions are derived from `inspiration/inspiration.png` (the Haga Tandläkeri reference) plus the rules in the root `README.md` — pushed sharper / more modern per the brief.
