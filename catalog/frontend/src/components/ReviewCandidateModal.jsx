import { useState } from 'react'
import { createPortal } from 'react-dom'
import { confirmCandidate } from '../api/suppliers'
import { Button } from './Button'
import { Spinner } from './Spinner'
import './ReviewCandidateModal.css'

const FIELDS = [
  ['name', 'Компания', 'text'],
  ['category', 'Категория', 'text'],
  ['region', 'Местонахождение', 'text'],
  ['product_lines', 'Что поставляет', 'text'],
  ['description', 'Описание', 'textarea'],
  ['moq', 'MOQ', 'text'],
  ['price_note', 'Цена', 'text'],
  ['certificates', 'Документы', 'text'],
  ['delivery_terms', 'Условия и география доставки', 'text'],
  ['contact_phone', 'Телефон', 'text'],
  ['contact_email', 'Почта', 'text'],
  ['website', 'Сайт', 'text'],
  ['notes', 'Заметки', 'textarea'],
]

export function ReviewCandidateModal({ candidate, onClose, onConfirmed }) {
  const [form, setForm] = useState(() => ({ ...candidate.preview }))
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')

  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('loading')
    setError('')
    try {
      const supplier = await confirmCandidate({ ...form, source_url: candidate.url })
      onConfirmed(supplier)
    } catch (err) {
      setError(err.message || 'Не получилось добавить')
      setStatus('idle')
    }
  }

  return createPortal(
    <div className="review-modal__overlay" onClick={onClose}>
      <div className="review-modal" onClick={(e) => e.stopPropagation()}>
        <div className="review-modal__head">
          <h2>Проверь карточку перед добавлением</h2>
          <p>
            Источник: <a href={candidate.url} target="_blank" rel="noreferrer">{candidate.domain}</a>.
            Ниже поля, заполненные автоматически по содержимому страницы. Поправь, если что-то не так,
            и оставь пустым, если фактов нет (покажем как «не опубликовано»).
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="review-modal__grid">
            {FIELDS.map(([key, label, type]) => (
              <label className="review-modal__field" key={key}>
                <span>{label}</span>
                {type === 'textarea' ? (
                  <textarea
                    rows={2}
                    value={form[key] || ''}
                    onChange={(e) => setField(key, e.target.value)}
                  />
                ) : (
                  <input
                    type="text"
                    value={form[key] || ''}
                    onChange={(e) => setField(key, e.target.value)}
                    placeholder="не опубликовано"
                  />
                )}
              </label>
            ))}
          </div>

          {error && <p className="review-modal__error">{error}</p>}

          <div className="review-modal__actions">
            <Button variant="outline" type="button" onClick={onClose}>Отмена</Button>
            <Button variant="cyan" type="submit" disabled={status === 'loading'}>
              {status === 'loading' ? <Spinner label="Добавляю..." /> : 'Добавить в каталог'}
            </Button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  )
}
