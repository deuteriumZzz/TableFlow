import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getReservations,
  createReservation,
  confirmReservation,
  cancelReservation,
  type Reservation,
} from '../api/reservations'

const STATUS_LABEL: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждено',
  cancelled: 'Отменено',
  completed: 'Завершено',
  no_show: 'Не пришли',
}

const STATUS_COLOR: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  completed: 'bg-gray-100 text-gray-600',
  no_show: 'bg-orange-100 text-orange-800',
}

const today = () => new Date().toISOString().slice(0, 10)

export default function ReservationPage() {
  const navigate = useNavigate()
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [date, setDate] = useState(today())
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    guest_name: '',
    guest_phone: '',
    guest_count: 2,
    reserved_at: `${today()}T19:00`,
    duration_minutes: 120,
    comment: '',
  })
  const [error, setError] = useState('')

  const load = async (d = date) => {
    setLoading(true)
    try {
      setReservations(await getReservations(d))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [date])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.guest_name || !form.guest_phone) {
      setError('Введите имя и телефон гостя')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      await createReservation({ ...form, reserved_at: new Date(form.reserved_at).toISOString() })
      setShowForm(false)
      setForm({ guest_name: '', guest_phone: '', guest_count: 2, reserved_at: `${today()}T19:00`, duration_minutes: 120, comment: '' })
      load()
    } catch {
      setError('Не удалось создать бронирование')
    } finally {
      setSubmitting(false)
    }
  }

  const handleConfirm = async (id: number) => {
    await confirmReservation(id)
    load()
  }

  const handleCancel = async (id: number) => {
    await cancelReservation(id)
    load()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Бронирования</h1>
        <div className="flex gap-3">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="border rounded-lg px-3 py-1.5 text-sm"
          />
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-700"
          >
            + Новое
          </button>
          <button onClick={() => navigate('/')} className="text-sm text-gray-500 hover:text-gray-800">
            ← Назад
          </button>
        </div>
      </header>

      <main className="p-6 max-w-4xl mx-auto">
        {loading ? (
          <p className="text-gray-400 text-center py-12">Загрузка...</p>
        ) : reservations.length === 0 ? (
          <p className="text-gray-400 text-center py-12">Бронирований на {date} нет</p>
        ) : (
          <div className="space-y-3">
            {reservations.map((r) => (
              <div key={r.id} className="bg-white rounded-xl border p-4 flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{r.guest_name}</span>
                    <span className="text-sm text-gray-500">{r.guest_phone}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLOR[r.status]}`}>
                      {STATUS_LABEL[r.status]}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500 flex gap-4">
                    <span>{new Date(r.reserved_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</span>
                    <span>{r.guest_count} гост.</span>
                    <span>{r.duration_minutes} мин.</span>
                    {r.table_number && <span>Стол #{r.table_number}</span>}
                  </div>
                  {r.comment && <p className="text-xs text-gray-400 mt-1 italic">{r.comment}</p>}
                </div>
                <div className="flex gap-2 shrink-0">
                  {r.status === 'pending' && (
                    <button
                      onClick={() => handleConfirm(r.id)}
                      className="bg-green-600 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-green-700"
                    >
                      Подтвердить
                    </button>
                  )}
                  {(r.status === 'pending' || r.status === 'confirmed') && (
                    <button
                      onClick={() => handleCancel(r.id)}
                      className="bg-red-100 text-red-700 text-xs px-3 py-1.5 rounded-lg hover:bg-red-200"
                    >
                      Отменить
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
            <h2 className="text-lg font-bold mb-4">Новое бронирование</h2>
            <form onSubmit={handleCreate} className="space-y-3">
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Имя гостя *"
                value={form.guest_name}
                onChange={(e) => setForm((f) => ({ ...f, guest_name: e.target.value }))}
              />
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Телефон *"
                value={form.guest_phone}
                onChange={(e) => setForm((f) => ({ ...f, guest_phone: e.target.value }))}
              />
              <div className="flex gap-2">
                <input
                  type="number" min={1}
                  className="flex-1 border rounded-lg px-3 py-2 text-sm"
                  placeholder="Гостей"
                  value={form.guest_count}
                  onChange={(e) => setForm((f) => ({ ...f, guest_count: +e.target.value }))}
                />
                <input
                  type="number" min={15}
                  className="flex-1 border rounded-lg px-3 py-2 text-sm"
                  placeholder="Мин."
                  value={form.duration_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, duration_minutes: +e.target.value }))}
                />
              </div>
              <input
                type="datetime-local"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={form.reserved_at}
                onChange={(e) => setForm((f) => ({ ...f, reserved_at: e.target.value }))}
              />
              <textarea
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Комментарий"
                rows={2}
                value={form.comment}
                onChange={(e) => setForm((f) => ({ ...f, comment: e.target.value }))}
              />
              {error && <p className="text-red-600 text-sm">{error}</p>}
              <div className="flex gap-2 pt-1">
                <button
                  type="submit" disabled={submitting}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
                >
                  {submitting ? 'Сохранение...' : 'Создать'}
                </button>
                <button
                  type="button" onClick={() => setShowForm(false)}
                  className="flex-1 border py-2 rounded-lg text-sm hover:bg-gray-50"
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
