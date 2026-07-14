import { useEffect } from 'react'
import useAuthStore from '../store/authStore'

export function useCurrentUser() {
  const { user, fetchMe, isAuthenticated } = useAuthStore()
  useEffect(() => {
    if (isAuthenticated && !user) fetchMe()
  }, [isAuthenticated, user, fetchMe])
  return user
}
