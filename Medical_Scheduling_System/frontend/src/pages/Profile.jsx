import { useEffect, useMemo, useState } from "react"
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
} from "antd"
import {
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  EditOutlined,
  SaveOutlined,
  MedicineBoxOutlined,
} from "@ant-design/icons"

import "../styles/Profile.css"
import { useAuthStore } from "../store/authStore"
import { userAPI } from "../services/api"
import dayjs from "dayjs"

const { Title, Text } = Typography
const { TextArea } = Input

const Profile = () => {
  const patientId = useAuthStore((s) => s.patientId)
  const user = useAuthStore((s) => s.user)
  const updateUser = useAuthStore((s) => s.updateUser)

  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(false)

  const [form] = Form.useForm()

  useEffect(() => {
    const loadMe = async () => {
      setFetching(true)
      try {
        const res = await userAPI.getMe(patientId)
        if (res?.data) {
          // backend returns: full_name, phone_number, date_of_birth, ...
          updateUser(res.data)
        }
      } catch (e) {
        antMessage.error(e?.errorData?.message || "Failed to load profile")
      } finally {
        setFetching(false)
      }
    }
    loadMe()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const initialValues = useMemo(() => {
    return {
      fullName: user?.full_name || user?.fullName || "",
      email: user?.email || "",
      dateOfBirth: user?.date_of_birth ? dayjs(user.date_of_birth) : user?.dateOfBirth ? dayjs(user.dateOfBirth) : null,
      address: user?.address || "",
      emergencyContact: user?.emergency_contact || user?.emergencyContact || "",
    }
  }, [user])

  useEffect(() => {
    form.setFieldsValue(initialValues)
  }, [initialValues, form])

  const handleSaveProfile = async (values) => {
    setLoading(true)
    try {
      // ✅ map to backend schema (snake_case)
      const payload = {
        full_name: values.fullName?.trim() || null,
        email: values.email?.trim() || null,
        date_of_birth: values.dateOfBirth ? values.dateOfBirth.format("YYYY-MM-DD") : null,
        // optional fields if you add them to UI later:
        // gender: values.gender ?? null,
        // time_zone: values.timeZone ?? null,
      }

      const res = await userAPI.updateMe(payload)

      // ✅ update store with server response (source of truth)
      if (res?.data) updateUser(res.data)

      antMessage.success("Profile updated successfully")
      setIsEditing(false)
    } catch (error) {
      antMessage.error(error?.errorData?.message || "Failed to update profile")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card
        loading={fetching}
        style={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "#fff",
          border: "none",
        }}
      >
        <Space align="center" size="large">
          <Avatar size={80} icon={<UserOutlined />} style={{ backgroundColor: "#fff", color: "#1890ff" }} />
          <div>
            <Title level={2} style={{ color: "#fff", marginBottom: 4 }}>
              {user?.full_name || user?.fullName || "User"}
            </Title>
            <Space direction="vertical" size={2}>
              <Space>
                <PhoneOutlined />
                <Text style={{ color: "rgba(255,255,255,0.9)" }}>{user?.phone_number || user?.phoneNumber || "-"}</Text>
              </Space>
              <Text style={{ color: "rgba(255,255,255,0.75)" }}>
                Patient ID: {patientId || "-"}
              </Text>
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
              <Button type="primary" icon={<SaveOutlined />} onClick={() => form.submit()} loading={loading}>
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
                rules={[{ required: true, message: "Please enter your full name" }]}
              >
                <Input prefix={<UserOutlined />} placeholder="Full Name" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item label="Email Address" name="email" rules={[{ type: "email", message: "Please enter a valid email" }]}>
                <Input prefix={<MailOutlined />} placeholder="Email Address" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item label="Date of Birth" name="dateOfBirth">
                <DatePicker style={{ width: "100%" }} format="YYYY-MM-DD" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item label="Emergency Contact" name="emergencyContact">
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

      <Card
        title={
          <Space>
            <MedicineBoxOutlined />
            <span>Medical History</span>
          </Space>
        }
      >
        <Space direction="vertical" size="middle" style={{ width: "100%" }}>
          <Card size="small" type="inner">
            <Title level={5}>Allergies</Title>
            <Text type="secondary">None reported</Text>
          </Card>
          <Card size="small" type="inner">
            <Title level={5}>Current Medications</Title>
            <Text type="secondary">None reported</Text>
          </Card>
          <Card size="small" type="inner">
            <Title level={5}>Chronic Conditions</Title>
            <Text type="secondary">None reported</Text>
          </Card>
          <Button block disabled>
            Update Medical History
          </Button>
        </Space>
      </Card>
    </Space>
  )
}

export default Profile
