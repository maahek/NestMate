import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import { CITIES, LISTING_TYPES_FLAT } from '../../utils/constants'

export default function SearchBar({ compact = false }) {
  const [city,    setCity]    = useState('')
  const [type,    setType]    = useState('')
  const [maxRent, setMaxRent] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (city)    params.set('city',     city)
    if (type)    params.set('type',     type)
    if (maxRent) params.set('max_rent', maxRent)
    navigate(`/search?${params.toString()}`)
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`
        bg-white rounded-2xl shadow-lg border border-stone-100
        ${compact ? 'p-4' : 'p-6'}
        flex flex-wrap gap-4 items-end
      `}
    >
      {/* City */}
      <div className="flex flex-col gap-1.5 flex-1 min-w-32">
        <label className="text-[11px] font-bold text-stone-400 uppercase tracking-wider">
          City
        </label>
        <select
          value={city}
          onChange={e => setCity(e.target.value)}
          className="form-input py-2.5"
        >
          <option value="">Any City</option>
          {CITIES.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Type */}
      <div className="flex flex-col gap-1.5 flex-1 min-w-32">
        <label className="text-[11px] font-bold text-stone-400 uppercase tracking-wider">
          Type
        </label>
        <select
          value={type}
          onChange={e => setType(e.target.value)}
          className="form-input py-2.5"
        >
          <option value="">All Types</option>
          <optgroup label="🏠 Residential">
            {LISTING_TYPES_FLAT.residential.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </optgroup>
          <optgroup label="🏪 Commercial">
            {LISTING_TYPES_FLAT.commercial.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </optgroup>
          <optgroup label="✨ Special">
            {LISTING_TYPES_FLAT.special.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </optgroup>
        </select>
      </div>

      {/* Max Rent */}
      <div className="flex flex-col gap-1.5 flex-1 min-w-32">
        <label className="text-[11px] font-bold text-stone-400 uppercase tracking-wider">
          Max Rent (₹)
        </label>
        <input
          type="number"
          value={maxRent}
          onChange={e => setMaxRent(e.target.value)}
          placeholder="e.g. 15000"
          className="form-input py-2.5"
          min="0"
        />
      </div>

      <button type="submit" className="btn-ochre py-2.5 px-6 gap-2">
        <Search size={16} />
        {!compact && 'Search'}
      </button>
    </form>
  )
}