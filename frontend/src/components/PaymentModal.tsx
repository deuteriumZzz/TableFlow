import { useEffect, useState } from 'react'
import { getPaymentMethods, createPayment } from '../api/payments'
import type { Order, PaymentMethod } from '../types'

interface Props {
  order: Order
  onClose: () => void
  onSuccess: () => void
}

export default function PaymentModal({ order, onClose, onSuccess }: Props) {
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [selectedMethod, setSelectedMethod] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getPaymentMethods().then((m) => {
      setMethods(m)
      if (m.length > 0) setSelectedMethod(m[0].id)
    })
  }, [])

  const handlePay = async () => {
    if (!selectedMethod) return
    setLoading(true)
    setError(null)
    try {
      await createPayment(order.id, selectedMethod)
      onSuccess()
    } catch {
      setError('Ошибка при проведении оплаты')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm mx-4">
        <h2 className="text-xl font-bold text-gray-800 mb-1">Оплата заказа</h2>
        <p className="text-gray-500 text-sm mb-5">Заказ #{order.id}</p>

        <div className="bg-gray-50 rounded-xl p-4 mb-5 flex justify-between items-center">
          <span className="text-gray-600">Сумма к оплате</span>
          <span className="text-2xl font-bold text-gray-900">
            {parseFloat(order.total_amount).toFixed(0)} ₽
          </span>
        </div>

        <p className="text-sm font-medium text-gray-700 mb-3">Способ оплаты</p>
        <div className="space-y-2 mb-6">
          {methods.map((m) => (
            <label
              key={m.id}
              className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors ${
                selectedMethod === m.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="method"
                value={m.id}
                checked={selectedMethod === m.id}
                onChange={() => setSelectedMethod(m.id)}
                className="accent-blue-600"
              />
              <span className="font-medium text-gray-800">{m.name}</span>
            </label>
          ))}
        </div>

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 border border-gray-300 text-gray-700 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handlePay}
            disabled={!selectedMethod || loading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {loading ? 'Обработка...' : 'Принять оплату'}
          </button>
        </div>
      </div>
    </div>
  )
}
