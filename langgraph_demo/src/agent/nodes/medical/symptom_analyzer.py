"""症状分析智能体"""
from .base_agent import BaseAgent


class SymptomAnalyzer(BaseAgent):
    def __init__(self):
        super().__init__("symptom_analyzer")

    def prepare_input(self, state) -> str:
        return f"""患者症状描述：
{state.patient_input.symptoms}

请分析上述症状并识别：
1. 主要症状（primary_symptoms）- 以数组形式返回
2. 症状严重程度（severity）- mild/moderate/severe
3. 持续时间（duration）- 具体时间描述
4. 症状特征（characteristics）- 症状的具体特点

重要：请直接返回 JSON 格式，不要使用任何 Markdown 格式或代码块标记。
返回示例：
{{
  "primary_symptoms": ["头痛", "发热"],
  "severity": "moderate",
  "duration": "3 天",
  "characteristics": {{"头痛": "持续性钝痛", "发热": "体温 38.5°C"}}
}}
"""

    def process_output(self, output: dict) -> dict:
        # 确保必要字段存在
        required_fields = ["primary_symptoms", "severity", "duration"]
        for field in required_fields:
            if field not in output:
                if field == "primary_symptoms":
                    output[field] = ["未明确识别"]
                elif field == "severity":
                    output[field] = "moderate"
                elif field == "duration":
                    output[field] = "未提及"

        # 添加症状特征字段
        if "characteristics" not in output:
            output["characteristics"] = "未详细描述"

        return output
