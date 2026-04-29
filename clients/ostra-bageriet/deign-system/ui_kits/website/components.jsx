/* global React */
const { useState } = React;

/* ============================================================
   Nav — sticky cream bar with logo + links + offert CTA
   ============================================================ */
function Nav({ active = "Hem" }) {
  const items = [
    { label: "Hem",      href: "index.html" },
    { label: "Meny",     href: "meny.html" },
    { label: "Catering", href: "catering.html" },
    { label: "Om oss",   href: "om-oss.html" },
  ];
  return (
    <header className="ob-nav">
      <a href="index.html" className="ob-nav__brand">
        <img src="../../assets/logo.png" alt="Östra Bageriet" className="ob-nav__brand-logo" />
      </a>
      <nav className="ob-nav__links">
        {items.map((it) => (
          <a key={it.label} href={it.href}
             className={"ob-nav__link" + (active === it.label ? " is-active" : "")}>
            {it.label}
          </a>
        ))}
      </nav>
      <a href="catering.html" className="ob-btn ob-btn--accent ob-nav__cta">
        Be om offert
      </a>
    </header>
  );
}

/* ============================================================
   Hero — dark slab with food, eyebrow, big serif headline, CTA
   ============================================================ */
function Hero({ onSeeMenu = () => {}, onQuote = () => {} }) {
  return (
    <section className="ob-hero">
      <div className="ob-hero__bg">
        <img src="../../assets/food/meze-platter.png" alt="" />
      </div>
      <div className="ob-hero__inner">
        <span className="ob-eyebrow ob-hero__eyebrow">Östra station · sedan länge</span>
        <h1 className="ob-display-xl ob-hero__title">
          Bakat på morgonen.<br/>
          <em className="ob-hero__title-em">Serverat hela dagen.</em>
        </h1>
        <p className="ob-lede ob-hero__lede">
          Smörgåsar, sallader och bakverk med svenska rötter och orientalisk kärlek.
          Inne i Östra stations vänthall.
        </p>
        <div className="ob-hero__ctas">
          <a href="catering.html" className="ob-btn ob-btn--accent ob-btn--lg">
            Be om offert
          </a>
          <a href="meny.html" className="ob-btn ob-btn--ghost-on-dark ob-btn--lg">
            Se hela menyn
          </a>
        </div>
        <span className="ob-hand ob-hero__hand">Färskt idag — varma frallor till 09:00</span>
      </div>
    </section>
  );
}

/* ============================================================
   Section header — eyebrow + display title
   ============================================================ */
function SectionHeader({ eyebrow, title, sub, id }) {
  return (
    <header className="ob-sec-head" id={id}>
      {eyebrow && <span className="ob-eyebrow">{eyebrow}</span>}
      <h2 className="ob-display-md">{title}</h2>
      {sub && <p className="ob-lede" style={{ maxWidth: 560 }}>{sub}</p>}
    </header>
  );
}

/* ============================================================
   PageHeader — sub-page hero with copy + image
   ============================================================ */
function PageHeader({ eyebrow, title, sub, image }) {
  return (
    <header className="ob-page-header">
      <div className="ob-page-header__copy">
        {eyebrow && <span className="ob-eyebrow">{eyebrow}</span>}
        <h1 className="ob-display-lg ob-page-header__title">{title}</h1>
        {sub && <p className="ob-lede ob-page-header__sub">{sub}</p>}
      </div>
      {image && (
        <div className="ob-page-header__media">
          <img src={image} alt="" />
        </div>
      )}
    </header>
  );
}

/* ============================================================
   CategoryStrip — simple jump-nav above the menu (no sticky)
   ============================================================ */
function CategoryStrip({ cats }) {
  return (
    <nav className="ob-cats">
      {cats.map((c) => (
        <a key={c.id} href={"#cat-" + c.id} className="ob-cat">
          {c.label}
        </a>
      ))}
    </nav>
  );
}

/* ============================================================
   MenuCard — photo + title + desc + price (display only)
   ============================================================ */
function MenuCard({ item }) {
  return (
    <article className="ob-menu-card">
      {item.image && (
        <div className="ob-menu-card__img" style={{ backgroundImage: `url(${item.image})` }}>
          {item.tag && (
            <span className={"ob-menu-card__tag ob-menu-card__tag--" + (item.tagTone || "skog")}>
              {item.tag}
            </span>
          )}
        </div>
      )}
      <div className="ob-menu-card__body">
        <h3 className="ob-menu-card__title">{item.title}</h3>
        {item.desc && <p className="ob-menu-card__desc">{item.desc}</p>}
        <div className="ob-menu-card__foot">
          <div className="ob-menu-card__price">
            <span className="ob-price">{item.price}:-</span>
            {item.student && <span className="ob-menu-card__student">student {item.student}:-</span>}
          </div>
        </div>
      </div>
    </article>
  );
}

/* ============================================================
   MenuRow — compact row layout (no image) for drinks etc.
   ============================================================ */
function MenuRow({ item }) {
  return (
    <div className="ob-menu-row">
      <div className="ob-menu-row__main">
        <span className="ob-menu-row__title">{item.title}</span>
        {item.desc && <span className="ob-menu-row__desc">{item.desc}</span>}
      </div>
      <div className="ob-menu-row__price">
        <span className="ob-price">{item.price}:-</span>
        {item.student && <span className="ob-menu-row__student">/ student {item.student}:-</span>}
      </div>
    </div>
  );
}

/* ============================================================
   MenuGroup — a category section with its own anchor
   ============================================================ */
function MenuGroup({ cat, items, reverse = false }) {
  return (
    <section id={"cat-" + cat.id} className={"ob-mg" + (reverse ? " is-reverse" : "")}>
      <aside className="ob-mg__media">
        {cat.image && <img src={cat.image} alt={cat.label} className="ob-mg__img" />}
        <div className="ob-mg__media-cap">
          <span className="ob-mg__eyebrow">Kategori</span>
          <h3 className="ob-mg__title">{cat.label}</h3>
          {cat.note && <p className="ob-mg__note">{cat.note}</p>}
        </div>
      </aside>
      <div className="ob-mg__list">
        {items.map((it) => <MenuRow key={it.id} item={it} />)}
      </div>
    </section>
  );
}

/* ============================================================
   FeatureRow — image + text alternating
   ============================================================ */
function FeatureRow({ image, eyebrow, title, body, cta, ctaHref, reverse = false }) {
  return (
    <section className={"ob-feature" + (reverse ? " is-reverse" : "")}>
      <div className="ob-feature__img" style={{ backgroundImage: `url(${image})` }} />
      <div className="ob-feature__copy">
        <span className="ob-eyebrow">{eyebrow}</span>
        <h2 className="ob-display-md">{title}</h2>
        <p className="ob-lede">{body}</p>
        {cta && <a href={ctaHref || "#"} className="ob-btn ob-btn--primary">{cta}</a>}
      </div>
    </section>
  );
}

/* ============================================================
   PricingTier — three plans for catering
   ============================================================ */
function PricingTier({ tier }) {
  return (
    <div className={"ob-tier" + (tier.highlight ? " is-hl" : "")}>
      {tier.highlight && <span className="ob-tier__ribbon">Populärast</span>}
      <h3 className="ob-tier__name">{tier.name}</h3>
      <div className="ob-tier__price"><span>{tier.price}</span><small>:-/person</small></div>
      <ul className="ob-tier__list">
        {tier.items.map((it) => <li key={it}>{it}</li>)}
      </ul>
      <a href="#offert" className={"ob-btn " + (tier.highlight ? "ob-btn--accent" : "ob-btn--ghost")}>
        Be om offert
      </a>
    </div>
  );
}

/* ============================================================
   QuoteForm — catering quote request (replaces cart)
   ============================================================ */
function QuoteForm() {
  const [sent, setSent] = useState(false);
  return (
    <form id="offert" className="ob-quote-form" onSubmit={(e) => { e.preventDefault(); setSent(true); }}>
      <header className="ob-quote-form__head">
        <span className="ob-eyebrow">Catering</span>
        <h3 className="ob-display-md" style={{margin: 0}}>Berätta om ditt event</h3>
        <p className="ob-lede" style={{margin: 0, maxWidth: 460}}>
          Vi återkommer med en offert inom samma arbetsdag.
        </p>
      </header>
      {sent ? (
        <div className="ob-quote-form__sent">
          <span className="ob-hand" style={{fontSize: 28}}>Tack — vi hör av oss!</span>
          <p className="ob-body">Vi läser din förfrågan och svarar inom samma arbetsdag.</p>
        </div>
      ) : (
        <>
          <div className="ob-quote-form__grid">
            <label className="ob-field">
              <span>Namn</span>
              <input type="text" required placeholder="Anna Andersson" />
            </label>
            <label className="ob-field">
              <span>Företag (frivilligt)</span>
              <input type="text" placeholder="Östra PR-byrå" />
            </label>
            <label className="ob-field">
              <span>E-post</span>
              <input type="email" required placeholder="anna@foretag.se" />
            </label>
            <label className="ob-field">
              <span>Telefon</span>
              <input type="tel" placeholder="070-123 45 67" />
            </label>
            <label className="ob-field">
              <span>Datum</span>
              <input type="date" />
            </label>
            <label className="ob-field">
              <span>Antal personer</span>
              <input type="number" min="4" defaultValue="12" />
            </label>
            <label className="ob-field ob-field--full">
              <span>Vad tänker du dig?</span>
              <textarea rows="4" placeholder="Brickor med smörgåsar och sallader, kaffe och bakverk, allergier, leveransadress…" />
            </label>
          </div>
          <div className="ob-quote-form__foot">
            <button type="submit" className="ob-btn ob-btn--accent ob-btn--lg">Skicka förfrågan</button>
            <span className="ob-caption">Eller ring oss direkt på 08-612 50 50.</span>
          </div>
        </>
      )}
    </form>
  );
}

/* ============================================================
   Testimonial — quote, name, dish
   ============================================================ */
function Testimonial({ t }) {
  return (
    <figure className="ob-quote">
      <blockquote className="ob-quote__text">"{t.text}"</blockquote>
      <figcaption className="ob-quote__cap">
        <span className="ob-quote__name">{t.name}</span>
        <span className="ob-quote__role">{t.role}</span>
      </figcaption>
    </figure>
  );
}

/* ============================================================
   Footer — address, hours, links
   ============================================================ */
function Footer() {
  return (
    <footer className="ob-foot" id="hitta">
      <div className="ob-foot__grid">
        <div>
          <img src="../../assets/logo.png" alt="" className="ob-foot__logo" />
          <p className="ob-caption" style={{ marginTop: 12 }}>
            Östra Bageriet, café &amp; catering. Inne i Östra stations vänthall i Stockholm.
          </p>
        </div>
        <div>
          <h4 className="ob-foot__h">Hitta hit</h4>
          <p className="ob-body">Drottning Kristinas väg 1<br/>114 28 Stockholm</p>
        </div>
        <div>
          <h4 className="ob-foot__h">Öppettider</h4>
          <p className="ob-body">Mån–fre 06:30–19:00<br/>Lör 09:00–17:00<br/>Sön stängt</p>
        </div>
        <div>
          <h4 className="ob-foot__h">Kontakt</h4>
          <p className="ob-body">08-612 50 50<br/>SMS 073-99 38 704<br/>Fkuorie@hotmail.com</p>
        </div>
      </div>
      <div className="ob-foot__bottom">
        <span className="ob-caption">© Östra Bageriet</span>
        <span className="ob-caption">Bakat med kärlek på Östra station.</span>
      </div>
    </footer>
  );
}

Object.assign(window, {
  Nav, Hero, SectionHeader, PageHeader, CategoryStrip, MenuCard, MenuRow, MenuGroup,
  FeatureRow, PricingTier, QuoteForm, Testimonial, Footer,
});
