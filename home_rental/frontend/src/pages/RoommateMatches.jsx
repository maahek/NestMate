import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { roommateAPI }  from '../api/roommate'
import MatchCard        from '../components/roommate/MatchCard'
import Spinner          from '../components/ui/Spinner'
import Button           from '../components/ui/Button'
import useAuthStore     from '../store/useAuthStore'
import toast            from 'react-hot-toast'

export default function RoommateMatches() {
  const { user }             = useAuthStore()
  const navigate             = useNavigate()
  const [tab,       setTab]  = useState('matches')
  const [matches,   setMatches]   = useState([])
  const [requests,  setRequests]  = useState({ received: [], sent: [] })
  const [profile,   setProfile]   = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [connected, setConnected] = useState(new Set())
  const loadAll = async () => {
    setLoading(true)
    try {
      const [matchRes, reqRes] = await Promise.all([
        roommateAPI.getMatches(),
        roommateAPI.getRequests(),
      ])
      setMatches(matchRes.data.matches || [])
      setProfile({ city: matchRes.data.city })
      setRequests(reqRes.data)

      // Mark already-connected users
      const sentIds = new Set(
        (reqRes.data.sent || []).map(r => r.other_user?.id)
      )
      setConnected(sentIds)
    } catch (err) {
      if (err.response?.status === 400) {
        navigate('/roommate/quiz')
      } else {
        toast.error('Failed to load matches')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    let mounted = true
    const load = async () => {
      setLoading(true)
      try {
        const [matchRes, reqRes] = await Promise.all([
          roommateAPI.getMatches(),
          roommateAPI.getRequests(),
        ])
        if (!mounted) return
        setMatches(matchRes.data.matches || [])
        setProfile({ city: matchRes.data.city })
        setRequests(reqRes.data)

        const sentIds = new Set((reqRes.data.sent || []).map(r => r.other_user?.id))
        setConnected(sentIds)
      } catch (err) {
        if (err.response?.status === 400) {
          navigate('/roommate/quiz')
        } else {
          toast.error('Failed to load matches')
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [user, navigate])

  const handleConnect = async (userId) => {
    try {
      await roommateAPI.sendConnectRequest(userId)
      setConnected(s => new Set([...s, userId]))
      toast.success('🤝 Connection request sent!')
      loadAll()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to send request')
    }
  }

  const handleRespond = async (matchId, action) => {
    try {
      await roommateAPI.respondToRequest(matchId, action)
      toast.success(action === 'accept' ? '✅ Request accepted!' : 'Request declined')
      loadAll()
    } catch {
      toast.error('Failed to respond')
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Spinner size="lg" />
      </div>
    )
  }

  const pendingCount = requests.received?.length || 0
  const avgScore     = matches.length
    ? Math.round(matches.reduce((s, m) => s + m.score, 0) / matches.length)
    : 0

  const TABS = [
    { id: 'matches',  label: `🤝 Matches (${matches.length})`    },
    { id: 'received', label: `📩 Requests (${pendingCount})`,
      badge: pendingCount > 0 },
    { id: 'sent',     label: `📤 Sent (${requests.sent?.length || 0})` },
  ]

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2.5rem 1.5rem 5rem', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontFamily: "'Fraunces', serif", fontWeight: 900, fontSize: 'clamp(1.8rem,4vw,2.5rem)', color: 'var(--text-primary)', marginBottom: 4 }}>
            🤝 Roommate Matches
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {matches.length} match{matches.length !== 1 ? 'es' : ''} in {profile?.city}
            {avgScore > 0 && ` · Avg score: ${avgScore}%`}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/roommate/quiz">
            <Button variant="ghost" size="sm">✏️ Edit Profile</Button>
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, borderBottom: '2px solid var(--border)', marginBottom: 24 }}>
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              background:   'none',
              border:       'none',
              padding:      '10px 20px',
              fontSize:     '0.9rem',
              fontWeight:   tab === t.id ? 700 : 400,
              color:        tab === t.id ? 'var(--ochre)' : 'var(--text-secondary)',
              borderBottom: tab === t.id ? '2px solid var(--ochre)' : '2px solid transparent',
              marginBottom: -2,
              cursor:       'pointer',
              fontFamily:   "'DM Sans', sans-serif",
              position:     'relative',
            }}
          >
            {t.label}
            {t.badge && (
              <span style={{
                position:   'absolute',
                top:        6,
                right:      6,
                width:      8,
                height:     8,
                borderRadius: '50%',
                background: '#dc2626',
              }} />
            )}
          </button>
        ))}
      </div>

      {/* ── MATCHES TAB ────────────────────────────────────────────── */}
      {tab === 'matches' && (
        matches.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {matches.map((match, i) => (
              <MatchCard
                key={match.candidate?.user_id || i}
                match={match}
                onConnect={handleConnect}
                alreadyConnected={connected.has(match.candidate?.user_id)}
              />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-secondary)' }}>
            <div style={{ fontSize: '3.5rem', marginBottom: 16 }}>🔍</div>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: 8 }}>No matches yet</h3>
            <p style={{ marginBottom: 16 }}>More people need to fill the quiz in your city.</p>
            <Link to="/roommate/quiz">
              <Button variant="primary">Update My Profile</Button>
            </Link>
          </div>
        )
      )}

      {/* ── RECEIVED REQUESTS TAB ───────────────────────────────────── */}
      {tab === 'received' && (
        <div>
          {requests.received?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {requests.received.map(req => (
                <div key={req.match_id} style={{
                  background:   'var(--bg-card)',
                  border:       '1px solid var(--border)',
                  borderRadius: 16,
                  padding:      '1.25rem',
                  display:      'flex',
                  alignItems:   'center',
                  gap:          16,
                  flexWrap:     'wrap',
                  boxShadow:    '0 4px 24px rgba(15,23,42,0.06)',
                }}>
                  {/* Avatar */}
                  <div style={{
                    width: 52, height: 52, borderRadius: '50%',
                    background: 'linear-gradient(135deg, var(--ochre-bg), var(--ochre-light))',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, fontSize: '1.3rem', color: 'var(--text-primary)',
                    flexShrink: 0, overflow: 'hidden',
                    border: '2px solid var(--ochre)',
                  }}>
                    {req.other_user?.avatar_url ? (
                      <img src={req.other_user.avatar_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      req.other_user?.name?.[0]?.toUpperCase() || '?'
                    )}
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem' }}>
                      {req.other_user?.name || 'Unknown User'}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                      📍 {req.other_user?.city || 'Unknown city'}
                      &nbsp;·&nbsp;
                      {req.created_at ? new Date(req.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
                    </div>
                    <div style={{
                      display: 'inline-block', marginTop: 6,
                      background: '#fef3c7', color: '#92400e',
                      fontSize: '0.72rem', fontWeight: 700,
                      padding: '2px 10px', borderRadius: 99,
                    }}>
                      ⏳ Pending your response
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                    <button
                      onClick={() => handleRespond(req.match_id, 'accept')}
                      style={{
                        background: '#16a34a', color: '#fff',
                        border: 'none', borderRadius: 99,
                        padding: '8px 20px', fontWeight: 700,
                        fontSize: '0.85rem', cursor: 'pointer',
                        fontFamily: "'DM Sans', sans-serif",
                      }}
                    >
                      ✅ Accept
                    </button>
                    <button
                      onClick={() => handleRespond(req.match_id, 'decline')}
                      style={{
                        background: 'transparent', color: '#dc2626',
                        border: '1.5px solid #fca5a5', borderRadius: 99,
                        padding: '8px 20px', fontWeight: 600,
                        fontSize: '0.85rem', cursor: 'pointer',
                        fontFamily: "'DM Sans', sans-serif",
                      }}
                    >
                      ✕ Decline
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '3.5rem', marginBottom: 16 }}>📩</div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: 8 }}>No pending requests</h3>
              <p>When someone sends you a connect request it will appear here.</p>
            </div>
          )}
        </div>
      )}

      {/* ── SENT REQUESTS TAB ───────────────────────────────────────── */}
      {tab === 'sent' && (
        <div>
          {requests.sent?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {requests.sent.map(req => (
                <div key={req.match_id} style={{
                  background:   'var(--bg-card)',
                  border:       '1px solid var(--border)',
                  borderRadius: 16,
                  padding:      '1.25rem',
                  display:      'flex',
                  alignItems:   'center',
                  gap:          16,
                  flexWrap:     'wrap',
                  boxShadow:    '0 4px 24px rgba(15,23,42,0.06)',
                }}>
                  {/* Avatar */}
                  <div style={{
                    width: 52, height: 52, borderRadius: '50%',
                    background: 'linear-gradient(135deg, var(--ochre-bg), var(--ochre-light))',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, fontSize: '1.3rem', color: 'var(--text-primary)',
                    flexShrink: 0, overflow: 'hidden',
                    border: '2px solid var(--border)',
                  }}>
                    {req.other_user?.avatar_url ? (
                      <img src={req.other_user.avatar_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      req.other_user?.name?.[0]?.toUpperCase() || '?'
                    )}
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem' }}>
                      {req.other_user?.name || 'Unknown User'}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                      📍 {req.other_user?.city || 'Unknown city'}
                    </div>
                    <div style={{
                      display: 'inline-block', marginTop: 6,
                      fontSize: '0.72rem', fontWeight: 700,
                      padding: '2px 10px', borderRadius: 99,
                      ...(
                        req.status === 'accepted'
                          ? { background: '#dcfce7', color: '#15803d' }
                          : req.status === 'declined'
                          ? { background: '#fee2e2', color: '#b91c1c' }
                          : { background: '#f1f5f9', color: '#64748b' }
                      ),
                    }}>
                      {req.status === 'accepted' && '✅ Accepted'}
                      {req.status === 'declined' && '✕ Declined'}
                      {req.status === 'pending'  && '⏳ Awaiting response'}
                    </div>
                  </div>

                  {req.status === 'accepted' && (
                    <div style={{
                      background: '#dcfce7', color: '#15803d',
                      padding: '8px 16px', borderRadius: 12,
                      fontSize: '0.82rem', fontWeight: 600,
                    }}>
                      🎉 You are now connected!
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '3.5rem', marginBottom: 16 }}>📤</div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: 8 }}>No requests sent yet</h3>
              <p>Go to your matches and click Connect to send a request.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}