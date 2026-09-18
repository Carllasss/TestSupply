import { Button } from './Button'
import './Hero.css'

export function Hero() {
  return (
    <section className="hero">
      <span className="hero__glow" aria-hidden="true" />
      <div className="container">
        <p className="hero__eyebrow hero-in">Иванов Никита · Python backend-разработчик · AI</p>
        <h1 className="hero-in" style={{ animationDelay: '90ms' }}>
          От идеи до <span className="accent">работающего сервиса</span>
        </h1>
        <p className="hero__lead hero-in" style={{ animationDelay: '180ms' }}>
          Разрабатываю API и интеграции на Python, работаю с данными и внутренними системами.
          Использую AI, когда он приносит пользу проекту.
        </p>
        <div className="hero__actions hero-in" style={{ animationDelay: '270ms' }}>
          <Button href="#match" variant="cyan" arrow>Смотреть проекты</Button>
        </div>
      </div>
    </section>
  )
}
