import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const CITY_CENTRES = {
  Mumbai:    [19.076,  72.877],
  Pune:      [18.520,  73.856],
  Bangalore: [12.971,  77.594],
  Delhi:     [28.613,  77.209],
  Hyderabad: [17.385,  78.487],
  Chennai:   [13.083,  80.270],
  Kolkata:   [22.572,  88.363],
  Ahmedabad: [23.023,  72.572],
}

function makeIcon(color) {
  return L.divIcon({
    className: '',
    html: `
      <div style="
        background:${color};color:#fff;
        border-radius:50% 50% 50% 0;
        width:34px;height:34px;
        display:flex;align-items:center;justify-content:center;
        font-size:12px;font-weight:700;
        transform:rotate(-45deg);
        box-shadow:0 3px 10px rgba(0,0,0,.3);
        border:2px solid rgba(255,255,255,.85);
      "></div>
    `,
    iconSize:    [34, 34],
    iconAnchor:  [17, 34],
    popupAnchor: [0,  -36],
  })
}

export default function MapView({ listings = [], city = 'Mumbai', height = '75vh' }) {
  const mapRef       = useRef(null)
  const mapInstanceRef = useRef(null)

  useEffect(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }

    const centre = CITY_CENTRES[city] || [20.593, 78.963]
    const map    = L.map(mapRef.current, { zoomControl: true }).setView(centre, 13)
    mapInstanceRef.current = map

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
      maxZoom: 18,
    }).addTo(map)

    const iconGreen  = makeIcon('#16a34a')
    const iconOchre  = makeIcon('#d97706')
    const iconPurple = makeIcon('#7c3aed')
    const iconRed    = makeIcon('#dc2626')

    const validListings = listings.filter(l => l.lat && l.lng)

    validListings.forEach((l) => {
      let icon = iconOchre
      if (l.trust >= 80)   icon = iconGreen
      if (l.is_scam)        icon = iconRed
      if (l.type === 'pg' || l.is_student) icon = iconPurple

      const marker = L.marker([l.lat, l.lng], { icon })

      marker.bindPopup(`
        <div style="min-width:200px;font-family:'DM Sans',sans-serif;">
          ${l.thumb ? `<img src="${l.thumb}" style="width:100%;height:90px;object-fit:cover;border-radius:8px;margin-bottom:8px;">` : ''}
          <div style="font-weight:700;font-size:1.1rem;color:#0f172a;">
            ₹${Number(l.rent).toLocaleString('en-IN')}/mo
          </div>
          <div style="font-size:.8rem;color:#78716c;margin:.2rem 0 .5rem;">
            📍 ${l.locality || ''}
          </div>
          <div style="font-size:.78rem;color:#78716c;">
            ${l.bedrooms ? `🛏 ${l.bedrooms}BR` : ''} &nbsp;
            ${l.type?.replace('_',' ')} &nbsp;
            ✅ Trust ${l.trust || 0}
          </div>
          <a href="/listing/${l.id}"
             style="display:inline-block;margin-top:8px;background:#0f172a;color:#fff;
                    padding:5px 14px;border-radius:99px;font-size:.78rem;font-weight:600;
                    text-decoration:none;">
            View →
          </a>
        </div>
      `)

      marker.addTo(map)
    })

    // Fit to markers
    if (validListings.length > 0) {
      const bounds = validListings.map(l => [l.lat, l.lng])
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 })
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [listings, city])

  return (
    <div
      ref={mapRef}
      style={{ height }}
      className="rounded-2xl overflow-hidden shadow-lg z-0 w-full"
    />
  )
}