import { formatDistanceToNow } from 'date-fns'

export default function ChatBubble({ message, isSent }) {
  const { content, msg_type, offer_amt, timestamp, is_read } = message

  const time = timestamp
    ? formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    : 'Just now'

  // Render different bubble types
  const renderContent = () => {
    if (msg_type === 'offer') {
      return (
        <div className="chat-bubble-offer">
          <div className="text-xs font-bold text-ochre mb-1">💰 Rent Offer</div>
          <div className="font-display font-bold text-xl text-navy">
            ₹{Number(offer_amt).toLocaleString('en-IN')}/mo
          </div>
          {content && <div className="text-xs text-stone-500 mt-1">{content}</div>}
        </div>
      )
    }

    if (msg_type === 'counter') {
      return (
        <div className="chat-bubble-offer" style={{ borderColor: '#93c5fd', background: '#dbeafe' }}>
          <div className="text-xs font-bold text-blue-600 mb-1">🔄 Counter Offer</div>
          <div className="font-display font-bold text-xl text-navy">
            ₹{Number(offer_amt).toLocaleString('en-IN')}/mo
          </div>
          {content && <div className="text-xs text-stone-500 mt-1">{content}</div>}
        </div>
      )
    }

    if (msg_type === 'deal') {
      return (
        <div className="chat-bubble-deal w-full">
          <div className="text-lg mb-1">🤝</div>
          <div className="font-bold">Deal Agreed!</div>
          <div className="font-display font-black text-2xl text-green-700 mt-1">
            ₹{Number(offer_amt).toLocaleString('en-IN')}/mo
          </div>
        </div>
      )
    }

    return (
      <div className={isSent ? 'chat-bubble-sent' : 'chat-bubble-received'}>
        {content}
      </div>
    )
  }

  return (
    <div className={`flex flex-col ${isSent ? 'items-end' : 'items-start'} mb-1`}>
      {renderContent()}
      <div className={`text-[10px] text-stone-400 mt-1 ${isSent ? 'text-right' : ''}`}>
        {time}
        {isSent && is_read && ' · Seen'}
      </div>
    </div>
  )
}