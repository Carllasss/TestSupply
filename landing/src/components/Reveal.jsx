import { useStagger } from '../hooks/useStagger'
import './Reveal.css'

export function Reveal({ children, className = '' }) {
  const [ref, visible] = useStagger(0.2)
  return (
    <div ref={ref} className={`reveal ${visible ? 'is-visible' : ''} ${className}`}>
      {children}
    </div>
  )
}
