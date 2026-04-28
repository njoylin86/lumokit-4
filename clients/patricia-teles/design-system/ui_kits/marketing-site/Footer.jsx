// Footer.jsx — centered low-key footer
function Footer() {
  return (
    <footer style={fStyles.wrap}>
      <img src="../../assets/logo.svg" alt="Patricia Teles" style={{ height: 40, opacity: 0.7 }}/>
      <div style={fStyles.icons}>
        <a href="#" aria-label="Instagram" style={fStyles.icon}>
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.6" fill="currentColor"/></svg>
        </a>
        <a href="#" aria-label="Facebook" style={fStyles.icon}>
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
        </a>
      </div>
      <div style={fStyles.meta}>
        PATRICIA TELES DDS &nbsp;|&nbsp; HAGAESPLANADEN 64B &nbsp;|&nbsp; 113 66 STOCKHOLM &nbsp;|&nbsp; 08-580 380 00 &nbsp;|&nbsp; <a href="#" style={fStyles.link}>Kontakt</a> &nbsp;|&nbsp; ORG.NR 559211-2543
      </div>
    </footer>
  );
}

const fStyles = {
  wrap: { padding: '56px 32px 80px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, background: '#fff' },
  icons: { display: 'flex', gap: 10 },
  icon: { width: 28, height: 28, borderRadius: 999, border: '1px solid var(--fg-subtle)', color: 'var(--fg-muted)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', textDecoration: 'none' },
  meta: { fontFamily: 'var(--font-sans)', fontSize: 11, color: 'var(--fg-muted)', letterSpacing: '0.1em', textTransform: 'uppercase' },
  link: { color: 'var(--blush-600)', textDecoration: 'underline' },
};

window.Footer = Footer;
