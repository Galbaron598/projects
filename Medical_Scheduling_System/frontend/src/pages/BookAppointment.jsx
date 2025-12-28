import { useState } from 'react'
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
  Tag,
  Divider,
  message as antMessage,
  Rate,
} from 'antd'
import "../styles/BookAppointment.css"
import {
  MedicineBoxOutlined,
  UserOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  HeartOutlined,
  ExperimentOutlined,
  ApiOutlined,
  EyeOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons'
import { appointmentsAPI } from '../services/api'
import { formatDate, formatTime, delay } from '../utils/helpers'
import dayjs from 'dayjs'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input
const { Step } = Steps

const BookAppointment = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    specialtyId: null,
    doctorId: null,
    date: null,
    timeSlot: null,
    notes: '',
  })
  const navigate = useNavigate()

  // Mock data
  const specialties = [
    {
      id: 1,
      name: 'Cardiology',
      icon: <HeartOutlined />,
      description: 'Heart & cardiovascular care',
      doctors: 5,
      color: '#ff4d4f'
    },
    {
      id: 2,
      name: 'Neurology',
      icon: <ExperimentOutlined />,
      description: 'Brain & nervous system',
      doctors: 4,
      color: '#722ed1'
    },
    {
      id: 3,
      name: 'Orthopedics',
      icon: <ApiOutlined />,
      description: 'Bones & joints',
      doctors: 6,
      color: '#1890ff'
    },
    {
      id: 4,
      name: 'Pediatrics',
      icon: <UserOutlined />,
      description: 'Children\'s health',
      doctors: 7,
      color: '#eb2f96'
    },
    {
      id: 5,
      name: 'Ophthalmology',
      icon: <EyeOutlined />,
      description: 'Eye care',
      doctors: 3,
      color: '#13c2c2'
    },
    {
      id: 6,
      name: 'General Medicine',
      icon: <MedicineBoxOutlined />,
      description: 'Primary care',
      doctors: 8,
      color: '#52c41a'
    },
  ]

  const doctors = [
    {
      id: 1,
      name: 'Dr. Sarah Johnson',
      specialtyId: 1,
      experience: '15 years',
      rating: 4.9,
      patients: 2500,
      qualification: 'MD, FACC'
    },
    {
      id: 2,
      name: 'Dr. Michael Chen',
      specialtyId: 1,
      experience: '12 years',
      rating: 4.8,
      patients: 2100,
      qualification: 'MD, FACP'
    },
    {
      id: 3,
      name: 'Dr. Emily Rodriguez',
      specialtyId: 2,
      experience: '18 years',
      rating: 4.9,
      patients: 3000,
      qualification: 'MD, PhD'
    },
    {
      id: 4,
      name: 'Dr. James Wilson',
      specialtyId: 3,
      experience: '20 years',
      rating: 5.0,
      patients: 3500,
      qualification: 'MD, FAAOS'
    },
  ]

  const timeSlots = [
    '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
  ]

  const steps = [
    {
      title: 'Choose Specialty',
      icon: <MedicineBoxOutlined />,
    },
    {
      title: 'Select Doctor',
      icon: <UserOutlined />,
    },
    {
      title: 'Pick Date & Time',
      icon: <CalendarOutlined />,
    },
    {
      title: 'Confirm',
      icon: <CheckCircleOutlined />,
    },
  ]

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await delay(1500)
      
      // Uncomment for real API
      // await appointmentsAPI.create({
      //   specialtyId: formData.specialtyId,
      //   doctorId: formData.doctorId,
      //   date: formData.date,
      //   time: formData.timeSlot,
      //   notes: formData.notes,
      // })
      
      antMessage.success('Appointment booked successfully!')
      navigate('/dashboard')
    } catch (error) {
      antMessage.error('Failed to book appointment')
    } finally {
      setLoading(false)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return formData.specialtyId !== null
      case 1:
        return formData.doctorId !== null
      case 2:
        return formData.date && formData.timeSlot
      default:
        return true
    }
  }

  const selectedSpecialty = specialties.find((s) => s.id === formData.specialtyId)
  const selectedDoctor = doctors.find((d) => d.id === formData.doctorId)
  const filteredDoctors = doctors.filter((d) => d.specialtyId === formData.specialtyId)

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div>
            <Title level={4} style={{ marginBottom: 24 }}>
              Choose Your Specialty
            </Title>
            <Row gutter={[16, 16]}>
              {specialties.map((specialty) => (
                <Col xs={24} sm={12} lg={8} key={specialty.id}>
                  <Card
                    hoverable
                    className={formData.specialtyId === specialty.id ? 'card-selected' : ''}
                    onClick={() => setFormData({ ...formData, specialtyId: specialty.id })}
                    style={{
                      border:
                        formData.specialtyId === specialty.id
                          ? '2px solid #1890ff'
                          : '1px solid #d9d9d9',
                    }}
                  >
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <div style={{ fontSize: 36, color: specialty.color }}>
                        {specialty.icon}
                      </div>
                      <Title level={5} style={{ marginBottom: 4 }}>
                        {specialty.name}
                      </Title>
                      <Text type="secondary">{specialty.description}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {specialty.doctors} doctors available
                      </Text>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        )

      case 1:
        return (
          <div>
            <Space style={{ marginBottom: 24 }}>
              {selectedSpecialty && (
                <>
                  <div style={{ fontSize: 24, color: selectedSpecialty.color }}>
                    {selectedSpecialty.icon}
                  </div>
                  <div>
                    <Title level={4} style={{ margin: 0 }}>
                      Select Your Doctor
                    </Title>
                    <Text type="secondary">{selectedSpecialty.name} Specialists</Text>
                  </div>
                </>
              )}
            </Space>
            <Row gutter={[16, 16]}>
              {filteredDoctors.map((doctor) => (
                <Col xs={24} lg={12} key={doctor.id}>
                  <Card
                    hoverable
                    onClick={() => setFormData({ ...formData, doctorId: doctor.id })}
                    style={{
                      border:
                        formData.doctorId === doctor.id
                          ? '2px solid #1890ff'
                          : '1px solid #d9d9d9',
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
                          <Text type="secondary">{doctor.qualification}</Text>
                          <Space split={<Divider type="vertical" />}>
                            <Text type="secondary">{doctor.experience}</Text>
                            <Space size="small">
                              <Rate disabled defaultValue={doctor.rating} />
                              <Text type="secondary">({doctor.rating})</Text>
                            </Space>
                          </Space>
                          <Text type="secondary">
                            {doctor.patients.toLocaleString()} patients treated
                          </Text>
                        </Space>
                      </Col>
                    </Row>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        )

      case 2:
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
                    disabledDate={(current) =>
                      current && current < dayjs().startOf('day')
                    }
                    onChange={(date) =>
                      setFormData({ ...formData, date: date?.format('YYYY-MM-DD') })
                    }
                  />
                </Card>
              </Col>
              <Col xs={24} md={12}>
                <Card title="Available Time Slots">
                  <div style={{ maxHeight: 300, overflow: 'auto' }}>
                    <Row gutter={[8, 8]}>
                      {timeSlots.map((slot) => (
                        <Col span={8} key={slot}>
                          <Button
                            type={formData.timeSlot === slot ? 'primary' : 'default'}
                            block
                            onClick={() => setFormData({ ...formData, timeSlot: slot })}
                          >
                            {formatTime(slot)}
                          </Button>
                        </Col>
                      ))}
                    </Row>
                  </div>
                </Card>
              </Col>
            </Row>
            <Card title="Additional Notes (Optional)" style={{ marginTop: 24 }}>
              <TextArea
                rows={4}
                placeholder="Any specific concerns or symptoms you'd like to mention..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
            </Card>
          </div>
        )

      case 3:
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
                      {selectedSpecialty?.name}
                    </Title>
                  </Space>
                </Col>
                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Doctor</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {selectedDoctor?.name}
                    </Title>
                  </Space>
                </Col>
                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Date</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {formData.date
                        ? formatDate(formData.date, 'dddd, MMMM DD, YYYY')
                        : '-'}
                    </Title>
                  </Space>
                </Col>
                <Col xs={24} md={12}>
                  <Space direction="vertical" size="small">
                    <Text type="secondary">Time</Text>
                    <Title level={5} style={{ margin: 0 }}>
                      {formData.timeSlot ? formatTime(formData.timeSlot) : '-'}
                    </Title>
                  </Space>
                </Col>
                {formData.notes && (
                  <Col span={24}>
                    <Divider />
                    <Space direction="vertical" size="small">
                      <Text type="secondary">Notes</Text>
                      <Paragraph>{formData.notes}</Paragraph>
                    </Space>
                  </Col>
                )}
              </Row>
            </Card>
            <Card style={{ marginTop: 16, background: '#e6f7ff', borderColor: '#91d5ff' }}>
              <Space>
                <CheckCircleOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                <Text>
                  <strong>Note:</strong> Please arrive 15 minutes before your scheduled
                  appointment time. Bring your ID and any relevant medical records.
                </Text>
              </Space>
            </Card>
          </div>
        )

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
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={handleBack}
              disabled={currentStep === 0}
              size="large"
            >
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