import React, { ChangeEvent } from 'react';
import { Card, Button, Space, Row, Col, Input, DatePicker, Image } from 'antd';
import { PlusOutlined, DeleteOutlined, UploadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

interface ImageData {
  type: string;
  description: string;
  date: string;
  file?: File | null;
  previewUrl?: string | null;
}

interface ImageFormProps {
  images: ImageData[];
  onAdd: () => void;
  onUpdate: (index: number, field: keyof ImageData, value: string) => void;
  onRemove: (index: number) => void;
  onUpload: (index: number, event: ChangeEvent<HTMLInputElement>) => void;
}

export const ImageForm: React.FC<ImageFormProps> = ({
  images,
  onAdd,
  onUpdate,
  onRemove,
  onUpload
}) => {
  const handleDateChange = (index: number, dateString: string | null) => {
    if (dateString) {
      onUpdate(index, 'date', dateString);
    }
  };

  const handleClickUpload = (index: number) => {
    const input = document.getElementById(`upload-${index}`);
    input?.click();
  };

  return (
    <div>
      <Space style={{ marginBottom: 8 }}>
        <Button size="small" icon={<PlusOutlined />} onClick={onAdd}>
          添加影像检查
        </Button>
      </Space>

      {images.map((img, index) => (
        <Card size="small" key={index} style={{ marginBottom: 8 }}>
          <Row gutter={8}>
            <Col span={6}>
              <Input
                placeholder="检查类型（如 CT、MRI）"
                value={img.type}
                onChange={(e) => onUpdate(index, 'type', e.target.value)}
                size="small"
              />
            </Col>
            <Col span={10}>
              <Input
                placeholder="检查描述"
                value={img.description}
                onChange={(e) => onUpdate(index, 'description', e.target.value)}
                size="small"
              />
            </Col>
            <Col span={5}>
              <DatePicker
                value={img.date ? dayjs(img.date) : null}
                onChange={(date, dateString) => handleDateChange(index, dateString)}
                size="small"
                style={{ width: '100%' }}
                format="YYYY-MM-DD"
              />
            </Col>
            <Col span={3}>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <input
                  type="file"
                  accept="image/*"
                  id={`upload-${index}`}
                  style={{ display: 'none' }}
                  onChange={(e) => onUpload(index, e)}
                />
                <Button
                  icon={<UploadOutlined />}
                  size="small"
                  type={img.file ? 'primary' : 'default'}
                  block
                  onClick={() => handleClickUpload(index)}
                >
                  {img.file ? '✓ 已上传' : '📷 上传图片'}
                </Button>
                <Button
                  danger
                  size="small"
                  icon={<DeleteOutlined />}
                  onClick={() => onRemove(index)}
                  block
                >
                  删除
                </Button>
              </Space>
            </Col>
          </Row>
          {img.previewUrl && (
            <Row style={{ marginTop: 8 }}>
              <Image
                src={img.previewUrl}
                alt="预览"
                style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 4 }}
                preview={true}
              />
            </Row>
          )}
        </Card>
      ))}
    </div>
  );
};

export default ImageForm;
