import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from './Button'
import { CardFacts } from './CardFacts'
import { ReviewCandidateModal } from './ReviewCandidateModal'

export function WebSupplierCard({ candidate, addedSupplier, onAdded, delay = 0, recommended = false }) {
  const preview = candidate.preview
  const [reviewing, setReviewing] = useState(false)

  return (
    <div className={`discover-card ${recommended ? 'discover-card--recommended' : ''}`} style={{ transitionDelay: `${delay}ms` }}>
      <div className="discover-card__top">
        <a href={candidate.url} target="_blank" rel="noreferrer" className="discover-card__domain">
          {candidate.domain}
        </a>
        {recommended ? <span className="discover-card__pick">Выбор ИИ</span> : <span className="discover-card__badge">найдено в интернете</span>}
      </div>

      <h3 className="discover-card__title">{preview.name}</h3>
      <p className="discover-card__desc">{preview.description}</p>

      <CardFacts
        category={preview.category}
        region={preview.region}
        moq={preview.moq}
        price_note={preview.price_note}
      />

      <div className="discover-card__actions">
        {addedSupplier ? (
          <Link to={`/suppliers/${addedSupplier.id}`} className="discover-card__added">
            Добавлено, открыть карточку →
          </Link>
        ) : (
          <Button variant="outline" type="button" onClick={() => setReviewing(true)}>
            Добавить в каталог
          </Button>
        )}
      </div>

      {reviewing && (
        <ReviewCandidateModal
          candidate={candidate}
          onClose={() => setReviewing(false)}
          onConfirmed={(supplier) => {
            setReviewing(false)
            onAdded(candidate.url, supplier)
          }}
        />
      )}
    </div>
  )
}
