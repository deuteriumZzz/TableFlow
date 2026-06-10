const STATUS_LABEL: Record<string, string> = {
  free: 'Свободен',
  occupied: 'Занят',
  reserved: 'Забронирован',
  created: 'Создан',
  in_progress: 'В работе',
  ready: 'Готов',
  delivered: 'Выдан',
  cancelled: 'Отменён',
  pending: 'Ожидание',
  paid: 'Оплачен',
  failed: 'Ошибка',
}

const STATUS_COLOR: Record<string, string> = {
  free: 'bg-green-100 text-green-800',
  occupied: 'bg-red-100 text-red-800',
  reserved: 'bg-yellow-100 text-yellow-800',
  created: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-orange-100 text-orange-800',
  ready: 'bg-green-100 text-green-800',
  delivered: 'bg-gray-100 text-gray-600',
  cancelled: 'bg-gray-100 text-gray-500',
  pending: 'bg-yellow-100 text-yellow-800',
  paid: 'bg-green-100 text-green-800',
}

export default function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLOR[status] ?? 'bg-gray-100 text-gray-600'
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {STATUS_LABEL[status] ?? status}
    </span>
  )
}
