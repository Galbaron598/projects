import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Avatar, Dropdown, Space, Button } from 'antd'
import {
  DashboardOutlined,
  CalendarOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuOutlined,
  MedicineBoxOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { message } from 'antd'
import '../styles/Layout.css'

const { Header, Content, Footer, Sider } = AntLayout

const Layout = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    message.success('Logged out successfully')
    navigate('/login')
  }

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/appointments',
      icon: <CalendarOutlined />,
      label: 'Appointments',
    },
    {
      key: '/book',
      icon: <MedicineBoxOutlined />,
      label: 'Book Appointment',
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'My Profile',
      onClick: () => navigate('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout,
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <AntLayout className="layout-container">
      {/* Desktop Sidebar */}
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        collapsed={collapsed}
        onCollapse={setCollapsed}
        className="layout-sider"
      >
        <div className="layout-logo">
          <MedicineBoxOutlined className="layout-logo-icon" />
          {!collapsed && 'MediCare'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      {/* Main Layout */}
      <AntLayout style={{ marginLeft: collapsed ? 0 : 200 }}>
        {/* Header */}
        <Header className="layout-header">
          <div className="layout-header-left">
            {/* Mobile menu button */}
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="layout-mobile-menu-button"
            />
            <h2 className="layout-header-title">
              Medical Scheduling System
            </h2>
          </div>

          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space className="layout-user-menu">
              <Avatar 
                icon={<UserOutlined />} 
                style={{ backgroundColor: '#1890ff' }} 
              />
            </Space>
          </Dropdown>
        </Header>

        {/* Content */}
        <Content className="layout-content">
          <div className="content-container">
            <Outlet />
          </div>
        </Content>

        {/* Footer */}
        <Footer className="layout-footer">
          MediCare Medical Scheduling System ©{new Date().getFullYear()} Created for CORTEX
        </Footer>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout