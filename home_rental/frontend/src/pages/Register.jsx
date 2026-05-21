import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '../store/useAuthStore'
import { CITIES } from '../utils/constants'

export default function Register() {
  const [form, setForm] = useState({
    full_name: '', username: '', email: '',
    phone: '', city: '', role: 'tenant',
    password: '', confirm_password: '',
  })
  const [showPwd,  setShowPwd]  = useState(false)
  const [strength, setStrength] = useState(0)
  const { register, loading }   = useAuthStore()
  const navigate                = useNavigate()

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const checkStrength = (val) => {
    let s = 0
    if (val.length >= 8)           s++
    if (/[A-Z]/.test(val))         s++
    if (/[0-9]/.test(val))         s++
    if (/[^A-Za-z0-9]/.test(val)) s++
    setStrength(s)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    const result = await register(form)
    if (result.success) {
      toast.success('🎉 Welcome to NestMate!')
      navigate('/')
    } else {
      const errs = result.error
      if (typeof errs === 'object') {
        Object.values(errs).forEach(e => toast.error(Array.isArray(e) ? e[0] : e))
      } else {
        toast.error(errs || 'Registration failed')
      }
    }
  }

  const strengthColors = ['bg-stone-200', 'bg-red-400', 'bg-ochre', 'bg-green-500', 'bg-green-600']
  const strengthLabels = ['', 'Weak', 'Fair', 'Strong', 'Very Strong']

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-xl">

        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🏠</div>
          <h1 className="font-display font-bold text-3xl text-navy">Join NestMate</h1>
          <p className="text-stone-400 mt-2">Create your free account in under 2 minutes</p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Role */}
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">I am a...</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'tenant', label: '🔍 Renter' },
                  { value: 'owner',  label: '🏠 Owner'  },
                  { value: 'both',   label: '🔄 Both'   },
                ].map(r => (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => update('role', r.value)}
                    className={`py-2.5 rounded-xl text-sm font-semibold border transition-all ${
                      form.role === r.value
                        ? 'bg-ochre-bg border-ochre text-navy'
                        : 'border-stone-200 text-stone-500 hover:border-navy'
                    }`}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Name + Username */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Full Name *</label>
                <input
                  type="text"
                  value={form.full_name}
                  onChange={e => update('full_name', e.target.value)}
                  className="form-input"
                  placeholder="Rahul Sharma"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Username *</label>
                <input
                  type="text"
                  value={form.username}
                  onChange={e => update('username', e.target.value)}
                  className="form-input"
                  placeholder="rahul_s"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={e => update('email', e.target.value)}
                className="form-input"
                placeholder="your@email.com"
                required
              />
            </div>

            {/* Phone + City */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Phone</label>
                <input
                  type="tel"
                  value={form.phone}
                  onChange={e => update('phone', e.target.value)}
                  className="form-input"
                  placeholder="+91 9876543210"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">City</label>
                <select
                  value={form.city}
                  onChange={e => update('city', e.target.value)}
                  className="form-input"
                >
                  <option value="">Select city</option>
                  {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>

            {/* Password */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Password *</label>
                <div className="relative">
                  <input
                    type={showPwd ? 'text' : 'password'}
                    value={form.password}
                    onChange={e => { update('password', e.target.value); checkStrength(e.target.value) }}
                    className="form-input pr-10"
                    placeholder="Min 8 chars"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPwd(!showPwd)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400"
                  >
                    {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {form.password && (
                  <div className="mt-1.5">
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${strengthColors[strength]}`}
                        style={{ width: `${strength * 25}%` }}
                      />
                    </div>
                    <span className="text-xs text-stone-400">{strengthLabels[strength]}</span>
                  </div>
                )}
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Confirm *</label>
                <input
                  type="password"
                  value={form.confirm_password}
                  onChange={e => update('confirm_password', e.target.value)}
                  className={`form-input ${form.confirm_password && form.password !== form.confirm_password ? 'border-red-400' : ''}`}
                  placeholder="Repeat password"
                  required
                />
                {form.confirm_password && form.password !== form.confirm_password && (
                  <p className="text-xs text-red-500 mt-1">Passwords don't match</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center py-3 text-base"
            >
              {loading ? 'Creating account...' : '🚀 Create Free Account'}
            </button>
          </form>

          <p className="text-center text-sm text-stone-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-ochre font-semibold hover:underline">Log In →</Link>
          </p>
        </div>
      </div>
    </div>
  )
}