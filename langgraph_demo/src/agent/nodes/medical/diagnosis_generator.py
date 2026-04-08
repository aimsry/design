"""诊断生成智能体"""
from .base_agent import BaseAgent


class DiagnosisGenerator(BaseAgent):
    def __init__(self):
        super().__init__("diagnosis_generator")

    def prepare_input(self, state) -> str:
        # 收集所有分析结果
        symptom_analysis = state.symptom_analysis.result if state.symptom_analysis else "未进行症状分析"
        history_analysis = state.history_analysis.result if state.history_analysis else "未进行病史分析"
        lab_analysis = state.lab_analysis.result if state.lab_analysis else "未进行实验室分析"
        imaging_analysis = state.imaging_analysis.result if state.imaging_analysis else "未进行影像学分析"

        return f"""请根据以下各项分析结果，生成一份专业的医疗诊断报告：

【患者基本信息】
{state.patient_input.basic_info}

【症状分析】
{symptom_analysis}

【病史分析】
{history_analysis}

【实验室分析】
{lab_analysis}

【影像学分析】
{imaging_analysis}

请生成一份完整的诊断报告，包括：

1. 基本信息（patient_info）
   - age（年龄）
   - gender（性别）
   - department（就诊科室）

2. 主诉（chief_complaint）- 患者最主要的痛苦或症状及其持续时间

3. 现病史（history_of_present_illness）- 本次疾病的发生、发展过程

4. 体格检查（physical_examination）
   - vital_signs（生命体征）：包含 temperature（体温）、pulse（脉搏）、respiration（呼吸）、blood_pressure（血压）
   - general_condition（一般情况）

5. 辅助检查（auxiliary_examinations）
   - laboratory_tests（实验室检查）- 异常结果总结
   - imaging_tests（影像学检查）- 重要发现总结

6. 初步诊断（preliminary_diagnosis）
   - primary_diagnosis（主要诊断）
   - icd_code（ICD-10 编码，如果知道的话）
   - differential_diagnosis（鉴别诊断列表）
   - reasoning（诊断依据 - 详细说明为什么做出这个诊断，包括症状、体征、实验室检查、影像学表现等支持点）

7. 风险评估（risk_assessment）
   - level（风险等级：low/moderate/high）
   - description（风险描述）

8. 紧急程度（urgency）
   - level（routine/urgent/emergency）
   - reason（需要紧急处理的原因）

9. 治疗计划（treatment_plan）
   - medications（药物治疗列表，每项包含 drug_name 药品名、dosage 剂量、usage 用法、frequency 频次、duration 疗程）
   - non_pharmacological（非药物治疗：休息、饮食等）
   - further_tests（进一步检查建议）

10. 随访计划（follow_up_plan）
    - follow_up_time（随访时间）
    - follow_up_items（随访项目）
    - precautions（注意事项）

重要：请直接返回 JSON 格式，不要使用任何 Markdown 格式或代码块标记。
返回示例：
{{
  "patient_info": {{"age": 45, "gender": "male", "department": "呼吸内科"}},
  "chief_complaint": "头痛、发热伴咳嗽 3 天",
  "history_of_present_illness": "患者 3 天前无明显诱因出现头痛、发热，体温最高 38.5°C，伴咳嗽...",
  "physical_examination": {{
    "vital_signs": {{"temperature": "38.5°C", "pulse": "90 次/分", "respiration": "20 次/分", "blood_pressure": "145/90mmHg"}},
    "general_condition": "神志清楚，精神尚可"
  }},
  "auxiliary_examinations": {{
    "laboratory_tests": ["白细胞计数升高：12.5×10^9/L", "C 反应蛋白升高：25.3mg/L"],
    "imaging_tests": ["胸部 X 光：肺部纹理增粗"]
  }},
  "preliminary_diagnosis": {{
    "primary_diagnosis": "急性呼吸道感染",
    "icd_code": "J06.9",
    "differential_diagnosis": ["肺炎", "上呼吸道感染", "病毒性感冒"],
    "reasoning": "诊断依据：①患者主诉咳嗽、咳痰伴发热 3 天，体温最高 39.2℃；②体格检查：咽部充血，扁桃体 II 度肿大；③实验室检查：白细胞计数升高（12.5×10^9/L），中性粒细胞百分比升高（75%）；④影像学检查：胸部 X 光显示肺纹理增粗。综合以上临床表现和辅助检查，符合急性呼吸道感染的诊断标准。"
  }},
  "risk_assessment": {{"level": "moderate", "description": "中等风险，需密切观察病情变化"}},
  "urgency": {{"level": "urgent", "reason": "高热不退，需及时处理"}},
  "treatment_plan": {{
    "medications": [
      {{"drug_name": "阿莫西林胶囊", "dosage": "0.5g", "usage": "口服", "frequency": "每日 3 次", "duration": "7 天"}},
      {{"drug_name": "布洛芬缓释胶囊", "dosage": "0.3g", "usage": "口服", "frequency": "必要时", "duration": "不超过 3 天"}}
    ],
    "non_pharmacological": ["充分休息", "多饮水", "清淡饮食", "监测体温"],
    "further_tests": ["胸部 CT 扫描", "血常规复查"]
  }},
  "follow_up_plan": {{
    "follow_up_time": "3 天后复诊",
    "follow_up_items": ["复查血常规", "评估治疗效果"],
    "precautions": ["如出现呼吸困难立即就医", "按时服药", "避免交叉感染"]
  }}
}}
"""

    def process_output(self, output: dict) -> dict:
        # 确保必要字段存在
        if "patient_info" not in output:
            output["patient_info"] = {"age": 0, "gender": "unknown", "department": "全科"}

        if "chief_complaint" not in output:
            output["chief_complaint"] = "患者自述不适"

        if "history_of_present_illness" not in output:
            output["history_of_present_illness"] = "待详细询问"

        if "physical_examination" not in output:
            output["physical_examination"] = {
                "vital_signs": {},
                "general_condition": "待查"
            }

        if "auxiliary_examinations" not in output:
            output["auxiliary_examinations"] = {
                "laboratory_tests": [],
                "imaging_tests": []
            }

        if "preliminary_diagnosis" not in output:
            output["preliminary_diagnosis"] = {
                "primary_diagnosis": "待诊断",
                "icd_code": "",
                "differential_diagnosis": [],
                "reasoning": "待补充诊断依据"
            }

        if "reasoning" not in output.get("preliminary_diagnosis", {}):
            output["preliminary_diagnosis"]["reasoning"] = "待补充诊断依据"

        if "risk_assessment" not in output:
            output["risk_assessment"] = {
                "level": "unknown",
                "description": "待评估"
            }

        if "urgency" not in output:
            output["urgency"] = {
                "level": "routine",
                "reason": ""
            }

        if "treatment_plan" not in output:
            output["treatment_plan"] = {
                "medications": [],
                "non_pharmacological": [],
                "further_tests": []
            }

        if "follow_up_plan" not in output:
            output["follow_up_plan"] = {
                "follow_up_time": "遵医嘱复诊",
                "follow_up_items": [],
                "precautions": []
            }

        return output
