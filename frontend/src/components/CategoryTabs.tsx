import type { Category } from '../types'

interface Props {
  categories: Category[]
  selected: number | null
  onSelect: (id: number | null) => void
}

export default function CategoryTabs({ categories, selected, onSelect }: Props) {
  return (
    <div className="flex gap-2 flex-wrap mb-4">
      <button
        onClick={() => onSelect(null)}
        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          selected === null
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
        }`}
      >
        Все
      </button>
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.id)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            selected === cat.id
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          {cat.name}
        </button>
      ))}
    </div>
  )
}
