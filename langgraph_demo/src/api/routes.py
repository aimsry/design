from fastapi import APIRouter, HTTPException
import time
from typing import List, Dict, Any

from .schemas import (
    DiagnosisRequest,
    DiagnosisResponse,
    MedicalReport,
    DiagnosisResult,
    WorkflowDefinition,
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowExecuteRequest,
    WorkflowResponse,
    AvailableAgentsResponse,
    AgentInfo
)

# 导入医疗图构建器
from src.agent.graph_bulider import MedicalGraph

router = APIRouter()


@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用智能体工作流编排系统 API",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/workflow/execute - 执行工作流",
            "/api/v1/workflows - 管理工作流",
            "/api/v1/agents - 查看可用智能体"
        ]
    }


@router.post("/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(request: DiagnosisRequest):
    """创建诊断报告（旧接口，保留用于向后兼容）"""
    try:
        # 直接调用医疗图构建器
        medical_graph = MedicalGraph()

        # 执行诊断流程
        result_dict = medical_graph.execute({
            "basic_info": request.patient_info.dict(),
            "symptoms": request.symptoms,
            "medical_history": request.medical_history,
            "images": [img.dict() for img in request.images],
            "lab_results": [lab.dict() for lab in request.lab_results]
        })

        # 构造诊断结果
        final_diagnosis = result_dict.get("final_diagnosis", {})

        # 处理 risk_assessment - 将字典转换为字符串
        risk_assessment_raw = final_diagnosis.get("risk_assessment", "unknown")
        if isinstance(risk_assessment_raw, dict):
            level = risk_assessment_raw.get("level", "unknown")
            description = risk_assessment_raw.get("description", "")
            risk_assessment_str = f"{level}: {description}" if description else level
        elif isinstance(risk_assessment_raw, str):
            risk_assessment_str = risk_assessment_raw
        else:
            risk_assessment_str = "unknown"

        diagnosis_result = DiagnosisResult(
            primary_diagnosis=final_diagnosis.get("primary_diagnosis", "待诊断"),
            differential_diagnosis=final_diagnosis.get("differential_diagnosis", []),
            confidence_score=float(final_diagnosis.get("confidence_score", 0.0)),
            risk_assessment=risk_assessment_str,
            recommended_actions=final_diagnosis.get("recommended_actions", ["需要进一步检查"]),
            reasoning=final_diagnosis.get("reasoning", "诊断依据待补充")
        )

        # 构造患者摘要
        patient_summary = {
            "name": request.patient_info.name,
            "age": str(request.patient_info.age),
            "gender": request.patient_info.gender,
            "chief_complaint": request.symptoms[:50] + "..." if len(request.symptoms) > 50 else request.symptoms
        }

        # 构造治疗计划
        treatment_plan = []
        recommendations = result_dict.get("treatment_recommendations", [])
        if isinstance(recommendations, list):
            for rec in recommendations:
                if isinstance(rec, dict):
                    treatment_plan.append({
                        "action": rec.get("action", "待确定"),
                        "details": rec.get("details", "")
                    })
                elif isinstance(rec, str):
                    treatment_plan.append({"action": rec, "details": ""})

        # 构造随访计划
        follow_up = {
            "plan": "根据诊断结果制定个体化随访计划",
            "frequency": "按医嘱执行"
        }

        # 构造患者教育
        patient_education = [
            "请遵医嘱按时服药",
            "注意休息，避免剧烈运动",
            "定期复查相关指标",
            "如有不适及时就医"
        ]

        # 创建完整的医疗报告
        medical_report = MedicalReport(
            report_id=f"REP_{int(time.time())}",
            generated_time=time.strftime("%Y-%m-%d %H:%M:%S"),
            patient_summary=patient_summary,
            clinical_findings={
                "symptom_analysis": result_dict.get("symptom_analysis"),
                "history_analysis": result_dict.get("history_analysis"),
                "lab_analysis": result_dict.get("lab_analysis"),
                "imaging_analysis": result_dict.get("imaging_analysis")
            },
            diagnosis=diagnosis_result,
            treatment_plan=treatment_plan,
            follow_up=follow_up,
            patient_education=patient_education
        )

        return DiagnosisResponse(
            success=True,
            message="诊断完成",
            report=medical_report
        )

    except Exception as e:
        return DiagnosisResponse(
            success=False,
            message="诊断失败",
            error_details=str(e)
        )


@router.get("/workflows", response_model=List[WorkflowDefinition])
async def list_workflows():
    """获取所有工作流列表"""
    try:
        from pathlib import Path
        import json

        graphs_dir = Path(__file__).parent.parent.parent / "graphs"
        if not graphs_dir.exists():
            return []

        workflows = []
        for file in graphs_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
                workflows.append(workflow_data)

        return workflows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreateRequest):
    """创建新的工作流"""
    try:
        from pathlib import Path
        import json
        import uuid

        # 生成唯一 ID
        workflow_id = f"workflow_{int(time.time())}"

        # 构造完整的工作流定义
        workflow_definition = {
            "graph_id": workflow_id,
            "description": request.description,
            "nodes": [node.dict() for node in request.nodes],
            "edges": [edge.dict() for edge in request.edges]
        }

        # 保存到文件
        graphs_dir = Path(__file__).parent.parent.parent / "graphs"
        graphs_dir.mkdir(exist_ok=True)

        file_path = graphs_dir / f"{workflow_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_definition, f, ensure_ascii=False, indent=2)

        return WorkflowResponse(
            success=True,
            message="工作流创建成功",
            workflow_id=workflow_id
        )

    except Exception as e:
        return WorkflowResponse(
            success=False,
            message="工作流创建失败",
            error_details=str(e)
        )


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, request: WorkflowUpdateRequest):
    """更新现有工作流"""
    try:
        from pathlib import Path
        import json

        # 加载现有工作流
        graphs_dir = Path(__file__).parent.parent.parent / "graphs"
        file_path = graphs_dir / f"{workflow_id}.json"

        if not file_path.exists():
            return WorkflowResponse(
                success=False,
                message="工作流不存在",
                workflow_id=workflow_id
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)

        # 更新字段
        if request.description is not None:
            workflow_data["description"] = request.description
        if request.nodes is not None:
            workflow_data["nodes"] = [node.dict() for node in request.nodes]
        if request.edges is not None:
            workflow_data["edges"] = [edge.dict() for edge in request.edges]

        # 保存回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, ensure_ascii=False, indent=2)

        return WorkflowResponse(
            success=True,
            message="工作流更新成功",
            workflow_id=workflow_id
        )

    except Exception as e:
        return WorkflowResponse(
            success=False,
            message="工作流更新失败",
            error_details=str(e)
        )


@router.delete("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def delete_workflow(workflow_id: str):
    """删除工作流"""
    try:
        from pathlib import Path

        graphs_dir = Path(__file__).parent.parent.parent / "graphs"
        file_path = graphs_dir / f"{workflow_id}.json"

        if not file_path.exists():
            return WorkflowResponse(
                success=False,
                message="工作流不存在",
                workflow_id=workflow_id
            )

        # 删除文件
        file_path.unlink()

        return WorkflowResponse(
            success=True,
            message="工作流删除成功",
            workflow_id=workflow_id
        )

    except Exception as e:
        return WorkflowResponse(
            success=False,
            message="工作流删除失败",
            error_details=str(e)
        )


@router.get("/workflows/{workflow_id}", response_model=WorkflowDefinition)
async def get_workflow(workflow_id: str):
    """获取单个工作流详情"""
    try:
        from pathlib import Path
        import json

        graphs_dir = Path(__file__).parent.parent.parent / "graphs"
        file_path = graphs_dir / f"{workflow_id}.json"

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"工作流 {workflow_id} 不存在")

        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)

        return workflow_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=AvailableAgentsResponse)
async def list_available_agents():
    """获取可用的智能体列表"""
    try:
        agents = [
            AgentInfo(
                id="symptom_analyzer",
                name="症状分析器",
                description="分析患者症状，识别主要症状、严重程度、持续时间等",
                type="llm_agent"
            ),
            AgentInfo(
                id="history_analyzer",
                name="病史分析器",
                description="分析患者病史，识别危险因素、既往疾病等",
                type="llm_agent"
            ),
            AgentInfo(
                id="lab_analyzer",
                name="检验分析器",
                description="分析检验结果，识别异常指标和临床意义",
                type="llm_agent"
            ),
            AgentInfo(
                id="imaging_analyzer",
                name="影像分析器",
                description="分析影像描述，识别主要发现和异常",
                type="llm_agent"
            ),
            AgentInfo(
                id="diagnosis_generator",
                name="诊断生成器",
                description="生成最终诊断，包括主要诊断、鉴别诊断和治疗建议",
                type="llm_agent"
            ),
            AgentInfo(
                id="report_generator",
                name="报告生成器",
                description="生成结构化诊断报告",
                type="template_agent"
            )
        ]

        return AvailableAgentsResponse(
            agents=agents,
            total=len(agents)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/execute", response_model=DiagnosisResponse)
async def execute_workflow(request: WorkflowExecuteRequest):
    """执行指定的工作流

    Args:
        request: 包含工作流 ID 和患者数据的请求对象

    Returns:
        诊断报告响应

    Example:
        POST /api/v1/workflow/execute
        {
            "workflow_id": "workflow_1773295457",
            "patient_data": {
                "basic_info": {
                    "name": "张伟",
                    "gender": "male",
                    "age": 45,
                    "department": "呼吸内科"
                },
                "symptoms": "咳嗽、发热...",
                "medical_history": "高血压病史...",
                "images": [...],
                "lab_results": [...]
            }
        }
    """
    try:
        print(f"\n{'=' * 60}")
        print(f"🚀 开始执行工作流：{request.workflow_id}")
        print(f"{'=' * 60}")

        # 1. 加载工作流定义
        from pathlib import Path
        import json

        file_path = Path(__file__).parent.parent.parent / "graphs" / f"{request.workflow_id}.json"
        if not file_path.exists():
            error_msg = f"工作流文件不存在：{file_path}"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)

        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_definition = json.load(f)

        print(
            f"📋 工作流定义：{len(workflow_definition.get('nodes', []))} 个节点，{len(workflow_definition.get('edges', []))} 条边")

        # 检查工作流是否包含必要的节点
        agent_nodes = [n for n in workflow_definition.get('nodes', []) if n.get('type') == 'agent']
        print(f"🤖 智能体节点：{len(agent_nodes)} 个")
        for node in agent_nodes:
            agent_id = node.get('data', {}).get('agentId', 'unknown')
            label = node.get('data', {}).get('label', 'unknown')
            print(f"   - {label} ({agent_id})")

        # 2. 创建医疗图实例（使用工作流定义）
        medical_graph = MedicalGraph(workflow_definition)

        # 3. 执行工作流 - 异步调用
        print(f"\n🚀 开始执行工作流...")
        result_dict = await medical_graph.execute_workflow_async(request.patient_data)
        print(f"✅ 工作流执行完成")

        # 4. 构造符合 Pydantic 模型的诊断报告
        print(f"\n📊 处理诊断结果...")

        # 处理年龄字段为字符串
        age_str = str(request.patient_data["basic_info"]["age"])

        # 🔹 直接使用大模型的原始输出
        final_diagnosis_raw = result_dict.get("final_diagnosis", {})

        if not final_diagnosis_raw:
            print("⚠️ 警告：final_diagnosis 为空，使用默认诊断")
            diagnosis_result = DiagnosisResult(
                primary_diagnosis="诊断流程未完成，请检查工作流配置",
                differential_diagnosis=["需要重新检查"],
                confidence_score=0.0,
                risk_assessment="unknown",
                recommended_actions=["建议完善相关检查后重新提交"],
                reasoning="诊断流程未正常完成，无法提供诊断依据"
            )
        else:
            print(f"\n🔍 [DEBUG] 使用大模型原始输出")
            print(f"   字段：{list(final_diagnosis_raw.keys())}")

            # 从大模型原始 JSON 中提取字段
            preliminary_diagnosis = final_diagnosis_raw.get("preliminary_diagnosis", {})
            risk_assessment_raw = final_diagnosis_raw.get("risk_assessment", {})

            # 处理 risk_assessment
            if isinstance(risk_assessment_raw, dict):
                level = risk_assessment_raw.get("level", "unknown")
                description = risk_assessment_raw.get("description", "")
                risk_assessment_str = f"{level}: {description}" if description else level
            elif isinstance(risk_assessment_raw, str):
                risk_assessment_str = risk_assessment_raw
            else:
                risk_assessment_str = "unknown"

            # 构造 DiagnosisResult
            # 构造 DiagnosisResult
            diagnosis_result = DiagnosisResult(
                primary_diagnosis=preliminary_diagnosis.get("primary_diagnosis", "待诊断"),
                differential_diagnosis=preliminary_diagnosis.get("differential_diagnosis", []),
                confidence_score=float(preliminary_diagnosis.get("confidence_score", 0.85)),
                risk_assessment=risk_assessment_str,
                recommended_actions=final_diagnosis_raw.get("recommended_actions", ["需要进一步检查"]),
            )

            print(f"✅ 诊断结果构造完成")
            print(f"   主要诊断：{diagnosis_result.primary_diagnosis}")

        # 构造患者摘要
        patient_summary = {
            "name": request.patient_data["basic_info"]["name"],
            "age": age_str,
            "gender": request.patient_data["basic_info"]["gender"],
            "chief_complaint": request.patient_data["symptoms"][:50] + "..." if len(
                request.patient_data["symptoms"]) > 50 else request.patient_data["symptoms"]
        }

        # 🔹 直接从大模型原始 JSON 中提取治疗计划
        print(f"\n🔍 [DEBUG] 构造报告")

        if final_diagnosis_raw:
            # ✅ 从大模型原始 JSON 中提取字段，构造成 Pydantic 模型需要的格式
            medical_report_data = {
                "report_id": f"REP_{int(time.time())}",
                "generated_time": time.strftime("%Y-%m-%d %H:%M:%S"),

                # 🔹 使用 patient_summary（旧格式，但兼容前端）
                "patient_summary": {
                    "name": request.patient_data["basic_info"]["name"],
                    "age": age_str,
                    "gender": request.patient_data["basic_info"]["gender"],
                    "chief_complaint": (
                        final_diagnosis_raw.get("chief_complaint", "")[:50] + "..."
                        if len(final_diagnosis_raw.get("chief_complaint", "")) > 50
                        else final_diagnosis_raw.get("chief_complaint", request.patient_data["symptoms"])
                    )
                },

                # 🔹 临床发现
                "clinical_findings": {
                    "symptom_analysis": result_dict.get("symptom_analysis"),
                    "history_analysis": result_dict.get("history_analysis"),
                    "lab_analysis": result_dict.get("lab_analysis"),
                    "imaging_analysis": result_dict.get("imaging_analysis")
                },

                # 🔹 诊断结果（使用 DiagnosisResult 模型）
                "diagnosis": {
                    "primary_diagnosis": final_diagnosis_raw.get("primary_diagnosis", "待诊断"),
                    "differential_diagnosis": final_diagnosis_raw.get("differential_diagnosis", []),
                    "confidence_score": final_diagnosis_raw.get("confidence_score", 0.85),
                    "risk_assessment": (
                        final_diagnosis_raw.get("risk_assessment", {}).get("description", "")
                        if isinstance(final_diagnosis_raw.get("risk_assessment"), dict)
                        else str(final_diagnosis_raw.get("risk_assessment", "unknown"))
                    ),
                    "recommended_actions": final_diagnosis_raw.get("recommended_actions", ["需要进一步检查"]),
                    "reasoning": final_diagnosis_raw.get("reasoning", "诊断依据待补充")
                },

                # 🔹 治疗计划（转换为列表格式）
                "treatment_plan": [],

                # 🔹 随访计划
                "follow_up": {
                    "plan": final_diagnosis_raw.get("follow_up_plan", {}).get("follow_up_time", "根据病情制定"),
                    "frequency": "按医嘱执行"
                },

                # 🔹 患者教育
                "patient_education": [
                    "请遵医嘱按时服药",
                    "注意休息，避免剧烈运动",
                    "定期复查相关指标",
                    "如有不适及时就医"
                ]
            }

            # 🔹 从原始 JSON 中提取治疗计划并转换格式
            treatment_recommendations = result_dict.get("treatment_recommendations", [])
            if treatment_recommendations:
                for rec in treatment_recommendations:
                    medical_report_data["treatment_plan"].append(rec)

            print(f"✅ 构造符合 Pydantic 模型的报告")
            print(f"   主要诊断：{medical_report_data['diagnosis']['primary_diagnosis']}")
            print(f"   治疗计划：{len(medical_report_data['treatment_plan'])} 项")

            print(f"✅ 构造符合 Pydantic 模型的报告")
            print(f"   主要诊断：{medical_report_data['diagnosis']['primary_diagnosis']}")
            print(f"   治疗计划：{len(medical_report_data['treatment_plan'])} 项")
        else:
            # 容错：使用默认值
            print("⚠️ 警告：final_diagnosis 为空，使用默认报告")
            medical_report_data = {
                "report_id": f"REP_{int(time.time())}",
                "generated_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "patient_summary": {
                    "name": request.patient_data["basic_info"]["name"],
                    "age": age_str,
                    "gender": request.patient_data["basic_info"]["gender"],
                    "chief_complaint": ""
                },
                "clinical_findings": {
                    "symptom_analysis": result_dict.get("symptom_analysis"),
                    "history_analysis": result_dict.get("history_analysis"),
                    "lab_analysis": result_dict.get("lab_analysis"),
                    "imaging_analysis": result_dict.get("imaging_analysis")
                },
                "diagnosis": {
                    "primary_diagnosis": "诊断流程未完成",
                    "differential_diagnosis": ["需要重新检查"],
                    "confidence_score": 0.0,
                    "risk_assessment": "unknown",
                    "recommended_actions": ["建议完善检查"],
                    "reasoning": "诊断流程未正常完成"
                },
                "treatment_plan": [],
                "follow_up": {
                    "plan": "待定",
                    "frequency": "按医嘱执行"
                },
                "patient_education": [
                    "请遵医嘱按时服药",
                    "注意休息",
                    "定期复查",
                    "如有不适及时就医"
                ]
            }

        # 5. 创建完整的医疗报告（使用 Pydantic 模型）
        medical_report = MedicalReport(**medical_report_data)

        # 6. 返回完整结果
        print(f"\n✅ 构造响应成功")
        print(f"{'=' * 60}\n")

        return DiagnosisResponse(
            success=True,
            message="工作流执行完成",
            report=medical_report
        )

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        print(f"\n❌ 工作流执行失败：{e}")
        import traceback
        traceback.print_exc()
        print(f"{'=' * 60}\n")
        return DiagnosisResponse(
            success=False,
            message="工作流执行失败",
            error_details=str(e)
        )

