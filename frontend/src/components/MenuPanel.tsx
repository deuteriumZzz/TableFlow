import { useEffect } from 'react'
import { usePosStore } from '../store/posStore'
import { getCategories, getProducts } from '../api/menu'
import CategoryTabs from './CategoryTabs'
import ProductCard from './ProductCard'
import type { Product } from '../types'

interface Props {
  onAddProduct: (product: Product) => void
}

export default function MenuPanel({ onAddProduct }: Props) {
  const { categories, products, selectedCategoryId, setCategories, setProducts, selectCategory } =
    usePosStore()

  useEffect(() => {
    getCategories().then(setCategories)
  }, [setCategories])

  useEffect(() => {
    getProducts(selectedCategoryId ?? undefined).then(setProducts)
  }, [selectedCategoryId, setProducts])

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <CategoryTabs
        categories={categories}
        selected={selectedCategoryId}
        onSelect={selectCategory}
      />
      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-3 gap-3 pb-4">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} onAdd={onAddProduct} />
          ))}
          {products.length === 0 && (
            <p className="col-span-3 text-center text-gray-400 py-8">Нет товаров</p>
          )}
        </div>
      </div>
    </div>
  )
}
