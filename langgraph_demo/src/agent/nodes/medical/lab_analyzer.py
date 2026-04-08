"""实验室分析智能体"""
from .base_agent import BaseAgent


class LabAnalyzer(BaseAgent):
    def __init__(self):
        super().__init__("lab_analyzer")

    def prepare_input(self, state) -> str:
        # 检查是否有检验数据
        if not state.patient_input.lab_results or len(state.patient_input.lab_results) == 0:
            return """无实验室检查数据。
请说明：由于缺乏检验数据，无法进行实验室分析，建议完善相关检查。"""

        lab_data_str = "\n".join([
            f"- {item['test_name']}: {item['value']} {item.get('unit', '')} (参考范围：{item.get('reference_range', 'N/A')})"
            for item in state.patient_input.lab_results
        ])

        return f"""实验室检查结果：
{lab_data_str}

请分析上述检验结果并识别：
1. 异常指标（abnormal_values）- 异常的检验项目数组，每项包含 name、value、reference_range
2. 临床意义（clinical_significance）- 异常结果的临床意义
3. 器官功能评估（organ_function）- 相关器官功能状态
4. 炎症指标（inflammatory_markers）- 如有炎症相关指标请特别标注

重要：请直接返回 JSON 格式，不要使用任何 Markdown 格式或代码块标记。
返回示例：
{{
  "abnormal_values": [
    {{"name": "白细胞计数", "value": "12.5", "reference_range": "4.0-10.0"}}
  ],
  "clinical_significance": "白细胞升高提示可能存在感染",
  "organ_function": {{"免疫系统": "激活状态"}},
  "inflammatory_markers": [{{"marker": "C 反应蛋白", "status": "升高"}}]
}}
"""

    def process_output(self, output: dict) -> dict:
        # 确保必要字段存在
        if "abnormal_values" not in output:
            output["abnormal_values"] = []
        if "clinical_significance" not in output:
            output["clinical_significance"] = "未发现明显异常或数据不足"
        if "organ_function" not in output:
            output["organ_function"] = {}
        if "inflammatory_markers" not in output:
            output["inflammatory_markers"] = []

        return output
