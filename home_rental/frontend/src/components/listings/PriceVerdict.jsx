import { TrendingUp, TrendingDown, CheckCircle, HelpCircle } from 'lucide-react'

export default function PriceVerdict({ data }) {
  if (!data) return null

  const { verdict, label, market_rent, explanation, confidence } = data

  const config = {
    fair: {
      bg:     'bg-green-50 border-green-400',
      text:   'text-green-800',
      icon:   <CheckCircle size={18} className="text-green-600 flex-shrink-0" />,
      title:  '✅ Fair Market Price',
    },
    overpriced: {
      bg:     'bg-red-50 border-red-400',
      text:   'text-red-800',
      icon:   <TrendingUp size={18} className="text-red-500 flex-shrink-0" />,
      title:  `⚠️ ${label}`,
    },
    underpriced: {
      bg:     'bg-ochre-bg border-ochre',
      text:   'text-amber-900',
      icon:   <TrendingDown size={18} className="text-ochre flex-shrink-0" />,
      title:  `📉 ${label}`,
    },
    unknown: {
      bg:     'bg-stone-50 border-stone-300',
      text:   'text-stone-600',
      icon:   <HelpCircle size={18} className="text-stone-400 flex-shrink-0" />,
      title:  'Market Data Unavailable',
    },
  }

  const cfg = config[verdict] || config.unknown

  return (
    <div className={`price-verdict border-l-4 ${cfg.bg} mb-4`}>
      <div className={`flex items-start gap-3 ${cfg.text}`}>
        {cfg.icon}
        <div>
          <div className="font-semibold text-sm">{cfg.title}</div>
          {market_rent && (
            <div className="text-xs mt-1 opacity-80">
              Market rent in this area: ₹{market_rent.toLocaleString('en-IN')}/mo
            </div>
          )}
          {explanation && (
            <div className="text-xs mt-1 opacity-70 leading-relaxed">
              {explanation}
            </div>
          )}
          {confidence && (
            <div className="text-xs mt-1 opacity-60">
              Confidence: {confidence}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}