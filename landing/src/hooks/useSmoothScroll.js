import { useEffect } from 'react'
import Lenis from 'lenis'

export function useSmoothScroll() {
  useEffect(() => {
    // Some in-app browsers (Telegram, etc.) restore/adjust scroll position
    // asynchronously after the initial paint, which can leave the page (and
    // the sticky header) offset from the top even though we scrolled to 0
    // on mount. Re-assert it once more after layout settles.
    const resetScroll = () => {
      if (window.scrollY > 0 && !window.location.hash) window.scrollTo(0, 0)
    }
    const timer = setTimeout(resetScroll, 150)
    window.addEventListener('pageshow', resetScroll)

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduceMotion) return () => {
      clearTimeout(timer)
      window.removeEventListener('pageshow', resetScroll)
    }

    const lenis = new Lenis({
      duration: 1.1,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      syncTouch: false,
    })

    let raf
    const loop = (time) => {
      lenis.raf(time)
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)

    const onClick = (e) => {
      const anchor = e.target.closest('a[href^="#"]')
      if (!anchor) return
      const id = anchor.getAttribute('href').slice(1)
      const target = id && document.getElementById(id)
      if (!target) return
      e.preventDefault()
      lenis.scrollTo(target, { offset: -56 })
    }
    document.addEventListener('click', onClick)

    return () => {
      clearTimeout(timer)
      window.removeEventListener('pageshow', resetScroll)
      document.removeEventListener('click', onClick)
      cancelAnimationFrame(raf)
      lenis.destroy()
    }
  }, [])
}
