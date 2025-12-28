# Error Component - Usage Examples

This file demonstrates how to use the Error component with various error scenarios from the server.

## 📋 Table of Contents
1. [Basic Usage](#basic-usage)
2. [Server Error Handling](#server-error-handling)
3. [Axios Error Handling](#axios-error-handling)
4. [Validation Errors](#validation-errors)
5. [Network Errors](#network-errors)
6. [Complete Component Example](#complete-component-example)

---

## Basic Usage

### Simple Error Display
```jsx
import Error from './components/Error'

function MyComponent() {
  return (
    <Error 
      type="error"
      message="Something went wrong!"
    />
  )
}
```

---

## Server Error Handling

### Example 1: Passing Axios Error Directly
```jsx
import { useState, useEffect } from 'react'
import { appointmentsAPI } from './services/api'
import Error from './components/Error'
import Loading from './components/Loading'

function AppointmentsList() {
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
      setError(err) // Pass the entire error object
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAppointments()
  }, [])

  if (loading) return <Loading />
  
  if (error) {
    return (
      <Error 
        error={error}  // Component will parse it automatically
        onRetry={fetchAppointments}
        showTechnicalDetails={import.meta.env.DEV} // Show in dev only
      />
    )
  }

  return (
    <div>
      {/* Render appointments */}
    </div>
  )
}
```

### Example 2: HTTP 500 - Server Error
```jsx
// Server response:
// {
//   status: 500,
//   data: {
//     message: "Internal server error",
//     details: "Database connection failed"
//   }
// }

function MyComponent() {
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    try {
      await api.post('/appointments', data)
    } catch (err) {
      setError(err)
    }
  }

  if (error) {
    return (
      <Error 
        error={error}
        // Will automatically show:
        // Title: "Server Error"
        // Message: "Internal server error"
        // Status Code: 500
        // Details: "Database connection failed"
      />
    )
  }

  // ... rest of component
}
```

### Example 3: HTTP 400 - Validation Error
```jsx
// Server response:
// {
//   status: 400,
//   data: {
//     message: "Validation failed",
//     details: [
//       "Phone number is required",
//       "Email format is invalid",
//       "Date must be in the future"
//     ]
//   }
// }

function RegistrationForm() {
  const [error, setError] = useState(null)

  const handleSubmit = async (formData) => {
    try {
      await authAPI.register(formData)
    } catch (err) {
      setError(err)
    }
  }

  if (error) {
    return (
      <Error 
        error={error}
        type="validation"
        // Will show:
        // - Bullet list of validation errors
        // - Status code 400
        // - Warning icon
        onRetry={() => setError(null)}
      />
    )
  }

  // ... form
}
```

### Example 4: HTTP 404 - Not Found
```jsx
// Server response:
// {
//   status: 404,
//   data: {
//     message: "Appointment not found",
//     details: "No appointment exists with ID: 12345"
//   }
// }

function AppointmentDetails({ id }) {
  const [error, setError] = useState(null)
  const [appointment, setAppointment] = useState(null)

  useEffect(() => {
    appointmentsAPI.getById(id)
      .then(res => setAppointment(res.data))
      .catch(err => setError(err))
  }, [id])

  if (error) {
    return (
      <Error 
        error={error}
        // Will automatically detect 404 and show:
        // Title: "Not Found"
        // Message: "Appointment not found"
        // Details: "No appointment exists with ID: 12345"
      />
    )
  }

  // ... render appointment
}
```

### Example 5: HTTP 401 - Unauthorized
```jsx
// Server response:
// {
//   status: 401,
//   data: {
//     message: "Authentication required",
//     details: "Your session has expired. Please login again."
//   }
// }

function ProtectedComponent() {
  const [error, setError] = useState(null)

  useEffect(() => {
    userAPI.getProfile()
      .catch(err => setError(err))
  }, [])

  if (error) {
    return (
      <Error 
        error={error}
        showRetry={false}
        extra={[
          <Button 
            type="primary" 
            onClick={() => navigate('/login')}
          >
            Login Again
          </Button>
        ]}
      />
    )
  }

  // ... protected content
}
```

### Example 6: HTTP 403 - Forbidden
```jsx
// Server response:
// {
//   status: 403,
//   data: {
//     message: "Access denied",
//     details: "You don't have permission to cancel appointments"
//   }
// }

function CancelAppointment() {
  const [error, setError] = useState(null)

  const handleCancel = async () => {
    try {
      await appointmentsAPI.cancel(appointmentId)
    } catch (err) {
      setError(err)
    }
  }

  if (error) {
    return (
      <Error 
        error={error}
        // Shows forbidden message
      />
    )
  }

  // ... cancel UI
}
```

---

## Axios Error Handling

### Complete Axios Error Structure
```jsx
try {
  await api.post('/endpoint', data)
} catch (error) {
  // Axios error structure:
  // {
  //   response: {
  //     status: 400,
  //     data: { message: "...", details: "..." },
  //     headers: {...}
  //   },
  //   request: {...},
  //   config: { url: "/endpoint", method: "post" },
  //   message: "Request failed with status code 400"
  // }

  // Pass entire error - component handles it
  setError(error)
}

// Render:
<Error error={error} showTechnicalDetails={isDev} />
```

---

## Validation Errors

### Multiple Validation Errors
```jsx
// Server response:
// {
//   status: 400,
//   data: {
//     message: "Validation failed",
//     details: [
//       "Name is required",
//       "Email must be valid",
//       "Phone must be 10 digits",
//       "Date must be in future"
//     ]
//   }
// }

function BookingForm() {
  const [error, setError] = useState(null)

  if (error) {
    return (
      <Error 
        error={error}
        type="validation"
        // Shows all validation errors as bullet list
        onRetry={() => setError(null)}
      />
    )
  }

  // ... form
}
```

### Custom Validation Display
```jsx
function CustomValidation() {
  const [error, setError] = useState(null)

  if (error) {
    return (
      <Error 
        error={error}
        title="Please Fix the Following Issues"
        message="Your form contains validation errors"
        // Custom styling for validation
      />
    )
  }

  // ... form
}
```

---

## Network Errors

### No Internet Connection
```jsx
// Error when network is unavailable:
// {
//   request: {...},
//   message: "Network Error"
// }

function DataFetcher() {
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get('/data')
      .catch(err => setError(err))
  }, [])

  if (error) {
    return (
      <Error 
        error={error}
        // Automatically detects network error
        // Shows: "Network error. Please check your internet connection."
      />
    )
  }

  // ... data display
}
```

### Timeout Error
```jsx
// Configure axios timeout:
// axios.create({ timeout: 5000 })

function SlowEndpoint() {
  const [error, setError] = useState(null)

  if (error) {
    return (
      <Error 
        error={error}
        message="Request timed out. The server is taking too long to respond."
      />
    )
  }

  // ... content
}
```

---

## Complete Component Example

### Full Implementation with All Error Handling
```jsx
import { useState, useEffect } from 'react'
import { Card, Button } from 'antd'
import { appointmentsAPI } from '../services/api'
import Loading from '../components/Loading'
import Error from '../components/Error'

function AppointmentManager() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const isDev = import.meta.env.DEV

  const fetchAppointments = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await appointmentsAPI.getUpcoming()
      setAppointments(response.data)
    } catch (err) {
      // Error could be:
      // - 500: Server error
      // - 404: Not found
      // - 401: Unauthorized
      // - 403: Forbidden
      // - 400: Validation error
      // - Network error
      setError(err)
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

  // Error state - automatically handles all error types
  if (error) {
    return (
      <Error 
        error={error}
        onRetry={fetchAppointments}
        showTechnicalDetails={isDev} // Only in development
      />
    )
  }

  // Success state
  return (
    <div>
      {appointments.map(apt => (
        <Card key={apt.id}>
          {/* Appointment details */}
        </Card>
      ))}
    </div>
  )
}

export default AppointmentManager
```

---

## Manual Error Props

### When Not Using Axios
```jsx
function ManualError() {
  return (
    <Error 
      statusCode={500}
      message="Custom error message"
      details="Additional details about the error"
      technicalInfo={{
        timestamp: new Date().toISOString(),
        userId: '12345',
        action: 'create_appointment'
      }}
      showTechnicalDetails={true}
    />
  )
}
```

### Custom Error Object
```jsx
function CustomErrorHandling() {
  const [error, setError] = useState(null)

  const handleAction = async () => {
    try {
      // Some action
    } catch (err) {
      // Create custom error object
      setError({
        statusCode: 400,
        message: "Custom error occurred",
        details: ["Error 1", "Error 2"],
        technicalInfo: { debug: "info" }
      })
    }
  }

  if (error) {
    return (
      <Error 
        statusCode={error.statusCode}
        message={error.message}
        details={error.details}
        technicalInfo={error.technicalInfo}
      />
    )
  }

  // ... component
}
```

---

## Props Reference

| Prop | Type | Description |
|------|------|-------------|
| `error` | Error | Axios error object (auto-parsed) |
| `statusCode` | number | HTTP status code |
| `message` | string | Error message |
| `details` | string/array | Additional details |
| `technicalInfo` | object | Debug information |
| `type` | string | Error type (error, warning, etc.) |
| `title` | string | Error title |
| `onRetry` | function | Retry callback |
| `showRetry` | boolean | Show retry button |
| `showTechnicalDetails` | boolean | Show debug info |
| `fullScreen` | boolean | Full screen mode |
| `extra` | ReactNode | Custom action buttons |

---

## Best Practices

1. **Always pass the error object**:
   ```jsx
   catch (err) {
     setError(err) // ✅ Let component parse it
   }
   ```

2. **Show technical details only in development**:
   ```jsx
   <Error error={error} showTechnicalDetails={import.meta.env.DEV} />
   ```

3. **Provide retry functionality**:
   ```jsx
   <Error error={error} onRetry={fetchData} />
   ```

4. **Handle different error types gracefully**:
   ```jsx
   // Component automatically handles:
   // - Server errors (5xx)
   // - Client errors (4xx)
   // - Network errors
   // - Validation errors
   ```

5. **Use appropriate error types**:
   ```jsx
   <Error error={error} type="validation" /> // For 400 errors
   <Error error={error} type="network" />    // For network issues
   ```

---

## Environment-Specific Behavior

```jsx
// Development
<Error 
  error={error}
  showTechnicalDetails={import.meta.env.DEV} // Shows debug info
/>

// Production
<Error 
  error={error}
  showTechnicalDetails={false} // Hides debug info
/>
```

---

This Error component now fully supports server error handling with automatic parsing and display! 🎉
