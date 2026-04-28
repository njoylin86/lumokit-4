// TreatmentDetail.jsx — detail page for a treatment
function TreatmentDetail({ treatment, onBack, onBook }) {
  return (
    <article style={tdStyles.wrap}>
      <button onClick={onBack} style={tdStyles.back}>← Alla behandlingar</button>
      <div style={tdStyles.grid}>
        <div>
          <div className="eyebrow" style={tdStyles.eyebrow}>Behandling</div>
          <h1 style={tdStyles.h}>{treatment.title}</h1>
          <p style={tdStyles.p}>{treatment.body}</p>
          <ul style={tdStyles.ul}>
            {treatment.bullets.map(b => <li key={b} style={tdStyles.li}>{b}</li>)}
          </ul>
          <div style={tdStyles.priceRow}>
            <div>
              <div style={tdStyles.priceLbl}>Från</div>
              <div style={tdStyles.price}>{treatment.price}</div>
            </div>
            <button style={tdStyles.cta} onClick={onBook}>Boka tid</button>
          </div>
        </div>
        <div style={tdStyles.imgWrap}>
          <img src={treatment.img} alt="" style={tdStyles.img}/>
        </div>
      </div>
    </article>
  );
}

const tdStyles = {
  wrap: { background: '#fff', padding: '64px 32px 96px', maxWidth: 1180, margin: '0 auto' },
  back: { background: 'transparent', border: 'none', fontFamily: 'var(--font-sans)', fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.2em', color: 'var(--fg-muted)', cursor: 'pointer', marginBottom: 32, padding: 0 },
  grid: { display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 64, alignItems: 'start' },
  eyebrow: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', color: 'var(--blush-600)', marginBottom: 16 },
  h: { fontFamily: 'var(--font-serif)', fontWeight: 500, fontSize: 56, lineHeight: 1.05, letterSpacing: '-0.02em', color: 'var(--ink-700)', margin: '0 0 24px' },
  p: { fontFamily: 'var(--font-sans)', fontSize: 16, lineHeight: 1.7, color: 'var(--fg)', maxWidth: '54ch', marginBottom: 28 },
  ul: { listStyle: 'none', padding: 0, margin: '0 0 36px', display: 'flex', flexDirection: 'column', gap: 10 },
  li: { fontFamily: 'var(--font-sans)', fontSize: 15, color: 'var(--fg)', position: 'relative', paddingLeft: 18 },
  priceRow: { display: 'flex', alignItems: 'center', gap: 24, padding: '24px 0', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' },
  priceLbl: { fontFamily: 'var(--font-sans)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.18em', color: 'var(--fg-muted)' },
  price: { fontFamily: 'var(--font-serif)', fontSize: 32, color: 'var(--ink-700)', fontWeight: 500 },
  cta: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', background: 'var(--ink-700)', color: '#fff', border: 'none', padding: '14px 28px', borderRadius: 4, cursor: 'pointer', marginLeft: 'auto' },
  imgWrap: { aspectRatio: '4/5', borderRadius: 4, overflow: 'hidden', background: 'var(--blush-100)' },
  img: { width: '100%', height: '100%', objectFit: 'cover' },
};

window.TreatmentDetail = TreatmentDetail;
