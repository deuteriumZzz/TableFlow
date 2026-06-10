import client from './client'
import type { Category, Product } from '../types'

export const getCategories = async (): Promise<Category[]> => {
  const { data } = await client.get<{ results: Category[] } | Category[]>('/menu/categories/')
  return Array.isArray(data) ? data : data.results
}

export const getProducts = async (categoryId?: number): Promise<Product[]> => {
  const params = categoryId ? { category: categoryId } : {}
  const { data } = await client.get<{ results: Product[] } | Product[]>('/menu/products/', { params })
  return Array.isArray(data) ? data : data.results
}
