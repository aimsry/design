"""测试工作流执行接口 - 验证大模型输出和最终响应"""
import requests
import json
from typing import Any


def test_workflow_execution():
    """测试 workflow_1773295446 的执行结果"""

    # API 地址
    url = "http://localhost:8000/api/v1/workflow/execute"

    # 测试数据
    payload = {
        "workflow_id": "workflow_1773295446",
        "patient_data": {
            "basic_info": {
                "name": "张三",
                "gender": "male",
                "age": 45,
                "department": "呼吸内科",
                "phone": "13800138000",
                "id_card": "110101197901011234"
            },
            "symptoms": "患者主诉咳嗽、咳痰伴发热5天，体温最高39.2℃，伴有胸闷、气短。痰液为黄白色粘稠痰，每日约30-50ml。活动后呼吸困难加重，夜间有盗汗。自述食欲减退，乏力明显。",
            "medical_history": "既往有高血压病史8年，长期服用氨氯地平5mg每日一次，血压控制尚可。否认糖尿病、冠心病史。吸烟史30年，每日20支，已戒烟2年。饮酒史20年，每周2-3次白酒，每次约100ml。无药物过敏史。父亲死于肺癌，母亲患有糖尿病。",
            "images": [
                {
                    "type": "胸部CT",
                    "description": "胸部CT平扫显示：右肺上叶可见片状高密度影，边界模糊，大小约3.5×2.8cm，内可见支气管充气征。纵隔淋巴结未见明显肿大。双侧胸腔少量积液。",
                    "date": "2024-03-15",
                    "url": "chest_ct_20240315.jpg"
                }
            ],
            "lab_results": [
                {
                    "test_name": "白细胞计数(WBC)",
                    "value": "15.8",
                    "unit": "×10^9/L",
                    "reference_range": "3.5-9.5",
                    "date": "2024-03-15"
                },
                {
                    "test_name": "C反应蛋白(CRP)",
                    "value": "68.3",
                    "unit": "mg/L",
                    "reference_range": "0-10",
                    "date": "2024-03-15"
                }
            ]
        }
    }

    print("=" * 100)
    print("🧪 测试工作流执行接口")
    print("=" * 100)
    print(f"📤 请求 URL: {url}")
    print(f"📋 工作流 ID: {payload['workflow_id']}")
    print(f"👤 患者姓名: {payload['patient_data']['basic_info']['name']}")
    print("-" * 100)

    try:
        # 发送请求
        print("⏳ 发送请求到后端...")
        print("   （这可能需要30-60秒，因为要调用大模型）\n")
        response = requests.post(url, json=payload, timeout=300)

        print(f"📥 响应状态码: {response.status_code}")
        print("-" * 100)

        if response.status_code != 200:
            print(f"❌ 请求失败！")
            print(f"错误信息: {response.text}")
            return None

        # 解析响应
        result = response.json()

        # ==================== 第一部分：打印完整响应 ====================
        print("\n" + "=" * 100)
        print("📄 完整响应 JSON（格式化）")
        print("=" * 100)
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # ==================== 第二部分：关键字段检查 ====================
        print("\n" + "=" * 100)
        print("🔍 关键字段详细检查")
        print("=" * 100)

        # 检查顶层字段
        print(f"\n✅ 顶层字段:")
        print(f"   success: {result.get('success')}")
        print(f"   message: {result.get('message')}")

        # 检查 report 对象
        report = result.get('report')
        if not report:
            print("\n❌ report 对象不存在！")
            print(f"错误详情: {result.get('error_details')}")
            return result

        print(f"\n✅ report 对象存在")
        print(f"   - report_id: {report.get('report_id')}")
        print(f"   - generated_time: {report.get('generated_time')}")

        # 检查 patient_summary
        print(f"\n👤 patient_summary:")
        patient_summary = report.get('patient_summary', {})
        for key in ['name', 'age', 'gender', 'chief_complaint']:
            value = patient_summary.get(key, 'MISSING')
            if key == 'chief_complaint':
                print(f"   - {key}: '{value}' (长度: {len(value) if value else 0})")
                if not value:
                    print(f"      ⚠️  警告: chief_complaint 为空！")
                else:
                    print(f"      ✅ 有值")
            else:
                print(f"   - {key}: {value}")

        # 检查 clinical_findings
        print(f"\n🔬 clinical_findings:")
        clinical_findings = report.get('clinical_findings', {})
        for key in ['symptom_analysis', 'history_analysis', 'lab_analysis', 'imaging_analysis']:
            value = clinical_findings.get(key)
            if value:
                print(f"   ✅ {key}: 存在")
                # 打印简要信息
                if isinstance(value, dict):
                    result_data = value.get('result', {})
                    if isinstance(result_data, dict):
                        print(f"      字段: {list(result_data.keys())[:5]}")
            else:
                print(f"   ❌ {key}: 缺失")

        # 检查 diagnosis
        print(f"\n🩺 diagnosis:")
        diagnosis = report.get('diagnosis', {})
        diagnosis_fields = {
            'primary_diagnosis': str,
            'differential_diagnosis': list,
            'confidence_score': (int, float),
            'risk_assessment': str,
            'recommended_actions': list,
            'reasoning': str
        }

        for field, expected_type in diagnosis_fields.items():
            value = diagnosis.get(field, 'MISSING')
            if value == 'MISSING':
                print(f"   ❌ {field}: 缺失")
            elif isinstance(value, expected_type):
                if field == 'primary_diagnosis':
                    status = "✅" if value != "待诊断" else "⚠️"
                    print(f"   {status} {field}: '{value}'")
                    if value == "待诊断":
                        print(f"      ⚠️  警告: 使用了默认值，可能大模型未正确返回")
                elif field == 'reasoning':
                    print(f"   ✅ {field}: 存在 (长度: {len(value)})")
                    if len(value) > 100:
                        print(f"      内容预览: '{value[:100]}...'")
                elif field == 'differential_diagnosis':
                    print(f"   ✅ {field}: {len(value)} 项")
                    if value:
                        for i, diff in enumerate(value[:3], 1):
                            print(f"      {i}. {diff}")
                else:
                    print(f"   ✅ {field}: {value}")
            else:
                print(f"   ❌ {field}: 类型错误 (期望 {expected_type}, 实际 {type(value).__name__})")

        # 检查 treatment_plan
        print(f"\n💊 treatment_plan:")
        treatment_plan = report.get('treatment_plan', [])
        print(f"   - 项目数量: {len(treatment_plan)}")
        if treatment_plan:
            for i, item in enumerate(treatment_plan[:5], 1):
                action = item.get('action', 'N/A')
                details = item.get('details', '')
                print(f"     {i}. {action}")
                if details:
                    print(f"        详情: {details}")

        # 检查 follow_up
        print(f"\n📅 follow_up:")
        follow_up = report.get('follow_up', {})
        print(f"   - plan: '{follow_up.get('plan')}'")
        print(f"   - frequency: '{follow_up.get('frequency')}'")

        # 检查 patient_education
        print(f"\n📚 patient_education:")
        patient_education = report.get('patient_education', [])
        print(f"   - 建议数量: {len(patient_education)}")
        for i, edu in enumerate(patient_education, 1):
            print(f"     {i}. {edu}")

        # ==================== 第三部分：问题总结 ====================
        print("\n" + "=" * 100)
        print("📊 问题总结")
        print("=" * 100)

        issues = []

        # 检查 chief_complaint
        if not patient_summary.get('chief_complaint'):
            issues.append("❌ chief_complaint 为空字符串")

        # 检查 primary_diagnosis
        if diagnosis.get('primary_diagnosis') == '待诊断':
            issues.append("❌ primary_diagnosis 为默认值'待诊断'")

        # 检查 differential_diagnosis
        if not diagnosis.get('differential_diagnosis'):
            issues.append("⚠️  differential_diagnosis 为空数组")

        # 检查 reasoning
        if not diagnosis.get('reasoning'):
            issues.append("❌ reasoning 字段缺失")

        # 检查 risk_assessment
        risk_assessment = diagnosis.get('risk_assessment', '')
        if risk_assessment and ':' not in risk_assessment:
            issues.append("⚠️  risk_assessment 格式不规范（缺少等级前缀）")

        if issues:
            print("\n发现的问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n🎉 所有检查项均通过！")

        print("\n" + "=" * 100)
        print("✅ 测试完成")
        print("=" * 100)

        return result

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：请确保后端服务已启动")
        print("   启动命令: cd langgraph_demo && python app.py")
        return None
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时：大模型响应时间过长（超过120秒）")
        return None
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_with_backend_logs():
    """提示用户如何查看后端日志进行对比"""
    print("\n" + "=" * 100)
    print("📝 如何查看后端日志进行对比")
    print("=" * 100)
    print("""
在后端控制台日志中，查找以下关键信息：

1️⃣  大模型原始回复:
   📝 [diagnosis_generator] LLM 原始回复:
   ============================================================
   { ... JSON 内容 ... }
   ============================================================

2️⃣  JSON 解析结果:
   ✅ [diagnosis_generator] JSON 解析成功，字段：[...]

3️⃣  诊断生成器提取的数据:
   🔍 [DEBUG] 诊断生成器原始输出:
      preliminary_diagnosis keys: [...]
      treatment_plan keys: [...]

4️⃣  最终返回的 result_dict:
   🔍 [DEBUG] 最终返回的 result_dict:
      final_diagnosis keys: [...]
      treatment_recommendations 数量：X

将后端日志中的 final_diagnosis keys 与前端收到的 diagnosis 字段对比，
确认数据是否正确传递。
    """)


if __name__ == "__main__":
    print("\n" + "🚀" * 50)
    print("开始测试工作流执行接口")
    print("🚀" * 50 + "\n")

    # 执行测试
    result = test_workflow_execution()

    if result:
        # 显示后端日志查看提示
        compare_with_backend_logs()

        # 保存结果到文件
        output_file = "test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 测试结果已保存到: {output_file}")
