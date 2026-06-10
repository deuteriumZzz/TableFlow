export interface Restaurant {
  id: number
  name: string
  currency: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'manager' | 'cashier' | 'waiter' | 'chef' | 'auditor' | 'client'
  restaurant: number | null
  phone: string
  avatar: string | null
}

export interface Table {
  id: number
  number: number
  capacity: number
  status: 'free' | 'occupied' | 'reserved'
  restaurant: number
}

export interface Category {
  id: number
  name: string
  description: string
  image: string | null
  sort_order: number
}

export interface Modifier {
  id: number
  name: string
  price: string
  is_required: boolean
}

export interface Product {
  id: number
  name: string
  description: string
  price: string
  status: 'available' | 'out_of_stock' | 'limited'
  image: string | null
  category: Category | null
  modifiers: Modifier[]
}

export interface OrderItemModifier {
  id: number
  modifier: Modifier
  quantity: number
}

export interface OrderItem {
  id: number
  product: Product
  quantity: number
  price: string
  total_price: string
  comment: string
  status: string
  applied_modifiers: OrderItemModifier[]
}

export type OrderStatus = 'created' | 'in_progress' | 'ready' | 'delivered' | 'cancelled' | 'refunded'
export type PaymentStatus = 'pending' | 'paid' | 'partial' | 'failed' | 'refunded'

export interface Order {
  id: number
  table: number | null
  table_number: number | null
  waitress: number | null
  status: OrderStatus
  payment_status: PaymentStatus
  total_amount: string
  discount: string
  tax: string
  comment: string
  is_online: boolean
  created_at: string
  updated_at: string
  items: OrderItem[]
}

export interface PaymentMethod {
  id: number
  name: string
  description: string
}

export interface Payment {
  id: number
  order: number
  amount: string
  method: number
  method_name: string
  status: string
  transaction_id: string
  created_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}
