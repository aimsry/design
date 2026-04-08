import { NodeConfig } from '../types/workflow';

/**
 * 检查工作流中是否包含特定类型的智能体
 */
export const hasAgentType = (nodes: NodeConfig[] | undefined, agentType: string): boolean => {
  if (!nodes) return false;

  return nodes.some(node =>
    node.type === 'agent' &&
    (node.data?.agentType === agentType || node.data?.agentId === agentType)
  );
};

/**
 * 检查工作流是否需要影像学检查
 */
export const needsImaging = (nodes: NodeConfig[] | undefined): boolean => {
  return hasAgentType(nodes, 'imaging_analyzer');
};

/**
 * 检查工作流是否需要实验室检验
 */
export const needsLabTests = (nodes: NodeConfig[] | undefined): boolean => {
  return hasAgentType(nodes, 'lab_analyzer');
};

/**
 * 获取工作流所需的所有检查类型
 */
export interface WorkflowRequirements {
  needsImaging: boolean;
  needsLabTests: boolean;
  requiredFields: string[];
}

export const analyzeWorkflowRequirements = (nodes: NodeConfig[] | undefined): WorkflowRequirements => {
  const imaging = needsImaging(nodes);
  const labTests = needsLabTests(nodes);

  const requiredFields: string[] = [];
  if (imaging) requiredFields.push('images');
  if (labTests) requiredFields.push('lab_results');

  return {
    needsImaging: imaging,
    needsLabTests: labTests,
    requiredFields
  };
};
