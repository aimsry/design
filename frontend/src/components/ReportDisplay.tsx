import React from 'react';
import { Modal, Card, Typography, Tag, Divider, Row, Col, Descriptions, Space } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import { DiagnosisReport } from '../types/workflow';

const { Title, Text, Paragraph } = Typography;

interface ReportDisplayProps {
  report: any | null;  // 🔧 改为 any 以兼容不同格式
  visible: boolean;
  onClose: () => void;
}

export const ReportDisplay: React.FC<ReportDisplayProps> = ({
  report,
  visible,
  onClose
}) => {
  if (!report) return null;

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'green';
      case 'moderate': return 'orange';
      case 'high': return 'red';
      default: return 'blue';
    }
  };

  return (
    <Modal
      title={
        <Space>
          <CheckCircleOutlined style={{ color: '#52c41a' }} />
          <span>诊断报告</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={900}
    >
      <div style={{ maxHeight: '70vh', overflowY: 'auto', padding: '20px' }}>
        {/* 报告头部 */}
        <Card style={{ marginBottom: 16, background: '#f0f5ff' }}>
          <Row gutter={16}>
            <Col span={12}>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="患者信息">
                  {report.patient_summary?.name}，{report.patient_summary?.age}岁，{report.patient_summary?.gender === 'male' ? '男' : '女'}
                </Descriptions.Item>
                <Descriptions.Item label="主诉">
                  {report.patient_summary?.chief_complaint || '暂无'}
                </Descriptions.Item>
              </Descriptions>
            </Col>
            <Col span={12}>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="风险等级">
                  <Tag color={getRiskColor(typeof report.diagnosis?.risk_assessment === 'string' ? (report.diagnosis.risk_assessment.startsWith('high') ? 'high' : 'moderate') : 'moderate')}>
                    {typeof report.diagnosis?.risk_assessment === 'string' ? report.diagnosis.risk_assessment.split(':')[0].toUpperCase() : 'MODERATE'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="置信度">
                  <Text>{(report.diagnosis?.confidence_score || 0) * 100}%</Text>
                </Descriptions.Item>
              </Descriptions>
            </Col>
          </Row>
        </Card>

        {/* 诊断结果 */}
        <Card title="🏥 诊断结果" style={{ marginBottom: 16 }}>
          <Title level={4}>{report.diagnosis?.primary_diagnosis || '待诊断'}</Title>

          {/* 诊断推理依据 */}
          {report.diagnosis?.reasoning && (
            <div style={{ background: '#f6ffed', padding: '12px', borderRadius: '8px', border: '1px solid #b7eb8f', marginTop: 12 }}>
              <Title level={5} style={{ margin: '0 0 8px 0', color: '#389e0d' }}>
                🔍 诊断推理依据
              </Title>
              <Paragraph style={{ margin: 0, fontSize: 14 }}>
                {report.diagnosis.reasoning}
              </Paragraph>
            </div>
          )}

          {report.diagnosis?.differential_diagnosis && report.diagnosis.differential_diagnosis.length > 0 && (
            <>
              <Divider dashed />
              <Text strong>鉴别诊断：</Text>
              <ul>
                {report.diagnosis.differential_diagnosis.map((item: string, index: number) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </>
          )}
        </Card>

        {/* 临床发现 */}
        {report.clinical_findings && (
          <Card title="🔬 临床发现" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>症状分析：</Text>
                {report.clinical_findings.symptom_analysis?.result?.primary_symptoms && (
                  <ul>
                    {report.clinical_findings.symptom_analysis.result.primary_symptoms.map((s: string, i: number) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                )}
              </Col>
              <Col span={12}>
                <Text strong>检验分析：</Text>
                {report.clinical_findings.lab_analysis?.result?.abnormal_values && (
                  <ul>
                    {report.clinical_findings.lab_analysis.result.abnormal_values.map((v: any, i: number) => (
                      <li key={i}>{v.name}: {v.value}</li>
                    ))}
                  </ul>
                )}
              </Col>
            </Row>
          </Card>
        )}

        {/* 治疗计划 */}
        <Card title="💊 治疗方案" style={{ marginBottom: 16 }}>
          <Title level={5}>药物治疗</Title>
          {report.treatment_plan && report.treatment_plan.length > 0 ? (
            report.treatment_plan.map((item: any, index: number) => (
              <Card size="small" key={index} style={{ marginBottom: 8 }}>
                <Row gutter={16}>
                  <Col span={24}>
                    <Text strong>{item.action}</Text>
                    {item.details && <><br /><Text type="secondary">{item.details}</Text></>}
                  </Col>
                </Row>
              </Card>
            ))
          ) : (
            <Text type="secondary">无药物治疗</Text>
          )}
        </Card>

        {/* 随访计划 */}
        <Card title="📅 随访计划" style={{ marginBottom: 16 }}>
          <Descriptions column={1}>
            <Descriptions.Item label="计划">
              {report.follow_up?.plan || '根据病情制定随访计划'}
            </Descriptions.Item>
            <Descriptions.Item label="频率">
              {report.follow_up?.frequency || '按医嘱执行'}
            </Descriptions.Item>
          </Descriptions>
        </Card>

        {/* 患者教育 */}
        <Card title="📚 健康教育" style={{ marginBottom: 16 }}>
          <ul>
            {report.patient_education && report.patient_education.map((item: string, index: number) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Card>
      </div>
    </Modal>
  );
};

export default ReportDisplay;
