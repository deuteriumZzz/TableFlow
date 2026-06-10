import client from './client'
import type { Order, OrderStatus } from '../types'

export const getOrders = async (orderStatus?: OrderStatus): Promise<Order[]> => {
  const params = orderStatus ? { status: orderStatus } : {}
  const { data } = await client.get<{ results: Order[] } | Order[]>('/orders/', { params })
  return Array.isArray(data) ? data : data.results
}

export const getOrder = async (id: number): Promise<Order> => {
  const { data } = await client.get<Order>(`/orders/${id}/`)
  return data
}

export const createOrder = async (tableId: number | null, comment = ''): Promise<Order> => {
  const { data } = await client.post<Order>('/orders/', { table: tableId, comment })
  return data
}

export const addItem = async (
  orderId: number,
  productId: number,
  quantity: number,
  comment = '',
  modifierIds: number[] = [],
): Promise<Order> => {
  const { data } = await client.post<Order>(`/orders/${orderId}/add_item/`, {
    product_id: productId,
    quantity,
    comment,
    modifier_ids: modifierIds,
  })
  return data
}

export const removeItem = async (orderId: number, itemId: number): Promise<Order> => {
  const { data } = await client.delete<Order>(`/orders/${orderId}/remove_item/${itemId}/`)
  return data
}

export const updateOrderStatus = async (orderId: number, newStatus: OrderStatus): Promise<Order> => {
  const { data } = await client.post<Order>(`/orders/${orderId}/update_status/`, { status: newStatus })
  return data
}
