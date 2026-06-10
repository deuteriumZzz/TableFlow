import { usePosStore } from '../store/posStore'
import OrderItemRow from './OrderItemRow'
import StatusBadge from './StatusBadge'

interface Props {
  onPay: () => void
  onClose: () => void
}

export default function OrderPanel({ onPay, onClose }: Props) {
  const { selectedTable, currentOrder, removeItem } = usePosStore()

  const total = currentOrder
    ? parseFloat(currentOrder.total_amount).toFixed(0)
    : '0'

  const canPay =
    currentOrder &&
    currentOrder.items.length > 0 &&
    currentOrder.payment_status === 'pending'

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="px-4 py-3 bg-gray-800 text-white flex items-center justify-between">
        <div>
          <p className="font-bold">
            {selectedTable ? `Стол #${selectedTable.number}` : 'Без стола'}
          </p>
          {currentOrder && (
            <p className="text-xs text-gray-300">Заказ #{currentOrder.id}</p>
          )}
        </div>
        {currentOrder && <StatusBadge status={currentOrder.status} />}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-2">
        {!currentOrder || currentOrder.items.length === 0 ? (
          <p className="text-center text-gray-400 py-8 text-sm">
            Добавьте позиции из меню
          </p>
        ) : (
          currentOrder.items.map((item) => (
            <OrderItemRow
              key={item.id}
              item={item}
              onRemove={(id) => removeItem(id)}
            />
          ))
        )}
      </div>

      <div className="px-4 py-4 border-t border-gray-200 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-600 font-medium">Итого</span>
          <span className="text-2xl font-bold text-gray-800">{total} ₽</span>
        </div>
        <button
          onClick={onPay}
          disabled={!canPay}
          className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-lg"
        >
          Оплатить
        </button>
        <button
          onClick={onClose}
          className="w-full text-gray-500 hover:text-gray-700 text-sm py-1"
        >
          ← Вернуться к столам
        </button>
      </div>
    </div>
  )
}
