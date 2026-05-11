/* =============================================================
   LumoKit — Boilerplate components.jsx
   Ersätt CONFIG och TREATMENTS med klientens faktiska data.
   Alla UI-mönster (Header, Footer, Reviews, Team etc.) är klara.
   ============================================================= */

// ---------------------------------------------------------------------------
// CONFIG — fyll i per klient
// ---------------------------------------------------------------------------
const CONFIG = {
  name:    'Klientnamn AB',
  phone:   '08-XXX XX XX',
  email:   'info@klient.se',
  address: 'Gatuadress X, Stad',
  hours:   'Öppet 07:00–20:00',
  org:     '556XXX-XXXX',
  social: {
    instagram: 'https://instagram.com/',
    facebook:  'https://facebook.com/',
  },
};

// ---------------------------------------------------------------------------
// Navigation — fyll i sidor och behandlingar
// ---------------------------------------------------------------------------
const navItems = [
  {
    label: 'Behandlingar', href: '#', children: [
      // { label: 'Akuttandvård', href: 'akuttandvard.html', tag: 'AKUT SAMMA DAG' },
      // { label: 'Implantat',    href: 'implantat.html',    tag: 'SPECIALISTTEAM'  },
    ],
  },
  { label: 'Om oss',  href: 'om-oss.html' },
  { label: 'Kontakt', href: 'kontakt.html' },
];

// ---------------------------------------------------------------------------
// Behandlingskort — fyll i per klient
// ---------------------------------------------------------------------------
const TREATMENTS = [
  // { tag: 'AKUT SAMMA DAG', title: 'Akuttandvård', img: 'img/t-akut.jpg',       href: 'akuttandvard.html' },
  // { tag: 'SPECIALISTTEAM', title: 'Implantat',    img: 'img/t-implantat.jpg',  href: 'implantat.html'    },
];

// ---------------------------------------------------------------------------
// Personal — fyll i per klient
// ---------------------------------------------------------------------------
const STAFF = [
  // { name: 'Förnamn Efternamn', role: 'Titel', img: 'img/staff-fornamn.jpg' },
];

// ---------------------------------------------------------------------------
// Ikoner (Lucide-stil, stroke-baserade)
// ---------------------------------------------------------------------------
function Ico({ size = 16, strokeWidth = 1.5, style = {}, children }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round"
      strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', flexShrink: 0, ...style }}>
      {children}
    </svg>
  );
}
const IcoPhone     = (p) => <Ico {...p}><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.21 12.8a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></Ico>;
const IcoPin       = (p) => <Ico {...p}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></Ico>;
const IcoMail      = (p) => <Ico {...p}><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></Ico>;
const IcoClock     = (p) => <Ico {...p}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></Ico>;
const IcoInstagram = (p) => <Ico {...p}><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5" strokeWidth="2"/></Ico>;
const IcoFacebook  = (p) => <Ico {...p}><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></Ico>;

// ---------------------------------------------------------------------------
// NavDropdown
// ---------------------------------------------------------------------------
function NavDropdown({ item }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div style={{ position: 'relative' }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}>
      <a href={item.href} style={{
        fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500,
        letterSpacing: '0.1em', textTransform: 'uppercase',
        textDecoration: 'none', color: 'var(--ink-600)',
        display: 'flex', alignItems: 'center', gap: 4,
      }}>
        {item.label}
        {item.children && <span style={{ fontSize: 10, opacity: 0.5 }}>▾</span>}
      </a>
      {item.children && open && (
        <div style={{
          position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)',
          paddingTop: 12, zIndex: 100, minWidth: 220,
        }}>
          <div style={{
            background: 'var(--white)', border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-md)', borderRadius: 'var(--radius-md)', overflow: 'hidden',
          }}>
            {item.children.map((child, i) => (
              <a key={i} href={child.href} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 18px', textDecoration: 'none',
                color: 'var(--ink-600)', fontSize: 13, fontWeight: 400,
                borderBottom: i < item.children.length - 1 ? '1px solid var(--border)' : 'none',
                transition: 'background var(--dur-fast)',
              }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--blush-50)'}
                onMouseLeave={e => e.currentTarget.style.background = ''}>
                {child.label}
                {child.tag && (
                  <span style={{
                    fontSize: 9, fontWeight: 600, letterSpacing: '0.1em',
                    textTransform: 'uppercase', color: 'var(--blush-600)',
                    background: 'var(--blush-50)', padding: '2px 6px',
                    borderRadius: 'var(--radius-pill)',
                  }}>{child.tag}</span>
                )}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------
function Header() {
  const [menuOpen, setMenuOpen] = React.useState(false);
  return (
    <header style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50 }}>
      {/* Top strip */}
      <div style={{
        background: 'var(--ink-700)', color: 'var(--white)',
        fontSize: 11, letterSpacing: '0.06em', fontWeight: 400,
        padding: '7px var(--gutter)', display: 'flex', justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <IcoPin size={12} style={{ color: 'var(--blush-300)' }} />{CONFIG.address}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <IcoClock size={12} style={{ color: 'var(--blush-300)' }} />{CONFIG.hours}
          </span>
        </div>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <IcoPhone size={12} style={{ color: 'var(--blush-300)' }} />
          <a href={`tel:${CONFIG.phone.replace(/\s/g,'')}`} style={{ color: 'inherit', textDecoration: 'none' }}>
            {CONFIG.phone}
          </a>
        </span>
      </div>

      {/* Main nav */}
      <div style={{
        background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border)',
        padding: '0 var(--gutter)', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', height: 64,
      }}>
        <a href="index.html" style={{ textDecoration: 'none' }}>
          <img src="img/logo.png" alt={CONFIG.name} style={{ height: 36 }} />
        </a>

        {/* Desktop nav */}
        <nav style={{ display: 'flex', gap: 32, alignItems: 'center' }}>
          {navItems.map((item, i) =>
            item.children
              ? <NavDropdown key={i} item={item} />
              : <a key={i} href={item.href} style={{
                  fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500,
                  letterSpacing: '0.1em', textTransform: 'uppercase',
                  textDecoration: 'none', color: 'var(--ink-600)',
                }}>{item.label}</a>
          )}
        </nav>

        <a href="#booking" className="btn btn-primary btn-sm">Boka tid</a>
      </div>
    </header>
  );
}

// ---------------------------------------------------------------------------
// TreatmentCard + Treatments
// ---------------------------------------------------------------------------
function TreatmentCard({ t }) {
  return (
    <a href={t.href} style={{
      position: 'relative', overflow: 'hidden', display: 'block',
      aspectRatio: '3/4', textDecoration: 'none', background: 'var(--ink-700)',
    }}>
      <img src={t.img} alt={t.title} style={{
        width: '100%', height: '100%', objectFit: 'cover', opacity: 0.7,
        transition: 'transform var(--dur-slow) var(--ease-standard)',
      }} />
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(to top, rgba(20,20,20,0.85) 0%, rgba(20,20,20,0.1) 60%)',
      }} />
      {t.tag && (
        <div style={{
          position: 'absolute', top: 18, left: 18,
          fontSize: 9, fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase',
          color: 'var(--blush-200)', fontFamily: 'var(--font-sans)',
        }}>{t.tag}</div>
      )}
      <div style={{ position: 'absolute', bottom: 24, left: 24, right: 24 }}>
        <h3 style={{
          fontFamily: 'var(--font-serif)', fontWeight: 400, fontSize: 24,
          color: 'var(--white)', letterSpacing: '-0.02em', lineHeight: 1.15, margin: 0,
        }}>{t.title}</h3>
      </div>
    </a>
  );
}

function Treatments() {
  if (!TREATMENTS.length) return null;
  return (
    <section className="section" style={{ paddingTop: 'var(--space-9)' }}>
      <div className="container-wide">
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
          marginBottom: 48, paddingBottom: 32, borderBottom: '1px solid var(--border)',
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 12 }}>01 / Behandlingar</div>
            <h2>Ett komplett utbud,<br />under ett tak.</h2>
          </div>
          <div style={{ textAlign: 'right' }}>
            <p style={{ fontSize: 15, color: 'var(--ink-400)', maxWidth: '30ch', marginBottom: 16 }}>
              Från regelbunden vård till specialistbehandlingar — alltid utförda av egna specialister.
            </p>
            <a href="#" style={{
              fontFamily: 'var(--font-sans)', fontSize: 12, fontWeight: 600,
              letterSpacing: '0.14em', textTransform: 'uppercase',
              textDecoration: 'none', color: 'var(--ink-700)',
              borderBottom: '1px solid var(--ink-700)', paddingBottom: 2,
            }}>Se alla behandlingar →</a>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2 }}>
          {TREATMENTS.map((t, i) => <TreatmentCard key={i} t={t} />)}
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Reviews
// ---------------------------------------------------------------------------
function Reviews() {
  const reviews = [
    // { name: 'Anna L.',  tag: 'BEHANDLING',  text: 'Recensionstext...', time: '3 veckor sedan' },
  ];
  return (
    <section className="section" style={{ background: 'var(--bg-soft)' }}>
      <div className="container-wide">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 56 }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 12 }}>02 / Patientomdömen</div>
            <h2 style={{ maxWidth: '20ch' }}>Tusentals nöjda patienter.</h2>
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 16, padding: '20px 28px',
            background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
          }}>
            <span style={{ fontSize: 24, color: '#4285F4', fontWeight: 700 }}>G</span>
            <div>
              <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--ink-700)' }}>4.9</div>
              <div style={{ fontSize: 12, color: 'var(--ink-400)' }}>Google Reviews</div>
            </div>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24 }}>
          {reviews.map((r, i) => (
            <div key={i} style={{
              background: 'var(--white)', padding: '36px 32px',
              border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
              position: 'relative', overflow: 'hidden',
            }}>
              <div style={{
                position: 'absolute', top: -8, left: 20,
                fontSize: 120, lineHeight: 1, color: 'var(--blush-100)',
                fontFamily: 'Georgia, serif', pointerEvents: 'none', userSelect: 'none',
              }}>"</div>
              <div style={{ display: 'flex', gap: 2, marginBottom: 16, color: 'var(--star)', fontSize: 14 }}>
                {'★★★★★'}
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.7, color: 'var(--ink-500)', marginBottom: 24, position: 'relative' }}>
                {r.text}
              </p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--ink-700)' }}>{r.name}</div>
                  <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--blush-600)', marginTop: 2 }}>{r.tag}</div>
                </div>
                <div style={{ fontSize: 12, color: 'var(--ink-300)' }}>{r.time}</div>
              </div>
            </div>
          ))}
        </div>
        <div style={{ textAlign: 'center', marginTop: 48 }}>
          <a href="#" style={{
            fontFamily: 'var(--font-sans)', fontSize: 12, fontWeight: 600,
            letterSpacing: '0.14em', textTransform: 'uppercase',
            textDecoration: 'none', color: 'var(--ink-700)',
            borderBottom: '1px solid var(--ink-200)', paddingBottom: 2,
          }}>Läs alla omdömen på Google →</a>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// EmergencyBanner
// ---------------------------------------------------------------------------
function EmergencyBanner() {
  return (
    <section style={{ background: 'var(--ink-700)', padding: '40px var(--gutter)' }}>
      <div className="container-wide" style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 32,
      }}>
        <div style={{ display: 'flex', gap: 32, alignItems: 'center' }}>
          <div style={{
            fontFamily: 'var(--font-serif)', fontSize: 48, fontWeight: 300,
            color: 'var(--blush-300)', letterSpacing: '-0.03em', lineHeight: 1,
          }}>24/7</div>
          <div>
            <h3 style={{ color: 'var(--white)', fontSize: 18, marginBottom: 6 }}>
              Akut hjälp? Vi prioriterar dig samma dag.
            </h3>
            <p style={{ color: 'var(--ink-300)', fontSize: 14, margin: 0 }}>
              Ring direkt — vi strävar efter att erbjuda tid samma dag.
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexShrink: 0 }}>
          <a href={`tel:${CONFIG.phone.replace(/\s/g,'')}`} style={{
            color: 'var(--white)', fontFamily: 'var(--font-serif)', fontSize: 22,
            textDecoration: 'none', letterSpacing: '-0.01em', display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <IcoPhone size={22} style={{ color: 'var(--blush-300)' }} />
            {CONFIG.phone}
          </a>
          <a href="#booking" className="btn btn-light btn-sm">Boka akuttid →</a>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Team
// ---------------------------------------------------------------------------
function Team() {
  if (!STAFF.length) return null;
  const preview = STAFF.slice(0, 6);
  return (
    <section className="section" style={{ background: 'var(--bg-soft)' }}>
      <div className="container-wide">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 48 }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 12 }}>04 / Teamet</div>
            <h2>Erfarna och engagerade<br />— för ditt leende.</h2>
          </div>
          <div style={{ maxWidth: '30ch', textAlign: 'right' }}>
            <p style={{ fontSize: 15, color: 'var(--ink-400)', marginBottom: 16 }}>
              Legitimerade specialister som brinner för din munhälsa.
            </p>
            <a href="om-oss.html#vi-som-jobbar" style={{
              fontSize: 12, fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase',
              textDecoration: 'none', color: 'var(--ink-700)',
              borderBottom: '1px solid var(--ink-200)', paddingBottom: 2,
            }}>Se hela teamet →</a>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 16 }}>
          {preview.map((p, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{
                aspectRatio: '1', borderRadius: 'var(--radius-md)', overflow: 'hidden',
                marginBottom: 12, background: 'var(--blush-100)',
              }}>
                {p.img
                  ? <img src={p.img} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, color: 'var(--blush-300)' }}>👤</div>
                }
              </div>
              <div style={{ fontWeight: 500, fontSize: 14, color: 'var(--ink-700)' }}>{p.name}</div>
              <div style={{ fontSize: 11, color: 'var(--blush-600)', letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 500 }}>{p.role}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// CTAStrip
// ---------------------------------------------------------------------------
function CTAStrip({ title, sub }) {
  return (
    <section style={{ background: 'var(--ink-700)', padding: 'var(--space-9) var(--gutter)', textAlign: 'center' }}>
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        <h2 style={{ color: 'var(--white)', marginBottom: 16 }}>{title}</h2>
        {sub && <p style={{ color: 'var(--ink-300)', marginBottom: 32 }}>{sub}</p>}
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
          <a href="#booking" className="btn btn-light">Boka tid online</a>
          <a href={`tel:${CONFIG.phone.replace(/\s/g,'')}`} className="btn btn-ghost" style={{ color: 'var(--white)', borderColor: 'rgba(255,255,255,0.3)' }}>
            {CONFIG.phone}
          </a>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// FAQ
// ---------------------------------------------------------------------------
function FAQ({ items, title }) {
  const [open, setOpen] = React.useState(null);
  return (
    <section className="section" style={{ background: 'var(--white)' }}>
      <div className="container">
        <div style={{ marginBottom: 48 }}>
          <div className="eyebrow" style={{ marginBottom: 12 }}>Vanliga frågor</div>
          <h2 style={{ maxWidth: '28ch' }}>{title || 'Frågor och svar.'}</h2>
        </div>
        <div style={{ maxWidth: 800 }}>
          {items.map((item, i) => (
            <div key={i} style={{ borderBottom: '1px solid var(--border)' }}>
              <button onClick={() => setOpen(open === i ? null : i)} style={{
                width: '100%', textAlign: 'left', padding: '24px 0',
                background: 'none', border: 'none', cursor: 'pointer',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16,
              }}>
                <span style={{ fontWeight: 500, fontSize: 16, color: 'var(--ink-700)' }}>{item.question}</span>
                <span style={{ color: 'var(--blush-500)', fontSize: 20, flexShrink: 0 }}>{open === i ? '−' : '+'}</span>
              </button>
              {open === i && (
                <p style={{ padding: '0 0 24px', color: 'var(--ink-500)', lineHeight: 1.7, fontSize: 15 }}>
                  {item.answer}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Footer
// ---------------------------------------------------------------------------
function Footer() {
  const footerNav = {
    // 'Behandlingar': [{ label: 'Akuttandvård', href: 'akuttandvard.html' }],
    // 'Kliniken':     [{ label: 'Om oss',        href: 'om-oss.html'       }],
    // 'Patient':      [{ label: 'Boka tid',       href: '#booking'          }],
  };
  const hours = [
    { day: 'Måndag',  time: '' },
    { day: 'Tisdag',  time: '' },
    { day: 'Onsdag',  time: '' },
    { day: 'Torsdag', time: '' },
    { day: 'Fredag',  time: '' },
    { day: 'Lördag',  time: '' },
    { day: 'Söndag',  time: 'Stängt' },
  ];
  return (
    <footer style={{ background: 'var(--ink-700)', color: 'var(--white)', paddingTop: 'var(--space-9)' }}>
      <div className="container-wide">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', gap: 48, paddingBottom: 64, borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          {/* Brand */}
          <div>
            <a href="index.html">
              <img src="img/logo-white.png" alt={CONFIG.name} style={{ height: 40, marginBottom: 24 }} />
            </a>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <a href={`https://maps.google.com/?q=${encodeURIComponent(CONFIG.address)}`} target="_blank" rel="noopener"
                style={{ color: 'var(--ink-300)', textDecoration: 'none', fontSize: 13, display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <IcoPin size={14} style={{ color: 'var(--blush-300)', flexShrink: 0, marginTop: 2 }} />{CONFIG.address}
              </a>
              <a href={`tel:${CONFIG.phone.replace(/\s/g,'')}`}
                style={{ color: 'var(--ink-300)', textDecoration: 'none', fontSize: 13, display: 'flex', gap: 10, alignItems: 'center' }}>
                <IcoPhone size={14} style={{ color: 'var(--blush-300)' }} />{CONFIG.phone}
              </a>
              <a href={`mailto:${CONFIG.email}`}
                style={{ color: 'var(--ink-300)', textDecoration: 'none', fontSize: 13, display: 'flex', gap: 10, alignItems: 'center' }}>
                <IcoMail size={14} style={{ color: 'var(--blush-300)' }} />{CONFIG.email}
              </a>
            </div>
          </div>

          {/* Nav kolumner */}
          {Object.entries(footerNav).map(([heading, links]) => (
            <div key={heading}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--blush-400)', marginBottom: 20 }}>{heading}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {links.map((l, i) => (
                  <a key={i} href={l.href} style={{ color: 'var(--ink-300)', textDecoration: 'none', fontSize: 13 }}>{l.label}</a>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Öppettider + bottom bar */}
        <div style={{ padding: '32px 0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', gap: 32 }}>
            {hours.map((h, i) => (
              <div key={i}>
                <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--blush-400)', marginBottom: 4 }}>{h.day}</div>
                <div style={{ fontSize: 13, color: h.time === 'Stängt' ? 'var(--ink-400)' : 'var(--white)' }}>{h.time || '–'}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.08)', padding: '20px 0',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span style={{ fontSize: 12, color: 'var(--ink-400)' }}>
            © {new Date().getFullYear()} {CONFIG.name} · Org.nr {CONFIG.org}
          </span>
          <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
            {['Integritetspolicy', 'Cookies', 'Personalingång'].map((l, i) => (
              <a key={i} href="#" style={{ fontSize: 12, color: 'var(--ink-400)', textDecoration: 'none' }}>{l}</a>
            ))}
            <div style={{ display: 'flex', gap: 12, marginLeft: 8 }}>
              {CONFIG.social.instagram && (
                <a href={CONFIG.social.instagram} target="_blank" rel="noopener"
                  style={{ color: 'var(--ink-400)', transition: 'color var(--dur-fast)' }}
                  onMouseEnter={e => e.currentTarget.style.color = 'var(--white)'}
                  onMouseLeave={e => e.currentTarget.style.color = 'var(--ink-400)'}>
                  <IcoInstagram size={16} />
                </a>
              )}
              {CONFIG.social.facebook && (
                <a href={CONFIG.social.facebook} target="_blank" rel="noopener"
                  style={{ color: 'var(--ink-400)', transition: 'color var(--dur-fast)' }}
                  onMouseEnter={e => e.currentTarget.style.color = 'var(--white)'}
                  onMouseLeave={e => e.currentTarget.style.color = 'var(--ink-400)'}>
                  <IcoFacebook size={16} />
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
