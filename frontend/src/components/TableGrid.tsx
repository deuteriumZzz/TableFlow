import type { Table } from '../types'

interface Props {
  tables: Table[]
  onSelect: (table: Table) => void
}

const TABLE_COLOR: Record<Table['status'], string> = {
  free: 'bg-green-500 hover:bg-green-600 text-white',
  occupied: 'bg-red-500 hover:bg-red-600 text-white',
  reserved: 'bg-yellow-500 hover:bg-yellow-600 text-white',
}

export default function TableGrid({ tables, onSelect }: Props) {
  if (tables.length === 0) {
    return (
      <p className="text-center text-gray-400 py-12">
        Нет столов. Добавьте их в панели администратора.
      </p>
    )
  }

  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-4">
      {tables.map((table) => (
        <button
          key={table.id}
          onClick={() => onSelect(table)}
          className={`${TABLE_COLOR[table.status]} rounded-2xl p-5 flex flex-col items-center justify-center shadow transition-transform hover:scale-105 active:scale-95`}
        >
          <span className="text-3xl font-bold">#{table.number}</span>
          <span className="text-sm mt-1 opacity-90">
            {table.status === 'free'
              ? `${table.capacity} мест`
              : table.status === 'occupied'
              ? 'Занят'
              : 'Бронь'}
          </span>
        </button>
      ))}
    </div>
  )
}
