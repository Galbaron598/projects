import { Result, Button, Alert, Collapse, Typography } from 'antd'
import { 
  FrownOutlined, 
  CloseCircleOutlined, 
  WarningOutlined,
  ExclamationCircleOutlined,
  BugOutlined,
  InfoCircleOutlined
} from '@ant-design/icons'
import '../styles/Error.css'

const { Text, Paragraph } = Typography

const Error = ({ 
  type = 'error',
  title,
  message,
  error, // Accept error object from server/catch block
  statusCode, // HTTP status code
  details, // Additional error details
  technicalInfo, // Technical/debug information
  onRetry,
  showRetry = true,
  extra,
  fullScreen = false,
  showTechnicalDetails = false, // Show/hide technical details
}) => {
  // Parse error object if provided
  const parseError = () => {
    if (!error) return null

    // Handle Axios error
    if (error.response) {
      return {
        statusCode: error.response.status,
        message: error.response.data?.message || error.response.data?.error || error.message,
        details: error.response.data?.details,
        technicalInfo: {
          url: error.config?.url,
          method: error.config?.method,
          data: error.response.data,
        }
      }
    }

    // Handle network error
    if (error.request) {
      return {
        statusCode: 0,
        message: 'Network error. Please check your internet connection.',
        details: 'Unable to reach the server',
        technicalInfo: {
          request: error.request,
        }
      }
    }

    // Handle generic error
    return {
      message: error.message || String(error),
      technicalInfo: {
        stack: error.stack,
      }
    }
  }

  const parsedError = parseError()
  const finalStatusCode = statusCode || parsedError?.statusCode
  const finalMessage = message || parsedError?.message
  const finalDetails = details || parsedError?.details
  const finalTechnicalInfo = technicalInfo || parsedError?.technicalInfo

  const getStatus = () => {
    // Use status code if provided
    if (finalStatusCode) {
      if (finalStatusCode >= 500) return '500'
      if (finalStatusCode === 404) return '404'
      if (finalStatusCode === 403) return '403'
      if (finalStatusCode === 401) return '403'
      if (finalStatusCode === 400) return 'warning'
    }

    const statusMap = {
      error: '500',
      warning: 'warning',
      info: 'info',
      notFound: '404',
      unauthorized: '403',
      network: 'error',
      validation: 'warning',
    }
    return statusMap[type] || '500'
  }

  const getIcon = () => {
    const iconMap = {
      error: <CloseCircleOutlined />,
      warning: <WarningOutlined />,
      info: <ExclamationCircleOutlined />,
      notFound: <FrownOutlined />,
      unauthorized: <ExclamationCircleOutlined />,
      network: <InfoCircleOutlined />,
      validation: <WarningOutlined />,
    }
    return iconMap[type]
  }

  const getDefaultTitle = () => {
    // Title based on status code
    if (finalStatusCode) {
      if (finalStatusCode >= 500) return 'Server Error'
      if (finalStatusCode === 404) return 'Not Found'
      if (finalStatusCode === 403) return 'Forbidden'
      if (finalStatusCode === 401) return 'Unauthorized'
      if (finalStatusCode === 400) return 'Bad Request'
      if (finalStatusCode === 0) return 'Network Error'
    }

    const titleMap = {
      error: 'Something went wrong',
      warning: 'Warning',
      info: 'Information',
      notFound: 'Not Found',
      unauthorized: 'Unauthorized',
      network: 'Connection Error',
      validation: 'Validation Error',
    }
    return titleMap[type] || 'Error'
  }

  const getDefaultMessage = () => {
    const messageMap = {
      error: 'We encountered an error while processing your request.',
      warning: 'Please check the information and try again.',
      info: 'This action requires additional permissions.',
      notFound: 'The page you are looking for does not exist.',
      unauthorized: 'You do not have permission to access this resource.',
      network: 'Unable to connect to the server. Please check your internet connection.',
      validation: 'Please check your input and try again.',
    }
    return messageMap[type] || 'An error occurred'
  }

  const containerClass = `error-container ${fullScreen ? 'fullscreen' : 'inline'}`

  return (
    <div className={containerClass}>
      <div className="error-content">
        <Result
          status={getStatus()}
          icon={getIcon()}
          title={title || getDefaultTitle()}
          subTitle={
            <div className="error-details">
              <Paragraph>{finalMessage || getDefaultMessage()}</Paragraph>
              
              {/* Show status code if available */}
              {finalStatusCode && (
                <Alert
                  className="error-alert"
                  message={`Error Code: ${finalStatusCode}`}
                  type="error"
                  showIcon
                />
              )}

              {/* Show additional details */}
              {finalDetails && typeof finalDetails === 'string' && (
                <Alert
                  className="error-alert"
                  message="Details"
                  description={finalDetails}
                  type="info"
                  showIcon
                />
              )}

              {/* Show validation errors if present */}
              {finalDetails && Array.isArray(finalDetails) && (
                <Alert
                  className="error-alert"
                  message="Validation Errors"
                  description={
                    <ul className="error-validation-list">
                      {finalDetails.map((detail, index) => (
                        <li key={index}>{detail}</li>
                      ))}
                    </ul>
                  }
                  type="warning"
                  showIcon
                />
              )}

              {/* Technical information (collapsible) */}
              {showTechnicalDetails && finalTechnicalInfo && (
                <Collapse 
                  ghost 
                  className="error-technical-details"
                  items={[
                    {
                      key: '1',
                      label: (
                        <Text type="secondary">
                          <BugOutlined /> Technical Details (Debug Info)
                        </Text>
                      ),
                      children: (
                        <pre className="error-technical-code">
                          {JSON.stringify(finalTechnicalInfo, null, 2)}
                        </pre>
                      )
                    }
                  ]}
                />
              )}
            </div>
          }
          extra={
            extra || (showRetry && onRetry && [
              <Button type="primary" key="retry" onClick={onRetry}>
                Try Again
              </Button>,
              <Button key="home" onClick={() => window.location.href = '/'}>
                Go Home
              </Button>
            ])
          }
        />
      </div>
    </div>
  )
}

export default Error