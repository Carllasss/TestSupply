import { useState } from 'react'
import { Button } from './Button'
import './SearchBar.css'

export function SearchBar({ query, city, cities = [], onSubmit }) {
  const [draftQuery, setDraftQuery] = useState(query)
  const [draftCity, setDraftCity] = useState(city)

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ query: draftQuery.trim(), city: draftCity.trim() })
  }

  return (
    <form className="search-bar page-in" onSubmit={handleSubmit}>
      <div className="search-bar__field">
        <label htmlFor="search-query">Что нужно?</label>
        <input
          id="search-query"
          type="text"
          placeholder="Например: моцарелла для пиццы"
          value={draftQuery}
          onChange={(e) => setDraftQuery(e.target.value)}
        />
      </div>
      <div className="search-bar__field search-bar__field--city">
        <label htmlFor="search-city">Город доставки</label>
        <input
          id="search-city"
          type="text"
          list="city-suggestions"
          placeholder="Например: Екатеринбург"
          value={draftCity}
          onChange={(e) => setDraftCity(e.target.value)}
        />
        <datalist id="city-suggestions">
          {cities.map((c) => <option key={c} value={c} />)}
        </datalist>
      </div>
      <Button variant="cyan" type="submit">Найти</Button>
    </form>
  )
}
