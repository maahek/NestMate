import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import { listingsAPI } from '../api/listings'
import ListingCard from '../components/listings/ListingCard'
import Spinner from '../components/ui/Spinner'

const CITIES = ['Mumbai', 'Pune', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad']

const FEATURES = [
  { icon: '🤝', title: 'AI Roommate Matching',   desc: 'Find compatible roommates using our personality and lifestyle algorithm.' },
  { icon: '✅', title: 'Verified Listings',       desc: 'Every listing gets a Trust Score based on ID, bill, and video proof.' },
  { icon: '💰', title: 'AI Price Estimator',      desc: 'Know instantly if a listing is fairly priced vs market rent.' },
  { icon: '🗺️', title: 'Map-Based Search',        desc: 'Find houses near metro, college, or office on an interactive map.' },
  { icon: '🌍', title: 'Environment Score',        desc: 'See area safety, noise level, and nearby hospitals and stops.' },
  { icon: '🎬', title: 'Virtual House Tour',       desc: 'Explore 360° video walkthroughs without visiting in person.' },
  { icon: '⚠️', title: 'Scam Detection',           desc: 'Suspicious listings are automatically flagged before you see them.' },
  { icon: '🎓', title: 'Student Rentals',          desc: 'Short-term rooms near colleges under your budget.' },
  { icon: '📄', title: 'Instant Agreement PDF',    desc: 'Generate and e-sign a rental agreement in minutes.' },
  { icon: '💬', title: 'Negotiation Chat',         desc: 'Chat, make offers, and close deals — all inside NestMate.' },
]

const STEPS = [
  { icon: '🔍', num: '01', title: 'Search & Filter',  desc: 'Use AI-powered search with trust score filters, map view, and fair price indicators.' },
  { icon: '💬', num: '02', title: 'Chat & Negotiate',  desc: 'Chat directly with owners, make offers, and negotiate rent — all inside NestMate.' },
  { icon: '📄', num: '03', title: 'Sign Agreement',    desc: 'Generate a professional PDF agreement instantly and sign it digitally.' },
]

export default function Home() {
  const [featured, setFeatured] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [city,     setCity]     = useState('')
  const [type,     setType]     = useState('')
  const [maxRent,  setMaxRent]  = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    listingsAPI.search({ limit: 6, sort: 'newest' })
      .then(r  => setFeatured(r.data.listings || []))
      .catch(() => setFeatured([]))
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (city)    params.set('city',     city)
    if (type)    params.set('type',     type)
    if (maxRent) params.set('max_rent', maxRent)
    navigate(`/search?${params.toString()}`)
  }

  return (
    <div style={{ fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── HERO ──────────────────────────────────────────────────── */}
      <section style={{
        minHeight: '88vh',
        background: '#fffbf5',
        display: 'flex',
        alignItems: 'center',
        padding: '4rem 5vw',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background decoration */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'radial-gradient(ellipse 65% 80% at 80% 50%, rgba(254,243,199,0.7) 0%, transparent 70%)',
        }} />

        <div style={{
          maxWidth: 1280, margin: '0 auto', width: '100%',
          display: 'grid', gridTemplateColumns: '1fr 1fr',
          gap: '4rem', alignItems: 'center',
        }}>
          <div>
            {/* Eyebrow */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: '#fef3c7', color: '#d97706',
              padding: '6px 16px', borderRadius: 99,
              fontSize: 11, fontWeight: 700, letterSpacing: '0.08em',
              textTransform: 'uppercase', marginBottom: 20,
            }}>
              ✨ AI-Powered Rental Platform
            </div>

            {/* Title */}
            <h1 style={{
              fontFamily: "'Fraunces', Georgia, serif",
              fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
              fontWeight: 900, lineHeight: 1.15,
              color: '#0f172a', marginBottom: 20,
            }}>
              Find Your<br />
              <span style={{ color: '#d97706', fontStyle: 'italic' }}>Perfect Nest</span><br />
              in India
            </h1>

            {/* Subtitle */}
            <p style={{
              fontSize: '1.1rem', color: '#78716c',
              lineHeight: 1.7, marginBottom: 32, maxWidth: 480,
            }}>
              Verified listings, AI roommate matching, fair price estimates,
              and scam detection — all in one place.
            </p>

            {/* Buttons */}
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 48 }}>
              <Link to="/search" style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: '#0f172a', color: '#fff',
                padding: '14px 32px', borderRadius: 99,
                fontWeight: 700, fontSize: '1rem', textDecoration: 'none',
                transition: 'all 0.2s',
              }}>
                Browse Homes
              </Link>
              <Link to="/roommate/quiz" style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: 'transparent', color: '#0f172a',
                padding: '14px 32px', borderRadius: 99,
                fontWeight: 700, fontSize: '1rem', textDecoration: 'none',
                border: '1.5px solid #e7e5e4',
              }}>
                🤝 Find Roommate
              </Link>
            </div>

            {/* Stats */}
            <div style={{
              display: 'flex', gap: 40,
              paddingTop: 32, borderTop: '1px solid #e7e5e4',
              flexWrap: 'wrap',
            }}>
              {[
                { num: '12,400+', label: 'Verified Listings' },
                { num: '98%',     label: 'Scam-Free Rate'    },
                { num: '8',       label: 'Major Cities'       },
              ].map(s => (
                <div key={s.label}>
                  <div style={{ fontFamily: "'Fraunces', serif", fontSize: '2.2rem', fontWeight: 900, color: '#0f172a', lineHeight: 1 }}>
                    {s.num}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#78716c', marginTop: 4 }}>
                    {s.label}
                  </div>
                </div>
              ))}
           </div>
          </div>

          {/* ── Right side preview cards ── */}
          <div className="hero-cards" style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr',
            gap: '1rem',
          }}>
            {[
              {
                img:   'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80',
                price: '₹22,000',
                loc:   'Koramangala, Bangalore',
                trust: 92,
                span:  true,
                h:     220,
              },
              {
                img:   'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&q=80',
                price: '₹8,500',
                loc:   'Wakad, Pune',
                trust: 88,
                span:  false,
                h:     160,
              },
              {
                img:   'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&q=80',
                price: '₹6,000',
                loc:   'Anna Nagar, Chennai',
                trust: 76,
                span:  false,
                h:     160,
              },
            ].map((card, i) => (
              <div
                key={i}
                style={{
                  background:   '#fff',
                  borderRadius: 16,
                  overflow:     'hidden',
                  boxShadow:    '0 12px 48px rgba(15,23,42,0.14)',
                  border:       '1px solid #f1f5f9',
                  transition:   'transform 0.3s',
                  gridColumn:   card.span ? '1 / -1' : 'span 1',
                }}
                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <img
                  src={card.img}
                  alt="Property"
                  style={{ width: '100%', height: card.h, objectFit: 'cover', display: 'block' }}
                />
                <div style={{ padding: '0.9rem' }}>
                  <div style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.2rem', color: '#0f172a' }}>
                    {card.price}<span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#78716c', fontFamily: "'DM Sans', sans-serif" }}>/mo</span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#78716c', margin: '2px 0 6px' }}>
                    📍 {card.loc}
                  </div>
                  <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: 4,
                    background: '#dcfce7', color: '#15803d',
                    borderRadius: 99, padding: '2px 10px',
                    fontSize: '0.7rem', fontWeight: 700,
                  }}>
                    ✅ Trust {card.trust}/100
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <style>{`
        @media (max-width: 900px) {
          .hero-cards { display: none !important; }
        }
      `}</style>
      </section>

      {/* ── SEARCH BAR ───────────────────────────────────────────── */}
      <div style={{ padding: '0 5vw', marginTop: -28, position: 'relative', zIndex: 10, marginBottom: 64 }}>
        <form
          onSubmit={handleSearch}
          style={{
            background: '#fff', borderRadius: 20,
            boxShadow: '0 12px 48px rgba(15,23,42,0.14)',
            border: '1px solid #f1f5f9',
            padding: '1.5rem',
            display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end',
            maxWidth: 900, margin: '0 auto',
          }}
        >
          {/* City */}
          <div style={{ flex: 1, minWidth: 140, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 11, fontWeight: 700, color: '#78716c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              City
            </label>
            <select
              value={city}
              onChange={e => setCity(e.target.value)}
              style={{ border: '1.5px solid #e7e5e4', borderRadius: 12, padding: '10px 14px', fontSize: '0.9rem', outline: 'none', background: '#fff', cursor: 'pointer' }}
            >
              <option value="">Any City</option>
              {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {/* Type */}
          <div style={{ flex: 1, minWidth: 140, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 11, fontWeight: 700, color: '#78716c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Type
            </label>
            <select
              value={type}
              onChange={e => setType(e.target.value)}
              style={{ border: '1.5px solid #e7e5e4', borderRadius: 12, padding: '10px 14px', fontSize: '0.9rem', outline: 'none', background: '#fff', cursor: 'pointer' }}
            >
              <option value="">All Types</option>
              <optgroup label="Residential">
                {['apartment','house','villa','studio','pg','shared_room','hostel'].map(t => (
                  <option key={t} value={t}>{t.replace(/_/g,' ')}</option>
                ))}
              </optgroup>
              <optgroup label="Commercial">
                {['shop','office','warehouse','showroom','coworking'].map(t => (
                  <option key={t} value={t}>{t.replace(/_/g,' ')}</option>
                ))}
              </optgroup>
            </select>
          </div>

          {/* Max Rent */}
          <div style={{ flex: 1, minWidth: 140, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 11, fontWeight: 700, color: '#78716c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Max Rent (₹)
            </label>
            <input
              type="number"
              value={maxRent}
              onChange={e => setMaxRent(e.target.value)}
              placeholder="e.g. 15000"
              style={{ border: '1.5px solid #e7e5e4', borderRadius: 12, padding: '10px 14px', fontSize: '0.9rem', outline: 'none', background: '#fff' }}
              min="0"
            />
          </div>

          <button
            type="submit"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: '#d97706', color: '#fff',
              padding: '11px 28px', borderRadius: 99,
              fontWeight: 700, fontSize: '0.95rem', border: 'none', cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            <Search size={16} /> Search
          </button>
        </form>
      </div>

      {/* ── FEATURED LISTINGS ────────────────────────────────────── */}
      <section style={{ padding: '0 5vw 80px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 32, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h2 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.8rem,4vw,2.8rem)', color: '#0f172a' }}>
              Featured Homes
            </h2>
            <p style={{ color: '#78716c', marginTop: 4 }}>Handpicked verified listings with high trust scores</p>
          </div>
          <Link to="/search" style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '10px 24px', borderRadius: 99,
            border: '1.5px solid #e7e5e4', color: '#0f172a',
            fontWeight: 600, fontSize: '0.88rem', textDecoration: 'none',
          }}>
            View All →
          </Link>
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '80px 0' }}>
            <Spinner size="lg" />
          </div>
        ) : featured.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: 24 }}>
            {featured.map(l => <ListingCard key={l.id} listing={l} />)}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#78716c' }}>
            <div style={{ fontSize: '3rem', marginBottom: 16 }}>🏠</div>
            <p>No listings yet. <Link to="/listing/create" style={{ color: '#d97706' }}>Be the first to list!</Link></p>
          </div>
        )}
      </section>

      {/* ── FEATURES GRID ────────────────────────────────────────── */}
      <section style={{ background: '#0f172a', padding: '80px 5vw' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.8rem,4vw,2.8rem)', color: '#fff', marginBottom: 12 }}>
              Why NestMate?
            </h2>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '1.05rem' }}>
              10 powerful features that make us different
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 16 }}>
            {FEATURES.map((f) => (
              <div key={f.title} style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 16, padding: '1.75rem',
                transition: 'background 0.2s',
              }}>
                <div style={{ fontSize: '2rem', marginBottom: 12 }}>{f.icon}</div>
                <h3 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, marginBottom: 8, lineHeight: 1.3 }}>
                  {f.title}
                </h3>
                <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: '0.82rem', lineHeight: 1.7 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────────── */}
      <section style={{ padding: '80px 5vw', background: '#fffbf5' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.8rem,4vw,2.8rem)', color: '#0f172a', marginBottom: 48 }}>
            Find Your Home in 3 Steps
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 40 }}>
            {STEPS.map(s => (
              <div key={s.num}>
                <div style={{
                  width: 64, height: 64, borderRadius: '50%',
                  background: '#fef3c7', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.8rem', margin: '0 auto 16px',
                }}>
                  {s.icon}
                </div>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#d97706', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
                  Step {s.num}
                </div>
                <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.2rem', color: '#0f172a', marginBottom: 8 }}>
                  {s.title}
                </h3>
                <p style={{ color: '#78716c', fontSize: '0.88rem', lineHeight: 1.7 }}>
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ROOMMATE CTA ─────────────────────────────────────────── */}
      <section style={{
        background: 'linear-gradient(135deg, #d97706 0%, #92400e 100%)',
        padding: '80px 5vw', textAlign: 'center',
      }}>
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
          <div style={{ fontSize: '3.5rem', marginBottom: 16 }}>🤝</div>
          <h2 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.8rem,4vw,2.8rem)', color: '#fff', marginBottom: 16 }}>
            Looking for a Roommate?
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.85)', fontSize: '1.05rem', marginBottom: 32, lineHeight: 1.7 }}>
            Our AI matches you with compatible roommates based on budget, lifestyle, and personality.
          </p>
          <Link to="/roommate/quiz" style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: '#fff', color: '#0f172a',
            padding: '14px 36px', borderRadius: 99,
            fontWeight: 700, fontSize: '1rem', textDecoration: 'none',
            boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
          }}>
            Take the Compatibility Quiz →
          </Link>
        </div>
      </section>
    </div>
  )
}