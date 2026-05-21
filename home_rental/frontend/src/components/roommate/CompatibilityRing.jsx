export default function CompatibilityRing({ score, size = 'md' }) {
  const sizes = {
    sm:  { outer: 72,  border: 5,  font: 'text-lg'  },
    md:  { outer: 90,  border: 6,  font: 'text-xl'  },
    lg:  { outer: 120, border: 8,  font: 'text-3xl' },
  }
  const cfg = sizes[size] || sizes.md

  const color =
    score >= 80 ? '#16a34a' :
    score >= 60 ? '#d97706' : '#dc2626'

  const gradient =
    score >= 80 ? 'linear-gradient(135deg,#d97706,#16a34a)' :
    score >= 60 ? 'linear-gradient(135deg,#fbbf24,#d97706)' :
                  'linear-gradient(135deg,#fca5a5,#dc2626)'

  return (
    <div
      className="flex-shrink-0 flex flex-col items-center justify-center rounded-full"
      style={{
        width:      cfg.outer,
        height:     cfg.outer,
        border:     `${cfg.border}px solid transparent`,
        background: `linear-gradient(white,white) padding-box, ${gradient} border-box`,
      }}
    >
      <div
        className={`font-display font-black ${cfg.font} leading-none`}
        style={{ color }}
      >
        {Math.round(score)}%
      </div>
      <div className="text-[10px] text-stone-400 mt-0.5">Match</div>
    </div>
  )
}