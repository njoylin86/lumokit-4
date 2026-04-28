// TreatmentGrid.jsx — square photo cards with spaced-caps overlay
function TreatmentGrid({ items, onSelect }) {
  return (
    <section style={tgStyles.wrap}>
      <div style={tgStyles.inner}>
        <div className="eyebrow" style={tgStyles.eyebrow}>Våra behandlingar</div>
        <div style={tgStyles.grid}>
          {items.map((it, i) => (
            <a key={i} href="#"
               onClick={(e) => { e.preventDefault(); onSelect && onSelect(it); }}
               style={{ ...tgStyles.card, background: it.bg }}>
              {it.img && <img src={it.img} alt="" style={tgStyles.cardImg} />}
              <div style={tgStyles.cardOverlay} />
              <div style={tgStyles.cardLabel}>{it.label}</div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

const tgStyles = {
  wrap: { background: 'var(--paper)', padding: '80px 0' },
  inner: { maxWidth: 1180, margin: '0 auto', padding: '0 32px' },
  eyebrow: {
    fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    color: 'var(--blush-600)', marginBottom: 28,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 16,
  },
  card: {
    position: 'relative', aspectRatio: '1', borderRadius: 4,
    overflow: 'hidden', display: 'block', textDecoration: 'none',
    cursor: 'pointer',
    transition: 'transform var(--dur-base) var(--ease-out)',
  },
  cardImg: { width: '100%', height: '100%', objectFit: 'cover' },
  cardOverlay: {
    position: 'absolute', inset: 0,
    background: 'linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.35) 100%)',
  },
  cardLabel: {
    position: 'absolute', inset: 0,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: 'var(--font-sans)', fontSize: 12, fontWeight: 500,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    color: '#fff', textAlign: 'center', padding: 20, lineHeight: 1.3,
  },
};

window.TreatmentGrid = TreatmentGrid;
