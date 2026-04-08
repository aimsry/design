"""图构建器"""
from typing import Dict, Any
from .state_manager import StateManager
from .nodes.medical.symptom_analyzer import SymptomAnalyzer
from .nodes.medical.history_analyzer import HistoryAnalyzer
from .nodes.medical.lab_analyzer import LabAnalyzer
from .nodes.medical.imaging_analyzer import ImagingAnalyzer
from .nodes.medical.diagnosis_generator import DiagnosisGenerator

"""图构建器"""
from typing import Dict, Any
from .state_manager import StateManager
from .workflow_executor import WorkflowExecutor
from .graph_loader import GraphLoader


class MedicalGraph:
    def __init__(self, workflow_definition: Dict[str, Any] = None):
        """
        初始化医疗图

        Args:
            workflow_definition: 工作流定义字典，如果为 None 则使用默认顺序
        """
        self.state_manager = StateManager()
        self.workflow_definition = workflow_definition

        # 如果提供了工作流定义，使用动态执行器
        if workflow_definition:
            self.executor = WorkflowExecutor(workflow_definition)
            print(f"[INFO] 使用动态工作流执行器，节点数：{len(workflow_definition.get('nodes', []))}")
        else:
            self.executor = None
            # 默认的智能体映射（向后兼容）
            self.agents = {
                "symptom_analyzer": None,  # 延迟加载
                "history_analyzer": None,
                "lab_analyzer": None,
                "imaging_analyzer": None,
                "diagnosis_generator": None
            }

    async def execute_workflow_async(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """异步执行完整的医疗诊断工作流"""
        if self.workflow_definition:
            # 使用新的动态执行器（异步版本）
            return await self.executor.execute(patient_data)
        else:
            # 使用旧的默认顺序执行（向后兼容）
            return self._execute_default_workflow(patient_data)

    def execute_workflow(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的医疗诊断工作流"""
        if self.workflow_definition:
            # 使用新的动态执行器
            return self.executor.execute_sync(patient_data)
        else:
            # 使用旧的默认顺序执行（向后兼容）
            return self._execute_default_workflow(patient_data)

    def _execute_default_workflow(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """默认的线性执行流程（向后兼容）"""
        from .nodes.medical.symptom_analyzer import SymptomAnalyzer
        from .nodes.medical.history_analyzer import HistoryAnalyzer
        from .nodes.medical.lab_analyzer import LabAnalyzer
        from .nodes.medical.imaging_analyzer import ImagingAnalyzer
        from .nodes.medical.diagnosis_generator import DiagnosisGenerator

        print("🏥 开始医疗诊断流程...")
        print(f"📋 患者：{patient_data['basic_info']['name']}")

        # 1. 初始化状态
        state = self.state_manager.initialize_state(patient_data)
        print("✅ 状态初始化完成")

        # 2. 依次执行各分析阶段
        analysis_sequence = [
            ("symptom_analyzer", "症状分析"),
            ("history_analyzer", "病史分析"),
            ("lab_analyzer", "实验室分析"),
            ("imaging_analyzer", "影像分析")
        ]

        agents = {
            "symptom_analyzer": SymptomAnalyzer(),
            "history_analyzer": HistoryAnalyzer(),
            "lab_analyzer": LabAnalyzer(),
            "imaging_analyzer": ImagingAnalyzer(),
        }

        for agent_name, stage_name in analysis_sequence:
            print(f"\n🔹 {stage_name}阶段")
            try:
                # 执行智能体分析
                result = agents[agent_name].execute(state)

                # 更新状态
                state = self.state_manager.update_analysis_result(agent_name, result)
                print(f"✅ {stage_name}完成")

            except Exception as e:
                print(f"❌ {stage_name}失败：{e}")
                # 即使某个阶段失败，也继续执行其他阶段
                continue

        # 3. 生成最终诊断
        print(f"\n🎯 生成最终诊断")
        try:
            diagnosis_generator = DiagnosisGenerator()
            diagnosis_result = diagnosis_generator.execute(state)
            state = self.state_manager.set_final_diagnosis(diagnosis_result)
            print("✅ 最终诊断生成完成")
        except Exception as e:
            print(f"❌ 诊断生成失败：{e}")
            # 设置默认诊断
            default_diagnosis = {
                "primary_diagnosis": "诊断流程异常，请重新提交",
                "differential_diagnosis": ["需要重新检查"],
                "risk_assessment": "unknown",
                "urgency": "routine"
            }
            state = self.state_manager.set_final_diagnosis(default_diagnosis)

        print("\n✅ 医疗诊断流程完成！")
        return state.to_dict()

    def get_agent(self, agent_name: str):
        """获取指定的智能体"""
        if self.executor and hasattr(self.executor, 'agents'):
            return self.executor.agents.get(agent_name)
        return None

    def get_state_manager(self):
        """获取状态管理器"""
        return self.state_manager

