import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchSuppliers, fetchFacets, fetchSupplier, webSearchStream } from '../api/suppliers'
import { Filters } from '../components/Filters'
import { SearchBar } from '../components/SearchBar'
import { SupplierCard } from '../components/SupplierCard'
import { WebSupplierCard } from '../components/WebSupplierCard'
import { CompareBar } from '../components/CompareBar'
import { Button } from '../components/Button'
import { sortBySupplierField } from '../utils/parseNumber'
import { useStagger } from '../hooks/useStagger'
import { useTypewriter } from '../hooks/useTypewriter'
import { Spinner } from '../components/Spinner'
import { SearchTicker } from '../components/SearchTicker'
import './CatalogPage.css'

const PAGE_SIZE = 12
const CATALOG_STATE_KEY = 'catalog-search-state-v1'

function readCatalogState() {
  try {
    return JSON.parse(sessionStorage.getItem(CATALOG_STATE_KEY)) || {}
  } catch {
    return {}
  }
}

export function CatalogPage() {
  const navigate = useNavigate()
  const [saved] = useState(readCatalogState)
  const skipInitialSearch = useRef(saved.status === 'ready')
  const [suppliers, setSuppliers] = useState(saved.suppliers || [])
  const [webResults, setWebResults] = useState(saved.webResults || [])
  const [recommendation, setRecommendation] = useState(saved.recommendation ?? null)
  const [recommendedSupplierId, setRecommendedSupplierId] = useState(saved.recommendedSupplierId ?? null)
  const [recommendedCandidateUrl, setRecommendedCandidateUrl] = useState(saved.recommendedCandidateUrl ?? null)
  const [featuredSupplier, setFeaturedSupplier] = useState(saved.featuredSupplier ?? null)
  const [facets, setFacets] = useState({ categories: [], regions: [] })
  const [category, setCategory] = useState(saved.category || '')
  const [query, setQuery] = useState(saved.query || '')
  const [city, setCity] = useState(saved.city || '')
  const [sort, setSort] = useState(saved.sort || '')
  const [hasPrice, setHasPrice] = useState(Boolean(saved.hasPrice))
  const [hasMoq, setHasMoq] = useState(Boolean(saved.hasMoq))
  const [status, setStatus] = useState(saved.status === 'ready' ? 'ready' : 'loading')
  const [webStatus, setWebStatus] = useState(saved.webStatus === 'ready' ? 'ready' : 'idle')
  const [added, setAdded] = useState(saved.added || {})
  const [selectedIds, setSelectedIds] = useState(saved.selectedIds || [])
  const [visibleCount, setVisibleCount] = useState(saved.visibleCount || PAGE_SIZE)
  const [searchLog, setSearchLog] = useState([])
  const [isRecommending, setIsRecommending] = useState(false)
  const [streamingRecommendation, pushStreamingChunk, resetStreamingRecommendation, finishStreamingRecommendation] = useTypewriter()
  const requestId = useRef(0)
  const webRequestId = useRef(0)
  const stopStream = useRef(null)
  const [filtersOpen, setFiltersOpen] = useState(() => window.innerWidth > 860)

  const runCatalogSearch = (q, region, price, moq, nextCategory = category) => {
    const currentRequest = ++requestId.current
    setVisibleCount(PAGE_SIZE)
    setStatus('loading')
    fetchSuppliers({ category: nextCategory, region, q, hasPrice: price, hasMoq: moq })
      .then((data) => {
        if (currentRequest !== requestId.current) return
        setSuppliers(data)
        setStatus('ready')
      })
      .catch(() => {
        if (currentRequest === requestId.current) {
          setSuppliers([])
          setStatus('error')
        }
      })
  }

  useEffect(() => {
    fetchFacets().then(setFacets).catch(() => {})
  }, [])

  useEffect(() => () => stopStream.current?.(), [])

  useEffect(() => {
    if (skipInitialSearch.current) {
      skipInitialSearch.current = false
      return
    }
    runCatalogSearch(query, city, hasPrice, hasMoq)
  }, [category, hasPrice, hasMoq])

  useEffect(() => {
    try {
      sessionStorage.setItem(CATALOG_STATE_KEY, JSON.stringify({
        suppliers, webResults, recommendation, recommendedSupplierId, recommendedCandidateUrl,
        featuredSupplier, category, query, city, sort, hasPrice, hasMoq, status, webStatus,
        added, selectedIds, visibleCount,
      }))
    } catch {
      // The catalog still works if browser storage is unavailable.
    }
  }, [suppliers, webResults, recommendation, recommendedSupplierId, recommendedCandidateUrl,
    featuredSupplier, category, query, city, sort, hasPrice, hasMoq, status, webStatus,
    added, selectedIds, visibleCount])

  const clearWebSearch = () => {
    webRequestId.current += 1
    stopStream.current?.()
    setWebResults([])
    setRecommendation(null)
    setRecommendedSupplierId(null)
    setRecommendedCandidateUrl(null)
    setFeaturedSupplier(null)
    setWebStatus('idle')
    setSearchLog([])
    setIsRecommending(false)
    resetStreamingRecommendation()
  }

  const handleSearchSubmit = ({ query: newQuery, city: newCity }) => {
    setQuery(newQuery)
    setCity(newCity)
    clearWebSearch()
    runCatalogSearch(newQuery, newCity, hasPrice, hasMoq)
  }

  const describeEvent = (event) => {
    switch (event.type) {
      case 'searching': return `Ищем «${event.query}» в интернете…`
      case 'found': return `Нашли сайт: ${event.domain}`
      case 'checked': return event.ok ? `Посмотрели ${event.domain} — данные собрали` : `Посмотрели ${event.domain} — не разобрали страницу`
      case 'recommending': return 'Собираю рекомендацию…'
      default: return null
    }
  }

  const handleWebSearch = () => {
    const currentRequest = ++webRequestId.current
    stopStream.current?.()
    setWebStatus('loading')
    setWebResults([])
    setRecommendation(null)
    setRecommendedSupplierId(null)
    setRecommendedCandidateUrl(null)
    setFeaturedSupplier(null)
    setSearchLog([])
    setIsRecommending(false)
    resetStreamingRecommendation()

    stopStream.current = webSearchStream({ category, region: city, q: query }, {
      onEvent: (event) => {
        if (currentRequest !== webRequestId.current) return
        if (event.type === 'chunk') {
          pushStreamingChunk(event.text)
          return
        }
        if (event.type === 'recommending') setIsRecommending(true)
        const line = describeEvent(event)
        if (line) setSearchLog((prev) => [...prev, line])
      },
      onDone: (data) => {
        if (currentRequest !== webRequestId.current) return
        finishStreamingRecommendation(data.recommendation)
        setWebResults(data.web.filter((c) => !c.already_in_catalog && c.preview))
        setRecommendation(data.recommendation)
        setRecommendedSupplierId(data.recommended_supplier_id ?? null)
        setRecommendedCandidateUrl(data.recommended_candidate_url ?? null)
        setWebStatus('ready')
        if (data.recommended_supplier_id != null) {
          fetchSupplier(data.recommended_supplier_id)
            .then((supplier) => {
              if (currentRequest === webRequestId.current) setFeaturedSupplier(supplier)
            })
            .catch(() => {})
        }
      },
      onError: () => {
        if (currentRequest === webRequestId.current) {
          resetStreamingRecommendation()
          setWebStatus('error')
        }
      },
    })
  }

  const resetFilters = () => {
    clearWebSearch()
    setCategory('')
    setSort('')
    setHasPrice(false)
    setHasMoq(false)
  }

  const toggleSelect = (id) => {
    setSelectedIds((prev) => (
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length >= 4 ? prev : [...prev, id]
    ))
  }

  const goToCompare = () => {
    const params = new URLSearchParams({ ids: selectedIds.join(',') })
    if (query) params.set('q', query)
    navigate(`/compare?${params.toString()}`)
  }

  const emptyMessage = useMemo(() => {
    if (category || city || query || hasPrice || hasMoq) return 'По этому запросу в каталоге пока ничего нет.'
    return 'В базе пока нет поставщиков.'
  }, [category, city, query, hasPrice, hasMoq])

  const sortedsuppliers = useMemo(() => {
    const ordered = sortBySupplierField(suppliers, sort, (s, key) => s[key])
    if (recommendedSupplierId == null) return ordered
    const winner = ordered.find((s) => s.id === recommendedSupplierId)
    return winner ? [winner, ...ordered.filter((s) => s.id !== recommendedSupplierId)] : ordered
  }, [suppliers, sort, recommendedSupplierId])
  const sortedWebResults = useMemo(
    () => sortBySupplierField(webResults, sort, (c, key) => c.preview?.[key]),
    [webResults, sort]
  )
  const featuredCatalogSupplier = recommendedSupplierId != null &&
    !suppliers.some((s) => s.id === recommendedSupplierId) &&
    featuredSupplier?.id === recommendedSupplierId ? featuredSupplier : null
  const featuredWebCandidate = recommendedCandidateUrl
    ? sortedWebResults.find((c) => c.url === recommendedCandidateUrl) : null
  const otherWebResults = featuredWebCandidate
    ? sortedWebResults.filter((c) => c.url !== recommendedCandidateUrl) : sortedWebResults

  const [gridRef, gridVisible] = useStagger(0.05)
  const [webGridRef, webGridVisible] = useStagger(0.05)

  return (
    <div className="catalog">
      <div className="container">
        <div className="catalog__head page-in">
          <div>
            <h1>Поставщики продуктов питания</h1>
            <p>Напиши, что нужно, и куда доставить. Покажем совпадения из каталога.</p>
          </div>
          <Button as={Link} to="/add" variant="ink" arrow>Добавить поставщика</Button>
        </div>

        <SearchBar query={query} city={city} cities={facets.regions} onSubmit={handleSearchSubmit} />

        <div className="catalog__layout">
          <div className="page-in catalog__filters-col" style={{ animationDelay: '80ms' }}>
            <button
              type="button"
              className="catalog__filters-toggle"
              onClick={() => setFiltersOpen((open) => !open)}
              aria-expanded={filtersOpen}
            >
              Фильтры
              <span className={`catalog__filters-toggle-icon ${filtersOpen ? 'is-open' : ''}`} aria-hidden="true" />
            </button>
            <div className={`catalog__filters-panel ${filtersOpen ? 'is-open' : ''}`}>
              <Filters
                facets={facets}
                category={category}
                sort={sort}
                hasPrice={hasPrice}
                hasMoq={hasMoq}
                onCategory={(value) => { clearWebSearch(); setCategory(value) }}
                onSort={setSort}
                onHasPrice={(value) => { clearWebSearch(); setHasPrice(value) }}
                onHasMoq={(value) => { clearWebSearch(); setHasMoq(value) }}
                onReset={resetFilters}
              />
            </div>
          </div>

          <div className="catalog__results">
            {status === 'error' && (
              <p className="catalog__error">Не получилось загрузить каталог. Проверь, что бэкенд запущен.</p>
            )}

            <div className="catalog__results-head">
              <p className="catalog__count">
                {status === 'loading' ? <Spinner label="Ищем..." /> : status === 'error' ? 'Каталог недоступен' : `Найдено в каталоге: ${sortedsuppliers.length}`}
              </p>
              {webStatus !== 'loading' && (
                <Button variant="outline" type="button" onClick={handleWebSearch}>
                  {webStatus === 'error' ? 'Повторить поиск в интернете' : webStatus === 'ready' ? 'Обновить поиск в интернете' : 'Найти ещё в интернете'}
                </Button>
              )}
            </div>

            {webStatus === 'loading' && <SearchTicker lines={searchLog} />}

            {(recommendation || (webStatus === 'loading' && isRecommending)) && (
              <div className={`catalog__recommendation ${webStatus === 'loading' ? 'catalog__recommendation--streaming' : ''} card-in`}>
                <span className="catalog__recommendation-label">
                  {webStatus === 'loading' ? 'Ответ ИИ · формируется' : 'Рекомендация по запросу'}
                </span>
                <p aria-live="polite">
                  {streamingRecommendation || recommendation || 'Анализирую найденных поставщиков…'}
                  {webStatus === 'loading' && <span className="catalog__recommendation-cursor" aria-hidden="true" />}
                </p>
              </div>
            )}

            {status === 'ready' && sortedsuppliers.length === 0 && (
              <p className="catalog__empty">{emptyMessage}</p>
            )}

            {featuredCatalogSupplier && (
              <div className="catalog__featured">
                <SupplierCard
                  supplier={featuredCatalogSupplier}
                  recommended
                  selected={selectedIds.includes(featuredCatalogSupplier.id)}
                  atLimit={selectedIds.length >= 4}
                  onToggleSelect={toggleSelect}
                />
              </div>
            )}

            {featuredWebCandidate && (
              <div className="catalog__featured">
                <WebSupplierCard
                  candidate={featuredWebCandidate}
                  recommended
                  addedSupplier={added[featuredWebCandidate.url]}
                  onAdded={(url, supplier) => setAdded((prev) => ({ ...prev, [url]: supplier }))}
                />
              </div>
            )}

            <div
              ref={gridRef}
              className={`catalog__grid ${status === 'loading' ? 'is-loading' : ''} ${gridVisible ? 'is-visible' : ''}`}
            >
              {sortedsuppliers.slice(0, visibleCount).map((s, i) => (
                <SupplierCard
                  key={s.id}
                  supplier={s}
                  delay={Math.min(i, 10) * 60}
                  selected={selectedIds.includes(s.id)}
                  atLimit={selectedIds.length >= 4}
                  recommended={s.id === recommendedSupplierId}
                  onToggleSelect={toggleSelect}
                />
              ))}
            </div>

            {status === 'ready' && sortedsuppliers.length > visibleCount && (
              <div className="catalog__more">
                <Button variant="outline" type="button" onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}>
                  Показать ещё {Math.min(PAGE_SIZE, sortedsuppliers.length - visibleCount)}
                </Button>
                <span>Показано {visibleCount} из {sortedsuppliers.length}</span>
              </div>
            )}

            {webStatus === 'error' && (
              <p className="catalog__error">Не получилось поискать в интернете, попробуй ещё раз.</p>
            )}

            {webStatus === 'ready' && sortedWebResults.length === 0 && (
              <p className="catalog__empty">В интернете похожих поставщиков не нашлось.</p>
            )}

            {otherWebResults.length > 0 && (
              <>
                <h2 className="catalog__section-title">Нашли в интернете, не в каталоге</h2>
                <div ref={webGridRef} className={`catalog__grid ${webGridVisible ? 'is-visible' : ''}`}>
                  {otherWebResults.map((c, i) => (
                    <WebSupplierCard
                      key={c.url}
                      candidate={c}
                      delay={Math.min(i, 10) * 60}
                      addedSupplier={added[c.url]}
                      onAdded={(url, supplier) => setAdded((prev) => ({ ...prev, [url]: supplier }))}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <CompareBar count={selectedIds.length} onCompare={goToCompare} onClear={() => setSelectedIds([])} />
    </div>
  )
}
