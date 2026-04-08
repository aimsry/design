"""
工作流执行 API 接口测试脚本（完整版）
功能：
1. 测试后端 API 接口
2. 显示每个智能体的 LLM 输出
3. 完善的错误处理和日志输出
4. 无超时限制，等待所有智能体执行完成
"""
import requests
import json
from pathlib import Path
from datetime import datetime


def print_section(title, icon="", width=80):
    """打印分隔线和标题"""
    print("\n" + "=" * width)
    if icon:
        print(f"{icon} {title}")
    else:
        print(title)
    print("=" * width)


def print_smart_agent_output(agent_name, agent_data, icon):
    """智能格式化显示智能体输出"""
    print_section(f"{icon} {agent_name}", "")

    # 显示执行时间
    timestamp = agent_data.get('timestamp', 'N/A')
    print(f"⏰ 执行时间：{timestamp}")

    # 显示智能体名称
    agent_name_field = agent_data.get('agent_name', 'unknown')
    print(f"🤖 智能体：{agent_name_field}")

    # 显示 LLM 输出结果
    result_data = agent_data.get('result', {})
    if not result_data:
        print("⚠️ 未找到 LLM 输出结果")
        return

    print(f"\n💬 LLM 输出内容:")
    print("-" * 80)

    # 根据不同智能体类型显示不同内容
    display_smart_agent_result(result_data, agent_name_field)

    print("-" * 80)


def display_smart_agent_result(result_data, agent_name):
    """根据智能体类型显示对应的输出内容"""

    if 'symptom' in agent_name:
        # 症状分析器
        primary_symptoms = result_data.get('primary_symptoms', [])
        print(f"\n【主要症状】")
        for i, symptom in enumerate(primary_symptoms, 1):
            print(f"  {i}. {symptom}")

        severity = result_data.get('severity', 'N/A')
        print(f"\n【严重程度】{severity}")

        duration = result_data.get('duration', 'N/A')
        print(f"\n【持续时间】{duration}")

        characteristics = result_data.get('characteristics', {})
        if characteristics:
            print(f"\n【症状特征】")
            for symptom_type, desc in characteristics.items():
                print(f"  • {symptom_type}: {desc}")

    elif 'history' in agent_name:
        # 病史分析器
        risk_factors = result_data.get('risk_factors', [])
        print(f"\n【危险因素】")
        for i, factor in enumerate(risk_factors, 1):
            print(f"  {i}. {factor}")

        past_diseases = result_data.get('past_diseases', [])
        print(f"\n【既往疾病】")
        for i, disease in enumerate(past_diseases, 1):
            print(f"  {i}. {disease}")

        medications = result_data.get('medications', [])
        print(f"\n【用药情况】")
        for i, med in enumerate(medications, 1):
            print(f"  {i}. {med}")

        lifestyle = result_data.get('lifestyle_factors', {})
        if lifestyle:
            print(f"\n【生活方式】")
            for habit, desc in lifestyle.items():
                print(f"  • {habit}: {desc}")

    elif 'imaging' in agent_name:
        # 影像分析器
        main_findings = result_data.get('main_findings', [])
        print(f"\n【主要发现】")
        for i, finding in enumerate(main_findings, 1):
            print(f"  {i}. {finding}")

        abnormalities = result_data.get('abnormalities', [])
        print(f"\n【异常表现】")
        for abnormality in abnormalities:
            if isinstance(abnormality, dict):
                location = abnormality.get('location', 'N/A')
                finding = abnormality.get('finding', 'N/A')
                print(f"  • {location}: {finding}")
            else:
                print(f"  • {abnormality}")

        affected_areas = result_data.get('affected_areas', [])
        print(f"\n【受累部位】")
        for i, area in enumerate(affected_areas, 1):
            print(f"  {i}. {area}")

        suggestions = result_data.get('diagnostic_suggestions', '')
        print(f"\n【诊断建议】{suggestions}")

    elif 'lab' in agent_name:
        # 检验分析器
        abnormal_values = result_data.get('abnormal_values', [])
        print(f"\n【异常指标】")
        for item in abnormal_values:
            if isinstance(item, dict):
                name = item.get('name', 'N/A')
                value = item.get('value', 'N/A')
                ref = item.get('reference_range', 'N/A')
                print(f"  ❌ {name}: {value} (参考范围：{ref})")
            else:
                print(f"  ❌ {item}")

        significance = result_data.get('clinical_significance', '')
        print(f"\n【临床意义】{significance}")

        organ_function = result_data.get('organ_function', {})
        if organ_function:
            print(f"\n【器官功能评估】")
            for organ, status in organ_function.items():
                print(f"  • {organ}: {status}")

        inflammatory_markers = result_data.get('inflammatory_markers', [])
        print(f"\n【炎症指标】")
        for marker_item in inflammatory_markers:
            if isinstance(marker_item, dict):
                marker = marker_item.get('marker', 'N/A')
                status = marker_item.get('status', 'N/A')
                print(f"  • {marker}: {status}")
            else:
                print(f"  • {marker_item}")

    elif 'diagnosis' in agent_name:
        # 诊断生成器
        primary_diagnosis = result_data.get('primary_diagnosis', 'N/A')
        print(f"\n【主要诊断】")
        print(f"  🎯 {primary_diagnosis}")

        diff_diagnosis = result_data.get('differential_diagnosis', [])
        print(f"\n【鉴别诊断】")
        for i, d in enumerate(diff_diagnosis, 1):
            print(f"  {i}. {d}")

        confidence = result_data.get('confidence_score', 0)
        print(f"\n【置信度】{confidence:.1%}")

        risk = result_data.get('risk_assessment', 'N/A')
        urgency = result_data.get('urgency', 'N/A')
        print(f"\n【风险评估】{risk}")
        print(f"【紧急程度】{urgency}")

        actions = result_data.get('recommended_actions', [])
        print(f"\n【治疗建议】")
        for i, action in enumerate(actions, 1):
            if isinstance(action, str):
                print(f"  {i}. {action}")
            else:
                action_name = action.get('action', 'N/A')
                details = action.get('details', '')
                print(f"  {i}. {action_name}")
                if details:
                    print(f"     详情：{details}")


def main():
    """主测试函数"""

    print_section("开始测试工作流执行 API", "🧪")
    print(f"📅 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ==================== 配置区域 ====================
    API_URL = "http://localhost:8000/api/v1/workflow/execute"
    WORKFLOW_ID = "workflow_1773295457"

    print(f"\n🔑 使用的工作流 ID: {WORKFLOW_ID}")
    print(f"🌐 API 地址：{API_URL}")

    # 加载工作流文件
    graphs_dir = Path(__file__).parent / "graphs"
    workflow_file = graphs_dir / f"{WORKFLOW_ID}.json"

    if not workflow_file.exists():
        print(f"\n❌ 工作流文件不存在：{workflow_file}")
        print(f"请确认 graphs 目录下有 {WORKFLOW_ID}.json 文件")
        return

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)

    # 检查工作流结构
    has_diagnosis = any(
        node.get('data', {}).get('agentId') == 'diagnosis_generator'
        for node in workflow_data.get('nodes', [])
    )

    if has_diagnosis:
        print("✅ 工作流包含诊断生成器节点")
    else:
        print("\n⚠️  警告：该工作流不包含诊断生成器节点")
        print("建议在前端工作流图中添加 diagnosis_generator 智能体")

    # 显示工作流信息
    print(f"\n📊 工作流结构:")
    print(f"   - 节点数：{len(workflow_data.get('nodes', []))}")
    print(f"   - 边数：{len(workflow_data.get('edges', []))}")

    agent_nodes = [
        node for node in workflow_data.get('nodes', [])
        if node.get('type') == 'agent'
    ]
    print(f"\n🤖 智能体节点列表 ({len(agent_nodes)} 个):")
    for node in agent_nodes:
        agent_id = node.get('data', {}).get('agentId', '未知')
        label = node.get('data', {}).get('label', '未知')
        print(f"   - {label} ({agent_id})")

    # ==================== 测试数据 ====================
    patient_data = {
        "workflow_id": WORKFLOW_ID,
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

    print(f"\n👤 测试患者：{patient_data['patient_data']['basic_info']['name']}")
    print(f"📋 影像检查：{len(patient_data['patient_data']['images'])} 项")
    print(f"🔬 检验项目：{len(patient_data['patient_data']['lab_results'])} 项")

    # ==================== 发送请求 ====================
    print_section("正在发送请求到后端...", "📤")
    print("⏳ 请耐心等待所有智能体执行完成（可能需要几分钟）...")
    print("⚠️  此过程没有超时限制，会一直等待直到所有智能体完成")

    try:
        # 发送 POST 请求 - 无超时限制
        response = requests.post(API_URL, json=patient_data, timeout=None)

        print(f"\n📥 响应状态码：{response.status_code}")

        # 解析响应
        result = response.json()

        # ==================== 完整响应结果 ====================
        print_section("完整响应结果", "📊")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # ==================== 错误检查 ====================
        if not result.get('success'):
            print_section("❌ 后端执行失败", "🚨")
            print(f"\n错误信息：{result.get('message', '未知错误')}")
            print(f"错误详情：{result.get('error_details', '无详细信息')}")

            error_details = result.get('error_details', '')
            print(f"\n💡 调试建议:")

            if 'NoneType' in error_details or "'get'" in error_details:
                print("   1. 工作流中可能缺少 diagnosis_generator 节点")
                print("   2. 某个智能体执行失败，导致后续流程中断")
                print("   3. 工作流图的边连接有问题")
                print("   4. 查看后端控制台的 Python 异常堆栈信息")
            elif 'diagnosis_generator' in error_details:
                print("   1. 诊断生成器执行失败")
                print("   2. 检查前面的分析节点是否正常完成")
                print("   3. 检查 LLM API Key 是否配置正确")
                print("   4. 检查网络连接是否正常")
            else:
                print("   1. 查看后端控制台的详细日志")
                print("   2. 检查工作流配置是否正确")
                print("   3. 确认所有智能体都已正确配置")

            # 提前结束
            print_section("测试结束（失败）", "🏁")
            return

        # ==================== 显示各智能体的详细输出 ====================
        print_section("各智能体 LLM 输出详情", "🤖")

        report = result.get('report', {})
        if not report:
            print("\n⚠️  警告：返回的报告为空")
            print_section("测试结束（报告为空）", "🏁")
            return

        findings = report.get('clinical_findings', {})

        # 1. 症状分析器
        symptom_analysis = findings.get('symptom_analysis')
        if symptom_analysis:
            print_smart_agent_output("症状分析器", symptom_analysis, "📋")
        else:
            print_section("1️⃣ 症状分析器 - 未执行", "⚠️")

        # 2. 病史分析器
        history_analysis = findings.get('history_analysis')
        if history_analysis:
            print_smart_agent_output("病史分析器", history_analysis, "📜")
        else:
            print_section("2️⃣ 病史分析器 - 未执行", "⚠️")

        # 3. 影像分析器
        imaging_analysis = findings.get('imaging_analysis')
        if imaging_analysis:
            print_smart_agent_output("影像分析器", imaging_analysis, "📷")
        else:
            print_section("3️⃣ 影像分析器 - 未执行", "⚠️")

        # 4. 检验分析器
        lab_analysis = findings.get('lab_analysis')
        if lab_analysis:
            print_smart_agent_output("检验分析器", lab_analysis, "🔬")
        else:
            print_section("4️⃣ 检验分析器 - 未执行", "⚠️")

        # 5. 诊断生成器
        print_section("5️⃣ 诊断生成器", "💊")
        diagnosis = report.get('diagnosis', {})

        if diagnosis and diagnosis.get('primary_diagnosis') != '诊断流程异常，请重新提交':
            display_smart_agent_result(diagnosis, 'diagnosis_generator')
        else:
            print("⚠️ 诊断生成器未正常工作或输出异常")
            print(f"   返回的诊断：{diagnosis}")

        # ==================== 结果总结 ====================
        print_section("测试结果总结", "📈")

        print("\n✅ 测试成功！")

        # 统计完成情况
        analysis_count = 0
        total_expected = 4

        print(f"\n🔬 分析结果完成情况:")
        analysis_items = [
            ('symptom_analysis', '症状分析'),
            ('history_analysis', '病史分析'),
            ('lab_analysis', '检验分析'),
            ('imaging_analysis', '影像分析')
        ]

        for key, name in analysis_items:
            if findings.get(key):
                print(f"   ✅ {name}: 已完成")
                analysis_count += 1
            else:
                print(f"   ⚠️  {name}: 未执行")

        print(f"\n📊 完成率：{analysis_count}/{total_expected} ({analysis_count/total_expected*100:.0f}%)")

        # 最终诊断
        if diagnosis_count >= 3 and diagnosis.get('primary_diagnosis'):
            print(f"\n🎉 工作流执行成功！生成了完整的诊断报告")
            print(f"\n💡 最终诊断结果:")
            print(f"   🎯 {diagnosis.get('primary_diagnosis')}")
        else:
            print(f"\n⚠️  部分分析未执行或诊断未完成")

    except requests.exceptions.ConnectionError as e:
        print_section("连接错误", "❌")
        print(f"\n❌ 无法连接到后端服务")
        print(f"\n请确保后端已启动:")
        print(f"   cd C:\\Users\\DELL\\Medical_agents_project\\langgraph_demo")
        print(f"   uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        print(f"\n监听地址：http://localhost:8000")

    except requests.exceptions.Timeout:
        print_section("请求超时", "⏰")
        print(f"\n❌ 请求超时：等待时间过长")
        print(f"\n可能原因:")
        print(f"   1. LLM API 响应慢")
        print(f"   2. 网络延迟")
        print(f"   3. 后端处理卡住")
        print(f"\n建议:")
        print(f"   1. 检查网络连接")
        print(f"   2. 查看后端日志")
        print(f"   3. 确认 LLM API Key 有效")

    except Exception as e:
        print_section("测试异常", "❌")
        print(f"\n❌ 测试异常：{e}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()

    print_section("测试结束", "🏁")


if __name__ == "__main__":
    main()
