import { useEffect, useRef, useState } from 'react'

// Smooths out bursty SSE text chunks into a steady character-by-character
// reveal instead of the text jumping forward in uneven jumps.
export function useTypewriter() {
  const [display, setDisplay] = useState('')
  const fullRef = useRef('')
  const timerRef = useRef(null)

  const stop = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const push = (chunk) => {
    fullRef.current += chunk
    if (!timerRef.current) {
      timerRef.current = setInterval(() => {
        setDisplay((prev) => {
          const full = fullRef.current
          if (prev.length >= full.length) {
            stop()
            return prev
          }
          const remaining = full.length - prev.length
          const step = Math.max(1, Math.ceil(remaining / 12))
          return full.slice(0, prev.length + step)
        })
      }, 16)
    }
  }

  const reset = () => {
    stop()
    fullRef.current = ''
    setDisplay('')
  }

  useEffect(() => stop, [])

  return [display, push, reset]
}
