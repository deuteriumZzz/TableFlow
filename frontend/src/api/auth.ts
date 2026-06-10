import client from './client'
import axios from 'axios'
import type { User, AuthTokens } from '../types'

export const login = async (username: string, password: string): Promise<AuthTokens> => {
  const { data } = await axios.post<AuthTokens>('/api/auth/token/', { username, password })
  return data
}

export const getMe = async (): Promise<User> => {
  const { data } = await client.get<User>('/users/me/')
  return data
}

export interface RegisterData {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
  phone?: string
}

export const register = async (data: RegisterData): Promise<User> => {
  const { data: user } = await axios.post<User>('/api/auth/register/', data)
  return user
}
