import React from 'react';
import { Form, Input, Divider } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';

export const SymptomsHistoryForm: React.FC = () => {
  return (
    <>
      <Divider style={{ textAlign: 'left', margin: '16px 0' }}>
        <FileTextOutlined /> 症状与病史
      </Divider>

      <Form.Item
        name="symptoms"
        label="主诉症状"
        rules={[{ required: true, message: '请输入主诉症状' }]}
      >
        <Input.TextArea rows={3} placeholder="请描述患者的主要症状" />
      </Form.Item>

      <Form.Item
        name="medical_history"
        label="既往病史"
        rules={[{ required: true, message: '请输入既往病史' }]}
      >
        <Input.TextArea rows={3} placeholder="请描述患者的既往病史、过敏史等" />
      </Form.Item>
    </>
  );
};

export default SymptomsHistoryForm;
