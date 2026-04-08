"""请求处理器"""
from typing import Dict, Any
from src.models.medical_state import MedicalState, PatientInput
from .schemas import DiagnosisRequest, DiagnosisResponse, MedicalReport
from src.agent.graph_bulider import MedicalGraph
from src.agent.state_manager import StateManager


class MedicalDiagnosisHandler:
    """医疗诊断处理器"""

    def __init__(self):
        self.graph = MedicalGraph()
        self.state_manager = StateManager()

    async def process_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        """处理诊断请求"""
        try:
            # 转换输入数据
            patient_input = PatientInput(
                basic_info=request.patient_info.dict(),
                symptoms=request.symptoms,
                medical_history=request.medical_history,
                images=[img.dict() for img in request.images],
                lab_results=[lab.dict() for lab in request.lab_results]
            )

            # 创建初始状态
            initial_state = MedicalState(patient_input=patient_input)

            # 执行诊断图
            final_state = self.graph.invoke(initial_state)

            # 生成报告
            report = self._generate_response_report(final_state)

            return DiagnosisResponse(
                success=True,
                message="诊断完成",
                report=report
            )

        except Exception as e:
            return DiagnosisResponse(
                success=False,
                message="诊断处理失败",
                error_details=str(e)
            )

    def _generate_response_report(self, state) -> MedicalReport:
        """生成响应报告"""
        # 这里将内部状态转换为 API 响应格式
        # 具体实现根据实际需要调整
        pass
