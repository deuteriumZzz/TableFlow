import client from './client'
import type { Payment, PaymentMethod } from '../types'

export const getPaymentMethods = async (): Promise<PaymentMethod[]> => {
  const { data } = await client.get<{ results: PaymentMethod[] } | PaymentMethod[]>('/payment-methods/')
  return Array.isArray(data) ? data : data.results
}

export const createPayment = async (orderId: number, methodId: number): Promise<Payment> => {
  const { data } = await client.post<Payment>('/payments/', {
    order_id: orderId,
    method_id: methodId,
  })
  return data
}
