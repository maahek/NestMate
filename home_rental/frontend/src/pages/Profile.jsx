import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { authAPI } from '../api/auth'
import useAuthStore from '../store/useAuthStore'
import { TRUST_BREAKDOWN, CITIES } from '../utils/constants'
import TrustBar from '../components/ui/TrustBar'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import toast from 'react-hot-toast'

export default function Profile() {
  const { fetchProfile } = useAuthStore()
  const [mongoUser, setMongoUser]   = useState(null)
  const [listings,  setListings]    = useState([])
  const [loading,   setLoading]     = useState(true)
  const [saving,    setSaving]      = useState(false)
  const [form, setForm] = useState({
    full_name: '', phone: '', bio: '', city: '', locality: '', role: 'tenant',
  })

  useEffect(() => {
    authAPI.getProfile()
      .then(r => {
        setMongoUser(r.data)
        setForm({
          full_name: r.data.full_name || '',
          phone:     r.data.phone     || '',
          bio:       r.data.bio       || '',
          city:      r.data.city      || '',
          locality:  r.data.locality  || '',
          role:      r.data.role      || 'tenant',
        })
        setListings(r.data.my_listings || [])
      })
      .catch(() => toast.error('Failed to load profile'))
      .finally(() => setLoading(false))
  }, [])

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => fd.append(k, v))
      const avatar = document.querySelector('input[name="avatar"]')?.files[0]
      if (avatar) fd.append('avatar', avatar)
      await authAPI.updateProfile(fd)
      await fetchProfile()
      toast.success('✅ Profile updated!')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handleVerification = async (e) => {
    e.preventDefault()
    const fd  = new FormData(e.target)
    try {
      await authAPI.uploadVerification(fd)
      toast.success('✅ Document uploaded!')
      e.target.reset()
    } catch {
      toast.error('Upload failed')
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center min-h-[60vh]"><Spinner size="lg" /></div>
  }

  if (!mongoUser) return null

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">

      {/* Profile Hero */}
      <div className="bg-gradient-to-br from-navy to-blue-900 rounded-2xl p-8 text-white mb-8 flex flex-wrap items-center gap-6">
        <div style={{
        width: 80, height: 80, borderRadius: '50%',
        border: '4px solid rgba(255,255,255,0.2)',
        overflow: 'hidden', flexShrink: 0,
        background: 'linear-gradient(135deg, #fef3c7, #fbbf24)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {mongoUser.avatar_url ? (
          <img
            src={mongoUser.avatar_url}
            alt="Profile"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={e => {
              e.target.style.display = 'none'
              e.target.nextSibling.style.display = 'flex'
            }}
          />
        ) : null}
        <span style={{
          fontFamily: "'Fraunces', serif",
          fontWeight: 900, fontSize: '2rem', color: '#0f172a',
          display: mongoUser.avatar_url ? 'none' : 'flex',
        }}>
          {mongoUser.full_name?.[0]?.toUpperCase() || '?'}
        </span>
      </div>
        <div className="flex-1">
          <h1 className="font-display font-bold text-3xl text-white">{mongoUser.full_name || mongoUser.username}</h1>
          <p className="text-white/60 mt-0.5">@{mongoUser.username} · {mongoUser.city || 'No city'} · {mongoUser.role}</p>
          <div className="flex items-center gap-2 mt-2">
            <div className="w-32 h-2 bg-white/20 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-ochre to-green-400 rounded-full" style={{ width: `${mongoUser.trust_score}%` }} />
            </div>
            <span className="text-sm font-bold">{mongoUser.trust_score}/100 Trust</span>
          </div>
        </div>
        <Link to="/listing/create">
          <Button variant="ochre">+ Add Listing</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Left */}
        <div className="space-y-5">

          {/* Trust breakdown */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-xl text-navy mb-5">🛡️ Trust Score Breakdown</h3>
            <TrustBar score={mongoUser.trust_score} />
            <div className="space-y-3 mt-5">
              {TRUST_BREAKDOWN.map(item => {
                const earned = item.key === 'phone'
                  ? Boolean(mongoUser.phone)
                  : item.key === 'avatar_url'
                  ? Boolean(mongoUser.avatar_url)
                  : item.key === 'bio'
                  ? Boolean(mongoUser.bio)
                  : item.key === 'full_name'
                  ? Boolean(mongoUser.full_name)
                  : Boolean(mongoUser[item.key])
                return (
                  <div key={item.key} className="flex items-center gap-3">
                    <span className="text-xl">{item.icon}</span>
                    <div className="flex-1">
                      <div className="flex justify-between text-sm">
                        <span className={`font-${earned ? 'semibold' : 'normal'} text-navy`}>{item.label}</span>
                        <span className={earned ? 'text-green-600 font-bold' : 'text-stone-400'}>
                          {earned ? `+${item.points} pts ✅` : `+${item.points} pts`}
                        </span>
                      </div>
                      {!earned && <p className="text-xs text-stone-400 mt-0.5">{item.action}</p>}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Upload Verification */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-xl text-navy mb-4">🪪 Upload Verification</h3>
            <form onSubmit={handleVerification} className="space-y-3">
              <select name="doc_type" className="form-input" required>
                <option value="aadhaar">🪪 Aadhaar Card (+40 pts)</option>
                <option value="pan">🗂️ PAN Card (+40 pts)</option>
                <option value="passport">📘 Passport (+40 pts)</option>
                <option value="electricity_bill">💡 Electricity Bill (+25 pts)</option>
                <option value="water_bill">💧 Water Bill (+25 pts)</option>
              </select>
              <input type="file" name="document_file" className="form-input" accept="image/*,application/pdf" required />
              <Button type="submit" fullWidth>Upload Document</Button>
            </form>
            {mongoUser.verification_docs?.length > 0 && (
              <div className="mt-4 space-y-2">
                {mongoUser.verification_docs.map((doc, i) => (
                  <div key={i} className="flex justify-between text-sm">
                    <span className="capitalize">{doc.doc_type}</span>
                    <span className={doc.verified ? 'text-green-600 font-semibold' : 'text-ochre'}>
                      {doc.verified ? '✅ Verified' : '⏳ Pending'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right */}
        <div className="space-y-5">

          {/* Edit Profile */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-xl text-navy mb-5">✏️ Edit Profile</h3>
            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Full Name</label>
                <input type="text" value={form.full_name} onChange={e => update('full_name', e.target.value)} className="form-input" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Phone</label>
                <input type="tel" value={form.phone} onChange={e => update('phone', e.target.value)} className="form-input" placeholder="+91 9876543210" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Bio</label>
                <textarea value={form.bio} onChange={e => update('bio', e.target.value)} className="form-input min-h-20" placeholder="Tell others about yourself..." />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-semibold text-navy mb-1.5">City</label>
                  <select value={form.city} onChange={e => update('city', e.target.value)} className="form-input">
                    <option value="">Select city</option>
                    {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-navy mb-1.5">Locality</label>
                  <input type="text" value={form.locality} onChange={e => update('locality', e.target.value)} className="form-input" placeholder="e.g. Koramangala" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Profile Photo</label>
                <input type="file" name="avatar" className="form-input" accept="image/*" />
              </div>
              <Button type="submit" fullWidth loading={saving}>Save Changes</Button>
            </form>
          </div>

          {/* My Listings */}
          {listings.length > 0 && (
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-display font-bold text-xl text-navy">🏠 My Listings</h3>
                <Link to="/listing/create">
                  <Button variant="ghost" size="sm">+ Add</Button>
                </Link>
              </div>
              <div className="space-y-3">
                {listings.map(l => (
                  <div key={l.id} className="flex items-center gap-3 p-3 border border-stone-100 rounded-xl">
                    {l.photos?.[0]
                      ? <img src={l.photos[0]} className="w-14 h-11 rounded-lg object-cover flex-shrink-0" alt="" />
                      : <div className="w-14 h-11 rounded-lg bg-stone-100 flex items-center justify-center text-xl flex-shrink-0">🏠</div>
                    }
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm text-navy truncate">{l.title}</p>
                      <p className="text-xs text-stone-400">₹{l.rent?.toLocaleString('en-IN')}/mo · Trust {l.trust_info?.score}/100</p>
                    </div>
                    <div className="flex gap-1.5 flex-shrink-0">
                      <Link to={`/listing/${l.id}`}><Button variant="ghost" size="sm">View</Button></Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}