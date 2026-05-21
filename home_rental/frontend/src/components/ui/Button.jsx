import { Loader2 } from 'lucide-react'

const variants = {
  primary: 'btn-primary',
  ghost:   'btn-ghost',
  ochre:   'btn-ochre',
  danger:  'inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-red-500 text-white font-semibold text-sm transition-all duration-200 hover:bg-red-600 hover:-translate-y-0.5 hover:shadow-lg',
  success: 'inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-green-500 text-white font-semibold text-sm transition-all duration-200 hover:bg-green-600 hover:-translate-y-0.5 hover:shadow-lg',
}

const sizes = {
  sm:  'text-xs px-3.5 py-1.5',
  md:  '',
  lg:  'text-base px-7 py-3',
  xl:  'text-lg px-9 py-4',
}

export default function Button({
  children,
  variant  = 'primary',
  size     = 'md',
  loading  = false,
  disabled = false,
  icon,
  className = '',
  fullWidth = false,
  type      = 'button',
  onClick,
  ...props
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full justify-center' : ''}
        ${disabled || loading ? 'opacity-60 cursor-not-allowed transform-none' : ''}
        ${className}
      `}
      {...props}
    >
      {loading
        ? <Loader2 size={16} className="animate-spin" />
        : icon
      }
      {children}
    </button>
  )
}