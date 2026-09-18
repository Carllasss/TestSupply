import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Header } from './components/Header'
import { CatalogPage } from './pages/CatalogPage'
import { SupplierPage } from './pages/SupplierPage'
import { AddSupplierPage } from './pages/AddSupplierPage'
import { ComparePage } from './pages/ComparePage'

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/suppliers/:id" element={<SupplierPage />} />
        <Route path="/add" element={<AddSupplierPage />} />
        <Route path="/compare" element={<ComparePage />} />
      </Routes>
    </BrowserRouter>
  )
}
