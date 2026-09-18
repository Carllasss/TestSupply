import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { Stats } from './components/Stats'
import { Cases } from './components/Cases'
import { Experience } from './components/Experience'
import { Skills } from './components/Skills'
import { Footer } from './components/Footer'
import { useSmoothScroll } from './hooks/useSmoothScroll'

const NAME = 'Иванов Никита'

export default function App() {
  useSmoothScroll()

  return (
    <div id="top">
      <Header name={NAME} />
      <Hero />
      <Stats />
      <Cases />
      <Experience />
      <Skills />
      <Footer />
    </div>
  )
}
