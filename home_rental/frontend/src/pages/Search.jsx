import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { listingsAPI } from '../api/listings'
import ListingCard from '../components/listings/ListingCard'
import FilterSidebar from '../components/listings/FilterSidebar'
// Spinner not used

export default function Search() {
  const [searchParams]          = useSearchParams()
  const [listings,  setListings]  = useState([])
  const [total,     setTotal]     = useState(0)
  const [page,      setPage]      = useState(1)
  const [totalPages,setTotalPages]= useState(1)
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)

  const fetchListings = async (params = {}) => {
    setLoading(true)
    setError(null)
    try {
      const res = await listingsAPI.search(params)
      const data = res.data
      setListings(data.listings   || [])
      setTotal(data.total         || 0)
      setPage(data.page           || 1)
      setTotalPages(data.total_pages || 1)
    } catch (err) {
      console.error('Search error:', err)
      setError('Failed to load listings. Please try again.')
      setListings([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let mounted = true
    const params = Object.fromEntries(searchParams.entries())
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        const res = await listingsAPI.search(params)
        if (!mounted) return
        const data = res.data
        setListings(data.listings   || [])
        setTotal(data.total         || 0)
        setPage(data.page           || 1)
        setTotalPages(data.total_pages || 1)
      } catch (err) {
        if (!mounted) return
        console.error('Search error:', err)
        setError('Failed to load listings. Please try again.')
        setListings([])
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [searchParams])

  const city    = searchParams.get('city')    || ''
  const type    = searchParams.get('type')    || ''
  const maxRent = searchParams.get('max_rent')|| ''

  const buildTitle = () => {
    const parts = []
    if (city)    parts.push(city)
    if (type)    parts.push(type.replace(/_/g, ' '))
    if (maxRent) parts.push(`under ₹${parseInt(maxRent).toLocaleString('en-IN')}`)
    return parts.length > 0 ? parts.join(' · ') : 'All Listings'
  }

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: '2rem 1.5rem 5rem', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.6rem,3vw,2.5rem)', color: '#0f172a' }}>
          {buildTitle()}
        </h1>
        {!loading && (
          <p style={{ color: '#78716c', marginTop: 4, fontSize: '0.9rem' }}>
            {total} listing{total !== 1 ? 's' : ''} found
          </p>
        )}
      </div>

      {/* Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 24, alignItems: 'start' }}>

        {/* Sidebar */}
        <div style={{ position: 'sticky', top: 88 }}>
          <FilterSidebar />
        </div>

        {/* Main content */}
        <div>

          {/* Error state */}
          {error && (
            <div style={{
              background: '#fee2e2', border: '1px solid #fca5a5',
              borderRadius: 12, padding: '1rem 1.25rem',
              color: '#b91c1c', marginBottom: 20,
            }}>
              {error}
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
              {[...Array(6)].map((_, i) => (
                <div key={i} style={{
                  background: '#fff', borderRadius: 20,
                  overflow: 'hidden', border: '1px solid #f1f5f9',
                }}>
                  <div style={{ height: 190, background: 'linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite' }} />
                  <div style={{ padding: '1rem' }}>
                    <div style={{ height: 20, background: '#f1f5f9', borderRadius: 8, marginBottom: 10, width: '60%' }} />
                    <div style={{ height: 14, background: '#f1f5f9', borderRadius: 8, marginBottom: 8, width: '100%' }} />
                    <div style={{ height: 14, background: '#f1f5f9', borderRadius: 8, width: '40%' }} />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && listings.length === 0 && (
            <div style={{ textAlign: 'center', padding: '80px 20px', color: '#78716c' }}>
              <div style={{ fontSize: '4rem', marginBottom: 16 }}>🔍</div>
              <h3 style={{ fontFamily: "'Fraunces', serif", fontSize: '1.5rem', color: '#0f172a', marginBottom: 8 }}>
                No listings found
              </h3>
              <p style={{ marginBottom: 24 }}>
                Try removing some filters or searching in a different area.
              </p>
              <Link
                to="/search"
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 8,
                  background: '#0f172a', color: '#fff',
                  padding: '12px 28px', borderRadius: 99,
                  fontWeight: 600, textDecoration: 'none', fontSize: '0.9rem',
                }}
              >
                Clear Filters
              </Link>
            </div>
          )}

          {/* Listings grid */}
          {!loading && listings.length > 0 && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
                {listings.map(l => (
                  <ListingCard key={l.id} listing={l} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8, marginTop: 40 }}>
                  <PaginationBtn
                    label="← Prev"
                    disabled={page <= 1}
                    onClick={() => {
                      const params = Object.fromEntries(searchParams.entries())
                      fetchListings({ ...params, page: page - 1 })
                      window.scrollTo(0, 0)
                    }}
                  />
                  {[...Array(totalPages)].map((_, i) => (
                    <PaginationBtn
                      key={i}
                      label={i + 1}
                      active={page === i + 1}
                      onClick={() => {
                        const params = Object.fromEntries(searchParams.entries())
                        fetchListings({ ...params, page: i + 1 })
                        window.scrollTo(0, 0)
                      }}
                    />
                  ))}
                  <PaginationBtn
                    label="Next →"
                    disabled={page >= totalPages}
                    onClick={() => {
                      const params = Object.fromEntries(searchParams.entries())
                      fetchListings({ ...params, page: page + 1 })
                      window.scrollTo(0, 0)
                    }}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function PaginationBtn({ label, active, disabled, onClick }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        padding:      '8px 16px',
        borderRadius: 10,
        border:       '1.5px solid',
        borderColor:  active ? '#0f172a' : disabled ? '#f1f5f9' : '#e7e5e4',
        background:   active ? '#0f172a' : disabled ? '#f9fafb' : '#fff',
        color:        active ? '#fff'    : disabled ? '#d1d5db' : '#0f172a',
        fontWeight:   active ? 700 : 400,
        fontSize:     '0.88rem',
        cursor:       disabled ? 'not-allowed' : 'pointer',
        fontFamily:   "'DM Sans', sans-serif",
        transition:   'all 0.15s',
        minWidth:     40,
      }}
    >
      {label}
    </button>
  )
}