// src/components/nodes/EndNode.tsx
import React from 'react';
import { Handle, Position } from 'reactflow';
import { StopOutlined } from '@ant-design/icons';
import { Card, Typography } from 'antd';

const { Text } = Typography;

const EndNode = ({ data }: any) => {
  return (
    <Card 
      size="small" 
      style={{ width: 120, textAlign: 'center' }}
      hoverable
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#555' }}
      />
      <StopOutlined style={{ fontSize: '24px', color: '#ff4d4f' }} />
      <br />
      <Text strong>{data.label}</Text>
    </Card>
  );
};

export default EndNode;