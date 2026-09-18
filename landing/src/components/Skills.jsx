import { skills } from '../data/content'
import { useStagger } from '../hooks/useStagger'
import { Reveal } from './Reveal'
import './Skills.css'

function PillRow({ items }) {
  const [ref, visible] = useStagger()
  return (
    <div className={`pillrow ${visible ? 'is-visible' : ''}`} ref={ref}>
      {items.map((item, i) => (
        <span className="pill" key={item} style={{ transitionDelay: `${i * 45}ms` }}>
          {item}
        </span>
      ))}
    </div>
  )
}

export function Skills() {
  return (
    <section className="section skills-section" id="skills">
      <span className="skills-section__glow" aria-hidden="true" />
      <div className="container">
        <Reveal className="section-head">
          <h2>Навыки</h2>
          <p>Технологии и инструменты, с которыми работаю.</p>
        </Reveal>
        <div className="skills">
          {skills.map((group) => (
            <div className="skill-group" key={group.group}>
              <h3>{group.group}</h3>
              <PillRow items={group.items} />
            </div>
          ))}
        </div>
        <Reveal className="skills-section__learning">
          <span>Дополнительно</span>
          <p>Знаю Go. Прошёл Ozon Golang Route уровня Middle.</p>
        </Reveal>
      </div>
    </section>
  )
}
