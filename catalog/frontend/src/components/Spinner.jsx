import './Spinner.css'

export function Spinner({ label, size = 16 }) {
  return (
    <span className="spinner-wrap">
      <span className="spinner" style={{ width: size, height: size }} aria-hidden="true" />
      {label && <span>{label}</span>}
    </span>
  )
}
