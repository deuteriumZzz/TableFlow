import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { usePosStore } from '../store/posStore'
import MenuPanel from '../components/MenuPanel'
import OrderPanel from '../components/OrderPanel'
import PaymentModal from '../components/PaymentModal'
import type { Product } from '../types'

export default function POSPage() {
  const { tableId } = useParams<{ tableId: string }>()
  const navigate = useNavigate()
  const { selectedTable, currentOrder, addItem, openPayment, paymentModalOpen, clearTable } =
    usePosStore()

  useEffect(() => {
    if (!selectedTable) navigate('/')
  }, [selectedTable, navigate])

  const handleAddProduct = (product: Product) => {
    addItem(product.id, 1)
  }

  const handleClose = () => {
    clearTable()
    navigate('/')
  }

  return (
    <div className="h-screen flex bg-gray-100 overflow-hidden">
      <div className="flex-1 flex flex-col p-4 overflow-hidden">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">
          Меню — Стол #{tableId}
        </h2>
        <div className="flex-1 overflow-hidden">
          <MenuPanel onAddProduct={handleAddProduct} />
        </div>
      </div>

      <div className="w-80 flex-shrink-0 p-4">
        <OrderPanel onPay={openPayment} onClose={handleClose} />
      </div>

      {paymentModalOpen && currentOrder && (
        <PaymentModal
          order={currentOrder}
          onClose={() => usePosStore.getState().closePayment()}
          onSuccess={() => {
            usePosStore.getState().closePayment()
            clearTable()
            navigate('/')
          }}
        />
      )}
    </div>
  )
}
