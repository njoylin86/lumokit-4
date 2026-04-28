// Reviews.jsx — split panel with star + quote and a 'read all' link
function Reviews({ items, onAll }) {
  const [i, setI] = React.useState(0);
  const r = items[i];
  const next = () => setI((i + 1) % items.length);
  const prev = () => setI((i - 1 + items.length) % items.length);
  return (
    <section style={rvStyles.wrap}>
      <div style={rvStyles.left}>
        <div style={rvStyles.stars}>★★★★★</div>
        <div style={rvStyles.name}>{r.name}</div>
        <p style={rvStyles.quote}>{r.text}</p>
        <div style={rvStyles.src}>{r.source}</div>
        <button style={{ ...rvStyles.arrow, left: 24 }} onClick={prev} aria-label="Föregående">‹</button>
        <button style={{ ...rvStyles.arrow, right: 24 }} onClick={next} aria-label="Nästa">›</button>
      </div>
      <div style={rvStyles.right}>
        <a href="#" onClick={(e) => { e.preventDefault(); onAll && onAll(); }} style={rvStyles.allLink}>
          ⟵ &nbsp;<span style={{ textDecoration: 'underline', textUnderlineOffset: 4 }}>Läs våra recensioner</span>
        </a>
      </div>
    </section>
  );
}

const rvStyles = {
  wrap: { display: 'grid', gridTemplateColumns: '1.4fr 1fr', minHeight: 280 },
  left: { background: 'var(--paper)', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '56px 80px', textAlign: 'center' },
  right: { background: 'var(--ink-100)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 56 },
  stars: { color: 'var(--star)', fontSize: 22, letterSpacing: 2, marginBottom: 14 },
  name: { fontFamily: 'var(--font-sans)', fontWeight: 600, color: 'var(--ink-700)', marginBottom: 12 },
  quote: { fontFamily: 'var(--font-sans)', fontSize: 14, color: 'var(--fg)', lineHeight: 1.6, maxWidth: '36ch', margin: '0 0 14px' },
  src: { fontFamily: 'var(--font-sans)', fontSize: 11, color: 'var(--fg-muted)' },
  arrow: { position: 'absolute', top: '50%', transform: 'translateY(-50%)', width: 32, height: 32, background: 'transparent', border: 'none', fontSize: 26, lineHeight: 1, cursor: 'pointer', color: 'var(--ink-500)', fontFamily: 'serif' },
  allLink: { fontFamily: 'var(--font-sans)', fontSize: 15, color: 'var(--ink-700)', textDecoration: 'none' },
};

window.Reviews = Reviews;
