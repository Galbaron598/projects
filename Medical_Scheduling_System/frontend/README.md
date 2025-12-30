# Medical Scheduling System - Frontend

A modern, professional medical appointment booking system built with **React**, **Ant Design**, and **Zustand**. This application provides an intuitive and seamless experience for patients to manage their medical appointments.

## 🚀 Features

### Core Functionality
- **OTP Authentication**: Secure phone-based login with one-time password verification
- **Smart Dashboard**: Context-aware interface that adapts for new and returning users
- **Multi-Step Booking Wizard**: Intuitive appointment booking flow with progress tracking
- **Appointment Management**: View, cancel, and manage appointments
- **Profile Management**: Update personal information, add family members, and track medical history
- **Responsive Design**: Fully optimized for mobile, tablet, and desktop devices

### Technical Highlights
- ✅ **Ant Design Components**: Professional, production-ready UI components
- ✅ **Zustand State Management**: Lightweight, efficient state management with persistence
- ✅ **Loading States**: Custom loading components for better UX
- ✅ **Error Handling**: Comprehensive error boundaries and user-friendly error messages
- ✅ **TypeScript Ready**: Easy migration to TypeScript if needed
- ✅ **Mock Data**: Built-in mock data for testing without backend

## 🛠️ Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI Library | ^18.2.0 |
| **Ant Design** | Component Library | ^5.12.0 |
| **Zustand** | State Management | ^4.4.7 |
| **React Router** | Client-side Routing | ^6.20.0 |
| **Axios** | HTTP Client | ^1.6.2 |
| **Day.js** | Date Manipulation | ^1.11.10 |
| **Vite** | Build Tool | ^5.0.8 |


## 🚀 Getting Started

# 📦 Dependencies

This project uses the following main libraries:

- **React 18** – UI framework
- **React Router DOM** – Client-side routing
- **Ant Design** – UI component library
- **Zustand** – State management
- **Axios** – HTTP client
- **Day.js** – Date and time utilities

### Development Tools

- **Vite** – Build tool and dev server
- **ESLint** – Linting and code quality

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd rontend
```
2. **Install dependencies**:
Install all dependencies (including development dependencies):
```bash
npm install
```

3. **Create environment file**:
```bash
cp .env.example .env
```

5. **Start the development server**:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`


## 🎨 UI Components (Ant Design)

### Why Ant Design?

Ant Design provides:
- **60+ High-Quality Components**: Pre-built, tested, and accessible
- **Consistent Design Language**: Professional enterprise-level UI
- **Responsive Out of the Box**: Works on all devices
- **Customizable Theme**: Easy to match your brand
- **TypeScript Support**: Built with TypeScript
- **Internationalization**: Multi-language support

### Key Components Used

| Component | Usage |
|-----------|-------|
| **Layout** | Sidebar navigation layout |
| **Card** | Content containers |
| **Form** | User input forms |
| **Steps** | Multi-step wizard |
| **Table/List** | Data display |
| **Modal** | Dialogs and confirmations |
| **Message** | Toast notifications |
| **Spin** | Loading indicators |
| **Button** | Actions |
| **Input** | Form fields |

### Theme Customization

The app uses a custom Ant Design theme configured in `src/main.jsx`:

```javascript
const theme = {
  token: {
    colorPrimary: '#1890ff',    // Primary blue
    colorSuccess: '#52c41a',    // Success green
    colorWarning: '#faad14',    // Warning orange
    colorError: '#ff4d4f',      // Error red
    borderRadius: 8,            // Rounded corners
    fontSize: 14,               // Base font size
  },
  components: {
    Button: {
      borderRadius: 8,
      controlHeight: 40,
    },
    // ... more customizations
  },
}
```

## 📦 State Management (Zustand)

### Why Zustand?

Zustand is perfect for this project because:
- ✅ **Minimal Boilerplate**: Simple API, less code
- ✅ **Small Bundle Size**: Only 1.2KB (vs Redux 12KB+)
- ✅ **Built-in Persistence**: Easy localStorage integration
- ✅ **No Providers Needed**: No wrapper components
- ✅ **TypeScript Ready**: Excellent TypeScript support
- ✅ **DevTools Support**: Redux DevTools compatible

### Store Structure

```javascript
// src/store/authStore.js
export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      
      // Actions
      login: (userData, token) => set({ 
        user: userData, 
        token, 
        isAuthenticated: true 
      }),
      
      logout: () => set({ 
        user: null, 
        token: null, 
        isAuthenticated: false 
      }),
      
      // ... more actions
    }),
    {
      name: 'auth-storage',  // localStorage key
    }
  )
)
```

## 🔐 Authentication Flow

1. **User enters phone number** → Validation
2. **System generates mock OTP** → Displayed for testing
3. **User enters OTP** → Verification
4. **Login successful** → Token stored in Zustand + localStorage
5. **Protected routes accessible** → Navigate to dashboard

**Note**: Mock OTP is shown in console and UI for testing. Replace with real SMS integration in production.

## 📱 Pages Overview

### 1. Login (`/login`)
- Phone number input with validation
- OTP verification (6-digit input)
- Mock OTP display for testing
- Responsive two-column layout
- Brand information display

### 2. Dashboard (`/dashboard`)
**New Users**:
- Welcome message
- Call-to-action to book first appointment
- Medical services overview

**Returning Users**:
- Upcoming appointments cards
- Quick action buttons
- Available specialties grid

### 3. Book Appointment (`/book`)
Multi-step wizard:
1. **Choose Specialty**: choose one medical specialty
2. **Select Doctor**: Doctor profiles with ratings
3. **Pick Date & Time**: Calendar and time slot picker
4. **Confirm**: Review and submit

Features:
- Progress indicator
- Form validation
- Back/Next navigation
- Data persistence across steps

### 4. Appointments (`/appointments`)
- Tabs: Upcoming & Past
- Search functionality
- Cancel appointments
- Reschedule option
- Status badges (Confirmed, Completed, Cancelled)

### 5. Profile (`/profile`)
- Personal information editing
- Emergency contacts
- Edit/Save modes

## 🔄 API Integration

The app uses a centralized API service (`src/services/api.js`):

```javascript
// Example API call
import { appointmentsAPI } from './services/api'

const fetchAppointments = async () => {
  try {
    const response = await appointmentsAPI.getUpcoming()
    setAppointments(response.data)
  } catch (error) {
    message.error('Failed to load appointments')
  }
}
```
### Connecting to Real Backend

1. Update `VITE_API_BASE_URL` in `.env`
2. Uncomment API calls in components (marked with comments)
3. Remove mock data

## 🎭 Loading & Error Components

### Loading Component

```javascript
import Loading from './components/Loading'

// Full screen loading
<Loading fullScreen tip="Loading..." />

// Inline loading
<Loading tip="Loading appointments..." />
```

### Error Component

```javascript
import Error from './components/Error'

// Display error
<Error 
  type="error"
  title="Something went wrong"
  message="Failed to load data"
  onRetry={fetchData}
/>

// Error types: error, warning, info, notFound, unauthorized
```

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Build and deploy
npm run build
netlify deploy --prod
```

### Environment Variables

Set these in your deployment platform:
- `VITE_API_BASE_URL` - Backend API URL

## 🔒 Security Features

- ✅ JWT token authentication
- ✅ Protected routes
- ✅ Axios request interceptors
- ✅ Secure token storage
- ✅ Input validation
- ✅ XSS protection (React escapes by default)
- ✅ HTTPS required in production

## 📝 Development Best Practices

### Code Organization
- Components are modular and reusable
- Services layer separates API logic
- Utils contain helper functions
- State management is centralized

### Performance
- Optimized re-renders with Zustand selectors
- Vite for fast builds

### Accessibility
- Semantic HTML
- ARIA labels (Ant Design provides)
- Keyboard navigation
- Screen reader support

## 🐛 Known Issues & Future Improvements

### Current Limitations
- Mock data for demonstration
- Reschedule feature is placeholder
- Medical history is static
- No real-time notifications


## 🤝 Contributing

This is a take-home assignment project for CORTEX. 

## 📄 License

This project was created as part of the CORTEX Full-Stack Developer Assignment.

## 👨‍💻 Author

Created for CORTEX R&D Center recruitment process.

## 🙏 Acknowledgments

- **Ant Design** - For React components
- **Zustand** - For simple state management
- **Vite** - For blazing fast build tool
- **Day.js** - For lightweight date manipulation
- **React Router** - For routing solution

---

## 📞 Support

For questions or issues:
1. Check the code comments
2. Review Ant Design documentation: https://ant.design
3. Review Zustand documentation: https://github.com/pmndrs/zustand

