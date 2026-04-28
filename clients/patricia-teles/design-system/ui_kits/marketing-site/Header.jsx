// Header.jsx — sticky top navigation
const { useState } = React;

function Header({ currentPage, onNavigate, onBook }) {
  const [open, setOpen] = useState(false);
  const navLinks = [
    { id: 'behandlingar', label: 'Behandlingar' },
    { id: 'om-oss', label: 'Om oss' },
    { id: 'priser', label: 'Priser' },
    { id: 'kontakt', label: 'Kontakt' },
  ];

  return (
    <header style={headerStyles.bar}>
      <div style={headerStyles.inner}>
        <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('hem'); }} style={headerStyles.logoLink}>
          <img src="../../assets/logo.svg" alt="Patricia Teles" style={{ height: 44 }} />
        </a>
        <nav style={headerStyles.nav}>
          {navLinks.map(l => (
            <a key={l.id}
               href={`#${l.id}`}
               onClick={(e) => { e.preventDefault(); onNavigate(l.id); }}
               style={{
                 ...headerStyles.link,
                 color: currentPage === l.id ? 'var(--blush-600)' : 'var(--ink-700)',
               }}>
              {l.label}
            </a>
          ))}
          <button onClick={onBook} style={headerStyles.cta}>Boka tid</button>
          <div style={headerStyles.flags}>
            <span style={headerStyles.flag}>🇸🇪</span>
            <span style={{ ...headerStyles.flag, opacity: 0.5 }}>🇬🇧</span>
          </div>
        </nav>
      </div>
    </header>
  );
}

const headerStyles = {
  bar: {
    position: 'sticky', top: 0, zIndex: 50,
    background: '#fff',
    borderBottom: '1px solid var(--border)',
  },
  inner: {
    maxWidth: 1280, margin: '0 auto', padding: '18px 32px',
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  },
  logoLink: { textDecoration: 'none' },
  nav: { display: 'flex', alignItems: 'center', gap: 28 },
  link: {
    fontFamily: 'var(--font-sans)', fontSize: 11,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    fontWeight: 500, textDecoration: 'none',
    transition: 'color var(--dur-fast) var(--ease-standard)',
  },
  cta: {
    fontFamily: 'var(--font-sans)', fontSize: 11,
    textTransform: 'uppercase', letterSpacing: '0.22em',
    fontWeight: 500, color: '#fff', background: 'var(--ink-700)',
    border: 'none', padding: '14px 24px', borderRadius: 4, cursor: 'pointer',
    transition: 'background var(--dur-fast) var(--ease-standard)',
  },
  flags: { display: 'flex', gap: 6, fontSize: 14 },
  flag: { cursor: 'pointer' },
};

window.Header = Header;
