# CSS Structure Documentation

## 📁 CSS Files Organization

All CSS files are organized in the `/src/styles/` directory with separate files for each component and page.

```
src/styles/
├── global.css              # Global styles and resets
├── Loading.css             # Loading component styles
├── Error.css               # Error component styles  
├── Layout.css              # Layout component styles
├── Login.css               # Login page styles
├── Dashboard.css           # Dashboard page styles
├── BookAppointment.css     # Book appointment page styles
├── Appointments.css        # Appointments list page styles
└── Profile.css             # Profile page styles
```

---

## 🎨 CSS Import Structure

### Global Styles
Imported in `main.jsx`:
```javascript
import './styles/global.css'
```

### Component Styles
Each component imports its own CSS file:

**Loading.jsx**:
```javascript
import '../styles/Loading.css'
```

**Error.jsx**:
```javascript
import '../styles/Error.css'
```

**Layout.jsx**:
```javascript
import '../styles/Layout.css'
```

### Page Styles
Each page imports its own CSS file:

**Login.jsx**:
```javascript
import '../styles/Login.css'
```

**Dashboard.jsx**:
```javascript
import '../styles/Dashboard.css'
```

**BookAppointment.jsx**:
```javascript
import '../styles/BookAppointment.css'
```

**Appointments.jsx**:
```javascript
import '../styles/Appointments.css'
```

**Profile.jsx**:
```javascript
import '../styles/Profile.css'
```

---

## 📋 CSS Classes Reference

### Global Classes (global.css)

| Class | Purpose |
|-------|---------|
| `.app-container` | Main app wrapper |
| `.content-container` | Content area wrapper |
| `.fade-in` | Fade-in animation |

### Loading Component (Loading.css)

| Class | Purpose |
|-------|---------|
| `.loading-container` | Inline loading wrapper |
| `.loading-overlay` | Full-screen loading overlay |
| `.loading-spinner` | Spinner container |
| `.loading-icon` | Icon styling |
| `.loading-text` | Loading text styling |

### Error Component (Error.css)

| Class | Purpose |
|-------|---------|
| `.error-container` | Main error wrapper |
| `.error-container.fullscreen` | Full-screen mode |
| `.error-container.inline` | Inline mode |
| `.error-content` | Content wrapper |
| `.error-details` | Details section |
| `.error-alert` | Alert styling |
| `.error-technical-details` | Debug info section |
| `.error-technical-code` | Code block styling |
| `.error-validation-list` | Validation errors list |

### Layout Component (Layout.css)

| Class | Purpose |
|-------|---------|
| `.layout-container` | Main layout wrapper |
| `.layout-sider` | Sidebar styling |
| `.layout-logo` | Logo container |
| `.layout-logo-icon` | Logo icon |
| `.layout-header` | Header styling |
| `.layout-header-left` | Header left section |
| `.layout-header-title` | Header title |
| `.layout-mobile-menu-button` | Mobile menu button |
| `.layout-user-menu` | User menu dropdown |
| `.layout-content` | Main content area |
| `.layout-footer` | Footer styling |

### Login Page (Login.css)

| Class | Purpose |
|-------|---------|
| `.login-container` | Main login wrapper |
| `.login-row` | Row layout |
| `.login-branding` | Branding section |
| `.login-branding-icon` | Brand icon |
| `.login-branding-title` | Brand title |
| `.login-branding-subtitle` | Brand subtitle |
| `.login-feature` | Feature item |
| `.login-feature-icon` | Feature icon |
| `.login-feature-title` | Feature title |
| `.login-feature-text` | Feature text |
| `.login-card` | Card styling |
| `.login-title` | Form title |
| `.login-subtitle` | Form subtitle |
| `.login-form` | Form wrapper |
| `.login-form-note` | Form note text |
| `.login-back-button` | Back button |
| `.login-otp-container` | OTP inputs container |
| `.login-otp-input` | Individual OTP input |
| `.login-resend` | Resend section |
| `.login-resend-button` | Resend button |

### Dashboard Page (Dashboard.css)

| Class | Purpose |
|-------|---------|
| `.dashboard-container` | Main wrapper |
| `.dashboard-banner` | Welcome banner |
| `.dashboard-banner-title` | Banner title |
| `.dashboard-banner-subtitle` | Banner subtitle |
| `.dashboard-welcome-card` | Welcome card |
| `.dashboard-welcome-icon` | Welcome icon |
| `.dashboard-welcome-title` | Welcome title |
| `.dashboard-welcome-text` | Welcome text |
| `.dashboard-services-title` | Services section title |
| `.dashboard-service-card` | Service card |
| `.dashboard-service-icon` | Service icon |
| `.dashboard-specialty-card` | Specialty card |
| `.dashboard-specialty-icon` | Specialty icon |
| `.dashboard-appointment-card` | Appointment card |
| `.dashboard-appointment-icon` | Appointment icon |
| `.dashboard-quick-action-card` | Quick action card |
| `.dashboard-quick-action-icon` | Quick action icon |

### Book Appointment Page (BookAppointment.css)

| Class | Purpose |
|-------|---------|
| `.booking-container` | Main wrapper |
| `.booking-steps-card` | Steps progress card |
| `.booking-content-card` | Content card |
| `.booking-actions-card` | Actions card |
| `.booking-specialty-card` | Specialty selection card |
| `.booking-specialty-card.selected` | Selected specialty |
| `.booking-specialty-icon` | Specialty icon |
| `.booking-specialty-title` | Specialty title |
| `.booking-doctor-card` | Doctor card |
| `.booking-doctor-card.selected` | Selected doctor |
| `.booking-doctor-avatar` | Doctor avatar |
| `.booking-doctor-name` | Doctor name |
| `.booking-doctor-qualification` | Doctor qualification |
| `.booking-doctor-info` | Doctor info |
| `.booking-time-slots-container` | Time slots container |
| `.booking-confirmation-info` | Confirmation info |
| `.booking-note-card` | Note card |
| `.booking-note-icon` | Note icon |

### Appointments Page (Appointments.css)

| Class | Purpose |
|-------|---------|
| `.appointments-container` | Main wrapper |
| `.appointments-header` | Page header |
| `.appointments-title` | Page title |
| `.appointments-subtitle` | Page subtitle |
| `.appointments-search` | Search input |
| `.appointments-tabs` | Tabs wrapper |
| `.appointment-card` | Appointment card |
| `.appointment-icon` | Appointment icon |
| `.appointment-title` | Appointment title |
| `.appointment-status-tag` | Status tag |
| `.appointment-doctor` | Doctor name |
| `.appointment-time-info` | Time information |
| `.appointment-location` | Location text |
| `.appointment-actions` | Actions section |
| `.appointment-action-button` | Action button |
| `.appointments-empty` | Empty state |
| `.appointment-cancel-modal-content` | Cancel modal content |

### Profile Page (Profile.css)

| Class | Purpose |
|-------|---------|
| `.profile-container` | Main wrapper |
| `.profile-header-card` | Header card |
| `.profile-header-avatar` | Avatar |
| `.profile-header-name` | Name |
| `.profile-header-phone` | Phone |
| `.profile-info-card` | Info card |
| `.profile-section-icon` | Section icon |
| `.profile-form` | Form wrapper |
| `.profile-family-card` | Family card |
| `.profile-family-description` | Family description |
| `.profile-family-empty` | Empty state |
| `.profile-family-list-item` | List item |
| `.profile-family-avatar` | Family avatar |
| `.profile-family-name` | Family name |
| `.profile-family-relationship` | Relationship |
| `.profile-family-dob` | Date of birth |
| `.profile-medical-card` | Medical history card |
| `.profile-medical-inner-card` | Inner card |
| `.profile-medical-title` | Section title |
| `.profile-medical-empty` | Empty state |
| `.profile-add-member-form` | Add member form |

---

## 🎨 CSS Variables & Theme

The project uses Ant Design's ConfigProvider for theming. Colors are defined in `main.jsx`:

```javascript
const theme = {
  token: {
    colorPrimary: '#1890ff',      // Primary blue
    colorSuccess: '#52c41a',      // Success green
    colorWarning: '#faad14',      // Warning orange
    colorError: '#ff4d4f',        // Error red
    colorInfo: '#1890ff',         // Info blue
    borderRadius: 8,              // Border radius
    fontSize: 14,                 // Base font size
  }
}
```

---

## 📱 Responsive Design

All CSS files include responsive breakpoints:

```css
/* Mobile */
@media (max-width: 768px) {
  /* Mobile styles */
}

/* Tablet */
@media (min-width: 768px) and (max-width: 992px) {
  /* Tablet styles */
}

/* Desktop */
@media (min-width: 992px) {
  /* Desktop styles */
}
```

---

## 🔧 Customization

### To modify a component's styles:

1. **Find the CSS file**: `src/styles/ComponentName.css`
2. **Update the styles**: Modify the relevant classes
3. **Test**: Changes are hot-reloaded by Vite

### To add new styles:

1. **Create new CSS file**: `src/styles/NewComponent.css`
2. **Import in component**: `import '../styles/NewComponent.css'`
3. **Apply classes**: Add `className` attributes to JSX elements

### Example:

**NewComponent.css**:
```css
.new-component-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.new-component-title {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}
```

**NewComponent.jsx**:
```javascript
import '../styles/NewComponent.css'

function NewComponent() {
  return (
    <div className="new-component-container">
      <h2 className="new-component-title">Title</h2>
    </div>
  )
}
```

---

## 💡 Best Practices

1. ✅ **Use semantic class names**: `.login-container`, not `.blue-box`
2. ✅ **One file per component**: Keep styles organized
3. ✅ **Avoid inline styles**: Use classes for maintainability
4. ✅ **Responsive first**: Design for mobile, enhance for desktop
5. ✅ **Leverage Ant Design**: Use their components and theme
6. ✅ **Consistent naming**: Use BEM-like convention
7. ✅ **Comment complex styles**: Explain why, not what

---

## 🚀 Build & Production

CSS files are automatically:
- ✅ Bundled by Vite
- ✅ Minified in production
- ✅ Optimized and tree-shaken
- ✅ Cache-busted with hashes

No additional configuration needed!

---

## 📚 Additional Resources

- [Ant Design Documentation](https://ant.design)
- [CSS Best Practices](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [Vite CSS Handling](https://vitejs.dev/guide/features.html#css)

---

**Your CSS is now fully modular and maintainable!** 🎨
