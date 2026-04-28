// BookModal.jsx — overlay confirmation modal
function BookModal({ open, onClose }) {
  if (!open) return null;
  return (
    <div style={bmStyles.scrim} onClick={onClose}>
      <div style={bmStyles.card} onClick={(e) => e.stopPropagation()}>
        <button style={bmStyles.x} onClick={onClose} aria-label="Stäng">×</button>
        <div className="eyebrow" style={bmStyles.eyebrow}>Boka tid</div>
        <h2 style={bmStyles.h}>Välkommen!</h2>
        <p style={bmStyles.p}>Lämna dina uppgifter så ringer vi upp inom 24 timmar och hittar en tid som passar dig.</p>
        <input placeholder="Ditt namn" style={bmStyles.input}/>
        <input placeholder="Telefon" style={bmStyles.input}/>
        <button style={bmStyles.cta} onClick={onClose}>Skicka</button>
      </div>
    </div>
  );
}

const bmStyles = {
  scrim: { position: 'fixed', inset: 0, background: 'rgba(31,31,31,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  card: { background: '#fff', borderRadius: 4, padding: '40px 48px', width: 420, maxWidth: '90vw', boxShadow: 'var(--shadow-lg)', position: 'relative', textAlign: 'center' },
  x: { position: 'absolute', top: 12, right: 16, background: 'transparent', border: 'none', fontSize: 24, color: 'var(--fg-muted)', cursor: 'pointer', lineHeight: 1 },
  eyebrow: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', color: 'var(--blush-600)', marginBottom: 12 },
  h: { fontFamily: 'var(--font-serif)', fontWeight: 500, fontSize: 36, color: 'var(--ink-700)', margin: '0 0 16px', letterSpacing: '-0.02em' },
  p: { fontFamily: 'var(--font-sans)', fontSize: 14, color: 'var(--fg)', lineHeight: 1.6, margin: '0 0 24px' },
  input: { width: '100%', boxSizing: 'border-box', padding: '12px 14px', border: '1px solid var(--border)', borderRadius: 4, fontFamily: 'var(--font-sans)', fontSize: 14, marginBottom: 12 },
  cta: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', background: 'var(--ink-700)', color: '#fff', border: 'none', padding: '14px 32px', borderRadius: 4, cursor: 'pointer', marginTop: 6 },
};

window.BookModal = BookModal;
