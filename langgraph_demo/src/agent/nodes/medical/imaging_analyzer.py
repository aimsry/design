"""影像分析智能体"""
from .base_agent import BaseAgent


class ImagingAnalyzer(BaseAgent):
    def __init__(self):
        super().__init__("imaging_analyzer")

    def prepare_input(self, state) -> str:
        # 检查是否有影像数据
        if not state.patient_input.images or len(state.patient_input.images) == 0:
            return """无影像学检查数据。
请说明：由于缺乏影像数据，无法进行影像学分析，建议完善相关检查。"""

        image_data_str = "\n".join([
            f"- {img['type']}: {img.get('description', '无描述')} ({img.get('date', '未知日期')})"
            for img in state.patient_input.images
        ])

        return f"""医学影像检查：
{image_data_str}

请分析上述影像描述并识别：
1. 主要发现（main_findings）- 影像学主要观察结果
2. 异常表现（abnormalities）- 异常或病变表现
3. 受累部位（affected_areas）- 受影响的身体部位或器官
4. 影像学诊断建议（diagnostic_suggestions）- 基于影像的初步诊断建议

重要：请直接返回 JSON 格式，不要使用任何 Markdown 格式或代码块标记。
返回示例：
{{
  "main_findings": ["肺部纹理增粗", "右肺下叶可见斑片状阴影"],
  "abnormalities": [{{"location": "右肺下叶", "finding": "斑片状阴影"}}],
  "affected_areas": ["右肺下叶"],
  "diagnostic_suggestions": "考虑肺炎可能性，建议结合临床症状和其他检查"
}}
"""

    def process_output(self, output: dict) -> dict:
        # 确保必要字段存在
        if "main_findings" not in output:
            output["main_findings"] = []
        if "abnormalities" not in output:
            output["abnormalities"] = []
        if "affected_areas" not in output:
            output["affected_areas"] = []
        if "diagnostic_suggestions" not in output:
            output["diagnostic_suggestions"] = "请结合临床综合判断"

        return output
