import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { agreementsAPI } from '../api/agreements'
import Spinner from '../components/ui/Spinner'
import Button from '../components/ui/Button'
import { FileText, Download } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AgreementList() {
  const [agreements, setAgreements] = useState([])
  const [loading, setLoading]       = useState(true)

 useEffect(() => {
    agreementsAPI.getAll()
      .then(r => {
        const data = r.data
        setAgreements(data.agreements || data || [])
      })
      .catch(() => toast.error('Failed to load agreements'))
      .finally(() => setLoading(false))
  }, [])

  const handleDownload = async (id) => {
    try {
      const res  = await agreementsAPI.download(id)
      const url  = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href  = url
      link.download = `NestMate_Agreement_${id.slice(-8)}.pdf`
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Download failed')
    }
  }

  const STATUS_CONFIG = {
    active:  { bg: 'bg-green-100 text-green-700',  label: '✅ Active'           },
    pending: { bg: 'bg-ochre-bg text-amber-700',   label: '⏳ Pending Signatures' },
    draft:   { bg: 'bg-stone-100 text-stone-600',  label: '📝 Draft'             },
    expired: { bg: 'bg-red-100 text-red-600',      label: '🕐 Expired'           },
  }

  if (loading) {
    return <div className="flex justify-center items-center min-h-[60vh]"><Spinner size="lg" /></div>
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-bold text-3xl text-navy">📄 My Agreements</h1>
          <p className="text-stone-400 text-sm mt-1">{agreements.length} agreement{agreements.length !== 1 ? 's' : ''}</p>
        </div>
        <Link to="/search"><Button variant="ghost">🔍 Find Properties</Button></Link>
      </div>

      {agreements.length === 0 ? (
        <div className="text-center py-20 text-stone-400">
          <FileText size={48} className="mx-auto mb-4 opacity-30" />
          <h3 className="font-display font-bold text-xl text-navy mb-2">No agreements yet</h3>
          <p className="mb-4">When you agree on rent with an owner, generate a PDF agreement here.</p>
          <Link to="/search"><Button variant="primary">Browse Listings</Button></Link>
        </div>
      ) : (
        <div className="space-y-3">
          {agreements.map(a => {
            const cfg = STATUS_CONFIG[a.status] || STATUS_CONFIG.draft
            return (
              <div key={a.id} className="card p-5 flex items-center gap-4 flex-wrap">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0 ${
                  a.status === 'active' ? 'bg-green-50' :
                  a.status === 'pending' ? 'bg-ochre-bg' : 'bg-stone-50'
                }`}>
                  📄
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-navy truncate">{a.listing_title || 'Agreement'}</div>
                  <div className="text-xs text-stone-400 mt-0.5">
                    {a.start_date} → {a.end_date} · {a.duration_months} months
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-stone-400">
                    <span className="font-bold text-navy text-sm">₹{a.rent?.toLocaleString('en-IN')}/mo</span>
                    <span>T: {a.tenant_signed ? '✅' : '⬜'} O: {a.owner_signed ? '✅' : '⬜'}</span>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${cfg.bg}`}>{cfg.label}</span>
                <div className="flex gap-2">
                  <Link to={`/agreements/${a.id}`}>
                    <Button variant="ghost" size="sm">View</Button>
                  </Link>
                  {a.pdf_url && (
                    <Button variant="ghost" size="sm" onClick={() => handleDownload(a.id)}>
                      <Download size={14} />
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}