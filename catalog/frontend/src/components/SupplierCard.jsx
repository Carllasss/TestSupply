import { Link } from 'react-router-dom'
import { CardFacts } from './CardFacts'
import './SupplierCard.css'

const STATUS_LABEL = {
  demo: 'демо',
  found: 'добавлено из веб-поиска',
  verified: 'проверено вручную',
}

export function SupplierCard({ supplier, delay = 0, selected = false, atLimit = false, recommended = false, onToggleSelect }) {
  const statusLabel = STATUS_LABEL[supplier.status]

  return (
    <article className={`supplier-card ${recommended ? 'supplier-card--recommended' : ''}`} style={{ transitionDelay: `${delay}ms` }}>
      <Link to={`/suppliers/${supplier.id}`} className="supplier-card__link">
      <div className="supplier-card__top">
        <span className="supplier-card__status">{statusLabel || ' '}</span>
        {recommended && <span className="supplier-card__pick">Выбор ИИ</span>}
      </div>

      <h3 className="supplier-card__name">{supplier.name}</h3>
      <p className="supplier-card__desc">{supplier.description}</p>

      <CardFacts
        category={supplier.category}
        region={supplier.region}
        moq={supplier.moq}
        price_note={supplier.price_note}
      />

      </Link>
      {onToggleSelect && (
        <button
          type="button"
          className={`supplier-card__compare-btn ${selected ? 'is-selected' : ''}`}
          onClick={() => onToggleSelect(supplier.id)}
          disabled={atLimit && !selected}
          title={atLimit && !selected ? 'Можно сравнить до 4 поставщиков' : undefined}
        >
          {selected ? 'В сравнении ✓' : 'Добавить в сравнение'}
        </button>
      )}
    </article>
  )
}
