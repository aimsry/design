"""医疗诊断状态模型"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PatientInput:
    """患者输入数据"""
    basic_info: Dict[str, Any]
    symptoms: str
    medical_history: str
    images: List[Dict[str, Any]]
    lab_results: List[Dict[str, Any]]


@dataclass
class AnalysisResult:
    """分析结果基类"""
    timestamp: datetime
    confidence: float
    findings: Dict[str, Any]


@dataclass
class MedicalState:
    """医疗诊断共享状态"""
    # 输入数据
    patient_input: PatientInput

    # 分析结果
    symptom_analysis: Optional[AnalysisResult] = None
    history_analysis: Optional[AnalysisResult] = None
    imaging_analysis: Optional[AnalysisResult] = None
    lab_analysis: Optional[AnalysisResult] = None

    # 控制标志
    needs_imaging: bool = False
    needs_lab_tests: bool = False
    diagnosis_ready: bool = False

    # 最终输出
    final_diagnosis: Optional[Dict[str, Any]] = None
    treatment_recommendations: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "patient_input": self.patient_input.__dict__,
            "symptom_analysis": self.symptom_analysis.__dict__ if self.symptom_analysis else None,
            "history_analysis": self.history_analysis.__dict__ if self.history_analysis else None,
            "imaging_analysis": self.imaging_analysis.__dict__ if self.imaging_analysis else None,
            "lab_analysis": self.lab_analysis.__dict__ if self.lab_analysis else None,
            "needs_imaging": self.needs_imaging,
            "needs_lab_tests": self.needs_lab_tests,
            "diagnosis_ready": self.diagnosis_ready,
            "final_diagnosis": self.final_diagnosis,
            "final_diagnosis_raw": getattr(self, 'final_diagnosis_raw', None),  # 新增：大模型原始 JSON
            "treatment_recommendations": self.treatment_recommendations
        }

