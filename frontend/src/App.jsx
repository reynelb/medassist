import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from './store/authStore'

// Auth pages
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import InviteRegisterPage from './pages/auth/InviteRegisterPage'

// Doctor pages
import DoctorDashboard from './pages/doctor/DoctorDashboard'
import DoctorPatientList from './pages/doctor/DoctorPatientList'
import DoctorPatientProfile from './pages/doctor/DoctorPatientProfile'
import DoctorAppointments from './pages/doctor/DoctorAppointments'
import DoctorAppointmentDetail from './pages/doctor/DoctorAppointmentDetail'
import DoctorCallRoom from './pages/doctor/DoctorCallRoom'
import DoctorTranscript from './pages/doctor/DoctorTranscript'
import DoctorReport from './pages/doctor/DoctorReport'
import DoctorProfile from './pages/doctor/DoctorProfile'
import DoctorInvitations from './pages/doctor/DoctorInvitations'

// Patient pages
import PatientHome from './pages/patient/PatientHome'
import PatientDoctorProfile from './pages/patient/PatientDoctorProfile'
import PatientAppointments from './pages/patient/PatientAppointments'
import PatientAppointmentDetail from './pages/patient/PatientAppointmentDetail'
import PatientCallRoom from './pages/patient/PatientCallRoom'
import PatientProfile from './pages/patient/PatientProfile'

function ProtectedRoute({ children, allowedRole }) {
  const { isAuthenticated, role } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (allowedRole && role !== allowedRole) {
    return <Navigate to={role === 'doctor' ? '/doctor/dashboard' : '/patient/home'} replace />
  }
  return children
}

function RoleRedirect() {
  const { isAuthenticated, role } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Navigate to={role === 'doctor' ? '/doctor/dashboard' : '/patient/home'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RoleRedirect />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/register/invite/:token" element={<InviteRegisterPage />} />

        <Route path="/doctor/dashboard" element={<ProtectedRoute allowedRole="doctor"><DoctorDashboard /></ProtectedRoute>} />
        <Route path="/doctor/patients" element={<ProtectedRoute allowedRole="doctor"><DoctorPatientList /></ProtectedRoute>} />
        <Route path="/doctor/patients/:id" element={<ProtectedRoute allowedRole="doctor"><DoctorPatientProfile /></ProtectedRoute>} />
        <Route path="/doctor/appointments" element={<ProtectedRoute allowedRole="doctor"><DoctorAppointments /></ProtectedRoute>} />
        <Route path="/doctor/appointments/:id" element={<ProtectedRoute allowedRole="doctor"><DoctorAppointmentDetail /></ProtectedRoute>} />
        <Route path="/doctor/appointments/:id/call" element={<ProtectedRoute allowedRole="doctor"><DoctorCallRoom /></ProtectedRoute>} />
        <Route path="/doctor/appointments/:id/transcript" element={<ProtectedRoute allowedRole="doctor"><DoctorTranscript /></ProtectedRoute>} />
        <Route path="/doctor/appointments/:id/report" element={<ProtectedRoute allowedRole="doctor"><DoctorReport /></ProtectedRoute>} />
        <Route path="/doctor/profile" element={<ProtectedRoute allowedRole="doctor"><DoctorProfile /></ProtectedRoute>} />
        <Route path="/doctor/invitations" element={<ProtectedRoute allowedRole="doctor"><DoctorInvitations /></ProtectedRoute>} />

        <Route path="/patient/home" element={<ProtectedRoute allowedRole="patient"><PatientHome /></ProtectedRoute>} />
        <Route path="/patient/doctor" element={<ProtectedRoute allowedRole="patient"><PatientDoctorProfile /></ProtectedRoute>} />
        <Route path="/patient/appointments" element={<ProtectedRoute allowedRole="patient"><PatientAppointments /></ProtectedRoute>} />
        <Route path="/patient/appointments/:id" element={<ProtectedRoute allowedRole="patient"><PatientAppointmentDetail /></ProtectedRoute>} />
        <Route path="/patient/appointments/:id/call" element={<ProtectedRoute allowedRole="patient"><PatientCallRoom /></ProtectedRoute>} />
        <Route path="/patient/profile" element={<ProtectedRoute allowedRole="patient"><PatientProfile /></ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
