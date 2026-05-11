// components.jsx — Älvsjö Tandvård
// All sections except hero (which has 3 variants in hero.jsx)

const { useState, useEffect, useRef } = React;

// ─────────────────────────────────────────────────────────────────────────────
// Header — sticky, white, dense for big-clinic feel
// ─────────────────────────────────────────────────────────────────────────────
function Header() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navItems = [
    {
      label: 'Behandlingar', children: [
        { label: 'Akuttandvård', href: 'Akuttandvård.html' },
        { label: 'Implantat', href: 'Implantat.html' },
        { label: 'Karies / Hål i tanden', href: 'Karies.html' },
        { label: 'Tandblekning', href: 'Tandblekning.html' },
        { label: 'Tandfasader / Veneers', href: 'Tandfasader.html' },
        { label: 'Tandreglering / Invisalign', href: 'Tandreglering.html' },
        { label: 'Tandsten / Tandhygienist', href: 'Tandsten.html' },
        { label: 'Tandvårdsrädsla', href: 'Tandvårdsrädsla.html' },
        { label: 'Tillhör du riskgrupp?', href: 'Riskgrupp.html' },
      ],
    },
    {
      label: 'Om oss', href: 'Om oss.html', children: [
        { label: 'Om kliniken', href: 'Om oss.html' },
        { label: 'Vi som jobbar', href: 'Om oss.html#vi-som-jobbar' },
        { label: 'Organisation', href: 'Om oss.html#organisation' },
        { label: 'Hitta till oss', href: 'Om oss.html#hitta-till-oss' },
        { label: 'Arbeta med oss', href: 'Om oss.html#arbeta-med-oss' },
        { label: 'Hjälp oss bli bäst', href: 'Om oss.html#hjalp-oss-bli-bast' },
      ],
    },
    { label: 'Barnspecialist', href: 'Barnspecialist.html' },
    { label: 'Kontakt', href: 'Kontakt.html' },
  ];

  return (
    <header style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'var(--white)',
      borderBottom: scrolled ? '1px solid var(--border)' : '1px solid transparent',
      transition: 'border-color 240ms var(--ease-standard)',
    }}>
      {/* Top strip */}
      <div style={{
        background: 'var(--ink-700)', color: 'var(--white)',
        fontSize: 12, letterSpacing: '0.04em',
      }}>
        <div className="container-wide" style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          height: 38, fontFamily: 'var(--font-sans)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 28, opacity: 0.85 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <IcoPin size={13} style={{ opacity: 0.7 }} />
              Prästgårdsgränd 4, Älvsjö · 2 min från pendeln
            </span>
            <span style={{ opacity: 0.4 }}>·</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <IcoClock size={13} style={{ opacity: 0.7 }} />
              Öppet idag 07:00 – 20:00
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24, opacity: 0.9 }}>
            <a href="#" style={{ color: 'var(--white)', textDecoration: 'none', textDecorationColor: 'transparent' }}>Mina tider</a>
            <span style={{ opacity: 0.4 }}>·</span>
            <a href="tel:+46812854555" style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--white)', textDecoration: 'none', textDecorationColor: 'transparent' }}>
              <IcoPhone size={13} style={{ opacity: 0.7 }} />
              08 — 12 85 45 55
            </a>
          </div>
        </div>
      </div>

      {/* Main nav */}
      <div className="container-wide" style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: 78,
      }}>
        <a href="index.html" style={{
          display: 'flex', alignItems: 'center', gap: 14,
          textDecoration: 'none', textDecorationColor: 'transparent',
          color: 'var(--ink-700)',
        }}>
          <img src="img/logo.png" alt="Älvsjö Tandvård" style={{ height: 52, width: 'auto', display: 'block' }} />
        </a>
        <nav style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
          {navItems.map((item, i) => item.children ? (
            <NavDropdown key={i} item={item} />
          ) : (
            <a key={i} href={item.href} style={{
              fontSize: 14, fontWeight: 500, color: 'var(--ink-600)',
              textDecoration: 'none', textDecorationColor: 'transparent',
              transition: 'color 140ms var(--ease-standard)',
            }}
            onMouseEnter={(e) => e.target.style.color = 'var(--sage-600)'}
            onMouseLeave={(e) => e.target.style.color = 'var(--ink-600)'}
            >{item.label}</a>
          ))}
        </nav>
        <a href="#booking" className="btn btn-primary btn-sm" style={{ letterSpacing: '0.14em' }}>
          Boka tid
        </a>
      </div>
    </header>
  );
}

function NavDropdown({ item }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      style={{ position: 'relative' }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button style={{
        background: 'transparent', border: 'none', cursor: 'pointer',
        fontFamily: 'var(--font-sans)', padding: 0,
        display: 'inline-flex', alignItems: 'center', gap: 6,
        fontSize: 14, fontWeight: 500,
        color: open ? 'var(--sage-600)' : 'var(--ink-600)',
        transition: 'color 140ms var(--ease-standard)',
      }}>
        {item.label}
        <span style={{
          fontSize: 9, transform: open ? 'rotate(180deg)' : 'rotate(0)',
          transition: 'transform 180ms var(--ease-standard)',
        }}>▼</span>
      </button>
      {open && (
        <div style={{
          position: 'absolute', top: '100%', right: 0,
          paddingTop: 14,
        }}>
          <div style={{
            minWidth: 240, background: 'var(--white)',
            border: '1px solid var(--border)',
            boxShadow: '0 16px 40px rgba(0,0,0,0.08)',
            padding: '12px 0',
          }}>
            {item.children.map((c, i) => (
              <a key={i} href={c.href} style={{
                display: 'block', padding: '10px 20px',
                fontSize: 14, fontWeight: 500, color: 'var(--ink-600)',
                textDecoration: 'none', textDecorationColor: 'transparent',
                transition: 'background 140ms var(--ease-standard), color 140ms var(--ease-standard)',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--cream)'; e.currentTarget.style.color = 'var(--sage-600)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--ink-600)'; }}
              >{c.label}</a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Icons — inline SVG, stroke-based (Lucide style)
// ─────────────────────────────────────────────────────────────────────────────
function Ico({ size = 16, strokeWidth = 1.5, style = {}, children }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={strokeWidth}
      strokeLinecap="round" strokeLinejoin="round"
      style={{ display: 'inline-block', flexShrink: 0, verticalAlign: 'middle', ...style }}>
      {children}
    </svg>
  );
}
const IcoPhone = (p) => <Ico {...p}><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></Ico>;
const IcoPin  = (p) => <Ico {...p}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></Ico>;
const IcoMail = (p) => <Ico {...p}><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></Ico>;
const IcoClock = (p) => <Ico {...p}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></Ico>;
const IcoInstagram = (p) => <Ico {...p}><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5" strokeWidth="2"/></Ico>;
const IcoFacebook = (p) => <Ico {...p}><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></Ico>;

// ─────────────────────────────────────────────────────────────────────────────
// Treatments — large grid emphasizing breadth
// ─────────────────────────────────────────────────────────────────────────────
const TREATMENTS = [
  { id: 't1', name: 'Akuttandvård', desc: 'Snabb hjälp samma dag vid värk eller skada.', img: 'img/t-akut.jpg', count: 'Tider samma dag', badge: true, href: 'Akuttandvård.html' },
  { id: 't2', name: 'Implantat', desc: 'Permanenta ersättningar — planeras med 3D/CBCT.', img: 'img/t-implantat.jpg', count: 'Specialistteam', href: 'Implantat.html' },
  { id: 't3', name: 'Karies / Hål i tanden', desc: 'Skonsamma lagningar med moderna kompositmaterial.', img: 'img/t-karies.jpg', count: 'Allmäntandvård', href: 'Karies.html' },
  { id: 't4', name: 'Tandblekning', desc: 'Professionell blekning på klinik eller hemma.', img: 'img/t-tandblekning.jpg', count: 'Klinik & hemma', href: 'Tandblekning.html' },
  { id: 't5', name: 'Tandfasader / Veneers', desc: 'Estetiska skal för ett harmoniskt leende.', img: 'img/t-tandfasader.jpg', count: 'Estetisk tandvård', href: 'Tandfasader.html' },
  { id: 't6', name: 'Tandreglering', desc: 'Osynlig tandreglering med Invisalign-skenor.', img: 'img/t-tandreglering.jpg', count: 'Invisalign', href: 'Tandreglering.html' },
  { id: 't7', name: 'Tandsten / Tandhygienist', desc: 'Förebyggande tandhygien för en frisk munhälsa.', img: 'img/t-tandsten.jpg', count: 'Förebyggande vård', href: 'Tandsten.html' },
  { id: 't8', name: 'Tandvårdsrädsla', desc: 'Extra tid och stegvis tillvänjning hos vårt team.', img: 'img/t-tandradsla.jpg', count: 'Lugnande vård', href: 'Tandvårdsrädsla.html' },
];

function Treatments() {
  return (
    <section id="treatments" className="section" style={{ background: 'var(--white)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'end',
          gap: 32, marginBottom: 56, paddingBottom: 32,
          borderBottom: '1px solid var(--border)',
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>01 / Behandlingar</div>
            <h2 style={{ maxWidth: '20ch' }}>Ett komplett utbud, under ett tak.</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
            <p className="small" style={{ maxWidth: '32ch', textAlign: 'right', margin: 0 }}>
              Från regelbunden tandvård till specialistbehandlingar — alltid utförda på plats av våra egna tandläkare.
            </p>
            <a href="#" style={{
              fontSize: 13, fontWeight: 500, letterSpacing: '0.08em',
              textTransform: 'uppercase', textDecoration: 'none', textDecorationColor: 'transparent',
              color: 'var(--ink-700)',
              borderBottom: '1px solid var(--ink-700)', paddingBottom: 2, marginTop: 8,
            }}>Se alla behandlingar →</a>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 1,
          background: 'var(--border)',
          border: '1px solid var(--border)',
        }}>
          {TREATMENTS.map(t => (
            <TreatmentCard key={t.id} t={t} />
          ))}
        </div>
      </div>
    </section>
  );
}

function TreatmentCard({ t }) {
  const [hover, setHover] = useState(false);
  return (
    <a href={t.href} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        position: 'relative', aspectRatio: '1 / 1.05',
        background: 'var(--white)',
        textDecoration: 'none', textDecorationColor: 'transparent',
        overflow: 'hidden',
        display: 'flex', flexDirection: 'column',
        transition: 'background 240ms var(--ease-standard)',
      }}>
      <div style={{
        position: 'absolute', inset: 0,
        background: `url(${t.img}) center/cover no-repeat`,
        opacity: hover ? 1 : 0.92,
        filter: hover ? 'none' : 'saturate(0.85)',
        transition: 'all 480ms var(--ease-standard)',
        transform: hover ? 'scale(1.03)' : 'scale(1)',
      }} />
      <div style={{
        position: 'absolute', inset: 0,
        background: hover
          ? 'linear-gradient(180deg, rgba(20,20,18,0.05) 0%, rgba(20,20,18,0.75) 100%)'
          : 'linear-gradient(180deg, rgba(20,20,18,0.15) 0%, rgba(20,20,18,0.55) 100%)',
        transition: 'background 480ms var(--ease-standard)',
      }} />
      {t.badge && (
        <div style={{
          position: 'absolute', top: 16, left: 16, zIndex: 2,
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 12px',
          background: 'var(--danger)', color: 'var(--white)',
          fontSize: 10, fontWeight: 600, letterSpacing: '0.14em',
          textTransform: 'uppercase',
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--white)' }} />
          Öppet nu
        </div>
      )}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 2,
        padding: 28, color: 'var(--white)',
        display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      }}>
        <div style={{
          fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
          letterSpacing: '0.22em', textTransform: 'uppercase',
          opacity: 0.85,
        }}>{t.count}</div>
        <div>
          <h3 style={{
            fontFamily: 'var(--font-serif)', fontWeight: 400,
            fontSize: 28, lineHeight: 1.1, letterSpacing: '-0.02em',
            color: 'var(--white)', marginBottom: 8,
          }}>{t.name}</h3>
          <div style={{
            maxHeight: hover ? 80 : 0, overflow: 'hidden',
            transition: 'max-height 480ms var(--ease-standard), opacity 240ms var(--ease-standard)',
            opacity: hover ? 1 : 0,
          }}>
            <p style={{ fontSize: 13, lineHeight: 1.5, color: 'rgba(255,255,255,0.85)', maxWidth: 'none' }}>
              {t.desc}
            </p>
            <div style={{
              marginTop: 14, fontSize: 11, fontWeight: 600,
              letterSpacing: '0.14em', textTransform: 'uppercase',
            }}>Läs mer →</div>
          </div>
        </div>
      </div>
    </a>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Reviews — early, big-feel social proof
// ─────────────────────────────────────────────────────────────────────────────
const REVIEWS = [
  { name: 'Anna L.', date: '2 veckor sedan', stars: 5, text: 'Mycket professionell klinik. Tydlig information, kort väntetid och otroligt fint resultat efter min implantatbehandling. Jag har redan rekommenderat dem till hela min familj.', tag: 'Tandimplantat' },
  { name: 'Markus S.', date: '1 månad sedan', stars: 5, text: 'Den modernaste kliniken jag varit på. 3D-skanning, digital uppföljning och en personal som faktiskt lyssnar. Sköts som ett sjukhus men känns personligt.', tag: 'Basundersökning' },
  { name: 'Linnea B.', date: '3 veckor sedan', stars: 5, text: 'Som tandvårdsrädd har jag varit hos många kliniker. Här blev jag bemött med ett tålamod jag aldrig upplevt tidigare. Tar mig tid att förklara varje steg.', tag: 'Tandvårdsrädsla' },
  { name: 'Johan K.', date: '5 dagar sedan', stars: 5, text: 'Ringde 08:30 med akut värk, fick tid 10:00 samma dag. Snabbt, professionellt och utan att kännas stressigt. Tack.', tag: 'Akuttandvård' },
];

function Reviews() {
  return (
    <section className="section" style={{ background: 'var(--sage-50)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 80,
          alignItems: 'end', marginBottom: 64,
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>02 / Patientomdömen</div>
            <h2 style={{ maxWidth: '15ch' }}>
              <span className="italic">Tusentals</span> nöjda patienter i Älvsjö.
            </h2>
          </div>
          <div style={{
            background: 'var(--white)', padding: 28,
            display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 20,
            alignItems: 'center',
            border: '1px solid var(--border)',
          }}>
            <div style={{
              width: 56, height: 56,
              background: 'var(--white)',
              border: '1px solid var(--border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'var(--font-sans)', fontSize: 26, fontWeight: 500,
              color: '#4285F4',
            }}>G</div>
            <div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 4 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: 36, fontWeight: 400, color: 'var(--ink-700)', lineHeight: 1 }}>4,9</span>
                <span className="stars">★★★★★</span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--fg-muted)' }}>Google Reviews · 2 100+ omdömen</div>
            </div>
          </div>
        </div>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24,
        }}>
          {REVIEWS.map((r, i) => (
            <article key={i} style={{
              background: 'var(--white)',
              padding: 32,
              display: 'flex', flexDirection: 'column', gap: 16,
              border: '1px solid var(--border)',
              minHeight: 320,
              position: 'relative', overflow: 'hidden',
            }}>
              {/* Decorative quote mark */}
              <div style={{
                position: 'absolute', top: 16, right: 20,
                fontFamily: 'Georgia, serif', fontSize: 120, lineHeight: 1,
                color: 'var(--sage-100)', userSelect: 'none', pointerEvents: 'none',
              }}>"</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span className="stars" style={{ fontSize: 14 }}>★★★★★</span>
                <span className="tiny" style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--sage-600)' }}>{r.tag}</span>
              </div>
              <p style={{ fontFamily: 'var(--font-serif)', fontSize: 18, lineHeight: 1.5, color: 'var(--ink-700)', fontWeight: 400, letterSpacing: '-0.01em', flex: 1, position: 'relative', zIndex: 1 }}>
                "{r.text}"
              </p>
              <div style={{ paddingTop: 16, borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink-700)' }}>{r.name}</span>
                <span className="tiny">{r.date}</span>
              </div>
            </article>
          ))}
        </div>

        <div style={{ marginTop: 48, textAlign: 'center' }}>
          <a href="#" style={{
            fontSize: 13, fontWeight: 500, letterSpacing: '0.14em',
            textTransform: 'uppercase', color: 'var(--ink-700)',
            textDecoration: 'none', textDecorationColor: 'transparent',
            borderBottom: '1px solid var(--ink-700)', paddingBottom: 4,
          }}>Läs alla omdömen på Google →</a>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Om kliniken — stats + story
// ─────────────────────────────────────────────────────────────────────────────
function About() {
  const stats = [
    { value: '16+', label: 'Tandläkare\n& hygienister' },
    { value: '07–20', label: 'Öppet alla\nvardagar' },
    { value: '2 min', label: 'Från pendel-\ntågsstationen' },
    { value: '0–23', label: 'Pedodonti\nspecialist' },
  ];

  return (
    <section className="section" style={{ background: 'var(--white)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1.1fr',
          gap: 96, alignItems: 'start',
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>03 / Om kliniken</div>
            <h2 style={{ marginBottom: 32 }}>
              Trygghet och kvalitet för ditt leende.
            </h2>
            <p className="lead" style={{ marginBottom: 24, maxWidth: '44ch' }}>
              Vår nyrenoverade och luftiga klinik på Prästgårdsgränd 4 erbjuder en lugn, modern miljö där vi tar hand om dig och din familj med professionalism och värme.
            </p>
            <p style={{ marginBottom: 32, maxWidth: '52ch', color: 'var(--ink-500)' }}>
              För de yngre familjemedlemmarna har vi även <strong>Älvsjö Pedodonti</strong>, en specialistenhet för barn och unga upp till 23 år. Vi är anslutna till Försäkringskassan och erbjuder räntefri delbetalning.
            </p>
            <a href="Om oss.html" className="btn btn-ghost">Läs mer om oss</a>
          </div>

          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1,
            background: 'var(--border)',
            border: '1px solid var(--border)',
          }}>
            {stats.map((s, i) => (
              <div key={i} style={{
                background: 'var(--white)', padding: '48px 32px',
                aspectRatio: '1.2 / 1',
                display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
              }}>
                <div style={{
                  fontFamily: 'var(--font-serif)', fontWeight: 300,
                  fontSize: 'clamp(72px, 7vw, 120px)', lineHeight: 0.9,
                  letterSpacing: '-0.04em', color: 'var(--ink-700)',
                }}>{s.value}</div>
                <div style={{
                  fontSize: 12, fontWeight: 500, letterSpacing: '0.22em',
                  textTransform: 'uppercase', color: 'var(--sage-600)',
                  whiteSpace: 'pre-line', lineHeight: 1.5,
                }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Emergency banner
// ─────────────────────────────────────────────────────────────────────────────
function EmergencyBanner() {
  return (
    <section style={{
      background: 'var(--ink-700)', color: 'var(--white)',
      padding: 'var(--space-9) 0',
      position: 'relative', overflow: 'hidden',
    }} id="emergency">
      <div className="container-wide" style={{
        display: 'grid', gridTemplateColumns: 'auto 1fr auto',
        gap: 56, alignItems: 'center',
      }}>
        <div style={{
          display: 'flex', flexDirection: 'column', gap: 4,
          paddingRight: 56, borderRight: '1px solid rgba(255,255,255,0.15)',
        }}>
          <span style={{
            fontFamily: 'var(--font-sans)', fontSize: 10, fontWeight: 500,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: 'var(--sage-300)',
          }}>Akut</span>
          <span style={{
            fontFamily: 'var(--font-serif)', fontSize: 64, fontWeight: 300,
            letterSpacing: '-0.04em', lineHeight: 1, color: 'var(--white)',
          }}>24/7</span>
        </div>
        <div>
          <h2 style={{
            color: 'var(--white)', marginBottom: 12,
            fontSize: 'clamp(28px, 2.4vw, 40px)',
          }}>
            Akut tandvärk? Vi prioriterar dig samma dag.
          </h2>
          <p style={{
            color: 'rgba(255,255,255,0.7)', maxWidth: '52ch',
            margin: 0, fontSize: 16,
          }}>
            Ring oss direkt på <strong style={{color:'var(--white)'}}>08-12 85 45 55</strong> om du behöver omedelbar hjälp. Vi prioriterar akuta patienter och strävar efter att erbjuda dig en tid samma dag.
          </p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minWidth: 220 }}>
          <a href="tel:+46812854555" style={{
            display: 'flex', alignItems: 'center', gap: 12,
            fontFamily: 'var(--font-serif)', fontSize: 28, fontWeight: 400,
            color: 'var(--white)', textDecoration: 'none', textDecorationColor: 'transparent',
            letterSpacing: '-0.01em',
          }}>
            <IcoPhone size={22} style={{ opacity: 0.7, flexShrink: 0 }} />
            08 — 12 85 45 55
          </a>
          <a href="#booking" className="btn btn-light btn-sm" style={{ width: 'fit-content' }}>Boka akuttid →</a>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Team — many faces grid
// ─────────────────────────────────────────────────────────────────────────────
const TEAM = [
  { name: 'Adel',       role: 'VD · Tandhygienist',      img: 'img/staff-adel.jpg' },
  { name: 'Aslan',      role: 'Tandläkare',              img: 'img/staff-aslan.jpg' },
  { name: 'Mike',       role: 'Tandläkare',              img: 'img/staff-mike.jpg' },
  { name: 'Ghiyas',     role: 'Tandläkare',              img: 'img/staff-ghiyas.jpg' },
  { name: 'Airo',       role: 'Tandläkare',              img: 'img/staff-airo.jpg' },
  { name: 'Bindu',      role: 'Tandläkare',              img: 'img/staff-bindu.jpg' },
  { name: 'Ashfa',      role: 'Tandläkare',              img: 'img/staff-ashfa.jpg' },
  { name: 'Aleksandra', role: 'Tandläkare',              img: 'img/staff-aleksandra.jpg' },
  { name: 'Arezoo',     role: 'Tandläkare',              img: 'img/staff-arezoo.jpg' },
  { name: 'Loren',      role: 'Tandläkare',              img: 'img/staff-loren.jpg' },
  { name: 'Marcel',     role: 'Tandläkare',              img: 'img/staff-marcel.jpg' },
  { name: 'Ahmed',      role: 'Tandhygienist',           img: 'img/staff-ahmed.jpg' },
  { name: 'Sibel',      role: 'Reception · Tandhygienist', img: 'img/staff-sibel.jpg' },
  { name: 'Badeel',     role: 'Tandsköterska',           img: 'img/staff-badeel.jpg' },
  { name: 'Evin',       role: 'Tandsköterska',           img: 'img/staff-evin.jpg' },
  { name: 'Erika',      role: 'Tandsköterska',           img: 'img/staff-erika.jpg' },
  { name: 'Maxim',      role: 'Ekonomi',                 img: 'img/staff-maxim.jpg' },
];

function Team() {
  return (
    <section id="team" className="section" style={{ background: 'var(--cream)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr', alignItems: 'end',
          gap: 48, marginBottom: 64, paddingBottom: 32,
          borderBottom: '1px solid var(--border)',
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>04 / Teamet</div>
            <h2 style={{ maxWidth: '16ch' }}>Erfarna och engagerade — för ditt leende.</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 16 }}>
            <p style={{ maxWidth: '40ch', margin: 0, textAlign: 'right', fontSize: 15 }}>
              Tandläkare, tandhygienister och tandsköterskor som brinner för din munhälsa. Vi vidareutbildar oss kontinuerligt och möter dig alltid med tid, lugn och förståelse.
            </p>
            <a href="#" className="btn btn-ghost btn-sm">Se hela teamet</a>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(6, 1fr)',
          gap: 24,
        }}>
          {TEAM.map((p, i) => (
            <article key={i} style={{
              display: 'flex', flexDirection: 'column', gap: 14,
            }}>
              <div style={{
                aspectRatio: '4 / 5',
                background: `url(${p.img}) center/cover no-repeat`,
                filter: 'saturate(0.9)',
              }} />
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink-700)', marginBottom: 4, lineHeight: 1.3 }}>{p.name}</div>
                <div style={{ fontSize: 11, color: 'var(--sage-600)', letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 500 }}>{p.role}</div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Photo tour — clinic facilities
// ─────────────────────────────────────────────────────────────────────────────
const TOUR = [
  { img: 'img/reception-plexiglasskarm.jpg', label: 'Receptionen', size: 'large' },
  { img: 'img/bla-behandlingsstol-rontgenarm.jpg', label: 'Behandlingsrum 04', size: 'small' },
  { img: 'img/intraoral-rontgen.jpg', label: 'Röntgenavdelning', size: 'small' },
  { img: 'img/tandlakarlupp-rosa-stol.jpg', label: 'Sterilcentral', size: 'medium' },
  { img: 'img/rosa-behandlingsstol-instrument.jpg', label: 'Operationsrum', size: 'medium' },
];

function PhotoTour() {
  return (
    <section className="section" style={{ background: 'var(--white)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'end',
          gap: 48, marginBottom: 56,
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>05 / Klinikens lokaler</div>
            <h2 style={{ maxWidth: '18ch' }}>14 behandlingsrum. 1 200 m² över två våningar.</h2>
          </div>
          <a href="#" className="btn btn-ghost btn-sm">Virtuell rundtur →</a>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gridAutoRows: '180px',
          gap: 16,
        }}>
          <PhotoTile img={TOUR[0].img} label={TOUR[0].label} cols="span 7" rows="span 3" />
          <PhotoTile img={TOUR[1].img} label={TOUR[1].label} cols="span 5" rows="span 2" />
          <PhotoTile img={TOUR[2].img} label={TOUR[2].label} cols="span 5" rows="span 1" />
          <PhotoTile img={TOUR[3].img} label={TOUR[3].label} cols="span 5" rows="span 2" />
          <PhotoTile img={TOUR[4].img} label={TOUR[4].label} cols="span 7" rows="span 2" />
        </div>
      </div>
    </section>
  );
}

function PhotoTile({ img, label, cols, rows }) {
  const [hover, setHover] = useState(false);
  return (
    <div onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        gridColumn: cols, gridRow: rows,
        position: 'relative', overflow: 'hidden',
        background: 'var(--ink-100)',
        cursor: 'pointer',
      }}>
      <div style={{
        position: 'absolute', inset: 0,
        background: `url(${img}) center/cover no-repeat`,
        filter: 'saturate(0.85)',
        transform: hover ? 'scale(1.04)' : 'scale(1)',
        transition: 'transform 600ms var(--ease-standard)',
      }} />
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(180deg, rgba(20,20,18,0) 50%, rgba(20,20,18,0.55) 100%)',
      }} />
      <div style={{
        position: 'absolute', left: 20, bottom: 18, color: 'var(--white)',
        fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
        letterSpacing: '0.22em', textTransform: 'uppercase',
      }}>{label}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Booking — calendar above footer
// ─────────────────────────────────────────────────────────────────────────────
function Booking() {
  const today = new Date(2026, 4, 11); // May 11
  const [selectedDate, setSelectedDate] = useState(13); // Wed
  const [selectedTime, setSelectedTime] = useState('14:30');
  const [selectedTreatment, setSelectedTreatment] = useState('Basundersökning');

  const dayLabels = ['Mån', 'Tis', 'Ons', 'Tor', 'Fre', 'Lör', 'Sön'];
  const days = [
    { d: 11, dl: 'Mån', avail: 0 },
    { d: 12, dl: 'Tis', avail: 3 },
    { d: 13, dl: 'Ons', avail: 8 },
    { d: 14, dl: 'Tor', avail: 6 },
    { d: 15, dl: 'Fre', avail: 12 },
    { d: 16, dl: 'Lör', avail: 4 },
    { d: 17, dl: 'Sön', avail: 0, closed: true },
    { d: 18, dl: 'Mån', avail: 9 },
    { d: 19, dl: 'Tis', avail: 5 },
    { d: 20, dl: 'Ons', avail: 11 },
    { d: 21, dl: 'Tor', avail: 7 },
    { d: 22, dl: 'Fre', avail: 8 },
    { d: 23, dl: 'Lör', avail: 6 },
    { d: 24, dl: 'Sön', avail: 0, closed: true },
  ];
  const times = ['08:00', '08:30', '09:00', '10:30', '11:00', '13:00', '13:30', '14:00', '14:30', '15:30', '16:00', '17:30'];
  const treatments = ['Basundersökning', 'Tandhygienist', 'Akut konsultation', 'Implantatkonsultation', 'Invisalign-utvärdering'];

  return (
    <section id="booking" className="section" style={{ background: 'var(--sage-50)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: 64, alignItems: 'start',
        }}>
          {/* Left rail */}
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>06 / Boka tid</div>
            <h2 style={{ marginBottom: 24 }}>
              Hitta en tid<br/>som passar dig.
            </h2>
            <p style={{ marginBottom: 32, color: 'var(--ink-500)', maxWidth: '38ch' }}>
              Boka direkt online — du får bekräftelse via SMS. Behöver du hjälp att välja behandling? Ring oss eller chatta med en sjuksköterska.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--border)', border: '1px solid var(--border)' }}>
              <BookingStat label="Nästa lediga akuttid" value="Idag 16:45" emphasis />
              <BookingStat label="Genomsnittlig väntetid" value="2 dagar" />
              <BookingStat label="Lediga tider denna vecka" value="34" />
            </div>

            <div style={{ marginTop: 32, paddingTop: 24, borderTop: '1px solid var(--border)' }}>
              <div className="tiny" style={{ marginBottom: 8 }}>Föredrar du att ringa?</div>
              <a href="tel:+46812854555" style={{
                fontFamily: 'var(--font-serif)', fontSize: 28, fontWeight: 400,
                color: 'var(--ink-700)', textDecoration: 'none', textDecorationColor: 'transparent',
                letterSpacing: '-0.01em',
              }}>08 — 12 85 45 55</a>
            </div>
          </div>

          {/* Booking panel */}
          <div style={{
            background: 'var(--white)',
            border: '1px solid var(--border)',
            padding: 48,
          }}>
            <div style={{
              display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16,
              marginBottom: 32, paddingBottom: 24,
              borderBottom: '1px solid var(--border)',
            }}>
              <FieldSelect label="Behandling" value={selectedTreatment} options={treatments} onChange={setSelectedTreatment} />
              <FieldSelect label="Tandläkare" value="Valfri" options={['Valfri', 'Adel Bashir', 'Aslan Karimi', 'Mike Saliba', 'Airo Nasser']} onChange={() => {}} />
            </div>

            {/* Calendar */}
            <div style={{ marginBottom: 32 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div className="eyebrow">Maj 2026</div>
                <div style={{ display: 'flex', gap: 4 }}>
                  <CalArrow dir="left" />
                  <CalArrow dir="right" />
                </div>
              </div>

              <div style={{
                display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 6,
              }}>
                {days.map((d, i) => {
                  const isSel = d.d === selectedDate;
                  const disabled = d.closed || d.avail === 0;
                  return (
                    <button key={i}
                      disabled={disabled}
                      onClick={() => !disabled && setSelectedDate(d.d)}
                      style={{
                        display: 'flex', flexDirection: 'column', gap: 4,
                        padding: '14px 6px',
                        background: isSel ? 'var(--ink-700)' : 'var(--white)',
                        color: isSel ? 'var(--white)' : disabled ? 'var(--fg-subtle)' : 'var(--ink-700)',
                        border: '1px solid',
                        borderColor: isSel ? 'var(--ink-700)' : 'var(--border)',
                        cursor: disabled ? 'not-allowed' : 'pointer',
                        transition: 'all 140ms var(--ease-standard)',
                        opacity: disabled ? 0.5 : 1,
                      }}>
                      <span style={{ fontSize: 10, fontWeight: 500, letterSpacing: '0.14em', textTransform: 'uppercase', opacity: 0.7 }}>{d.dl}</span>
                      <span style={{ fontFamily: 'var(--font-serif)', fontSize: 24, fontWeight: 400, lineHeight: 1 }}>{d.d}</span>
                      <span style={{ fontSize: 10, letterSpacing: '0.04em', marginTop: 2, opacity: isSel ? 0.7 : 0.5 }}>
                        {d.closed ? 'Stängt' : d.avail === 0 ? 'Fullt' : `${d.avail} tider`}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Time slots */}
            <div style={{ marginBottom: 32 }}>
              <div className="eyebrow" style={{ marginBottom: 14 }}>Lediga tider · Onsdag 13 maj</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 6 }}>
                {times.map(t => {
                  const isSel = t === selectedTime;
                  return (
                    <button key={t}
                      onClick={() => setSelectedTime(t)}
                      style={{
                        padding: '12px 8px',
                        background: isSel ? 'var(--sage-600)' : 'var(--white)',
                        color: isSel ? 'var(--white)' : 'var(--ink-600)',
                        border: '1px solid',
                        borderColor: isSel ? 'var(--sage-600)' : 'var(--border)',
                        fontSize: 14, fontWeight: 500,
                        fontFamily: 'var(--font-sans)',
                        cursor: 'pointer',
                        transition: 'all 140ms var(--ease-standard)',
                      }}>{t}</button>
                  );
                })}
              </div>
            </div>

            {/* Summary + CTA */}
            <div style={{
              padding: '24px 0 0', borderTop: '1px solid var(--border)',
              display: 'grid', gridTemplateColumns: '1fr auto', gap: 24, alignItems: 'center',
            }}>
              <div>
                <div className="tiny" style={{ marginBottom: 6 }}>Din valda tid</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: 22, fontWeight: 400, color: 'var(--ink-700)', letterSpacing: '-0.01em' }}>
                  Onsdag 13 maj · {selectedTime}
                </div>
                <div className="small" style={{ marginTop: 4, color: 'var(--fg-muted)' }}>
                  {selectedTreatment} · ca 45 min · Från 795 kr
                </div>
              </div>
              <button className="btn btn-primary">Fortsätt boka →</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function BookingStat({ label, value, emphasis }) {
  return (
    <div style={{
      background: 'var(--white)',
      padding: '18px 20px',
      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 16,
    }}>
      <span className="small" style={{ color: 'var(--fg-muted)' }}>{label}</span>
      <span style={{
        fontFamily: 'var(--font-serif)',
        fontSize: emphasis ? 20 : 17,
        fontWeight: 400,
        color: emphasis ? 'var(--sage-600)' : 'var(--ink-700)',
        letterSpacing: '-0.01em',
      }}>{value}</span>
    </div>
  );
}

function FieldSelect({ label, value, options, onChange }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <span className="tiny" style={{ fontWeight: 500, letterSpacing: '0.14em', textTransform: 'uppercase' }}>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)} style={{
        padding: '12px 14px',
        border: '1px solid var(--border)',
        background: 'var(--white)',
        fontFamily: 'var(--font-sans)', fontSize: 15, color: 'var(--ink-700)',
        appearance: 'none',
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8' fill='none'><path d='M1 1.5L6 6.5L11 1.5' stroke='%232b2b29' stroke-width='1.2'/></svg>")`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 14px center',
        cursor: 'pointer',
      }}>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );
}

function CalArrow({ dir }) {
  return (
    <button style={{
      width: 32, height: 32, border: '1px solid var(--border)',
      background: 'var(--white)', cursor: 'pointer',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ transform: dir === 'left' ? 'rotate(0)' : 'rotate(180deg)' }}>
        <path d="M6 1.5L2 5L6 8.5" stroke="#2b2b29" strokeWidth="1.2"/>
      </svg>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Footer
// ─────────────────────────────────────────────────────────────────────────────
function Footer() {
  const cols = [
    { title: 'Behandlingar', items: [
      { label: 'Akuttandvård', href: 'Akuttandvård.html' },
      { label: 'Implantat', href: '#' },
      { label: 'Karies / Hål', href: '#' },
      { label: 'Tandblekning', href: '#' },
      { label: 'Tandfasader', href: '#' },
      { label: 'Tandreglering', href: '#' },
      { label: 'Tandsten', href: '#' },
      { label: 'Tandvårdsrädsla', href: '#' },
    ]},
    { title: 'Kliniken', items: [
      { label: 'Om oss', href: 'Om oss.html' },
      { label: 'Barnspecialist', href: 'Barnspecialist.html' },
      { label: 'Lista dig', href: 'Lista dig.html' },
      { label: 'Remiss', href: 'Remiss.html' },
      { label: 'Kampanjer', href: 'Kampanjer.html' },
      { label: 'Räntefri delbetalning', href: 'Räntefritt.html' },
    ]},
    { title: 'Patient', items: [
      { label: 'Boka tid', href: 'Älvsjö Tandvård.html#booking' },
      { label: 'Mina tider', href: 'Mina tider.html' },
      { label: 'Kontakt', href: 'Kontakt.html' },
      { label: 'Hitta hit', href: 'Kontakt.html' },
      { label: 'Företag', href: '#' },
      { label: 'Arbeta med oss', href: '#' },
    ]},
  ];

  return (
    <footer style={{ background: 'var(--ink-700)', color: 'var(--white)', paddingTop: 96 }}>
      <div className="container-wide" style={{ paddingBottom: 64 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr 1fr', gap: 64, marginBottom: 72 }}>
          <div>
            <img src="img/logo-white.png" alt="Älvsjö Tandvård" style={{ height: 64, width: 'auto', display: 'block', marginBottom: 12, marginLeft: -6 }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14, fontSize: 14, color: 'rgba(255,255,255,0.7)', maxWidth: 280 }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <IcoPin size={15} style={{ color: 'var(--sage-300)', marginTop: 2, flexShrink: 0 }} />
                <div>Prästgårdsgränd 4<br/>125 44 Älvsjö</div>
              </div>
              <a href="tel:+46812854555" style={{ display: 'flex', gap: 10, alignItems: 'center', color: 'var(--white)', textDecoration: 'none' }}>
                <IcoPhone size={15} style={{ color: 'var(--sage-300)', flexShrink: 0 }} />
                08 — 12 85 45 55
              </a>
              <a href="mailto:boka@alvsjotandvard.se" style={{ display: 'flex', gap: 10, alignItems: 'center', color: 'rgba(255,255,255,0.7)', textDecoration: 'none' }}>
                <IcoMail size={15} style={{ color: 'var(--sage-300)', flexShrink: 0 }} />
                boka@alvsjotandvard.se
              </a>
            </div>
          </div>

          {cols.map((c, i) => (
            <div key={i}>
              <div className="eyebrow" style={{ color: 'var(--sage-300)', marginBottom: 20 }}>{c.title}</div>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
                {c.items.map(it => (
                  <li key={it.label}>
                    <a href={it.href} style={{
                      color: 'rgba(255,255,255,0.75)', textDecoration: 'none', textDecorationColor: 'transparent',
                      fontSize: 14,
                    }}>{it.label}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Hours strip */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)',
          padding: '24px 0',
          borderTop: '1px solid rgba(255,255,255,0.12)',
          borderBottom: '1px solid rgba(255,255,255,0.12)',
        }}>
          {[
            ['Måndag', '07:00 – 20:00'],
            ['Tisdag', '07:00 – 20:00'],
            ['Onsdag', '07:00 – 20:00'],
            ['Torsdag', '07:00 – 20:00'],
            ['Fredag', '07:00 – 17:00'],
            ['Lördag', '09:00 – 15:00'],
            ['Söndag', 'Stängt'],
          ].map(([d, h], i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: '0 16px', borderLeft: i ? '1px solid rgba(255,255,255,0.08)' : 'none' }}>
              <span style={{ fontSize: 10, fontWeight: 500, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--sage-300)' }}>{d}</span>
              <span style={{ fontSize: 13, color: 'var(--white)' }}>{h}</span>
            </div>
          ))}
        </div>

        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          paddingTop: 32, fontSize: 12, color: 'rgba(255,255,255,0.5)',
        }}>
          <div>© 2026 Älvsjö Tandvård AB · Org.nr 559089-8598</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <a href="#" style={{ color: 'rgba(255,255,255,0.5)', textDecoration: 'none' }}>Integritetspolicy</a>
            <a href="#" style={{ color: 'rgba(255,255,255,0.5)', textDecoration: 'none' }}>Cookies</a>
            <a href="#" style={{ color: 'rgba(255,255,255,0.5)', textDecoration: 'none' }}>Personalingång</a>
            <div style={{ display: 'flex', gap: 12, marginLeft: 8 }}>
              <a href="#" style={{ color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center' }}
                onMouseEnter={e => e.currentTarget.style.color = 'var(--white)'}
                onMouseLeave={e => e.currentTarget.style.color = 'rgba(255,255,255,0.5)'}>
                <IcoInstagram size={18} />
              </a>
              <a href="#" style={{ color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center' }}
                onMouseEnter={e => e.currentTarget.style.color = 'var(--white)'}
                onMouseLeave={e => e.currentTarget.style.color = 'rgba(255,255,255,0.5)'}>
                <IcoFacebook size={18} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

// Export to window
Object.assign(window, {
  Header, Treatments, Reviews, About, EmergencyBanner, Team, PhotoTour, Booking, Footer,
});
