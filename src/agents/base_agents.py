"""
基础智能体模块
包含所有Agent的基础实现和通用功能
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from src.configs.config import Config, AgentConfig
from src.llm.llm_factory import LLMFactory
from src.agents.scoring_manager import DynamicScoringManager
import json
import re
import ast


class TaskResult(BaseModel):
    """任务执行结果的Pydantic模型"""
    result: str = Field(description="任务执行结果")
    success: bool = Field(description="任务是否成功")


class CritiqueResult(BaseModel):
    """批判性分析结果的Pydantic模型"""
    critique: str = Field(description="详细的批判性分析内容")
    completeness_score: int = Field(ge=1, le=10, description="信息完整性评分 (1-10分)")
    accuracy_score: int = Field(ge=1, le=10, description="信息准确性评分 (1-10分)")
    needs_more_research: bool = Field(description="是否需要更多研究")
    missing_information: List[str] = Field(default=[], description="缺失的信息列表")
    recommendations: List[str] = Field(default=[], description="改进建议列表")


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
        try:
            llm_config = Config.get_llm_config()
            self.llm_instance = LLMFactory.create_llm(**llm_config)
            
            # 为了兼容CrewAI，我们需要创建一个LangChain兼容的LLM对象
            self.llm = self._create_crewai_compatible_llm()
            
            logger.info(f"Agent '{self.name}' LLM初始化成功: {self.llm_instance}")
        except Exception as e:
            logger.error(f"Agent '{self.name}' LLM初始化失败: {str(e)}")
            raise
        
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
    
    def _create_crewai_compatible_llm(self):
        """
        创建与CrewAI兼容的LLM对象
        
        Returns:
            CrewAI兼容的LLM对象
        """
        llm_config = Config.get_llm_config()
        provider = llm_config['provider']
        
        if provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=llm_config['model'],
                temperature=llm_config['temperature'],
                api_key=llm_config['api_key'],
                max_tokens=llm_config.get('max_tokens'),
                timeout=llm_config.get('timeout'),
                max_retries=llm_config.get('max_retries')
            )
        elif provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=llm_config['model'],
                temperature=llm_config['temperature'],
                api_key=llm_config['api_key'],
                max_tokens=llm_config.get('max_tokens'),
                timeout=llm_config.get('timeout')
            )
        elif provider == 'gemini':
            # Gemini需要特殊处理，使用CrewAI的LLM类而不是LangChain
            from crewai import LLM
            
            # 保持完整的模型名称格式
            model_name = llm_config['model']
            if not model_name.startswith('gemini/'):
                model_name = f"gemini/{model_name}"
            
            logger.info(f"Gemini初始化，模型: {model_name}")
            return LLM(
                model=model_name,
                api_key=llm_config['api_key'],
                temperature=llm_config['temperature'],
                max_tokens=llm_config.get('max_tokens')
            )
        elif provider == 'qwen':
            # Qwen需要自定义适配器
            return self._create_qwen_adapter(llm_config)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
    
    def _create_qwen_adapter(self, llm_config):
        """
        创建Qwen适配器
        
        Args:
            llm_config: LLM配置
            
        Returns:
            Qwen适配器对象
        """
        # 这里需要创建一个自定义的适配器来兼容CrewAI
        # 由于CrewAI可能不直接支持Qwen，我们需要创建一个包装器
        class QwenAdapter:
            def __init__(self, config):
                self.config = config
                self.llm_instance = LLMFactory.create_llm(**config)
            
            def invoke(self, messages, **kwargs):
                # 将CrewAI的消息格式转换为我们的格式
                if isinstance(messages, list):
                    prompt = "\n".join([msg.content for msg in messages if hasattr(msg, 'content')])
                else:
                    prompt = str(messages)
                
                response = self.llm_instance.generate(prompt)
                if response.success:
                    # 创建一个类似LangChain响应的对象
                    class MockResponse:
                        def __init__(self, content):
                            self.content = content
                            self.usage_metadata = response.usage
                            self.finish_reason = response.finish_reason
                    
                    return MockResponse(response.content)
                else:
                    raise Exception(f"Qwen生成失败: {response.error_message}")
            
            def stream(self, messages, **kwargs):
                # 流式生成适配
                if isinstance(messages, list):
                    prompt = "\n".join([msg.content for msg in messages if hasattr(msg, 'content')])
                else:
                    prompt = str(messages)
                
                for chunk in self.llm_instance.generate_stream(prompt):
                    if chunk.success:
                        class MockChunk:
                            def __init__(self, content):
                                self.content = content
                        yield MockChunk(chunk.content)
                    else:
                        raise Exception(f"Qwen流式生成失败: {chunk.error_message}")
        
        return QwenAdapter(llm_config)
    
    def execute_task(self, task_description: str, context: Optional[Dict[str, Any]] = None, 
                     use_json_output: bool = False, output_model: Optional[BaseModel] = None) -> AgentResult:
        """
        执行任务
        
        Args:
            task_description: 任务描述
            context: 上下文信息
            use_json_output: 是否使用JSON输出格式
            output_model: Pydantic模型类（当use_json_output=True时使用）
            
        Returns:
            Agent执行结果
        """
        try:
            logger.info(f"Agent '{self.name}' 开始执行任务: {task_description}")
            
            # 创建任务
            task_kwargs = {
                'description': task_description,
                'agent': self.agent,
                'expected_output': "详细的任务执行结果"
            }
            
            # 如果需要JSON输出，添加output_json属性
            if use_json_output:
                if output_model:
                    task_kwargs['output_json'] = output_model
                else:
                    # 默认使用TaskResult模型
                    task_kwargs['output_json'] = TaskResult
            
            task = Task(**task_kwargs)
            
            # 创建Crew并执行
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            # 执行任务
            result = crew.kickoff()
            
            # 如果任务要求JSON输出，但返回的不是纯JSON字符串，尽量序列化为JSON字符串
            if use_json_output and not isinstance(result, str):
                try:
                    result = json.dumps(result)
                except Exception:
                    result = str(result)
            
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
    
    def __init__(self, search_tools=None):
        super().__init__(
            name="WebResearcherAgent",
            role=AgentConfig.WEB_RESEARCHER_ROLE,
            goal=AgentConfig.WEB_RESEARCHER_GOAL,
            backstory=AgentConfig.WEB_RESEARCHER_BACKSTORY
        )
        # 初始化搜索工具
        if search_tools is None:
            from src.tools.search_tools import SearchToolsManager
            try:
                self.search_tools = SearchToolsManager()
                logger.info("WebResearcherAgent 搜索工具初始化成功")
            except Exception as e:
                logger.warning(f"WebResearcherAgent 搜索工具初始化失败: {e}")
                self.search_tools = None
        else:
            self.search_tools = search_tools
    
    def research_topic(self, research_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行研究任务
        
        Args:
            research_plan: 研究计划
            
        Returns:
            研究结果
        """
        try:
            # 首先使用搜索工具收集信息
            search_results = []
            if self.search_tools:
                queries = research_plan.get('research_queries', [])
                if not queries:
                    # 如果没有提供查询，从研究计划中提取
                    queries = [research_plan.get('query', '')]
                
                logger.info(f"开始执行网络搜索，查询数量: {len(queries)}")
                
                for query in queries[:5]:  # 限制查询数量
                    if query.strip():
                        try:
                            results = self.search_tools.comprehensive_search(
                                query=query,
                                max_results=5,
                                scrape_content=True
                            )
                            search_results.extend(results)
                            logger.info(f"查询 '{query}' 找到 {len(results)} 个结果")
                        except Exception as e:
                            logger.warning(f"搜索查询 '{query}' 失败: {e}")
                            continue
            
            # 构建包含搜索结果的提示
            search_context = ""
            if search_results:
                search_context = "\n\n**网络搜索结果:**\n"
                for i, result in enumerate(search_results[:10], 1):  # 限制结果数量
                    search_context += f"{i}. **{result.get('title', '无标题')}**\n"
                    search_context += f"   链接: {result.get('url', '无链接')}\n"
                    search_context += f"   内容: {result.get('content', '无内容')[:200]}...\n\n"
            else:
                search_context = "\n\n**注意**: 未能获取到网络搜索结果，将基于现有知识进行分析。\n"
            
            # 检测查询语言
            query_language = self._detect_query_language(research_plan.get('query', ''))
            
            research_prompt = f"""
            基于以下研究计划和网络搜索结果，执行深入分析：

            **研究计划:**
            {research_plan.get('plan', '')}
            
            **原始查询:**
            {research_plan.get('query', '')}
            
            **查询意图:**
            {research_plan.get('intent', '')}
            {search_context}
            
            **重要：请严格按照以下要求进行分析：**
            1. **语言要求**: 分析结果必须使用与原始查询相同的语言。原始查询是{query_language}，因此分析结果必须完全使用{query_language}撰写。
            2. 关键发现和重要信息
            3. 信息来源和可信度评估
            4. 技术细节和实现方式
            5. 优缺点分析
            6. 需要进一步研究的方向
            7. 相关案例和应用场景

            请确保信息的准确性、完整性和相关性，并使用{query_language}撰写分析结果。
            """
            
            result = self.execute_task(research_prompt)
            return {
                'research_data': result.result if result.success else '',
                'search_results': search_results,
                'success': result.success,
                'error': result.error_message if not result.success else None
            }
            
        except Exception as e:
            logger.error(f"研究任务执行失败: {e}")
            return {
                'research_data': '',
                'search_results': [],
                'success': False,
                'error': str(e)
            }


class CriticAnalystAgent(BaseAgent):
    """批判性分析师Agent"""
    
    def __init__(self, search_tools=None):
        super().__init__(
            name="CriticAnalystAgent",
            role=AgentConfig.CRITIC_ANALYST_ROLE,
            goal=AgentConfig.CRITIC_ANALYST_GOAL,
            backstory=AgentConfig.CRITIC_ANALYST_BACKSTORY
        )
        # 初始化搜索工具（用于验证和补充信息）
        if search_tools is None:
            from src.tools.search_tools import SearchToolsManager
            try:
                self.search_tools = SearchToolsManager()
                logger.info("CriticAnalystAgent 搜索工具初始化成功")
            except Exception as e:
                logger.warning(f"CriticAnalystAgent 搜索工具初始化失败: {e}")
                self.search_tools = None
        else:
            self.search_tools = search_tools
        
        # 初始化动态评分管理器
        self.scoring_manager = DynamicScoringManager()
        logger.info("CriticAnalystAgent 动态评分管理器初始化成功")
    
    def critique_research(self, research_data: str, original_query: str, iteration: int = 1) -> Dict[str, Any]:
        """
        批判性分析研究结果（支持动态评分）
        
        Args:
            research_data: 研究数据
            original_query: 原始查询
            iteration: 当前迭代次数
            
        Returns:
            批判分析结果
        """
        logger.info(f"开始第{iteration}轮批判分析")
        
        # 使用搜索工具验证关键信息
        verification_results = []
        if self.search_tools:
            try:
                # 提取关键术语进行验证搜索
                key_terms = self._extract_key_terms_for_verification(original_query, research_data)
                logger.info(f"开始验证关键术语: {key_terms}")
                
                for term in key_terms[:3]:  # 限制验证查询数量
                    try:
                        verification = self.search_tools.comprehensive_search(
                            query=f"{term} 技术 文档 官方",
                            max_results=3,
                            scrape_content=False  # 只获取标题和链接用于验证
                        )
                        verification_results.extend(verification)
                    except Exception as e:
                        logger.warning(f"验证搜索 '{term}' 失败: {e}")
                        continue
            except Exception as e:
                logger.warning(f"验证搜索过程失败: {e}")
        
        # 构建验证上下文
        verification_context = ""
        if verification_results:
            verification_context = "\n\n**验证搜索结果:**\n"
            for i, result in enumerate(verification_results[:5], 1):
                verification_context += f"{i}. {result.get('title', '无标题')} - {result.get('url', '无链接')}\n"
            verification_context += "\n"
        
        # 检测查询语言
        query_language = self._detect_query_language(original_query)
        
        # 获取渐进式批判标准
        critique_standards = self.scoring_manager._get_progressive_critique_standards(iteration)
        
        critique_prompt = f"""
        请对以下研究结果进行批判性分析：

        **原始查询:** {original_query}
        
        **研究数据:** {research_data}
        {verification_context}
        
        **当前迭代轮次:** 第{iteration}轮
        **批判重点:** {critique_standards['focus']}
        **评分阈值:** {critique_standards['threshold']}分
        
        **重要：请严格按照以下要求进行分析：**
        1. **语言要求**: 分析结果必须使用与原始查询相同的语言。原始查询是{query_language}，因此分析结果必须完全使用{query_language}撰写。
        2. **迭代调整**: 这是第{iteration}轮分析，请根据迭代次数调整批判标准：
           - 第1轮：重点关注基础信息完整性，给予适当宽容
           - 第2轮：重点关注信息准确性，适度严格
           - 第3轮及以后：重点关注深度分析和一致性，较为严格
        3. 信息的完整性和准确性
        4. 是否存在矛盾或遗漏
        5. 是否偏离了原始查询
        6. 需要补充的信息
        7. 整体质量评分 (1-10分，考虑迭代调整)
        8. 信息来源的可信度
        9. 技术细节的准确性

        如果信息不充分，请提供具体的补充建议。
        如果信息已足够，请确认可以进入报告撰写阶段。
        
        请使用{query_language}撰写分析结果。
        """
        
        result = self.execute_task(critique_prompt, use_json_output=True, output_model=CritiqueResult)
        if result.success:
            try:
                # 尝试解析JSON结果（处理常见的围栏与单引号问题）
                raw_text = result.result.strip()
                
                # 去除markdown代码围栏
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```[a-zA-Z]*\n|```$", "", raw_text).strip()
                
                # 优先尝试标准JSON解析
                try:
                    critique_data = json.loads(raw_text)
                except json.JSONDecodeError:
                    # 如果标准JSON解析失败，尝试用ast.literal_eval解析Python字典字符串
                    critique_data = ast.literal_eval(raw_text)
                
                # 获取基础评分
                base_scores = {
                    'completeness': critique_data.get('completeness_score', 5),
                    'accuracy': critique_data.get('accuracy_score', 5)
                }
                
                # 使用动态评分管理器计算调整后的评分
                dynamic_result = self.scoring_manager.calculate_dynamic_score(
                    base_scores=base_scores,
                    iteration=iteration,
                    research_data=research_data,
                    original_query=original_query
                )
                
                # 构建返回结果
                return {
                    'critique': critique_data.get('critique', raw_text),
                    'completeness_score': dynamic_result['completeness_score'],
                    'accuracy_score': dynamic_result['accuracy_score'],
                    'overall_score': dynamic_result['overall_score'],
                    'needs_more_research': dynamic_result['needs_more_research'],
                    'missing_information': critique_data.get('missing_information', []),
                    'recommendations': critique_data.get('recommendations', []),
                    'quality_metrics': dynamic_result['quality_metrics'],
                    'adjustment_factors': dynamic_result['adjustment_factors'],
                    'critique_standards': dynamic_result['critique_standards'],
                    'iteration': iteration,
                    'success': True
                }
                
            except Exception as e:
                # 如果所有解析方法都失败，回退到文本分析
                logger.warning(f"JSON解析失败: {e}，已回退到文本分析")
                critique_text = raw_text.lower()
                needs_more_research = any(keyword in critique_text for keyword in [
                    '不充分', '不完整', '需要补充', '遗漏', 'insufficient', 'incomplete', 'need more'
                ])
                
                # 使用默认评分进行动态调整
                base_scores = {'completeness': 5, 'accuracy': 5}
                dynamic_result = self.scoring_manager.calculate_dynamic_score(
                    base_scores=base_scores,
                    iteration=iteration,
                    research_data=research_data,
                    original_query=original_query
                )
                
                return {
                    'critique': raw_text,
                    'completeness_score': dynamic_result['completeness_score'],
                    'accuracy_score': dynamic_result['accuracy_score'],
                    'overall_score': dynamic_result['overall_score'],
                    'needs_more_research': needs_more_research or dynamic_result['needs_more_research'],
                    'missing_information': [],
                    'recommendations': [],
                    'quality_metrics': dynamic_result['quality_metrics'],
                    'adjustment_factors': dynamic_result['adjustment_factors'],
                    'critique_standards': dynamic_result['critique_standards'],
                    'iteration': iteration,
                    'success': True
                }
        else:
            # 出错时使用默认评分
            base_scores = {'completeness': 5, 'accuracy': 5}
            dynamic_result = self.scoring_manager.calculate_dynamic_score(
                base_scores=base_scores,
                iteration=iteration,
                research_data=research_data,
                original_query=original_query
            )
            
            return {
                'critique': '',
                'completeness_score': dynamic_result['completeness_score'],
                'accuracy_score': dynamic_result['accuracy_score'],
                'overall_score': dynamic_result['overall_score'],
                'needs_more_research': True,  # 出错时默认需要更多研究
                'quality_metrics': dynamic_result['quality_metrics'],
                'adjustment_factors': dynamic_result['adjustment_factors'],
                'critique_standards': dynamic_result['critique_standards'],
                'iteration': iteration,
                'success': False,
                'error': result.error_message
            }
    
    def _extract_key_terms_for_verification(self, original_query: str, research_data: str) -> List[str]:
        """
        从查询和研究数据中提取关键术语用于验证
        
        Args:
            original_query: 原始查询
            research_data: 研究数据
            
        Returns:
            关键术语列表
        """
        import re
        
        # 从原始查询中提取技术术语
        tech_keywords = []
        
        # 常见技术术语模式
        tech_patterns = [
            r'\b[A-Z][a-zA-Z]*[A-Z][a-zA-Z]*\b',  # CamelCase 技术名称
            r'\b[a-z]+-[a-z]+\b',  # kebab-case 技术名称
            r'\b[a-z]+_[a-z]+\b',  # snake_case 技术名称
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, original_query)
            tech_keywords.extend(matches)
        
        # 从研究数据中提取提到的技术名称
        research_terms = []
        if research_data:
            # 查找技术名称（首字母大写的词）
            tech_matches = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', research_data)
            research_terms.extend(tech_matches[:10])  # 限制数量
        
        # 合并并去重
        all_terms = list(set(tech_keywords + research_terms))
        
        # 过滤掉常见的非技术词汇
        common_words = {'The', 'This', 'That', 'With', 'From', 'They', 'There', 'These', 'Those'}
        filtered_terms = [term for term in all_terms if term not in common_words]
        
        return filtered_terms[:5]  # 返回前5个术语


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
        
        # 检测用户查询的语言
        query_language = self._detect_query_language(query)
        logger.info(f"检测到查询语言: {query_language}")
        
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
            
            # 使用Agent进一步优化报告内容，明确指定语言要求
            optimization_prompt = f"""
            请基于以下研究数据，优化和完善这份技术报告：

            原始查询: {query}
            查询意图: {intent}
            研究数据: {research_data}

            **重要：请严格按照以下要求生成报告：**
            1. **语言要求**: 报告必须使用与原始查询相同的语言。原始查询是{query_language}，因此报告必须完全使用{query_language}撰写。
            2. 内容详实、逻辑清晰
            3. 使用专业的技术术语
            4. 提供具体的例子和代码
            5. 确保信息的准确性
            6. 保持Markdown格式
            7. 结构完整，各部分内容充实
            8. **绝对不要混用其他语言**，整个报告必须保持语言一致性

            请直接输出优化后的完整报告内容（使用{query_language}）：
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

            **重要：报告必须使用{query_language}撰写，与原始查询语言保持一致。**

            请生成一份结构清晰、内容详实的Markdown格式报告（使用{query_language}）。
            """
            
            result = self.execute_task(simple_prompt)
            if result.success:
                return result.result
            else:
                return f"报告生成失败: {result.error_message}"
    
    def _detect_query_language(self, query: str) -> str:
        """
        检测查询语言
        
        Args:
            query: 用户查询
            
        Returns:
            检测到的语言名称
        """
        import re
        
        # 英文字符检测
        english_pattern = re.compile(r'[a-zA-Z]')
        english_count = len(english_pattern.findall(query))
        
        # 中文字符检测
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        chinese_count = len(chinese_pattern.findall(query))
        
        # 根据字符数量判断主要语言
        total_chars = len(query.strip())
        if total_chars == 0:
            return "中文"  # 默认返回中文
        
        # 计算各语言字符占比
        chinese_ratio = chinese_count / total_chars
        english_ratio = english_count / total_chars
        
        # 判断主要语言
        # 优先考虑中文（即使占比不高）
        if chinese_count > 0:
            return "中文"
        elif english_count > 0:
            return "英文"
        else:
            return "中文"  # 默认返回中文


# 将语言检测方法添加到BaseAgent类中，让所有Agent都能使用
def _detect_query_language(self, query: str) -> str:
    """
    检测查询语言
    
    Args:
        query: 用户查询
        
    Returns:
        检测到的语言名称
    """
    import re
    
    # 英文字符检测
    english_pattern = re.compile(r'[a-zA-Z]')
    english_count = len(english_pattern.findall(query))
    
    # 中文字符检测
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    chinese_count = len(chinese_pattern.findall(query))
    
    # 根据字符数量判断主要语言
    total_chars = len(query.strip())
    if total_chars == 0:
        return "中文"  # 默认返回中文
    
    # 计算各语言字符占比
    chinese_ratio = chinese_count / total_chars
    english_ratio = english_count / total_chars
    
    # 判断主要语言
    # 优先考虑中文（即使占比不高）
    if chinese_count > 0:
        return "中文"
    elif english_count > 0:
        return "英文"
    else:
        return "中文"  # 默认返回中文

# 将方法添加到BaseAgent类
BaseAgent._detect_query_language = _detect_query_language
