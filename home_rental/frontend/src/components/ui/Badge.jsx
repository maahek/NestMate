const variants = {
  trust:   'bg-green-500/90 text-white',
  scam:    'bg-red-500/90 text-white',
  caution: 'bg-ochre-DEFAULT/90 text-white',
  student: 'bg-purple-600/90 text-white',
  type:    'bg-white/90 text-navy-DEFAULT',
  info:    'bg-blue-100 text-blue-700',
}

export default function Badge({ variant = 'info', children, className = '' }) {
  return (
    <span className={`
      inline-flex items-center gap-1 px-2 py-0.5 rounded-full
      text-[11px] font-bold tracking-wide backdrop-blur-sm
      ${variants[variant]} ${className}
    `}>
      {children}
    </span>
  )
}