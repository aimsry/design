"""配置管理"""
"""配置管理"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")  # 添加这行
    MODEL_NAME = os.getenv("MODEL_NAME", "qwen-max")    # 修改默认模型
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

    # 项目配置
    GRAPHS_DIR = "graphs"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # 系统提示词
    SYSTEM_PROMPTS = {
        "symptom_analyzer": """你是一个专业的症状分析医生。请仔细分析患者的症状描述，识别：
1. 主要症状（primary_symptoms）
2. 症状严重程度（severity：mild/moderate/severe）
3. 持续时间（duration）
4. 症状特征（characteristics）

请以JSON格式返回结果。""",

        "history_analyzer": """你是一个病史分析专家。请基于症状分析结果和患者病史，分析：
1. 危险因素（risk_factors）
2. 既往疾病（past_diseases）
3. 用药情况（medications）
4. 家族史（family_history）

请以JSON格式返回结果。""",

        "lab_analyzer": """你是检验分析专家。请分析实验室检查结果：
1. 异常指标（abnormal_values）
2. 临床意义（clinical_significance）
3. 器官功能评估（organ_function）

请以JSON格式返回结果。""",

        "imaging_analyzer": """你是影像分析专家。请分析影像检查描述：
1. 主要发现（key_findings）
2. 异常检测（abnormalities）
3. 临床意义（clinical_significance）

请以JSON格式返回结果。""",

        "diagnosis_generator": """你是综合诊断专家。请基于所有分析结果生成：
1. 主要诊断（primary_diagnosis）
2. 鉴别诊断（differential_diagnosis）
3. 风险评估（risk_assessment）
4. 治疗建议（treatment_recommendations）

请以JSON格式返回结果。"""
    }

settings = Settings()
