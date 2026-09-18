import { useState } from 'react'
import { discoverSuppliers } from '../api/suppliers'
import { Button } from './Button'
import { Spinner } from './Spinner'
import { WebSupplierCard } from './WebSupplierCard'
import './DiscoverPanel.css'

export function DiscoverPanel() {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [candidates, setCandidates] = useState([])
  const [added, setAdded] = useState({})

  const busy = status === 'loading'
  const visibleCandidates = candidates.filter((c) => !c.already_in_catalog && c.preview)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('loading')
    setError('')
    setCandidates([])
    try {
      const data = await discoverSuppliers(query.trim())
      setSearchQuery(data.search_query)
      setCandidates(data.candidates)
      setStatus('done')
    } catch (err) {
      setError(err.message || 'Не получилось найти поставщиков')
      setStatus('error')
    }
  }

  return (
    <div className="discover">
      <form className="discover__form" onSubmit={handleSubmit}>
        <input
          className="discover__input"
          type="text"
          required
          minLength={3}
          placeholder="Например: поставщик безглютеновой муки в Москве оптом"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button variant="cyan" arrow={!busy} disabled={busy} type="submit">
          {busy ? <Spinner label="Ищу в интернете..." /> : 'Найти поставщиков'}
        </Button>
      </form>

      {error && <p className="discover__error">{error}</p>}

      {status === 'done' && (
        <p className="discover__query-used">Искал по запросу: «{searchQuery}»</p>
      )}

      {status === 'done' && visibleCandidates.length === 0 && (
        <p className="discover__empty">Ничего похожего на реальных поставщиков не нашлось.</p>
      )}

      <div className="discover__list">
        {visibleCandidates.map((c) => (
          <WebSupplierCard
            key={c.url}
            candidate={c}
            addedSupplier={added[c.url]}
            onAdded={(url, supplier) => setAdded((prev) => ({ ...prev, [url]: supplier }))}
          />
        ))}
      </div>
    </div>
  )
}
