"""
DeepDive Analyst 项目配置文件
包含所有Agent配置、模型配置、API配置等
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """项目配置类"""
    
    # API 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    
    # LLM 提供商配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    
    # LLM 基础URL配置（用于自定义部署）
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
    
    # LangSmith 配置
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "deepdive-analyst")
    
    # 搜索配置
    MAX_SEARCH_RESULTS: int = 10
    SEARCH_TIMEOUT: int = 30
    
    # 报告配置
    DEFAULT_OUTPUT_FILE: str = "report.md"
    MAX_REPORT_LENGTH: int = 10000
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """
        获取LLM配置字典
        
        Returns:
            LLM配置字典
        """
        # 根据提供商获取对应的API密钥
        api_key_map = {
            'openai': cls.OPENAI_API_KEY,
            'gemini': cls.GEMINI_API_KEY,
            'qwen': cls.QWEN_API_KEY,
            'anthropic': cls.ANTHROPIC_API_KEY
        }
        
        api_key = api_key_map.get(cls.LLM_PROVIDER.lower(), "")
        
        config = {
            'provider': cls.LLM_PROVIDER.lower(),
            'model': cls.LLM_MODEL,
            'temperature': cls.LLM_TEMPERATURE,
            'max_tokens': cls.LLM_MAX_TOKENS,
            'api_key': api_key,
            'timeout': cls.LLM_TIMEOUT,
            'max_retries': cls.LLM_MAX_RETRIES
        }
        
        # 如果设置了基础URL，添加到配置中
        if cls.LLM_BASE_URL:
            config['base_url'] = cls.LLM_BASE_URL
        
        return config
    
    @classmethod
    def validate_llm_config(cls) -> bool:
        """
        验证LLM配置是否完整
        
        Returns:
            配置是否有效
        """
        config = cls.get_llm_config()
        
        # 检查必需字段
        required_fields = ['provider', 'model', 'api_key']
        for field in required_fields:
            if not config.get(field):
                return False
        
        # 检查提供商是否支持
        from src.llm.llm_factory import LLMFactory
        if config['provider'] not in LLMFactory.get_supported_providers():
            return False
        
        return True


class AgentConfig:
    """Agent配置类"""
    
    # Query Classifier Agent 配置
    QUERY_CLASSIFIER_ROLE: str = "查询意图分类专家"
    QUERY_CLASSIFIER_GOAL: str = "准确识别用户查询的意图类型，为后续处理提供正确的分类标签"
    QUERY_CLASSIFIER_BACKSTORY: str = """
    你是一位经验丰富的技术咨询专家，擅长快速理解用户的技术问题意图。
    你能够准确地将复杂的技术查询分类为不同的类型，包括对比分析、深度解析、
    技术巡览和实践指南等。你的分类能力为整个调研团队提供了正确的方向指引。
    """
    
    # Chief Planner Agent 配置
    CHIEF_PLANNER_ROLE: str = "首席调研规划师"
    CHIEF_PLANNER_GOAL: str = "制定详细的研究计划，将复杂问题分解为可执行的研究任务"
    CHIEF_PLANNER_BACKSTORY: str = """
    你是一位资深的项目管理和技术调研专家，拥有丰富的复杂项目规划经验。
    你擅长将抽象的技术问题转化为具体的、可执行的研究计划，确保调研工作
    的系统性和完整性。你的规划能力是整个调研团队成功的关键。
    """
    
    # Web Researcher Agent 配置
    WEB_RESEARCHER_ROLE: str = "网络信息研究员"
    WEB_RESEARCHER_GOAL: str = "通过网络搜索收集准确、全面的技术信息"
    WEB_RESEARCHER_BACKSTORY: str = """
    你是一位专业的技术信息研究员，精通各种网络搜索和信息收集技巧。
    你能够快速找到最相关、最权威的技术资料，并从中提取关键信息。
    你的信息收集能力为整个调研团队提供了坚实的数据基础。
    """
    
    # Critic Analyst Agent 配置
    CRITIC_ANALYST_ROLE: str = "批判性分析师"
    CRITIC_ANALYST_GOAL: str = "审查研究结果的质量和完整性，提出改进建议"
    CRITIC_ANALYST_BACKSTORY: str = """
    你是一位严谨的技术分析师，拥有敏锐的批判性思维和深厚的技术背景。
    你能够识别研究中的不足和矛盾，提出建设性的改进建议。
    你的批判能力确保了调研结果的质量和可靠性。
    """
    
    # Report Writer Agent 配置
    REPORT_WRITER_ROLE: str = "技术报告撰写师"
    REPORT_WRITER_GOAL: str = "将研究结果整合为结构清晰、内容详实的技术报告"
    REPORT_WRITER_BACKSTORY: str = """
    你是一位资深的技术文档专家，擅长将复杂的技术信息转化为清晰易懂的报告。
    你能够根据不同的问题类型选择合适的报告结构，确保内容的逻辑性和可读性。
    你的写作能力让复杂的技术调研结果变得易于理解和应用。
    """


# 查询意图分类的Prompt模板
QUERY_CLASSIFICATION_PROMPT = """
你是一个AI助手，负责将用户的技术查询分类到以下四种类型之一：

1. comparison: 当用户明确要求比较两个或多个事物时。
2. deep_dive: 当用户要求深入解释单个概念、技术或项目时。
3. survey: 当用户要求盘点或调研某个领域的主要参与者或技术时。
4. tutorial: 当用户询问如何完成某项具体的技术任务时。

请只输出最终的分类标签，不要有任何其他解释。

用户查询: "{query}"

分类标签:
"""


# 报告模板配置
REPORT_TEMPLATES: Dict[str, str] = {
    "comparison": """
# {title}

## 摘要 (TL;DR)
{summary}

## 核心特性对比
{feature_comparison}

## 优缺点分析
{pros_cons}

## 最佳应用场景
{use_cases}

## 代码示例
{code_examples}

## 参考来源
{sources}
""",
    
    "deep_dive": """
# {title}

## 摘要 (TL;DR)
{summary}

## 核心概念与背景
{core_concepts}

## 关键工作机制/架构详解
{key_mechanisms}

## 代码实现/伪代码示例
{code_implementation}

## 应用与影响
{applications}

## 参考来源
{sources}
""",
    
    "survey": """
# {title}

## 摘要 (TL;DR)
{summary}

## 主要参与者/项目列表
{key_players}

## 分类与归纳
{categorization}

## 关键特性对比
{feature_comparison}

## 未来趋势展望
{future_trends}

## 参考来源
{sources}
""",
    
    "tutorial": """
# {title}

## 摘要 (TL;DR)
{summary}

## 前置准备与环境要求
{prerequisites}

## 分步操作指南
{step_by_step}

## 常见问题与解决方案
{troubleshooting}

## 代码/脚本示例
{code_examples}

## 参考来源
{sources}
"""
}
