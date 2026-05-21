import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { listingsAPI } from '../api/listings'
import {
  CITIES,
  ALL_LISTING_TYPES,
  AMENITIES_RESIDENTIAL,
  AMENITIES_COMMERCIAL,
  COMMERCIAL_TYPE_VALUES,
  HIDE_BEDS_TYPES,
} from '../utils/constants'

// ══════════════════════════════════════════════════════════════════════════════
// CRITICAL: Define Section OUTSIDE the component.
// If defined inside, every keystroke re-renders it and inputs lose focus.
// ══════════════════════════════════════════════════════════════════════════════
function Section({ icon, title, bg = '#fef3c7', children }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 20, padding: '1.75rem',
      boxShadow: '0 4px 24px rgba(15,23,42,0.08)',
      border: '1px solid #f1f5f9', marginBottom: 20,
    }}>
      <h3 style={{
        fontFamily: "'Fraunces', serif", fontWeight: 700,
        fontSize: '1.2rem', color: '#0f172a',
        marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <span style={{ background: bg, padding: '6px 10px', borderRadius: 10, fontSize: '1.2rem' }}>
          {icon}
        </span>
        {title}
      </h3>
      {children}
    </div>
  )
}

// Input style — defined outside so it doesn't recreate on every render
const inputStyle = {
  width: '100%', border: '1.5px solid #e7e5e4', borderRadius: 12,
  padding: '10px 14px', fontSize: '0.95rem', outline: 'none',
  background: '#fff', color: '#0f172a', fontFamily: "'DM Sans', sans-serif",
  boxSizing: 'border-box', transition: 'border-color 0.2s',
}

const labelStyle = {
  display: 'block', fontSize: '0.85rem', fontWeight: 600,
  color: '#0f172a', marginBottom: 6,
}

const gridStyle = (cols = 2) => ({
  display: 'grid',
  gridTemplateColumns: `repeat(${cols}, 1fr)`,
  gap: 16,
})

// ══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════════════════════════════════════
export default function CreateListing() {
  const navigate = useNavigate()
  const [loading,  setLoading]  = useState(false)
  const [photos,   setPhotos]   = useState([])
  const [previews, setPreviews] = useState([])

  const [form, setForm] = useState({
    title:             '',
    description:       '',
    rent:              '',
    deposit:           '',
    listing_type:      'apartment',
    rental_period:     'monthly',
    city:              '',
    locality:          '',
    address:           '',
    pincode:           '',
    latitude:          '',
    longitude:         '',
    bedrooms:          '1',
    bathrooms:         '1',
    area_sqft:         '',
    furnished:         'semi',
    is_negotiable:     true,
    pets_allowed:      false,
    smoking_allowed:   false,
    bachelors_allowed: true,
    is_student_only:   false,
    target_gender:     'any',
    near_college:      '',
    video_tour_url:    '',
    tour_360_url:      '',
    amenities:         [],
  })

  // ── Use useCallback so update() reference is stable ────────────────────────
  const update = useCallback((key, val) => {
    setForm(prev => ({ ...prev, [key]: val }))
  }, [])

  const toggleAmenity = useCallback((a) => {
    setForm(prev => ({
      ...prev,
      amenities: prev.amenities.includes(a)
        ? prev.amenities.filter(x => x !== a)
        : [...prev.amenities, a],
    }))
  }, [])

  // ── Photo handler ──────────────────────────────────────────────────────────
  const handlePhotos = (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    // Validate file types
    const allowed = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    const invalid = files.filter(f => !allowed.includes(f.type))
    if (invalid.length > 0) {
      toast.error('Only JPG, PNG, WEBP images allowed')
      return
    }

    // Validate file sizes (max 5MB each)
    const tooBig = files.filter(f => f.size > 5 * 1024 * 1024)
    if (tooBig.length > 0) {
      toast.error('Each image must be under 5MB')
      return
    }

    setPhotos(files)

    // Generate previews
    const newPreviews = []
    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = (ev) => {
        newPreviews.push(ev.target.result)
        if (newPreviews.length === files.length) {
          setPreviews([...newPreviews])
        }
      }
      reader.readAsDataURL(file)
    })
  }

  const removePhoto = (index) => {
    const newPhotos   = photos.filter((_, i) => i !== index)
    const newPreviews = previews.filter((_, i) => i !== index)
    setPhotos(newPhotos)
    setPreviews(newPreviews)
  }

  // ── Submit ─────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!form.title.trim()) { toast.error('Title is required');  return }
    if (!form.rent)          { toast.error('Rent is required');   return }
    if (!form.city)          { toast.error('City is required');   return }

    setLoading(true)
    try {
      const fd = new FormData()

      // Append all form fields
      Object.entries(form).forEach(([key, val]) => {
        if (key === 'amenities') {
          val.forEach(a => fd.append('amenities', a))
        } else {
          fd.append(key, val)
        }
      })

      // Append photos
      photos.forEach(photo => fd.append('photos', photo))

      const res = await listingsAPI.create(fd)
      toast.success('✅ Listing created successfully!')
      navigate(`/listing/${res.data.id}`)
    } catch (err) {
      const msg = err.response?.data?.error || 'Failed to create listing'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const isCommercial = COMMERCIAL_TYPE_VALUES.includes(form.listing_type)
  const hideBeds     = HIDE_BEDS_TYPES.includes(form.listing_type)
  const allAmenities = [
    ...AMENITIES_RESIDENTIAL,
    ...(isCommercial ? AMENITIES_COMMERCIAL : []),
  ]

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: '2.5rem 1.5rem 5rem', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <div style={{ fontSize: '3rem', marginBottom: 10 }}>🏠</div>
        <h1 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(2rem,5vw,3rem)', color: '#0f172a', marginBottom: 8 }}>
          List Your Property
        </h1>
        <p style={{ color: '#78716c' }}>
          AI will evaluate pricing and trust score automatically
        </p>
      </div>

      <form onSubmit={handleSubmit} autoComplete="off">

        {/* ── BASIC INFO ─────────────────────────────────────────── */}
        <Section icon="📋" title="Basic Information" bg="#fef3c7">
          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle}>Title *</label>
            <input
              type="text"
              value={form.title}
              onChange={e => update('title', e.target.value)}
              placeholder="e.g. Spacious 2BHK in Koramangala with Parking"
              style={inputStyle}
              required
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle}>Description</label>
            <textarea
              value={form.description}
              onChange={e => update('description', e.target.value)}
              placeholder="Describe the property, neighbourhood, amenities..."
              style={{ ...inputStyle, minHeight: 110, resize: 'vertical', lineHeight: 1.6 }}
            />
          </div>

          <div style={gridStyle(2)}>
            <div>
              <label style={labelStyle}>Property Type *</label>
              <select
                value={form.listing_type}
                onChange={e => update('listing_type', e.target.value)}
                style={inputStyle}
              >
                <optgroup label="🏠 Residential">
                  {ALL_LISTING_TYPES.filter(t =>
                    ['apartment','house','villa','studio','pg','shared_room','hostel'].includes(t.value)
                  ).map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </optgroup>
                <optgroup label="🏪 Commercial">
                  {ALL_LISTING_TYPES.filter(t =>
                    ['shop','office','warehouse','showroom','coworking'].includes(t.value)
                  ).map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </optgroup>
                <optgroup label="✨ Special">
                  {ALL_LISTING_TYPES.filter(t =>
                    ['studio_space','event_hall','garage','farmhouse','plot'].includes(t.value)
                  ).map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </optgroup>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Rental Period</label>
              <select
                value={form.rental_period}
                onChange={e => update('rental_period', e.target.value)}
                style={inputStyle}
              >
                <option value="monthly">Monthly</option>
                <option value="short_term">Short Term (3–6 months)</option>
                <option value="student">Student</option>
              </select>
            </div>
          </div>
        </Section>

        {/* ── LOCATION ───────────────────────────────────────────── */}
        <Section icon="📍" title="Location" bg="#dcfce7">
          <div style={gridStyle(2)}>
            <div>
              <label style={labelStyle}>City *</label>
              <select
                value={form.city}
                onChange={e => update('city', e.target.value)}
                style={inputStyle}
                required
              >
                <option value="">Select city</option>
                {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Locality *</label>
              <input
                type="text"
                value={form.locality}
                onChange={e => update('locality', e.target.value)}
                placeholder="e.g. Koramangala"
                style={inputStyle}
                required
              />
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <label style={labelStyle}>Full Address</label>
            <input
              type="text"
              value={form.address}
              onChange={e => update('address', e.target.value)}
              placeholder="Flat no., Building, Street..."
              style={inputStyle}
            />
          </div>

          <div style={{ ...gridStyle(3), marginTop: 16 }}>
            <div>
              <label style={labelStyle}>Pincode</label>
              <input
                type="text"
                value={form.pincode}
                onChange={e => update('pincode', e.target.value)}
                placeholder="560001"
                style={inputStyle}
                maxLength={6}
              />
            </div>
            <div>
              <label style={labelStyle}>Latitude</label>
              <input
                type="number"
                value={form.latitude}
                onChange={e => update('latitude', e.target.value)}
                placeholder="12.9716"
                style={inputStyle}
                step="0.0001"
              />
            </div>
            <div>
              <label style={labelStyle}>Longitude</label>
              <input
                type="number"
                value={form.longitude}
                onChange={e => update('longitude', e.target.value)}
                placeholder="77.5946"
                style={inputStyle}
                step="0.0001"
              />
            </div>
          </div>
        </Section>

        {/* ── PRICING ────────────────────────────────────────────── */}
        <Section icon="💰" title="Pricing" bg="#ede9fe">
          <div style={gridStyle(2)}>
            <div>
              <label style={labelStyle}>Monthly Rent (₹) *</label>
              <input
                type="number"
                value={form.rent}
                onChange={e => update('rent', e.target.value)}
                placeholder="15000"
                style={inputStyle}
                min="0"
                required
              />
            </div>
            <div>
              <label style={labelStyle}>Security Deposit (₹)</label>
              <input
                type="number"
                value={form.deposit}
                onChange={e => update('deposit', e.target.value)}
                placeholder="30000"
                style={inputStyle}
                min="0"
              />
            </div>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 14, cursor: 'pointer', fontSize: '0.9rem' }}>
            <input
              type="checkbox"
              checked={form.is_negotiable}
              onChange={e => update('is_negotiable', e.target.checked)}
              style={{ width: 16, height: 16, cursor: 'pointer' }}
            />
            Rent is negotiable
          </label>
        </Section>

        {/* ── PROPERTY DETAILS ───────────────────────────────────── */}
        {!hideBeds && (
          <Section icon="🏗️" title="Property Details" bg="#dbeafe">
            <div style={gridStyle(3)}>
              <div>
                <label style={labelStyle}>Bedrooms</label>
                <select value={form.bedrooms} onChange={e => update('bedrooms', e.target.value)} style={inputStyle}>
                  {['1','2','3','4','5'].map(n => <option key={n} value={n}>{n} BHK</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Bathrooms</label>
                <select value={form.bathrooms} onChange={e => update('bathrooms', e.target.value)} style={inputStyle}>
                  {['1','2','3','4'].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Area (sqft)</label>
                <input
                  type="number"
                  value={form.area_sqft}
                  onChange={e => update('area_sqft', e.target.value)}
                  placeholder="800"
                  style={inputStyle}
                  min="0"
                />
              </div>
            </div>

            <div style={{ marginTop: 16 }}>
              <label style={labelStyle}>Furnished Status</label>
              <div style={{ display: 'flex', gap: 10 }}>
                {['unfurnished','semi','fully'].map(f => (
                  <button
                    key={f}
                    type="button"
                    onClick={() => update('furnished', f)}
                    style={{
                      flex: 1, padding: '10px', borderRadius: 12,
                      border: '1.5px solid',
                      borderColor: form.furnished === f ? '#0f172a' : '#e7e5e4',
                      background:  form.furnished === f ? '#0f172a' : '#fff',
                      color:       form.furnished === f ? '#fff'    : '#78716c',
                      fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer',
                      fontFamily: "'DM Sans', sans-serif", textTransform: 'capitalize',
                    }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>
          </Section>
        )}

        {/* ── RULES ──────────────────────────────────────────────── */}
        <Section icon="📜" title="Rules & Preferences" bg="#fce7f3">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
            {[
              { key: 'pets_allowed',      label: '🐾 Pets Allowed'         },
              { key: 'smoking_allowed',   label: '🚬 Smoking Allowed'      },
              { key: 'bachelors_allowed', label: '👤 Bachelors Allowed'    },
              { key: 'is_student_only',   label: '🎓 Student Only'         },
            ].map(item => (
              <label key={item.key} style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', fontSize: '0.9rem', color: '#0f172a' }}>
                <input
                  type="checkbox"
                  checked={form[item.key]}
                  onChange={e => update(item.key, e.target.checked)}
                  style={{ width: 16, height: 16, cursor: 'pointer', accentColor: '#d97706' }}
                />
                {item.label}
              </label>
            ))}
          </div>

          {form.is_student_only && (
            <div style={{ marginTop: 16 }}>
              <label style={labelStyle}>Nearby College / University</label>
              <input
                type="text"
                value={form.near_college}
                onChange={e => update('near_college', e.target.value)}
                placeholder="e.g. IIT Bombay, Christ University..."
                style={inputStyle}
              />
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            <label style={labelStyle}>Preferred Gender</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {[
                { v: 'any',    l: '🤷 Any'    },
                { v: 'male',   l: '♂️ Male'   },
                { v: 'female', l: '♀️ Female' },
              ].map(g => (
                <button
                  key={g.v}
                  type="button"
                  onClick={() => update('target_gender', g.v)}
                  style={{
                    flex: 1, padding: '10px', borderRadius: 12,
                    border: '1.5px solid',
                    borderColor: form.target_gender === g.v ? '#d97706' : '#e7e5e4',
                    background:  form.target_gender === g.v ? '#fef3c7' : '#fff',
                    color:       form.target_gender === g.v ? '#92400e' : '#78716c',
                    fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer',
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                >
                  {g.l}
                </button>
              ))}
            </div>
          </div>
        </Section>

        {/* ── AMENITIES ──────────────────────────────────────────── */}
        <Section icon="⚡" title="Amenities" bg="#fef3c7">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {allAmenities.map(a => (
              <button
                key={a}
                type="button"
                onClick={() => toggleAmenity(a)}
                style={{
                  padding: '7px 16px', borderRadius: 99,
                  border: '1.5px solid',
                  borderColor: form.amenities.includes(a) ? '#d97706' : '#e7e5e4',
                  background:  form.amenities.includes(a) ? '#fef3c7' : '#fff',
                  color:       form.amenities.includes(a) ? '#92400e' : '#78716c',
                  fontSize: '0.82rem', fontWeight: 600,
                  cursor: 'pointer', textTransform: 'capitalize',
                  fontFamily: "'DM Sans', sans-serif",
                  transition: 'all 0.15s',
                }}
              >
                {form.amenities.includes(a) ? '✓ ' : ''}{a.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </Section>

        {/* ── PHOTOS ─────────────────────────────────────────────── */}
        <Section icon="📸" title="Photos & Tour" bg="#fce7f3">

          {/* Photo upload area */}
          <div
            style={{
              border: '2px dashed #e7e5e4', borderRadius: 16,
              padding: '2rem', textAlign: 'center',
              background: '#fafafa', cursor: 'pointer',
              transition: 'border-color 0.2s',
              marginBottom: 16,
            }}
            onDragOver={e => { e.preventDefault(); e.currentTarget.style.borderColor = '#d97706' }}
            onDragLeave={e => { e.currentTarget.style.borderColor = '#e7e5e4' }}
            onDrop={e => {
              e.preventDefault()
              e.currentTarget.style.borderColor = '#e7e5e4'
              const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
              if (files.length > 0) {
                handlePhotos({ target: { files } })
              }
            }}
            onClick={() => document.getElementById('photo-upload').click()}
          >
            <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>📷</div>
            <p style={{ fontWeight: 600, color: '#0f172a', marginBottom: 4 }}>
              Click to upload or drag and drop
            </p>
            <p style={{ fontSize: '0.82rem', color: '#78716c' }}>
              JPG, PNG, WEBP — max 5MB each — first photo is thumbnail
            </p>
            <input
              id="photo-upload"
              type="file"
              multiple
              accept="image/jpeg,image/jpg,image/png,image/webp"
              onChange={handlePhotos}
              style={{ display: 'none' }}
            />
          </div>

          {/* Photo previews */}
          {previews.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: 10, marginBottom: 16 }}>
              {previews.map((src, i) => (
                <div key={i} style={{ position: 'relative', borderRadius: 10, overflow: 'hidden', aspectRatio: '4/3' }}>
                  <img
                    src={src}
                    alt={`Photo ${i + 1}`}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  {i === 0 && (
                    <div style={{
                      position: 'absolute', top: 4, left: 4,
                      background: '#d97706', color: '#fff',
                      fontSize: '0.65rem', fontWeight: 700,
                      padding: '2px 7px', borderRadius: 99,
                    }}>
                      MAIN
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => removePhoto(i)}
                    style={{
                      position: 'absolute', top: 4, right: 4,
                      background: 'rgba(0,0,0,0.6)', color: '#fff',
                      border: 'none', borderRadius: '50%',
                      width: 22, height: 22, cursor: 'pointer',
                      fontSize: '0.75rem', display: 'flex',
                      alignItems: 'center', justifyContent: 'center',
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: 8 }}>
            <label style={labelStyle}>Video Tour URL (optional)</label>
            <input
              type="url"
              value={form.video_tour_url}
              onChange={e => update('video_tour_url', e.target.value)}
              placeholder="YouTube or Google Drive link"
              style={inputStyle}
            />
          </div>
        </Section>

        {/* ── SUBMIT ─────────────────────────────────────────────── */}
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 8 }}>
          <button
            type="button"
            onClick={() => navigate(-1)}
            style={{
              padding: '13px 32px', borderRadius: 99,
              border: '1.5px solid #e7e5e4', background: '#fff',
              color: '#0f172a', fontWeight: 600, fontSize: '0.95rem',
              cursor: 'pointer', fontFamily: "'DM Sans', sans-serif",
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '13px 40px', borderRadius: 99,
              background: loading ? '#78716c' : '#0f172a',
              color: '#fff', fontWeight: 700, fontSize: '1rem',
              border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
              fontFamily: "'DM Sans', sans-serif",
              transition: 'background 0.2s',
            }}
          >
            {loading ? '⏳ Publishing...' : '🚀 Publish Listing'}
          </button>
        </div>
      </form>
    </div>
  )
}