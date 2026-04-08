"""病史分析智能体"""
from .base_agent import BaseAgent


class HistoryAnalyzer(BaseAgent):
    def __init__(self):
        super().__init__("history_analyzer")

    def prepare_input(self, state) -> str:
        return f"""患者病史信息：
{state.patient_input.medical_history}

请分析上述病史并识别：
1. 危险因素（risk_factors）- 心血管疾病、糖尿病等风险因素
2. 既往疾病（past_diseases）- 既往患病史
3. 用药情况（medications）- 当前使用的药物
4. 家族史（family_history）- 家族遗传病史
5. 生活习惯（lifestyle_factors）- 吸烟、饮酒、运动等

重要：请直接返回 JSON 格式，不要使用任何 Markdown 格式或代码块标记。
返回示例：
{{
  "risk_factors": ["高血压", "吸烟"],
  "past_diseases": ["高血压病史 2 年"],
  "medications": ["降压药"],
  "family_history": "无特殊",
  "lifestyle_factors": {{"吸烟": "10 年", "饮酒": "偶尔"}}
}}
"""

    def process_output(self, output: dict) -> dict:
        # 确保必要字段存在
        required_fields = ["risk_factors", "past_diseases"]
        for field in required_fields:
            if field not in output:
                output[field] = []

        # 可选字段设置默认值
        if "medications" not in output:
            output["medications"] = []
        if "family_history" not in output:
            output["family_history"] = "未知"
        if "lifestyle_factors" not in output:
            output["lifestyle_factors"] = {}

        return output
