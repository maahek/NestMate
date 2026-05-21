import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '../store/useAuthStore'

export default function Login() {
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [showPwd,  setShowPwd]  = useState(false)
  const { login, loading }      = useAuthStore()
  const navigate                = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await login(email, password)
    if (result.success) {
      toast.success('Welcome back! 👋')
      navigate('/')
    } else {
      toast.error(result.error || 'Login failed')
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-md">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🔑</div>
          <h1 className="font-display font-bold text-3xl text-navy">Welcome Back</h1>
          <p className="text-stone-400 mt-2">Log in to your NestMate account</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">

            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="form-input"
                placeholder="your@email.com"
                required
                autoFocus
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-sm font-semibold text-navy">Password</label>
                <a href="#" className="text-xs text-ochre hover:underline">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="form-input pr-11"
                  placeholder="Your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600 transition-colors"
                >
                  {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center py-3 text-base"
            >
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <hr className="border-stone-200" />
            <span className="absolute left-1/2 -translate-x-1/2 -top-2.5 bg-white px-3 text-xs text-stone-400">
              or
            </span>
          </div>

          <p className="text-center text-sm text-stone-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-ochre font-semibold hover:underline">
              Join NestMate Free →
            </Link>
          </p>
        </div>

        {/* Trust badges */}
        <div className="flex justify-center gap-6 mt-6 text-xs text-stone-400">
          <span>🔒 Secure Login</span>
          <span>✅ Verified Platform</span>
          <span>🛡️ Privacy Protected</span>
        </div>
      </div>
    </div>
  )
}