export default function Card({
  children,
  className   = '',
  padding     = true,
  hover       = false,
  onClick,
  ...props
}) {
  return (
    <div
      onClick={onClick}
      className={`
        card
        ${padding ? 'p-6' : ''}
        ${hover   ? 'hover:-translate-y-1 hover:shadow-lg cursor-pointer' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  )
}

Card.Header = function CardHeader({ children, className = '' }) {
  return (
    <div className={`flex items-center justify-between mb-5 ${className}`}>
      {children}
    </div>
  )
}

Card.Title = function CardTitle({ children, className = '' }) {
  return (
    <h3 className={`font-display font-bold text-lg text-navy ${className}`}>
      {children}
    </h3>
  )
}

Card.Body = function CardBody({ children, className = '' }) {
  return (
    <div className={className}>
      {children}
    </div>
  )
}

Card.Footer = function CardFooter({ children, className = '' }) {
  return (
    <div className={`mt-5 pt-5 border-t border-stone-100 ${className}`}>
      {children}
    </div>
  )
}