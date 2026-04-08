import React, { useRef } from 'react';
import { Modal, Button, Space, message } from 'antd';
import { DownloadOutlined, CloseOutlined } from '@ant-design/icons';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

interface MedicalReportPDFProps {
  report: any;
  visible: boolean;
  onClose: () => void;
}

export const MedicalReportPDF: React.FC<MedicalReportPDFProps> = ({
  report,
  visible,
  onClose
}) => {
  const reportRef = useRef<HTMLDivElement>(null);

  if (!report) return null;

  // 解析风险等级
  const parseRiskLevel = (riskAssessment: string) => {
    if (!riskAssessment) return { level: '未知', description: riskAssessment || '' };

    const match = riskAssessment.match(/^(high|moderate|low|高风险|中风险|低风险)[:：]\s*(.+)/i);
    if (match) {
      const levelMap: Record<string, string> = {
        'high': '高风险',
        'moderate': '中风险',
        'low': '低风险',
        '高风险': '高风险',
        '中风险': '中风险',
        '低风险': '低风险'
      };
      return {
        level: levelMap[match[1].toLowerCase()] || match[1],
        description: match[2]
      };
    }

    return { level: '未评估', description: riskAssessment };
  };

  const riskInfo = parseRiskLevel(report.diagnosis?.risk_assessment);

  // 获取风险颜色
  const getRiskColor = (level: string) => {
    if (level.includes('高')) return '#ff4d4f';
    if (level.includes('中')) return '#faad14';
    if (level.includes('低')) return '#52c41a';
    return '#1890ff';
  };

  // 导出为 PDF
  const handleExportPDF = async () => {
    if (!reportRef.current) return;

    try {
      message.loading({ content: '正在生成PDF...', key: 'pdf' });

      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);

      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      let imgY = 10;

      const scaledHeight = imgHeight * ratio;

      // 如果内容超过一页，分页处理
      let heightLeft = scaledHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', imgX, imgY, pdfWidth - 20, scaledHeight);
      heightLeft -= pdfHeight;

      while (heightLeft > 0) {
        position = heightLeft - scaledHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', imgX, position, pdfWidth - 20, scaledHeight);
        heightLeft -= pdfHeight;
      }

      const fileName = `诊断报告_${report.patient_summary?.name}_${new Date().toLocaleDateString()}.pdf`;
      pdf.save(fileName);

      message.success({ content: 'PDF导出成功！', key: 'pdf' });
    } catch (error) {
      console.error('PDF导出失败:', error);
      message.error({ content: 'PDF导出失败，请重试', key: 'pdf' });
    }
  };

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={900}
      centered
      bodyStyle={{ padding: 0 }}
    >
      {/* 操作按钮 */}
      <div style={{
        padding: '16px 24px',
        background: '#fafafa',
        borderBottom: '1px solid #e8e8e8',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span style={{ fontSize: '16px', fontWeight: 500 }}>医疗诊断报告</span>
        <Space>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExportPDF}
          >
            导出PDF
          </Button>
          <Button
            icon={<CloseOutlined />}
            onClick={onClose}
          >
            关闭
          </Button>
        </Space>
      </div>

      {/* 报告内容 */}
      <div
        ref={reportRef}
        style={{
          maxHeight: '75vh',
          overflowY: 'auto',
          background: '#fff',
          padding: '40px'
        }}
      >
        {/* 医院抬头 */}
        <div style={{ textAlign: 'center', marginBottom: '30px', borderBottom: '3px double #1890ff', paddingBottom: '20px' }}>
          <h1 style={{
            margin: 0,
            fontSize: '28px',
            color: '#1890ff',
            fontWeight: 'bold',
            letterSpacing: '4px'
          }}>
            医疗诊断报告
          </h1>
          <p style={{ margin: '8px 0 0 0', color: '#8c8c8c', fontSize: '14px' }}>
            Medical Diagnosis Report
          </p>
          <p style={{ margin: '8px 0 0 0', color: '#595959', fontSize: '12px' }}>
            报告编号：{report.report_id} | 生成时间：{report.generated_time}
          </p>
        </div>

        {/* 患者基本信息 */}
        <section style={{ marginBottom: '24px' }}>
          <h2 style={{
            fontSize: '18px',
            color: '#1890ff',
            borderBottom: '2px solid #1890ff',
            paddingBottom: '8px',
            marginBottom: '16px'
          }}>
            一、患者基本信息
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
            fontSize: '14px'
          }}>
            <div><strong>姓名：</strong>{report.patient_summary?.name}</div>
            <div><strong>性别：</strong>{report.patient_summary?.gender === 'male' ? '男' : '女'}</div>
            <div><strong>年龄：</strong>{report.patient_summary?.age} 岁</div>
            <div><strong>主诉：</strong>{report.patient_summary?.chief_complaint || '暂无'}</div>
          </div>
        </section>

        {/* 临床发现 */}
        {report.clinical_findings && (
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{
              fontSize: '18px',
              color: '#1890ff',
              borderBottom: '2px solid #1890ff',
              paddingBottom: '8px',
              marginBottom: '16px'
            }}>
              二、临床发现
            </h2>

            {/* 症状分析 */}
            {report.clinical_findings.symptom_analysis?.result && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '15px', color: '#262626', marginBottom: '8px' }}>
                  2.1 症状分析
                </h3>
                <div style={{ paddingLeft: '16px', fontSize: '14px', lineHeight: '1.8' }}>
                  <div><strong>主要症状：</strong>
                    {report.clinical_findings.symptom_analysis.result.primary_symptoms?.join('、')}
                  </div>
                  <div><strong>严重程度：</strong>
                    {report.clinical_findings.symptom_analysis.result.severity === 'severe' ? '重度' :
                     report.clinical_findings.symptom_analysis.result.severity === 'moderate' ? '中度' : '轻度'}
                  </div>
                  <div><strong>持续时间：</strong>{report.clinical_findings.symptom_analysis.result.duration}</div>
                  <div><strong>症状特征：</strong>
                    {Object.entries(report.clinical_findings.symptom_analysis.result.characteristics || {})
                      .map(([key, value]) => `${key}: ${value}`).join('；')}
                  </div>
                </div>
              </div>
            )}

            {/* 病史分析 */}
            {report.clinical_findings.history_analysis?.result && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '15px', color: '#262626', marginBottom: '8px' }}>
                  2.2 病史分析
                </h3>
                <div style={{ paddingLeft: '16px', fontSize: '14px', lineHeight: '1.8' }}>
                  <div><strong>危险因素：</strong>
                    {report.clinical_findings.history_analysis.result.risk_factors?.join('、')}
                  </div>
                  <div><strong>既往疾病：</strong>
                    {report.clinical_findings.history_analysis.result.past_diseases?.join('、')}
                  </div>
                  <div><strong>家族史：</strong>
                    {Object.entries(report.clinical_findings.history_analysis.result.family_history || {})
                      .map(([key, value]) => `${key}: ${value}`).join('；')}
                  </div>
                </div>
              </div>
            )}

            {/* 检验分析 */}
            {report.clinical_findings.lab_analysis?.result && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '15px', color: '#262626', marginBottom: '8px' }}>
                  2.3 实验室检查
                </h3>
                <div style={{ paddingLeft: '16px', fontSize: '14px', lineHeight: '1.8' }}>
                  <div><strong>异常指标：</strong></div>
                  <ul style={{ margin: '4px 0', paddingLeft: '32px' }}>
                    {report.clinical_findings.lab_analysis.result.abnormal_values?.map((item: any, idx: number) => (
                      <li key={idx}>{item.name}: {item.value} (参考范围: {item.reference_range})</li>
                    ))}
                  </ul>
                  <div><strong>临床意义：</strong>{report.clinical_findings.lab_analysis.result.clinical_significance}</div>
                </div>
              </div>
            )}

            {/* 影像分析 */}
            {report.clinical_findings.imaging_analysis?.result && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '15px', color: '#262626', marginBottom: '8px' }}>
                  2.4 影像学检查
                </h3>
                <div style={{ paddingLeft: '16px', fontSize: '14px', lineHeight: '1.8' }}>
                  <div><strong>主要发现：</strong></div>
                  <ul style={{ margin: '4px 0', paddingLeft: '32px' }}>
                    {report.clinical_findings.imaging_analysis.result.main_findings?.map((finding: string, idx: number) => (
                      <li key={idx}>{finding}</li>
                    ))}
                  </ul>
                  <div><strong>诊断建议：</strong>{report.clinical_findings.imaging_analysis.result.diagnostic_suggestions}</div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* 诊断结果 */}
        <section style={{ marginBottom: '24px' }}>
          <h2 style={{
            fontSize: '18px',
            color: '#1890ff',
            borderBottom: '2px solid #1890ff',
            paddingBottom: '8px',
            marginBottom: '16px'
          }}>
            三、诊断结果
          </h2>

          <div style={{
            background: '#f6ffed',
            border: '2px solid #b7eb8f',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '16px'
          }}>
            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#389e0d', marginBottom: '8px' }}>
              主要诊断：{report.diagnosis?.primary_diagnosis || '待诊断'}
            </div>
            <div style={{ fontSize: '14px', color: '#595959' }}>
              <strong>置信度：</strong>{(report.diagnosis?.confidence_score || 0) * 100}%
            </div>
          </div>

          {/* 诊断推理依据 */}
          {report.diagnosis?.reasoning && (
            <div style={{
              background: '#e6f7ff',
              borderLeft: '4px solid #1890ff',
              padding: '12px 16px',
              marginBottom: '16px',
              fontSize: '14px',
              lineHeight: '1.8'
            }}>
              <div style={{ fontWeight: 'bold', color: '#0050b3', marginBottom: '8px' }}>
                🔍 诊断推理依据
              </div>
              <div>{report.diagnosis.reasoning}</div>
            </div>
          )}

          {/* 鉴别诊断 */}
          {report.diagnosis?.differential_diagnosis && report.diagnosis.differential_diagnosis.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>鉴别诊断：</div>
              <ol style={{ margin: 0, paddingLeft: '24px', fontSize: '14px', lineHeight: '1.8' }}>
                {report.diagnosis.differential_diagnosis.map((item: string, idx: number) => (
                  <li key={idx}>{item}</li>
                ))}
              </ol>
            </div>
          )}

          {/* 风险评估 */}
          <div style={{
            background: '#fff7e6',
            border: '1px solid #ffd591',
            borderRadius: '8px',
            padding: '12px 16px',
            fontSize: '14px'
          }}>
            <div style={{ marginBottom: '8px' }}>
              <strong>风险等级：</strong>
              <span style={{
                display: 'inline-block',
                marginLeft: '8px',
                padding: '2px 12px',
                background: getRiskColor(riskInfo.level),
                color: '#fff',
                borderRadius: '4px',
                fontSize: '13px'
              }}>
                {riskInfo.level}
              </span>
            </div>
            <div><strong>风险描述：</strong>{riskInfo.description}</div>
          </div>
        </section>

        {/* 治疗方案 */}
        <section style={{ marginBottom: '24px' }}>
          <h2 style={{
            fontSize: '18px',
            color: '#1890ff',
            borderBottom: '2px solid #1890ff',
            paddingBottom: '8px',
            marginBottom: '16px'
          }}>
            四、治疗方案
          </h2>

          {/* 药物治疗 */}
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '15px', color: '#262626', marginBottom: '12px' }}>
              4.1 药物治疗
            </h3>
            {report.treatment_plan?.filter((item: any) => item.action?.includes('药物')).map((item: any, idx: number) => (
              <div key={idx} style={{
                border: '1px solid #d9d9d9',
                borderRadius: '6px',
                padding: '12px',
                marginBottom: '8px',
                fontSize: '14px'
              }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{item.action.replace('药物治疗：', '')}</div>
                {item.details && <div style={{ color: '#595959' }}>{item.details}</div>}
              </div>
            ))}
          </div>

          {/* 非药物治疗 */}
          <div>
            <h3 style={{ fontSize: '15px', color: '#262626', marginBottom: '12px' }}>
              4.2 非药物治疗及生活指导
            </h3>
            <ul style={{ margin: 0, paddingLeft: '24px', fontSize: '14px', lineHeight: '2' }}>
              {report.treatment_plan?.filter((item: any) => !item.action?.includes('药物')).map((item: any, idx: number) => (
                <li key={idx}>{item.action.replace('非药物治疗：', '')}</li>
              ))}
            </ul>
          </div>
        </section>

        {/* 随访计划 */}
        <section style={{ marginBottom: '24px' }}>
          <h2 style={{
            fontSize: '18px',
            color: '#1890ff',
            borderBottom: '2px solid #1890ff',
            paddingBottom: '8px',
            marginBottom: '16px'
          }}>
            五、随访计划
          </h2>
          <div style={{ fontSize: '14px', lineHeight: '1.8' }}>
            <div><strong>复诊时间：</strong>{report.follow_up?.plan || '根据病情制定'}</div>
            <div><strong>复诊频率：</strong>{report.follow_up?.frequency || '按医嘱执行'}</div>
          </div>
        </section>

        {/* 健康教育 */}
        <section style={{ marginBottom: '24px' }}>
          <h2 style={{
            fontSize: '18px',
            color: '#1890ff',
            borderBottom: '2px solid #1890ff',
            paddingBottom: '8px',
            marginBottom: '16px'
          }}>
            六、健康教育
          </h2>
          <ol style={{ margin: 0, paddingLeft: '24px', fontSize: '14px', lineHeight: '2' }}>
            {report.patient_education?.map((item: string, idx: number) => (
              <li key={idx}>{item}</li>
            ))}
          </ol>
        </section>

        {/* 医师签名区 */}
        <div style={{
          marginTop: '40px',
          paddingTop: '20px',
          borderTop: '1px solid #d9d9d9',
          textAlign: 'right',
          fontSize: '14px',
          color: '#595959'
        }}>
          <div>报告生成时间：{report.generated_time}</div>
          <div style={{ marginTop: '8px' }}>本报告由AI辅助诊断系统生成，仅供参考</div>
          <div>请结合临床实际情况进行判断</div>
        </div>
      </div>
    </Modal>
  );
};

export default MedicalReportPDF;
