import { useEffect, useRef } from 'react'
import './SearchTicker.css'

export function SearchTicker({ lines }) {
  const viewportRef = useRef(null)

  useEffect(() => {
    const el = viewportRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [lines])

  return (
    <section className="search-ticker" aria-label="Ход поиска в интернете">
      <div className="search-ticker__head">
        <span className="search-ticker__activity" aria-hidden="true" />
        <strong>Ищем поставщиков в интернете</strong>
        {lines.length > 0 && <span className="search-ticker__count">Шагов: {lines.length}</span>}
      </div>
      <div className="search-ticker__viewport" ref={viewportRef} role="log" aria-live="polite" aria-relevant="additions">
        {lines.length === 0 ? (
          <p className="search-ticker__pending">Подключаемся к поиску…</p>
        ) : lines.map((line, i) => (
          <div key={i} className={`search-ticker__line ${i === lines.length - 1 ? 'search-ticker__line--current' : ''}`}>
            <span className="search-ticker__dot" aria-hidden="true" />
            <span>{line}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
