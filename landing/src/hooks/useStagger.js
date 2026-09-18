import { useEffect, useRef, useState } from 'react'

export function useStagger(threshold = 0.3) {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    if (!('IntersectionObserver' in window)) {
      setVisible(true)
      return
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true)
            io.unobserve(entry.target)
          }
        })
      },
      { threshold }
    )
    io.observe(node)
    return () => io.disconnect()
  }, [threshold])

  return [ref, visible]
}
