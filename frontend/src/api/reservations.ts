import api from './client'

export interface Reservation {
  id: number
  table: number | null
  table_number: number | null
  guest_name: string
  guest_phone: string
  guest_count: number
  reserved_at: string
  duration_minutes: number
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no_show'
  comment: string
  created_by: number | null
  created_at: string
  updated_at: string
}

export interface CreateReservationPayload {
  table?: number | null
  guest_name: string
  guest_phone: string
  guest_count: number
  reserved_at: string
  duration_minutes?: number
  comment?: string
}

export const getReservations = (date?: string) =>
  api.get<{ results: Reservation[] }>('/reservations/', { params: date ? { date } : {} })
    .then((r) => r.data.results)

export const createReservation = (data: CreateReservationPayload) =>
  api.post<Reservation>('/reservations/', data).then((r) => r.data)

export const confirmReservation = (id: number) =>
  api.post<Reservation>(`/reservations/${id}/confirm/`).then((r) => r.data)

export const cancelReservation = (id: number) =>
  api.post<Reservation>(`/reservations/${id}/cancel/`).then((r) => r.data)
