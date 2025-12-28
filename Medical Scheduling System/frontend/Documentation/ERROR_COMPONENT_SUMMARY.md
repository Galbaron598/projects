# Enhanced Error Component - Server Error Handling

## 🎯 Overview

The Error component now **fully supports server errors** with automatic parsing and intelligent display of error information from your backend API.

---

## ✨ New Features

### 1. **Automatic Error Parsing**
The component automatically parses Axios error objects and extracts:
- ✅ HTTP status code
- ✅ Error message
- ✅ Validation details
- ✅ Technical/debug information
- ✅ Request information (URL, method)

### 2. **Smart Error Display**
Based on the error, the component shows:
- **500 errors** → "Server Error" with red icon
- **404 errors** → "Not Found" with sad face icon
- **403 errors** → "Forbidden" with warning icon
- **401 errors** → "Unauthorized" with redirect to login
- **400 errors** → "Validation Error" with list of issues
- **Network errors** → "Connection Error" with network icon

### 3. **Validation Error Handling**
Automatically displays validation errors as a formatted list:
```json
{
  "status": 400,
  "data": {
    "message": "Validation failed",
    "details": [
      "Phone number is required",
      "Email format is invalid"
    ]
  }
}
```

### 4. **Technical Details (Debug Mode)**
Shows collapsible technical information in development:
- Request URL and method
- Full error response
- Stack trace (for non-HTTP errors)
- Custom debug data

---

## 📋 Usage Examples

### Basic Usage - Just Pass the Error
```jsx
import Error from './components/Error'

function MyComponent() {
  const [error, setError] = useState(null)

  const fetchData = async () => {
    try {
      const response = await api.get('/appointments')
      setData(response.data)
    } catch (err) {
      setError(err) // Just pass the error!
    }
  }

  if (error) {
    return (
      <Error 
        error={err}  // Component does all the parsing
        onRetry={fetchData}
        showTechnicalDetails={import.meta.env.DEV}
      />
    )
  }

  return <div>{/* Your content */}</div>
}
```

### Server Error Examples

#### 1. HTTP 500 - Server Error
```jsx
// Backend returns:
// {
//   status: 500,
//   data: {
//     message: "Database connection failed",
//     details: "Connection timeout after 30s"
//   }
// }

<Error error={error} />
// Displays:
// Title: "Server Error"
// Message: "Database connection failed"
// Details: "Connection timeout after 30s"
// Status Badge: "Error Code: 500"
```

#### 2. HTTP 400 - Validation Errors
```jsx
// Backend returns:
// {
//   status: 400,
//   data: {
//     message: "Validation failed",
//     details: [
//       "Name is required",
//       "Email must be valid",
//       "Phone must be 10 digits"
//     ]
//   }
// }

<Error error={error} type="validation" />
// Displays:
// Title: "Validation Error"
// Message: "Validation failed"
// Details: Bulleted list of all validation errors
```

#### 3. HTTP 404 - Not Found
```jsx
// Backend returns:
// {
//   status: 404,
//   data: {
//     message: "Appointment not found",
//     details: "No appointment with ID 12345"
//   }
// }

<Error error={error} />
// Displays:
// Title: "Not Found"
// Message: "Appointment not found"
// Details: "No appointment with ID 12345"
// Icon: Sad face
```

#### 4. Network Error (No Internet)
```jsx
// When fetch fails without response:
// {
//   request: {...},
//   message: "Network Error"
// }

<Error error={error} />
// Displays:
// Title: "Network Error"
// Message: "Network error. Please check your internet connection."
// Details: "Unable to reach the server"
```

---

## 🔧 Component Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| **error** | Error | - | **NEW!** Axios error object (auto-parsed) |
| **statusCode** | number | - | HTTP status code (optional if using error) |
| **message** | string | - | Error message (optional if using error) |
| **details** | string/array | - | Additional details (optional if using error) |
| **technicalInfo** | object | - | Debug information (optional if using error) |
| **type** | string | 'error' | Error type: error, warning, info, notFound, unauthorized, network, validation |
| **title** | string | Auto | Custom title (auto-generated from status code) |
| **onRetry** | function | - | Retry button callback |
| **showRetry** | boolean | true | Show/hide retry button |
| **showTechnicalDetails** | boolean | false | **NEW!** Show collapsible debug info |
| **fullScreen** | boolean | false | Full-screen error display |
| **extra** | ReactNode | - | Custom action buttons |

---

## 🎨 What Gets Displayed

### For HTTP 500 Error:
```
┌─────────────────────────────────────┐
│         ❌ Server Error             │
│                                     │
│  Database connection failed         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚠️ Error Code: 500          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ℹ️ Details                   │   │
│  │ Connection timeout after 30s│   │
│  └─────────────────────────────┘   │
│                                     │
│  [🔄 Try Again]  [🏠 Go Home]      │
└─────────────────────────────────────┘
```

### For Validation Errors (HTTP 400):
```
┌─────────────────────────────────────┐
│      ⚠️ Validation Error            │
│                                     │
│  Please fix the following issues    │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚠️ Validation Errors         │   │
│  │ • Phone number is required  │   │
│  │ • Email format is invalid   │   │
│  │ • Date must be in future    │   │
│  └─────────────────────────────┘   │
│                                     │
│  [🔄 Try Again]                    │
└─────────────────────────────────────┘
```

### With Technical Details (Development):
```
┌─────────────────────────────────────┐
│         ❌ Server Error             │
│                                     │
│  Database connection failed         │
│                                     │
│  ▼ 🐛 Technical Details (Debug)    │
│  ┌─────────────────────────────┐   │
│  │ {                           │   │
│  │   "url": "/api/appointments"│   │
│  │   "method": "GET",          │   │
│  │   "status": 500,            │   │
│  │   "timestamp": "..."        │   │
│  │ }                           │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🔄 API Integration

### Updated API Interceptor

The API service (`src/services/api.js`) now formats errors for the Error component:

```javascript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Automatically formats error with:
    if (error.response) {
      error.errorData = {
        statusCode: error.response.status,
        message: error.response.data?.message,
        details: error.response.data?.details,
        url: error.config?.url,
        method: error.config?.method,
      }
    }
    return Promise.reject(error)
  }
)
```

---

## 📝 Real-World Example

### Complete Component with Error Handling

```jsx
import { useState, useEffect } from 'react'
import { appointmentsAPI } from '../services/api'
import Loading from '../components/Loading'
import Error from '../components/Error'

function Appointments() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAppointments = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await appointmentsAPI.getUpcoming()
      setAppointments(response.data)
    } catch (err) {
      // Possible errors:
      // - 500: Server crashed
      // - 404: Endpoint not found
      // - 401: Not logged in
      // - 403: No permission
      // - 400: Invalid request
      // - Network error
      setError(err) // Component handles all cases!
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAppointments()
  }, [])

  // Loading state
  if (loading) {
    return <Loading tip="Loading appointments..." />
  }

  // Error state - automatically shows appropriate UI
  if (error) {
    return (
      <Error 
        error={error}
        onRetry={fetchAppointments}
        showTechnicalDetails={import.meta.env.DEV}
      />
    )
  }

  // Success state
  return (
    <div>
      {appointments.map(apt => (
        <AppointmentCard key={apt.id} appointment={apt} />
      ))}
    </div>
  )
}
```

---

## 🎯 Key Benefits

### Before (Manual Error Handling):
```jsx
catch (error) {
  if (error.response?.status === 500) {
    setErrorMessage('Server error')
  } else if (error.response?.status === 404) {
    setErrorMessage('Not found')
  } else if (error.request) {
    setErrorMessage('Network error')
  } else {
    setErrorMessage('Unknown error')
  }
}

// Then manually render error UI...
```

### After (Automatic Error Handling):
```jsx
catch (error) {
  setError(error) // Done! ✅
}

<Error error={error} onRetry={fetchData} />
```

---

## 🛠️ Disable Toast Notifications

If you want to show errors ONLY in the Error component (no toasts):

```javascript
// In api.js, configure request:
try {
  const response = await api.get('/endpoint', {
    showErrorToast: false  // Disable automatic toast
  })
} catch (err) {
  // Only show in Error component
  setError(err)
}
```

---

## 📚 Documentation Files

1. **Error.jsx** - Enhanced component with server error support
2. **ERROR_COMPONENT_EXAMPLES.md** - Comprehensive usage examples
3. **api.js** - Updated with error formatting
4. **Dashboard.jsx** - Real implementation example

---

## 🚀 Getting Started

1. **Use the Error component**:
   ```jsx
   import Error from './components/Error'
   ```

2. **Catch errors**:
   ```jsx
   try {
     await api.call()
   } catch (err) {
     setError(err)
   }
   ```

3. **Display errors**:
   ```jsx
   if (error) {
     return <Error error={error} onRetry={retry} />
   }
   ```

That's it! The component handles everything else automatically! 🎉

---

## 💡 Best Practices

1. ✅ **Always pass the error object**: `setError(err)`
2. ✅ **Provide retry functionality**: `onRetry={fetchData}`
3. ✅ **Show debug info in dev only**: `showTechnicalDetails={import.meta.env.DEV}`
4. ✅ **Let component auto-detect error type**: Don't manually set type unless needed
5. ✅ **Use consistent error structure** in your backend API

---

**Your Error component is now production-ready with full server error support!** 🎯
