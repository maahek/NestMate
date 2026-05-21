import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import useChatStore from '../store/useChatStore'
import Spinner from '../components/ui/Spinner'
import { MessageSquare } from 'lucide-react'

// Small presentational component moved out of parent to avoid recreation on each render
const RoomCard = ({ room }) => (
  <Link to={`/chat/${room.id}`}>
    <div className="card p-4 hover:-translate-y-0.5 hover:shadow-lg transition-all flex items-center gap-3">
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-ochre-bg to-ochre-light flex items-center justify-center font-bold text-navy text-lg flex-shrink-0 relative">
        {room.other_name?.[0]?.toUpperCase() || '?'}
        {room.status === 'deal_done' && (
          <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center text-[9px] text-white">✓</div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-center">
          <span className="font-semibold text-navy text-sm">{room.other_name}</span>
          <span className="text-xs text-stone-400">{room.last_msg_time}</span>
        </div>
        <div className="text-xs text-stone-400 truncate mt-0.5">
          📍 {room.listing_title} · ₹{room.listing_rent?.toLocaleString('en-IN')}/mo
        </div>
        <div className={`text-xs mt-0.5 truncate ${
          room.last_msg_type === 'deal' ? 'text-green-600 font-semibold' :
          room.last_msg_type === 'offer' || room.last_msg_type === 'counter' ? 'text-ochre font-semibold' :
          'text-stone-400'
        }`}>
          {room.last_msg_type === 'deal'    && `🤝 Deal: ₹${room.agreed_rent?.toLocaleString('en-IN')}/mo`}
          {room.last_msg_type === 'offer'   && `💰 Offer: ₹${room.last_message}`}
          {room.last_msg_type === 'counter' && `🔄 Counter: ₹${room.last_message}`}
          {!['deal','offer','counter'].includes(room.last_msg_type) && (room.last_message || 'No messages yet')}
        </div>
      </div>
      {room.unread > 0 && (
        <div className="w-5 h-5 rounded-full bg-ochre text-white text-[10px] font-bold flex items-center justify-center flex-shrink-0">
          {room.unread}
        </div>
      )}
    </div>
  </Link>
)

const Section = ({ title, titleClass, rooms }) => rooms.length === 0 ? null : (
  <div className="mb-6">
    <h3 className={`text-xs font-bold uppercase tracking-wider mb-3 ${titleClass}`}>{title} — {rooms.length}</h3>
    <div className="space-y-2">{rooms.map(r => <RoomCard key={r.id} room={r} />)}</div>
  </div>
)

export default function ChatList() {
  const { rooms, loading, roomsError, fetchRooms, totalUnread } = useChatStore()

  useEffect(() => { fetchRooms() }, [])

  if (loading) {
    return <div className="flex justify-center items-center min-h-[60vh]"><Spinner size="lg" /></div>
  }

  const active  = rooms.filter(r => r.status === 'active')
  const deals   = rooms.filter(r => r.status === 'deal_done')
  const closed  = rooms.filter(r => r.status === 'closed')

  
  // Render

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-bold text-3xl text-navy">💬 My Chats</h1>
          <p className="text-stone-400 text-sm mt-1">
            {rooms.length} conversation{rooms.length !== 1 ? 's' : ''}
            {totalUnread > 0 && <span className="text-ochre font-semibold"> · {totalUnread} unread</span>}
          </p>
        </div>
        <Link to="/search" className="btn-primary text-sm py-2">🔍 Find Homes</Link>
      </div>

      {roomsError ? (
        <div className="text-center py-20 text-stone-400">
          <MessageSquare size={48} className="mx-auto mb-4 opacity-30" />
          <h3 className="font-display font-bold text-xl text-navy mb-2">Unable to load chats</h3>
          <p className="mb-4">{roomsError}</p>
          <button onClick={fetchRooms} className="btn-primary">Retry</button>
        </div>
      ) : rooms.length === 0 ? (
        <div className="text-center py-20 text-stone-400">
          <MessageSquare size={48} className="mx-auto mb-4 opacity-30" />
          <h3 className="font-display font-bold text-xl text-navy mb-2">No chats yet</h3>
          <p className="mb-4">Browse listings and click "Chat with Owner" to start a conversation.</p>
          <Link to="/search" className="btn-primary">Browse Listings</Link>
        </div>
      ) : (
        <>
          <Section title="Active"      titleClass="text-navy"    rooms={active}  />
          <Section title="🤝 Deals"   titleClass="text-green-600" rooms={deals}   />
          <Section title="Archived"   titleClass="text-stone-400" rooms={closed}  />
        </>
      )}
    </div>
  )
}