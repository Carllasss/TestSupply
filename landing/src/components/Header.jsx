import { useEffect, useState } from 'react'
import './Header.css'

export function Header({ name }) {
  const [stuck, setStuck] = useState(false)

  useEffect(() => {
    const onScroll = () => setStuck(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className={`site-header ${stuck ? 'is-stuck' : ''}`}>
      <div className="container">
        <a className="site-header__brand" href="#top">
          <span className="site-header__mark" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
          </span>
          <span className="site-header__name">{name}</span>
        </a>
        <nav className="site-header__nav">
          <a href="#match"><span>Проекты</span></a>
          <a href="#experience"><span>Работа</span></a>
          <a href="#skills"><span>Навыки</span></a>
        </nav>
      </div>
    </header>
  )
}
