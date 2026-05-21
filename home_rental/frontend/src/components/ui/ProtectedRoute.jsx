import { Navigate } from 'react-router-dom'
import useAuthStore from '../../store/useAuthStore'

export default function ProtectedRoute({ children }) {
  const { user } = useAuthStore()

  // If user is null (not logged in) redirect to login
  if (user === null) {
    return <Navigate to="/login" replace />
  }

  return children
}