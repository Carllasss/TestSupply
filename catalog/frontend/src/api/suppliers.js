// Относительный путь по умолчанию: nginx фронтенда сам проксирует /api на
// бэкенд (см. nginx.conf), так что это работает и при прямом заходе на
// контейнер фронтенда, и через общий reverse-proxy. Для локальной разработки
// через `npm run dev` (без nginx) можно задать VITE_API_URL=http://localhost:8000.
const BASE_URL = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Ошибка запроса: ${response.status}`)
  }

  return response.json()
}

export function fetchSuppliers({ category, region, q, hasPrice, hasMoq } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (region) params.set('region', region)
  if (q) params.set('q', q)
  if (hasPrice) params.set('has_price', 'true')
  if (hasMoq) params.set('has_moq', 'true')
  const qs = params.toString()
  return request(`/api/suppliers${qs ? `?${qs}` : ''}`)
}

export function fetchSupplier(id) {
  return request(`/api/suppliers/${id}`)
}

export function fetchFacets() {
  return request('/api/suppliers/facets')
}

export function webSearch({ category, region, q } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (region) params.set('region', region)
  if (q) params.set('q', q)
  const qs = params.toString()
  return request(`/api/suppliers/web-search${qs ? `?${qs}` : ''}`)
}

export function scrapeSupplier(url) {
  return request('/api/suppliers/scrape', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}

export function extractSupplier(text) {
  return request('/api/suppliers/extract', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export function discoverSuppliers(query) {
  return request('/api/suppliers/discover', {
    method: 'POST',
    body: JSON.stringify({ query }),
  })
}

export function createSupplier(data) {
  return request('/api/suppliers', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function confirmCandidate(data) {
  return request('/api/suppliers/confirm', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function compareSuppliers(ids, query) {
  return request('/api/suppliers/compare', {
    method: 'POST',
    body: JSON.stringify({ ids, query }),
  })
}
