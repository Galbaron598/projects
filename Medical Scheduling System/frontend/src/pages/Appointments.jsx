import { useState, useEffect } from 'react'
import {
  Card,
  Tabs,
  Row,
  Col,
  Space,
  Tag,
  Button,
  Input,
  Typography,
  Empty,
  Modal,
  message as antMessage,
} from 'antd'
import "../styles/Appointments.css"
import {
  CalendarOutlined,
  ClockCircleOutlined,
  SearchOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons'
import { appointmentsAPI } from '../services/api'
import { formatDate, formatTime, getRelativeDate, getStatusColor, getStatusText } from '../utils/helpers'
import Loading from '../components/Loading'

const { Title, Text } = Typography
const { TabPane } = Tabs

const Appointments = () => {
  const [activeTab, setActiveTab] = useState('upcoming')
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [cancelModalVisible, setCancelModalVisible] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)

  const mockUpcoming = [
    {
      id: 1,
      specialty: 'Cardiology',
      doctor: 'Dr. Sarah Johnson',
      date: '2024-12-26',
      time: '10:00',
      status: 'confirmed',
      location: 'Building A, Floor 3, Room 301',
    },
    {
      id: 2,
      specialty: 'Orthopedics',
      doctor: 'Dr. James Wilson',
      date: '2024-12-28',
      time: '14:30',
      status: 'confirmed',
      location: 'Building B, Floor 2, Room 205',
    },
  ]

  const mockPast = [
    {
      id: 3,
      specialty: 'General Medicine',
      doctor: 'Dr. Emily Rodriguez',
      date: '2024-12-15',
      time: '09:00',
      status: 'completed',
      location: 'Building A, Floor 1, Room 105',
    },
    {
      id: 4,
      specialty: 'Pediatrics',
      doctor: 'Dr. Michael Chen',
      date: '2024-11-20',
      time: '11:00',
      status: 'completed',
      location: 'Building C, Floor 2, Room 210',
    },
  ]

  useEffect(() => {
    fetchAppointments()
  }, [activeTab])

  const fetchAppointments = async () => {
    setLoading(true)
    try {
      if (activeTab === 'upcoming') {
        setAppointments(mockUpcoming)
      } else {
        setAppointments(mockPast)
      }
      
      // Uncomment for real API
      // const response = activeTab === 'upcoming'
      //   ? await appointmentsAPI.getUpcoming()
      //   : await appointmentsAPI.getPast()
      // setAppointments(response.data)
    } catch (error) {
      antMessage.error('Failed to load appointments')
    } finally {
      setLoading(false)
    }
  }

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return

    try {
      setAppointments(appointments.filter((a) => a.id !== selectedAppointment.id))
      antMessage.success('Appointment cancelled successfully')
      setCancelModalVisible(false)
      setSelectedAppointment(null)
      
      // Uncomment for real API
      // await appointmentsAPI.cancel(selectedAppointment.id)
      // fetchAppointments()
    } catch (error) {
      antMessage.error('Failed to cancel appointment')
    }
  }

  const filteredAppointments = appointments.filter(
    (apt) =>
      apt.doctor.toLowerCase().includes(searchQuery.toLowerCase()) ||
      apt.specialty.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const AppointmentCard = ({ appointment }) => (
    <Card 
      hoverable
      style={{ marginBottom: 16 }}
    >
      <Row justify="space-between" align="top">
        <Col xs={24} md={18}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Space align="center">
              <CalendarOutlined style={{ fontSize: 24, color: '#1890ff' }} />
              <div>
                <Title level={5} style={{ margin: 0 }}>
                  {appointment.specialty}
                </Title>
                <Tag color={getStatusColor(appointment.status)}>
                  {getStatusText(appointment.status)}
                </Tag>
              </div>
            </Space>
            
            <Text type="secondary" strong>{appointment.doctor}</Text>
            
            <Space size="large" wrap>
              <Space size="small">
                <CalendarOutlined />
                <Text>
                  {activeTab === 'upcoming'
                    ? getRelativeDate(appointment.date)
                    : formatDate(appointment.date, 'MMM DD, YYYY')}
                </Text>
              </Space>
              <Space size="small">
                <ClockCircleOutlined />
                <Text>{formatTime(appointment.time)}</Text>
              </Space>
            </Space>
            
            <Space size="small">
              <EnvironmentOutlined style={{ color: '#8c8c8c' }} />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {appointment.location}
              </Text>
            </Space>
          </Space>
        </Col>
        
        {activeTab === 'upcoming' && (
          <Col xs={24} md={6} style={{ textAlign: 'right' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                icon={<SyncOutlined />}
                block
                onClick={() => {
                  antMessage.info('Reschedule feature coming soon')
                }}
              >
                Reschedule
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                block
                onClick={() => {
                  setSelectedAppointment(appointment)
                  setCancelModalVisible(true)
                }}
              >
                Cancel
              </Button>
            </Space>
          </Col>
        )}
      </Row>
    </Card>
  )

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div className="page-header">
        <Title level={2}>My Appointments</Title>
        <Text type="secondary">Manage your medical appointments</Text>
      </div>

      <Card>
        <Input
          size="large"
          placeholder="Search appointments..."
          prefix={<SearchOutlined />}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ marginBottom: 16 }}
        />

        <Tabs activeKey={activeTab} onChange={setActiveTab} size="large">
          <TabPane tab="Upcoming" key="upcoming" />
          <TabPane tab="Past" key="past" />
        </Tabs>

        {loading ? (
          <Loading tip="Loading appointments..." />
        ) : filteredAppointments.length > 0 ? (
          filteredAppointments.map((appointment) => (
            <AppointmentCard key={appointment.id} appointment={appointment} />
          ))
        ) : (
          <Empty
            description={
              searchQuery
                ? 'No appointments found matching your search'
                : `No ${activeTab} appointments`
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>

      <Modal
        title="Cancel Appointment"
        open={cancelModalVisible}
        onOk={handleCancelAppointment}
        onCancel={() => {
          setCancelModalVisible(false)
          setSelectedAppointment(null)
        }}
        okText="Yes, Cancel"
        okButtonProps={{ danger: true }}
      >
        <p>Are you sure you want to cancel this appointment?</p>
        {selectedAppointment && (
          <Card size="small">
            <Space direction="vertical">
              <Text strong>{selectedAppointment.specialty}</Text>
              <Text>{selectedAppointment.doctor}</Text>
              <Text type="secondary">
                {formatDate(selectedAppointment.date, 'MMM DD, YYYY')} at{' '}
                {formatTime(selectedAppointment.time)}
              </Text>
            </Space>
          </Card>
        )}
      </Modal>
    </Space>
  )
}

export default Appointments