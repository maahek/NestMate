export default function TrustBar({ score }) {
  const color =
    score >= 80 ? 'from-ochre-DEFAULT to-green-500' :
    score >= 60 ? 'from-ochre-light to-ochre-DEFAULT' :
                  'from-red-400 to-ochre-DEFAULT'

  return (
    <div className="mt-1">
      <div className="flex justify-between text-[10px] text-stone-400 mb-1">
        <span>Trust Score</span>
        <span className="font-semibold">{score}/100</span>
      </div>
      <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-700`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  )
}