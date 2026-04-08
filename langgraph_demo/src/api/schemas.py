"""API数据模型"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PatientBasicInfo(BaseModel):
    name: str
    gender: str
    age: int
    phone: Optional[str] = None
    id_card: Optional[str] = None

class LabResult(BaseModel):
    test_name: str
    value: str
    unit: str
    reference_range: str
    date: str

class MedicalImage(BaseModel):
    type: str
    url: str
    description: str
    date: str

class DiagnosisRequest(BaseModel):
    patient_info: PatientBasicInfo
    symptoms: str
    medical_history: str
    images: List[MedicalImage] = []
    lab_results: List[LabResult] = []

class AnalysisFinding(BaseModel):
    timestamp: str
    confidence: float
    findings: Dict[str, Any]

class DiagnosisResult(BaseModel):
    primary_diagnosis: str
    differential_diagnosis: List[str]
    confidence_score: float
    risk_assessment: str
    recommended_actions: List[str]
    reasoning: Optional[str] = "诊断依据待补充"

class MedicalReport(BaseModel):
    report_id: str
    generated_time: str
    patient_summary: Dict[str, str]
    clinical_findings: Dict[str, Any]
    diagnosis: DiagnosisResult
    treatment_plan: List[Dict[str, str]]
    follow_up: Dict[str, str]
    patient_education: List[str]

class DiagnosisResponse(BaseModel):
    success: bool
    message: str
    report: Optional[MedicalReport] = None
    error_details: Optional[str] = None

# 在文件末尾添加以下模型

class NodeConfig(BaseModel):
    id: str
    type: str  # 'start', 'end', 'agent'
    position: Dict[str, float]  # {'x': 100, 'y': 200}
    data: Dict[str, Any]

class EdgeConfig(BaseModel):
    id: Optional[str] = None  # 改为可选，前端可以自动生成
    source: str
    target: str
    type: Optional[str] = "default"

class WorkflowDefinition(BaseModel):
    graph_id: str
    description: Optional[str] = ""
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]

class WorkflowCreateRequest(BaseModel):
    description: Optional[str] = ""
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]

class WorkflowUpdateRequest(BaseModel):
    description: Optional[str] = None
    nodes: Optional[List[NodeConfig]] = None
    edges: Optional[List[EdgeConfig]] = None

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    patient_data: Dict[str, Any]

class WorkflowResponse(BaseModel):
    success: bool
    message: str
    workflow_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None

class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    type: str
    config_template: Optional[Dict[str, Any]] = None

class AvailableAgentsResponse(BaseModel):
    agents: List[AgentInfo]
    total: int
