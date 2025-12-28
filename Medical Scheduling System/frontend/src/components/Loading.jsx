import { Spin } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import '../styles/Loading.css'

const Loading = ({ 
  size = 'large', 
  tip = 'Loading...', 
  fullScreen = false,
  spinning = true 
}) => {
  const antIcon = <LoadingOutlined className="loading-icon" spin />

  if (fullScreen) {
    return (
      <div className="loading-overlay">
        <div className="loading-spinner">
          <Spin indicator={antIcon} size={size} tip={tip} spinning={spinning} />
        </div>
      </div>
    )
  }

  return (
    <div className="loading-container">
      <div className="loading-spinner">
        <Spin indicator={antIcon} size={size} tip={tip} spinning={spinning} />
      </div>
    </div>
  )
}

export default Loading