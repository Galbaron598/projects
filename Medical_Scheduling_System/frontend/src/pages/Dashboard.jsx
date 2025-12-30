import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Typography, Button, Space, Tag, Empty } from 'antd'
import { CalendarOutlined, ClockCircleOutlined, PlusOutlined, UserOutlined } from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { appointmentsAPI, medicalFieldsAPI } from '../services/api'
import { getRelativeDate, getStatusColor } from '../utils/helpers'
import { resolveMedicalIconComponent } from '../utils/medicalIcons'
import '../styles/Dashboard.css'
import Error from '../components/Error'
import Loading from '../components/Loading'
import useEnsurePatientInStore from '../hooks/useEnsurePatientInStore'

const { Title, Text, Paragraph } = Typography

const SERVICE_COLORS = ['#ff4d4f', '#722ed1', '#1890ff', '#eb2f96', '#13c2c2', '#52c41a', '#fa8c16', '#2f54eb']
const pickColor = (idx) => SERVICE_COLORS[idx % SERVICE_COLORS.length]

const formatTimeFromISO = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatDateForRelative = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

const normalizeUpcoming = (rows) =>
  (rows || []).map((a) => ({
    id: a.id,
    specialty: a.medical_field_name ?? a.specialty ?? 'Appointment',
    doctor: a.doctor_name ?? a.doctor ?? 'Doctor',
    appointment_time: a.appointment_time,
    date: formatDateForRelative(a.appointment_time),
    time: formatTimeFromISO(a.appointment_time),
    status: a.status ?? 'scheduled',
    duration_minutes: a.duration_minutes,
    location: a.location ?? null,
    consultation_fee: a.consultation_fee ?? null,
  }))

const normalizeMedicalFields = (rows) => {
  const arr = Array.isArray(rows) ? rows : []
  return arr.map((f, idx) => ({
    id: f.id ?? `${f.medical_field_name ?? f.name ?? 'service'}-${idx}`,
    name: f.medical_field_name ?? f.name ?? 'Medical Service',
    description: f.description ?? '',
    icon: f.icon ?? null,
    is_active: f.is_active ?? true,
    color: pickColor(idx),
  }))
}

const Dashboard = () => {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const patientIdFromStore = useAuthStore((state) => state.patientId)

  const navigate = useNavigate()

  const ensurePatientInStore = useEnsurePatientInStore()

  const [upcomingAppointments, setUpcomingAppointments] = useState([])
  const [medicalServices, setMedicalServices] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchMedicalServices = useCallback(async () => {
    const res = await medicalFieldsAPI.getAll()
    const normalized = normalizeMedicalFields(res?.data).filter((s) => s.is_active !== false)
    setMedicalServices(normalized)
  }, [])

  const fetchUpcomingAppointments = useCallback(async () => {
    if (!token) {
      navigate('/login')
      return
    }

    const ensuredPatientId = patientIdFromStore ? Number(patientIdFromStore) : await ensurePatientInStore()
    if (!ensuredPatientId || Number.isNaN(ensuredPatientId)) throw new Error('Missing patientId after ensure')

    const res = await appointmentsAPI.getUpcoming(10, ensuredPatientId)
    const data = Array.isArray(res?.data) ? res.data : []
    setUpcomingAppointments(normalizeUpcoming(data))
  }, [ensurePatientInStore, navigate, patientIdFromStore, token])

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      await Promise.all([fetchMedicalServices(), fetchUpcomingAppointments()])
    } catch (err) {
      setError(err)
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }, [fetchMedicalServices, fetchUpcomingAppointments])

  useEffect(() => {
    loadDashboard()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const isNewUser = !upcomingAppointments.length

  const servicesForUI = useMemo(() => {
    return (medicalServices || []).map((s, idx) => {
      const Icon = resolveMedicalIconComponent(s.icon, s.name)
      return { ...s, color: s.color || pickColor(idx), Icon }
    })
  }, [medicalServices])

  if (loading) return <Loading tip="Loading dashboard..." />
  if (error) return <Error error={error} onRetry={loadDashboard} showTechnicalDetails={import.meta.env.DEV} />

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          border: 'none',
        }}
      >
        <Title level={2} style={{ color: '#fff', marginBottom: 8 }}>
          {isNewUser ? 'Welcome to MediCare!' : `Welcome back, ${user?.full_name?.split(' ')[0] || 'there'}!`}
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.9)', fontSize: 16, marginBottom: 0 }}>
          {isNewUser ? "Let's get started with your first appointment" : 'Manage your health appointments with ease'}
        </Paragraph>
      </Card>

      {isNewUser ? (
        <>
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <CalendarOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
              <Title level={3}>Book Your First Appointment</Title>
              <Paragraph type="secondary" style={{ maxWidth: 600, margin: '0 auto 24px' }}>
                Choose from our wide range of medical specialties and find the perfect time for your visit
              </Paragraph>
              <Button type="primary" size="large" icon={<PlusOutlined />} onClick={() => navigate('/book')}>
                Get Started
              </Button>
            </div>
          </Card>

          <div>
            <Title level={3} style={{ marginBottom: 16 }}>
              Our Medical Services
            </Title>

            {servicesForUI.length === 0 ? (
              <Empty description="No medical services available" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <Row gutter={[16, 16]}>
                {servicesForUI.map((service) => {
                  const Icon = service.Icon
                  return (
                    <Col xs={24} sm={12} lg={8} key={service.id}>
                      <Card hoverable onClick={() => navigate('/book')}>
                        <Space direction="vertical" size="small">
                          <div style={{ fontSize: 32, color: service.color }}>
                            <Icon />
                          </div>
                          <Title level={5} style={{ marginBottom: 4 }}>
                            {service.name}
                          </Title>
                          <Text type="secondary">{service.description || '—'}</Text>
                        </Space>
                      </Card>
                    </Col>
                  )
                })}
              </Row>
            )}
          </div>
        </>
      ) : (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={16}>
            <Card
              title={
                <Title level={4} style={{ margin: 0 }}>
                  Upcoming Appointments
                </Title>
              }
              extra={
                <Button type="link" onClick={() => navigate('/appointments')}>
                  View all
                </Button>
              }
            >
              {upcomingAppointments.length > 0 ? (
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  {upcomingAppointments.map((appointment) => (
                    <Card key={appointment.id} type="inner">
                      <Row justify="space-between" align="middle" gutter={[16, 16]}>
                        <Col flex="auto">
                          <Space direction="vertical" size="small">
                            <Space>
                              <CalendarOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                              <Title level={5} style={{ margin: 0 }}>
                                {appointment.specialty}
                              </Title>
                            </Space>

                            <Text type="secondary">{appointment.doctor}</Text>

                            <Space size="large" wrap>
                              <Space size="small">
                                <CalendarOutlined />
                                <Text>{getRelativeDate(appointment.date)}</Text>
                              </Space>
                              <Space size="small">
                                <ClockCircleOutlined />
                                <Text>{appointment.time}</Text>
                              </Space>

                              {typeof appointment.duration_minutes === 'number' && (
                                <Space size="small">
                                  <Text type="secondary">{appointment.duration_minutes} min</Text>
                                </Space>
                              )}

                              {appointment.consultation_fee != null && (
                                <Space size="small">
                                  <Text type="secondary">₪{appointment.consultation_fee}</Text>
                                </Space>
                              )}
                            </Space>

                            {appointment.location && (
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                {appointment.location}
                              </Text>
                            )}
                          </Space>
                        </Col>

                        <Col>
                          <Tag color={getStatusColor(appointment.status)}>{String(appointment.status).toUpperCase()}</Tag>
                        </Col>
                      </Row>
                    </Card>
                  ))}
                </Space>
              ) : (
                <Empty description="No upcoming appointments" image={Empty.PRESENTED_IMAGE_SIMPLE}>
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/book')}>
                    Book Appointment
                  </Button>
                </Empty>
              )}
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Title level={4}>Quick Actions</Title>

              <Card hoverable onClick={() => navigate('/book')}>
                <Space direction="vertical" size="small">
                  <PlusOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                  <Title level={5} style={{ marginBottom: 4 }}>
                    Book New Appointment
                  </Title>
                  <Text type="secondary">Schedule a visit with our specialists</Text>
                </Space>
              </Card>

              <Card hoverable onClick={() => navigate('/appointments')}>
                <Space direction="vertical" size="small">
                  <CalendarOutlined style={{ fontSize: 24, color: '#722ed1' }} />
                  <Title level={5} style={{ marginBottom: 4 }}>
                    View History
                  </Title>
                  <Text type="secondary">Check your past appointments</Text>
                </Space>
              </Card>

              <Card hoverable onClick={() => navigate('/profile')}>
                <Space direction="vertical" size="small">
                  <UserOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                  <Title level={5} style={{ marginBottom: 4 }}>
                    Medical Profile
                  </Title>
                  <Text type="secondary">Update your health information</Text>
                </Space>
              </Card>
            </Space>
          </Col>
        </Row>
      )}

      {!isNewUser && (
        <div>
          <Title level={4} style={{ marginBottom: 16 }}>
            Available Specialties
          </Title>

          {servicesForUI.length === 0 ? (
            <Empty description="No specialties available" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <Row gutter={[16, 16]}>
              {servicesForUI.map((service) => {
                const Icon = service.Icon
                return (
                  <Col xs={12} sm={8} lg={4} key={service.id}>
                    <Card
                      hoverable
                      styles={{ body: { textAlign: 'center', padding: '20px 12px' } }}
                      onClick={() => navigate('/book')}
                    >
                      <div style={{ fontSize: 32, color: service.color, marginBottom: 8 }}>
                        <Icon />
                      </div>
                      <Text strong style={{ fontSize: 12 }}>
                        {service.name}
                      </Text>
                    </Card>
                  </Col>
                )
              })}
            </Row>
          )}
        </div>
      )}
    </Space>
  )
}

export default Dashboard
