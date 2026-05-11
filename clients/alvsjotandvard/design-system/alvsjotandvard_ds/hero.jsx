// hero.jsx — Three hero variants for Älvsjö Tandvård

const { useState: useStateH } = React;

// ─────────────────────────────────────────────────────────────────────────────
// HeroStats — large stat grid; conveys scale immediately
// ─────────────────────────────────────────────────────────────────────────────
function HeroStats() {
  return (
    <section style={{
      background: 'var(--white)',
      paddingTop: 'var(--space-10)',
      paddingBottom: 'var(--space-10)',
    }}>
      <div className="container-wide">
        {/* Eyebrow row */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          paddingBottom: 28, marginBottom: 56,
          borderBottom: '1px solid var(--border)',
        }}>
          <div className="eyebrow">Modern tandvård · 2 min från pendeln · Älvsjö</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span className="stars" style={{ fontSize: 14 }}>★★★★★</span>
            <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--ink-700)' }}>4,9</span>
            <span style={{ fontSize: 12, color: 'var(--fg-muted)' }}>· 4 142 Google-omdömen</span>
          </div>
        </div>

        {/* Headline */}
        <h1 className="display" style={{
          maxWidth: '17ch', marginBottom: 48,
        }}>
          Trygg tand&shy;v&aring;rd<br/>
          f&ouml;r hela familjen.<br/>
          <span className="italic" style={{ color: 'var(--sage-600)' }}>Mitt i &Auml;lvsj&ouml;.</span>
        </h1>

        {/* Subhead + CTA row */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 56,
          alignItems: 'end', marginBottom: 80,
        }}>
          <p className="lead" style={{ maxWidth: '52ch', color: 'var(--ink-500)' }}>
            Välkommen till en lugn och välkomnande klinik två minuter från pendeltåget. Här får du och hela familjen kvalitativ tandvård — från regelbunden undersökning till implantat, Invisalign och estetisk tandvård. Akut hjälp oftast samma dag.
          </p>
          <div style={{ display: 'flex', gap: 12, justifySelf: 'end' }}>
            <a href="#booking" className="btn btn-primary btn-lg">Boka tid</a>
            <a href="#" className="btn btn-ghost btn-lg">Se behandlingar</a>
          </div>
        </div>

        {/* Stat grid */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 1, background: 'var(--border)',
          border: '1px solid var(--border)',
        }}>
          {[
            ['Gratis', 'Tandvård för\nbarn upp till 19'],
            ['Idag', 'Akut hjälp\nsamma dag'],
            ['07–20', 'Öppet vardagar\n+ lördagar'],
            ['0 %', 'Räntefri\ndelbetalning'],
          ].map(([v, l], i) => (
            <div key={i} style={{
              background: 'var(--white)', padding: '36px 32px',
              display: 'flex', flexDirection: 'column', gap: 12,
            }}>
              <div style={{
                fontFamily: 'var(--font-serif)', fontWeight: 300,
                fontSize: 'clamp(48px, 4.4vw, 72px)', lineHeight: 0.95,
                letterSpacing: '-0.03em', color: 'var(--ink-700)',
              }}>{v}</div>
              <div style={{
                fontSize: 11, fontWeight: 500, letterSpacing: '0.22em',
                textTransform: 'uppercase', color: 'var(--sage-600)',
                whiteSpace: 'pre-line', lineHeight: 1.5,
              }}>{l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// HeroBleed — full-bleed clinic photograph + overlay
// ─────────────────────────────────────────────────────────────────────────────
function HeroBleed() {
  return (
    <section style={{
      position: 'relative', minHeight: 'min(82vh, 820px)',
      background: 'var(--ink-700)',
      display: 'flex', alignItems: 'flex-end',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        background: `url("img/korridor-bla-tandlogga.jpg") center/cover no-repeat`,
        filter: 'saturate(0.85) brightness(0.85)',
      }} />
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(180deg, rgba(20,20,18,0.45) 0%, rgba(20,20,18,0.15) 35%, rgba(20,20,18,0.85) 100%)',
      }} />

      {/* Top eyebrow */}
      <div style={{
        position: 'absolute', top: 48, left: 0, right: 0, zIndex: 2,
      }}>
        <div className="container-wide" style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          color: 'var(--white)',
        }}>
          <div style={{
            fontSize: 11, fontWeight: 500, letterSpacing: '0.22em',
            textTransform: 'uppercase', color: 'rgba(255,255,255,0.85)',
          }}>Modern tandvård · 2 min från pendeln · Älvsjö</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--white)' }}>
            <span style={{ color: '#f5c136', fontSize: 14 }}>★★★★★</span>
            <span style={{ fontSize: 13, fontWeight: 500 }}>4,9</span>
            <span style={{ fontSize: 12, opacity: 0.7 }}>· 4 142 Google-omdömen</span>
          </div>
        </div>
      </div>

      <div className="container-wide" style={{
        position: 'relative', zIndex: 2,
        paddingTop: 96, paddingBottom: 80, color: 'var(--white)',
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 80, alignItems: 'end' }}>
          <div>
            <h1 className="display" style={{
              color: 'var(--white)', maxWidth: '14ch', marginBottom: 32,
              fontWeight: 300,
            }}>
              Trygg tandvård.<br/>
              <span className="italic">Hela familjen.</span>
            </h1>
            <p className="lead" style={{
              color: 'rgba(255,255,255,0.85)', maxWidth: '48ch',
            }}>
              Från första undersökningen till implantat och Invisalign — en nyrenoverad klinik mitt i Älvsjö där varje besök är utformat för att du ska känna dig lugn och omhändertagen.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, alignItems: 'flex-start' }}>
            <a href="#booking" className="btn btn-light btn-lg" style={{ width: '100%' }}>Boka tid online</a>
            <a href="#" style={{
              color: 'var(--white)', fontSize: 13, fontWeight: 500,
              letterSpacing: '0.14em', textTransform: 'uppercase',
              textDecoration: 'none', textDecorationColor: 'transparent',
              borderBottom: '1px solid rgba(255,255,255,0.4)', paddingBottom: 4,
            }}>Akuttandvård 24/7 →</a>
          </div>
        </div>

        {/* Bottom info strip */}
        <div style={{
          marginTop: 80, paddingTop: 32,
          borderTop: '1px solid rgba(255,255,255,0.2)',
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 32,
        }}>
          {[
            ['Gratis', 'Barn t.o.m. 19'],
            ['Idag', 'Akut hjälp'],
            ['07–20', 'Öppet vardagar'],
            ['0 %', 'Delbetalning'],
          ].map(([v, l], i) => (
            <div key={i}>
              <div style={{
                fontFamily: 'var(--font-serif)', fontWeight: 300,
                fontSize: 52, lineHeight: 1,
                letterSpacing: '-0.02em', color: 'var(--white)', marginBottom: 6,
              }}>{v}</div>
              <div style={{
                fontSize: 11, fontWeight: 500, letterSpacing: '0.22em',
                textTransform: 'uppercase', color: 'rgba(255,255,255,0.7)',
              }}>{l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// HeroEditorial — split layout, large headline left, image right
// ─────────────────────────────────────────────────────────────────────────────
function HeroEditorial() {
  return (
    <section style={{ background: 'var(--white)' }}>
      <div className="container-wide" style={{ paddingTop: 56, paddingBottom: 80 }}>
        {/* Eyebrow strip */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          paddingBottom: 24, marginBottom: 56,
          borderBottom: '1px solid var(--border)',
        }}>
          <div className="eyebrow">N° 01 — Hem</div>
          <div className="eyebrow" style={{ color: 'var(--fg-muted)' }}>
            Älvsjö Tandvård · Est. 1987
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="stars" style={{ fontSize: 13 }}>★★★★★</span>
            <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--ink-700)' }}>4,9 / 5</span>
            <span style={{ fontSize: 11, color: 'var(--fg-muted)', letterSpacing: '0.08em' }}>· Google · 4 142 omdömen</span>
          </div>
        </div>

        <div style={{
          display: 'grid', gridTemplateColumns: '1.15fr 0.85fr', gap: 64,
          alignItems: 'stretch',
        }}>
          {/* Left — type */}
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{
                fontFamily: 'var(--font-serif)', fontWeight: 300,
                fontSize: 'clamp(56px, 7vw, 120px)', lineHeight: 0.95,
                letterSpacing: '-0.03em', color: 'var(--ink-700)',
                marginBottom: 40,
              }}>
                Trygg<br/>
                tandvård<br/>
                <span className="italic" style={{ color: 'var(--sage-600)' }}>för hela</span><br/>
                <span className="italic" style={{ color: 'var(--sage-600)' }}>familjen.</span>
              </h1>
              <p className="lead" style={{
                maxWidth: '42ch', color: 'var(--ink-500)', marginBottom: 32,
              }}>
                En nyrenoverad klinik mitt i Älvsjö, två minuter från pendeltåget. Här möter vi dig med tid, lugn och modern teknik — från regelbunden tandvård till implantat och osynlig tandreglering.
              </p>
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              <a href="#booking" className="btn btn-primary btn-lg">Boka tid</a>
              <a href="#" className="btn btn-ghost btn-lg">Våra behandlingar</a>
            </div>
          </div>

          {/* Right — image stack */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              flex: 1, minHeight: 420,
              background: `url("img/korridor-bla-tandlogga.jpg") center/cover no-repeat`,
              filter: 'saturate(0.9)',
            }} />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, height: 200 }}>
              <div style={{
                background: `url("img/behandlingsrum-oversikt-bla-stol.jpg") center/cover no-repeat`,
                filter: 'saturate(0.9)',
              }} />
              <div style={{
                background: 'var(--sage-50)',
                padding: 24,
                display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
              }}>
                <div className="eyebrow">Idag</div>
                <div>
                  <div style={{
                    fontFamily: 'var(--font-serif)', fontWeight: 300,
                    fontSize: 36, letterSpacing: '-0.02em', color: 'var(--ink-700)',
                    lineHeight: 1, marginBottom: 8,
                  }}>34 lediga<br/>tider</div>
                  <div className="small">denna vecka</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { HeroStats, HeroBleed, HeroEditorial });
