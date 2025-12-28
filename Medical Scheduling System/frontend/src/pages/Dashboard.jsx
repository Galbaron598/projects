import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Card, 
  Row, 
  Col, 
  Typography, 
Button, 
Space, 
  Tag,
  Empty,
  Skeleton 
} from 'antd'
import {
  CalendarOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  HeartOutlined,
  ExperimentOutlined,
  MedicineBoxOutlined,
  UserOutlined,
  EyeOutlined,
  ApiOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { appointmentsAPI } from '../services/api'
import { formatDate, formatTime, getRelativeDate, getStatusColor } from '../utils/helpers'
import { message } from 'antd'
import { message } from 'antd'
import "../styles/Dashboard.css"
import Error from '../components/Error'

const { Title, Text, Paragraph } = Typography

const Dashboard = () => {
  const user = useAuthStore((state) => state.user)
  const [upcomingAppointments, setUpcomingAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const medicalServices = [
    { 
      icon: <HeartOutlined />, 
      name: 'Cardiology', 
      description: 'Heart & cardiovascular care',
      color: '#ff4d4f'
    },
    { 
      icon: <ExperimentOutlined />, 
      name: 'Neurology', 
      description: 'Brain & nervous system',
      color: '#722ed1'
    },
    { 
      icon: <ApiOutlined />, 
      name: 'Orthopedics', 
      description: 'Bones & joints',
      color: '#1890ff'
    },
    { 
      icon: <UserOutlined />, 
      name: 'Pediatrics', 
      description: 'Children\'s health',
      color: '#eb2f96'
    },
    { 
      icon: <EyeOutlined />, 
      name: 'Ophthalmology', 
      description: 'Eye care',
      color: '#13c2c2'
    },
    { 
      icon: <MedicineBoxOutlined />, 
      name: 'General Medicine', 
      description: 'Primary care',
      color: '#52c41a'
    },
  ]

  useEffect(() => {
    fetchUpcomingAppointments()
  }, [])

  const fetchUpcomingAppointments = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Mock data
      const mockAppointments = [
        {
          id: 1,
          specialty: 'Cardiology',
          doctor: 'Dr. Sarah Johnson',
          date: '2024-12-26',
          time: '10:00',
          status: 'confirmed',
          location: 'Building A, Floor 3, Room 301'
        },
      ]
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      setUpcomingAppointments(mockAppointments)
      
      // Uncomment for real API
      // const response = await appointmentsAPI.getUpcoming()
      // setUpcomingAppointments(response.data)
    } catch (err) {
      // Error will be automatically parsed by Error component
      setError(err)
      console.error('Failed to load appointments:', err)
    } finally {
      setLoading(false)
    }
  }

  const isNewUser = !upcomingAppointments.length

  if (loading) {
    return <Loading tip="Loading dashboard..." />
  }

  // Show error if fetch failed
  if (error) {
    return (
      <Error 
        error={error}
        onRetry={fetchUpcomingAppointments}
        showTechnicalDetails={import.meta.env.DEV}
      />
    )
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Welcome Banner */}
      <Card
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          border: 'none'
        }}
      >
        <Title level={2} style={{ color: '#fff', marginBottom: 8 }}>
          {isNewUser ? 'Welcome to MediCare!' : `Welcome back, ${user?.fullName?.split(' ')[0]}!`}
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.9)', fontSize: 16, marginBottom: 0 }}>
          {isNewUser 
            ? 'Let\'s get started with your first appointment'
            : 'Manage your health appointments with ease'
          }
        </Paragraph>
      </Card>

      {isNewUser ? (
        // New User View
        <>
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <CalendarOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
              <Title level={3}>Book Your First Appointment</Title>
              <Paragraph type="secondary" style={{ maxWidth: 600, margin: '0 auto 24px' }}>
                Choose from our wide range of medical specialties and find the perfect time for your visit
              </Paragraph>
              <Button 
                type="primary" 
                size="large" 
                icon={<PlusOutlined />}
                onClick={() => navigate('/book')}
              >
                Get Started
              </Button>
            </div>
          </Card>

          <div>
            <Title level={3} style={{ marginBottom: 16 }}>Our Medical Services</Title>
            <Row gutter={[16, 16]}>
              {medicalServices.map((service) => (
                <Col xs={24} sm={12} lg={8} key={service.name}>
                  <Card 
                    hoverable
                    onClick={() => navigate('/book')}
                  >
                    <Space direction="vertical" size="small">
                      <div style={{ fontSize: 32, color: service.color }}>
                        {service.icon}
                      </div>
                      <Title level={5} style={{ marginBottom: 4 }}>
                        {service.name}
                      </Title>
                      <Text type="secondary">{service.description}</Text>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </>
      ) : (
        // Returning User View
        <Row gutter={[16, 16]}>
          {/* Upcoming Appointments */}
          <Col xs={24} lg={16}>
            <Card 
              title={<Title level={4} style={{ margin: 0 }}>Upcoming Appointments</Title>}
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
                      <Row justify="space-between" align="middle">
                        <Col>
                          <Space direction="vertical" size="small">
                            <Space>
                              <CalendarOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                              <Title level={5} style={{ margin: 0 }}>
                                {appointment.specialty}
                              </Title>
                            </Space>
                            <Text type="secondary">{appointment.doctor}</Text>
                            <Space size="large">
                              <Space size="small">
                                <CalendarOutlined />
                                <Text>{getRelativeDate(appointment.date)}</Text>
                              </Space>
                              <Space size="small">
                                <ClockCircleOutlined />
                                <Text>{formatTime(appointment.time)}</Text>
                              </Space>
                            </Space>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {appointment.location}
                            </Text>
                          </Space>
                        </Col>
                        <Col>
                          <Tag color={getStatusColor(appointment.status)}>
                            {appointment.status.toUpperCase()}
                          </Tag>
                        </Col>
                      </Row>
                    </Card>
                  ))}
                </Space>
              ) : (
                <Empty
                  description="No upcoming appointments"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                  <Button 
                    type="primary" 
                    icon={<PlusOutlined />}
                    onClick={() => navigate('/book')}
                  >
                    Book Appointment
                  </Button>
                </Empty>
              )}
            </Card>
          </Col>

          {/* Quick Actions */}
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

      {/* Available Specialties */}
      {!isNewUser && (
        <div>
          <Title level={4} style={{ marginBottom: 16 }}>Available Specialties</Title>
          <Row gutter={[16, 16]}>
            {medicalServices.map((service) => (
              <Col xs={12} sm={8} lg={4} key={service.name}>
                <Card 
                  hoverable
                  bodyStyle={{ textAlign: 'center', padding: '20px 12px' }}
                  onClick={() => navigate('/book')}
                >
                  <div style={{ fontSize: 32, color: service.color, marginBottom: 8 }}>
                    {service.icon}
                  </div>
                  <Text strong style={{ fontSize: 12 }}>{service.name}</Text>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </Space>
  )
}

export default Dashboard