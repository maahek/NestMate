import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { roommateAPI } from '../api/roommate'
import { CITIES, SLEEP_OPTIONS, WORK_OPTIONS, DIET_OPTIONS, GUEST_OPTIONS } from '../utils/constants'
import Button from '../components/ui/Button'
import toast from 'react-hot-toast'

// Small UI subcomponents moved out to avoid recreation each render
const RadioGroup = ({ name, options, value, update }) => (
  <div className="flex flex-wrap gap-2">
    {options.map(opt => (
      <button
        key={opt.value}
        type="button"
        onClick={() => update(name, opt.value)}
        className={`flex-1 min-w-28 py-3 px-3 rounded-xl text-sm font-semibold border transition-all text-center ${
          value === opt.value
            ? 'bg-ochre-bg border-ochre text-navy'
            : 'border-stone-200 text-stone-500 hover:border-ochre'
        }`}
      >
        <div>{opt.label}</div>
        {opt.desc && <div className="text-xs font-normal mt-0.5 opacity-70">{opt.desc}</div>}
      </button>
    ))}
  </div>
)

const BoolGroup = ({ name, value, update }) => (
  <div className="flex gap-3">
    {[{v:'yes',l:'✅ Yes'},{v:'no',l:'❌ No'}].map(o => (
      <button key={o.v} type="button" onClick={() => update(name, o.v)}
        className={`flex-1 py-3 rounded-xl text-sm font-semibold border transition-all ${value === o.v ? 'bg-ochre-bg border-ochre text-navy' : 'border-stone-200 text-stone-500 hover:border-ochre'}`}>
        {o.l}
      </button>
    ))}
  </div>
)

const STEPS = ['Basics', 'Location & Budget', 'Lifestyle', 'Habits']

export default function RoommateQuestionnaire() {
  const navigate        = useNavigate()
  const [params]        = useSearchParams()
  const [step,  setStep]  = useState(0)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    full_name: '', age: '', gender: 'other', profession: '',
    city: params.get('city') || '', locality: '',
    budget_min: '', budget_max: '',
    sleep_schedule: 'flexible', smoking: 'no', drinking: 'no',
    pets: 'no', cleanliness: 3,
    guests_frequency: 'rarely', work_schedule: 'day_shift',
    diet: 'any', gender_pref: 'any', about: '',
  })

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const nextStep = () => {
    if (step === 1 && (!form.city || !form.budget_min || !form.budget_max)) {
      toast.error('Please fill city and budget')
      return
    }
    setStep(s => Math.min(s + 1, STEPS.length - 1))
    window.scrollTo(0, 0)
  }

  const prevStep = () => {
    setStep(s => Math.max(s - 1, 0))
    window.scrollTo(0, 0)
  }

  const handleSubmit = async () => {
    setSaving(true)
    try {
      const payload = {
        ...form,
        smoking:  form.smoking  === 'yes',
        drinking: form.drinking === 'yes',
        pets:     form.pets     === 'yes',
      }
      // Use correct API endpoint
      await roommateAPI.saveProfile(payload)
      toast.success('✅ Profile saved! Finding your matches...')
      navigate('/roommate/matches')
    } catch {
      toast.error('Failed to save profile')
    } finally {
      setSaving(false)
    }
  }
  
  // Render

  return (
    <div className="max-w-xl mx-auto px-4 py-12">
      <div className="text-center mb-8">
        <div className="text-5xl mb-3">🤝</div>
        <h1 className="font-display font-bold text-3xl text-navy">Find Your Roommate</h1>
        <p className="text-stone-400 mt-2">Step {step + 1} of {STEPS.length}: {STEPS[step]}</p>
      </div>

      {/* Step indicator */}
      <div className="flex gap-2 justify-center mb-8">
        {STEPS.map((_, i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full transition-all ${
            i < step ? 'bg-green-500' : i === step ? 'bg-ochre' : 'bg-stone-200'
          }`} />
        ))}
      </div>

      <div className="card p-8 space-y-5">

        {/* Step 0: Basics */}
        {step === 0 && (
          <>
            <h3 className="font-display font-bold text-xl text-navy">📋 About You</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Full Name</label>
                <input type="text" value={form.full_name} onChange={e => update('full_name', e.target.value)} className="form-input" placeholder="Your name" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Age</label>
                <input type="number" value={form.age} onChange={e => update('age', e.target.value)} className="form-input" placeholder="24" min="18" max="80" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Gender</label>
              <div className="flex gap-3">
                {[{v:'male',l:'♂️ Male'},{v:'female',l:'♀️ Female'},{v:'other',l:'⚧ Other'}].map(g => (
                  <button key={g.v} type="button" onClick={() => update('gender', g.v)}
                    className={`flex-1 py-2.5 rounded-xl text-sm font-semibold border transition-all ${form.gender === g.v ? 'bg-ochre-bg border-ochre text-navy' : 'border-stone-200 text-stone-500 hover:border-ochre'}`}>
                    {g.l}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Profession</label>
              <input type="text" value={form.profession} onChange={e => update('profession', e.target.value)} className="form-input" placeholder="Software Engineer, Student..." />
            </div>
          </>
        )}

        {/* Step 1: Location & Budget */}
        {step === 1 && (
          <>
            <h3 className="font-display font-bold text-xl text-navy">📍 Location & Budget</h3>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">City *</label>
              <select value={form.city} onChange={e => update('city', e.target.value)} className="form-input" required>
                <option value="">Select city</option>
                {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">Preferred Locality</label>
              <input type="text" value={form.locality} onChange={e => update('locality', e.target.value)} className="form-input" placeholder="e.g. Koramangala" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Min Budget (₹/mo) *</label>
                <input type="number" value={form.budget_min} onChange={e => update('budget_min', e.target.value)} className="form-input" placeholder="5000" required />
              </div>
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">Max Budget (₹/mo) *</label>
                <input type="number" value={form.budget_max} onChange={e => update('budget_max', e.target.value)} className="form-input" placeholder="15000" required />
              </div>
            </div>
          </>
        )}

        {/* Step 2: Lifestyle */}
        {step === 2 && (
          <>
            <h3 className="font-display font-bold text-xl text-navy">🌙 Lifestyle</h3>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Sleep Schedule</label>
              <RadioGroup name="sleep_schedule" options={SLEEP_OPTIONS} value={form.sleep_schedule} update={update} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Do you smoke?</label>
              <BoolGroup name="smoking" value={form.smoking} update={update} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Do you have pets?</label>
              <BoolGroup name="pets" value={form.pets} update={update} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Diet</label>
              <RadioGroup name="diet" options={DIET_OPTIONS} value={form.diet} update={update} />
            </div>
          </>
        )}

        {/* Step 3: Habits */}
        {step === 3 && (
          <>
            <h3 className="font-display font-bold text-xl text-navy">🏠 Living Habits</h3>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">
                Cleanliness Level: <span className="text-ochre">{form.cleanliness}/5</span>
              </label>
              <input
                type="range" min="1" max="5" value={form.cleanliness}
                onChange={e => update('cleanliness', parseInt(e.target.value))}
                className="w-full accent-ochre"
              />
              <div className="flex justify-between text-xs text-stone-400 mt-1">
                <span>Relaxed</span><span>Moderate</span><span>Spotless</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Guest Frequency</label>
              <RadioGroup name="guests_frequency" options={GUEST_OPTIONS} value={form.guests_frequency} update={update} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Work Schedule</label>
              <RadioGroup name="work_schedule" options={WORK_OPTIONS} value={form.work_schedule} update={update} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-2">Roommate Gender Preference</label>
              <div className="flex gap-3">
                {[{v:'any',l:'🤷 Any'},{v:'male',l:'♂️ Male'},{v:'female',l:'♀️ Female'}].map(g => (
                  <button key={g.v} type="button" onClick={() => update('gender_pref', g.v)}
                    className={`flex-1 py-2.5 rounded-xl text-sm font-semibold border transition-all ${form.gender_pref === g.v ? 'bg-ochre-bg border-ochre text-navy' : 'border-stone-200 text-stone-500 hover:border-ochre'}`}>
                    {g.l}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy mb-1.5">About You (optional)</label>
              <textarea value={form.about} onChange={e => update('about', e.target.value)} className="form-input min-h-20" placeholder="Tell potential roommates about yourself..." maxLength={500} />
            </div>
          </>
        )}

        {/* Navigation */}
        <div className="flex gap-3 pt-2">
          {step > 0 && (
            <Button variant="ghost" onClick={prevStep}>← Back</Button>
          )}
          {step < STEPS.length - 1 ? (
            <Button variant="primary" onClick={nextStep} className="flex-1 justify-center">
              Next →
            </Button>
          ) : (
            <Button variant="ochre" onClick={handleSubmit} loading={saving} className="flex-1 justify-center">
              🤝 Find My Matches
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}