import { AlertTriangle, ShieldAlert } from 'lucide-react'

export default function ScamAlert({ data }) {
  if (!data) return null

  const { is_scam, is_caution, risk_score, reasons, badge } = data

  if (!is_scam && !is_caution) return null

  return (
    <div className={`
      rounded-xl p-5 mb-5 border-2
      ${is_scam
        ? 'bg-red-50 border-red-300'
        : 'bg-ochre-bg border-ochre-light'
      }
    `}>
      <div className="flex items-start gap-3">
        {is_scam
          ? <ShieldAlert size={22} className="text-red-500 flex-shrink-0 mt-0.5" />
          : <AlertTriangle size={22} className="text-ochre flex-shrink-0 mt-0.5" />
        }
        <div className="flex-1">
          <h3 className={`font-bold text-base mb-1 ${is_scam ? 'text-red-700' : 'text-amber-800'}`}>
            {badge}
          </h3>

          {/* Risk score bar */}
          <div className="flex items-center gap-2 mb-3">
            <div className="flex-1 h-2 bg-white/60 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  risk_score >= 70 ? 'bg-red-500' :
                  risk_score >= 40 ? 'bg-ochre'   : 'bg-green-500'
                }`}
                style={{ width: `${risk_score}%` }}
              />
            </div>
            <span className={`text-xs font-bold ${is_scam ? 'text-red-600' : 'text-ochre'}`}>
              Risk: {risk_score}/100
            </span>
          </div>

          {/* Reasons list */}
          {reasons?.length > 0 && (
            <ul className="space-y-1">
              {reasons.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-red-700">
                  <span className="mt-0.5 flex-shrink-0">⚠️</span>
                  {r}
                </li>
              ))}
            </ul>
          )}

          <p className={`text-xs mt-3 font-medium ${is_scam ? 'text-red-600' : 'text-amber-700'}`}>
            {is_scam
              ? 'We strongly recommend verifying this listing in person before making any payment.'
              : 'Some trust signals are missing. Proceed with caution.'
            }
          </p>
        </div>
      </div>
    </div>
  )
}