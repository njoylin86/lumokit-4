// DigitalConsultation.jsx — pink form panel with stacked inputs
const { useState: useStateDC } = React;

function DigitalConsultation({ onSubmit }) {
  const [submitted, setSubmitted] = useStateDC(false);
  const [form, setForm] = useStateDC({ name: '', phone: '', email: '', body: '' });
  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const submit = (e) => {
    e.preventDefault();
    setSubmitted(true);
    onSubmit && onSubmit(form);
  };
  return (
    <section style={dcStyles.wrap}>
      <div style={dcStyles.inner}>
        <div className="eyebrow" style={dcStyles.eyebrow}>Behöver du hjälp?</div>
        <h2 style={dcStyles.title}>Digital konsultation</h2>
        {submitted ? (
          <p style={dcStyles.thanks}>Tack! Vi återkommer inom kort.</p>
        ) : (
          <form style={dcStyles.form} onSubmit={submit}>
            <label style={dcStyles.lbl}>Ange ditt namn <span style={dcStyles.req}>*</span>
              <input style={dcStyles.input} value={form.name} onChange={upd('name')} required/>
            </label>
            <label style={dcStyles.lbl}>Telefon <span style={dcStyles.req}>*</span>
              <input style={dcStyles.input} value={form.phone} onChange={upd('phone')} required/>
            </label>
            <label style={dcStyles.lbl}>E-post <span style={dcStyles.req}>*</span>
              <input type="email" style={dcStyles.input} value={form.email} onChange={upd('email')} required/>
            </label>
            <label style={dcStyles.lbl}>Beskriv ditt ärende <span style={dcStyles.req}>*</span>
              <textarea style={{...dcStyles.input, minHeight: 110, resize: 'vertical'}} value={form.body} onChange={upd('body')} required/>
            </label>
            <button style={dcStyles.upload} type="button">Välj bild +</button>
            <button style={dcStyles.submit} type="submit">Skicka in förfrågan</button>
          </form>
        )}
      </div>
    </section>
  );
}

const dcStyles = {
  wrap: { background: 'var(--blush-100)', padding: '96px 0' },
  inner: { maxWidth: 540, margin: '0 auto', padding: '0 32px', textAlign: 'center' },
  eyebrow: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', color: 'var(--blush-600)', marginBottom: 14 },
  title: { fontFamily: 'var(--font-serif)', fontWeight: 500, fontSize: 44, lineHeight: 1.1, letterSpacing: '-0.02em', color: 'var(--ink-700)', margin: '0 0 36px' },
  form: { display: 'flex', flexDirection: 'column', gap: 18, textAlign: 'left' },
  lbl: { fontFamily: 'var(--font-sans)', fontSize: 13, color: 'var(--ink-700)', display: 'flex', flexDirection: 'column', gap: 6 },
  req: { color: 'var(--blush-600)' },
  input: { background: '#fff', border: '1px solid transparent', padding: '12px 14px', borderRadius: 4, fontFamily: 'var(--font-sans)', fontSize: 14, color: 'var(--ink-700)' },
  upload: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', background: 'var(--ink-700)', color: '#fff', border: 'none', padding: '12px 28px', borderRadius: 4, cursor: 'pointer', alignSelf: 'center' },
  submit: { fontFamily: 'var(--font-sans)', fontSize: 11, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.22em', background: 'var(--ink-700)', color: '#fff', border: 'none', padding: '14px 32px', borderRadius: 4, cursor: 'pointer', alignSelf: 'center' },
  thanks: { fontFamily: 'var(--font-serif)', fontSize: 24, color: 'var(--ink-700)' },
};

window.DigitalConsultation = DigitalConsultation;
