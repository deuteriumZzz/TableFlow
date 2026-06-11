import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import PrivateRoute from './components/PrivateRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import TablesPage from './pages/TablesPage'
import POSPage from './pages/POSPage'
import KitchenPage from './pages/KitchenPage'
import ReservationPage from './pages/ReservationPage'

export default function App() {
  const loadUser = useAuthStore((s) => s.loadUser)

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <TablesPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/pos/:tableId"
          element={
            <PrivateRoute>
              <POSPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/kitchen"
          element={
            <PrivateRoute>
              <KitchenPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/reservations"
          element={
            <PrivateRoute>
              <ReservationPage />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
