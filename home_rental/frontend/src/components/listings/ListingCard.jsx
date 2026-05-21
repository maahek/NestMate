import { Link } from 'react-router-dom'
import { Bed, Bath, Maximize, MapPin } from 'lucide-react'
import Badge from '../ui/Badge'
import TrustBar from '../ui/TrustBar'

export default function ListingCard({ listing }) {
  const {
    id, title, rent, photos, location,
    bedrooms, bathrooms, area_sqft,
    listing_type, trust_info, price_verdict,
    is_scam_flagged, is_student_only,
    furnished, scam_risk_score,
  } = listing

  const photo = photos?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=500&q=70'

  return (
    <Link to={`/listing/${id}`} className="block group">
      <article className="card overflow-hidden hover:-translate-y-1.5 hover:shadow-lg transition-all duration-300 border border-stone-100 h-full flex flex-col">

        {/* Image */}
        <div className="relative h-48 overflow-hidden flex-shrink-0">
          <img
            src={photo}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />

          {/* Overlay gradient */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />

          {/* Badges */}
          <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
            {trust_info?.score >= 80 && (
              <Badge variant="trust">✅ {trust_info.score}</Badge>
            )}
            {is_scam_flagged && (
              <Badge variant="scam">⚠️ Check</Badge>
            )}
            {!is_scam_flagged && scam_risk_score >= 30 && (
              <Badge variant="caution">⚡ Caution</Badge>
            )}
            {is_student_only && (
              <Badge variant="student">🎓 Student</Badge>
            )}
            <Badge variant="type">
              {listing_type?.replace('_', ' ')}
            </Badge>
          </div>

          {/* Save button */}
          <button
            className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 flex items-center justify-center text-sm hover:bg-white hover:scale-110 transition-all shadow"
            onClick={(e) => { e.preventDefault(); /* toggleSave */ }}
          >
            🤍
          </button>
        </div>

        {/* Body */}
        <div className="p-4 flex flex-col flex-1">
          {/* Price */}
          <div className="flex items-baseline gap-1 mb-1">
           <span className="font-display font-bold text-2xl text-navy">
              ₹{rent?.toLocaleString('en-IN')}
            </span>
            <span className="text-sm text-stone-400">/month</span>
          </div>

          {/* Title */}
          <p className="text-sm font-semibold text-navy mb-1 truncate">
            {title}
          </p>

          {/* Location */}
          <div className="flex items-center gap-1 text-xs text-stone-400 mb-3">
            <MapPin size={12} />
            {location?.locality}, {location?.city}
          </div>

          {/* Meta */}
          <div className="flex items-center gap-3 text-xs text-stone-500 mb-3">
            {bedrooms != null && (
              <span className="flex items-center gap-1">
                <Bed size={12} /> {bedrooms} BR
              </span>
            )}
            {bathrooms != null && (
              <span className="flex items-center gap-1">
                <Bath size={12} /> {bathrooms} BA
              </span>
            )}
            {area_sqft && (
              <span className="flex items-center gap-1">
                <Maximize size={12} /> {area_sqft} sqft
              </span>
            )}
            <span className="ml-auto capitalize text-stone-400">
              {furnished}
            </span>
          </div>

          {/* Trust bar */}
          {trust_info?.score != null && (
            <TrustBar score={trust_info.score} />
          )}

          {/* Price verdict */}
          {price_verdict && price_verdict !== 'unknown' && (
            <div className={`text-xs mt-2 font-semibold ${
              price_verdict === 'fair'       ? 'text-green-600' :
              price_verdict === 'overpriced' ? 'text-red-500'   : 'text-ochre'
            }`}>
              {price_verdict === 'fair'        && '✅ Fair market price'}
              {price_verdict === 'overpriced'  && '⚠️ Above market rate'}
              {price_verdict === 'underpriced' && '📉 Below market — verify'}
            </div>
          )}
        </div>
      </article>
    </Link>
  )
}