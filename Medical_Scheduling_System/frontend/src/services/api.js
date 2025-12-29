import axios from 'axios'
import { message } from 'antd'
import { useAuthStore } from '../store/authStore'

const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8000'
const API_SERVICE_URL = import.meta.env.VITE_API_SERVICE_URL || 'http://localhost:8001'

const DEFAULT_TIMEOUT_MS = 9999999999999999999999999999999999

const authService = axios.create({
  baseURL: AUTH_SERVICE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: DEFAULT_TIMEOUT_MS,
})

const apiService = axios.create({
  baseURL: API_SERVICE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: DEFAULT_TIMEOUT_MS,
})

const requestInterceptor = (config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

authService.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))
apiService.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))

const forceLogoutAndRedirect = () => {
  try {
    useAuthStore.getState().logout()
  } catch (e) {
    console.error('Logout failed:', e)
  }

  try {
    localStorage.removeItem('auth-storage')
  } catch (e) {
    console.error('Failed to remove auth-storage:', e)
  }

  window.location.href = '/login'
}

const responseErrorInterceptor = (error) => {
  if (error.response) {
    const errorData = {
      statusCode: error.response.status,
      message:
        error.response.data?.detail ||
        error.response.data?.message ||
        error.response.statusText ||
        'An error occurred',
      details: error.response.data?.details || error.response.data?.errors,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response.data,
    }

    error.errorData = errorData

    const showToast = error.config?.showErrorToast !== false
    if (showToast) {
      switch (error.response.status) {
        case 401:
          message.error('Unauthorized. Please login again.')
          setTimeout(() => forceLogoutAndRedirect(), 800)
          break
        case 403:
          message.error('Access forbidden')
          break
        case 404:
          message.error(errorData.message || 'Resource not found')
          break
        case 400:
          message.error(errorData.message)
          break
        case 409:
          message.error(errorData.message || 'Conflict')
          break
        case 422:
          message.error('Validation failed. Please check your input.')
          break
        case 500:
        case 502:
        case 503:
          message.error('Server error. Please try again later.')
          break
        default:
          message.error(errorData.message)
      }
    }
  } else if (error.request) {
    error.errorData = {
      statusCode: 0,
      message: 'Network error. Please check your internet connection.',
      details: 'Unable to reach the server',
    }
    message.error(error.errorData.message)
  } else {
    error.errorData = { message: error.message || 'An unexpected error occurred' }
    message.error(error.errorData.message)
  }

  return Promise.reject(error)
}

authService.interceptors.response.use((r) => r, responseErrorInterceptor)
apiService.interceptors.response.use((r) => r, responseErrorInterceptor)

// AUTH (8000)
export const authAPI = {
  requestOTP: (phoneNumber) => authService.post('/api/auth/request-otp', { phoneNumber }),
  verifyOTP: (phoneNumber, otp) => authService.post('/api/auth/verify-otp', { phoneNumber, otp }),
  getCurrentUser: () => authService.get('/api/auth/profile'),
  logout: () => authService.post('/api/auth/logout'),
  validateToken: (token) => authService.post('/api/auth/validate-token', { token }),
  health: () => authService.get('/api/auth/health'),
}

// API (8001)
export const medicalFieldsAPI = {
  getAll: () => apiService.get('/api/medical-fields'),
  getById: (id) => apiService.get(`/api/medical-fields/${id}`),
  getDoctorsCount: (fieldId) => apiService.get(`/api/medical-fields/${fieldId}/doctors-count`),
}

export const doctorsAPI = {
  getAll: (params) => apiService.get('/api/doctors', { params }),
  getBySpecialty: (medicalFieldId, params = {}) =>
    apiService.get('/api/doctors', { params: { medical_field_id: medicalFieldId, ...params } }),
  getById: (id) => apiService.get(`/api/doctors/${id}`),

  getAvailableSlots: (doctorId, date) =>
    apiService.get(`/api/doctors/${doctorId}/available-slots`, { params: { date } }),

  search: (searchTerm, params = {}) =>
    apiService.get('/api/doctors', { params: { search: searchTerm, ...params } }),
}

// ✅ store-based patientId helper (used only where backend needs it)
const requirePatientId = () => {
  const patientId = useAuthStore.getState().patientId
  const n = Number(patientId)
  if (!n || Number.isNaN(n)) {
    throw new Error('Missing patientId in store. Please login again.')
  }
  return n
}

export const appointmentsAPI = {
  create: (appointmentData) => apiService.post('/api/appointments', appointmentData),

  getAll: ({ status_filter, limit = 50, offset = 0 } = {}) =>
    apiService.get('/api/appointments', { params: { status_filter, limit, offset } }),

  getUpcoming: (limit = 100) => {
    const patient_id = requirePatientId()
    return apiService.get('/api/appointments/upcoming', { params: { patient_id, limit } })
  },

  getPast: (limit = 50, offset = 0) => {
    const patient_id = requirePatientId()
    return apiService.get('/api/appointments/past', { params: { patient_id, limit, offset } })
  },

  getById: (id) => apiService.get(`/api/appointments/${id}`),

  update: (id, updateData) => apiService.patch(`/api/appointments/${id}`, updateData),

  cancel: (id, cancellationReason = null) =>
    apiService.patch(`/api/appointments/${id}`, {
      status: 'cancelled',
      cancellation_reason: cancellationReason,
    }),
}

export const patientsAPI = {
  exists: (phoneNumber) =>
    apiService.get('/api/patients/exists', {
      params: { phone_number: phoneNumber },
    }),

  create: (phoneNumber) =>
    apiService.post('/api/patients/new', {
      phone_number: phoneNumber,
    }),

  getProfile: (patient_id) => {
    const pid = patient_id ?? requirePatientId()
    return apiService.get('/api/patients/profile', {
      params: { patient_id: patient_id },
    })
  },

  updateProfile: (data, patient_id) => {
    const pid = patient_id ?? requirePatientId()
    return apiService.patch('/api/patients/profile', data, {
      params: { patient_id: pid },
    })
  },
}

export default {
  authService,
  apiService,
  authAPI,
  medicalFieldsAPI,
  doctorsAPI,
  appointmentsAPI,
  patientsAPI
}
