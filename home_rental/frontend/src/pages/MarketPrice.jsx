import { useState, useEffect } from 'react'
import { listingsAPI } from '../api/listings'
import { CITIES } from '../utils/constants'
// Spinner not used

const SEED_DATA = {
  Mumbai:    { apartment: { '1bhk': 25000, '2bhk': 42000 }, pg: { '1': 9000 } },
  Pune:      { apartment: { '1bhk': 13000, '2bhk': 21000 }, pg: { '1': 6000 } },
  Bangalore: { apartment: { '1bhk': 20000, '2bhk': 34000 }, pg: { '1': 8000 } },
  Delhi:     { apartment: { '1bhk': 16000, '2bhk': 28000 }, pg: { '1': 7000 } },
  Hyderabad: { apartment: { '1bhk': 14000, '2bhk': 24000 }, pg: { '1': 6500 } },
  Chennai:   { apartment: { '1bhk': 14000, '2bhk': 22000 }, pg: { '1': 6000 } },
  Kolkata:   { apartment: { '1bhk': 10000, '2bhk': 16000 }, pg: { '1': 5000 } },
  Ahmedabad: { apartment: { '1bhk': 11000, '2bhk': 18000 }, pg: { '1': 5500 } },
}

export default function MarketPrice() {
  const [city,     setCity]     = useState('Mumbai')
  const [type,     setType]     = useState('apartment')
  const [bedrooms, setBedrooms] = useState('1')
  const [rent,     setRent]     = useState('')
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [listings, setListings] = useState([])

  useEffect(() => {
    listingsAPI.search({ city, type, bedrooms, limit: 12 })
      .then(r => setListings(r.data.listings || []))
      .catch(() => setListings([]))
  }, [city, type, bedrooms])

  const checkPrice = async (e) => {
    e.preventDefault()
    if (!rent) return
    setLoading(true)
    try {
      const res = await listingsAPI.priceCheck({ city, type, bedrooms, rent })
      setResult(res.data)
    } catch {
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const cityData  = SEED_DATA[city] || {}
  const typeData  = cityData[type]  || {}
  const avg1bhk   = typeData['1bhk'] || typeData['1'] || 0
  const avg2bhk   = typeData['2bhk'] || 0

  const verdictStyle = (verdict) => ({
    fair:       { background: '#dcfce7', color: '#15803d', border: '1px solid #86efac' },
    overpriced: { background: '#fee2e2', color: '#b91c1c', border: '1px solid #fca5a5' },
    underpriced:{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a' },
    unknown:    { background: '#f1f5f9', color: '#64748b', border: '1px solid #e2e8f0' },
  }[verdict] || { background: '#f1f5f9', color: '#64748b', border: '1px solid #e2e8f0' })

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '2.5rem 2rem 4rem', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(2rem,4vw,3rem)', color: '#0f172a', marginBottom: 8 }}>
          📊 Market Rent Dashboard
        </h1>
        <p style={{ color: '#78716c', fontSize: '1.05rem' }}>
          Compare rents across cities and check if a listing is fairly priced
        </p>
      </div>

      {/* Filters */}
      <div style={{
        background: '#fff', borderRadius: 16, padding: '1.5rem',
        boxShadow: '0 4px 24px rgba(15,23,42,0.08)',
        border: '1px solid #f1f5f9', marginBottom: 32,
        display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end',
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1, minWidth: 120 }}>
          <label style={{ fontSize: 11, fontWeight: 700, color: '#78716c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>City</label>
          <select value={city} onChange={e => setCity(e.target.value)}
            style={{ border: '1.5px solid #e7e5e4', borderRadius: 10, padding: '10px 12px', fontSize: '0.9rem', outline: 'none', background: '#fff' }}>
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1, minWidth: 120 }}>
          <label style={{ fontSize: 11, fontWeight: 700, color: '#78716c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Type</label>
          <select value={type} onChange={e => setType(e.target.value)}
            style={{ border: '1.5px solid #e7e5e4', borderRadius: 10, padding: '10px 12px', fontSize: '0.9rem', outline: 'none', background: '#fff' }}>
            <option value="apartment">Apartment</option>
            <option value="house">House</option>
            <option value="pg">PG</option>
            <option value="studio">Studio</option>
            <option value="shop">Shop</option>
            <option value="office">Office</option>
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1, minWidth: 100 }}>
          <label style={{ fontSize: 11, fontWeight: 700, color: '#78716c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Bedrooms</label>
          <select value={bedrooms} onChange={e => setBedrooms(e.target.value)}
            style={{ border: '1.5px solid #e7e5e4', borderRadius: 10, padding: '10px 12px', fontSize: '0.9rem', outline: 'none', background: '#fff' }}>
            <option value="1">1 BHK</option>
            <option value="2">2 BHK</option>
            <option value="3">3 BHK</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 24, marginBottom: 40 }}>

        {/* Market Rate Card */}
        <div style={{ background: '#0f172a', borderRadius: 20, padding: '2rem', color: '#fff', gridColumn: 'span 1' }}>
          <h3 style={{ fontFamily: "'Fraunces', serif", color: '#fff', fontSize: '1.1rem', marginBottom: 20 }}>
            📍 {city} Market Rates
          </h3>
          {avg1bhk > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>1 BHK Average</div>
                <div style={{ fontFamily: "'Fraunces', serif", fontSize: '2rem', fontWeight: 900, color: '#fbbf24' }}>
                  ₹{avg1bhk.toLocaleString('en-IN')}<span style={{ fontSize: '0.9rem', fontWeight: 400, color: 'rgba(255,255,255,0.6)' }}>/mo</span>
                </div>
              </div>
              {avg2bhk > 0 && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>2 BHK Average</div>
                  <div style={{ fontFamily: "'Fraunces', serif", fontSize: '2rem', fontWeight: 900, color: '#fbbf24' }}>
                    ₹{avg2bhk.toLocaleString('en-IN')}<span style={{ fontSize: '0.9rem', fontWeight: 400, color: 'rgba(255,255,255,0.6)' }}>/mo</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: 'rgba(255,255,255,0.5)' }}>No data available for this combination</p>
          )}
        </div>

        {/* Price Checker Card */}
        <div style={{ background: '#fff', borderRadius: 20, padding: '2rem', boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9' }}>
          <h3 style={{ fontFamily: "'Fraunces', serif", color: '#0f172a', fontSize: '1.1rem', marginBottom: 16 }}>
            💰 Is This Rent Fair?
          </h3>
          <form onSubmit={checkPrice} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <input
              type="number"
              value={rent}
              onChange={e => setRent(e.target.value)}
              placeholder={`Enter rent (e.g. ₹${avg1bhk.toLocaleString('en-IN')})`}
              style={{ border: '1.5px solid #e7e5e4', borderRadius: 10, padding: '10px 14px', fontSize: '0.9rem', outline: 'none' }}
              min="0"
            />
            <button type="submit" style={{
              background: '#d97706', color: '#fff', border: 'none',
              borderRadius: 99, padding: '10px 20px',
              fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer',
            }}>
              {loading ? 'Checking...' : '🔍 Check Price'}
            </button>
          </form>

          {result && (
            <div style={{ marginTop: 16, padding: '1rem', borderRadius: 10, borderLeft: '4px solid', ...verdictStyle(result.verdict) }}>
              <div style={{ fontWeight: 700, marginBottom: 4 }}>
                {result.verdict === 'fair'        && '✅ Fair Market Price'}
                {result.verdict === 'overpriced'  && `⚠️ ${result.label}`}
                {result.verdict === 'underpriced' && `📉 ${result.label}`}
                {result.verdict === 'unknown'     && '❓ Insufficient Data'}
              </div>
              {result.market_rent && (
                <div style={{ fontSize: '0.82rem', marginTop: 4 }}>
                  Market rate: ₹{result.market_rent.toLocaleString('en-IN')}/mo
                </div>
              )}
              {result.explanation && (
                <div style={{ fontSize: '0.78rem', marginTop: 6, opacity: 0.8 }}>
                  {result.explanation}
                </div>
              )}
            </div>
          )}
        </div>

        {/* City Comparison Card */}
        <div style={{ background: '#fff', borderRadius: 20, padding: '2rem', boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9' }}>
          <h3 style={{ fontFamily: "'Fraunces', serif", color: '#0f172a', fontSize: '1.1rem', marginBottom: 16 }}>
            🏙️ City Comparison (1BHK Apt)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {Object.entries(SEED_DATA).map(([c, d]) => {
              const avgRent = d.apartment?.['1bhk'] || 0
              const max     = 45000
              const pct     = Math.round((avgRent / max) * 100)
              return (
                <div key={c}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: 4 }}>
                    <span style={{ color: c === city ? '#d97706' : '#0f172a', fontWeight: c === city ? 700 : 400 }}>{c}</span>
                    <span style={{ color: '#78716c' }}>₹{avgRent.toLocaleString('en-IN')}/mo</span>
                  </div>
                  <div style={{ height: 6, background: '#f1f5f9', borderRadius: 99, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', width: `${pct}%`, borderRadius: 99,
                      background: c === city ? '#d97706' : '#0f172a',
                      transition: 'width 0.6s ease',
                    }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Live Listings */}
      <div>
        <h2 style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.8rem', color: '#0f172a', marginBottom: 20 }}>
          Live Listings in {city}
        </h2>
        {listings.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
            {listings.slice(0, 6).map(l => (
              <div key={l.id} style={{ background: '#fff', borderRadius: 16, overflow: 'hidden', boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9' }}>
                <img
                  src={l.thumb || l.photos?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&q=70'}
                  alt={l.title}
                  style={{ width: '100%', height: 160, objectFit: 'cover' }}
                />
                <div style={{ padding: '1rem' }}>
                  <div style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.3rem', color: '#0f172a' }}>
                    ₹{l.rent?.toLocaleString('en-IN')}<span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#78716c' }}>/mo</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#78716c', margin: '4px 0 8px' }}>
                    📍 {l.locality || l.location?.locality}, {l.location?.city}
                  </div>
                  <div style={{
                    display: 'inline-block', fontSize: '0.72rem', fontWeight: 700,
                    padding: '3px 10px', borderRadius: 99,
                    background: l.price_verdict === 'fair' ? '#dcfce7' : l.price_verdict === 'overpriced' ? '#fee2e2' : '#f1f5f9',
                    color: l.price_verdict === 'fair' ? '#15803d' : l.price_verdict === 'overpriced' ? '#b91c1c' : '#78716c',
                  }}>
                    {l.price_verdict === 'fair'        && '✅ Fair Price'}
                    {l.price_verdict === 'overpriced'  && '⚠️ Overpriced'}
                    {l.price_verdict === 'underpriced' && '📉 Below Market'}
                    {(!l.price_verdict || l.price_verdict === 'unknown') && 'Price N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#78716c' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>🔍</div>
            <p>No listings found for {city}. Try a different city or type.</p>
          </div>
        )}
      </div>
    </div>
  )
}