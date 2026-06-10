import type { Product } from '../types'

interface Props {
  product: Product
  onAdd: (product: Product) => void
}

export default function ProductCard({ product, onAdd }: Props) {
  const unavailable = product.status === 'out_of_stock'
  return (
    <button
      onClick={() => !unavailable && onAdd(product)}
      disabled={unavailable}
      className={`bg-white rounded-xl p-3 text-left shadow-sm border-2 transition-all ${
        unavailable
          ? 'opacity-50 cursor-not-allowed border-transparent'
          : 'border-transparent hover:border-blue-400 hover:shadow-md active:scale-95'
      }`}
    >
      {product.image ? (
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-24 object-cover rounded-lg mb-2"
        />
      ) : (
        <div className="w-full h-24 bg-gray-100 rounded-lg mb-2 flex items-center justify-center text-3xl">
          🍽
        </div>
      )}
      <p className="text-sm font-semibold text-gray-800 truncate">{product.name}</p>
      <p className="text-blue-600 font-bold mt-1">{parseFloat(product.price).toFixed(0)} ₽</p>
      {product.status === 'out_of_stock' && (
        <p className="text-red-400 text-xs mt-0.5">Нет в наличии</p>
      )}
    </button>
  )
}
