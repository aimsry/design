import React, { useState, useEffect, ChangeEvent } from 'react';
import { Card, Button, Select, Space, message, Typography, Divider, Row, Col, Form, Modal, Tag } from 'antd';
import { PlayCircleOutlined, UserOutlined } from '@ant-design/icons';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import AgentNode from '../components/nodes/AgentNode';
import StartNode from '../components/nodes/StartNode';
import EndNode from '../components/nodes/EndNode';
import CustomEdge from '../components/edges/CustomEdge';
import { PatientData, ImageFormData, LabFormData, DiagnosisReport } from '../types/workflow';
import api from '../services/api';
import { analyzeWorkflowRequirements } from '../utils/workflowAnalyzer';
import PatientInfoForm from '../components/forms/PatientInfoForm';
import SymptomsHistoryForm from '../components/forms/SymptomsHistoryForm';
import ImageForm from '../components/forms/ImageForm';
import LabForm from '../components/forms/LabForm';
import ReportDisplay from '../components/ReportDisplay';
import MedicalReportPDF from '../components/MedicalReportPDF';


const { Title, Text } = Typography;
const { Option } = Select;

const nodeTypes = {
  start: StartNode,
  end: EndNode,
  agent: AgentNode
};

const edgeTypes = {
  custom: CustomEdge
};

export const WorkflowExecutor: React.FC = () => {
  const [workflows, setWorkflows] = useState<Array<{ graph_id: string; description: string; created_time: number }>>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('');
  const [selectedWorkflowData, setSelectedWorkflowData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [diagnosisReport, setDiagnosisReport] = useState<DiagnosisReport | null>(null);

  // 表单相关状态
  const [form] = Form.useForm();
  const [images, setImages] = useState<ImageFormData[]>([]);
  const [labResults, setLabResults] = useState<LabFormData[]>([]);

  // 工作流需求分析
  const [workflowRequirements, setWorkflowRequirements] = useState({
    needsImaging: false,
    needsLabTests: false
  });

  const API_BASE_URL = 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchWorkflowList();
  }, []);

  // 获取工作流列表
  const fetchWorkflowList = async () => {
    setLoading(true);
    try {
      // 🔧 修正：使用正确的 API 端点 /workflows
      const response = await fetch(`${API_BASE_URL}/workflows`);
      const data = await response.json();
      console.log('📋 获取到的工作流列表:', data);

      // 🔍 根据后端返回格式调整：直接就是 workflows 数组
      if (Array.isArray(data)) {
        setWorkflows(data);
      } else if (data.workflows) {
        setWorkflows(data.workflows);
      } else {
        message.warning('未找到工作流列表');
      }
    } catch (error) {
      console.error('获取工作流列表失败:', error);
      message.error('无法连接到后端服务，请确保后端已启动');
    } finally {
      setLoading(false);
    }
  };

  // 获取工作流详情并分析需求
  const fetchWorkflowDetail = async (workflowId: string) => {
    try {
      // 🔧 修正：使用正确的 API 端点 /workflows/{id}
      const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}`);
      const data = await response.json();
      console.log('📄 获取到的工作流详情:', data);

      // 🔍 后端直接返回 workflow 对象，不需要 data.data
      if (data) {
        setSelectedWorkflowData(data);

        // 分析工作流需求
        const requirements = analyzeWorkflowRequirements(data.nodes);
        console.log('🔍 工作流需求分析:', requirements);

        setWorkflowRequirements({
          needsImaging: requirements.needsImaging,
          needsLabTests: requirements.needsLabTests
        });
      }
    } catch (error) {
      console.error('获取工作流详情失败:', error);
    }
  };

  // 打开执行表单
  const openExecutionForm = () => {
    if (!selectedWorkflow) {
      message.warning('请先选择一个工作流');
      return;
    }

    form.resetFields();
    setImages([]);
    setLabResults([]);
    setIsModalVisible(true);
  };

  // 影像学检查管理
  const addImage = () => {
    setImages([...images, {
      type: '',
      description: '',
      date: new Date().toISOString().split('T')[0]
    }]);
  };

  const updateImage = (index: number, field: keyof ImageFormData, value: string) => {
    const newImages = [...images];
    // 使用类型断言来避免 TypeScript 类型检查错误
    // 因为我们已经在上面检查了 field 不是 file 或 previewUrl
    if (field !== 'file' && field !== 'previewUrl') {
      (newImages[index] as any)[field] = value;
    }
    setImages(newImages);
  };

  const handleImageUpload = (index: number, event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const newImages = [...images];
    newImages[index].file = file;
    newImages[index].previewUrl = URL.createObjectURL(file);
    setImages(newImages);
  };

  const removeImage = (index: number) => {
    if (images[index].previewUrl) {
      URL.revokeObjectURL(images[index].previewUrl!);
    }
    setImages(images.filter((_, i) => i !== index));
  };

  // 实验室检验管理
  const addLabResult = () => {
    setLabResults([...labResults, {
      test_name: '',
      value: '',
      unit: '',
      reference_range: '',
      date: new Date().toISOString().split('T')[0]
    }]);
  };

  const updateLabResult = (index: number, field: keyof LabFormData, value: string) => {
    const newResults = [...labResults];
    newResults[index][field] = value;
    setLabResults(newResults);
  };

  const removeLabResult = (index: number) => {
    setLabResults(labResults.filter((_, i) => i !== index));
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    // 验证必填的检查项目
    if (workflowRequirements.needsImaging && images.length === 0) {
      message.warning('该工作流需要至少添加一项影像学检查');
      return;
    }

    if (workflowRequirements.needsLabTests && labResults.length === 0) {
      message.warning('该工作流需要至少添加一项实验室检验');
      return;
    }

    setExecuting(true);
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

      const result = await api.workflow.executeWorkflow(selectedWorkflow, patientData);
      console.log('📥 执行结果:', result);

      if (result.success && result.report) {
        message.success('诊断完成！');
        setIsModalVisible(false);
        setDiagnosisReport(result.report);
        setShowReport(true);
      } else {
        message.error(`执行失败：${result.message || '未知错误'}`);
      }
    } catch (error) {
      console.error('❌ 执行工作流失败:', error);
      message.error('执行工作流失败');
    } finally {
      setExecuting(false);
    }
  };

  // 渲染工作流图
  const renderWorkflowGraph = () => {
    if (!selectedWorkflowData) return null;

    const nodes = selectedWorkflowData.nodes.map((node: any) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: node.data
    }));

    const edges = selectedWorkflowData.edges.map((edge: any) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type || 'custom',
      animated: true
    }));

    return (
      <Card title="工作流预览" size="small" style={{ marginTop: 20 }}>
        <div style={{ height: 300, position: 'relative' }}>
          <ReactFlow
            nodes={nodes as any}
            edges={edges as any}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            fitView
            attributionPosition="bottom-left"
            nodesDraggable={false}
            nodesConnectable={false}
            elementsSelectable={false}
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </Card>
    );
  };

  return (
    <div>
      {/* 主要内容区域 */}
      <Card title={
        <Space>
          <PlayCircleOutlined />
          <span>工作流执行</span>
        </Space>
      } extra={
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={openExecutionForm}
          disabled={!selectedWorkflow || executing}
          loading={executing}
        >
          {executing ? '执行中...' : '执行工作流'}
        </Button>
      }>
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 工作流选择 */}
          <Card size="small" title="选择工作流">
            <Select
              style={{ width: '100%' }}
              placeholder="请选择要执行的工作流"
              value={selectedWorkflow}
              onChange={(value) => {
                setSelectedWorkflow(value);
                fetchWorkflowDetail(value);
              }}
              loading={loading}
              showSearch
            >
              {workflows.map(workflow => (
                <Option key={workflow.graph_id} value={workflow.graph_id}>
                  {workflow.description || workflow.graph_id}
                </Option>
              ))}
            </Select>
          </Card>

          {/* 当前选择信息 */}
          {selectedWorkflow && (
            <Card size="small" title="当前选择">
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>工作流 ID: </Text>
                  <Text code>{selectedWorkflow}</Text>
                </Col>
                <Col span={16}>
                  <Text strong>描述： </Text>
                  <Text>{workflows.find(w => w.graph_id === selectedWorkflow)?.description || '无描述'}</Text>
                </Col>
              </Row>

              {selectedWorkflowData && (
                <>
                  {(workflowRequirements.needsImaging || workflowRequirements.needsLabTests) && (
                    <Divider dashed style={{ margin: '12px 0' }} />
                  )}

                  {(workflowRequirements.needsImaging || workflowRequirements.needsLabTests) && (
                    <Row gutter={16}>
                      <Col span={12}>
                        {workflowRequirements.needsImaging && (
                          <Tag color="blue">需要影像学检查</Tag>
                        )}
                        {workflowRequirements.needsLabTests && (
                          <Tag color="green">需要实验室检验</Tag>
                        )}
                      </Col>
                    </Row>
                  )}
                </>
              )}
            </Card>
          )}

          {/* 工作流图预览 */}
          {selectedWorkflowData && renderWorkflowGraph()}
        </Space>
      </Card>

      {/* 执行表单模态框 */}
      <Modal
        title={
          <Space>
            <UserOutlined />
            <span>填写患者信息</span>
          </Space>
        }
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
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
          {/* 患者基本信息 */}
          <PatientInfoForm />

          {/* 症状与病史 */}
          <SymptomsHistoryForm />

          {/* 辅助检查区域 - 根据工作流需求动态显示 */}
          {(workflowRequirements.needsImaging || workflowRequirements.needsLabTests) && (
            <>
              <Divider style={{ textAlign: 'left', margin: '16px 0' }}>辅助检查</Divider>

              {/* 影像学检查表单 */}
              {workflowRequirements.needsImaging && (
                <Form.Item label="影像学检查">
                  <ImageForm
                    images={images}
                    onAdd={addImage}
                    onUpdate={updateImage}
                    onRemove={removeImage}
                    onUpload={handleImageUpload}
                  />
                </Form.Item>
              )}

              {/* 实验室检验表单 */}
              {workflowRequirements.needsLabTests && (
                <Form.Item label="实验室检验">
                  <LabForm
                    labResults={labResults}
                    onAdd={addLabResult}
                    onUpdate={updateLabResult}
                    onRemove={removeLabResult}
                  />
                </Form.Item>
              )}
            </>
          )}

          <Divider />
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={executing}>
                提交执行
              </Button>
              <Button htmlType="button" onClick={() => setIsModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 诊断报告展示 */}
      <MedicalReportPDF
        report={diagnosisReport}
        visible={showReport}
        onClose={() => setShowReport(false)}
      />
    </div>
  );
};

export default WorkflowExecutor;
