import axios from 'axios'
import { message } from 'antd'

// Base URLs for different services
const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8000'
const API_SERVICE_URL = import.meta.env.VITE_API_SERVICE_URL || 'http://localhost:8001'

// Create separate axios instances for each service
const authService = axios.create({
  baseURL: AUTH_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

const apiService = axios.create({
  baseURL: API_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor - Add token to requests (for both services)
const requestInterceptor = (config) => {
  const authStorage = localStorage.getItem('auth-storage')
  if (authStorage) {
    try {
      const { state } = JSON.parse(authStorage)
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`
      }
    } catch (error) {
      console.error('Error parsing auth storage:', error)
    }
  }
  return config
}

authService.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))
apiService.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))

// Response interceptor - Handle errors (shared for both services)
const responseErrorInterceptor = (error) => {
  // Add custom error information for better handling
  if (error.response) {
    // Server responded with error
    const errorData = {
      statusCode: error.response.status,
      message: error.response.data?.detail || error.response.data?.message || error.response.statusText || 'An error occurred',
      details: error.response.data?.details || error.response.data?.errors,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response.data,
    }

    // Optional: Show toast notifications (can be disabled)
    const showToast = error.config?.showErrorToast !== false

    if (showToast) {
      switch (error.response.status) {
        case 401:
          message.error('Unauthorized. Please login again.')
          // Clear auth and redirect to login
          setTimeout(() => {
            localStorage.removeItem('auth-storage')
            window.location.href = '/login'
          }, 1000)
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
        case 422:
          message.error('Validation failed. Please check your input.')
          break
        case 409:
          message.error(errorData.message || 'Conflict - Resource already exists')
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

    // Attach formatted error data to error object
    error.errorData = errorData
    
  } else if (error.request) {
    // Request made but no response (network error)
    error.errorData = {
      statusCode: 0,
      message: 'Network error. Please check your internet connection.',
      details: 'Unable to reach the server',
    }
    message.error(error.errorData.message)
    
  } else {
    // Something else happened
    error.errorData = {
      message: error.message || 'An unexpected error occurred',
    }
    message.error(error.errorData.message)
  }
  
  return Promise.reject(error)
}

authService.interceptors.response.use((response) => response, responseErrorInterceptor)
apiService.interceptors.response.use((response) => response, responseErrorInterceptor)

// =============================================================================
// AUTH SERVICE ENDPOINTS (Port 8000)
// =============================================================================

export const authAPI = {
  // Request OTP
  requestOTP: (phoneNumber) => authService.post('/request-otp', { phoneNumber }),
  
  // Verify OTP
  verifyOTP: (phoneNumber, otp) => authService.post('/verify-otp', { phoneNumber, otp }),
  
  // Get current user profile
  getCurrentUser: () => authService.get('/profile'),
  
  // Logout
  logout: () => authService.post('/logout'),
  
  // Validate token (internal use)
  validateToken: (token) => authService.post('/validate-token', { token }),
  
  // Health check
  health: () => authService.get('/health'),
}

// =============================================================================
// API SERVICE ENDPOINTS (Port 8001)
// =============================================================================

// Medical fields endpoints
export const medicalFieldsAPI = {
  // Get all medical fields
  getAll: () => apiService.get('/api/medical-fields'),
  
  // Get specific medical field by ID
  getById: (id) => apiService.get(`/api/medical-fields/${id}`),
  
  // Get doctor count for a medical field
  getDoctorsCount: (fieldId) => apiService.get(`/api/medical-fields/${fieldId}/doctors-count`),
}

// Doctors endpoints
export const doctorsAPI = {
  // Get all doctors with filters
  getAll: (params) => apiService.get('/api/doctors', { params }),
  
  // Get doctors by specialty
  getBySpecialty: (specialtyId, params = {}) => 
    apiService.get('/api/doctors', { 
      params: { medical_field_id: specialtyId, ...params } 
    }),
  
  // Get specific doctor by ID
  getById: (id) => apiService.get(`/api/doctors/${id}`),
  
  // Get available time slots for a doctor
  getAvailableSlots: (doctorId, date) => 
    apiService.get(`/api/doctors/${doctorId}/available-slots`, { 
      params: { date } 
    }),
  
  // Search doctors
  search: (searchTerm, params = {}) => 
    apiService.get('/api/doctors', { 
      params: { search: searchTerm, ...params } 
    }),
}

// Appointments endpoints
export const appointmentsAPI = {
  // Create new appointment
  create: (appointmentData) => apiService.post('/api/appointments', appointmentData),
  
  // Get all appointments with filters
  getAll: (params) => apiService.get('/api/appointments', { params }),
  
  // Get upcoming appointments
  getUpcoming: (limit = 10) => 
    apiService.get('/api/appointments/upcoming', { params: { limit } }),
  
  // Get past appointments
  getPast: (limit = 20, offset = 0) => 
    apiService.get('/api/appointments/past', { params: { limit, offset } }),
  
  // Get appointment statistics
  getStats: () => apiService.get('/api/appointments/stats'),
  
  // Get specific appointment by ID
  getById: (id) => apiService.get(`/api/appointments/${id}`),
  
  // Update appointment (status, notes, etc.)
  update: (id, updateData) => apiService.patch(`/api/appointments/${id}`, updateData),
  
  // Cancel appointment
  cancel: (id, cancellationReason = null) => 
    apiService.patch(`/api/appointments/${id}`, { 
      status: 'cancelled',
      cancellation_reason: cancellationReason 
    }),
  
  // Delete appointment (hard delete)
  delete: (id) => apiService.delete(`/api/appointments/${id}`),
  
  // Reschedule appointment
  reschedule: (id, newAppointmentTime) => 
    apiService.patch(`/api/appointments/${id}`, { 
      appointment_time: newAppointmentTime 
    }),
}

// Patient/User endpoints
export const patientAPI = {
  // Get current patient profile
  getProfile: () => apiService.get('/api/patients/profile'),
  
  // Update patient profile
  updateProfile: (userData) => apiService.patch('/api/patients/profile', userData),
}

// Alias for backward compatibility
export const userAPI = patientAPI

// =============================================================================
// EXPORT DEFAULT
// =============================================================================

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