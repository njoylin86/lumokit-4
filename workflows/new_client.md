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
