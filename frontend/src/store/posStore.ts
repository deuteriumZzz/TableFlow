import { create } from 'zustand'
import type { Table, Order, Category, Product } from '../types'
import * as ordersApi from '../api/orders'

interface PosState {
  selectedTable: Table | null
  currentOrder: Order | null
  categories: Category[]
  products: Product[]
  selectedCategoryId: number | null
  paymentModalOpen: boolean

  selectTable: (table: Table) => void
  clearTable: () => void
  setOrder: (order: Order) => void
  setCategories: (cats: Category[]) => void
  setProducts: (prods: Product[]) => void
  selectCategory: (id: number | null) => void
  openPayment: () => void
  closePayment: () => void
  addItem: (productId: number, quantity: number, comment?: string) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
}

export const usePosStore = create<PosState>((set, get) => ({
  selectedTable: null,
  currentOrder: null,
  categories: [],
  products: [],
  selectedCategoryId: null,
  paymentModalOpen: false,

  selectTable: (table) => set({ selectedTable: table }),
  clearTable: () => set({ selectedTable: null, currentOrder: null }),

  setOrder: (order) => set({ currentOrder: order }),
  setCategories: (cats) => set({ categories: cats }),
  setProducts: (prods) => set({ products: prods }),
  selectCategory: (id) => set({ selectedCategoryId: id }),
  openPayment: () => set({ paymentModalOpen: true }),
  closePayment: () => set({ paymentModalOpen: false }),

  addItem: async (productId, quantity, comment = '') => {
    const { currentOrder } = get()
    if (!currentOrder) return
    const updated = await ordersApi.addItem(currentOrder.id, productId, quantity, comment)
    set({ currentOrder: updated })
  },

  removeItem: async (itemId) => {
    const { currentOrder } = get()
    if (!currentOrder) return
    const updated = await ordersApi.removeItem(currentOrder.id, itemId)
    set({ currentOrder: updated })
  },
}))
