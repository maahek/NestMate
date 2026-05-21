import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { MapPin } from 'lucide-react'
import { listingsAPI } from '../api/listings'
import { chatAPI } from '../api/chat'
import PriceVerdict from '../components/listings/PriceVerdict'
import ScamAlert from '../components/listings/ScamAlert'
import EnvironmentScore from '../components/listings/EnvironmentScore'
import TrustBar from '../components/ui/TrustBar'
import MapView from '../components/listings/MapView'
import Spinner from '../components/ui/Spinner'
import Button from '../components/ui/Button'
import useAuthStore from '../store/useAuthStore'
import toast from 'react-hot-toast'

export default function ListingDetail() {
  const { id }       = useParams()
  const { user }     = useAuthStore()
  const navigate     = useNavigate()
  const [listing,    setListing]    = useState(null)
  const [priceData,  setPriceData]  = useState(null)
  const [scamData,   setScamData]   = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [chatLoading,setChatLoading]= useState(false)
  const [activePhoto,setActivePhoto]= useState(0)

  useEffect(() => {
    Promise.all([
      listingsAPI.detail(id),
      listingsAPI.priceCheck({ city: '', type: '', bedrooms: 1, rent: 0 }),
      listingsAPI.scamCheck(id),
    ])
    .then(([listRes, , scamRes]) => {
      setListing(listRes.data)
      setScamData(scamRes.data)
      // Fetch price after we have listing data
      return listingsAPI.priceCheck({
        city:     listRes.data.location?.city     || '',
        locality: listRes.data.location?.locality || '',
        type:     listRes.data.listing_type        || 'apartment',
        bedrooms: listRes.data.bedrooms            || 1,
        rent:     listRes.data.rent                || 0,
      })
    })
    .then(pRes => setPriceData(pRes.data))
    .catch(() => toast.error('Failed to load listing'))
    .finally(() => setLoading(false))
  }, [id])

  const handleStartChat = async () => {
    if (!user) { navigate('/login'); return }
    setChatLoading(true)
    try {
      const res = await chatAPI.startChat(id)
      navigate(`/chat/${res.data.room_id || res.data.id}`)
    } catch {
      toast.error('Could not start chat')
    } finally {
      setChatLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!listing) {
    return (
      <div className="text-center py-20">
        <div className="text-5xl mb-4">🏠</div>
        <h2 className="font-display font-bold text-2xl text-navy">Listing Not Found</h2>
        <Link to="/search" className="btn-primary mt-4 inline-flex">Browse Listings</Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">

      {/* Scam Alert */}
      <ScamAlert data={scamData} />

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-8">

        {/* ── LEFT ─────────────────────────────────────────────────── */}
        <div>
          {/* Photos */}
          <div className="rounded-2xl overflow-hidden mb-6 bg-stone-100">
            <img
              src={listing.photos?.[activePhoto] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80'}
              alt={listing.title}
              className="w-full h-96 object-cover"
            />
            {listing.photos?.length > 1 && (
              <div className="flex gap-2 p-3 overflow-x-auto">
                {listing.photos.map((p, i) => (
                  <img
                    key={i}
                    src={p}
                    alt=""
                    onClick={() => setActivePhoto(i)}
                    className={`w-20 h-16 object-cover rounded-lg cursor-pointer flex-shrink-0 transition-all ${activePhoto === i ? 'ring-2 ring-ochre' : 'opacity-60 hover:opacity-100'}`}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Virtual Tour */}
          {listing.video_tour_url && (
            <div className="card p-5 mb-6 bg-navy text-white flex items-center justify-between">
              <div>
                <div className="font-bold">🎬 Virtual Tour Available</div>
                <div className="text-white/60 text-sm mt-0.5">Explore without visiting</div>
              </div>
              <a href={listing.video_tour_url} target="_blank" rel="noreferrer">
                <Button variant="ochre" size="sm">▶ Watch Tour</Button>
              </a>
            </div>
          )}

          {/* Details */}
          <div className="card p-6 mb-6">
            <h2 className="font-display font-bold text-2xl text-navy mb-3">About This Property</h2>
            <p className="text-stone-500 leading-relaxed">{listing.description}</p>

            <hr className="border-stone-100 my-5" />

            <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
              {[
                { icon: '🛏', val: `${listing.bedrooms} BR`,   label: 'Bedrooms'   },
                { icon: '🚿', val: `${listing.bathrooms} BA`,  label: 'Bathrooms'  },
                { icon: '📐', val: listing.area_sqft ? `${listing.area_sqft} sqft` : '—', label: 'Area' },
                { icon: '🛋️', val: listing.furnished,          label: 'Furnished'  },
                { icon: '🐾', val: listing.pets_allowed ? 'Yes' : 'No',  label: 'Pets'    },
                { icon: '🚬', val: listing.smoking_allowed ? 'Yes' : 'No', label: 'Smoking' },
              ].map((item) => (
                <div key={item.label} className="text-center p-3 bg-stone-50 rounded-xl">
                  <div className="text-2xl mb-1">{item.icon}</div>
                  <div className="font-semibold text-navy text-sm capitalize">{item.val}</div>
                  <div className="text-xs text-stone-400 mt-0.5">{item.label}</div>
                </div>
              ))}
            </div>

            {listing.amenities?.length > 0 && (
              <>
                <hr className="border-stone-100 my-5" />
                <h3 className="font-semibold text-navy mb-3">Amenities</h3>
                <div className="flex flex-wrap gap-2">
                  {listing.amenities.map((a) => (
                    <span key={a} className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-xs font-semibold capitalize">
                      {a.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Environment Score */}
          {listing.environment_score && (
            <div className="mb-6">
              <EnvironmentScore score={listing.environment_score} />
            </div>
          )}

          {/* Map */}
          {listing.location?.latitude && (
            <div className="mb-6">
              <h3 className="font-display font-bold text-xl text-navy mb-3">📍 Location</h3>
              <MapView
                listings={[{
                  id:    listing.id,
                  lat:   listing.location.latitude,
                  lng:   listing.location.longitude,
                  rent:  listing.rent,
                  trust: listing.trust_info?.score || 0,
                  type:  listing.listing_type,
                }]}
                city={listing.location.city}
                height="300px"
              />
              <p className="text-sm text-stone-400 mt-2">
                📍 {listing.location.address || `${listing.location.locality}, ${listing.location.city}`}
              </p>
            </div>
          )}
        </div>

        {/* ── RIGHT SIDEBAR ──────────────────────────────────────────── */}
        <div>
          <div className="sticky top-24 space-y-4">

            {/* Price card */}
            <div className="card p-6">
              <div className="flex items-start justify-between gap-3 mb-1">
                <h1 className="font-display font-bold text-2xl text-navy leading-tight">
                  {listing.title}
                </h1>
              </div>

              <div className="flex items-center gap-1.5 text-sm text-stone-400 mb-4">
                <MapPin size={13} />
                {listing.location?.locality}, {listing.location?.city}
              </div>

              <div className="flex items-baseline gap-1 mb-1">
                <span className="font-display font-black text-4xl text-navy">
                  ₹{listing.rent?.toLocaleString('en-IN')}
                </span>
                <span className="text-stone-400">/month</span>
              </div>
              {listing.deposit > 0 && (
                <div className="text-sm text-stone-400 mb-4">
                  Deposit: ₹{listing.deposit?.toLocaleString('en-IN')}
                </div>
              )}

              <hr className="border-stone-100 my-4" />

              {/* Price Verdict */}
              <PriceVerdict data={priceData} />

              {/* Trust Score */}
              {listing.trust_info && (
                <div className="mb-4">
                  <TrustBar score={listing.trust_info.score} />
                  <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2 text-xs text-stone-400">
                    <span>{listing.trust_info.id_verified   ? '✅ ID Verified'    : '❌ ID Not Verified'}</span>
                    <span>{listing.trust_info.bill_uploaded  ? '✅ Bill Proof'     : '❌ No Bill'         }</span>
                    {listing.trust_info.video_walkthrough &&  <span>✅ Video Tour</span>}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="space-y-3">
                <Button
                  variant="primary"
                  fullWidth
                  loading={chatLoading}
                  onClick={handleStartChat}
                >
                  💬 Chat with Owner
                </Button>
                {user && (
                  <Link to={`/agreements/create/${listing.id}`}>
                    <Button variant="ghost" fullWidth>📄 Generate Agreement</Button>
                  </Link>
                )}
                {!user && (
                  <Link to="/login">
                    <Button variant="ghost" fullWidth>Login to Contact Owner</Button>
                  </Link>
                )}
              </div>
            </div>

            {/* Stats */}
            <div className="card p-4 flex justify-around text-center text-sm text-stone-400">
              <div>
                <div className="font-bold text-navy text-lg">{listing.views_count || 0}</div>
                <div className="text-xs">Views</div>
              </div>
              <div>
                <div className="font-bold text-navy text-lg">{listing.trust_info?.reviews_count || 0}</div>
                <div className="text-xs">Reviews</div>
              </div>
              <div>
                <div className="font-bold text-navy text-lg capitalize">{listing.rental_period?.replace('_', ' ')}</div>
                <div className="text-xs">Period</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}