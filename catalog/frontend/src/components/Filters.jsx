import './Filters.css'

const SORT_OPTIONS = [
  { value: '', label: 'По релевантности' },
  { value: 'price_asc', label: 'Сначала дешевле' },
  { value: 'moq_asc', label: 'Сначала маленькие партии' },
]

export function Filters({ facets, category, sort, hasPrice, hasMoq, onCategory, onSort, onHasPrice, onHasMoq, onReset }) {
  return (
    <aside className="filters" aria-label="Фильтры каталога">
      <div className="filters__head"><strong>Фильтры</strong><button type="button" onClick={onReset}>Сбросить</button></div>
      <div className="filters__block filters__block--categories">
        <h3 className="filters__title">Категория</h3>
        <div className="filters__categories">
        <label className="filters__option">
          <input
            type="radio"
            name="category"
            checked={!category}
            onChange={() => onCategory('')}
          />
          Все категории
        </label>
        {facets.categories.map((c) => (
          <label className="filters__option" key={c}>
            <input
              type="radio"
              name="category"
              checked={category === c}
              onChange={() => onCategory(c)}
            />
            {c}
          </label>
        ))}
        </div>
      </div>

      <div className="filters__block">
        <h3 className="filters__title">Сортировка</h3>
        {SORT_OPTIONS.map((opt) => (
          <label className="filters__option" key={opt.value}>
            <input
              type="radio"
              name="sort"
              checked={sort === opt.value}
              onChange={() => onSort(opt.value)}
            />
            {opt.label}
          </label>
        ))}
      </div>

      <div className="filters__block">
        <h3 className="filters__title">Заполненность карточки</h3>
        <label className="filters__option">
          <input type="checkbox" checked={hasPrice} onChange={(e) => onHasPrice(e.target.checked)} />
          Указана цена
        </label>
        <label className="filters__option">
          <input type="checkbox" checked={hasMoq} onChange={(e) => onHasMoq(e.target.checked)} />
          Указана партия
        </label>
      </div>
    </aside>
  )
}
