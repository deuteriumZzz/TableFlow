import type { OrderItem } from '../types'

interface Props {
  item: OrderItem
  onRemove: (itemId: number) => void
}

export default function OrderItemRow({ item, onRemove }: Props) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate">{item.product.name}</p>
        {item.comment && <p className="text-xs text-gray-400">{item.comment}</p>}
        <p className="text-xs text-gray-500">×{item.quantity}</p>
      </div>
      <p className="text-sm font-semibold text-gray-800 whitespace-nowrap">
        {parseFloat(item.total_price).toFixed(0)} ₽
      </p>
      <button
        onClick={() => onRemove(item.id)}
        className="text-red-400 hover:text-red-600 text-lg leading-none ml-1"
        title="Удалить"
      >
        ×
      </button>
    </div>
  )
}
