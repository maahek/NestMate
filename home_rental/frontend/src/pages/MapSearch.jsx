import { useState, useEffect } from 'react'
import { List } from 'lucide-react'
import { Link } from 'react-router-dom'
import MapView from '../components/listings/MapView'
import { listingsAPI } from '../api/listings'
import { CITIES } from '../utils/constants'
import Spinner from '../components/ui/Spinner'

export default function MapSearch() {
  const [city,     setCity]     = useState('Mumbai')
  const [listings, setListings] = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        if (mounted) setLoading(true)
        const r = await listingsAPI.search({ city, limit: 100 })
        if (!mounted) return
        setListings(r.data.listings || [])
      } catch {
        if (!mounted) return
        setListings([])
      } finally {
        if (mounted) setLoading(false)
      }
    }

    load()
    return () => { mounted = false }
  }, [city])

  const mapListings = listings
    .filter(l => l.lat && l.lng)
    .map(l => ({
      id:       l.id,
      lat:      l.lat,
      lng:      l.lng,
      rent:     l.rent,
      trust:    l.trust,
      type:     l.type,
      locality: l.locality,
      bedrooms: l.bedrooms,
      thumb:    l.thumb,
      is_scam:  l.is_scam,
      is_student: l.is_student,
    }))

  return (
    <div className="h-[calc(100vh-68px)] flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-4 px-4 py-3 bg-white border-b border-stone-100 flex-shrink-0 flex-wrap">
        <h1 className="font-display font-bold text-xl text-navy">🗺️ Map Search</h1>

        <select
          value={city}
          onChange={e => setCity(e.target.value)}
          className="form-input py-2 max-w-44"
        >
          {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        <div className="text-sm text-stone-400">
          {loading ? 'Loading...' : `${mapListings.length} listings on map`}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 ml-auto text-xs text-stone-500">
          {[
            { color: '#16a34a', label: 'High Trust' },
            { color: '#d97706', label: 'Medium Trust' },
            { color: '#7c3aed', label: 'Student/PG' },
            { color: '#dc2626', label: 'Flagged' },
          ].map(l => (
            <div key={l.label} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ background: l.color }} />
              {l.label}
            </div>
          ))}
        </div>

        <Link to="/search" className="btn-ghost text-xs py-1.5 px-4">
          <List size={14} /> List View
        </Link>
      </div>

      {/* Map */}
      <div className="flex-1 p-3">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <Spinner size="lg" />
          </div>
        ) : (
          <MapView listings={mapListings} city={city} height="100%" />
        )}
      </div>
    </div>
  )
}