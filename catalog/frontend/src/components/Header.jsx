import { NavLink } from 'react-router-dom'
import './Header.css'

export function Header() {
  return (
    <header className="site-header">
      <div className="container">
        <NavLink to="/" className="site-header__brand">
          <span className="site-header__mark" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
          </span>
          <span className="site-header__name">Каталог поставщиков</span>
        </NavLink>
        <nav className="site-header__nav">
          <NavLink to="/" end>Каталог</NavLink>
          <NavLink to="/add">Добавить поставщика</NavLink>
        </nav>
      </div>
    </header>
  )
}
