import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { agreementsAPI } from '../api/agreements'
import { listingsAPI } from '../api/listings'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import toast from 'react-hot-toast'

export default function CreateAgreement() {
  const { id }      = useParams()
  const navigate    = useNavigate()
  const [listing,   setListing]   = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [saving,    setSaving]    = useState(false)
  const [duration,  setDuration]  = useState(11)

  const today      = new Date()
  const defaultEnd = new Date(today)
  defaultEnd.setMonth(defaultEnd.getMonth() + 11)

  const [form, setForm] = useState({
    rent:           '',
    deposit:        '',
    maintenance:    '0',
    start_date:     today.toISOString().split('T')[0],
    end_date:       defaultEnd.toISOString().split('T')[0],
    tenant_address: '',
    owner_address:  '',
    custom_terms:   '',
  })

  useEffect(() => {
    listingsAPI.detail(id)
      .then(r => {
        setListing(r.data)
        setForm(f => ({
          ...f,
          rent:    r.data.rent     || '',
          deposit: r.data.deposit  || '',
        }))
      })
      .catch(() => toast.error('Listing not found'))
      .finally(() => setLoading(false))
  }, [id])

  const update = (k, v) => {
    setForm(f => {
      const next = { ...f, [k]: v }
      // Recalculate duration
      if (k === 'start_date' || k === 'end_date') {
        const start = new Date(k === 'start_date' ? v : f.start_date)
        const end   = new Date(k === 'end_date'   ? v : f.end_date)
        const months = Math.max(1, Math.round((end - start) / (1000 * 60 * 60 * 24 * 30)))
        setDuration(months)
      }
      return next
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (new Date(form.end_date) <= new Date(form.start_date)) {
      toast.error('End date must be after start date')
      return
    }
    setSaving(true)
    try {
      const res = await agreementsAPI.create(id, form)
      toast.success('✅ Agreement created! PDF generated.')
      navigate(`/agreements/${res.data.id || res.data.agreement_id}`)
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create agreement')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center min-h-[60vh]"><Spinner size="lg" /></div>
  }

  const totalUpfront  = (parseInt(form.rent) || 0) + (parseInt(form.deposit) || 0)
  const totalForTerm  = (parseInt(form.rent) || 0) * duration

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      <div className="text-center mb-8">
        <div className="text-5xl mb-3">📄</div>
        <h1 className="font-display font-bold text-4xl text-navy">Create Rental Agreement</h1>
        <p className="text-stone-400 mt-2">Generate a professional PDF agreement in minutes</p>
      </div>

      {/* Listing Banner */}
      {listing && (
        <div className="bg-gradient-to-br from-navy to-blue-900 rounded-2xl p-5 text-white flex items-center gap-4 mb-6">
          <div className="text-4xl">🏠</div>
          <div className="flex-1">
            <div className="font-display font-bold text-lg text-white">{listing.title}</div>
            <div className="text-white/60 text-sm">📍 {listing.location?.locality}, {listing.location?.city}</div>
          </div>
          <div className="text-right">
            <div className="font-display font-black text-2xl text-white">
              ₹{listing.rent?.toLocaleString('en-IN')}/mo
            </div>
            <div className="text-white/50 text-xs">Listed Rent</div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">

        {/* Parties */}
        <div className="card p-6">
          <h3 className="font-display font-bold text-xl text-navy mb-5 flex items-center gap-2">
            <span className="bg-green-50 p-2 rounded-lg">👥</span> Party Details
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-xl p-4 border border-green-100">
              <div className="text-xs font-bold text-green-700 uppercase tracking-wider mb-3">🧑 TENANT (You)</div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Your Address</label>
                <textarea
                  value={form.tenant_address}
                  onChange={e => update('tenant_address', e.target.value)}
                  className="form-input min-h-16"
                  placeholder="Your current address"
                />
              </div>
            </div>
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
              <div className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-3">🏠 OWNER</div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Owner's Address</label>
                <textarea
                  value={form.owner_address}
                  onChange={e => update('owner_address', e.target.value)}
                  className="form-input min-h-16"
                  placeholder="Owner's address (optional)"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Financial Terms */}
        <div className="card p-6">
          <h3 className="font-display font-bold text-xl text-navy mb-5 flex items-center gap-2">
            <span className="bg-ochre-bg p-2 rounded-lg">💰</span> Financial Terms
          </h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Monthly Rent (₹) *</label>
              <input type="number" value={form.rent} onChange={e => update('rent', e.target.value)} className="form-input" required min="1" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Security Deposit (₹)</label>
              <input type="number" value={form.deposit} onChange={e => update('deposit', e.target.value)} className="form-input" min="0" />
            </div>
          </div>
          {/* Summary */}
          <div className="bg-ochre-bg rounded-xl p-4 flex flex-wrap gap-6">
            <div>
              <div className="text-xs text-ochre font-bold uppercase tracking-wide">Total Upfront</div>
              <div className="font-display font-black text-2xl text-navy">₹{totalUpfront.toLocaleString('en-IN')}</div>
              <div className="text-xs text-stone-400">Deposit + first month</div>
            </div>
            <div>
              <div className="text-xs text-ochre font-bold uppercase tracking-wide">Total for {duration} Months</div>
              <div className="font-display font-black text-2xl text-navy">₹{totalForTerm.toLocaleString('en-IN')}</div>
              <div className="text-xs text-stone-400">Rent only</div>
            </div>
          </div>
        </div>

        {/* Tenancy Period */}
        <div className="card p-6">
          <h3 className="font-display font-bold text-xl text-navy mb-5 flex items-center gap-2">
            <span className="bg-purple-50 p-2 rounded-lg">📅</span> Tenancy Period
          </h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Start Date *</label>
              <input type="date" value={form.start_date} onChange={e => update('start_date', e.target.value)} className="form-input" required />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">End Date *</label>
              <input type="date" value={form.end_date} onChange={e => update('end_date', e.target.value)} className="form-input" required />
            </div>
          </div>
          <div className="bg-ochre-bg rounded-xl p-3 flex items-center gap-3">
            <span className="text-2xl">⏱️</span>
            <div>
              <div className="font-bold text-navy">{duration} month{duration !== 1 ? 's' : ''}</div>
              <div className="text-xs text-stone-400">Agreement duration</div>
            </div>
          </div>
        </div>

        {/* Custom Terms */}
        <div className="card p-6">
          <h3 className="font-display font-bold text-xl text-navy mb-3 flex items-center gap-2">
            <span className="bg-pink-50 p-2 rounded-lg">📝</span>
            Special Conditions
            <span className="text-sm font-normal text-stone-400">(optional)</span>
          </h3>
          <textarea
            value={form.custom_terms}
            onChange={e => update('custom_terms', e.target.value)}
            className="form-input min-h-28"
            placeholder={`One clause per line. Example:\nParking space B-12 included in rent.\nPets allowed with prior approval.`}
          />
          <p className="text-xs text-stone-400 mt-1.5">
            Standard clauses (payment, notice period, maintenance) are included automatically.
          </p>
        </div>

        {/* Submit */}
        <div className="flex gap-4 justify-center">
          <Link to={`/listing/${id}`}><Button variant="ghost" size="lg">Cancel</Button></Link>
          <Button type="submit" variant="primary" size="lg" loading={saving}>
            📄 Generate Agreement PDF
          </Button>
        </div>
      </form>
    </div>
  )
}