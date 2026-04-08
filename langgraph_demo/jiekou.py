"""
简化的 API 接口测试脚本
FastAPI 风格
"""
import requests
import json
from pathlib import Path


def test_workflow_execution():
    """测试工作流执行"""

    # API 端点
    url = "http://localhost:8000/api/v1/workflow/execute"

    # 工作流 ID
    workflow_id = "workflow_1773295457"

    # 测试数据
    payload = {
        "workflow_id": workflow_id,
        "patient_data": {
            "basic_info": {
                "name": "张伟",
                "gender": "male",
                "age": 45,
                "department": "呼吸内科",
                "phone": "13800138000",
                "id_card": "110101197901011234"
            },
            "symptoms": "患者主诉：咳嗽、咳痰伴发热 3 天。体温最高达 39.2℃，伴有寒战、乏力，咳嗽较剧烈，咳少量白色粘痰，不易咳出。自服感冒药无明显改善，遂来就诊。",
            "medical_history": "既往有高血压病史 5 年，规律服用氨氯地平片，血压控制尚可。否认糖尿病、心脏病史。否认药物过敏史。吸烟史 20 年，每日约 10 支，已戒烟 2 年。偶饮酒。",
            "images": [
                {
                    "type": "胸部 CT",
                    "url": "",
                    "description": "胸部 CT 平扫显示：双肺纹理增粗、紊乱，右肺中叶及左肺下叶可见斑片状高密度影，边界模糊，其内可见支气管充气征。双侧胸腔未见明显积液。纵隔内未见明显肿大淋巴结。",
                    "date": "2024-01-15"
                }
            ],
            "lab_results": [
                {
                    "test_name": "白细胞计数",
                    "value": "15.8",
                    "unit": "×10^9/L",
                    "reference_range": "4.0-10.0",
                    "date": "2024-01-15"
                },
                {
                    "test_name": "中性粒细胞百分比",
                    "value": "85.2",
                    "unit": "%",
                    "reference_range": "50.0-70.0",
                    "date": "2024-01-15"
                },
                {
                    "test_name": "C 反应蛋白",
                    "value": "68.5",
                    "unit": "mg/L",
                    "reference_range": "0-8.0",
                    "date": "2024-01-15"
                }
            ]
        }
    }

    print("=" * 60)
    print("🧪 开始测试工作流执行 API")
    print("=" * 60)
    print(f"\n📍 URL: {url}")
    print(f"🔑 Workflow ID: {workflow_id}")
    print(f"👤 患者：{payload['patient_data']['basic_info']['name']}")
    print(f"📋 检验项目：{len(payload['patient_data']['lab_results'])} 项")
    print(f"📷 影像检查：{len(payload['patient_data']['images'])} 项")

    # 发送请求
    print("\n📤 发送请求...")
    try:
        response = requests.post(url, json=payload, timeout=None)
        print(f"📥 响应状态码：{response.status_code}")

        # 解析响应
        result = response.json()

        print("\n" + "=" * 60)
        print("📊 完整响应结果:")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 分析结果
        print("\n" + "=" * 60)
        print("📈 详细结果分析:")
        print("=" * 60)

        if result.get('success'):
            print("\n✅ 测试成功！")

            report = result.get('report', {})
            if report:
                # 诊断信息
                diagnosis = report.get('diagnosis', {})
                print(f"\n💊 主要诊断：{diagnosis.get('primary_diagnosis', 'N/A')}")
                print(f"🎯 置信度：{diagnosis.get('confidence_score', 0):.1%}")
                print(f"🔍 诊断推理：{diagnosis.get('reasoning', 'N/A')[:100]}...")

                # 风险评估
                risk = diagnosis.get('risk_assessment', 'N/A')
                print(f"⚠️ 风险评估：{risk}")

                # 推荐检查
                actions = diagnosis.get('recommended_actions', [])
                print(f"📋 推荐检查：{len(actions)} 项")
                for i, action in enumerate(actions, 1):
                    print(f"   [{i}] {action}")

                # 治疗计划
                treatment_plan = report.get('treatment_plan', [])
                print(f"\n💊 治疗计划：{len(treatment_plan)} 项")
                if treatment_plan:
                    for i, item in enumerate(treatment_plan, 1):
                        action = item.get('action', 'N/A')
                        details = item.get('details', '')
                        print(f"   [{i}] {action}")
                        if details:
                            print(f"       详情：{details}")
                else:
                    print("   ⚠️ 治疗计划为空！")

                # 随访计划
                follow_up = report.get('follow_up', {})
                print(f"\n📅 随访计划:")
                print(f"   计划：{follow_up.get('plan', 'N/A')}")
                print(f"   频率：{follow_up.get('frequency', 'N/A')}")

                # 患者教育
                patient_edu = report.get('patient_education', [])
                print(f"\n📚 患者教育：{len(patient_edu)} 条")
                for i, edu in enumerate(patient_edu, 1):
                    print(f"   [{i}] {edu}")

                # 临床发现
                findings = report.get('clinical_findings', {})
                completed = sum(
                    1 for k in ['symptom_analysis', 'history_analysis', 'lab_analysis', 'imaging_analysis'] if
                    findings.get(k))
                print(f"\n🔬 分析完成：{completed}/4")

                # 显示各项分析的简要信息
                if findings.get('symptom_analysis'):
                    symptom_result = findings['symptom_analysis'].get('result', {})
                    print(f"   ✓ 症状分析：{len(symptom_result.get('primary_symptoms', []))} 个主要症状")

                if findings.get('history_analysis'):
                    history_result = findings['history_analysis'].get('result', {})
                    print(f"   ✓ 病史分析：{len(history_result.get('risk_factors', []))} 个危险因素")

                if findings.get('lab_analysis'):
                    lab_result = findings['lab_analysis'].get('result', {})
                    print(f"   ✓ 检验分析：{len(lab_result.get('abnormal_values', []))} 个异常指标")

                if findings.get('imaging_analysis'):
                    imaging_result = findings['imaging_analysis'].get('result', {})
                    print(f"   ✓ 影像分析：{len(imaging_result.get('abnormalities', []))} 个异常发现")
            else:
                print("\n⚠️ 报告为空")
        else:
            print("\n❌ 测试失败！")
            print(f"错误信息：{result.get('message', '未知错误')}")
            print(f"错误详情：{result.get('error_details', '无详细信息')}")

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接错误：无法连接到后端服务")
        print("请确保后端已启动：uvicorn app:app --reload")
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("🏁 测试结束")
    print("=" * 60)


if __name__ == "__main__":
    test_workflow_execution()

