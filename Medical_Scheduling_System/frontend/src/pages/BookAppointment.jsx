import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Steps,
  Card,
  Row,
  Col,
  Button,
  Typography,
  Space,
  DatePicker,
  Input,
  Divider,
  message as antMessage,
  Rate,
  Skeleton,
  Empty,
} from 'antd'
import '../styles/BookAppointment.css'
import {
  MedicineBoxOutlined,
  UserOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons'
import { appointmentsAPI, medicalFieldsAPI, doctorsAPI } from '../services/api'
import { formatDate, formatTime } from '../utils/helpers'
import { resolveMedicalIconComponent } from '../utils/medicalIcons'
import dayjs from 'dayjs'
import { useAuthStore } from '../store/authStore'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input
const { Step } = Steps

const BookAppointment = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)

  // data loading
  const [loadingFields, setLoadingFields] = useState(false)
  const [loadingDoctors, setLoadingDoctors] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)

  // fetched data
  const [specialties, setSpecialties] = useState([])
  const [doctors, setDoctors] = useState([])
  const [timeSlots, setTimeSlots] = useState([]) // [{start_time,end_time,available}]

  const [formData, setFormData] = useState({
    specialtyId: null,
    doctorId: null,
    date: null, // YYYY-MM-DD
    timeSlotISO: null, // slot.start_time ISO
    notes: '',
  })

  const navigate = useNavigate()
  const patientId = useAuthStore((s) => s.patientId)

  const steps = useMemo(
    () => [
      { title: 'Choose Specialty', icon: <MedicineBoxOutlined /> },
      { title: 'Select Doctor', icon: <UserOutlined /> },
      { title: 'Pick Date & Time', icon: <CalendarOutlined /> },
      { title: 'Confirm', icon: <CheckCircleOutlined /> },
    ],
    []
  )

  const selectedSpecialty = useMemo(
    () => specialties.find((s) => s.id === formData.specialtyId) || null,
    [specialties, formData.specialtyId]
  )

  const selectedDoctor = useMemo(
    () => doctors.find((d) => d.id === formData.doctorId) || null,
    [doctors, formData.doctorId]
  )

  const SelectedSpecialtyIcon = useMemo(() => {
    const Icon = resolveMedicalIconComponent(selectedSpecialty?.icon, selectedSpecialty?.name)
    return Icon || MedicineBoxOutlined
  }, [selectedSpecialty?.icon, selectedSpecialty?.name])

  // load specialties
  useEffect(() => {
    const loadFields = async () => {
      setLoadingFields(true)
      try {
        const res = await medicalFieldsAPI.getAll()
        const rows = Array.isArray(res?.data) ? res.data : []

        setSpecialties(
          rows
            .filter((f) => f?.is_active !== false)
            .map((f) => ({
              id: f.id,
              name: f.medical_field_name ?? `Field ${f.id}`,
              description: f.description ?? '',
              icon: f.icon ?? null,
            }))
        )
      } catch (e) {
        antMessage.error('Failed to load medical fields')
      } finally {
        setLoadingFields(false)
      }
    }

    loadFields()
  }, [])

  // load doctors when specialty changes
  useEffect(() => {
    const loadDoctors = async () => {
      if (!formData.specialtyId) {
        setDoctors([])
        return
      }

      setLoadingDoctors(true)
      try {
        const res = await doctorsAPI.getBySpecialty(formData.specialtyId)
        const rows = Array.isArray(res?.data) ? res.data : []

        setDoctors(
          rows.map((d) => ({
            id: d.id,
            name: d.name ?? `Doctor ${d.id}`,
            medical_field_id: d.medical_field_id,
            medical_field_name: d.medical_field_name,
            specialization: d.specialization ?? '',
            years_of_experience: d.years_of_experience ?? null,
            rating: typeof d.rating === 'number' ? d.rating : null,
            total_reviews: d.total_reviews ?? null,
            consultation_fee: d.consultation_fee ?? null,
            image_url: d.image_url ?? null,
          }))
        )

        // reset doctor/date/slot when specialty changes
        setFormData((p) => ({ ...p, doctorId: null, date: null, timeSlotISO: null }))
        setTimeSlots([])
      } catch (e) {
        antMessage.error('Failed to load doctors')
        setDoctors([])
      } finally {
        setLoadingDoctors(false)
      }
    }

    loadDoctors()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.specialtyId])

  // load slots when doctor + date chosen
  useEffect(() => {
    const loadSlots = async () => {
      if (!formData.doctorId || !formData.date) {
        setTimeSlots([])
        return
      }

      setLoadingSlots(true)
      try {
        const res = await doctorsAPI.getAvailableSlots(formData.doctorId, formData.date)
        const slots = Array.isArray(res?.data?.available_slots) ? res.data.available_slots : []

        const normalized = slots
          .filter((s) => s?.start_time)
          .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())

        setTimeSlots(normalized)

        // clear chosen slot if it disappeared
        setFormData((p) => {
          if (p.timeSlotISO && !normalized.some((s) => s.start_time === p.timeSlotISO)) {
            return { ...p, timeSlotISO: null }
          }
          return p
        })
      } catch (e) {
        antMessage.error('Failed to load available slots')
        setTimeSlots([])
      } finally {
        setLoadingSlots(false)
      }
    }

    loadSlots()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.doctorId, formData.date])

  const handleNext = () => {
    if (currentStep < 3) setCurrentStep((s) => s + 1)
  }

  const handleBack = () => {
    if (currentStep > 0) setCurrentStep((s) => s - 1)
  }

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return formData.specialtyId !== null
      case 1:
        return formData.doctorId !== null
      case 2:
        return Boolean(formData.date && formData.timeSlotISO)
      default:
        return true
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      if (!formData.doctorId || !formData.specialtyId || !formData.date || !formData.timeSlotISO) {
        antMessage.error('Missing appointment details')
        return
      }

      if (!patientId || Number.isNaN(patientId)) {
        antMessage.error('Missing patient id. Please login again.')
        navigate('/login')
        return
      }

      const appointmentTimeISO = dayjs(formData.timeSlotISO).second(0).millisecond(0).toISOString()

      await appointmentsAPI.create({
        patient_id: patientId,
        doctor_id: formData.doctorId,
        medical_field_id: formData.specialtyId,
        appointment_time: appointmentTimeISO,
        duration_minutes: 30,
        reason_for_visit: formData.notes?.trim() || null,
      })

      antMessage.success('Appointment booked successfully!')
      navigate('/dashboard')
    } catch (error) {
      const status = error?.response?.status
      const detail = error?.response?.data?.detail

      if (status === 401) antMessage.error('Unauthorized. Please log in again.')
      else if (status === 404) antMessage.error(detail || 'Doctor not found.')
      else if (status === 409) antMessage.error(detail || 'This time slot is already booked.')
      else antMessage.error(detail || 'Failed to book appointment')
    } finally {
      setLoading(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: {
        return (
          <div>
            <Title level={4} style={{ marginBottom: 24 }}>
              Choose Your Specialty
            </Title>

            {loadingFields ? (
              <Skeleton active />
            ) : specialties.length === 0 ? (
              <Empty description="No specialties found" />
            ) : (
              <Row gutter={[16, 16]}>
                {specialties.map((specialty) => {
                  const isSelected = formData.specialtyId === specialty.id
                  const Icon = resolveMedicalIconComponent(specialty.icon, specialty.name) || MedicineBoxOutlined

                  return (
                    <Col xs={24} sm={12} lg={8} key={specialty.id}>
                      <Card
                        hoverable
                        onClick={() => setFormData((p) => ({ ...p, specialtyId: specialty.id }))}
                        style={{ border: isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9' }}
                      >
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Space align="center">
                            <span style={{ fontSize: 22 }}>
                              <Icon />
                            </span>
                            <Title level={5} style={{ margin: 0 }}>
                              {specialty.name}
                            </Title>
                          </Space>
                          {specialty.description ? <Text type="secondary">{specialty.description}</Text> : null}
                        </Space>
                      </Card>
                    </Col>
                  )
                })}
              </Row>
            )}
          </div>
        )
      }

      case 1: {
        return (
          <div>
            <Space style={{ marginBottom: 24 }} align="center">
              <span style={{ fontSize: 22 }}>
                <SelectedSpecialtyIcon />
              </span>
              <div>
                <Title level={4} style={{ margin: 0 }}>
                  Select Your Doctor
                </Title>
                <Text type="secondary">{selectedSpecialty?.name || 'Specialty'}</Text>
              </div>
            </Space>

            {loadingDoctors ? (
              <Skeleton active />
            ) : doctors.length === 0 ? (
              <Empty description="No doctors found for this specialty" />
            ) : (
              <Row gutter={[16, 16]}>
                {doctors.map((doctor) => (
                  <Col xs={24} lg={12} key={doctor.id}>
                    <Card
                      hoverable
                      onClick={() =>
                        setFormData((p) => ({ ...p, doctorId: doctor.id, date: null, timeSlotISO: null }))
                      }
                      style={{
                        border: formData.doctorId === doctor.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
                      }}
                    >
                      <Row gutter={16}>
                        <Col span={4}>
                          <div
                            style={{
                              width: 60,
                              height: 60,
                              borderRadius: '50%',
                              background: '#1890ff',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: '#fff',
                              fontSize: 24,
                            }}
                          >
                            <UserOutlined />
                          </div>
                        </Col>

                        <Col span={20}>
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <Title level={5} style={{ margin: 0 }}>
                              {doctor.name}
                            </Title>

                            {doctor.specialization ? <Text type="secondary">{doctor.specialization}</Text> : null}

                            <Space split={<Divider type="vertical" />}>
                              {doctor.years_of_experience != null ? (
                                <Text type="secondary">{doctor.years_of_experience} yrs</Text>
                              ) : (
                                <Text type="secondary">—</Text>
                              )}

                              {typeof doctor.rating === 'number' ? (
                                <Space size="small">
                                  <Rate disabled value={doctor.rating} allowHalf />
                                  <Text type="secondary">({doctor.rating})</Text>
                                </Space>
                              ) : (
                                <Text type="secondary">No rating</Text>
                              )}
                            </Space>

                            {doctor.consultation_fee != null ? (
                              <Text type="secondary">₪{doctor.consultation_fee}</Text>
                            ) : null}
                          </Space>
                        </Col>
                      </Row>
                    </Card>
                  </Col>
                ))}
              </Row>
            )}
          </div>
        )
      }

      case 2: {
        return (
          <div>
            <Title level={4} style={{ marginBottom: 24 }}>
              Pick Your Date & Time
            </Title>

            <Row gutter={[24, 24]}>
              <Col xs={24} md={12}>
                <Card title="Select Date">
                  <DatePicker
                    size="large"
                    style={{ width: '100%' }}
                    getPopupContainer={() => document.body}
                    popupStyle={{ zIndex: 2000 }}
                    disabled={!formData.doctorId}
                    disabledDate={(current) => current && current < dayjs().startOf('day')}
                    value={formData.date ? dayjs(formData.date, 'YYYY-MM-DD') : null}
                    onChange={(date) =>
                      setFormData((p) => ({
                        ...p,
                        date: date?.format('YYYY-MM-DD') || null,
                        timeSlotISO: null,
                      }))
                    }
                  />
                  {!formData.doctorId ? (
                    <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                      Select a doctor first
                    </Text>
                  ) : null}
                </Card>
              </Col>

              <Col xs={24} md={12}>
                <Card title="Available Time Slots">
                  {!formData.doctorId || !formData.date ? (
                    <Empty description="Select doctor + date to see slots" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                  ) : loadingSlots ? (
                    <Skeleton active />
                  ) : timeSlots.length === 0 ? (
                    <Empty description="No available slots" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                  ) : (
                    <div style={{ maxHeight: 300, overflow: 'auto' }}>
                      <Row gutter={[8, 8]}>
                        {timeSlots.map((slot) => {
                          const iso = slot.start_time
                          const selected = formData.timeSlotISO === iso
                          const disabled = slot.available === false

                          return (
                            <Col span={8} key={iso}>
                              <Button
                                type={selected ? 'primary' : 'default'}
                                block
                                disabled={disabled}
                                onClick={() => setFormData((p) => ({ ...p, timeSlotISO: iso }))}
                              >
                                {formatTime(dayjs(iso).format('HH:mm'))}
                              </Button>
                            </Col>
                          )
                        })}
                      </Row>
                    </div>
                  )}
                </Card>
              </Col>
            </Row>

            <Card title="Additional Notes (Optional)" style={{ marginTop: 24 }}>
              <TextArea
                rows={4}
                placeholder="Any specific concerns or symptoms you'd like to mention..."
                value={formData.notes}
                onChange={(e) => setFormData((p) => ({ ...p, notes: e.target.value }))}
              />
            </Card>
          </div>
        )
      }

      case 3: {
        const chosenTime = formData.timeSlotISO ? dayjs(formData.timeSlotISO).format('HH:mm') : null

        return (
          <div>
            <Title level={4} style={{ marginBottom: 24 }}>
              Confirm Your Appointment
            </Title>

            <Card>
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Specialty</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {selectedSpecialty?.name || '-'}
                    </Title>
                  </Space>
                </Col>

                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Doctor</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {selectedDoctor?.name || '-'}
                    </Title>
                  </Space>
                </Col>

                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Date</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {formData.date ? formatDate(formData.date, 'dddd, MMMM DD, YYYY') : '-'}
                    </Title>
                  </Space>
                </Col>

                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Time</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {chosenTime ? formatTime(chosenTime) : '-'}
                    </Title>
                  </Space>
                </Col>

                {formData.notes?.trim() ? (
                  <Col span={24}>
                    <Divider />
                    <Space direction="vertical" size="small">
                      <Text type="secondary">Notes</Text>
                      <Paragraph>{formData.notes}</Paragraph>
                    </Space>
                  </Col>
                ) : null}
              </Row>
            </Card>

            <Card style={{ marginTop: 16, background: '#e6f7ff', borderColor: '#91d5ff' }}>
              <Space>
                <CheckCircleOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                <Text>
                  <strong>Note:</strong> Please arrive 15 minutes before your scheduled appointment time. Bring your ID
                  and any relevant medical records.
                </Text>
              </Space>
            </Card>
          </div>
        )
      }

      default:
        return null
    }
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <Steps current={currentStep}>
          {steps.map((step) => (
            <Step key={step.title} title={step.title} icon={step.icon} />
          ))}
        </Steps>
      </Card>

      <Card>{renderStepContent()}</Card>

      <Card>
        <Row justify="space-between">
          <Col>
            <Button icon={<ArrowLeftOutlined />} onClick={handleBack} disabled={currentStep === 0} size="large">
              Back
            </Button>
          </Col>

          <Col>
            {currentStep < 3 ? (
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                onClick={handleNext}
                disabled={!canProceed()}
                size="large"
              >
                Next
              </Button>
            ) : (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleSubmit}
                loading={loading}
                size="large"
              >
                Confirm Booking
              </Button>
            )}
          </Col>
        </Row>
      </Card>
    </Space>
  )
}

export default BookAppointment
