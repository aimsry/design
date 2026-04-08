import React from 'react';
import { Form, Input, Select, Row, Col, Divider } from 'antd';
import { UserOutlined } from '@ant-design/icons';
const { Option } = Select;
interface PatientBasicInfoFormData {
  name: string;
  gender: 'male' | 'female';
  age: number;
  department?: string;
  phone?: string;
  id_card?: string;
}
interface PatientInfoFormProps {
  initialValues?: Partial<PatientBasicInfoFormData>;
}
export const PatientInfoForm: React.FC<PatientInfoFormProps> = ({
  initialValues
}) => {
  return (
    <>
      <Divider style={{ textAlign: 'left', margin: '16px 0' }}>
        <UserOutlined /> 基本信息
      </Divider>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item
            name="name"
            label="姓名"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input placeholder="请输入姓名" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="gender"
            label="性别"
            rules={[{ required: true, message: '请选择性别' }]}
          >
            <Select placeholder="请选择性别">
              <Option value="male">男</Option>
              <Option value="female">女</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="age"
            label="年龄"
            rules={[{ required: true, message: '请输入年龄' }]}
          >
            <Input type="number" placeholder="请输入年龄" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="department" label="科室">
            <Select placeholder="请选择科室">
              <Option value="全科">全科</Option>
              <Option value="内科">内科</Option>
              <Option value="外科">外科</Option>
              <Option value="儿科">儿科</Option>
              <Option value="妇产科">妇产科</Option>
              <Option value="神经科">神经科</Option>
              <Option value="心血管科">心血管科</Option>
              <Option value="呼吸科">呼吸科</Option>
              <Option value="消化科">消化科</Option>
              <Option value="内分泌科">内分泌科</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="phone" label="联系电话">
            <Input placeholder="请输入联系电话" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="id_card" label="身份证号">
            <Input placeholder="请输入身份证号" />
          </Form.Item>
        </Col>
      </Row>
    </>
  );
};
export default PatientInfoForm;
