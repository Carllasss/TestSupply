import { Button } from './Button'
import './CompareBar.css'

export function CompareBar({ count, onCompare, onClear }) {
  if (count === 0) return null

  return (
    <div className="compare-bar">
      <span>Выбрано для сравнения: {count}</span>
      <div className="compare-bar__actions">
        <button className="compare-bar__clear" type="button" onClick={onClear}>Очистить</button>
        <Button variant="cyan" type="button" disabled={count < 2} onClick={onCompare}>Перейти к сравнению</Button>
      </div>
    </div>
  )
}
