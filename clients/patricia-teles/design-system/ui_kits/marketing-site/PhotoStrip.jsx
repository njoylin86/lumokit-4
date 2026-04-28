// PhotoStrip.jsx — full-bleed 5 image marquee
function PhotoStrip({ images }) {
  return (
    <section style={{ display: 'grid', gridTemplateColumns: `repeat(${images.length}, 1fr)`, gap: 0 }}>
      {images.map((src, i) => (
        <div key={i} style={{ aspectRatio: '1/1', overflow: 'hidden' }}>
          <img src={src} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}/>
        </div>
      ))}
    </section>
  );
}
window.PhotoStrip = PhotoStrip;
