import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// In-app browsers (Telegram, Instagram, etc.) sometimes restore a stale
// scroll position on load, which makes the sticky header appear offset from
// the top. Force a clean scroll-to-top instead of relying on the browser.
if ('scrollRestoration' in history) history.scrollRestoration = 'manual'
window.scrollTo(0, 0)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
