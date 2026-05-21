const NOISE_COLORS = {
  low:    'text-green-600 bg-green-50',
  medium: 'text-ochre bg-ochre-bg',
  high:   'text-red-500 bg-red-50',
}

const AIR_COLORS = {
  good:     'text-green-600 bg-green-50',
  moderate: 'text-ochre bg-ochre-bg',
  poor:     'text-red-500 bg-red-50',
}

const AMENITY_ICONS = {
  transport:  '🚇',
  hospital:   '🏥',
  grocery:    '🛒',
  education:  '🎓',
  restaurant: '🍽️',
  bank:       '🏦',
  other:      '📍',
}

export default function EnvironmentScore({ score }) {
  if (!score) return null

  return (
    <div className="card p-5">
      <h3 className="font-display font-bold text-lg text-navy mb-4">
        🌍 Area Environment Score
      </h3>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {/* Safety */}
        <div className="env-item">
          <div className="text-2xl mb-1">🛡️</div>
          <div className="font-bold text-navy text-lg">{score.safety_score}/10</div>
          <div className="text-xs text-stone-400 mt-0.5">Safety</div>
          <div className="h-1.5 bg-stone-100 rounded-full mt-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-ochre to-green-500 rounded-full"
              style={{ width: `${score.safety_score * 10}%` }}
            />
          </div>
        </div>

        {/* Walkability */}
        <div className="env-item">
          <div className="text-2xl mb-1">🚶</div>
          <div className="font-bold text-navy text-lg">{score.walkability}/10</div>
          <div className="text-xs text-stone-400 mt-0.5">Walkability</div>
          <div className="h-1.5 bg-stone-100 rounded-full mt-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-ochre to-green-500 rounded-full"
              style={{ width: `${score.walkability * 10}%` }}
            />
          </div>
        </div>

        {/* Noise */}
        <div className="env-item">
          <div className="text-2xl mb-1">🔊</div>
          <div className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${NOISE_COLORS[score.noise_level]}`}>
            {score.noise_level?.charAt(0).toUpperCase() + score.noise_level?.slice(1)}
          </div>
          <div className="text-xs text-stone-400 mt-1">Noise Level</div>
        </div>

        {/* Air Quality */}
        <div className="env-item">
          <div className="text-2xl mb-1">💨</div>
          <div className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${AIR_COLORS[score.air_quality]}`}>
            {score.air_quality?.charAt(0).toUpperCase() + score.air_quality?.slice(1)}
          </div>
          <div className="text-xs text-stone-400 mt-1">Air Quality</div>
        </div>
      </div>

      {/* Nearby amenities */}
      {score.nearby?.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-navy mb-3">Nearby Amenities</h4>
          <div className="space-y-2">
            {score.nearby.map((place, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <span>{AMENITY_ICONS[place.category] || '📍'}</span>
                  <span className="text-stone-600">{place.name}</span>
                </span>
                <span className="text-xs text-stone-400 font-medium">
                  {place.distance < 1000
                    ? `${place.distance}m`
                    : `${(place.distance / 1000).toFixed(1)}km`
                  }
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}