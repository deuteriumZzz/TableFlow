import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { usePosStore } from '../store/posStore'
import { getTables } from '../api/tables'
import { createOrder } from '../api/orders'
import TableGrid from '../components/TableGrid'
import type { Table } from '../types'

export default function TablesPage() {
  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const { selectTable, setOrder } = usePosStore()
  const navigate = useNavigate()

  const load = async () => {
    try {
      const data = await getTables()
      setTables(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleSelectTable = async (table: Table) => {
    setCreating(true)
    try {
      selectTable(table)
      const order = await createOrder(table.id)
      setOrder(order)
      navigate(`/pos/${table.id}`)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">TableFlow POS</h1>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/kitchen')}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Кухня
          </button>
          <span className="text-sm text-gray-500">
            {user?.first_name || user?.username}
          </span>
          <button
            onClick={logout}
            className="text-sm text-red-500 hover:text-red-700"
          >
            Выйти
          </button>
        </div>
      </header>

      <main className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-700">Выберите стол</h2>
          <button
            onClick={load}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Обновить
          </button>
        </div>

        {loading ? (
          <p className="text-center text-gray-400 py-12">Загрузка...</p>
        ) : (
          <TableGrid tables={tables} onSelect={handleSelectTable} />
        )}
      </main>

      {creating && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center">
          <div className="bg-white rounded-xl px-8 py-6 shadow-xl">
            <p className="text-gray-700">Создание заказа...</p>
          </div>
        </div>
      )}
    </div>
  )
}
