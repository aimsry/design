// src/components/nodes/StartNode.tsx
import React from 'react';
import { Handle, Position } from 'reactflow';
import { PlayCircleOutlined } from '@ant-design/icons';
import { Card, Typography } from 'antd';

const { Text } = Typography;

const StartNode = ({ data }: any) => {
  return (
    <Card 
      size="small" 
      style={{ width: 120, textAlign: 'center' }}
      hoverable
    >
      <PlayCircleOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
      <br />
      <Text strong>{data.label}</Text>
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#555' }}
      />
    </Card>
  );
};

export default StartNode;