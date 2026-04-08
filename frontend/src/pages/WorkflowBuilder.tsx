import React, { useState, useCallback, ChangeEvent } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  MiniMap,
  Connection,
  useNodesState,
  useEdgesState,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button, Card, List, Modal, Input, Space, message, Typography, Divider, Row, Col, Form, Select, DatePicker, Image, Tag } from 'antd';
import { PlusOutlined, SaveOutlined, PlayCircleOutlined, UserOutlined, UploadOutlined, DeleteOutlined } from '@ant-design/icons';
import AgentNode from '../components/nodes/AgentNode';
import StartNode from '../components/nodes/StartNode';
import EndNode from '../components/nodes/EndNode';
import CustomEdge from '../components/edges/CustomEdge';
import { AgentType, PatientData } from '../types/workflow';
import api from '../services/api';

const { Title } = Typography;
const { Option } = Select;

const nodeTypes = {
  start: StartNode,
  end: EndNode,
  agent: AgentNode
};

const edgeTypes = {
  custom: CustomEdge
};

interface ImageData {
  type: string;
  description: string;
  date: string;
  file?: File | null;
  previewUrl?: string | null;
}

interface LabData {
  test_name: string;
  value: string;
  unit: string;
  reference_range: string;
  date: string;
}

export const WorkflowBuilder: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [availableAgents, setAvailableAgents] = useState<AgentType[]>([]);
  const [isAgentModalVisible, setIsAgentModalVisible] = useState(false);
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);

  // 新增：表单相关状态
  const [isPatientModalVisible, setIsPatientModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [images, setImages] = useState<ImageData[]>([]);
  const [labResults, setLabResults] = useState<LabData[]>([]);
  const [hasImagingAnalyzer, setHasImagingAnalyzer] = useState(false);
  const [hasLabAnalyzer, setHasLabAnalyzer] = useState(false);

  React.useEffect(() => {
    loadAvailableAgents();
  }, []);

  const loadAvailableAgents = async () => {
    try {
      const response = await api.workflow.getAvailableAgents();
      if (response.success) {
        setAvailableAgents(response.data || []);
      }
    } catch (error) {
      console.error('加载智能体列表失败:', error);
    }
  };

  const onConnect = useCallback((params: Connection) => {
    setEdges((eds: Edge[]) => addEdge({
      ...params,
      type: 'custom',
      animated: true
    }, eds));
  }, [setEdges]);

  const addAgentNode = (agent: AgentType) => {
    const newNode = {
      id: `agent_${Date.now()}`,
      type: 'agent',
      position: {
        x: Math.random() * 500 + 100,
        y: Math.random() * 300 + 100
      },
      data: {
        label: agent.name,
        agentType: agent.type,
        agentId: agent.id,
        description: agent.description
      }
    };

    setNodes((nds: Node[]) => [...nds, newNode]);
    setIsAgentModalVisible(false);
  };

  const saveWorkflow = async () => {
    if (nodes.length === 0) {
      message.warning('请先添加节点');
      return;
    }

    try {
      const workflow = {
        graph_id: `workflow_${Date.now()}`,
        description: workflowDescription,
        nodes: nodes.map((node: Node) => ({
          id: node.id,
          type: node.type,
          position: node.position,
          data: node.data
        })),
        edges: edges.map((edge: Edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type
        }))
      };

      const response = await api.workflow.saveWorkflow(workflow);
      if (response.success) {
        message.success('工作流保存成功！');
      }
    } catch (error) {
      message.error('保存工作流失败');
    }
  };

  // 添加影像检查
  const addImage = () => {
    setImages([...images, {
      type: '',
      description: '',
      date: new Date().toISOString().split('T')[0]
    }]);
  };

  // 更新影像检查（只更新 string 字段）
  const updateImage = (index: number, field: keyof ImageData, value: string) => {
    const newImages = [...images];
    if (field !== 'file' && field !== 'previewUrl') {
      newImages[index][field] = value;
    }
    setImages(newImages);
  };

  // 处理图片上传
  const handleImageUpload = (index: number, event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const newImages = [...images];
    newImages[index].file = file;
    newImages[index].previewUrl = URL.createObjectURL(file);
    setImages(newImages);
  };

  // 删除影像检查
  const removeImage = (index: number) => {
    if (images[index].previewUrl) {
      URL.revokeObjectURL(images[index].previewUrl!);
    }
    setImages(images.filter((_, i) => i !== index));
  };

  // 添加检验结果
  const addLabResult = () => {
    setLabResults([...labResults, {
      test_name: '',
      value: '',
      unit: '',
      reference_range: '',
      date: new Date().toISOString().split('T')[0]
    }]);
  };

  // 更新检验结果
  const updateLabResult = (index: number, field: keyof LabData, value: string) => {
    const newResults = [...labResults];
    newResults[index][field] = value;
    setLabResults(newResults);
  };

  // 删除检验结果
  const removeLabResult = (index: number) => {
    setLabResults(labResults.filter((_, i) => i !== index));
  };

  // 打开执行表单
  const openExecutionForm = () => {
    // 检查工作流中是否包含影像学分析和实验室分析节点
    const hasImaging = nodes.some((node: Node) =>
      node.type === 'agent' && node.data.agentType === 'imaging_analyzer'
    );
    const hasLab = nodes.some((node: Node) =>
      node.type === 'agent' && node.data.agentType === 'lab_analyzer'
    );

    setHasImagingAnalyzer(hasImaging);
    setHasLabAnalyzer(hasLab);

    form.resetFields();
    setImages([]);
    setLabResults([]);
    setIsPatientModalVisible(true);
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    // 验证必填的检查项目
    if (hasImagingAnalyzer && images.length === 0) {
      message.warning('该工作流需要至少添加一项影像学检查');
      return;
    }

    if (hasLabAnalyzer && labResults.length === 0) {
      message.warning('该工作流需要至少添加一项实验室检验');
      return;
    }

    setIsExecuting(true);
    try {
      const patientData: PatientData = {
        basic_info: {
          name: values.name,
          gender: values.gender,
          age: values.age,
          department: values.department || '全科',
          phone: values.phone || undefined,
          id_card: values.id_card || undefined
        },
        symptoms: values.symptoms,
        medical_history: values.medical_history,
        images: images.map(img => ({
          type: img.type,
          description: img.description,
          date: img.date,
          url: img.file ? img.file.name : ''
        })),
        lab_results: labResults.map(lab => ({
          test_name: lab.test_name,
          value: lab.value,
          unit: lab.unit,
          reference_range: lab.reference_range,
          date: lab.date
        }))
      };

      console.log('📤 发送请求:', JSON.stringify(patientData, null, 2));

      const result = await api.workflow.executeWorkflow(`workflow_${Date.now()}`, patientData);
      if (result.success) {
        message.success('工作流执行成功');
        setIsPatientModalVisible(false);
        console.log('执行结果:', result);
      } else {
        message.error(`执行失败：${result.message}`);
      }
    } catch (error) {
      message.error('执行工作流失败');
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex' }}>
      {/* 左侧面板 - 智能体库 */}
      <div style={{ width: 300, borderRight: '1px solid #ddd', padding: 16, overflowY: 'auto' }}>
        <Title level={4}>智能体库</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          block
          onClick={() => setIsAgentModalVisible(true)}
          style={{ marginBottom: 16 }}
        >
          添加智能体
        </Button>

        <List
          dataSource={availableAgents}
          renderItem={agent => (
            <List.Item>
              <Card
                size="small"
                hoverable
                onClick={() => addAgentNode(agent)}
                style={{ width: '100%' }}
              >
                <Card.Meta
                  title={agent.name}
                  description={agent.description}
                />
              </Card>
            </List.Item>
          )}
        />
      </div>

      {/* 中间画布区域 */}
      <div style={{ flex: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes.map((node: Node) => ({
            ...node,
            data: { ...node.data }
          }))}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Background />
          <Controls />
          <MiniMap />

          <Panel position="top-right">
            <Space>
              <Input
                placeholder="工作流描述"
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
                style={{ width: 200 }}
              />
              <Button
                icon={<SaveOutlined />}
                onClick={saveWorkflow}
              >
                保存
              </Button>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={openExecutionForm}
                loading={isExecuting}
              >
                执行
              </Button>
            </Space>
          </Panel>
        </ReactFlow>
      </div>

      {/* 添加智能体模态框 */}
      <Modal
        title="选择智能体"
        open={isAgentModalVisible}
        onCancel={() => setIsAgentModalVisible(false)}
        footer={null}
        width={600}
      >
        <List
          grid={{ gutter: 16, column: 2 }}
          dataSource={availableAgents}
          renderItem={agent => (
            <List.Item>
              <Card
                hoverable
                onClick={() => addAgentNode(agent)}
              >
                <Card.Meta
                  title={agent.name}
                  description={agent.description}
                />
              </Card>
            </List.Item>
          )}
        />
      </Modal>

      {/* 患者信息填写模态框 */}
      <Modal
        title={
          <Space>
            <UserOutlined />
            <span>填写患者信息</span>
          </Space>
        }
        open={isPatientModalVisible}
        onCancel={() => setIsPatientModalVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            department: '全科',
            gender: 'male'
          }}
        >
          <Divider style={{ textAlign: 'left', margin: '16px 0' }}>基本信息</Divider>
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

          <Divider style={{ textAlign: 'left', margin: '16px 0' }}>症状与病史</Divider>
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

          {(hasImagingAnalyzer || hasLabAnalyzer) && (
            <>
              <Divider style={{ textAlign: 'left', margin: '16px 0' }}>辅助检查</Divider>

              {hasImagingAnalyzer && (
                <>
                  <Form.Item label="影像学检查">
                    <Space style={{ marginBottom: 8 }}>
                      <Button size="small" icon={<PlusOutlined />} onClick={addImage}>
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
                              onChange={(e) => updateImage(index, 'type', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={10}>
                            <Input
                              placeholder="检查描述"
                              value={img.description}
                              onChange={(e) => updateImage(index, 'description', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={5}>
                            <DatePicker
                              value={img.date}
                              onChange={(date, dateString) => {
                                if (dateString) updateImage(index, 'date', dateString);
                              }}
                              size="small"
                              style={{ width: '100%' }}
                            />
                          </Col>
                          <Col span={3}>
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                              <input
                                type="file"
                                accept="image/*"
                                id={`upload-${index}`}
                                style={{ display: 'none' }}
                                onChange={(e) => handleImageUpload(index, e)}
                              />
                              <label htmlFor={`upload-${index}`}>
                                <Button
                                  icon={<UploadOutlined />}
                                  size="small"
                                  type={img.file ? 'primary' : 'default'}
                                  block
                                  onClick={(e) => e.preventDefault()}
                                >
                                  {img.file ? '✓ 已上传' : '📷 上传图片'}
                                </Button>
                              </label>
                              <Button
                                danger
                                size="small"
                                icon={<DeleteOutlined />}
                                onClick={() => removeImage(index)}
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
                  </Form.Item>
                </>
              )}

              {hasLabAnalyzer && (
                <>
                  <Form.Item label="实验室检验">
                    <Space style={{ marginBottom: 8 }}>
                      <Button size="small" icon={<PlusOutlined />} onClick={addLabResult}>
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
                              onChange={(e) => updateLabResult(index, 'test_name', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={4}>
                            <Input
                              placeholder="结果值"
                              value={lab.value}
                              onChange={(e) => updateLabResult(index, 'value', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={3}>
                            <Input
                              placeholder="单位"
                              value={lab.unit}
                              onChange={(e) => updateLabResult(index, 'unit', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={5}>
                            <Input
                              placeholder="参考范围"
                              value={lab.reference_range}
                              onChange={(e) => updateLabResult(index, 'reference_range', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={4}>
                            <DatePicker
                              value={lab.date}
                              onChange={(date, dateString) => {
                                if (dateString) updateLabResult(index, 'date', dateString);
                              }}
                              size="small"
                              style={{ width: '100%' }}
                            />
                          </Col>
                          <Col span={3}>
                            <Button
                              danger
                              size="small"
                              icon={<DeleteOutlined />}
                              onClick={() => removeLabResult(index)}
                              style={{ width: '100%' }}
                            >
                              删除
                            </Button>
                          </Col>
                        </Row>
                      </Card>
                    ))}
                  </Form.Item>
                </>
              )}
            </>
          )}

          <Divider />
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={isExecuting}>
                提交执行
              </Button>
              <Button htmlType="button" onClick={() => setIsPatientModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkflowBuilder;
