import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { agreementsAPI } from '../api/agreements'
// Button not used
import Spinner from '../components/ui/Spinner'
import toast from 'react-hot-toast'
import { Download, CheckCircle } from 'lucide-react'

export default function AgreementDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [agreement, setAgreement] = useState(null)
  const [loading, setLoading] = useState(true)
  const [signing, setSigning] = useState(false)

  const fetchAgreement = async () => {
    try {
      const res = await agreementsAPI.getDetail(id)
      setAgreement(res.data)
    } catch {
      toast.error('Failed to load agreement')
      navigate('/agreements')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const res = await agreementsAPI.getDetail(id)
        if (!mounted) return
        setAgreement(res.data)
      } catch {
        if (!mounted) return
        toast.error('Failed to load agreement')
        navigate('/agreements')
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => { mounted = false }
  }, [id, navigate])

  const handleSign = async (role) => {
    setSigning(true)
    try {
      await agreementsAPI.sign(id, role)
      toast.success(`✅ Signed as ${role === 'tenant' ? 'Tenant' : 'Owner'}!`)
      await fetchAgreement()
    } catch {
      toast.error('Failed to sign agreement')
    } finally {
      setSigning(false)
    }
  }

  const handleDownload = async () => {
    try {
      const res = await agreementsAPI.download(id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Agreement_${id.slice(0, 8)}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
    } catch {
      toast.error('Failed to download PDF')
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center min-h-[60vh]"><Spinner size="lg" /></div>
  }

  if (!agreement) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10 text-center">
        <p className="text-stone-400">Agreement not found</p>
        <Link to="/agreements" className="text-ochre font-semibold mt-4 inline-block">← Back to Agreements</Link>
      </div>
    )
  }

  const statusColors = {
    draft:    'bg-yellow-50 border-yellow-200 text-yellow-700',
    pending:  'bg-blue-50 border-blue-200 text-blue-700',
    active:   'bg-green-50 border-green-200 text-green-700',
    expired:  'bg-gray-50 border-gray-200 text-gray-700',
  }

  const statusLabel = {
    draft:   '📝 Draft',
    pending: '⏳ Pending Signature',
    active:  '✅ Active',
    expired: '⏰ Expired',
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display font-bold text-4xl text-navy mb-2">
            {agreement.listing_title}
          </h1>
          <p className="text-stone-400">Agreement #{agreement.id.slice(0, 8)}</p>
        </div>
        <Link to="/agreements" className="text-stone-400 hover:text-navy">← Back</Link>
      </div>

      {/* Status Badge */}
      <div className={`rounded-xl border-2 p-4 mb-8 ${statusColors[agreement.status] || statusColors.draft}`}>
        <div className="flex items-center justify-between">
          <div className="text-lg font-semibold">{statusLabel[agreement.status] || 'Unknown Status'}</div>
          <div className="text-sm">Last updated: {agreement.created_at || 'N/A'}</div>
        </div>
      </div>

      {/* Property Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card p-6">
          <h3 className="font-display font-bold text-lg text-navy mb-4 flex items-center gap-2">
            <span>🏠</span> Property
          </h3>
          <div className="space-y-3 text-sm">
            <div>
              <div className="text-stone-500 font-semibold">Title</div>
              <div className="text-navy font-medium">{agreement.listing_title}</div>
            </div>
            <div>
              <div className="text-stone-500 font-semibold">Address</div>
              <div className="text-navy font-medium">{agreement.property_address || 'Not provided'}</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="font-display font-bold text-lg text-navy mb-4 flex items-center gap-2">
            <span>💰</span> Financial Terms
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-stone-500">Monthly Rent</span>
              <span className="font-bold text-ochre">₹{agreement.rent?.toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-500">Deposit</span>
              <span className="font-bold">₹{agreement.deposit?.toLocaleString('en-IN')}</span>
            </div>
            {agreement.maintenance > 0 && (
              <div className="flex justify-between">
                <span className="text-stone-500">Maintenance</span>
                <span className="font-bold">₹{agreement.maintenance?.toLocaleString('en-IN')}</span>
              </div>
            )}
            <div className="flex justify-between pt-3 border-t">
              <span className="text-stone-700 font-semibold">Duration</span>
              <span className="font-bold">{agreement.duration_months} months</span>
            </div>
          </div>
        </div>
      </div>

      {/* Parties */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card p-6">
          <h3 className="font-display font-bold text-lg text-navy mb-4 flex items-center gap-2">
            <span>🧑</span> Tenant
          </h3>
          <div className="space-y-2 text-sm">
            <div>
              <div className="text-stone-500 font-semibold">Name</div>
              <div className="text-navy font-medium">{agreement.tenant_name}</div>
            </div>
            {agreement.tenant_phone && (
              <div>
                <div className="text-stone-500 font-semibold">Phone</div>
                <div className="text-navy font-medium">{agreement.tenant_phone}</div>
              </div>
            )}
            <div>
              <div className="text-stone-500 font-semibold">Address</div>
              <div className="text-navy font-medium text-xs">{agreement.tenant_address || 'Not provided'}</div>
            </div>
            {agreement.tenant_signed && (
              <div className="mt-3 flex items-center gap-2 text-green-600 font-semibold">
                <CheckCircle size={16} /> Signed {agreement.tenant_signed_at}
              </div>
            )}
            {!agreement.tenant_signed && agreement.is_tenant && agreement.can_sign_as_tenant && (
              <button
                onClick={() => handleSign('tenant')}
                disabled={signing}
                className="mt-3 w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                {signing ? 'Signing...' : '✍️ Sign as Tenant'}
              </button>
            )}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="font-display font-bold text-lg text-navy mb-4 flex items-center gap-2">
            <span>🏢</span> Owner
          </h3>
          <div className="space-y-2 text-sm">
            <div>
              <div className="text-stone-500 font-semibold">Name</div>
              <div className="text-navy font-medium">{agreement.owner_name}</div>
            </div>
            {agreement.owner_phone && (
              <div>
                <div className="text-stone-500 font-semibold">Phone</div>
                <div className="text-navy font-medium">{agreement.owner_phone}</div>
              </div>
            )}
            <div>
              <div className="text-stone-500 font-semibold">Address</div>
              <div className="text-navy font-medium text-xs">{agreement.owner_address || 'Not provided'}</div>
            </div>
            {agreement.owner_signed && (
              <div className="mt-3 flex items-center gap-2 text-green-600 font-semibold">
                <CheckCircle size={16} /> Signed {agreement.owner_signed_at}
              </div>
            )}
            {!agreement.owner_signed && agreement.is_owner && agreement.can_sign_as_owner && (
              <button
                onClick={() => handleSign('owner')}
                disabled={signing}
                className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                {signing ? 'Signing...' : '✍️ Sign as Owner'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Dates */}
      <div className="card p-6 mb-8">
        <h3 className="font-display font-bold text-lg text-navy mb-4 flex items-center gap-2">
          <span>📅</span> Duration
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-stone-500 font-semibold mb-1">Start Date</div>
            <div className="text-navy font-medium">{agreement.start_date}</div>
          </div>
          <div>
            <div className="text-stone-500 font-semibold mb-1">End Date</div>
            <div className="text-navy font-medium">{agreement.end_date}</div>
          </div>
        </div>
      </div>

      {/* Custom Terms */}
      {agreement.custom_terms && agreement.custom_terms.length > 0 && (
        <div className="card p-6 mb-8">
          <h3 className="font-display font-bold text-lg text-navy mb-4">📋 Custom Terms</h3>
          <ul className="space-y-2">
            {agreement.custom_terms.map((term, idx) => (
              <li key={idx} className="text-sm text-navy flex items-start gap-3">
                <span className="text-ochre font-bold">•</span>
                <span>{term}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-4 justify-center">
        {agreement.pdf_exists && (
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 bg-ochre hover:bg-ochre-dark text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            <Download size={20} /> Download PDF
          </button>
        )}
        {agreement.both_signed && (
          <div className="flex items-center gap-2 text-green-600 font-semibold">
            <CheckCircle size={20} /> Both parties signed
          </div>
        )}
      </div>
    </div>
  )
}
