import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import customParseFormat from 'dayjs/plugin/customParseFormat'

dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)

// Date formatting utilities
export const formatDate = (date, format = 'MMM DD, YYYY') => {
  if (!date) return ''
  return dayjs(date).format(format)
}

export const formatTime = (time) => {
  if (!time) return ''
  return dayjs(time, 'HH:mm').format('h:mm A')
}

export const getRelativeDate = (date) => {
  if (!date) return ''
  const today = dayjs().startOf('day')
  const targetDate = dayjs(date).startOf('day')
  const diff = targetDate.diff(today, 'day')

  if (diff === 0) return 'Today'
  if (diff === 1) return 'Tomorrow'
  if (diff === -1) return 'Yesterday'
  if (diff > 0 && diff <= 7) return dayjs(date).format('dddd')
  
  return dayjs(date).format('MMM DD, YYYY')
}

export const isAppointmentUpcoming = (date) => {
  return dayjs(date).isAfter(dayjs())
}

// Phone number validation and formatting
export const formatPhoneNumber = (phone) => {
  if (!phone) return ''
  const cleaned = phone.replace(/\D/g, '')
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
  }
  return phone
}

export const validatePhoneNumber = (phone) => {
  if (!phone) return false
  const cleaned = phone.replace(/\D/g, '')
  return cleaned.length === 10
}

// String utilities
export const truncate = (str, length = 50) => {
  if (!str) return ''
  return str.length > length ? `${str.substring(0, length)}...` : str
}

export const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

// Status utilities
export const getStatusColor = (status) => {
  const statusMap = {
    confirmed: 'success',
    pending: 'warning',
    cancelled: 'error',
    completed: 'processing',
  }
  return statusMap[status?.toLowerCase()] || 'default'
}

export const getStatusText = (status) => {
  const statusMap = {
    confirmed: 'Confirmed',
    pending: 'Pending',
    cancelled: 'Cancelled',
    completed: 'Completed',
  }
  return statusMap[status?.toLowerCase()] || status
}

// Validation helpers
export const validators = {
  email: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  },
  
  required: (value) => {
    return value !== null && value !== undefined && value !== ''
  },
  
  minLength: (value, length) => {
    return value && value.length >= length
  },
  
  maxLength: (value, length) => {
    return value && value.length <= length
  },
  
  phoneNumber: (phone) => {
    return validatePhoneNumber(phone)
  },
}

// Error handling
export const getErrorMessage = (error) => {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'An unexpected error occurred'
}

// Local storage helpers
export const storage = {
  get: (key) => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch (error) {
      console.error('Error reading from localStorage:', error)
      return null
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('Error writing to localStorage:', error)
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('Error removing from localStorage:', error)
    }
  },
  
  clear: () => {
    try {
      localStorage.clear()
    } catch (error) {
      console.error('Error clearing localStorage:', error)
    }
  },
}
