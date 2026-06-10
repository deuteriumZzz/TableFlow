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
