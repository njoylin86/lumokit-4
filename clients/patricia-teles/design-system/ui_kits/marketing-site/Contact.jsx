// Contact.jsx — pink panel with telephone/hours block + contact form
function Contact({ onSubmit }) {
  const [sent, setSent] = React.useState(false);
  const submit = (e) => { e.preventDefault(); setSent(true); onSubmit && onSubmit(); };
  return (
    <section id="kontakt" style={cStyles.wrap}>
      <div style={cStyles.inner}>
        <div>
          <h3 style={cStyles.h}>Telefon &amp; e-post</h3>
          <div style={cStyles.line}>08 – 580 380 00</div>
          <div style={cStyles.line}><a href="mailto:hej@patriciatelesdds.com" style={cStyles.email}>hej@patriciatelesdds.com</a></div>
          <h3 style={{ ...cStyles.h, marginTop: 48 }}>Öppettider</h3>
          {[['Måndag','07:30 – 19:30'],['Tisdag','07:30 – 19:30'],['Onsdag','07:30 – 19:30'],['Torsdag','07:30 – 16:30'],['Fredag','07:30 – 17:00'],['Helger','Stängt']].map(([d,t]) => (
            <div key={d} style={cStyles.row}><span style={cStyles.day}>{d}</span><span>{t}</span></div>
          ))}
        </div>
        <div>
          <h3 style={{ ...cStyles.h, textAlign: 'center', marginBottom: 28 }}>Kontakta oss</h3>
          {sent ? (
            <p style={cStyles.thanks}>Tack! Vi hör av oss inom 24 timmar.</p>
          ) : (
            <form onSubmit={submit} style={cStyles.form}>
              <div style={cStyles.two}>
                <label style={cStyles.lbl}>Förnamn <span style={cStyles.req}>*</span><input style={cStyles.input} required/></label>
                <label style={cStyles.lbl}>Efternamn <span style={cStyles.req}>*</span><input style={cStyles.input} required/></label>
              </div>
              <div style={cStyles.two}>
                <label style={cStyles.lbl}>E-post <span style={cStyles.req}>*</span><input type="email" style={cStyles.input} required/></label>
                <label style={cStyles.lbl}>Telefon <span style={cStyles.req}>*</span><input style={cStyles.input} required/></label>
              </div>
              <label style={cStyles.lbl}>Ditt meddelande <span style={cStyles.req}>*</span>
                <textarea style={{ ...cStyles.input, minHeight: 110 }} required/>
              </label>
              <button type="submit" style={cStyles.submit}>Skicka</button>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}

const cStyles = {
  wrap: { background: 'var(--blush-200)', padding: '96px 0' },
  inner: { maxWidth: 1100, margin: '0 auto', padding: '0 32px', display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 80 },
  h: { fontFamily: 'var(--font-sans)', fontSize: 18, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.18em', color: 'var(--ink-700)', margin: '0 0 22px' },
  line: { fontFamily: 'var(--font-sans)', fontSize: 14, color: 'var(--blush-700)', marginBottom: 8 },
  email: { color: 'var(--blush-700)', textDecoration: 'underline', textUnderlineOffset: 3 },
  row: { display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontFamily: 'var(--font-sans)', fontSize: 14, color: 'var(--ink-600)', textTransform: 'uppercase', letterSpacing: '0.06em', maxWidth: 280 },
  day: { color: 'var(--fg-muted)' },
  form: { display: 'flex', flexDirection: 'column', gap: 18 },
  two: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 },
  lbl: { fontFamily: 'var(--font-sans)', fontSize: 13, color: 'var(--ink-700)', display: 'flex', flexDirection: 'column', gap: 6 },
  req: { color: 'var(--blush-600)' },
  input: { background: '#fff', border: '1px solid transparent', padding: '12px 14px', borderRadius: 4, fontFamily: 'var(--font-sans)', fontSize: 14, color: 'var(--ink-700)' },
  submit: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', background: 'var(--ink-700)', color: '#fff', border: 'none', padding: '14px 56px', borderRadius: 4, cursor: 'pointer', alignSelf: 'center' },
  thanks: { fontFamily: 'var(--font-serif)', fontSize: 24, textAlign: 'center', color: 'var(--ink-700)' },
};

window.Contact = Contact;
