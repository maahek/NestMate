import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { roommateAPI } from '../api/roommate'

export default function RoommateHome() {
  const [cityStats, setCityStats] = useState({})

  useEffect(() => {
    roommateAPI.getCityStats()
      .then(r => setCityStats(r.data.stats || {}))
      .catch(() => {})
  }, [])

  const steps = [
    { icon: '📋', title: 'Fill the Quiz',         desc: 'Answer 10 questions about your budget, lifestyle, and habits.' },
    { icon: '🤖', title: 'AI Matches You',         desc: 'Our algorithm scores compatibility across 8 dimensions.' },
    { icon: '🤝', title: 'Connect & Move In',      desc: 'Chat with your top matches and find your perfect roommate.' },
  ]

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-navy to-blue-900 py-24 text-center text-white px-4">
        <div className="max-w-2xl mx-auto">
          <div className="text-6xl mb-5">🤝</div>
          <h1 className="font-display font-black text-5xl text-white mb-4">
            Find Your Perfect Roommate
          </h1>
          <p className="text-white/70 text-lg mb-8 leading-relaxed">
            Our AI matches you with compatible roommates based on budget, lifestyle, sleep schedule, and more.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/roommate/quiz" className="btn-ochre text-base px-7 py-3">Take the Quiz →</Link>
            <Link to="/roommate/matches" className="inline-flex items-center gap-2 px-7 py-3 rounded-full bg-white/10 text-white font-semibold border border-white/20 hover:bg-white/20 transition-all">
              My Matches
            </Link>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <div className="bg-white border-b border-stone-100 py-5">
        <div className="max-w-4xl mx-auto px-4 flex justify-center gap-12 flex-wrap text-center">
          {[
            { num: '1,200+', label: 'Successful Matches' },
            { num: '8',      label: 'Major Cities'       },
            { num: '92%',    label: 'Satisfaction Rate'  },
            { num: 'Free',   label: 'No Hidden Charges'  },
          ].map(s => (
            <div key={s.label}>
              <div className="font-display font-black text-2xl text-navy">{s.num}</div>
              <div className="text-xs text-stone-400">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* How it works */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-display font-bold text-4xl text-navy mb-12">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((s, i) => (
              <div key={i}>
                <div className="w-16 h-16 bg-ochre-bg rounded-full flex items-center justify-center text-2xl mx-auto mb-4">{s.icon}</div>
                <div className="text-xs font-bold text-ochre uppercase tracking-widest mb-1">Step 0{i+1}</div>
                <h3 className="font-display font-bold text-xl text-navy mb-2">{s.title}</h3>
                <p className="text-stone-400 text-sm leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* City seekers */}
      {Object.keys(cityStats).length > 0 && (
        <section className="py-16 px-4 bg-stone-50">
          <div className="max-w-5xl mx-auto">
            <h2 className="font-display font-bold text-3xl text-navy text-center mb-8">Active Seekers by City</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {Object.entries(cityStats).map(([city, count]) => (
                <Link key={city} to={`/roommate/quiz?city=${city}`}>
                  <div className="card p-4 text-center hover:-translate-y-1 hover:shadow-lg transition-all cursor-pointer">
                    <div className="text-2xl mb-2">🏙️</div>
                    <div className="font-semibold text-navy">{city}</div>
                    <div className="font-display font-black text-2xl text-ochre mt-1">{count}</div>
                    <div className="text-xs text-stone-400">active seekers</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="bg-gradient-to-br from-ochre to-amber-800 py-20 text-center text-white px-4">
        <div className="max-w-xl mx-auto">
          <h2 className="font-display font-bold text-4xl text-white mb-4">Ready to Find Your Match?</h2>
          <p className="text-white/80 mb-8">Takes only 3 minutes. Answer a few questions and see your best matches.</p>
          <Link to="/roommate/quiz" className="inline-flex items-center gap-2 bg-white text-navy font-bold px-8 py-3.5 rounded-full hover:bg-ochre-bg transition-all hover:-translate-y-0.5 shadow-lg">
            Start Matching — It's Free →
          </Link>
        </div>
      </section>
    </div>
  )
}