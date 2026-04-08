// frontend/src/services/api.ts
import { PatientData, DiagnosisReport } from '../types/workflow';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 工作流相关 API
export const workflowApi = {
  // 获取可用智能体列表
  getAvailableAgents: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/workflow/agents`);
      return await response.json();
    } catch (error) {
      console.error('获取智能体列表失败:', error);
      throw error;
    }
  },

  // 保存工作流
  saveWorkflow: async (workflow: any) => {
    try {
      const response = await fetch(`${API_BASE_URL}/workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflow)
      });
      return await response.json();
    } catch (error) {
      console.error('保存工作流失败:', error);
      throw error;
    }
  },

  // 执行工作流
  executeWorkflow: async (workflowId: string, patientData: PatientData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/workflow/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          patient_data: patientData
        })
      });
      return await response.json();
    } catch (error) {
      console.error('执行工作流失败:', error);
      throw error;
    }
  },

  // 获取工作流列表
  getWorkflowList: async () => {
    try {
      // 🔧 修正：使用正确的 API 端点 /workflows
      const response = await fetch(`${API_BASE_URL}/workflows`);
      return await response.json();
    } catch (error) {
      console.error('获取工作流列表失败:', error);
      throw error;
    }
  },

  // 获取工作流详情
  getWorkflowDetail: async (workflowId: string) => {
    try {
      // 🔧 修正：使用正确的 API 端点 /workflows/{id}
      const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}`);
      return await response.json();
    } catch (error) {
      console.error('获取工作流详情失败:', error);
      throw error;
    }
  }
};

// 导出默认对象以便统一管理
export default {
  workflow: workflowApi
};
