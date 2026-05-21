import { useState } from 'react'
import { X } from 'lucide-react'

export default function OfferRow({ onSendOffer, onClose, isOwner }) {
  const [amount, setAmount] = useState('')
  const [error,  setError]  = useState('')

  const send = (type) => {
    const amt = parseInt(amount)
    if (!amt || amt <= 0) {
      setError('Please enter a valid amount')
      return
    }
    setError('')
    onSendOffer(type, amt)
    setAmount('')
    onClose()
  }

  return (
    <div className="flex flex-wrap items-center gap-3 px-4 py-3 bg-ochre-bg border-t border-ochre-light">
      {/* Amount input */}
      <div className="flex items-center gap-1 flex-1 min-w-40">
        <span className="text-ochre font-bold text-sm">₹</span>
        <input
          type="number"
          value={amount}
          onChange={e => { setAmount(e.target.value); setError('') }}
          placeholder="Enter amount"
          className="form-input py-2 flex-1 max-w-44"
          min="0"
          step="500"
          autoFocus
        />
      </div>

      {error && (
        <span className="text-xs text-red-500 w-full">{error}</span>
      )}

      {/* Action buttons */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => send('offer')}
          className="text-xs font-bold px-4 py-2 rounded-full bg-ochre text-white hover:bg-ochre-light transition-colors"
        >
          💰 Make Offer
        </button>

        {isOwner && (
          <button
            onClick={() => send('counter')}
            className="text-xs font-bold px-4 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-600 transition-colors"
          >
            🔄 Counter
          </button>
        )}

        <button
          onClick={() => send('deal')}
          className="text-xs font-bold px-4 py-2 rounded-full bg-green-500 text-white hover:bg-green-600 transition-colors"
        >
          🤝 Accept Deal
        </button>

        <button
          onClick={onClose}
          className="text-xs font-bold px-3 py-2 rounded-full border border-stone-200 text-stone-400 hover:border-stone-400 transition-colors"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  )
}