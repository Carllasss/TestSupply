import { useStagger } from '../hooks/useStagger'
import { stats, statsIntro } from '../data/content'
import { StatIcon } from './StatIcon'
import './Stats.css'

export function Stats() {
  const [ref, visible] = useStagger()

  return (
    <section className="stats" id="numbers">
      <div className="container">
        <p className="stats__head">Коротко о профиле</p>
        <p className="stats__intro">{statsIntro}</p>
        <div className="stats__grid" ref={ref}>
          {stats.map((item, i) => (
            <div
              key={item.label}
              className={`stat-card ${visible ? 'is-visible' : ''}`}
              style={{ transitionDelay: `${i * 60}ms` }}
            >
              <StatIcon name={item.icon} />
              <b>{item.value}</b>
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
