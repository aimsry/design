import React from 'react';
import { Card, Button, Space, Row, Col, Input, DatePicker } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

interface LabData {
  test_name: string;
  value: string;
  unit: string;
  reference_range: string;
  date: string;
}

interface LabFormProps {
  labResults: LabData[];
  onAdd: () => void;
  onUpdate: (index: number, field: keyof LabData, value: string) => void;
  onRemove: (index: number) => void;
}

export const LabForm: React.FC<LabFormProps> = ({
  labResults,
  onAdd,
  onUpdate,
  onRemove
}) => {
  const handleDateChange = (index: number, dateString: string | null) => {
    if (dateString) {
      onUpdate(index, 'date', dateString);
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 8 }}>
        <Button size="small" icon={<PlusOutlined />} onClick={onAdd}>
          添加检验结果
        </Button>
      </Space>

      {labResults.map((lab, index) => (
        <Card size="small" key={index} style={{ marginBottom: 8 }}>
          <Row gutter={8}>
            <Col span={5}>
              <Input
                placeholder="检验项目名称"
                value={lab.test_name}
                onChange={(e) => onUpdate(index, 'test_name', e.target.value)}
                size="small"
              />
            </Col>
            <Col span={4}>
              <Input
                placeholder="结果值"
                value={lab.value}
                onChange={(e) => onUpdate(index, 'value', e.target.value)}
                size="small"
              />
            </Col>
            <Col span={3}>
              <Input
                placeholder="单位"
                value={lab.unit}
                onChange={(e) => onUpdate(index, 'unit', e.target.value)}
                size="small"
              />
            </Col>
            <Col span={5}>
              <Input
                placeholder="参考范围"
                value={lab.reference_range}
                onChange={(e) => onUpdate(index, 'reference_range', e.target.value)}
                size="small"
              />
            </Col>
            <Col span={4}>
              <DatePicker
                value={lab.date ? dayjs(lab.date) : null}
                onChange={(date, dateString) => handleDateChange(index, dateString)}
                size="small"
                style={{ width: '100%' }}
                format="YYYY-MM-DD"
              />
            </Col>
            <Col span={3}>
              <Button
                danger
                size="small"
                icon={<DeleteOutlined />}
                onClick={() => onRemove(index)}
                style={{ width: '100%' }}
              >
                删除
              </Button>
            </Col>
          </Row>
        </Card>
      ))}
    </div>
  );
};

export default LabForm;
