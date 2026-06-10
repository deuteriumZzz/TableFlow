import client from './client'
import type { Table } from '../types'

export const getTables = async (): Promise<Table[]> => {
  const { data } = await client.get<{ results: Table[] } | Table[]>('/tables/')
  return Array.isArray(data) ? data : data.results
}

export const updateTableStatus = async (
  id: number,
  tableStatus: Table['status'],
): Promise<Table> => {
  const { data } = await client.patch<Table>(`/tables/${id}/`, { status: tableStatus })
  return data
}
