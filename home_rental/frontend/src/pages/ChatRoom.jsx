import { useEffect, useRef, useState, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import useChatStore from '../store/useChatStore'
import useAuthStore from '../store/useAuthStore'
import ChatBubble from '../components/chat/ChatBubble'
import OfferRow from '../components/chat/OfferRow'
import Spinner from '../components/ui/Spinner'
import { Send, DollarSign, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ChatRoom() {
  const { roomId }   = useParams()
  const { user }     = useAuthStore()
  const navigate     = useNavigate()
  const {
    messages, activeRoom, loading,
    fetchMessages, addMessage, markRoomAsRead,
  } = useChatStore()

  const [input,      setInput]      = useState('')
  const [showOffer,  setShowOffer]  = useState(false)
  const [wsStatus,   setWsStatus]   = useState('connecting')
  const [messagesError, setMessagesError] = useState(null)

  const wsRef            = useRef(null)
  const reconnectTimer   = useRef(null)
  const messagesEndRef   = useRef(null)
  const seenIds          = useRef(new Set())

  const userId = user?.id?.toString()

  // ── 1. FETCH MESSAGES ────────────────────────────────────────────────────
  useEffect(() => {
    if (!user) { navigate('/login'); return }

    setMessagesError(null)
    fetchMessages(roomId)
      .catch(() => setMessagesError('Could not load messages. Check your connection.'))

    markRoomAsRead(roomId)
  }, [roomId])

  // ── 2. WEBSOCKET ─────────────────────────────────────────────────────────
  const connectWS = useCallback(function connect() {
    // Don't open a second connection if already open or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN)       return
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return

    // Point to Vite dev server — it proxies /ws → ws://127.0.0.1:8000
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl    = `${protocol}//${window.location.host}/ws/chat/${roomId}/`

    console.log('🔗 Connecting WebSocket:', wsUrl)
    setWsStatus('connecting')

    const ws      = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('✅ WebSocket connected')
      setWsStatus('connected')
    }

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)

        if (data.type === 'chat_message') {
          // Deduplicate using message_id
          const msgId = data.message_id
            || `${data.sender_id}-${Date.now()}-${Math.random()}`

          if (seenIds.current.has(msgId)) return
          seenIds.current.add(msgId)

          addMessage({
            id:        msgId,
            sender_id: data.sender_id,
            content:   data.content,
            msg_type:  data.msg_type  || 'text',
            offer_amt: data.offer_amt || null,
            timestamp: data.timestamp || new Date().toISOString(),
            is_read:   false,
          })
        }

        if (data.type === 'deal_struck') {
          toast.success(
            `🤝 Deal agreed at ₹${Number(data.agreed_rent).toLocaleString('en-IN')}/mo!`,
            { duration: 6000 }
          )
        }
      } catch (err) {
        console.error('❌ WS parse error:', err)
      }
    }

    ws.onclose = (e) => {
      console.log('❌ WebSocket closed, code:', e.code)
      wsRef.current = null

      if (e.code !== 1000 && e.code !== 1001) {
        setWsStatus('disconnected')
        if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
        reconnectTimer.current = setTimeout(() => {
          console.log('🔄 Reconnecting...')
          connect()
        }, 3000)
      } else {
        setWsStatus('disconnected')
      }
    }

    ws.onerror = (err) => {
      console.error('⚠️ WebSocket error:', err)
      setWsStatus('error')
    }
  }, [roomId, addMessage])

  // Start WebSocket when component mounts
  useEffect(() => {
    if (!user) return
    connectWS()

    return () => {
      // Clean up on unmount
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current) {
        wsRef.current.onclose = null   // prevent auto-reconnect
        wsRef.current.close(1000, 'Component unmounted')
        wsRef.current = null
      }
    }
  }, [roomId, user, connectWS])

  // ── 3. AUTO SCROLL ───────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // ── 4. SEND MESSAGE ──────────────────────────────────────────────────────
  const sendMessage = () => {
    const text = input.trim()
    if (!text) return

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      toast.error('Chat not connected. Reconnecting...')
      connectWS()
      return
    }

    wsRef.current.send(JSON.stringify({
      type:      'chat_message',
      msg_type:  'text',
      content:   text,
      sender_id: userId,
    }))
    setInput('')
  }

  // ── 5. SEND OFFER / COUNTER / DEAL ───────────────────────────────────────
  const sendOffer = (type, amount) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      toast.error('Not connected to chat')
      return
    }

    const labels = {
      offer:   `I'd like to offer ₹${Number(amount).toLocaleString('en-IN')}/mo`,
      counter: `My counter offer is ₹${Number(amount).toLocaleString('en-IN')}/mo`,
      deal:    `✅ I accept ₹${Number(amount).toLocaleString('en-IN')}/mo — Deal!`,
    }

    wsRef.current.send(JSON.stringify({
      type:      'chat_message',
      msg_type:  type,
      content:   labels[type],
      offer_amt: amount,
      sender_id: userId,
    }))
    setShowOffer(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // ── 6. STATUS DOT ────────────────────────────────────────────────────────
  const statusDot = {
    connected:    { color: '#16a34a', label: 'Live'             },
    connecting:   { color: '#d97706', label: 'Connecting...'    },
    disconnected: { color: '#dc2626', label: 'Reconnecting...'  },
    error:        { color: '#dc2626', label: 'Connection error' },
  }[wsStatus] || { color: '#94a3b8', label: 'Unknown' }

  // ── 7. LOADING / ERROR STATES ────────────────────────────────────────────
  if (loading && !messages.length && !messagesError) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <Spinner size="lg" />
      </div>
    )
  }

  if (messagesError && !messages.length) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh', flexDirection: 'column', gap: 12, color: '#475569' }}>
        <div style={{ fontSize: 36 }}>⚠️</div>
        <div style={{ fontSize: 18, fontWeight: 700 }}>Unable to load this chat</div>
        <div style={{ maxWidth: 420, textAlign: 'center' }}>{messagesError}</div>
        <button
          onClick={() => fetchMessages(roomId)}
          style={{ padding: '10px 18px', borderRadius: 999, border: 'none', background: '#0f172a', color: '#fff', cursor: 'pointer' }}
        >
          Retry
        </button>
      </div>
    )
  }

  const isDealDone = activeRoom?.status === 'deal_done'
  const isClosed   = activeRoom?.status === 'closed'

  // ── 8. RENDER ────────────────────────────────────────────────────────────
  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '1.5rem 1rem 3rem', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <button
          onClick={() => navigate('/chat')}
          style={{ padding: '8px 12px', borderRadius: 12, border: '1.5px solid var(--border, #e7e5e4)', background: 'none', cursor: 'pointer', color: 'var(--text-primary, #0f172a)' }}
        >
          <ArrowLeft size={18} />
        </button>

        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, color: 'var(--text-primary, #0f172a)', fontSize: '1rem' }}>
            {activeRoom?.listing_title || 'Chat'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-secondary, #78716c)' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: statusDot.color }} />
            {statusDot.label}
            {activeRoom?.listing_rent && (
              <span> · ₹{activeRoom.listing_rent.toLocaleString('en-IN')}/mo</span>
            )}
          </div>
        </div>

        {isDealDone && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ background: '#dcfce7', color: '#15803d', padding: '4px 12px', borderRadius: 99, fontSize: '0.8rem', fontWeight: 700 }}>
              🤝 Deal: ₹{activeRoom.agreed_rent?.toLocaleString('en-IN')}/mo
            </span>
            <Link to={`/agreements/create/${activeRoom?.listing_id}`}>
              <button style={{ background: '#d97706', color: '#fff', border: 'none', borderRadius: 99, padding: '6px 16px', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}>
                📄 Agreement
              </button>
            </Link>
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 16 }}>

        {/* Chat Window */}
        <div style={{ background: 'var(--bg-card, #fff)', borderRadius: 20, border: '1px solid var(--border, #f1f5f9)', boxShadow: '0 4px 24px rgba(15,23,42,0.08)', display: 'flex', flexDirection: 'column', height: '70vh', overflow: 'hidden' }}>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {messages.length === 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#78716c' }}>
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>💬</div>
                <div style={{ fontWeight: 600 }}>Start the conversation</div>
                <div style={{ fontSize: '0.85rem', marginTop: 4 }}>Ask about the property or make an offer below.</div>
              </div>
            ) : (
              messages.map((msg, i) => (
                <ChatBubble
                  key={msg.id || i}
                  message={msg}
                  isSent={msg.sender_id === userId}
                />
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Offer Row */}
          {showOffer && (
            <OfferRow
              onSendOffer={sendOffer}
              onClose={() => setShowOffer(false)}
              isOwner={false}
            />
          )}

          {/* Input */}
          {!isDealDone && !isClosed ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0.85rem', borderTop: '1px solid var(--border, #f1f5f9)', background: 'var(--bg-secondary, #f8fafc)' }}>
              <button
                onClick={() => setShowOffer(!showOffer)}
                title="Make an offer"
                style={{
                  width: 38, height: 38, borderRadius: 12,
                  border: `1.5px solid ${showOffer ? '#d97706' : 'var(--border, #e7e5e4)'}`,
                  background: showOffer ? '#fef3c7' : 'none',
                  color: showOffer ? '#d97706' : '#78716c',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <DollarSign size={16} />
              </button>

              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message..."
                maxLength={1000}
                style={{
                  flex: 1, border: '1.5px solid var(--border, #e7e5e4)',
                  borderRadius: 99, padding: '9px 16px',
                  fontSize: '0.9rem', outline: 'none',
                  background: 'var(--bg-card, #fff)',
                  color: 'var(--text-primary, #0f172a)',
                }}
                onFocus={e  => e.target.style.borderColor = '#d97706'}
                onBlur={e   => e.target.style.borderColor = 'var(--border, #e7e5e4)'}
              />

              <button
                onClick={sendMessage}
                disabled={!input.trim()}
                style={{
                  width: 38, height: 38, borderRadius: '50%',
                  background: input.trim() ? '#0f172a' : '#e2e8f0',
                  border: 'none', color: '#fff',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  cursor: input.trim() ? 'pointer' : 'default',
                  flexShrink: 0, transition: 'background 0.2s',
                }}
              >
                <Send size={15} />
              </button>
            </div>
          ) : (
            <div style={{ padding: '0.85rem', textAlign: 'center', fontSize: '0.85rem', color: '#78716c', borderTop: '1px solid var(--border, #f1f5f9)', background: 'var(--bg-secondary, #f8fafc)' }}>
              {isDealDone
                ? '🎉 Deal agreed! Generate your agreement above.'
                : '🔒 This chat is closed.'}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {/* Listing info */}
          <div style={{ background: 'var(--bg-card, #fff)', borderRadius: 16, padding: '1.25rem', border: '1px solid var(--border, #f1f5f9)', boxShadow: '0 4px 24px rgba(15,23,42,0.08)' }}>
            <div style={{ fontWeight: 700, color: 'var(--text-primary, #0f172a)', marginBottom: 12, fontSize: '0.95rem' }}>📋 Listing</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.85rem', color: '#78716c' }}>
              <div><strong style={{ color: 'var(--text-primary, #0f172a)' }}>Rent:</strong> ₹{activeRoom?.listing_rent?.toLocaleString('en-IN')}/mo</div>
              {activeRoom?.agreed_rent && (
                <div><strong style={{ color: '#16a34a' }}>Agreed:</strong> ₹{activeRoom.agreed_rent.toLocaleString('en-IN')}/mo</div>
              )}
              <div><strong style={{ color: 'var(--text-primary, #0f172a)' }}>Status:</strong> <span style={{ textTransform: 'capitalize' }}>{activeRoom?.status?.replace('_', ' ')}</span></div>
            </div>
            {activeRoom?.listing_id && (
              <Link to={`/listing/${activeRoom.listing_id}`}>
                <button style={{ width: '100%', marginTop: 12, padding: '7px', borderRadius: 99, border: '1.5px solid var(--border, #e7e5e4)', background: 'none', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', color: 'var(--text-primary, #0f172a)' }}>
                  View Listing ↗
                </button>
              </Link>
            )}
          </div>

          {/* Negotiation tips */}
          <div style={{ background: '#fef3c7', borderRadius: 16, padding: '1.25rem', border: '1px solid #fde68a' }}>
            <div style={{ fontWeight: 700, color: '#92400e', marginBottom: 10, fontSize: '0.9rem' }}>💡 Tips</div>
            <ul style={{ padding: '0 0 0 16px', margin: 0, fontSize: '0.8rem', color: '#78716c', lineHeight: 2 }}>
              <li>Start 10–15% below asking</li>
              <li>Offer longer stay for discount</li>
              <li>Offer deposit upfront</li>
              <li>Be polite — it goes a long way</li>
              <li>Confirm deal in writing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}