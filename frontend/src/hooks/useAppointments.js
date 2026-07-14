import { useState, useEffect } from 'react'
import { appointmentsApi } from '../api/services'

export function useAppointments() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    appointmentsApi.list()
      .then(r => setAppointments(r.data))
      .catch(e => setError(e.response?.data?.detail || 'Failed to load appointments'))
      .finally(() => setLoading(false))
  }, [])

  return { appointments, loading, error }
}
