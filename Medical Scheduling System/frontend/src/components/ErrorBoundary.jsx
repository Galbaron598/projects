import { Component } from 'react'
import Error from './Error'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  handleReset = () => {
    this.setState({ 
      hasError: false,
      error: null,
      errorInfo: null
    })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <Error
          type="error"
          title="Application Error"
          message="We're sorry for the inconvenience. The application encountered an unexpected error."
          onRetry={this.handleReset}
          fullScreen={true}
        />
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary