"""
基础智能体模块
包含所有Agent的基础实现和通用功能
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from src.configs.config import Config, AgentConfig


@dataclass
class AgentResult:
    """Agent执行结果数据类"""
    agent_name: str
    task_description: str
    result: str
    success: bool
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class BaseAgent:
    """基础Agent类"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        """
        初始化基础Agent
        
        Args:
            name: Agent名称
            role: Agent角色
            goal: Agent目标
            backstory: Agent背景故事
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        # 创建CrewAI Agent
        self.agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        logger.info(f"Agent '{self.name}' 初始化成功")
    
    def execute_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        执行任务
        
        Args:
            task_description: 任务描述
            context: 上下文信息
            
        Returns:
            Agent执行结果
        """
        try:
            logger.info(f"Agent '{self.name}' 开始执行任务: {task_description}")
            
            # 创建任务
            task = Task(
                description=task_description,
                agent=self.agent,
                expected_output="详细的任务执行结果"
            )
            
            # 创建Crew并执行
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            # 执行任务
            result = crew.kickoff()
            
            logger.info(f"Agent '{self.name}' 任务执行成功")
            return AgentResult(
                agent_name=self.name,
                task_description=task_description,
                result=str(result),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Agent '{self.name}' 任务执行失败: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                task_description=task_description,
                result="",
                success=False,
                error_message=str(e)
            )


class QueryClassifierAgent(BaseAgent):
    """查询意图分类Agent"""
    
    def __init__(self):
        super().__init__(
            name="QueryClassifierAgent",
            role=AgentConfig.QUERY_CLASSIFIER_ROLE,
            goal=AgentConfig.QUERY_CLASSIFIER_GOAL,
            backstory=AgentConfig.QUERY_CLASSIFIER_BACKSTORY
        )
    
    def classify_query(self, query: str) -> str:
        """
        分类用户查询
        
        Args:
            query: 用户查询字符串
            
        Returns:
            分类结果 (comparison, deep_dive, survey, tutorial)
        """
        classification_prompt = f"""
        你是一个AI助手，负责将用户的技术查询分类到以下四种类型之一：

        1. comparison: 当用户明确要求比较两个或多个事物时。
        2. deep_dive: 当用户要求深入解释单个概念、技术或项目时。
        3. survey: 当用户要求盘点或调研某个领域的主要参与者或技术时。
        4. tutorial: 当用户询问如何完成某项具体的技术任务时。

        请只输出最终的分类标签，不要有任何其他解释。

        用户查询: "{query}"

        分类标签:
        """
        
        result = self.execute_task(classification_prompt)
        if result.success:
            # 提取分类结果
            classification = result.result.strip().lower()
            if classification in ['comparison', 'deep_dive', 'survey', 'tutorial']:
                return classification
            else:
                logger.warning(f"未知分类结果: {classification}，使用默认分类: deep_dive")
                return 'deep_dive'
        else:
            logger.error(f"查询分类失败: {result.error_message}")
            return 'deep_dive'  # 默认分类


class ChiefPlannerAgent(BaseAgent):
    """首席规划Agent"""
    
    def __init__(self):
        super().__init__(
            name="ChiefPlannerAgent",
            role=AgentConfig.CHIEF_PLANNER_ROLE,
            goal=AgentConfig.CHIEF_PLANNER_GOAL,
            backstory=AgentConfig.CHIEF_PLANNER_BACKSTORY
        )
    
    def create_research_plan(self, query: str, intent: str) -> Dict[str, Any]:
        """
        创建研究计划
        
        Args:
            query: 用户查询
            intent: 查询意图
            
        Returns:
            研究计划字典
        """
        planning_prompt = f"""
        基于以下信息，制定一个详细的研究计划：

        用户查询: {query}
        查询意图: {intent}

        请提供以下内容：
        1. 研究目标
        2. 关键搜索词列表
        3. 需要关注的技术方面
        4. 预期输出结构
        5. 研究优先级

        请以结构化的方式组织你的回答。
        """
        
        result = self.execute_task(planning_prompt)
        if result.success:
            return {
                'plan': result.result,
                'query': query,
                'intent': intent,
                'success': True
            }
        else:
            return {
                'plan': '',
                'query': query,
                'intent': intent,
                'success': False,
                'error': result.error_message
            }


class WebResearcherAgent(BaseAgent):
    """网络研究员Agent"""
    
    def __init__(self):
        super().__init__(
            name="WebResearcherAgent",
            role=AgentConfig.WEB_RESEARCHER_ROLE,
            goal=AgentConfig.WEB_RESEARCHER_GOAL,
            backstory=AgentConfig.WEB_RESEARCHER_BACKSTORY
        )
    
    def research_topic(self, research_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行研究任务
        
        Args:
            research_plan: 研究计划
            
        Returns:
            研究结果
        """
        research_prompt = f"""
        基于以下研究计划，执行网络研究：

        研究计划: {research_plan.get('plan', '')}
        查询: {research_plan.get('query', '')}
        意图: {research_plan.get('intent', '')}

        请提供：
        1. 找到的关键信息
        2. 信息来源
        3. 重要发现
        4. 需要进一步研究的方向

        请确保信息的准确性和相关性。
        """
        
        result = self.execute_task(research_prompt)
        return {
            'research_data': result.result if result.success else '',
            'success': result.success,
            'error': result.error_message if not result.success else None
        }


class CriticAnalystAgent(BaseAgent):
    """批判性分析师Agent"""
    
    def __init__(self):
        super().__init__(
            name="CriticAnalystAgent",
            role=AgentConfig.CRITIC_ANALYST_ROLE,
            goal=AgentConfig.CRITIC_ANALYST_GOAL,
            backstory=AgentConfig.CRITIC_ANALYST_BACKSTORY
        )
    
    def critique_research(self, research_data: str, original_query: str) -> Dict[str, Any]:
        """
        批判性分析研究结果
        
        Args:
            research_data: 研究数据
            original_query: 原始查询
            
        Returns:
            批判分析结果
        """
        critique_prompt = f"""
        请对以下研究结果进行批判性分析：

        原始查询: {original_query}
        研究数据: {research_data}

        请评估：
        1. 信息的完整性和准确性
        2. 是否存在矛盾或遗漏
        3. 是否偏离了原始查询
        4. 需要补充的信息
        5. 整体质量评分 (1-10分)

        如果信息不充分，请提供具体的补充建议。
        如果信息已足够，请确认可以进入报告撰写阶段。
        """
        
        result = self.execute_task(critique_prompt)
        if result.success:
            # 简单判断是否需要继续研究
            critique_text = result.result.lower()
            needs_more_research = any(keyword in critique_text for keyword in [
                '不充分', '不完整', '需要补充', '遗漏', 'insufficient', 'incomplete', 'need more'
            ])
            
            return {
                'critique': result.result,
                'needs_more_research': needs_more_research,
                'success': True
            }
        else:
            return {
                'critique': '',
                'needs_more_research': True,  # 出错时默认需要更多研究
                'success': False,
                'error': result.error_message
            }


class ReportWriterAgent(BaseAgent):
    """报告撰写Agent"""
    
    def __init__(self):
        super().__init__(
            name="ReportWriterAgent",
            role=AgentConfig.REPORT_WRITER_ROLE,
            goal=AgentConfig.REPORT_WRITER_GOAL,
            backstory=AgentConfig.REPORT_WRITER_BACKSTORY
        )
    
    def write_report(self, research_data: str, intent: str, query: str) -> str:
        """
        撰写最终报告
        
        Args:
            research_data: 研究数据
            intent: 查询意图
            query: 原始查询
            
        Returns:
            生成的报告
        """
        from src.configs.templates import template_processor
        
        # 使用模板处理器生成报告
        report_data = {
            'title': f"{query} - 技术调研报告",
            'summary': f"本报告针对'{query}'进行了深入的技术调研和分析。",
            'research_data': research_data,
            'query': query,
            'intent': intent
        }
        
        # 根据意图处理模板
        try:
            report_content = template_processor.process_template(intent, report_data)
            
            # 使用Agent进一步优化报告内容
            optimization_prompt = f"""
            请基于以下研究数据，优化和完善这份技术报告：

            原始查询: {query}
            查询意图: {intent}
            研究数据: {research_data}

            请确保报告：
            1. 内容详实、逻辑清晰
            2. 使用专业的技术术语
            3. 提供具体的例子和代码
            4. 确保信息的准确性
            5. 保持Markdown格式
            6. 结构完整，各部分内容充实

            请直接输出优化后的完整报告内容：
            """
            
            result = self.execute_task(optimization_prompt)
            if result.success:
                return result.result
            else:
                # 如果Agent优化失败，返回模板处理的结果
                return report_content
                
        except Exception as e:
            logger.error(f"模板处理失败: {str(e)}")
            # 回退到简单的报告生成
            simple_prompt = f"""
            基于以下研究数据，撰写一份专业的技术调研报告：

            原始查询: {query}
            查询意图: {intent}
            研究数据: {research_data}

            请生成一份结构清晰、内容详实的Markdown格式报告。
            """
            
            result = self.execute_task(simple_prompt)
            if result.success:
                return result.result
            else:
                return f"报告生成失败: {result.error_message}"
