import { useCallback, useEffect, useState } from 'react'

export function useStagger(threshold = 0.1) {
  const [node, setNode] = useState(null)
  const [visible, setVisible] = useState(false)

  const ref = useCallback((el) => setNode(el), [])

  useEffect(() => {
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
  }, [node, threshold])

  return [ref, visible]
}
