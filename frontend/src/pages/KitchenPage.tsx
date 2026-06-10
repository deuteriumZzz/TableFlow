import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getOrders, updateOrderStatus } from '../api/orders'
import type { Order, OrderStatus } from '../types'

const KITCHEN_STATUSES: OrderStatus[] = ['created', 'in_progress', 'ready']

const COLUMN_TITLE: Record<string, string> = {
  created: 'Новые',
  in_progress: 'Готовятся',
  ready: 'Готовы к выдаче',
}

const COLUMN_COLOR: Record<string, string> = {
  created: 'bg-blue-50 border-blue-200',
  in_progress: 'bg-orange-50 border-orange-200',
  ready: 'bg-green-50 border-green-200',
}

const BUTTON_COLOR: Record<string, string> = {
  created: 'bg-orange-500 hover:bg-orange-600',
  in_progress: 'bg-green-600 hover:bg-green-700',
  ready: 'bg-gray-600 hover:bg-gray-700',
}

const BUTTON_LABEL: Record<string, string> = {
  created: 'В работу',
  in_progress: 'Готово',
  ready: 'Выдано',
}

const NEXT_STATUS: Record<string, OrderStatus> = {
  created: 'in_progress',
  in_progress: 'ready',
  ready: 'delivered',
}

export default function KitchenPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const load = async () => {
    try {
      const results = await Promise.all(KITCHEN_STATUSES.map((s) => getOrders(s)))
      setOrders(results.flat())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 15000)
    return () => clearInterval(interval)
  }, [])

  const advance = async (order: Order) => {
    const next = NEXT_STATUS[order.status]
    if (!next) return
    await updateOrderStatus(order.id, next)
    load()
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="px-6 py-4 bg-gray-800 flex items-center justify-between">
        <h1 className="text-xl font-bold">Кухня — TableFlow</h1>
        <div className="flex gap-4">
          <button onClick={load} className="text-sm text-gray-400 hover:text-white">
            Обновить
          </button>
          <button
            onClick={() => navigate('/')}
            className="text-sm text-gray-400 hover:text-white"
          >
            ← Назад
          </button>
        </div>
      </header>

      {loading ? (
        <p className="text-center text-gray-400 py-12">Загрузка...</p>
      ) : (
        <div className="grid grid-cols-3 gap-4 p-4">
          {KITCHEN_STATUSES.map((col) => {
            const colOrders = orders.filter((o) => o.status === col)
            return (
              <div key={col}>
                <h2 className="text-lg font-semibold mb-3 text-gray-300">
                  {COLUMN_TITLE[col]}
                  <span className="ml-2 bg-gray-700 text-white text-xs px-2 py-0.5 rounded-full">
                    {colOrders.length}
                  </span>
                </h2>
                <div className="space-y-3">
                  {colOrders.length === 0 && (
                    <p className="text-gray-500 text-sm text-center py-4">Пусто</p>
                  )}
                  {colOrders.map((order) => (
                    <div
                      key={order.id}
                      className={`rounded-xl border p-4 ${COLUMN_COLOR[col]}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-gray-800">
                          {order.table_number
                            ? `Стол #${order.table_number}`
                            : 'Без стола'}
                        </span>
                        <span className="text-xs text-gray-500">#{order.id}</span>
                      </div>
                      <ul className="space-y-1 mb-3">
                        {order.items.map((item) => (
                          <li
                            key={item.id}
                            className="text-sm text-gray-700 flex justify-between"
                          >
                            <span>{item.product.name}</span>
                            <span className="font-medium">×{item.quantity}</span>
                          </li>
                        ))}
                      </ul>
                      {order.comment && (
                        <p className="text-xs text-gray-500 italic mb-2">
                          {order.comment}
                        </p>
                      )}
                      <button
                        onClick={() => advance(order)}
                        className={`w-full text-white text-sm font-medium py-2 rounded-lg transition-colors ${BUTTON_COLOR[col]}`}
                      >
                        {BUTTON_LABEL[col]}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
