"""工作流执行引擎 - 支持拓扑排序和并行执行"""
import asyncio
from typing import Dict, Any, List, Set
from collections import defaultdict, deque
from .state_manager import StateManager
from .nodes.medical.symptom_analyzer import SymptomAnalyzer
from .nodes.medical.history_analyzer import HistoryAnalyzer
from .nodes.medical.lab_analyzer import LabAnalyzer
from .nodes.medical.imaging_analyzer import ImagingAnalyzer
from .nodes.medical.diagnosis_generator import DiagnosisGenerator


class WorkflowExecutor:
    """动态工作流执行器"""

    def __init__(self, workflow_definition: Dict[str, Any]):
        self.workflow = workflow_definition
        self.nodes = workflow_definition.get("nodes", [])
        self.edges = workflow_definition.get("edges", [])

        # 智能体工厂
        self.agent_factory = {
            "symptom_analyzer": SymptomAnalyzer,
            "history_analyzer": HistoryAnalyzer,
            "lab_analyzer": LabAnalyzer,
            "imaging_analyzer": ImagingAnalyzer,
            "diagnosis_generator": DiagnosisGenerator,
        }

        # 状态管理器
        self.state_manager = StateManager()
        self.state = None

        # 缓存已创建的智能体实例
        self.agents = {}

    def _build_graph(self) -> tuple[Dict[str, List[str]], Dict[str, int]]:
        """
        构建邻接表和入度表

        Returns:
            (adjacency_list, in_degree_dict)
            - adjacency_list: {node_id: [successor_node_ids]}
            - in_degree_dict: {node_id: incoming_edge_count}
        """
        adjacency = defaultdict(list)
        in_degree = defaultdict(int)

        # 初始化所有节点的入度为 0
        for node in self.nodes:
            node_id = node["id"]
            if node_id not in in_degree:
                in_degree[node_id] = 0

        # 根据边构建图
        for edge in self.edges:
            source = edge["source"]
            target = edge["target"]

            adjacency[source].append(target)
            in_degree[target] += 1

            # 确保 source 也在 in_degree 中
            if source not in in_degree:
                in_degree[source] = 0

        return dict(adjacency), dict(in_degree)

    def _topological_sort(self) -> List[List[str]]:
        """
        拓扑排序，返回分层的结果，每层可以并行执行

        Returns:
            List[List[str]]: 分层节点 ID 列表，每层内的节点可以并行执行
            例如：[["start"], ["node1", "node2"], ["node3"], ["end"]]
        """
        adjacency, in_degree = self._build_graph()

        # 找到所有入度为 0 的节点作为起始点
        queue = deque()
        for node_id, degree in in_degree.items():
            if degree == 0:
                queue.append(node_id)

        result = []
        while queue:
            # 当前层的所有节点
            current_level = list(queue)
            result.append(current_level)

            # 清空队列用于下一层
            queue.clear()

            # 处理当前层的所有节点
            for node_id in current_level:
                # 减少所有后继节点的入度
                for successor in adjacency.get(node_id, []):
                    in_degree[successor] -= 1
                    if in_degree[successor] == 0:
                        queue.append(successor)

        # 检查是否有环（如果还有节点入度不为 0）
        total_nodes = len(in_degree)
        processed_nodes = sum(len(level) for level in result)

        if processed_nodes != total_nodes:
            raise ValueError("图中存在环，无法进行拓扑排序")

        return result

    def _create_agent(self, agent_id: str):
        """根据 agent_id 创建智能体实例"""
        if agent_id in self.agents:
            return self.agents[agent_id]

        if agent_id not in self.agent_factory:
            raise ValueError(f"未知的智能体类型：{agent_id}")

        agent = self.agent_factory[agent_id]()
        self.agents[agent_id] = agent
        return agent

    def _get_agent_id_from_node(self, node: Dict[str, Any]) -> str:
        """从节点配置中提取 agent_id"""
        data = node.get("data", {})
        agent_id = data.get("agentId")

        if not agent_id:
            raise ValueError(f"节点 {node['id']} 未指定 agentId")

        return agent_id

    async def _execute_node(self, node_id: str) -> Dict[str, Any]:
        """执行单个节点"""
        # 找到对应的节点配置
        node_config = None
        for node in self.nodes:
            if node["id"] == node_id:
                node_config = node
                break

        if not node_config:
            raise ValueError(f"节点配置不存在：{node_id}")

        node_type = node_config.get("type")

        # 跳过开始和结束节点
        if node_type in ["start", "end"]:
            print(f"⏭️ 跳过 {node_type} 节点：{node_id}")
            return {"status": "skipped"}

        # 执行智能体节点
        agent_id = self._get_agent_id_from_node(node_config)
        print(f"🤖 执行智能体：{agent_id} (节点 ID: {node_id})")

        try:
            agent = self._create_agent(agent_id)
            result = agent.execute(self.state)

            # 更新状态 - 特殊处理诊断生成器
            if agent_id == "diagnosis_generator":
                # 打印大模型返回的原始结果用于调试
                print(f"\n🔍 [DEBUG] 诊断生成器原始输出:")
                print(f"   preliminary_diagnosis keys: {list(result.get('preliminary_diagnosis', {}).keys())}")
                print(f"   treatment_plan keys: {list(result.get('treatment_plan', {}).keys())}")
                print(f"   treatment_plan.medications: {result.get('treatment_plan', {}).get('medications', [])}")
                print(
                    f"   treatment_plan.non_pharmacological: {result.get('treatment_plan', {}).get('non_pharmacological', [])}")

                # 将诊断生成器的输出转换为最终诊断格式
                preliminary_diagnosis = result.get("preliminary_diagnosis", {})
                risk_assessment = result.get("risk_assessment", {})
                urgency = result.get("urgency", {})
                treatment_plan_data = result.get("treatment_plan", {})

                # 🔹 提取 further_tests 作为推荐行动
                further_tests = treatment_plan_data.get("further_tests", ["需要进一步检查"])

                # 🔹 调试打印
                print(f"\n🔍 [DEBUG] diagnosis_generator 提取的数据:")
                print(f"   further_tests: {further_tests}")
                print(f"   further_tests 类型：{type(further_tests)}")
                print(f"   urgency: {urgency}")

                # 确保 further_tests 是列表
                if not isinstance(further_tests, list):
                    print(f"   ⚠️ 警告：further_tests 不是列表，强制转换")
                    further_tests = ["需要进一步检查"]

                # 构建 final_diagnosis 对象
                final_diagnosis_data = {
                    "primary_diagnosis": preliminary_diagnosis.get("primary_diagnosis", "待诊断"),
                    "differential_diagnosis": preliminary_diagnosis.get("differential_diagnosis", []),
                    "confidence_score": 0.85,  # 默认置信度
                    "risk_assessment": risk_assessment,
                    "urgency": urgency,
                    "recommended_actions": further_tests,
                    "reasoning": preliminary_diagnosis.get("reasoning", "诊断依据待补充"),
                    # 🔹 新增：保存 chief_complaint 和其他关键字段供 routes.py 使用
                    "chief_complaint": result.get("chief_complaint", ""),
                    "history_of_present_illness": result.get("history_of_present_illness", ""),
                    "physical_examination": result.get("physical_examination", {}),
                    "auxiliary_examinations": result.get("auxiliary_examinations", {}),
                    "patient_info": result.get("patient_info", {}),
                    "follow_up_plan": result.get("follow_up_plan", {})
                }

                self.state = self.state_manager.set_final_diagnosis(final_diagnosis_data)
                print(f"✅ 诊断生成器执行完成，已设置最终诊断")

                # 🔹 打印 final_diagnosis_data
                print(f"\n🔍 [DEBUG] final_diagnosis_data:")
                print(f"   recommended_actions: {final_diagnosis_data.get('recommended_actions')}")
                print(f"   recommended_actions 类型：{type(final_diagnosis_data.get('recommended_actions'))}")
                print(f"   urgency: {final_diagnosis_data.get('urgency')}")

                # 保存治疗计划到状态中
                medications = treatment_plan_data.get("medications", [])
                non_pharm = treatment_plan_data.get("non_pharmacological", [])

                print(f"\n🔍 [DEBUG] 准备提取的治疗计划:")
                print(f"   medications 数量：{len(medications)}")
                print(f"   non_pharm 数量：{len(non_pharm)}")

                # 构建治疗建议列表
                treatment_recommendations = []

                # 添加药物治疗
                for med in medications:
                    drug_name = med.get("drug_name", "未知药物")
                    dosage = med.get("dosage", "")
                    usage = med.get("usage", "")
                    frequency = med.get("frequency", "")
                    duration = med.get("duration", "")

                    treatment_recommendations.append({
                        "action": f"药物治疗：{drug_name}",
                        "details": f"{dosage} {usage} {frequency} {duration}".strip()
                    })

                # 添加非药物治疗
                for action in non_pharm:
                    treatment_recommendations.append({
                        "action": f"非药物治疗：{action}",
                        "details": ""
                    })

                # 保存到状态
                self.state.treatment_recommendations = treatment_recommendations

                print(f"\n🔍 [DEBUG] 构建完成的治疗建议:")
                print(f"   treatment_recommendations 数量：{len(treatment_recommendations)}")
                for i, rec in enumerate(treatment_recommendations):
                    print(f"   [{i}] action: {rec['action']}")
                    print(f"       details: {rec['details']}")

            else:
                self.state = self.state_manager.update_analysis_result(agent_id, result)
                print(f"✅ 智能体 {agent_id} 执行完成")

            return {"status": "success", "agent_id": agent_id, "result": result}

        except Exception as e:
            print(f"❌ 智能体 {agent_id} 执行失败：{e}")
            # 继续执行其他节点，不中断整个流程
            return {"status": "failed", "agent_id": agent_id, "error": str(e)}

    async def _execute_layer(self, layer: List[str]) -> Dict[str, Any]:
        """并行执行一层中的所有节点"""
        if len(layer) == 1:
            # 只有一个节点，直接顺序执行
            result = await self._execute_node(layer[0])
            return {layer[0]: result}

        # 多个节点，并行执行
        print(f"🔄 并行执行层：{layer}")
        tasks = {node_id: self._execute_node(node_id) for node_id in layer}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # 整理结果
        layer_results = {}
        for (node_id, _), result in zip(tasks.items(), results):
            if isinstance(result, Exception):
                layer_results[node_id] = {
                    "status": "exception",
                    "error": str(result)
                }
            else:
                layer_results[node_id] = result

        return layer_results

    async def execute(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行完整工作流

        Args:
            patient_data: 患者数据

        Returns:
            最终状态字典
        """
        print("🏥 开始执行医疗诊断工作流...")
        print(f"📋 患者：{patient_data['basic_info']['name']}")
        print(f"🔧 工作流配置：{len(self.nodes)} 个节点，{len(self.edges)} 条边")

        # 1. 初始化状态
        self.state = self.state_manager.initialize_state(patient_data)
        print("✅ 状态初始化完成")

        # 2. 拓扑排序
        try:
            sorted_layers = self._topological_sort()
            print(f"📊 拓扑排序完成，共 {len(sorted_layers)} 层")
            for i, layer in enumerate(sorted_layers):
                print(f"   层 {i + 1}: {layer}")
        except ValueError as e:
            print(f"❌ 拓扑排序失败：{e}")
            raise

        # 3. 按层执行
        all_results = {}
        for i, layer in enumerate(sorted_layers):
            print(f"\n🎯 执行第 {i + 1}/{len(sorted_layers)} 层")
            layer_results = await self._execute_layer(layer)
            all_results[f"layer_{i + 1}"] = layer_results

            # 检查是否有致命错误（所有节点都失败）
            if all(r.get("status") == "failed" for r in layer_results.values()):
                print(f"⚠️ 第 {i + 1} 层所有节点执行失败，终止流程")
                break

        # 4. 查找并执行诊断生成器（如果还没执行）
        diagnosis_executed = False
        for layer_results in all_results.values():
            for result in layer_results.values():
                if isinstance(result, dict) and result.get("agent_id") == "diagnosis_generator":
                    diagnosis_executed = True
                    break

        if not diagnosis_executed:
            print(f"\n⚠️ 诊断生成器未执行，尝试查找并执行...")
            for node in self.nodes:
                # 跳过 start 和 end 节点
                if node.get("type") in ["start", "end"]:
                    continue

                try:
                    agent_id = self._get_agent_id_from_node(node)
                    if agent_id == "diagnosis_generator":
                        result = await self._execute_node(node["id"])
                        if result["status"] == "success":
                            print("✅ 诊断生成器补执行成功")
                            diagnosis_executed = True
                        break
                except ValueError:
                    # 节点没有 agentId，跳过
                    continue

        # 5. 如果没有诊断生成器，设置默认诊断
        if not diagnosis_executed:
            print("⚠️ 未找到诊断生成器，设置默认诊断")
            default_diagnosis = {
                "primary_diagnosis": "诊断流程异常，请重新提交",
                "differential_diagnosis": ["需要重新检查"],
                "risk_assessment": "unknown",
                "urgency": "routine"
            }
            self.state = self.state_manager.set_final_diagnosis(default_diagnosis)

        print("\n✅ 医疗诊断工作流完成！")
        final_dict = self.state.to_dict()
        print(f"\n🔍 [DEBUG] 最终返回的 result_dict:")
        print(f"   final_diagnosis keys: {list(final_dict.get('final_diagnosis', {}).keys())}")
        print(f"   treatment_recommendations 数量：{len(final_dict.get('treatment_recommendations', []))}")
        if final_dict.get('treatment_recommendations'):
            for i, rec in enumerate(final_dict['treatment_recommendations']):
                print(f"   [{i}] {rec}")

        return final_dict

    def execute_sync(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """同步执行接口"""
        return asyncio.run(self.execute(patient_data))
