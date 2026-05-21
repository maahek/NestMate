// ── Cities ────────────────────────────────────────────────────────────────────
export const CITIES = [
  'Mumbai', 'Pune', 'Bangalore', 'Delhi',
  'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad',
]

// ── Property Types ────────────────────────────────────────────────────────────
export const LISTING_TYPES_FLAT = {
  residential: [
    { value: 'apartment',   label: '🏢 Apartment'         },
    { value: 'house',       label: '🏠 Independent House'  },
    { value: 'villa',       label: '🏡 Villa / Bungalow'   },
    { value: 'studio',      label: '🛋️ Studio Apartment'   },
    { value: 'pg',          label: '🛏️ PG / Paying Guest'  },
    { value: 'shared_room', label: '👥 Shared Room'        },
    { value: 'hostel',      label: '🏨 Hostel'             },
  ],
  commercial: [
    { value: 'shop',      label: '🏪 Shop / Retail Space' },
    { value: 'office',    label: '🏢 Office Space'        },
    { value: 'warehouse', label: '🏭 Warehouse / Godown'  },
    { value: 'showroom',  label: '🚘 Showroom'            },
    { value: 'coworking', label: '💻 Coworking Space'     },
  ],
  special: [
    { value: 'studio_space', label: '📸 Studio Space'        },
    { value: 'event_hall',   label: '🎉 Event Hall / Banquet' },
    { value: 'garage',       label: '🚗 Garage / Parking'     },
    { value: 'farmhouse',    label: '🌾 Farmhouse'            },
    { value: 'plot',         label: '📐 Plot / Land'          },
  ],
}

export const ALL_LISTING_TYPES = [
  ...LISTING_TYPES_FLAT.residential,
  ...LISTING_TYPES_FLAT.commercial,
  ...LISTING_TYPES_FLAT.special,
]

export const COMMERCIAL_TYPE_VALUES = LISTING_TYPES_FLAT.commercial.map(t => t.value)
export const HIDE_BEDS_TYPES = [
  'studio', 'pg', 'shared_room', 'hostel',
  'shop', 'office', 'warehouse', 'showroom', 'coworking',
  'studio_space', 'event_hall', 'garage', 'plot',
]

// ── Amenities ─────────────────────────────────────────────────────────────────
export const AMENITIES_RESIDENTIAL = [
  'wifi', 'ac', 'parking', 'gym', 'lift', 'geyser',
  'washing_machine', 'fridge', 'tv', 'gas',
  'security', 'cctv', 'garden', 'terrace',
]

export const AMENITIES_COMMERCIAL = [
  'reception', 'conference_room', 'cafeteria', 'power_backup',
  'loading_dock', 'server_room', 'fire_safety', 'restrooms',
  'pantry', 'soundproofing', 'high_speed_internet',
]

// ── Roommate constants ────────────────────────────────────────────────────────
export const SLEEP_OPTIONS = [
  { value: 'early_bird', label: '🌅 Early Bird',  desc: 'Asleep by 10 PM'    },
  { value: 'flexible',   label: '😎 Flexible',    desc: 'Adapt to roommate'  },
  { value: 'night_owl',  label: '🦉 Night Owl',   desc: 'Up past midnight'   },
]

export const WORK_OPTIONS = [
  { value: 'day_shift',   label: '💼 Day Shift',      desc: '9 AM – 6 PM' },
  { value: 'night_shift', label: '🌙 Night Shift',    desc: 'Evening/Night' },
  { value: 'wfh',         label: '🏠 Work From Home', desc: 'Home all day' },
  { value: 'student',     label: '🎓 Student',        desc: 'College schedule' },
]

export const DIET_OPTIONS = [
  { value: 'any',     label: '🍽️ No Preference' },
  { value: 'veg',     label: '🥗 Vegetarian'     },
  { value: 'non_veg', label: '🍗 Non-Vegetarian' },
  { value: 'vegan',   label: '🌱 Vegan'           },
]

export const GUEST_OPTIONS = [
  { value: 'never',     label: '🚫 Never'     },
  { value: 'rarely',    label: '🤏 Rarely'    },
  { value: 'sometimes', label: '😊 Sometimes' },
  { value: 'often',     label: '🎉 Often'     },
]

// ── Trust score breakdown ─────────────────────────────────────────────────────
export const TRUST_BREAKDOWN = [
  { key: 'id_verified',       icon: '🪪', label: 'Identity Verified',       points: 40, action: 'Upload Aadhaar / Passport'      },
  { key: 'bill_verified',     icon: '💡', label: 'Utility Bill Uploaded',   points: 25, action: 'Upload electricity or water bill' },
  { key: 'email_verified',    icon: '📧', label: 'Email Verified',          points: 10, action: 'Verify your email address'        },
  { key: 'phone',             icon: '📱', label: 'Phone Number Added',      points: 10, action: 'Add your phone number'            },
  { key: 'avatar_url',        icon: '🖼️', label: 'Profile Photo',           points: 5,  action: 'Upload a profile photo'           },
  { key: 'bio',               icon: '✍️', label: 'Bio Written',             points: 5,  action: 'Write something about yourself'   },
  { key: 'full_name',         icon: '👤', label: 'Full Name Added',         points: 5,  action: 'Add your full name'               },
]

// ── API base URL ──────────────────────────────────────────────────────────────
export const API_BASE = 'http://localhost:8000'

// ── WebSocket base ────────────────────────────────────────────────────────────
// In development: Vite proxies /ws to localhost:8000
// In production: use wss:// of your backend domain
export const WS_BASE = ''
// ── Pagination ────────────────────────────────────────────────────────────────
export const PAGE_SIZE = 12

// ── Price verdict config ──────────────────────────────────────────────────────
export const VERDICT_CONFIG = {
  fair:       { color: 'text-green-600', bg: 'bg-green-50',   label: '✅ Fair Market Price' },
  overpriced: { color: 'text-red-500',   bg: 'bg-red-50',     label: '⚠️ Overpriced'        },
  underpriced:{ color: 'text-ochre',     bg: 'bg-ochre-bg',   label: '📉 Below Market'      },
  unknown:    { color: 'text-stone-400', bg: 'bg-stone-50',   label: 'Price Unknown'        },
}