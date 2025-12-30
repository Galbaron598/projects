import { useEffect, useMemo, useState, useCallback } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  Typography,
  Row,
  Col,
  Avatar,
  DatePicker,
  message as antMessage,
} from 'antd'
import {
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EditOutlined,
  SaveOutlined,
} from '@ant-design/icons'

import '../styles/Profile.css'
import { useAuthStore } from '../store/authStore'
import { patientsAPI } from '../services/api'
import dayjs from 'dayjs'
import useEnsurePatientInStore from '../hooks/useEnsurePatientInStore'

const { Title, Text } = Typography
const { TextArea } = Input

const Profile = () => {
  const user = useAuthStore((s) => s.user)
  const token = useAuthStore((s) => s.token)
  const patientIdFromStore = useAuthStore((s) => s.patientId)
  const updateUser = useAuthStore((s) => s.updateUser)

  const { ensurePatientId } = useEnsurePatientInStore()

  const [isEditing, setIsEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [fetching, setFetching] = useState(false)

  const [form] = Form.useForm()

  const loadProfile = useCallback(async () => {
    if (!token) return

    setFetching(true)
    try {
      const ensuredId = patientIdFromStore ? Number(patientIdFromStore) : await ensurePatientId()
      if (!ensuredId || Number.isNaN(ensuredId)) throw new Error('Missing patientId after ensure')

      const res = await patientsAPI.getProfile(ensuredId)
      if (res?.data) updateUser(res.data)
    } catch (e) {
      antMessage.error(e?.errorData?.message || e?.message || 'Failed to load profile')
    } finally {
      setFetching(false)
    }
  }, [token, patientIdFromStore, ensurePatientId, updateUser])

  useEffect(() => {
    loadProfile()
  }, [loadProfile])

  const initialValues = useMemo(() => {
    return {
      fullName: user?.full_name ?? user?.fullName ?? '',
      email: user?.email ?? '',
      dateOfBirth: user?.date_of_birth
        ? dayjs(user.date_of_birth)
        : user?.dateOfBirth
          ? dayjs(user.dateOfBirth)
          : null,

      emergencyContact: user?.emergency_contact ?? user?.emergencyContact ?? '',
      address: user?.address ?? '',
    }
  }, [user])

  useEffect(() => {
    form.setFieldsValue(initialValues)
  }, [form, initialValues])

  const handleSaveProfile = async (values) => {
    if (!token) {
      antMessage.error('Please login again.')
      return
    }

    setSaving(true)
    try {
      const ensuredId = patientIdFromStore ? Number(patientIdFromStore) : await ensurePatientId()
      if (!ensuredId || Number.isNaN(ensuredId)) throw new Error('Missing patientId after ensure')

      const payload = {
        full_name: values.fullName?.trim() || null,
        email: values.email?.trim() || null,
        date_of_birth: values.dateOfBirth ? values.dateOfBirth.format('YYYY-MM-DD') : null,

        emergency_contact: values.emergencyContact?.trim() || null,
        address: values.address?.trim() || null,
      }

      const res = await patientsAPI.updateProfile(payload, ensuredId)
      if (res?.data) updateUser(res.data)

      antMessage.success('Profile updated successfully')
      setIsEditing(false)
    } catch (e) {
      antMessage.error(e?.errorData?.message || e?.message || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card
        loading={fetching}
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          border: 'none',
        }}
      >
        <Space align="center" size="large">
          <Avatar size={80} icon={<UserOutlined />} style={{ backgroundColor: '#fff', color: '#1890ff' }} />

          <div>
            <Title level={2} style={{ color: '#fff', marginBottom: 4 }}>
              {user?.full_name || 'User'}
            </Title>

            <Space direction="vertical" size={2}>
              <Space>
                <PhoneOutlined />
                <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
                  {user?.phone_number || user?.phoneNumber || '-'}
                </Text>
              </Space>
            </Space>
          </div>
        </Space>
      </Card>

      <Card
        title={
          <Space>
            <UserOutlined />
            <span>Personal Information</span>
          </Space>
        }
        extra={
          !isEditing ? (
            <Button icon={<EditOutlined />} onClick={() => setIsEditing(true)} disabled={fetching}>
              Edit
            </Button>
          ) : (
            <Space>
              <Button
                onClick={() => {
                  setIsEditing(false)
                  form.setFieldsValue(initialValues)
                }}
              >
                Cancel
              </Button>
              <Button type="primary" icon={<SaveOutlined />} onClick={() => form.submit()} loading={saving}>
                Save
              </Button>
            </Space>
          )
        }
      >
        <Form form={form} layout="vertical" onFinish={handleSaveProfile} disabled={!isEditing}>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                label="Full Name"
                name="fullName"
                rules={[{ required: true, message: 'Please enter your full name' }]}
              >
                <Input prefix={<UserOutlined />} placeholder="Full Name" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                label="Email Address"
                name="email"
                rules={[{ type: 'email', message: 'Please enter a valid email' }]}
              >
                <Input prefix={<MailOutlined />} placeholder="Email Address" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item label="Date of Birth" name="dateOfBirth">
                <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                label="Emergency Contact"
                name="emergencyContact"
                rules={[
                  {
                    pattern: /^[0-9+\-\s()]{7,20}$/,
                    message: 'Please enter a valid phone number',
                  },
                ]}
              >
                <Input prefix={<PhoneOutlined />} placeholder="Emergency Contact Number" />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item label="Address" name="address">
                <TextArea placeholder="Your complete address" rows={3} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>
    </Space>
  )
}

export default Profile
