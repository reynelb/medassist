import api from './client'

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  registerViaInvite: (token, data) => api.post(`/auth/register/invite/${token}`, data),
  validateInvite: (token) => api.get(`/auth/invite/validate/${token}`),
  invite: (email) => api.post('/auth/invite', { email }),
  refresh: (refresh_token) => api.post('/auth/refresh', { refresh_token }),
  logout: () => { localStorage.clear() },
}

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  getMe: () => api.get('/users/me'),
  updateMe: (data) => api.patch('/users/me', data),
}

// ── Doctors ───────────────────────────────────────────────────────────────────
export const doctorsApi = {
  getProfile: (doctorId) => api.get(`/doctors/${doctorId}/profile`),
  updateMyProfile: (data) => api.patch('/doctors/me/profile', data),
  getMyPatients: () => api.get('/doctors/me/patients'),
  getDashboard: () => api.get('/doctors/me/dashboard'),
}

// ── Patients ──────────────────────────────────────────────────────────────────
export const patientsApi = {
  getMyProfile: () => api.get('/patients/me/profile'),
  getMyDoctor: () => api.get('/patients/me/doctor'),
  getPatient: (patientId) => api.get(`/patients/${patientId}/profile`),
  updateNotes: (patientId, notes) => api.patch(`/patients/${patientId}/notes`, { doctor_notes: notes }),
  updateConditions: (patientId, data) => api.patch(`/patients/${patientId}/conditions`, data),
}

// ── Appointments ──────────────────────────────────────────────────────────────
export const appointmentsApi = {
  create: (data) => api.post('/appointments/', data),
  list: () => api.get('/appointments/'),
  get: (id) => api.get(`/appointments/${id}`),
  update: (id, data) => api.patch(`/appointments/${id}`, data),
  cancel: (id) => api.delete(`/appointments/${id}`),
  start: (id) => api.post(`/appointments/${id}/start`),
  end: (id) => api.post(`/appointments/${id}/end`),
}

// ── Calls ─────────────────────────────────────────────────────────────────────
export const callsApi = {
  uploadRecording: (appointmentId, audioBlob) => {
    const form = new FormData()
    form.append('file', audioBlob, 'recording.webm')
    return api.post(`/transcripts/calls/${appointmentId}/recording`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ── Transcripts ───────────────────────────────────────────────────────────────
export const transcriptsApi = {
  get: (appointmentId) => api.get(`/transcripts/${appointmentId}`),
  poll: (appointmentId, onReady, interval = 3000) => {
    const id = setInterval(async () => {
      try {
        const { data } = await api.get(`/transcripts/${appointmentId}`)
        if (data.status === 'ready') {
          clearInterval(id)
          onReady(data)
        } else if (data.status === 'failed') {
          clearInterval(id)
        }
      } catch { clearInterval(id) }
    }, interval)
    return () => clearInterval(id)
  },
}

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportsApi = {
  get: (appointmentId) => api.get(`/reports/${appointmentId}`),
  update: (appointmentId, data) => api.patch(`/reports/${appointmentId}`, data),
  confirm: (appointmentId) => api.post(`/reports/${appointmentId}/confirm`),
  getPatientReports: (patientId) => api.get(`/reports/patient/${patientId}`),
  poll: (appointmentId, onReady, interval = 3000) => {
    const id = setInterval(async () => {
      try {
        const { data } = await api.get(`/reports/${appointmentId}`)
        if (data.status === 'draft' || data.status === 'confirmed') {
          clearInterval(id)
          onReady(data)
        }
      } catch { clearInterval(id) }
    }, interval)
    return () => clearInterval(id)
  },
}
