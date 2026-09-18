import { projects } from '../data/content'
import { Reveal } from './Reveal'
import { useStagger } from '../hooks/useStagger'
import './Cases.css'

export function Cases() {
  const [ref, visible] = useStagger(0.08)

  return (
    <section className="section cases" id="match">
      <div className="container">
        <Reveal className="section-head">
          <h2>Проекты и задачи</h2>
          <p>Несколько примеров того, как я применял AI в рабочих системах. Последний кейс — прототип для этого задания.</p>
        </Reveal>
        <div className={`cases__grid ${visible ? 'is-visible' : ''}`} ref={ref}>
          {projects.map((project, i) => (
            <article className="case" key={project.number} style={{ transitionDelay: `${i * 70}ms` }}>
              <div className="case__top">
                <span className="case__number">{project.number}</span>
                <span className="case__area">{project.area}</span>
              </div>
              <h3>{project.title}</h3>
              <dl className="case__details">
                <div><dt>Задача</dt><dd>{project.problem}</dd></div>
                <div><dt>Что сделал</dt><dd>{project.work}</dd></div>
                <div><dt>Результат</dt><dd>{project.result}</dd></div>
              </dl>
              <div className="case__tags">
                {project.tags.map((tag) => <span key={tag}>{tag}</span>)}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
