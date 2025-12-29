import { useEffect, useMemo, useState } from 'react'
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
  Skeleton,
  DatePicker,
} from 'antd'
import '../styles/Appointments.css'
import {
  CalendarOutlined,
  ClockCircleOutlined,
  SearchOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { appointmentsAPI, doctorsAPI } from '../services/api'
import { formatDate, formatTime, getRelativeDate, getStatusColor, getStatusText } from '../utils/helpers'
import { useAuthStore } from '../store/authStore'

const { Title, Text } = Typography
const { TabPane } = Tabs

const PAGE_SIZE = 10

const normalizeAppointment = (row) => {
  const iso = row.appointment_time
  const d = iso ? dayjs(iso) : null

  return {
    id: row.id,
    status: row.status,
    specialty: row.medical_field_name || '—',
    doctor: row.doctor_name || '—',
    doctorId: row.doctor_id,
    medicalFieldId: row.medical_field_id,
    durationMinutes: row.duration_minutes ?? 30,
    reasonForVisit: row.reason_for_visit ?? null,
    notes: row.notes ?? null,

    dateISO: iso,
    date: d ? d.format('YYYY-MM-DD') : null,
    time: d ? d.format('HH:mm') : null,

    location: row.location || '', // not returned by backend currently
    raw: row,
  }
}

export default function Appointments() {
  const patientId = useAuthStore((s) => s.patientId)

  const [activeTab, setActiveTab] = useState('upcoming')
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  // Pagination (past)
  const [pastPage, setPastPage] = useState(1)
  const [pastHasMore, setPastHasMore] = useState(false)

  // Cancel
  const [cancelModalVisible, setCancelModalVisible] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)
  const [cancelling, setCancelling] = useState(false)

  // Reschedule
  const [rescheduleVisible, setRescheduleVisible] = useState(false)
  const [rescheduleDate, setRescheduleDate] = useState(null) // YYYY-MM-DD
  const [rescheduleSlots, setRescheduleSlots] = useState([])
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [selectedSlotISO, setSelectedSlotISO] = useState(null)
  const [rescheduling, setRescheduling] = useState(false)

  // when switching tabs, reset things
  useEffect(() => {
    setSearchQuery('')
    setSelectedAppointment(null)
    setCancelModalVisible(false)
    setRescheduleVisible(false)
    setRescheduleDate(null)
    setRescheduleSlots([])
    setSelectedSlotISO(null)

    if (activeTab === 'past') setPastPage(1)
  }, [activeTab])

  useEffect(() => {
    fetchAppointments()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, pastPage])

  const fetchAppointments = async () => {
    setLoading(true)
    try {
      if (activeTab === 'upcoming') {
        if (!patientId) {
          setAppointments([])
          setLoading(false)
          return
        }
        // upcoming endpoint supports limit (+ patient_id), no offset
        const res = await appointmentsAPI.getUpcoming(50, patientId)
        const rows = Array.isArray(res?.data) ? res.data : []
        setAppointments(rows.map(normalizeAppointment))
      } else {
        // past endpoint supports limit + offset
        const offset = (pastPage - 1) * PAGE_SIZE
        const res = await appointmentsAPI.getPast(PAGE_SIZE, offset)
        const rows = Array.isArray(res?.data) ? res.data : []
        const normalized = rows.map(normalizeAppointment)

        setAppointments(normalized)
        setPastHasMore(rows.length === PAGE_SIZE)
      }
    } catch (e) {
      antMessage.error(e?.errorData?.message || e?.message || 'Failed to load appointments')
      setAppointments([])
      setPastHasMore(false)
    } finally {
      setLoading(false)
    }
  }

  const filteredAppointments = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return appointments
    return appointments.filter((apt) => {
      const a = `${apt.doctor} ${apt.specialty}`.toLowerCase()
      return a.includes(q)
    })
  }, [appointments, searchQuery])

  const openCancel = (appointment) => {
    setSelectedAppointment(appointment)
    setCancelModalVisible(true)
  }

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return
    setCancelling(true)
    try {
      await appointmentsAPI.delete(selectedAppointment.id, null)
      antMessage.success('Appointment cancelled successfully')
      setCancelModalVisible(false)
      setSelectedAppointment(null)
      await fetchAppointments()
    } catch (e) {
      antMessage.error(e?.errorData?.message || 'Failed to cancel appointment')
    } finally {
      setCancelling(false)
    }
  }

  const openReschedule = (appointment) => {
    setSelectedAppointment(appointment)
    setRescheduleDate(null)
    setRescheduleSlots([])
    setSelectedSlotISO(null)
    setRescheduleVisible(true)
  }

  // load slots for reschedule modal
  useEffect(() => {
    const loadSlots = async () => {
      if (!rescheduleVisible || !selectedAppointment?.doctorId || !rescheduleDate) {
        setRescheduleSlots([])
        return
      }

      setLoadingSlots(true)
      try {
        const res = await doctorsAPI.getAvailableSlots(selectedAppointment.doctorId, rescheduleDate)
        const slots = Array.isArray(res?.data?.available_slots) ? res.data.available_slots : []

        const normalized = slots
          .filter((s) => s?.start_time)
          .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())

        setRescheduleSlots(normalized)
        setSelectedSlotISO((prev) => (prev && normalized.some((s) => s.start_time === prev) ? prev : null))
      } catch (e) {
        antMessage.error('Failed to load available slots')
        setRescheduleSlots([])
      } finally {
        setLoadingSlots(false)
      }
    }

    loadSlots()
  }, [rescheduleVisible, selectedAppointment?.doctorId, rescheduleDate])

  const handleConfirmReschedule = async () => {
    if (!selectedAppointment || !selectedSlotISO) return
    if (!patientId) {
      antMessage.error('Missing patient id. Please login again.')
      return
    }

    setRescheduling(true)
    try {
      // 1) create new appointment
      const newTimeISO = dayjs(selectedSlotISO).second(0).millisecond(0).toISOString()

      await appointmentsAPI.create({
        patient_id: patientId,
        doctor_id: selectedAppointment.doctorId,
        medical_field_id: selectedAppointment.medicalFieldId,
        appointment_time: newTimeISO,
        duration_minutes: selectedAppointment.durationMinutes ?? 30,
        reason_for_visit: selectedAppointment.reasonForVisit ?? null,
      })

      // // 2) cancel old appointment
      await appointmentsAPI.delete(selectedAppointment.id, 'cancelled')

      antMessage.success('Appointment rescheduled successfully')
      setRescheduleVisible(false)
      setSelectedAppointment(null)
      await fetchAppointments()
    } catch (e) {
      const status = e?.response?.status
      const detail = e?.response?.data?.detail

      if (status === 409) antMessage.error(detail || 'This time slot is already booked.')
      else antMessage.error(detail || e?.errorData?.message || 'Failed to reschedule appointment')
    } finally {
      setRescheduling(false)
    }
  }

  const AppointmentCard = ({ appointment }) => (
    <Card hoverable style={{ marginBottom: 16 }}>
      <Row justify="space-between" align="top" gutter={[12, 12]}>
        <Col xs={24} md={18}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Space align="center">
              <CalendarOutlined style={{ fontSize: 24, color: '#1890ff' }} />
              <div>
                <Title level={5} style={{ margin: 0 }}>
                  {appointment.specialty}
                </Title>
                <Tag color={getStatusColor(appointment.status)}>{getStatusText(appointment.status)}</Tag>
              </div>
            </Space>

            <Text type="secondary" strong>
              {appointment.doctor}
            </Text>

            <Space size="large" wrap>
              <Space size="small">
                <CalendarOutlined />
                <Text>
                  {activeTab === 'upcoming'
                    ? getRelativeDate(appointment.date)
                    : appointment.date
                      ? formatDate(appointment.date, 'MMM DD, YYYY')
                      : '—'}
                </Text>
              </Space>
              <Space size="small">
                <ClockCircleOutlined />
                <Text>{appointment.time ? formatTime(appointment.time) : '—'}</Text>
              </Space>
            </Space>

            {appointment.location ? (
              <Space size="small">
                <EnvironmentOutlined style={{ color: '#8c8c8c' }} />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {appointment.location}
                </Text>
              </Space>
            ) : null}
          </Space>
        </Col>

        {activeTab === 'upcoming' && appointment.status !== 'cancelled' && (
          <Col xs={24} md={6} style={{ textAlign: 'right' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button icon={<SyncOutlined />} block onClick={() => openReschedule(appointment)}>
                Reschedule
              </Button>
              <Button danger icon={<CloseCircleOutlined />} block onClick={() => openCancel(appointment)}>
                Cancel
              </Button>
            </Space>
          </Col>
        )}
      </Row>
    </Card>
  )

  const PastPagination = () => {
    if (activeTab !== 'past') return null
    if (loading) return null
    if (searchQuery.trim()) return null // avoid confusion while filtering

    return (
      <Row justify="space-between" align="middle" style={{ marginTop: 16 }}>
        <Col>
          <Button onClick={() => setPastPage((p) => Math.max(1, p - 1))} disabled={pastPage === 1}>
            Previous
          </Button>
        </Col>
        <Col>
          <Text type="secondary">Page {pastPage}</Text>
        </Col>
        <Col>
          <Button onClick={() => setPastPage((p) => p + 1)} disabled={!pastHasMore}>
            Next
          </Button>
        </Col>
      </Row>
    )
  }

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
          <Skeleton active />
        ) : filteredAppointments.length > 0 ? (
          <>
            {filteredAppointments.map((appointment) => (
              <AppointmentCard key={appointment.id} appointment={appointment} />
            ))}
            <PastPagination />
          </>
        ) : (
          <Empty
            description={searchQuery ? 'No appointments found matching your search' : `No ${activeTab} appointments`}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>

      {/* Cancel modal */}
      <Modal
        title="Cancel Appointment"
        open={cancelModalVisible}
        onOk={handleCancelAppointment}
        confirmLoading={cancelling}
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
                {selectedAppointment.date ? formatDate(selectedAppointment.date, 'MMM DD, YYYY') : '—'} at{' '}
                {selectedAppointment.time ? formatTime(selectedAppointment.time) : '—'}
              </Text>
            </Space>
          </Card>
        )}
      </Modal>

      {/* Reschedule modal */}
      <Modal
        title="Reschedule Appointment"
        open={rescheduleVisible}
        onOk={handleConfirmReschedule}
        confirmLoading={rescheduling}
        okText="Confirm Reschedule"
        okButtonProps={{ disabled: !selectedSlotISO }}
        onCancel={() => {
          setRescheduleVisible(false)
          setSelectedAppointment(null)
          setRescheduleDate(null)
          setRescheduleSlots([])
          setSelectedSlotISO(null)
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Text type="secondary">
            Pick a new date and time for: <Text strong>{selectedAppointment?.doctor}</Text>
          </Text>

          <DatePicker
            size="large"
            style={{ width: '100%' }}
            disabledDate={(current) => current && current < dayjs().startOf('day')}
            value={rescheduleDate ? dayjs(rescheduleDate, 'YYYY-MM-DD') : null}
            onChange={(d) => {
              setRescheduleDate(d ? d.format('YYYY-MM-DD') : null)
              setSelectedSlotISO(null)
            }}
          />

          <Card title="Available Time Slots">
            {!rescheduleDate ? (
              <Empty description="Select a date to see slots" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : loadingSlots ? (
              <Skeleton active />
            ) : rescheduleSlots.length === 0 ? (
              <Empty description="No available slots" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <div style={{ maxHeight: 260, overflow: 'auto' }}>
                <Row gutter={[8, 8]}>
                  {rescheduleSlots.map((slot) => {
                    const iso = slot.start_time
                    const selected = selectedSlotISO === iso
                    const disabled = slot.available === false
                    const label = iso ? dayjs(iso).format('HH:mm') : '—'

                    return (
                      <Col span={8} key={iso}>
                        <Button
                          type={selected ? 'primary' : 'default'}
                          block
                          disabled={disabled}
                          onClick={() => setSelectedSlotISO(iso)}
                        >
                          {formatTime(label)}
                        </Button>
                      </Col>
                    )
                  })}
                </Row>
              </div>
            )}
          </Card>
        </Space>
      </Modal>
    </Space>
  )
}
