"""状态管理器"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class PatientInput:
    basic_info: Dict[str, Any]
    symptoms: str
    medical_history: str
    images: list
    lab_results: list


@dataclass
class AnalysisResult:
    timestamp: str
    agent_name: str
    result: Dict[str, Any]


@dataclass
class MedicalState:
    # 输入数据
    patient_input: PatientInput

    # 分析结果
    symptom_analysis: Optional[AnalysisResult] = None
    history_analysis: Optional[AnalysisResult] = None
    lab_analysis: Optional[AnalysisResult] = None
    imaging_analysis: Optional[AnalysisResult] = None

    # 控制状态
    current_stage: str = "initialized"
    diagnosis_complete: bool = False
    final_diagnosis: Optional[Dict[str, Any]] = None

    # 🔹 治疗建议（新增字段）
    treatment_recommendations: list = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StateManager:
    def __init__(self):
        self.state = None


    def initialize_state(self, patient_data: Dict[str, Any]) -> MedicalState:
        """初始化状态"""
        patient_input = PatientInput(
            basic_info=patient_data["basic_info"],
            symptoms=patient_data["symptoms"],
            medical_history=patient_data["medical_history"],
            images=patient_data.get("images", []),
            lab_results=patient_data.get("lab_results", [])
        )

        self.state = MedicalState(patient_input=patient_input)
        self.state.current_stage = "symptom_analysis"
        return self.state

    def update_analysis_result(self, agent_name: str, result: Dict[str, Any]) -> MedicalState:
        """更新分析结果"""
        if not self.state:
            raise ValueError("状态未初始化")

        analysis_result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            result=result
        )

        # 直接映射到预定义的属性名
        attr_mapping = {
            "symptom_analyzer": "symptom_analysis",
            "history_analyzer": "history_analysis",
            "lab_analyzer": "lab_analysis",
            "imaging_analyzer": "imaging_analysis"
        }

        attr_name = attr_mapping.get(agent_name)
        if attr_name:
            setattr(self.state, attr_name, analysis_result)
        else:
            # 如果没有预定义映射，使用原来的格式作为后备
            setattr(self.state, f"{agent_name}_analysis", analysis_result)

        # 更新当前阶段
        stage_mapping = {
            "symptom_analyzer": "history_analysis",
            "history_analyzer": "lab_analysis",
            "lab_analyzer": "imaging_analysis",
            "imaging_analyzer": "diagnosis_generation"
        }

        if agent_name in stage_mapping:
            self.state.current_stage = stage_mapping[agent_name]
        return self.state

    def set_final_diagnosis(self, diagnosis: Dict[str, Any]) -> MedicalState:
        """设置最终诊断结果"""
        if not self.state:
            raise ValueError("状态未初始化")

        self.state.final_diagnosis = diagnosis
        self.state.diagnosis_complete = True
        self.state.current_stage = "completed"
        return self.state

    def get_current_state(self) -> MedicalState:
        """获取当前状态"""
        if not self.state:
            raise ValueError("状态未初始化")
        return self.state

    def get_analysis_results(self) -> Dict[str, Any]:

        """获取所有分析结果"""
        if not self.state:
            return {}

        results = {}
        analysis_fields = ["symptom", "history", "lab", "imaging"]

        for field in analysis_fields:
            analysis_attr = f"{field}_analysis"
            if hasattr(self.state, analysis_attr) and getattr(self.state, analysis_attr):
                results[field] = getattr(self.state, analysis_attr).result

        return results
