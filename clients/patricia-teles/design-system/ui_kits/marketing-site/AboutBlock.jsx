// AboutBlock.jsx — eyebrow, serif headline, prose, ghost CTA
function AboutBlock({ image, onMore }) {
  return (
    <section style={aboutStyles.wrap}>
      <div style={aboutStyles.inner}>
        <div>
          <div className="eyebrow" style={aboutStyles.eyebrow}>Om oss</div>
          <h2 style={aboutStyles.title}>Patricia Teles</h2>
          <p style={aboutStyles.p}>
            Patricia Teles är en modern tandläkarklinik mitt i Stockholm. På kliniken
            arbetar tre tandläkare, en tandhygienist samt två dentalassistenter.
          </p>
          <p style={aboutStyles.p}>
            Vi är en av de största klinikerna i Sverige inom Invisalignbehandlingar
            (osynlig tandställning) och skalfasader (porslinsfasader) med
            hundratals utförda patientfall årligen. Vi strävar alltid efter
            naturligt vackra resultat.
          </p>
          <p style={aboutStyles.p}>
            För oss är varje individ unik. Att lyssna på och se varje person vi
            möter är därför av största vikt.
          </p>
          <p style={{ ...aboutStyles.p, marginBottom: 32 }}>
            <strong style={{ fontWeight: 600 }}>Varmt välkommen till oss.</strong>
          </p>
          <button style={aboutStyles.cta} onClick={onMore}>Läs mer</button>
        </div>
        <div style={aboutStyles.imgWrap}>
          {image && <img src={image} alt="" style={aboutStyles.img} />}
        </div>
      </div>
    </section>
  );
}

const aboutStyles = {
  wrap: { background: '#fff', padding: '96px 0' },
  inner: {
    maxWidth: 1180, margin: '0 auto', padding: '0 32px',
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64,
    alignItems: 'start',
  },
  eyebrow: {
    fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    color: 'var(--blush-600)', marginBottom: 16,
  },
  title: {
    fontFamily: 'var(--font-serif)', fontWeight: 500,
    fontSize: 56, lineHeight: 1.05, letterSpacing: '-0.02em',
    color: 'var(--ink-700)', margin: '0 0 28px',
  },
  p: {
    fontFamily: 'var(--font-sans)', fontSize: 15, lineHeight: 1.7,
    color: 'var(--fg)', margin: '0 0 14px', maxWidth: '52ch',
  },
  cta: {
    fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    color: '#fff', background: 'var(--ink-700)', border: 'none',
    padding: '14px 28px', borderRadius: 4, cursor: 'pointer',
  },
  imgWrap: {
    background: 'var(--blush-100)', aspectRatio: '4/5',
    borderRadius: 4, overflow: 'hidden',
  },
  img: { width: '100%', height: '100%', objectFit: 'cover' },
};

window.AboutBlock = AboutBlock;
