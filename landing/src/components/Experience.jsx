import { experience } from '../data/content'
import { Reveal } from './Reveal'
import { useStagger } from '../hooks/useStagger'
import './Experience.css'

export function Experience() {
  const [ref, visible] = useStagger(0.15)

  return (
    <section className="section section--soft" id="experience">
      <div className="container">
        <Reveal className="section-head">
          <h2>Опыт работы</h2>
          <p>Опыт разработки: backend, интеграции и AI-сервисы.</p>
        </Reveal>
        <div className={`tl ${visible ? 'is-visible' : ''}`} ref={ref}>
          {experience.map((job, i) => (
            <div
              className={`tl-item ${job.current ? 'current' : ''}`}
              key={job.company}
              style={{
                transitionDelay: `${i * 90}ms`,
                ...(i === experience.length - 1 ? { borderBottom: 'none' } : {}),
              }}
            >
              <div className="tl-head">
                <h3>{job.company}</h3>
                <span className="tl-date">{job.date}</span>
              </div>
              <div className="tl-role">{job.role}</div>
              <div className="tl-body">
                <ul>
                  {job.bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
