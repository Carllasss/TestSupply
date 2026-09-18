import './CardFacts.css'

const DASH = 'не опубликовано'

export function CardFacts({ category, region, moq, price_note }) {
  return (
    <div className="card-facts">
      <span className="fact"><span className="fact__label">Категория</span><span className="fact__value" title={category}>{category}</span></span>
      <span className="fact"><span className="fact__label">Регион</span><span className="fact__value" title={region}>{region}</span></span>
      <span className="fact"><span className="fact__label">Партия</span><span className="fact__value" title={moq || DASH}>{moq || DASH}</span></span>
      <span className="fact"><span className="fact__label">Цена</span><span className="fact__value" title={price_note || DASH}>{price_note || DASH}</span></span>
    </div>
  )
}
