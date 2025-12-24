# Database Schema

PostgreSQL database for Medical Scheduling System.

## Setup
```bash
createdb medical_scheduling
psql medical_scheduling < schema.sql
```

## Tables

- `patients` - User accounts
- `doctors` - Doctor profiles
- `medical_fields` - Medical specialties
- `appointments` - Appointment bookings
- `otp_codes` - OTP verification codes
- `doctor_working_hours` - Doctor schedules

## Key Constraints

- `UNIQUE(doctor_id, appointment_time)` - Prevents double booking
- Foreign keys for referential integrity
- Check constraints for data validation