// subpage.jsx — Shared layout components for subpages
// PageHero, ContentBlock, Bullets, InfoStrip, FAQ

const { useState: useStateSP } = React;

function PageHero({ eyebrow, title, ingress, bullets = [], dark = false }) {
  return (
    <section style={{
      background: dark ? 'var(--ink-700)' : 'var(--cream)',
      color: dark ? 'var(--white)' : 'var(--ink-700)',
      paddingTop: 96, paddingBottom: 96,
      borderBottom: dark ? 'none' : '1px solid var(--border)',
    }}>
      <div className="container-wide">
        <div className="eyebrow" style={{
          marginBottom: 32,
          color: dark ? 'var(--sage-300)' : 'var(--sage-600)',
        }}>{eyebrow}</div>

        <div style={{
          display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 80,
          alignItems: 'end',
        }}>
          <h1 style={{
            fontFamily: 'var(--font-serif)', fontWeight: 300,
            fontSize: 'clamp(64px, 7.5vw, 132px)', lineHeight: 0.95,
            letterSpacing: '-0.035em',
            color: dark ? 'var(--white)' : 'var(--ink-700)',
            maxWidth: '14ch',
          }}>{title}</h1>

          <div style={{ paddingBottom: 16 }}>
            <p className="lead" style={{
              maxWidth: '40ch', marginBottom: 32,
              color: dark ? 'rgba(255,255,255,0.85)' : 'var(--ink-500)',
            }}>{ingress}</p>

            {bullets.length > 0 && (
              <div style={{
                display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14,
                paddingTop: 24,
                borderTop: dark ? '1px solid rgba(255,255,255,0.15)' : '1px solid var(--border)',
              }}>
                {bullets.map((b, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'baseline', gap: 10,
                    fontSize: 14, fontWeight: 500,
                    color: dark ? 'rgba(255,255,255,0.85)' : 'var(--ink-600)',
                  }}>
                    <span style={{
                      fontSize: 11, color: dark ? 'var(--sage-300)' : 'var(--sage-600)',
                      letterSpacing: '0.14em',
                    }}>0{i + 1}</span>
                    {b}
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: 12, marginTop: 40 }}>
              <a href={dark ? '#' : 'Älvsjö Tandvård.html#booking'} className={dark ? 'btn btn-light btn-lg' : 'btn btn-primary btn-lg'}>Boka tid</a>
              <a href="tel:+46812854555" className={dark ? 'btn btn-ghost btn-lg' : 'btn btn-ghost btn-lg'} style={dark ? { color: 'var(--white)', borderColor: 'rgba(255,255,255,0.4)' } : {}}>Ring oss</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ContentBlock({ eyebrow, title, html, ctaLabel = 'Boka tid', ctaHref = 'Älvsjö Tandvård.html#booking', img, imgRight = false, bg = 'var(--white)' }) {
  return (
    <section className="section" style={{ background: bg }}>
      <div className="container-wide">
        <div style={{
          display: 'grid',
          gridTemplateColumns: img ? (imgRight ? '1fr 1fr' : '1fr 1fr') : '1fr 2fr',
          gap: 64, alignItems: 'center',
        }}>
          {img && !imgRight && (
            <div style={{
              aspectRatio: '4 / 5',
              background: `url(${img}) center/cover no-repeat`,
              filter: 'saturate(0.9)',
            }} />
          )}
          <div>
            {eyebrow && <div className="eyebrow" style={{ marginBottom: 16 }}>{eyebrow}</div>}
            <h2 style={{ maxWidth: '20ch', marginBottom: 32 }}>{title}</h2>
            <div className="prose" style={{
              fontFamily: 'var(--font-sans)', fontSize: 16, lineHeight: 1.7,
              color: 'var(--ink-500)',
            }} dangerouslySetInnerHTML={{ __html: html }} />
            {ctaLabel && (
              <a href={ctaHref} className="btn btn-primary" style={{ marginTop: 32 }}>{ctaLabel}</a>
            )}
          </div>
          {img && imgRight && (
            <div style={{
              aspectRatio: '4 / 5',
              background: `url(${img}) center/cover no-repeat`,
              filter: 'saturate(0.9)',
            }} />
          )}
        </div>
      </div>
    </section>
  );
}

function TextBlocks({ eyebrow, title, blocks }) {
  return (
    <section className="section" style={{ background: 'var(--cream)' }}>
      <div className="container-wide">
        <div style={{ marginBottom: 64, paddingBottom: 32, borderBottom: '1px solid var(--border)' }}>
          {eyebrow && <div className="eyebrow" style={{ marginBottom: 16 }}>{eyebrow}</div>}
          <h2 style={{ maxWidth: '24ch' }}>{title}</h2>
        </div>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '64px 80px',
        }}>
          {blocks.map((b, i) => (
            <article key={i} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{
                fontSize: 11, fontWeight: 500, letterSpacing: '0.22em',
                textTransform: 'uppercase', color: 'var(--sage-600)',
              }}>{String(i + 1).padStart(2, '0')}</div>
              <h3 style={{
                fontFamily: 'var(--font-serif)', fontWeight: 400,
                fontSize: 28, lineHeight: 1.2, letterSpacing: '-0.02em',
                color: 'var(--ink-700)', maxWidth: '22ch',
              }}>{b.h3}</h3>
              <div className="prose" style={{
                fontSize: 15, lineHeight: 1.7, color: 'var(--ink-500)',
              }} dangerouslySetInnerHTML={{ __html: b.html }} />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function FAQ({ eyebrow = 'FAQ', title = 'Vanliga frågor', items = [] }) {
  const [open, setOpen] = useStateSP(0);
  return (
    <section className="section" style={{ background: 'var(--white)' }}>
      <div className="container-wide">
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: 64,
        }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: 16 }}>{eyebrow}</div>
            <h2 style={{ maxWidth: '14ch' }}>{title}</h2>
          </div>
          <div style={{ borderTop: '1px solid var(--border)' }}>
            {items.map((it, i) => {
              const isOpen = open === i;
              return (
                <div key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                  <button onClick={() => setOpen(isOpen ? -1 : i)} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 24,
                    width: '100%', padding: '28px 0',
                    background: 'transparent', border: 'none', cursor: 'pointer',
                    textAlign: 'left',
                  }}>
                    <span style={{
                      fontFamily: 'var(--font-serif)', fontSize: 22, fontWeight: 400,
                      color: 'var(--ink-700)', letterSpacing: '-0.01em', lineHeight: 1.3,
                    }}>{it.question}</span>
                    <span style={{
                      fontFamily: 'var(--font-sans)', fontSize: 20, color: 'var(--sage-600)',
                      transform: isOpen ? 'rotate(45deg)' : 'rotate(0)',
                      transition: 'transform 240ms var(--ease-standard)',
                      lineHeight: 1, flexShrink: 0,
                    }}>+</span>
                  </button>
                  {isOpen && (
                    <div style={{
                      paddingBottom: 28, paddingRight: 60,
                      fontSize: 15, lineHeight: 1.7, color: 'var(--ink-500)',
                      maxWidth: '70ch',
                    }}>{it.answer}</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function CTAStrip({ title = 'Boka tid hos oss', sub = 'Ring 08-12 85 45 55 eller boka online — vi prioriterar akuta besvär.' }) {
  return (
    <section style={{
      background: 'var(--ink-700)', color: 'var(--white)',
      padding: '80px 0',
    }}>
      <div className="container-wide" style={{
        display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 48, alignItems: 'center',
      }}>
        <div>
          <h2 style={{ color: 'var(--white)', marginBottom: 16, maxWidth: '18ch' }}>{title}</h2>
          <p style={{ color: 'rgba(255,255,255,0.7)', maxWidth: '46ch', fontSize: 16 }}>{sub}</p>
        </div>
        <div style={{ display: 'flex', gap: 12, justifySelf: 'end' }}>
          <a href="Älvsjö Tandvård.html#booking" className="btn btn-light btn-lg">Boka tid</a>
          <a href="tel:+46812854555" className="btn btn-ghost btn-lg" style={{ color: 'var(--white)', borderColor: 'rgba(255,255,255,0.4)' }}>08 — 12 85 45 55</a>
        </div>
      </div>
    </section>
  );
}

// TreatmentHero — CSS height: exact fold fit (header = 116px)
function TreatmentHero({ eyebrow, title, ingress, bullets = [], img, stat, caption }) {
  return (
    <section style={{
      background: 'var(--cream)',
      height: 660,
      borderBottom: '1px solid var(--border)',
      overflow: 'hidden',
    }}>
      <div className="container-wide" style={{ width: '100%', paddingTop: 40, paddingBottom: 40 }}>
        <div className="eyebrow" style={{ marginBottom: 20, color: 'var(--sage-600)' }}>{eyebrow}</div>

        <div style={{
          display: 'grid', gridTemplateColumns: '1.15fr 1fr', gap: 64,
          alignItems: 'stretch',
          height: 500,
        }}>
          {/* LEFT */}
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <h1 style={{
              fontFamily: 'var(--font-serif)', fontWeight: 300,
              fontSize: 'clamp(44px, 5.5vw, 96px)', lineHeight: 0.95,
              letterSpacing: '-0.035em', color: 'var(--ink-700)',
              maxWidth: '14ch', marginTop: 0,
            }}>{title}</h1>

            <div>
              <p className="lead" style={{ maxWidth: '44ch', marginBottom: 24, color: 'var(--ink-500)', fontSize: 17 }}>
                {ingress}
              </p>
              {bullets.length > 0 && (
                <div style={{
                  display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px 24px',
                  paddingTop: 20, marginBottom: 28,
                  borderTop: '1px solid var(--border)',
                }}>
                  {bullets.map((b, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'baseline', gap: 10,
                      fontSize: 13, fontWeight: 500, color: 'var(--ink-600)',
                    }}>
                      <span style={{ fontSize: 10, color: 'var(--sage-600)', letterSpacing: '0.14em' }}>0{i + 1}</span>
                      {b}
                    </div>
                  ))}
                </div>
              )}
              <div style={{ display: 'flex', gap: 12 }}>
                <a href="#booking" className="btn btn-primary">Boka tid</a>
                <a href="tel:+46812854555" className="btn btn-ghost">Ring oss</a>
              </div>
            </div>
          </div>

          {/* RIGHT — image fills remaining height, stat card inside */}
          <div style={{ position: 'relative' }}>
            <div style={{
              position: 'absolute', inset: 0,
              backgroundImage: `url(${img})`,
              backgroundSize: 'cover', backgroundPosition: 'center',
              filter: 'saturate(0.9)',
            }} />
            {stat && (
              <div style={{
                position: 'absolute', left: -28, bottom: 28,
                background: 'var(--ink-700)', color: 'var(--white)',
                padding: '24px 28px', maxWidth: 260,
                boxShadow: '0 24px 60px rgba(0,0,0,0.18)',
              }}>
                <div style={{
                  fontSize: 10, fontWeight: 600, letterSpacing: '0.22em', textTransform: 'uppercase',
                  color: 'var(--sage-300)', marginBottom: 10,
                }}>{stat.label}</div>
                <div style={{
                  fontFamily: 'var(--font-serif)', fontWeight: 300,
                  fontSize: 'clamp(40px, 4vw, 56px)', lineHeight: 0.95, letterSpacing: '-0.03em',
                  marginBottom: 8,
                }}>{stat.value}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', lineHeight: 1.5 }}>{stat.sub}</div>
              </div>
            )}
            {caption && (
              <div style={{
                position: 'absolute', top: 20, right: 0,
                writingMode: 'vertical-rl', transform: 'rotate(180deg)',
                fontSize: 10, fontWeight: 600, letterSpacing: '0.32em', textTransform: 'uppercase',
                color: 'var(--white)', mixBlendMode: 'difference',
              }}>{caption}</div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { PageHero, ContentBlock, TextBlocks, FAQ, CTAStrip, TreatmentHero });
