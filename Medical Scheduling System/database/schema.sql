-- Medical Scheduling System Database Schema
-- PostgreSQL 15+

-- Patients (Users)
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    time_zone VARCHAR(50) NOT NULL DEFAULT 'Asia/Jerusalem',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- -- OTP Codes
-- CREATE TABLE otp_codes (
--     id SERIAL PRIMARY KEY,
--     phone_number VARCHAR(20) NOT NULL,
--     otp_code VARCHAR(6) NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '5 minutes',
--     is_verified BOOLEAN DEFAULT false,
--     attempts INT DEFAULT 0
-- );

-- Medical Fields
CREATE TABLE medical_fields (
    id SERIAL PRIMARY KEY,
    medical_field_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Doctors
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    medical_field_id INT NOT NULL REFERENCES medical_fields(id),
    time_zone VARCHAR(50) NOT NULL DEFAULT 'Asia/Jerusalem',
    specialization VARCHAR(200),
    years_of_experience INT,
    rating DECIMAL(3,2) DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INT DEFAULT 0,
    bio TEXT,
    consultation_fee DECIMAL(10,2),
    image_url VARCHAR(255),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Doctor Working Hours
CREATE TABLE doctor_working_hours (
    id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration_minutes INT DEFAULT 30,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, day_of_week)
);

-- Appointments
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctors(id),
    medical_field_id INT NOT NULL REFERENCES medical_fields(id),
    appointment_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INT DEFAULT 30,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (
        status IN ('scheduled', 'confirmed', 'cancelled', 'completed', 'no_show')
    ),
    reason_for_visit TEXT,
    notes TEXT,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_doctor_time UNIQUE(doctor_id, appointment_time)
);

-- Indexes
CREATE INDEX idx_patients_phone ON patients(phone_number);
CREATE INDEX idx_otp_phone ON otp_codes(phone_number, is_verified);
CREATE INDEX idx_doctors_medical_field ON doctors(medical_field_id);
CREATE INDEX idx_doctors_available ON doctors(is_available);
CREATE INDEX idx_appointments_patient ON appointments(patient_id, appointment_time DESC);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id, appointment_time);
CREATE INDEX idx_appointments_status ON appointments(status);
