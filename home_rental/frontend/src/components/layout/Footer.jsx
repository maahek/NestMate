import { Link } from 'react-router-dom'

const links = {
  Renters:  [
    { to: '/search',   label: 'Browse Listings' },
    { to: '/map',      label: 'Map Search' },
    { to: '/roommate', label: 'Find Roommate' },
  ],
  Owners: [
    { to: '/listing/create', label: 'List Property' },
    { to: '/agreements',     label: 'My Agreements' },
  ],
  Platform: [
    { to: '/analytics/environment', label: 'Environment Scores' },
    { to: '/analytics/market',      label: 'Market Prices' },
    { to: '/analytics/trust-leaderboard', label: 'Trust Leaderboard' },
  ],
}

export default function Footer() {
  return (
    <footer className="bg-navy text-white/70">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">

          {/* Brand */}
          <div>
            <div className="font-display font-black text-2xl text-white mb-3">
              🏠 NestMate
            </div>
            <p className="text-sm text-white/50 leading-relaxed max-w-56">
              India's smartest rental platform. AI-powered matching, verified listings, fair pricing.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(links).map(([title, items]) => (
            <div key={title}>
              <h4 className="text-white font-semibold text-xs uppercase tracking-widest mb-4">
                {title}
              </h4>
              <ul className="space-y-2">
                {items.map((item) => (
                  <li key={item.to}>
                    <Link
                      to={item.to}
                      className="text-sm text-white/60 hover:text-ochre-light transition-colors duration-200 hover:translate-x-0.5 inline-block"
                    >
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-white/10 pt-6 text-center text-xs text-white/30">
          © 2026 NestMate. Built with Django + MongoDB + React + ❤️
        </div>
      </div>
    </footer>
  )
}