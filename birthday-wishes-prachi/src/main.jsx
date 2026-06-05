import React from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const defaultMemories = [
  {
    title: 'Golden Smile',
    note: 'Prachi, tumhari smile har moment ko special bana deti hai.',
    gradient: 'linear-gradient(135deg, #ff8fb8, #ffd0a6)',
  },
  {
    title: 'Beautiful Soul',
    note: 'Aaj ka din sirf tumhare naam — full happiness, love aur surprises ke saath.',
    gradient: 'linear-gradient(135deg, #9775fa, #ff9fdb)',
  },
  {
    title: 'Dream Big',
    note: 'May your year be as bright as candles and as sweet as cake.',
    gradient: 'linear-gradient(135deg, #f6c85f, #ff7d7d)',
  },
]

const wishHighlights = [
  'Har subah ek nayi smile ke saath start ho',
  'Har dream ke saath universe tumhara support kare',
  'Har moment mein love, luck aur magic ho',
  'Prachi, tumhari birthday party memories forever shine karein',
]

const confettiPieces = Array.from({ length: 42 }, (_, index) => ({
  id: index,
  left: `${(index * 23) % 100}%`,
  delay: `${(index % 11) * 0.35}s`,
  duration: `${5 + (index % 7) * 0.45}s`,
  hue: (index * 37) % 360,
}))

function App() {
  const [photos, setPhotos] = React.useState([])
  const [surpriseOpen, setSurpriseOpen] = React.useState(false)
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
      <AnimatedBackdrop />
      <ConfettiRain />

      <section className="hero-section" aria-label="Birthday landing page for Prachi">
        <div className="hero-content reveal-up">
          <p className="eyebrow"><Icon label="sparkles" symbol="✦" /> Special Birthday Wish</p>
          <h1>Happy Birthday, <span>Prachi</span>!</h1>
          <p className="hero-message">
            Tumhari life ka har din flowers ki tarah beautiful, stars ki tarah bright aur cake ki tarah sweet ho.
            Aaj ka pura celebration sirf tumhare liye hai!
          </p>

          <div className="hero-actions">
            <a href="#photos" className="primary-button"><Icon label="camera" symbol="📸" /> Add Photos</a>
            <a href="#surprise" className="secondary-button"><Icon label="heart" symbol="♥" /> Open Surprise</a>
          </div>
        </div>

        <div className="birthday-card reveal-up delay-one" id="wish">
          <div className="card-glow" />
          <div className="sparkle-ring" />
          <div className="card-icon" aria-hidden="true">🎉</div>
          <h2>Dear Prachi</h2>
          <p>
            Bhagwan kare tumhari har wish complete ho, har dream reality bane aur tumhari smile hamesha aise hi shine karti rahe.
            Happy Birthday, queen!
          </p>
          <div className="candle-cake" aria-hidden="true">
            <div className="flames"><span /><span /><span /></div>
            <div className="cake-layer top" />
            <div className="cake-layer middle" />
            <div className="cake-layer bottom" />
          </div>
        </div>
      </section>

      <section className="marquee-strip" aria-label="Animated birthday wishes">
        <div>
          <span>Happy Birthday Prachi ✦</span>
          <span>Stay blessed always ✦</span>
          <span>Keep shining queen ✦</span>
          <span>Lots of love & smiles ✦</span>
          <span aria-hidden="true">Happy Birthday Prachi ✦</span>
          <span aria-hidden="true">Stay blessed always ✦</span>
          <span aria-hidden="true">Keep shining queen ✦</span>
          <span aria-hidden="true">Lots of love & smiles ✦</span>
        </div>
      </section>

      <section className="stats-strip" aria-label="Birthday highlights">
        <div><strong>365</strong><span>Days of joy</span></div>
        <div><strong>∞</strong><span>Smiles for Prachi</span></div>
        <div><strong>100%</strong><span>Love & blessings</span></div>
      </section>

      <section className="surprise-section" id="surprise">
        <div className="surprise-copy">
          <p><Icon label="gift" symbol="🎁" /> Birthday Surprise</p>
          <h2>Ek chhota sa magical note</h2>
          <p>
            Button dabao aur Prachi ke liye ek animated surprise message open karo — bilkul birthday card jaisa feel.
          </p>
          <button className="primary-button surprise-button" type="button" onClick={() => setSurpriseOpen((open) => !open)}>
            <Icon label="sparkles" symbol="✨" /> {surpriseOpen ? 'Hide Magic' : 'Reveal Magic'}
          </button>
        </div>
        <div className={`surprise-envelope ${surpriseOpen ? 'is-open' : ''}`}>
          <div className="envelope-lid" />
          <div className="letter">
            <span>For Prachi</span>
            <strong>May your birthday bring unlimited happiness, cute surprises, and memories that feel like fairy lights.</strong>
          </div>
        </div>
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

      <section className="wish-orbit-section" aria-label="Animated wish highlights">
        <div className="orbit-center">
          <span>Prachi</span>
          <strong>Birthday Glow</strong>
        </div>
        <div className="wish-list">
          {wishHighlights.map((wish, index) => (
            <article className="wish-pill" key={wish} style={{ '--delay': `${index * 0.18}s` }}>
              <Icon label="sparkles" symbol="✦" /> {wish}
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

function ConfettiRain() {
  return (
    <div className="confetti-rain" aria-hidden="true">
      {confettiPieces.map((piece) => (
        <span
          key={piece.id}
          style={{
            '--left': piece.left,
            '--delay': piece.delay,
            '--duration': piece.duration,
            '--color': `hsl(${piece.hue}, 92%, 64%)`,
          }}
        />
      ))}
    </div>
  )
}

function AnimatedBackdrop() {
  return (
    <div className="floating-decorations" aria-hidden="true">
      <span className="blob blob-one" />
      <span className="blob blob-two" />
      <span className="blob blob-three" />
      <span className="balloon balloon-one">🎈</span>
      <span className="balloon balloon-two">💝</span>
      <span className="balloon balloon-three">🎀</span>
      <span className="heart heart-one">♥</span>
      <span className="heart heart-two">✦</span>
      <span className="heart heart-three">★</span>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
