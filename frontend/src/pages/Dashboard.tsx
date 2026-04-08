// src/pages/Dashboard.tsx
import React from 'react';
import { Card, Typography, Space } from 'antd';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* 装饰性卡片 */}
      <Card title="系统概览" bordered={false}>
        <Space size="middle">
          <Card size="small" style={{ width: 200, textAlign: 'center' }}>
            <Text strong>今日诊断</Text>
            <br />
            <Text type="success" style={{ fontSize: '24px' }}>24</Text>
          </Card>
          <Card size="small" style={{ width: 200, textAlign: 'center' }}>
            <Text strong>待处理</Text>
            <br />
            <Text type="warning" style={{ fontSize: '24px' }}>8</Text>
          </Card>
          <Card size="small" style={{ width: 200, textAlign: 'center' }}>
            <Text strong>系统状态</Text>
            <br />
            <Text type="success">正常运行</Text>
          </Card>
        </Space>
      </Card>

      {/* 功能介绍卡片 */}
      <Card title="功能特色" bordered={false}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Card size="small">
            <Text strong>🤖 AI智能诊断</Text>
            <br />
            <Text type="secondary">基于大语言模型的智能症状分析和诊断建议</Text>
          </Card>
          <Card size="small">
            <Text strong>📊 可视化流程</Text>
            <br />
            <Text type="secondary">直观的诊断流程图展示和管理</Text>
          </Card>
          <Card size="small">
            <Text strong>💾 数据管理</Text>
            <br />
            <Text type="secondary">完整的患者信息和诊断记录管理</Text>
          </Card>
        </Space>
      </Card>

      {/* 快捷操作卡片 */}
      <Card title="快捷操作" bordered={false}>
        <Space>
          <Card hoverable style={{ width: 150, textAlign: 'center' }}>
            <Text>新建诊断</Text>
          </Card>
          <Card hoverable style={{ width: 150, textAlign: 'center' }}>
            <Text>查看报告</Text>
          </Card>
          <Card hoverable style={{ width: 150, textAlign: 'center' }}>
            <Text>系统设置</Text>
          </Card>
        </Space>
      </Card>
    </Space>
  );
};

export default Dashboard;