import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Typography, Space, Alert, Row, Col, message } from 'antd'
import { PhoneOutlined, SafetyOutlined, MedicineBoxOutlined } from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../services/api'
import { validatePhoneNumber, getErrorMessage } from '../utils/helpers'
import '../styles/Login.css'

const { Title, Text, Paragraph } = Typography

const Login = () => {
  const [step, setStep] = useState('phone')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)

  // Keep this ONLY for dev/testing (your backend returns debug.otp)
  const [debugOtp, setDebugOtp] = useState('')

  const otpRefs = useRef([])
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const [form] = Form.useForm()

  useEffect(() => {
    if (step === 'otp') {
      setTimeout(() => otpRefs.current[0]?.focus(), 0)
    }
  }, [step])

  const handlePhoneSubmit = async (values) => {
    const phone = (values.phoneNumber || '').replace(/\D/g, '')

    if (!validatePhoneNumber(phone)) {
      message.error('Please enter a valid 10-digit phone number')
      return
    }

    setLoading(true)
    try {
      setPhoneNumber(phone)

      // Call auth-service
      const res = await authAPI.requestOTP(phone)

      // Optional: show debug OTP if backend returns it
      const otpFromServer = res?.data?.debug?.otp
      setDebugOtp(otpFromServer || '')

      message.success(`OTP sent to ${phone}`)
      setStep('otp')
      setOtp(['', '', '', '', '', ''])
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const handleOtpChange = (index, value) => {
    if (!/^\d*$/.test(value)) return

    const newOtp = [...otp]
    newOtp[index] = value.slice(-1)
    setOtp(newOtp)

    if (value && index < 5) otpRefs.current[index + 1]?.focus()
  }

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace') {
      if (!otp[index] && index > 0) otpRefs.current[index - 1]?.focus()
    }
  }

  const handleOtpPaste = (e) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    const next = pasted.split('').concat(Array(6 - pasted.length).fill(''))
    setOtp(next)

    const nextEmptyIndex = next.findIndex((d) => !d)
    if (nextEmptyIndex !== -1) otpRefs.current[nextEmptyIndex]?.focus()
    else otpRefs.current[5]?.focus()
  }

  const handleOtpSubmit = async () => {
    const otpValue = otp.join('')

    if (otpValue.length !== 6) {
      message.error('Please enter complete OTP')
      return
    }

    setLoading(true)
    try {
      // Call auth-service verify
      const res = await authAPI.verifyOTP(phoneNumber, otpValue)

      const token = res?.data?.token
      const user = res?.data?.user

      if (!token || !user) {
        message.error('Login failed: missing token/user from server')
        return
      }

      // Normalize user shape for store 
      const normalizedUser = {
        id: user.phoneNumber, //  phone is a stable key for start
        phoneNumber: user.phoneNumber,
        fullName: user.full_name || 'User',
        email: user.email || '',
        isNewUser: !!user.isNewUser,
        createdAt: user.createdAt,
      }

      login(normalizedUser, token)
      message.success('Login successful!')
      navigate('/dashboard')
    } catch (error) {
      message.error(getErrorMessage(error))
      setOtp(['', '', '', '', '', ''])
      otpRefs.current[0]?.focus()
    } finally {
      setLoading(false)
    }
  }

  const handleResendOTP = async () => {
    if (!phoneNumber) return

    setLoading(true)
    try {
      const res = await authAPI.requestOTP(phoneNumber)
      const otpFromServer = res?.data?.debug?.otp
      setDebugOtp(otpFromServer || '')

      message.success('OTP resent successfully')
      setOtp(['', '', '', '', '', ''])
      otpRefs.current[0]?.focus()
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <Row className="login-row" gutter={[32, 32]}>
        {/* Left side - Branding */}
        <Col xs={24} lg={12} className="login-left-col">
          <div className="login-branding-panel">
            <div className="login-branding">
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div>
                  <Space align="center" size="middle">
                    <MedicineBoxOutlined className="login-branding-icon" />
                    <Title level={1} className="login-branding-title">
                      MediCare
                    </Title>
                  </Space>
                  <Paragraph className="login-branding-subtitle">Your Health, Our Priority</Paragraph>
                </div>

                <div>
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div className="login-feature">
                      <SafetyOutlined className="login-feature-icon" />
                      <Title level={4} className="login-feature-title">
                        Secure &amp; Private
                      </Title>
                      <Text className="login-feature-text">
                        Your medical information is protected with bank-level security
                      </Text>
                    </div>

                    <div className="login-feature">
                      <PhoneOutlined className="login-feature-icon" />
                      <Title level={4} className="login-feature-title">
                        Easy Access
                      </Title>
                      <Text className="login-feature-text">
                        Book appointments anytime, anywhere with just a few taps
                      </Text>
                    </div>
                  </Space>
                </div>
              </Space>
            </div>
          </div>
        </Col>

        {/* Right side - Login Form */}
        <Col xs={24} lg={12}>
          <Card className="login-card">
            {step === 'phone' ? (
              <>
                <Title level={2} className="login-title">
                  Welcome
                </Title>
                <Paragraph type="secondary" className="login-subtitle">
                  Enter your phone number to continue
                </Paragraph>

                <Form form={form} layout="vertical" onFinish={handlePhoneSubmit} className="login-form">
                  <Form.Item
                    label="Phone Number"
                    name="phoneNumber"
                    rules={[
                      { required: true, message: 'Please enter your phone number' },
                      {
                        validator: (_, value) => {
                          if (!value || validatePhoneNumber(value)) return Promise.resolve()
                          return Promise.reject(new Error('Please enter a valid 10-digit phone number'))
                        },
                      },
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
                    <Button type="primary" htmlType="submit" size="large" block loading={loading}>
                      Continue
                    </Button>
                  </Form.Item>

                  <Text type="secondary" className="login-form-note">
                    We'll send you a one-time password via SMS
                  </Text>
                </Form>
              </>
            ) : (
              <>
                <Button
                  type="link"
                  onClick={() => {
                    setStep('phone')
                    setOtp(['', '', '', '', '', ''])
                    setDebugOtp('')
                  }}
                  className="login-back-button"
                >
                  ← Change number
                </Button>

                <Title level={2}>Verify OTP</Title>
                <Paragraph type="secondary">
                  Enter the 6-digit code sent to <strong>{phoneNumber}</strong>
                </Paragraph>

                {!!debugOtp && (
                  <Alert
                    message={`Test OTP: ${debugOtp}`}
                    type="warning"
                    showIcon
                    className="login-otp-alert"
                    description="This is returned by the backend for development. In production you won’t show this."
                  />
                )}

                <Space direction="vertical" size="large" style={{ width: '100%', marginTop: 24 }}>
                  <div className="login-otp-container">
                    {otp.map((digit, index) => (
                      <Input
                        key={index}
                        ref={(el) => (otpRefs.current[index] = el)}
                        value={digit}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleOtpKeyDown(index, e)}
                        onPaste={index === 0 ? handleOtpPaste : undefined}
                        maxLength={1}
                        inputMode="numeric"
                        className="login-otp-input"
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
                    Verify &amp; Continue
                  </Button>

                  <div className="login-resend">
                    <Text type="secondary">Didn't receive code? </Text>
                    <Button type="link" onClick={handleResendOTP} className="login-resend-button" disabled={loading}>
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