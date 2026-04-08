"""基础智能体类 - 优化版"""
import json
import os
import re
from abc import ABC, abstractmethod
from openai import OpenAI
from config.settings import settings


class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        # 使用配置管理器获取 Qwen 配置
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = settings.MODEL_NAME

        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")

    def call_qwen(self, system_prompt: str, user_input: str) -> dict:
        """调用 Qwen 大模型 - 增强版 JSON 解析"""
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            print(f"\n📤 [{self.agent_name}] 发送请求到 {self.model}...")

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )

            # 解析响应
            content = response.choices[0].message.content
            print(f"\n📝 [{self.agent_name}] LLM 原始回复:\n{'='*60}")
            print(content[:800] if len(content) > 800 else content)
            print(f"{'='*60}")

            # 方法 1：直接解析
            try:
                result = json.loads(content)
                print(f"✅ [{self.agent_name}] JSON 解析成功，字段：{list(result.keys())}")
                return result
            except json.JSONDecodeError as e:
                print(f"⚠️ [{self.agent_name}] JSON 解析失败：{e}")
                print(f"尝试从文本中提取 JSON 内容...")

            # 方法 2：移除 Markdown 代码块标记
            cleaned_content = re.sub(r'json\s*', '', content)
            cleaned_content = re.sub(r'\s*$', '', cleaned_content)
            cleaned_content = cleaned_content.strip()

            try:
                result = json.loads(cleaned_content)
                print(f"✅ [{self.agent_name}] 移除 Markdown 标记后解析成功")
                return result
            except:
                pass

            # 方法 3：提取第一个完整的 JSON 对象（支持嵌套）
            json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    extracted_json = json_match.group()
                    print(f"提取到的 JSON 片段:\n{extracted_json[:300]}")
                    result = json.loads(extracted_json)
                    print(f"✅ [{self.agent_name}] 从文本中提取 JSON 成功")
                    return result
                except Exception as extract_error:
                    print(f"提取后仍然解析失败：{extract_error}")

            # 方法 4：尝试提取多个可能的 JSON 片段
            json_patterns = [
                r'\{[^{}]*\}',  # 简单对象
                r'\{(?:[^{}]|\{[^{}]*\})*\}',  # 一层嵌套
                r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'  # 两层嵌套
            ]

            for pattern in json_patterns:
                matches = re.finditer(pattern, cleaned_content, re.DOTALL)
                for match in matches:
                    try:
                        candidate = match.group()
                        result = json.loads(candidate)
                        print(f"✅ [{self.agent_name}] 使用模式 {pattern[:30]}... 提取成功")
                        return result
                    except:
                        continue

            # 如果所有方法都失败，返回包装后的结果
            print(f"❌ 所有 JSON 解析方法均失败，返回原始响应")
            return {"raw_response": content, "parse_error": "JSON 解析失败"}

        except Exception as e:
            print(f"❌ [{self.agent_name}] Qwen 调用错误：{e}")
            return {"error": str(e)}

    @abstractmethod
    def prepare_input(self, state) -> str:
            """准备输入给大模型的提示词"""
            pass

    @abstractmethod
    def process_output(self, output: dict) -> dict:
            """处理大模型输出"""
            pass

    def execute(self, state) -> dict:
            """执行智能体"""
            print(f"🤖 {self.agent_name} 正在分析...")

            # 准备输入
            user_input = self.prepare_input(state)

            # 调用 Qwen
            llm_output = self.call_qwen(self.get_system_prompt(), user_input)

            # 处理输出
            processed_output = self.process_output(llm_output)

            print(f"✅ {self.agent_name} 分析完成")
            return processed_output

    def get_system_prompt(self) -> str:
            """获取系统提示词"""
            return settings.SYSTEM_PROMPTS.get(self.agent_name, "你是一个医疗助手。")
