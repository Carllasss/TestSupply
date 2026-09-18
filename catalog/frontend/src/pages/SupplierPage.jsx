import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchSupplier } from '../api/suppliers'
import { Spinner } from '../components/Spinner'
import './SupplierPage.css'

const DASH = 'не опубликовано'

const STATUS_LABEL = {
  demo: 'демо',
  found: 'найдено в интернете',
  verified: 'проверено вручную',
}

const FIELDS = [
  ['product_lines', 'Что поставляет'],
  ['moq', 'Минимальный заказ'],
  ['price_note', 'Цена'],
  ['certificates', 'Документы и сертификаты'],
  ['delivery_terms', 'Условия и география доставки'],
  ['contact_phone', 'Телефон'],
  ['contact_email', 'Почта'],
  ['website', 'Сайт'],
  ['notes', 'Заметки'],
]

function fieldValue(supplier, key) {
  const value = supplier[key]
  if (!value) return DASH
  if (key === 'contact_phone') return <a href={`tel:${value}`}>{value}</a>
  if (key === 'contact_email') return <a href={`mailto:${value}`}>{value}</a>
  if (key === 'website') {
    const href = value.startsWith('http') ? value : `https://${value}`
    return <a href={href} target="_blank" rel="noreferrer">{value}</a>
  }
  return value
}

export function SupplierPage() {
  const { id } = useParams()
  const [supplier, setSupplier] = useState(null)
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    setStatus('loading')
    fetchSupplier(id)
      .then((data) => {
        setSupplier(data)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [id])

  if (status === 'loading') return <div className="container supplier-page"><Spinner label="Загрузка..." /></div>
  if (status === 'error' || !supplier) {
    return (
      <div className="container supplier-page">
        <p>Поставщик не найден.</p>
        <Link to="/" className="supplier-page__back">Назад в каталог</Link>
      </div>
    )
  }

  return (
    <div className="supplier-page">
      <div className="container page-in">
        <Link to="/" className="supplier-page__back">Назад в каталог</Link>

        <div className="supplier-page__head">
          <div className="supplier-page__head-top">
            <span className="supplier-page__cat">{supplier.category}</span>
            {STATUS_LABEL[supplier.status] && (
              <span className="supplier-page__status">{STATUS_LABEL[supplier.status]}</span>
            )}
          </div>
          <h1>{supplier.name}</h1>
          <p className="supplier-page__region">{supplier.region}</p>
        </div>

        <p className="supplier-page__desc">{supplier.description || DASH}</p>

        <div className="supplier-page__grid">
          {FIELDS.map(([key, label]) => (
            <div className="supplier-page__field" key={key}>
              <span>{label}</span>
              <p>{fieldValue(supplier, key)}</p>
            </div>
          ))}
        </div>

        {supplier.source_url && (
          <p className="supplier-page__source">
            Источник: <a href={supplier.source_url} target="_blank" rel="noreferrer">{supplier.source_url}</a>
          </p>
        )}
      </div>
    </div>
  )
}
