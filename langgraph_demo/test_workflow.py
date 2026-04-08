"""
工作流执行引擎测试
放在 langgraph_demo 目录下，和 src 文件夹同级
"""
import sys
from pathlib import Path

# 关键：添加当前目录到 Python 路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
import json
from src.agent.workflow_executor import WorkflowExecutor

# 测试用例 1：并行工作流
PARALLEL_WORKFLOW = {
    "graph_id": "test_parallel",
    "nodes": [
        {"id": "start", "type": "start", "data": {"label": "开始"}},
        {"id": "symptom", "type": "agent", "data": {"agentId": "symptom_analyzer"}},
        {"id": "lab", "type": "agent", "data": {"agentId": "lab_analyzer"}},
        {"id": "imaging", "type": "agent", "data": {"agentId": "imaging_analyzer"}},
        {"id": "diagnosis", "type": "agent", "data": {"agentId": "diagnosis_generator"}},
        {"id": "end", "type": "end", "data": {"label": "结束"}}
    ],
    "edges": [
        {"source": "start", "target": "symptom"},
        {"source": "symptom", "target": "lab"},
        {"source": "symptom", "target": "imaging"},  # 并行分支
        {"source": "lab", "target": "diagnosis"},
        {"source": "imaging", "target": "diagnosis"},  # 并行汇合
        {"source": "diagnosis", "target": "end"}
    ]
}

# 测试用例 2：线性工作流
LINEAR_WORKFLOW = {
    "graph_id": "test_linear",
    "nodes": [
        {"id": "start", "type": "start", "data": {"label": "开始"}},
        {"id": "n1", "type": "agent", "data": {"agentId": "symptom_analyzer"}},
        {"id": "n2", "type": "agent", "data": {"agentId": "history_analyzer"}},
        {"id": "n3", "type": "agent", "data": {"agentId": "lab_analyzer"}},
        {"id": "end", "type": "end", "data": {"label": "结束"}}
    ],
    "edges": [
        {"source": "start", "target": "n1"},
        {"source": "n1", "target": "n2"},
        {"source": "n2", "target": "n3"},
        {"source": "n3", "target": "end"}
    ]
}

SAMPLE_PATIENT = {
    "basic_info": {"name": "张三", "gender": "male", "age": 35},
    "symptoms": "发热、咳嗽",
    "medical_history": "无",
    "images": [],
    "lab_results": []
}


def test_topological_sort():
    """测试拓扑排序 - 验证并行层识别"""
    print("\n" + "=" * 60)
    print("测试 1：拓扑排序")
    print("=" * 60)

    executor = WorkflowExecutor(PARALLEL_WORKFLOW)
    layers = executor._topological_sort()

    print(f"\n并行工作流分层结果:")
    for i, layer in enumerate(layers, 1):
        print(f"  第{i}层：{layer}")

    # 验证：应该存在包含多个节点的层（并行）
    parallel_found = any(len(layer) > 1 for layer in layers)
    assert parallel_found, "应该检测到并行节点"

    print("✅ 拓扑排序测试通过")
    return True


def test_linear_workflow():
    """测试线性工作流 - 每层只有一个节点"""
    print("\n" + "=" * 60)
    print("测试 2：线性工作流")
    print("=" * 60)

    executor = WorkflowExecutor(LINEAR_WORKFLOW)
    layers = executor._topological_sort()

    print(f"\n线性工作流分层结果:")
    for i, layer in enumerate(layers, 1):
        print(f"  第{i}层：{layer}")

    # 验证：每层只能有一个节点
    assert all(len(layer) == 1 for layer in layers), "线性工作流每层应该只有一个节点"

    print("✅ 线性工作流测试通过")
    return True


def test_real_workflow():
    """测试真实的工作流文件"""
    print("\n" + "=" * 60)
    print("测试 3：真实工作流文件")
    print("=" * 60)

    # 使用绝对路径：相对于当前测试文件
    graphs_dir = current_dir / "graphs"
    if not graphs_dir.exists():
        print("❌ graphs 目录不存在")
        return False

    json_files = list(graphs_dir.glob("*.json"))
    if not json_files:
        print("❌ 没有找到工作流文件")
        return False

    # 加载第一个文件
    workflow_file = json_files[0]
    print(f"\n加载：{workflow_file.name}")

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_def = json.load(f)

    executor = WorkflowExecutor(workflow_def)
    layers = executor._topological_sort()

    print(f"\n工作流 '{workflow_def.get('graph_id')}' 的分层:")
    for i, layer in enumerate(layers, 1):
        print(f"  第{i}层：{layer}")

    # 检查是否有并行层
    parallel_layers = [l for l in layers if len(l) > 1]
    if parallel_layers:
        print(f"✅ 检测到 {len(parallel_layers)} 个并行层")
    else:
        print("ℹ️ 该工作流是线性的")

    print("✅ 真实工作流测试通过")
    return True


if __name__ == "__main__":
    print("🧪 开始测试工作流执行引擎")

    tests = [
        ("拓扑排序", test_topological_sort),
        ("线性工作流", test_linear_workflow),
        ("真实工作流", test_real_workflow)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}测试失败：{e}")
            results.append((name, False))

    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    total = sum(1 for _, p in results if p)
    print(f"\n总计：{total}/{len(results)} 通过")

    if total == len(results):
        print("\n🎉 所有测试通过！")
