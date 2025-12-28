// src/services/api.js
import axios from 'axios'
import { message } from 'antd'

// Base URLs for different services
const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8000'
const API_SERVICE_URL = import.meta.env.VITE_API_SERVICE_URL || 'http://localhost:8001'

// Axios instances
const authService = axios.create({
  baseURL: AUTH_SERVICE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

const apiService = axios.create({
  baseURL: API_SERVICE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Add Bearer token to requests (both services)
const requestInterceptor = (config) => {
  const authStorage = localStorage.getItem('auth-storage')
  if (authStorage) {
    try {
      const { state } = JSON.parse(authStorage)
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`
      }
    } catch (err) {
      console.error('Error parsing auth storage:', err)
    }
  }
  return config
}

authService.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))
apiService.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))

// Shared error handler
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
          setTimeout(() => {
            localStorage.removeItem('auth-storage')
            window.location.href = '/login'
          }, 800)
          break
        case 403:
          message.error('Access forbidden')
          break
        case 404:
          message.error('Resource not found')
          break
        case 400:
          message.error(errorData.message)
          break
        case 409:
          message.error(errorData.message || 'Conflict - Resource already exists')
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

// =============================================================================
// AUTH SERVICE (8000)
// =============================================================================
export const authAPI = {
  requestOTP: (phoneNumber) => authService.post('/request-otp', { phoneNumber }),
  verifyOTP: (phoneNumber, otp) => authService.post('/verify-otp', { phoneNumber, otp }),
  getCurrentUser: () => authService.get('/profile'),
  logout: () => authService.post('/logout'),
  validateToken: (token) => authService.post('/validate-token', { token }),
  health: () => authService.get('/health'),
}

// =============================================================================
// API SERVICE (8001)
// =============================================================================

// Medical fields
export const medicalFieldsAPI = {
  getAll: () => apiService.get('/api/medical-fields'),
  getById: (id) => apiService.get(`/api/medical-fields/${id}`),
  getDoctorsCount: (fieldId) => apiService.get(`/api/medical-fields/${fieldId}/doctors-count`),
}

// Doctors
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

// Appointments
export const appointmentsAPI = {
  // POST /api/appointments
  create: (appointmentData) => apiService.post('/api/appointments', appointmentData),

  // GET /api/appointments?status_filter=&limit=&offset=
  getAll: ({ status_filter, limit = 50, offset = 0 } = {}) =>
    apiService.get('/api/appointments', {
      params: { status_filter, limit, offset },
    }),

  // GET /api/appointments/upcoming?limit=
  getUpcoming: (limit = 10) =>
    apiService.get('/api/appointments/upcoming', { params: { limit } }),

  // GET /api/appointments/past?limit=&offset=
  getPast: (limit = 20, offset = 0) =>
    apiService.get('/api/appointments/past', { params: { limit, offset } }),

  // GET /api/appointments/stats
  getStats: () => apiService.get('/api/appointments/stats'),

  // GET /api/appointments/{id}
  getById: (id) => apiService.get(`/api/appointments/${id}`),

  // PATCH /api/appointments/{id}
  // Body supports: status, notes, cancellation_reason
  update: (id, updateData) => apiService.patch(`/api/appointments/${id}`, updateData),

  // Convenience cancel helper
  cancel: (id, cancellationReason) =>
    apiService.patch(`/api/appointments/${id}`, {
      status: 'cancelled',
      cancellation_reason: cancellationReason ?? null,
    }),

  // DELETE /api/appointments/{id}
  delete: (id) => apiService.delete(`/api/appointments/${id}`),
}

// Patients (based on your tests: /api/patients/me)
export const patientAPI = {
  getMe: () => apiService.get('/api/patients/me'),
  updateMe: (data) => apiService.patch('/api/patients/me', data),
}

// Backward compatibility alias (if your UI imports userAPI)
export const userAPI = patientAPI

export default {
  authService,
  apiService,
  authAPI,
  medicalFieldsAPI,
  doctorsAPI,
  appointmentsAPI,
  patientAPI,
  userAPI,
}
