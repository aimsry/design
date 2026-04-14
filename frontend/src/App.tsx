// frontend/src/App.tsx
import React, { useState } from 'react';
import { Layout, Menu, Card, Typography, Space } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  FileTextOutlined,
  SettingOutlined,
  HeartTwoTone,
  PartitionOutlined,
  PlayCircleOutlined  // 新增导入
} from '@ant-design/icons';
import WorkflowBuilder from './pages/WorkflowBuilder';
import WorkflowExecutor from './pages/WorkflowExecutor';  // 新增导入
import Dashboard from './pages/Dashboard';
import './App.css';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderContent = () => {
    switch(currentView) {
      case 'workflow':
        return <WorkflowBuilder />;
      case 'workflow-executor':  // 新增case
        return <WorkflowExecutor />;
      case 'dashboard':
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 左侧导航栏 */}
      <Sider theme="light" width={250}>
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <HeartTwoTone twoToneColor="#eb2f96" style={{ fontSize: '32px' }} />
          <Title level={4} style={{ margin: '8px 0 0 0' }}>医疗诊断系统</Title>
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['dashboard']}
          selectedKeys={[currentView]}
          onClick={({ key }) => setCurrentView(key)}
          style={{ borderRight: 0 }}
        >
          <Menu.Item key="dashboard" icon={<HomeOutlined />}>
            首页
          </Menu.Item>
          <Menu.Item key="workflow" icon={<PartitionOutlined />}>
            工作流编排
          </Menu.Item>
          <Menu.Item key="workflow-executor" icon={<PlayCircleOutlined />}>
            工作流执行
          </Menu.Item>
          <Menu.Item key="patients" icon={<UserOutlined />}>
            患者管理
          </Menu.Item>
          <Menu.Item key="records" icon={<FileTextOutlined />}>
            诊断记录
          </Menu.Item>
          <Menu.Item key="settings" icon={<SettingOutlined />}>
            系统设置
          </Menu.Item>
        </Menu>
      </Sider>

      {/* 主要内容区域 */}
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <Title level={3} style={{ lineHeight: '64px', margin: 0 }}>
            {currentView === 'dashboard' && '欢迎使用医疗诊断系统'}
            {currentView === 'workflow' && '工作流编排'}
            {currentView === 'workflow-executor' && '工作流执行'}
            {currentView === 'patients' && '患者管理'}
            {currentView === 'records' && '诊断记录'}
            {currentView === 'settings' && '系统设置'}
          </Title>
        </Header>

        <Content style={{ margin: '24px', padding: '24px', background: '#fff', borderRadius: '8px' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;