import './Button.css'

const Arrow = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 5l7 7-7 7" />
  </svg>
)

export function Button({ variant = 'cyan', arrow = false, as: As = 'button', children, ...rest }) {
  return (
    <As className={`btn btn--${variant}`} {...rest}>
      {children}
      {arrow && <Arrow />}
    </As>
  )
}
