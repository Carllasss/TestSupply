export function leadingNumber(text) {
  if (!text) return null
  const match = text.replace(/\s/g, ' ').match(/(\d[\d\s]*(?:[.,]\d+)?)/)
  if (!match) return null
  const value = parseFloat(match[1].replace(/\s/g, '').replace(',', '.'))
  return Number.isNaN(value) ? null : value
}

export function sortBySupplierField(items, sort, getField) {
  if (!sort) return items
  const key = sort === 'price_asc' ? 'price_note' : 'moq'
  const withValue = items.map((item) => ({ item, value: leadingNumber(getField(item, key)) }))
  withValue.sort((a, b) => {
    if (a.value === null && b.value === null) return 0
    if (a.value === null) return 1
    if (b.value === null) return -1
    return a.value - b.value
  })
  return withValue.map((w) => w.item)
}
