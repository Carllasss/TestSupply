import { useEffect, useRef } from 'react'
import './SearchTicker.css'

export function SearchTicker({ lines }) {
  const viewportRef = useRef(null)

  useEffect(() => {
    const el = viewportRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [lines])

  if (!lines.length) return null

  return (
    <div className="search-ticker">
      <div className="search-ticker__viewport" ref={viewportRef}>
        {lines.map((line, i) => (
          <div key={i} className="search-ticker__line">{line}</div>
        ))}
      </div>
    </div>
  )
}
