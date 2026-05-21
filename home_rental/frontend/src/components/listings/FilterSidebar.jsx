import { useSearchParams } from 'react-router-dom'
import { SlidersHorizontal, X } from 'lucide-react'
import { CITIES, LISTING_TYPES_FLAT } from '../../utils/constants'

export default function FilterSidebar() {
  const [params, setParams] = useSearchParams()
  

  const get = (key) => params.get(key) || ''

  const update = (key, val) => {
    const next = new URLSearchParams(params)
    if (val) next.set(key, val)
    else     next.delete(key)
    next.delete('page')
    setParams(next)
  }

  const clearAll = () => {
    setParams({})
  }

  const hasFilters = [...params.keys()].length > 0

  const LabelStyle = {
    display: 'block', fontSize: '0.72rem', fontWeight: 700,
    color: '#78716c', textTransform: 'uppercase',
    letterSpacing: '0.08em', marginBottom: 6,
  }

  const selectStyle = {
    width: '100%', border: '1.5px solid #e7e5e4', borderRadius: 10,
    padding: '8px 12px', fontSize: '0.88rem', outline: 'none',
    background: '#fff', cursor: 'pointer', color: '#0f172a',
    fontFamily: "'DM Sans', sans-serif",
  }

  const inputStyle = {
    ...selectStyle, cursor: 'text',
  }

  return (
    <div style={{
      background: '#fff', borderRadius: 20, padding: '1.25rem',
      boxShadow: '0 4px 24px rgba(15,23,42,0.08)',
      border: '1px solid #f1f5f9',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, color: '#0f172a', fontSize: '0.95rem' }}>
          <SlidersHorizontal size={16} color="#d97706" />
          Filters
        </div>
        {hasFilters && (
          <button
            onClick={clearAll}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: '#d97706', fontSize: '0.78rem', fontWeight: 600,
              display: 'flex', alignItems: 'center', gap: 4,
              fontFamily: "'DM Sans', sans-serif",
            }}
          >
            <X size={12} /> Clear All
          </button>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* City */}
        <div>
          <label style={LabelStyle}>City</label>
          <select value={get('city')} onChange={e => update('city', e.target.value)} style={selectStyle}>
            <option value="">All Cities</option>
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* Locality */}
        <div>
          <label style={LabelStyle}>Locality</label>
          <input
            type="text"
            value={get('locality')}
            onChange={e => update('locality', e.target.value)}
            placeholder="e.g. Koramangala"
            style={inputStyle}
          />
        </div>

        {/* Type */}
        <div>
          <label style={LabelStyle}>Property Type</label>
          <select value={get('type')} onChange={e => update('type', e.target.value)} style={selectStyle}>
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

        {/* Rent range */}
        <div>
          <label style={LabelStyle}>Rent Range (₹)</label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            <input
              type="number"
              value={get('min_rent')}
              onChange={e => update('min_rent', e.target.value)}
              placeholder="Min"
              style={inputStyle}
              min="0"
            />
            <input
              type="number"
              value={get('max_rent')}
              onChange={e => update('max_rent', e.target.value)}
              placeholder="Max"
              style={inputStyle}
              min="0"
            />
          </div>
        </div>

        {/* Bedrooms */}
        <div>
          <label style={LabelStyle}>Bedrooms</label>
          <div style={{ display: 'flex', gap: 6 }}>
            {['Any','1','2','3','4+'].map(b => (
              <button
                key={b}
                type="button"
                onClick={() => update('bedrooms', b === 'Any' ? '' : b.replace('+',''))}
                style={{
                  flex: 1, padding: '7px 0',
                  borderRadius: 10, fontSize: '0.8rem', fontWeight: 600,
                  border: '1.5px solid',
                  borderColor: get('bedrooms') === (b === 'Any' ? '' : b.replace('+','')) ? '#0f172a' : '#e7e5e4',
                  background:  get('bedrooms') === (b === 'Any' ? '' : b.replace('+','')) ? '#0f172a' : '#fff',
                  color:       get('bedrooms') === (b === 'Any' ? '' : b.replace('+','')) ? '#fff'    : '#78716c',
                  cursor: 'pointer', fontFamily: "'DM Sans', sans-serif",
                  transition: 'all 0.15s',
                }}
              >
                {b}
              </button>
            ))}
          </div>
        </div>

        {/* Furnished */}
        <div>
          <label style={LabelStyle}>Furnished</label>
          <select value={get('furnished')} onChange={e => update('furnished', e.target.value)} style={selectStyle}>
            <option value="">Any</option>
            <option value="unfurnished">Unfurnished</option>
            <option value="semi">Semi-Furnished</option>
            <option value="fully">Fully Furnished</option>
          </select>
        </div>

        {/* Trust Score */}
        <div>
          <label style={LabelStyle}>Min Trust Score</label>
          <select value={get('trust_min')} onChange={e => update('trust_min', e.target.value)} style={selectStyle}>
            <option value="">Any</option>
            <option value="60">60+ Good</option>
            <option value="75">75+ Great</option>
            <option value="85">85+ Verified</option>
          </select>
        </div>

        {/* Checkboxes */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, paddingTop: 4 }}>
          {[
            { key: 'student_only', label: '🎓 Student Rentals Only' },
            { key: 'pets',         label: '🐾 Pets Allowed'         },
          ].map(({ key, label }) => (
            <label key={key} style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', fontSize: '0.88rem', color: '#0f172a' }}>
              <input
                type="checkbox"
                checked={get(key) === 'on'}
                onChange={e => update(key, e.target.checked ? 'on' : '')}
                style={{ width: 16, height: 16, cursor: 'pointer', accentColor: '#d97706' }}
              />
              {label}
            </label>
          ))}
        </div>

        {/* Sort */}
        <div style={{ paddingTop: 4, borderTop: '1px solid #f1f5f9' }}>
          <label style={LabelStyle}>Sort By</label>
          <select value={get('sort')} onChange={e => update('sort', e.target.value)} style={selectStyle}>
            <option value="newest">Newest First</option>
            <option value="rent_asc">Rent: Low → High</option>
            <option value="rent_desc">Rent: High → Low</option>
            <option value="trust">Trust Score</option>
            <option value="popular">Most Viewed</option>
          </select>
        </div>

      </div>
    </div>
  )
}