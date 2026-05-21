import { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  size      = 'md',
  showClose = true,
}) {
  const sizes = {
    sm:  'max-w-md',
    md:  'max-w-lg',
    lg:  'max-w-2xl',
    xl:  'max-w-4xl',
    full:'max-w-6xl',
  }

  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose?.() }
    if (isOpen) document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Lock body scroll
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-navy/60 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      {/* Panel */}
      <div className={`
        relative w-full ${sizes[size]}
        bg-white rounded-2xl shadow-xl
        animate-fade-in-up max-h-[90vh] overflow-y-auto
      `}>
        {/* Header */}
        {(title || showClose) && (
          <div className="flex items-center justify-between p-6 border-b border-stone-100">
            {title && (
              <h2 className="font-display font-bold text-xl text-navy">
                {title}
              </h2>
            )}
            {showClose && (
              <button
                onClick={onClose}
                className="w-9 h-9 rounded-full flex items-center justify-center text-stone-400 hover:text-navy hover:bg-stone-100 transition-colors ml-auto"
              >
                <X size={20} />
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  )
}