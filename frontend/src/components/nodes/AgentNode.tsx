// src/components/nodes/AgentNode.tsx
import React from 'react';
import { Handle, Position } from 'reactflow';
import { RobotOutlined, MedicineBoxOutlined } from '@ant-design/icons';
import { Card, Typography, Tag, Tooltip } from 'antd';

const { Text } = Typography;

interface AgentNodeProps {
  data: {
    label: string;
    agentType: string;
    agentId?: string;
    description?: string;
  };
  selected?: boolean;
}

const AgentNode = ({ data, selected }: AgentNodeProps) => {
  return (
    <Tooltip title={data.description}>
      <Card
        size="small"
        style={{
          width: 180,
          textAlign: 'center',
          borderColor: selected ? '#1890ff' : undefined,
          boxShadow: selected ? '0 0 0 2px rgba(24, 144, 255, 0.2)' : undefined
        }}
        hoverable
      >
        <Handle
          type="target"
          position={Position.Left}
          style={{
            background: '#555',
            width: 12,
            height: 12
          }}
        />

        {data.agentType === 'llm_agent' ? (
          <MedicineBoxOutlined style={{ fontSize: '28px', color: '#1890ff' }} />
        ) : (
          <RobotOutlined style={{ fontSize: '28px', color: '#1890ff' }} />
        )}

        <br />
        <Text strong style={{ fontSize: '12px' }}>{data.label}</Text>
        <br />
        <Tag color="blue" style={{ marginTop: 4 }}>{data.agentType}</Tag>

        <Handle
          type="source"
          position={Position.Right}
          style={{
            background: '#555',
            width: 12,
            height: 12
          }}
        />
      </Card>
    </Tooltip>
  );
};

export default AgentNode;
