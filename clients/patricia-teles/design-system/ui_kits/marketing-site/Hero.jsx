// Hero.jsx — full-bleed photograph with the blush halo wash beneath
function Hero({ image, eyebrow, title, subtitle, cta, onCta }) {
  return (
    <section style={heroStyles.wrap}>
      <div style={heroStyles.halo} />
      <div style={heroStyles.frame}>
        <img src={image} alt="" style={heroStyles.img} />
        <div style={heroStyles.dots}>
          <span style={heroStyles.dotActive} />
          <span style={heroStyles.dot} />
          <span style={heroStyles.dot} />
          <span style={heroStyles.dot} />
          <span style={heroStyles.dot} />
        </div>
        <button style={{ ...heroStyles.arrow, left: 24 }} aria-label="Föregående">‹</button>
        <button style={{ ...heroStyles.arrow, right: 24 }} aria-label="Nästa">›</button>
      </div>
      {(eyebrow || title) && (
        <div style={heroStyles.caption}>
          {eyebrow && <div className="eyebrow" style={heroStyles.eyebrow}>{eyebrow}</div>}
          {title && <h1 style={heroStyles.title}>{title}</h1>}
          {subtitle && <p style={heroStyles.sub}>{subtitle}</p>}
          {cta && <button style={heroStyles.cta} onClick={onCta}>{cta}</button>}
        </div>
      )}
    </section>
  );
}

const heroStyles = {
  wrap: { position: 'relative', padding: '0 0 64px', overflow: 'hidden' },
  halo: {
    position: 'absolute', left: 0, right: 0, top: 80, bottom: 0,
    background: 'var(--blush-50)', zIndex: 0,
  },
  frame: {
    position: 'relative', maxWidth: 1180, margin: '0 auto', height: 540,
    overflow: 'hidden', borderRadius: 4, zIndex: 1,
  },
  img: { width: '100%', height: '100%', objectFit: 'cover', display: 'block' },
  dots: {
    position: 'absolute', bottom: 22, left: '50%', transform: 'translateX(-50%)',
    display: 'flex', gap: 8,
  },
  dot: { width: 6, height: 6, borderRadius: 999, background: 'rgba(255,255,255,0.6)' },
  dotActive: { width: 6, height: 6, borderRadius: 999, background: '#fff' },
  arrow: {
    position: 'absolute', top: '50%', transform: 'translateY(-50%)',
    width: 40, height: 40, borderRadius: 999, border: 'none',
    background: 'transparent', color: '#fff', fontSize: 28, cursor: 'pointer',
    fontFamily: 'serif', lineHeight: 1,
  },
  caption: {
    position: 'relative', zIndex: 2,
    maxWidth: 720, margin: '40px auto 0', padding: '0 32px',
    textAlign: 'center',
  },
  eyebrow: {
    fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    color: 'var(--blush-600)', marginBottom: 16,
  },
  title: {
    fontFamily: 'var(--font-serif)', fontWeight: 500,
    fontSize: 'clamp(40px, 5vw, 64px)', lineHeight: 1.05,
    letterSpacing: '-0.02em', color: 'var(--ink-700)',
    margin: '0 0 16px',
  },
  sub: {
    fontFamily: 'var(--font-sans)', fontSize: 17, lineHeight: 1.65,
    color: 'var(--fg)', margin: '0 auto 24px', maxWidth: 520,
  },
  cta: {
    fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    color: '#fff', background: 'var(--ink-700)', border: 'none',
    padding: '14px 28px', borderRadius: 4, cursor: 'pointer',
  },
};

window.Hero = Hero;
