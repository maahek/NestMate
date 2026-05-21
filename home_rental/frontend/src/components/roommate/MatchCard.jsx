import { Link } from 'react-router-dom'
import CompatibilityRing from './CompatibilityRing'
import Button from '../ui/Button'
import { MapPin, Briefcase } from 'lucide-react'

export default function MatchCard({ match, onConnect, alreadyConnected }) {
  const { candidate, score, verdict, highlights, conflicts, breakdown } = match

  return (
    <div className="card p-5 hover:-translate-y-1 hover:shadow-lg transition-all duration-300 flex flex-wrap gap-4 items-center">

      {/* Score ring */}
      <CompatibilityRing score={score} size="md" />

      {/* Avatar */}
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-ochre-bg to-ochre-light flex items-center justify-center font-bold text-navy text-lg flex-shrink-0 border-2 border-ochre/30">
        {candidate.name?.[0]?.toUpperCase() || '?'}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-44">
        <div className="font-semibold text-navy text-base">{candidate.name}</div>
        <div className="flex items-center gap-3 text-xs text-stone-400 mt-1 flex-wrap">
          {candidate.profession && (
            <span className="flex items-center gap-1">
              <Briefcase size={11} /> {candidate.profession}
            </span>
          )}
          <span className="flex items-center gap-1">
            <MapPin size={11} /> {candidate.city}
          </span>
          {candidate.age && (
            <span>{candidate.age} yrs</span>
          )}
        </div>
        <div className="text-ochre font-semibold text-sm mt-1.5">
          ₹{candidate.budget_min?.toLocaleString('en-IN')} – ₹{candidate.budget_max?.toLocaleString('en-IN')}/mo
        </div>
        <div className="text-xs font-bold text-navy mt-1">{verdict}</div>
        {highlights?.length > 0 && (
          <div className="text-xs text-green-600 mt-1">
            ✅ {highlights.slice(0, 2).join(' · ')}
          </div>
        )}
        {conflicts?.length > 0 && (
          <div className="text-xs text-stone-400 mt-0.5">
            ⚠️ {conflicts[0]}
          </div>
        )}
      </div>

      {/* Breakdown bars */}
      {breakdown && (
        <div className="flex-1 min-w-44 max-w-56 hidden lg:block">
          {Object.entries(breakdown).slice(0, 5).map(([key, val]) => (
            <div key={key} className="mb-1.5">
              <div className="flex justify-between text-[10px] text-stone-400 mb-0.5">
                <span className="capitalize">{key.replace('_', ' ')}</span>
                <span>{val}%</span>
              </div>
              <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-ochre to-green-500"
                  style={{ width: `${val}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col gap-2 flex-shrink-0">
        <Link to={`/roommate/profile/${candidate.user_id}`}>
          <Button variant="ghost" size="sm">View Profile</Button>
        </Link>
        {alreadyConnected ? (
          <Button variant="ghost" size="sm" disabled className="text-green-600 border-green-200">
            ✅ Requested
          </Button>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={() => onConnect?.(candidate.user_id)}
          >
            👋 Connect
          </Button>
        )}
      </div>
    </div>
  )
}