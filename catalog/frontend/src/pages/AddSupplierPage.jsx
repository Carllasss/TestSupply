import { useState } from 'react'
import { Link } from 'react-router-dom'
import { scrapeSupplier, extractSupplier } from '../api/suppliers'
import { Button } from '../components/Button'
import { DiscoverPanel } from '../components/DiscoverPanel'
import { Spinner } from '../components/Spinner'
import './AddSupplierPage.css'

const MODES = [
  { id: 'url', label: 'По ссылке' },
  { id: 'text', label: 'По тексту' },
  { id: 'web', label: 'Найти в интернете' },
]

export function AddSupplierPage() {
  const [mode, setMode] = useState('url')
  const [url, setUrl] = useState('')
  const [text, setText] = useState('')
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const busy = status === 'loading'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('loading')
    setError('')
    setResult(null)
    try {
      const supplier = mode === 'url' ? await scrapeSupplier(url.trim()) : await extractSupplier(text.trim())
      setResult(supplier)
      setStatus('done')
    } catch (err) {
      setError(err.message || 'Не получилось разобрать текст')
      setStatus('error')
    }
  }

  return (
    <div className="add-page">
      <div className="container page-in">
        <div className="add-page__head">
          <h1>Добавить поставщика</h1>
          <p>
            Добавь поставщика по ссылке или тексту. Чтобы найти новые компании,
            выбери поиск в интернете.
          </p>
        </div>

        <div className="add-page__modes">
          {MODES.map((m) => (
            <button
              key={m.id}
              className={`add-page__mode ${mode === m.id ? 'is-active' : ''}`}
              onClick={() => setMode(m.id)}
              type="button"
            >
              {m.label}
            </button>
          ))}
        </div>

        {mode === 'web' ? (
          <DiscoverPanel />
        ) : (
          <>
            <form className="add-page__form" onSubmit={handleSubmit}>
              {mode === 'url' ? (
                <label className="add-page__field-label">Сайт поставщика
                <input
                  className="add-page__input"
                  type="url"
                  required
                  placeholder="https://postavshik-site.ru"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
                </label>
              ) : (
                <label className="add-page__field-label">Описание поставщика
                <textarea
                  className="add-page__textarea"
                  required
                  minLength={20}
                  rows={8}
                  placeholder="Вставь текст: описание с сайта, прайс, визитку поставщика"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
                </label>
              )}

              <Button variant="cyan" arrow={!busy} disabled={busy} type="submit">
                {busy ? <Spinner label="Разбираю через ИИ..." /> : 'Разобрать и добавить'}
              </Button>
            </form>

            {error && <p className="add-page__error">{error}</p>}

            {result && (
              <div className="add-page__result card-in">
                <p className="add-page__result-label">Готово, карточка добавлена в каталог</p>
                <h2>{result.name}</h2>
                <p className="add-page__result-meta">{result.category} · {result.region}</p>
                <p className="add-page__result-desc">{result.description}</p>
                <Link to={`/suppliers/${result.id}`} className="add-page__result-link">
                  Открыть карточку в каталоге →
                </Link>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
