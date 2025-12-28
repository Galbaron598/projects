import { useState } from "react";
import { Card, Form, Input, Button, Space, Typography, Row, Col, Avatar, Divider, List, Modal, DatePicker, message as antMessage } from "antd";
import {
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  EditOutlined,
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
  TeamOutlined,
  MedicineBoxOutlined,
} from "@ant-design/icons";

import "../styles/Profile.css";
import { useAuthStore } from "../store/authStore";
import { userAPI } from "../services/api";
import dayjs from "dayjs";


const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

const Profile = () => {
  const { user, updateUser } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [addMemberModalVisible, setAddMemberModalVisible] = useState(false)
  const [familyMembers, setFamilyMembers] = useState([
    { id: 1, name: 'Jane Doe', relationship: 'Spouse', dateOfBirth: '1990-03-20' },
  ])
  
  const [form] = Form.useForm()
  const [memberForm] = Form.useForm()

  const initialValues = {
    fullName: user?.fullName || '',
    email: user?.email || '',
    dateOfBirth: user?.dateOfBirth ? dayjs(user.dateOfBirth) : null,
    address: user?.address || '',
    emergencyContact: user?.emergencyContact || '',
  }

  const handleSaveProfile = async (values) => {
    setLoading(true)
    try {
      const updatedData = {
        ...values,
        dateOfBirth: values.dateOfBirth?.format('YYYY-MM-DD'),
      }
      
      updateUser(updatedData)
      antMessage.success('Profile updated successfully')
      setIsEditing(false)
      
      // Uncomment for real API
      // await userAPI.updateProfile(updatedData)
    } catch (error) {
      antMessage.error('Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleAddFamilyMember = async (values) => {
    try {
      const newMember = {
        id: Date.now(),
        ...values,
        dateOfBirth: values.dateOfBirth.format('YYYY-MM-DD'),
      }
      
      setFamilyMembers([...familyMembers, newMember])
      antMessage.success('Family member added successfully')
      setAddMemberModalVisible(false)
      memberForm.resetFields()
      
      // Uncomment for real API
      // await userAPI.addFamilyMember(newMember)
    } catch (error) {
      antMessage.error('Failed to add family member')
    }
  }

  const handleRemoveFamilyMember = (id) => {
    Modal.confirm({
      title: 'Remove Family Member',
      content: 'Are you sure you want to remove this family member?',
      okText: 'Yes, Remove',
      okType: 'danger',
      onOk: () => {
        setFamilyMembers(familyMembers.filter((m) => m.id !== id))
        antMessage.success('Family member removed')
        
        // Uncomment for real API
        // await userAPI.removeFamilyMember(id)
      },
    })
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Profile Header */}
      <Card
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
              {user?.fullName || 'User'}
            </Title>
            <Space>
              <PhoneOutlined />
              <Text style={{ color: 'rgba(255,255,255,0.9)' }}>{user?.phoneNumber}</Text>
            </Space>
          </div>
        </Space>
      </Card>

      {/* Personal Information */}
      <Card
        title={
          <Space>
            <UserOutlined />
            <span>Personal Information</span>
          </Space>
        }
        extra={
          !isEditing ? (
            <Button icon={<EditOutlined />} onClick={() => setIsEditing(true)}>
              Edit
            </Button>
          ) : (
            <Space>
              <Button onClick={() => {
                setIsEditing(false)
                form.resetFields()
              }}>
                Cancel
              </Button>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={() => form.submit()}
                loading={loading}
              >
                Save
              </Button>
            </Space>
          )
        }
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={initialValues}
          onFinish={handleSaveProfile}
          disabled={!isEditing}
        >
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
                rules={[
                  { type: 'email', message: 'Please enter a valid email' },
                ]}
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
              <Form.Item label="Emergency Contact" name="emergencyContact">
                <Input prefix={<PhoneOutlined />} placeholder="Emergency Contact Number" />
              </Form.Item>
            </Col>
            <Col xs={24}>
              <Form.Item label="Address" name="address">
                <TextArea
                  prefix={<EnvironmentOutlined />}
                  placeholder="Your complete address"
                  rows={3}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {/* Family Members */}
      <Card
        title={
          <Space>
            <TeamOutlined />
            <span>Family Members</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setAddMemberModalVisible(true)}
          >
            Add Member
          </Button>
        }
      >
        <Paragraph type="secondary">
          Book appointments for your family members
        </Paragraph>
        
        {familyMembers.length > 0 ? (
          <List
            dataSource={familyMembers}
            renderItem={(member) => (
              <List.Item
                actions={[
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemoveFamilyMember(member.id)}
                  >
                    Remove
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={<Avatar icon={<UserOutlined />} />}
                  title={member.name}
                  description={
                    <Space direction="vertical" size="small">
                      <Text type="secondary">{member.relationship}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        DOB: {member.dateOfBirth}
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Text type="secondary">No family members added yet</Text>
        )}
      </Card>

      {/* Medical History */}
      <Card
        title={
          <Space>
            <MedicineBoxOutlined />
            <span>Medical History</span>
          </Space>
        }
      >
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
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
          <Button block>Update Medical History</Button>
        </Space>
      </Card>

      {/* Add Family Member Modal */}
      <Modal
        title="Add Family Member"
        open={addMemberModalVisible}
        onOk={() => memberForm.submit()}
        onCancel={() => {
          setAddMemberModalVisible(false)
          memberForm.resetFields()
        }}
        okText="Add Member"
      >
        <Form form={memberForm} layout="vertical" onFinish={handleAddFamilyMember}>
          <Form.Item
            label="Full Name"
            name="name"
            rules={[{ required: true, message: 'Please enter name' }]}
          >
            <Input placeholder="Full Name" />
          </Form.Item>
          <Form.Item
            label="Relationship"
            name="relationship"
            rules={[{ required: true, message: 'Please enter relationship' }]}
          >
            <Input placeholder="e.g., Spouse, Child, Parent" />
          </Form.Item>
          <Form.Item
            label="Date of Birth"
            name="dateOfBirth"
            rules={[{ required: true, message: 'Please select date of birth' }]}
          >
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}

export default Profile