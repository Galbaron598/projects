import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Typography, Space, Alert, Row, Col } from 'antd'
import { PhoneOutlined, SafetyOutlined, MedicineBoxOutlined } from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../services/api'
import { message } from 'antd'
import { validatePhoneNumber, generateMockOTP, getErrorMessage } from '../utils/helpers'
import "../styles/Login.css"

const { Title, Text, Paragraph } = Typography

const Login = () => {
  const [step, setStep] = useState('phone') // 'phone' or 'otp'
  const [phoneNumber, setPhoneNumber] = useState('')
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [mockOtp, setMockOtp] = useState('')
  const otpRefs = useRef([])
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const [form] = Form.useForm()

  useEffect(() => {
    if (step === 'otp' && otpRefs.current[0]) {
      otpRefs.current[0].focus()
    }
  }, [step])

  const handlePhoneSubmit = async (values) => {
    const phone = values.phoneNumber.replace(/\D/g, '')
    
    if (!validatePhoneNumber(phone)) {
      message.error('Please enter a valid 10-digit phone number')
      return
    }

    setLoading(true)
    try {
      // Generate mock OTP
      const generatedOtp = generateMockOTP()
      setMockOtp(generatedOtp)
      setPhoneNumber(phone)
      
      // In production, call API to send real OTP
      // await authAPI.sendOTP(phone)
      
      message.success(`OTP sent to ${phone}`)
      console.log('Mock OTP:', generatedOtp)
      setStep('otp')
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const handleOtpChange = (index, value) => {
    if (!/^\d*$/.test(value)) return

    const newOtp = [...otp]
    newOtp[index] = value.slice(-1) // Only take last character

    setOtp(newOtp)

    // Auto-focus next input
    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus()
    }
  }

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace') {
      if (!otp[index] && index > 0) {
        otpRefs.current[index - 1]?.focus()
      }
    }
  }

  const handleOtpPaste = (e) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    const newOtp = pastedData.split('').concat(Array(6 - pastedData.length).fill(''))
    setOtp(newOtp.slice(0, 6))
    
    const nextEmptyIndex = newOtp.findIndex((digit) => !digit)
    if (nextEmptyIndex !== -1 && nextEmptyIndex < 6) {
      otpRefs.current[nextEmptyIndex]?.focus()
    } else {
      otpRefs.current[5]?.focus()
    }
  }

  const handleOtpSubmit = async () => {
    const otpValue = otp.join('')
    if (otpValue.length !== 6) {
      message.error('Please enter complete OTP')
      return
    }

    setLoading(true)
    try {
      // Mock verification
      if (otpValue === mockOtp) {
        const mockUser = {
          id: Date.now(),
          phoneNumber: phoneNumber,
          fullName: 'John Doe',
          email: 'john.doe@example.com',
          isNewUser: false,
        }
        const mockToken = 'mock-jwt-token-' + Date.now()
        
        login(mockUser, mockToken)
        message.success('Login successful!')
        navigate('/dashboard')
      } else {
        message.error('Invalid OTP. Please try again.')
        setOtp(['', '', '', '', '', ''])
        otpRefs.current[0]?.focus()
      }
      
      // In production, call API
      // const response = await authAPI.verifyOTP(phoneNumber, otpValue)
      // login(response.data.user, response.data.token)
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const handleResendOTP = () => {
    const newOtp = generateMockOTP()
    setMockOtp(newOtp)
    console.log('New Mock OTP:', newOtp)
    message.success('OTP resent successfully')
    setOtp(['', '', '', '', '', ''])
    otpRefs.current[0]?.focus()
  }

  return (
    <div className="login-container" style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <Row gutter={[32, 32]} style={{ maxWidth: 1200, width: '100%' }}>
        {/* Left side - Branding */}
        <Col xs={24} lg={12} style={{ display: 'flex', alignItems: 'center' }}>
          <div className="login-container" style={{ color: '#fff' }}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Space align="center" size="middle">
                  <MedicineBoxOutlined style={{ fontSize: 48 }} />
                  <Title level={1} style={{ color: '#fff', margin: 0 }}>
                    MediCare
                  </Title>
                </Space>
                <Paragraph style={{ color: 'rgba(255,255,255,0.9)', fontSize: 18, marginTop: 8 }}>
                  Your Health, Our Priority
                </Paragraph>
              </div>

              <div>
                <Space direction="vertical" size="middle">
                  <div>
                    <SafetyOutlined style={{ fontSize: 32, marginBottom: 8 }} />
                    <Title level={4} style={{ color: '#fff' }}>Secure & Private</Title>
                    <Text style={{ color: 'rgba(255,255,255,0.85)' }}>
                      Your medical information is protected with bank-level security
                    </Text>
                  </div>
                  <div>
                    <PhoneOutlined style={{ fontSize: 32, marginBottom: 8 }} />
                    <Title level={4} style={{ color: '#fff' }}>Easy Access</Title>
                    <Text style={{ color: 'rgba(255,255,255,0.85)' }}>
                      Book appointments anytime, anywhere with just a few taps
                    </Text>
                  </div>
                </Space>
              </div>
            </Space>
          </div>
        </Col>

        {/* Right side - Login Form */}
        <Col xs={24} lg={12}>
          <Card
            style={{
              boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
              borderRadius: 16,
              maxWidth: 480,
              margin: '0 auto'
            }}
          >
            {step === 'phone' ? (
              <>
                <Title level={2}>Welcome Back</Title>
                <Paragraph type="secondary">
                  Enter your phone number to continue
                </Paragraph>

                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handlePhoneSubmit}
                  style={{ marginTop: 24 }}
                >
                  <Form.Item
                    label="Phone Number"
                    name="phoneNumber"
                    rules={[
                      { required: true, message: 'Please enter your phone number' },
                      {
                        validator: (_, value) => {
                          if (!value || validatePhoneNumber(value)) {
                            return Promise.resolve()
                          }
                          return Promise.reject(new Error('Please enter a valid 10-digit phone number'))
                        }
                      }
                    ]}
                  >
                    <Input
                      prefix={<PhoneOutlined />}
                      placeholder="Enter 10-digit phone number"
                      size="large"
                      maxLength={10}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '')
                        form.setFieldsValue({ phoneNumber: value })
                      }}
                    />
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      size="large"
                      block
                      loading={loading}
                    >
                      Continue
                    </Button>
                  </Form.Item>

                  <Text type="secondary" style={{ fontSize: 12 }}>
                    We'll send you a one-time password via SMS
                  </Text>
                </Form>
              </>
            ) : (
              <>
                <Button
                  type="link"
                  onClick={() => setStep('phone')}
                  style={{ padding: 0, marginBottom: 16 }}
                >
                  ← Change number
                </Button>

                <Title level={2}>Verify OTP</Title>
                <Paragraph type="secondary">
                  Enter the 6-digit code sent to <strong>{phoneNumber}</strong>
                </Paragraph>

                {mockOtp && (
                  <Alert
                    message={`Test OTP: ${mockOtp}`}
                    type="warning"
                    showIcon
                    style={{ marginBottom: 24 }}
                    description="This is a mock OTP for testing. In production, you'll receive it via SMS."
                  />
                )}

                <Space direction="vertical" size="large" style={{ width: '100%', marginTop: 24 }}>
                  <div className="login-container" style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                    {otp.map((digit, index) => (
                      <Input
                        key={index}
                        ref={(el) => (otpRefs.current[index] = el)}
                        value={digit}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleOtpKeyDown(index, e)}
                        onPaste={index === 0 ? handleOtpPaste : undefined}
                        maxLength={1}
                        style={{
                          width: '100%',
                          height: 56,
                          fontSize: 24,
                          textAlign: 'center',
                          fontWeight: 'bold'
                        }}
                      />
                    ))}
                  </div>

                  <Button
                    type="primary"
                    size="large"
                    block
                    loading={loading}
                    onClick={handleOtpSubmit}
                    disabled={otp.join('').length !== 6}
                  >
                    Verify & Continue
                  </Button>

                  <div className="login-container" style={{ textAlign: 'center' }}>
                    <Text type="secondary">Didn't receive code? </Text>
                    <Button type="link" onClick={handleResendOTP} style={{ padding: 0 }}>
                      Resend
                    </Button>
                  </div>
                </Space>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Login