// frontend/src/types/workflow.ts

// 更新现有接口
export interface NodeConfig {
  id: string;
  type: 'start' | 'end' | 'agent';
  position: { x: number; y: number };
  data: {
    label: string;
    agentType?: string;
    agentId?: string;
    description?: string;
    config?: any;
  };
}

export interface EdgeConfig {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
}

export interface WorkflowGraph {
  graph_id?: string;
  description?: string;
  nodes: NodeConfig[];
  edges: EdgeConfig[];
}

export interface AgentType {
  id: string;
  name: string;
  description: string;
  type: string;
  configTemplate?: any;
}

// 新增 API 响应类型
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error_details?: string;
}

export interface WorkflowListResponse {
  workflows: Array<{
    graph_id: string;
    description: string;
    created_time: number;
  }>;
  total: number;
}

// ========== 新增：患者数据接口 ==========

// 患者基本信息
export interface PatientBasicInfo {
  name: string;
  gender: 'male' | 'female';
  age: number;
  department?: string;
  phone?: string;
  id_card?: string;
}

// 影像学检查
export interface MedicalImage {
  type: string;
  url?: string;
  description: string;
  date: string;
}

// 实验室检验
export interface LabResult {
  test_name: string;
  value: string;
  unit: string;
  reference_range: string;
  date: string;
}

// 完整的患者数据
export interface PatientData {
  basic_info: PatientBasicInfo;
  symptoms: string;
  medical_history: string;
  images: MedicalImage[];
  lab_results: LabResult[];
}

// 诊断报告响应
export interface DiagnosisReport {
  report_id: string;
  generated_time: string;
  patient_info: {
    age: number;
    gender: string;
    department: string;
  };
  chief_complaint: string;
  history_of_present_illness: string;
  physical_examination: {
    vital_signs: {
      temperature?: string;
      pulse?: string;
      respiration?: string;
      blood_pressure?: string;
    };
    general_condition: string;
  };
  auxiliary_examinations: {
    laboratory_tests: string[];
    imaging_tests: string[];
  };
  preliminary_diagnosis: {
    primary_diagnosis: string;
    icd_code?: string;
    differential_diagnosis: string[];
  };
  risk_assessment: {
    level: 'low' | 'moderate' | 'high';
    description: string;
  };
  urgency: {
    level: 'routine' | 'urgent' | 'emergency';
    reason: string;
  };
  treatment_plan: {
    medications: Array<{
      drug_name: string;
      dosage: string;
      usage: string;
      frequency: string;
      duration: string;
    }>;
    non_pharmacological: string[];
    further_tests: string[];
  };
  follow_up_plan: {
    follow_up_time: string;
    follow_up_items: string[];
    precautions: string[];
  };
}
export interface ImageFormData {
  type: string;
  description: string;
  date: string;
  file?: File | null;
  previewUrl?: string | null;
}

export interface LabFormData {
  test_name: string;
  value: string;
  unit: string;
  reference_range: string;
  date: string;
}

export interface ExecutionFormValues {
  name: string;
  gender: 'male' | 'female';
  age: number;
  department?: string;
  phone?: string;
  id_card?: string;
  symptoms: string;
  medical_history: string;
}

