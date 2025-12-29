-- ============================================
-- seed_data.sql (RUN ONCE AFTER schema.sql)
-- Medical Scheduling System - Seed Data
-- PostgreSQL 15+
--
-- Usage:
--   psql medical_scheduling < seed_data.sql
-- ============================================

BEGIN;

-- ============================================
-- BASE MEDICAL FIELDS
-- ============================================
INSERT INTO medical_fields (medical_field_name, description, icon) VALUES
('Cardiology', 'Heart and cardiovascular system', 'heart'),
('Pediatrics', 'Children and adolescent care', 'baby'),
('Dermatology', 'Skin, hair, and nail conditions', 'skin'),
('Orthopedics', 'Bones, joints, and muscles', 'bone'),
('Neurology', 'Brain and nervous system', 'brain'),
('General Practice', 'Primary and family care', 'stethoscope')
ON CONFLICT (medical_field_name) DO NOTHING;

-- ============================================
-- ADDITIONAL MEDICAL FIELDS
-- ============================================
INSERT INTO medical_fields (medical_field_name, description, icon) VALUES
('Ophthalmology', 'Eye care and vision', 'eye'),
('Dentistry', 'Dental and oral health', 'tooth'),
('Psychiatry', 'Mental health and therapy', 'brain'),
('Emergency Medicine', 'Urgent and emergency care', 'ambulance')
ON CONFLICT (medical_field_name) DO NOTHING;

-- ============================================
-- BASE DOCTORS
-- NOTE: assumes medical_fields were created in order 1..6 in a fresh DB
-- ============================================
INSERT INTO doctors (name, medical_field_id, specialization, years_of_experience, rating, consultation_fee) VALUES
('Dr. Sarah Cohen', 1, 'Interventional Cardiology', 15, 4.8, 350.00),
('Dr. David Levi', 1, 'Cardiac Surgery', 20, 4.9, 400.00),
('Dr. Rachel Goldstein', 2, 'General Pediatrics', 12, 4.7, 280.00),
('Dr. Michael Shapiro', 3, 'Medical Dermatology', 8, 4.6, 300.00),
('Dr. Emma Friedman', 4, 'Sports Medicine', 10, 4.8, 320.00);

-- ============================================
-- MORE DOCTORS
-- NOTE: assumes medical_fields ids 1..10 exist in a fresh DB
-- ============================================
INSERT INTO doctors (
    name,
    medical_field_id,
    specialization,
    years_of_experience,
    rating,
    total_reviews,
    consultation_fee,
    bio,
    time_zone
) VALUES
-- Cardiology (field_id = 1)
('Dr. Ahmed Hassan', 1, 'Preventive Cardiology', 12, 4.6, 45, 320.00,
 'Focuses on heart disease prevention and lifestyle management', 'Asia/Jerusalem'),

('Dr. Jennifer Lee', 1, 'Pediatric Cardiology', 16, 4.9, 67, 380.00,
 'Specialist in children''s heart conditions', 'Asia/Jerusalem'),

-- Pediatrics (field_id = 2)
('Dr. Lisa Wong', 2, 'Adolescent Medicine', 9, 4.8, 89, 290.00,
 'Specializes in teenage health and development', 'Asia/Jerusalem'),

('Dr. Mark Thompson', 2, 'Neonatology', 18, 4.7, 52, 350.00,
 'Expert in newborn intensive care', 'Asia/Jerusalem'),

-- Dermatology (field_id = 3)
('Dr. Sophia Martinez', 3, 'Cosmetic Dermatology', 11, 4.5, 78, 400.00,
 'Aesthetic treatments and anti-aging procedures', 'Asia/Jerusalem'),

-- Orthopedics (field_id = 4)
('Dr. Robert Taylor', 4, 'Joint Replacement', 22, 4.9, 134, 450.00,
 'Over 1500 successful joint replacement surgeries', 'Asia/Jerusalem'),

('Dr. Nina Patel', 4, 'Sports Injuries', 13, 4.8, 98, 380.00,
 'Specialist in sports medicine and rehabilitation', 'Asia/Jerusalem'),

-- Neurology (field_id = 5)
('Dr. John Smith', 5, 'Clinical Neurology', 18, 4.9, 112, 380.00,
 'Expert in stroke treatment and epilepsy', 'Asia/Jerusalem'),

('Dr. Elena Rodriguez', 5, 'Movement Disorders', 14, 4.7, 76, 360.00,
 'Specialist in Parkinson''s and tremor disorders', 'Asia/Jerusalem'),

-- General Practice (field_id = 6)
('Dr. Maria Garcia', 6, 'Family Medicine', 14, 4.7, 156, 250.00,
 'Comprehensive primary care for all ages', 'Asia/Jerusalem'),

('Dr. James Wilson', 6, 'Geriatric Medicine', 20, 4.6, 89, 280.00,
 'Focused on elderly patient care', 'Asia/Jerusalem'),

-- Ophthalmology (field_id = 7)
('Dr. Sarah Kim', 7, 'Cataract Surgery', 17, 4.8, 145, 420.00,
 'Specialist in laser eye surgery and cataracts', 'Asia/Jerusalem'),

-- Dentistry (field_id = 8)
('Dr. Michael Brown', 8, 'General Dentistry', 10, 4.5, 203, 200.00,
 'Family dentist with focus on preventive care', 'Asia/Jerusalem'),

('Dr. Laura Green', 8, 'Orthodontics', 15, 4.9, 167, 350.00,
 'Braces and teeth alignment specialist', 'Asia/Jerusalem'),

-- Psychiatry (field_id = 9)
('Dr. Daniel Cohen', 9, 'Adult Psychiatry', 19, 4.7, 92, 400.00,
 'Depression, anxiety, and mood disorders', 'Asia/Jerusalem'),

-- Emergency Medicine (field_id = 10)
('Dr. Anna White', 10, 'Emergency Medicine', 12, 4.6, 78, 500.00,
 'ER specialist available for urgent care', 'Asia/Jerusalem');

-- ============================================
-- DOCTOR WORKING HOURS
-- Add "random-ish" hours for every doctor/day if missing.
-- This makes the seed file safe and complete in one run.
--
-- Using ON CONFLICT DO NOTHING because of UNIQUE(doctor_id, day_of_week)
-- ============================================

-- Sun–Thu (Israel work week): 0..4
INSERT INTO doctor_working_hours (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, is_active)
SELECT
  d.id,
  dow.day_of_week,

  -- start: 08:00/09:00/10:00/11:00
  (TIME '08:00' + (floor(random() * 4)::int * INTERVAL '1 hour'))::time AS start_time,

  -- end: start + (4..7) hours
  (
    (TIME '08:00' + (floor(random() * 4)::int * INTERVAL '1 hour'))
    + ((4 + floor(random() * 4))::int * INTERVAL '1 hour')
  )::time AS end_time,

  -- duration: 15/20/30/45/60
  (ARRAY[15, 20, 30, 45, 60])[1 + floor(random() * 5)::int] AS slot_duration_minutes,

  true
FROM doctors d
CROSS JOIN (VALUES (0),(1),(2),(3),(4)) AS dow(day_of_week)
ON CONFLICT (doctor_id, day_of_week) DO NOTHING;

-- ============================================
-- TEST PATIENTS
-- ============================================
INSERT INTO patients (phone_number, full_name, email, date_of_birth, gender, time_zone) VALUES
('0501111111', 'Alice Johnson', 'alice.j@example.com', '1985-03-15', 'female', 'Asia/Jerusalem'),
('0502222222', 'Bob Smith', 'bob.smith@example.com', '1990-07-22', 'male', 'Asia/Jerusalem'),
('0503333333', 'Charlie Brown', 'charlie.b@example.com', '1978-11-30', 'male', 'Asia/Jerusalem'),
('0504444444', 'Diana Prince', 'diana.p@example.com', '1988-05-18', 'female', 'Asia/Jerusalem'),
('0505555555', 'Eve Martinez', 'eve.m@example.com', '1995-09-25', 'female', 'Asia/Jerusalem'),
('0506666666', 'Frank Wilson', 'frank.w@example.com', '1982-12-08', 'male', 'Asia/Jerusalem'),
('0507777777', 'Grace Lee', 'grace.l@example.com', '1991-04-14', 'female', 'Asia/Jerusalem'),
('0508888888', 'Henry Taylor', 'henry.t@example.com', '1975-06-20', 'male', 'Asia/Jerusalem'),
('0509999999', 'Iris Chen', 'iris.c@example.com', '1993-08-10', 'female', 'Asia/Jerusalem'),
('0500000000', 'Jack Davis', 'jack.d@example.com', '1987-02-28', 'male', 'Asia/Jerusalem')
ON CONFLICT (phone_number) DO NOTHING;

-- ============================================
-- SAMPLE APPOINTMENTS
-- NOTE: these assume patient ids 1..10 and doctor ids exist in a fresh DB.
-- ============================================

-- Future (Upcoming)
INSERT INTO appointments (
    patient_id, doctor_id, medical_field_id, appointment_time, duration_minutes, status, reason_for_visit
) VALUES
(1, 1, 1, NOW() + INTERVAL '1 day' + TIME '10:00:00', 30, 'scheduled', 'Regular heart checkup'),
(2, 3, 2, NOW() + INTERVAL '1 day' + TIME '11:00:00', 30, 'scheduled', 'Child vaccination'),
(3, 6, 1, NOW() + INTERVAL '1 day' + TIME '14:00:00', 30, 'scheduled', 'Follow-up consultation'),

(4, 8, 2, NOW() + INTERVAL '2 days' + TIME '09:00:00', 30, 'scheduled', 'Teenage health consultation'),
(5, 10, 3, NOW() + INTERVAL '2 days' + TIME '15:00:00', 60, 'scheduled', 'Cosmetic consultation'),
(1, 15, 6, NOW() + INTERVAL '2 days' + TIME '08:30:00', 20, 'confirmed', 'Annual physical exam'),

(6, 11, 4, NOW() + INTERVAL '3 days' + TIME '10:00:00', 45, 'scheduled', 'Knee pain evaluation'),
(7, 13, 5, NOW() + INTERVAL '3 days' + TIME '16:00:00', 45, 'scheduled', 'Headache consultation'),
(8, 18, 8, NOW() + INTERVAL '3 days' + TIME '11:00:00', 30, 'scheduled', 'Dental cleaning'),

(9, 17, 7, NOW() + INTERVAL '5 days' + TIME '14:00:00', 30, 'scheduled', 'Vision test'),
(10, 20, 9, NOW() + INTERVAL '5 days' + TIME '10:00:00', 60, 'scheduled', 'Mental health consultation'),

(1, 7, 1, NOW() + INTERVAL '7 days' + TIME '11:00:00', 45, 'scheduled', 'Cardiology follow-up'),
(2, 9, 2, NOW() + INTERVAL '7 days' + TIME '09:30:00', 30, 'scheduled', 'Newborn checkup'),
(3, 12, 4, NOW() + INTERVAL '7 days' + TIME '15:00:00', 30, 'scheduled', 'Sports injury consultation'),

(4, 19, 8, NOW() + INTERVAL '10 days' + TIME '13:00:00', 60, 'scheduled', 'Orthodontic consultation'),
(5, 14, 5, NOW() + INTERVAL '10 days' + TIME '10:00:00', 30, 'scheduled', 'Movement disorder evaluation')
ON CONFLICT DO NOTHING;

-- Past (Historical)
INSERT INTO appointments (
    patient_id, doctor_id, medical_field_id, appointment_time, duration_minutes, status, reason_for_visit, notes
) VALUES
(1, 1, 1, NOW() - INTERVAL '14 days' + TIME '10:00:00', 30, 'completed', 'Annual checkup', 'All tests normal. Patient healthy.'),
(2, 3, 2, NOW() - INTERVAL '14 days' + TIME '14:00:00', 30, 'completed', 'Well-child visit', 'Child developing normally.'),

(3, 4, 3, NOW() - INTERVAL '7 days' + TIME '11:00:00', 30, 'completed', 'Skin rash', 'Prescribed topical cream.'),
(4, 5, 4, NOW() - INTERVAL '7 days' + TIME '15:00:00', 30, 'completed', 'Back pain', 'Recommended physical therapy.'),
(5, 15, 6, NOW() - INTERVAL '7 days' + TIME '09:00:00', 20, 'completed', 'Flu symptoms', 'Prescribed rest and fluids.'),

(6, 18, 8, NOW() - INTERVAL '5 days' + TIME '10:00:00', 30, 'completed', 'Tooth cleaning', 'No cavities found.'),
(7, 13, 5, NOW() - INTERVAL '5 days' + TIME '16:00:00', 45, 'completed', 'Migraine evaluation', 'Prescribed medication.'),

(8, 17, 7, NOW() - INTERVAL '3 days' + TIME '11:00:00', 30, 'completed', 'Eye examination', 'Updated prescription.'),
(9, 1, 1, NOW() - INTERVAL '3 days' + TIME '14:00:00', 30, 'no_show', 'Chest pain', NULL),

(10, 15, 6, NOW() - INTERVAL '1 day' + TIME '10:00:00', 20, 'completed', 'Blood pressure check', 'BP slightly elevated. Follow up in 3 months.'),

(1, 6, 1, NOW() - INTERVAL '10 days' + TIME '10:00:00', 30, 'cancelled', 'Follow-up', NULL),
(2, 8, 2, NOW() - INTERVAL '5 days' + TIME '11:00:00', 30, 'cancelled', 'Checkup', NULL),
(3, 10, 3, NOW() + INTERVAL '1 day' + TIME '16:00:00', 60, 'cancelled', 'Cosmetic procedure', NULL)
ON CONFLICT DO NOTHING;

-- ============================================
-- SUMMARY
-- ============================================
DO $$
DECLARE
    field_count INT;
    doctor_count INT;
    patient_count INT;
    appointment_count INT;
    upcoming_count INT;
    hours_count INT;
BEGIN
    SELECT COUNT(*) INTO field_count FROM medical_fields;
    SELECT COUNT(*) INTO doctor_count FROM doctors;
    SELECT COUNT(*) INTO patient_count FROM patients;
    SELECT COUNT(*) INTO appointment_count FROM appointments;
    SELECT COUNT(*) INTO upcoming_count FROM appointments WHERE appointment_time > NOW();
    SELECT COUNT(*) INTO hours_count FROM doctor_working_hours;

    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'SEED DATA LOADED SUCCESSFULLY!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Medical Fields: %', field_count;
    RAISE NOTICE 'Doctors: %', doctor_count;
    RAISE NOTICE 'Doctor working hours rows: %', hours_count;
    RAISE NOTICE 'Patients: %', patient_count;
    RAISE NOTICE 'Total Appointments: %', appointment_count;
    RAISE NOTICE 'Upcoming Appointments: %', upcoming_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
END $$;

COMMIT;
