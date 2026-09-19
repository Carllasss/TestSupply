import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { compareSuppliers } from '../api/suppliers'
import { Spinner } from '../components/Spinner'
import './ComparePage.css'

const DASH = 'не опубликовано'

const ROWS = [
  ['product_lines', 'Ассортимент'],
  ['region', 'Местонахождение'],
  ['delivery_terms', 'Условия и география доставки'],
  ['moq', 'MOQ'],
  ['price_note', 'Цена'],
  ['certificates', 'Документы'],
]

function contactsOf(s) {
  const parts = [s.contact_phone, s.contact_email, s.website].filter(Boolean)
  return parts.length ? parts.join(', ') : DASH
}

export function ComparePage() {
  const [params] = useSearchParams()
  const ids = params.get('ids')?.split(',').map(Number).filter(Boolean) || []
  const query = params.get('q') || ''

  const [suppliers, setSuppliers] = useState([])
  const [recommendation, setRecommendation] = useState(null)
  const [recommendedSupplierId, setRecommendedSupplierId] = useState(null)
  const [status, setStatus] = useState('loading')
  const winner = suppliers.find((supplier) => supplier.id === recommendedSupplierId)

  useEffect(() => {
    if (ids.length < 2) {
      setStatus('error')
      return
    }
    compareSuppliers(ids, query)
      .then((data) => {
        setSuppliers(data.suppliers)
        setRecommendation(data.recommendation)
        setRecommendedSupplierId(data.recommended_supplier_id ?? null)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [params])

  if (status === 'loading') {
    return (
      <div className="container compare-page">
        <Spinner label="Собираем таблицу и рекомендацию..." size={20} />
      </div>
    )
  }
  if (status === 'error') {
    return (
      <div className="container compare-page">
        <p>Не получилось собрать сравнение. Выбери минимум 2 компании в каталоге.</p>
        <Link to="/" className="compare-page__back">Назад в каталог</Link>
      </div>
    )
  }

  return (
    <div className="compare-page">
      <div className="container page-in">
        <Link to="/" className="compare-page__back">Назад в каталог</Link>
        <h1>Сравнение поставщиков</h1>

        <div className="compare-page__table-wrap">
          <table className="compare-page__table">
            <thead>
              <tr>
                <th>Компания</th>
                {suppliers.map((s) => (
                  <th key={s.id} scope="col" className={s.id === recommendedSupplierId ? 'compare-page__winner' : undefined}><Link to={`/suppliers/${s.id}`}>{s.name}</Link>{s.id === recommendedSupplierId && <span className="compare-page__winner-badge">Выбор ИИ</span>}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ROWS.map(([key, label]) => (
                <tr key={key}>
                  <td className="compare-page__row-label">{label}</td>
                  {suppliers.map((s) => (
                    <td key={s.id} className={s.id === recommendedSupplierId ? 'compare-page__winner' : undefined}>{s[key] || DASH}</td>
                  ))}
                </tr>
              ))}
              <tr>
                <td className="compare-page__row-label">Контакты</td>
                {suppliers.map((s) => (
                  <td key={s.id} className={s.id === recommendedSupplierId ? 'compare-page__winner' : undefined}>{contactsOf(s)}</td>
                ))}
              </tr>
              <tr>
                <td className="compare-page__row-label">Источник</td>
                {suppliers.map((s) => (
                  <td key={s.id} className={s.id === recommendedSupplierId ? 'compare-page__winner' : undefined}>
                    {s.source_url ? <a href={s.source_url} target="_blank" rel="noreferrer">ссылка</a> : DASH}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Same data as the table above, laid out as stacked cards — swapped
            in on narrow screens via CSS so nothing needs a horizontal swipe. */}
        <div className="compare-page__cards">
          {suppliers.map((s) => (
            <div key={s.id} className={`compare-page__card ${s.id === recommendedSupplierId ? 'compare-page__card--winner' : ''}`}>
              <div className="compare-page__card-head">
                <Link to={`/suppliers/${s.id}`}>{s.name}</Link>
                {s.id === recommendedSupplierId && <span className="compare-page__winner-badge">Выбор ИИ</span>}
              </div>
              <dl className="compare-page__card-rows">
                {ROWS.map(([key, label]) => (
                  <div className="compare-page__card-row" key={key}>
                    <dt>{label}</dt>
                    <dd>{s[key] || DASH}</dd>
                  </div>
                ))}
                <div className="compare-page__card-row">
                  <dt>Контакты</dt>
                  <dd>{contactsOf(s)}</dd>
                </div>
                <div className="compare-page__card-row">
                  <dt>Источник</dt>
                  <dd>{s.source_url ? <a href={s.source_url} target="_blank" rel="noreferrer">ссылка</a> : DASH}</dd>
                </div>
              </dl>
            </div>
          ))}
        </div>

        {recommendation && (
          <div className="compare-page__recommendation card-in">
            <span>Что подходит лучше</span>
            {winner && <strong className="compare-page__recommended-name">{winner.name} <span>Выбор ИИ</span></strong>}
            <p>{recommendation}</p>
          </div>
        )}
      </div>
    </div>
  )
}
