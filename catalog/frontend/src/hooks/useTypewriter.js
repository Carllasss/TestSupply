import { useEffect, useRef, useState } from 'react'

// Smooths bursty SSE chunks and continues revealing any remaining text after
// the final event arrives.
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

  const start = () => {
    if (timerRef.current) return
    timerRef.current = setInterval(() => {
      setDisplay((prev) => {
        const full = fullRef.current
        if (prev.length >= full.length) {
          stop()
          return prev
        }
        const remaining = full.length - prev.length
        const step = Math.max(1, Math.ceil(remaining / 18))
        return full.slice(0, prev.length + step)
      })
    }, 22)
  }

  const push = (chunk) => {
    fullRef.current += chunk
    start()
  }

  const reset = () => {
    stop()
    fullRef.current = ''
    setDisplay('')
  }

  const finish = (finalText) => {
    if (!finalText) {
      reset()
      return
    }
    if (!finalText.startsWith(fullRef.current)) setDisplay('')
    fullRef.current = finalText
    start()
  }

  useEffect(() => stop, [])

  return [display, push, reset, finish]
}
