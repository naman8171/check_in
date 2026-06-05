import React from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const defaultMemories = [
  {
    title: 'Golden Smile',
    note: 'Prachi, tumhari smile har moment ko special bana deti hai.',
    gradient: 'linear-gradient(135deg, #ff9a9e, #fad0c4)',
  },
  {
    title: 'Beautiful Soul',
    note: 'Aaj ka din sirf tumhare naam — full happiness, love aur surprises ke saath.',
    gradient: 'linear-gradient(135deg, #a18cd1, #fbc2eb)',
  },
  {
    title: 'Dream Big',
    note: 'May your year be as bright as candles and as sweet as cake.',
    gradient: 'linear-gradient(135deg, #f6d365, #fda085)',
  },
]

function App() {
  const [photos, setPhotos] = React.useState([])
  const objectUrls = React.useRef([])

  const handleImageUpload = (event) => {
    const files = Array.from(event.target.files || [])

    const imageFiles = files.filter((file) => file.type.startsWith('image/'))
    const previews = imageFiles.map((file) => {
      const src = URL.createObjectURL(file)
      objectUrls.current.push(src)

      return {
        id: `${file.name}-${file.lastModified}-${crypto.randomUUID()}`,
        name: file.name,
        src,
      }
    })

    setPhotos((currentPhotos) => [...previews, ...currentPhotos])
    event.target.value = ''
  }

  React.useEffect(() => {
    return () => {
      objectUrls.current.forEach((src) => URL.revokeObjectURL(src))
    }
  }, [])

  return (
    <main className="page-shell">
      <FloatingDecorations />

      <section className="hero-section" aria-label="Birthday landing page for Prachi">
        <div className="hero-content">
          <p className="eyebrow"><Icon label="sparkles" symbol="✦" /> Special Birthday Wish</p>
          <h1>Happy Birthday, <span>Prachi</span>!</h1>
          <p className="hero-message">
            Tumhari life ka har din flowers ki tarah beautiful, stars ki tarah bright aur cake ki tarah sweet ho.
            Aaj ka pura celebration sirf tumhare liye hai!
          </p>

          <div className="hero-actions">
            <a href="#photos" className="primary-button"><Icon label="camera" symbol="📸" /> Add Photos</a>
            <a href="#wish" className="secondary-button"><Icon label="heart" symbol="♥" /> Read Wish</a>
          </div>
        </div>

        <div className="birthday-card" id="wish">
          <div className="card-glow" />
          <div className="card-icon" aria-hidden="true">🎉</div>
          <h2>Dear Prachi</h2>
          <p>
            Bhagwan kare tumhari har wish complete ho, har dream reality bane aur tumhari smile hamesha aise hi shine karti rahe.
            Happy Birthday, queen!
          </p>
          <div className="cake">
            <span />
            <span />
            <span />
          </div>
        </div>
      </section>

      <section className="stats-strip" aria-label="Birthday highlights">
        <div><strong>365</strong><span>Days of joy</span></div>
        <div><strong>∞</strong><span>Smiles for Prachi</span></div>
        <div><strong>100%</strong><span>Love & blessings</span></div>
      </section>

      <section className="memory-section">
        <div className="section-heading">
          <p><Icon label="gift" symbol="🎁" /> Celebration Moments</p>
          <h2>Prachi ke liye sweet memories</h2>
        </div>

        <div className="memory-grid">
          {defaultMemories.map((memory) => (
            <article className="memory-card" key={memory.title} style={{ '--card-bg': memory.gradient }}>
              <Icon label="star" symbol="★" />
              <h3>{memory.title}</h3>
              <p>{memory.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="photo-section" id="photos">
        <div className="photo-copy">
          <p><Icon label="image" symbol="🖼️" /> Custom Photo Gallery</p>
          <h2>Apni images add karo</h2>
          <p>
            Neeche upload button se Prachi ki photos ya birthday memories add kar sakte ho. Select karte hi photos page par preview ho jayengi.
          </p>
          <label className="upload-button">
            <input type="file" accept="image/*" multiple onChange={handleImageUpload} />
            <Icon label="image" symbol="🖼️" /> Choose Birthday Images
          </label>
        </div>

        <div className="photo-gallery" aria-live="polite">
          {photos.length === 0 ? (
            <div className="empty-gallery">
              <div className="empty-icon" aria-hidden="true">📷</div>
              <h3>No photos yet</h3>
              <p>Prachi ki best photos upload karke yahan beautiful gallery bana do.</p>
            </div>
          ) : (
            photos.map((photo) => (
              <figure className="uploaded-photo" key={photo.id}>
                <img src={photo.src} alt={`Uploaded birthday memory: ${photo.name}`} />
                <figcaption>{photo.name}</figcaption>
              </figure>
            ))
          )}
        </div>
      </section>
    </main>
  )
}

function Icon({ label, symbol }) {
  return <span className="inline-icon" role="img" aria-label={label}>{symbol}</span>
}

function FloatingDecorations() {
  return (
    <div className="floating-decorations" aria-hidden="true">
      <span className="bubble bubble-one" />
      <span className="bubble bubble-two" />
      <span className="bubble bubble-three" />
      <span className="heart heart-one">♥</span>
      <span className="heart heart-two">✦</span>
      <span className="heart heart-three">★</span>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
