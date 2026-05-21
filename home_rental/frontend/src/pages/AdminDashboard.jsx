import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import useAuthStore from '../store/useAuthStore'
import Spinner from '../components/ui/Spinner'
import toast from 'react-hot-toast'

export default function AdminDashboard() {
  const { user }          = useAuthStore()
  const navigate          = useNavigate()
  const [tab,     setTab] = useState('overview')
  const [stats,   setStats]    = useState(null)
  const [listings, setListings] = useState([])
  const [users,    setUsers]    = useState([])
  const [scam,     setScam]     = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    if (!user?.is_admin && !user?.is_staff) {
      toast.error('Admin access required')
      navigate('/')
      return
    }
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsRes, listingsRes, scamRes] = await Promise.all([
        api.get('/analytics/api/city-stats/'),
        api.get('/api/listings/?limit=100'),
        api.get('/api/listings/?limit=100'),
      ])
      setStats(statsRes.data)
      setListings(listingsRes.data.listings || [])
      setScam((listingsRes.data.listings || []).filter(l => l.is_scam_flagged))
    } catch {
      toast.error('Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }

  const unflagListing = async (id) => {
    try {
      await api.post(`/analytics/admin/listing/${id}/`, { action: 'unflag' })
      toast.success('Listing unflagged')
      loadData()
    } catch {
      toast.error('Failed to unflag')
    }
  }

  const removeListing = async (id) => {
    if (!window.confirm('Delete this listing permanently?')) return
    try {
      await api.post(`/analytics/admin/listing/${id}/`, { action: 'remove' })
      toast.success('Listing removed')
      loadData()
    } catch {
      toast.error('Failed to remove')
    }
  }

  const featureListing = async (id, isFeatured) => {
    try {
      await api.post(`/analytics/admin/listing/${id}/`, {
        action: isFeatured ? 'unfeature' : 'feature'
      })
      toast.success(isFeatured ? 'Removed from featured' : 'Added to featured')
      loadData()
    } catch {
      toast.error('Failed to update')
    }
  }

  const verifyListing = async (id) => {
    try {
      await api.post(`/analytics/admin/listing/${id}/`, { action: 'verify' })
      toast.success('Listing verified!')
      loadData()
    } catch {
      toast.error('Failed to verify')
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Spinner size="lg" />
      </div>
    )
  }

  const totalListings  = listings.length
  const available      = listings.filter(l => l.is_available).length
  const featured       = listings.filter(l => l.is_featured).length
  const scamFlagged    = listings.filter(l => l.is_scam_flagged).length
  const verified       = listings.filter(l => l.trust_info?.id_verified).length

  const TABS = [
    { id: 'overview',  label: '📊 Overview'       },
    { id: 'listings',  label: '🏠 All Listings'   },
    { id: 'scam',      label: `⚠️ Scam (${scamFlagged})` },
    { id: 'featured',  label: '⭐ Featured'        },
  ]

  const StatCard = ({ icon, label, value, color = '#0f172a' }) => (
    <div style={{
      background: '#fff', borderRadius: 16, padding: '1.5rem',
      boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9',
    }}>
      <div style={{ fontSize: '2rem', marginBottom: 8 }}>{icon}</div>
      <div style={{ fontFamily: "'Fraunces', serif", fontSize: '2.2rem', fontWeight: 900, color, lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ fontSize: '0.82rem', color: '#78716c', marginTop: 4 }}>
        {label}
      </div>
    </div>
  )

  const ListingRow = ({ listing }) => (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 16,
      padding: '1rem', borderBottom: '1px solid #f1f5f9',
      flexWrap: 'wrap',
    }}>
      <img
        src={listing.photos?.[0] || listing.thumb || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=100&q=60'}
        alt=""
        style={{ width: 64, height: 50, borderRadius: 8, objectFit: 'cover', flexShrink: 0 }}
      />
      <div style={{ flex: 1, minWidth: 180 }}>
        <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#0f172a' }}>
          {listing.title}
        </div>
        <div style={{ fontSize: '0.78rem', color: '#78716c', marginTop: 2 }}>
          📍 {listing.location?.locality}, {listing.location?.city}
          &nbsp;·&nbsp; ₹{listing.rent?.toLocaleString('en-IN')}/mo
          &nbsp;·&nbsp; Trust: {listing.trust_info?.score || 0}/100
        </div>
        <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
          {listing.is_scam_flagged && (
            <span style={{ background: '#fee2e2', color: '#b91c1c', fontSize: '0.68rem', fontWeight: 700, padding: '2px 8px', borderRadius: 99 }}>
              ⚠️ SCAM FLAG
            </span>
          )}
          {listing.is_featured && (
            <span style={{ background: '#fef3c7', color: '#92400e', fontSize: '0.68rem', fontWeight: 700, padding: '2px 8px', borderRadius: 99 }}>
              ⭐ FEATURED
            </span>
          )}
          {listing.trust_info?.id_verified && (
            <span style={{ background: '#dcfce7', color: '#15803d', fontSize: '0.68rem', fontWeight: 700, padding: '2px 8px', borderRadius: 99 }}>
              ✅ VERIFIED
            </span>
          )}
          <span style={{ background: '#f1f5f9', color: '#64748b', fontSize: '0.68rem', fontWeight: 600, padding: '2px 8px', borderRadius: 99 }}>
            {listing.listing_type}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', flexShrink: 0 }}>
        <Link to={`/listing/${listing.id}`} target="_blank">
          <button style={btnStyle('#f1f5f9', '#0f172a')}>View</button>
        </Link>
        <button
          onClick={() => verifyListing(listing.id)}
          style={btnStyle('#dcfce7', '#15803d')}
        >
          ✅ Verify
        </button>
        <button
          onClick={() => featureListing(listing.id, listing.is_featured)}
          style={btnStyle('#fef3c7', '#92400e')}
        >
          {listing.is_featured ? '★ Unfeature' : '☆ Feature'}
        </button>
        {listing.is_scam_flagged && (
          <button
            onClick={() => unflagListing(listing.id)}
            style={btnStyle('#dbeafe', '#1d4ed8')}
          >
            Clear Flag
          </button>
        )}
        <button
          onClick={() => removeListing(listing.id)}
          style={btnStyle('#fee2e2', '#b91c1c')}
        >
          🗑️ Remove
        </button>
      </div>
    </div>
  )

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '2.5rem 2rem 5rem', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.8rem, 4vw, 2.5rem)', color: '#0f172a' }}>
            🛡️ Admin Dashboard
          </h1>
          <p style={{ color: '#78716c', marginTop: 4 }}>
            NestMate platform management
          </p>
        </div>
        
          href="http://localhost:8000/admin"
          target="_blank"
          rel="noreferrer"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: '#0f172a', color: '#fff',
            padding: '10px 20px', borderRadius: 99,
            fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none',
          }}
        <a>
          Django Admin →
        </a>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
        <StatCard icon="🏠" label="Total Listings"    value={totalListings} />
        <StatCard icon="✅" label="Available"          value={available}     color="#16a34a" />
        <StatCard icon="⭐" label="Featured"           value={featured}      color="#d97706" />
        <StatCard icon="🛡️" label="Verified"           value={verified}      color="#2563eb" />
        <StatCard icon="⚠️" label="Scam Flagged"       value={scamFlagged}   color="#dc2626" />
        <StatCard icon="📊" label="Verification Rate"  value={`${totalListings > 0 ? Math.round(verified / totalListings * 100) : 0}%`} />
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 24, borderBottom: '2px solid #f1f5f9', flexWrap: 'wrap' }}>
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              background:   'none',
              border:       'none',
              padding:      '10px 20px',
              fontSize:     '0.9rem',
              fontWeight:   tab === t.id ? 700 : 400,
              color:        tab === t.id ? '#d97706' : '#78716c',
              borderBottom: tab === t.id ? '2px solid #d97706' : '2px solid transparent',
              marginBottom: -2,
              cursor:       'pointer',
              transition:   'all 0.2s',
              fontFamily:   "'DM Sans', sans-serif",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}

      {/* Overview */}
      {tab === 'overview' && (
        <div>
          <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.3rem', color: '#0f172a', marginBottom: 20 }}>
            📍 Listings by City
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
            {['Mumbai','Pune','Bangalore','Delhi','Hyderabad','Chennai','Kolkata','Ahmedabad'].map(city => {
              const cityListings = listings.filter(l => l.location?.city?.toLowerCase().includes(city.toLowerCase()))
              return (
                <div key={city} style={{
                  background: '#fff', borderRadius: 16, padding: '1.25rem',
                  boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9',
                }}>
                  <div style={{ fontWeight: 700, color: '#0f172a' }}>{city}</div>
                  <div style={{ fontFamily: "'Fraunces', serif", fontSize: '1.8rem', fontWeight: 900, color: '#d97706', margin: '4px 0' }}>
                    {cityListings.length}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#78716c' }}>
                    {cityListings.filter(l => l.is_scam_flagged).length > 0 && (
                      <span style={{ color: '#dc2626' }}>⚠️ {cityListings.filter(l => l.is_scam_flagged).length} flagged</span>
                    )}
                    {cityListings.filter(l => l.is_scam_flagged).length === 0 && '✅ All clear'}
                  </div>
                </div>
              )
            })}
          </div>

          <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.3rem', color: '#0f172a', margin: '32px 0 20px' }}>
            📋 Recent Listings
          </h3>
          <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9', overflow: 'hidden' }}>
            {listings.slice(0, 5).map(l => <ListingRow key={l.id} listing={l} />)}
          </div>
        </div>
      )}

      {/* All Listings */}
      {tab === 'listings' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.3rem', color: '#0f172a' }}>
              All Listings ({listings.length})
            </h3>
            <Link to="/listing/create">
              <button style={{
                background: '#0f172a', color: '#fff', border: 'none',
                borderRadius: 99, padding: '8px 20px',
                fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer',
              }}>
                + Add Listing
              </button>
            </Link>
          </div>
          <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9', overflow: 'hidden' }}>
            {listings.length > 0
              ? listings.map(l => <ListingRow key={l.id} listing={l} />)
              : <div style={{ textAlign: 'center', padding: '40px', color: '#78716c' }}>No listings found</div>
            }
          </div>
        </div>
      )}

      {/* Scam Flagged */}
      {tab === 'scam' && (
        <div>
          <div style={{ background: '#fff1f2', border: '1px solid #fecaca', borderRadius: 16, padding: '1.25rem', marginBottom: 20 }}>
            <h3 style={{ color: '#b91c1c', fontWeight: 700, marginBottom: 4 }}>
              ⚠️ {scamFlagged} Suspicious Listings
            </h3>
            <p style={{ color: '#7f1d1d', fontSize: '0.88rem' }}>
              These listings were automatically flagged by the AI scam detection system. Review and take action.
            </p>
          </div>
          {scam.length > 0 ? (
            <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9', overflow: 'hidden' }}>
              {scam.map(l => <ListingRow key={l.id} listing={l} />)}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px', color: '#78716c' }}>
              <div style={{ fontSize: '3rem', marginBottom: 16 }}>🎉</div>
              <h3 style={{ color: '#0f172a', marginBottom: 8 }}>No scam listings!</h3>
              <p>All listings are clean.</p>
            </div>
          )}
        </div>
      )}

      {/* Featured */}
      {tab === 'featured' && (
        <div>
          <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 700, fontSize: '1.3rem', color: '#0f172a', marginBottom: 16 }}>
            ⭐ Featured Listings ({listings.filter(l => l.is_featured).length})
          </h3>
          <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(15,23,42,0.08)', border: '1px solid #f1f5f9', overflow: 'hidden' }}>
            {listings.filter(l => l.is_featured).length > 0
              ? listings.filter(l => l.is_featured).map(l => <ListingRow key={l.id} listing={l} />)
              : (
                <div style={{ textAlign: 'center', padding: '40px', color: '#78716c' }}>
                  No featured listings. Click ☆ Feature on any listing to feature it.
                </div>
              )
            }
          </div>
        </div>
      )}
    </div>
  )
}

// Button style helper
function btnStyle(bg, color) {
  return {
    background: bg, color, border: 'none',
    borderRadius: 99, padding: '5px 12px',
    fontSize: '0.75rem', fontWeight: 600,
    cursor: 'pointer', fontFamily: "'DM Sans', sans-serif",
    transition: 'opacity 0.2s', whiteSpace: 'nowrap',
  }
}