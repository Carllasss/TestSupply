import { contact } from '../data/content'
import './Footer.css'

export function Footer() {
  return (
    <footer>
      <div className="container">
        <div className="footer-list">
          <div className="footer-row"><span>Email</span><a href={`mailto:${contact.email}`}>{contact.email}</a></div>
          <div className="footer-row"><span>Город</span><span>{contact.city}</span></div>
          <div className="footer-row"><span>GitHub</span><a href={contact.github} target="_blank" rel="noreferrer">github.com/ivanovns</a></div>
          <div className="footer-row"><span>Часть 2</span><span>{contact.part2}</span></div>
        </div>
        <span className="foot-note">Иванов Никита · 2026</span>
      </div>
    </footer>
  )
}
