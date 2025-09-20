"""
LangGraph工作流模块
实现"研究-批判-修正"的迭代循环
"""

from typing import Dict, Any, List, TypedDict, Annotated
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import os
from src.agents.base_agents import (
    QueryClassifierAgent,
    ChiefPlannerAgent,
    WebResearcherAgent,
    CriticAnalystAgent,
    ReportWriterAgent
)
from src.tools.search_tools import SearchToolsManager


class GraphState(TypedDict):
    """LangGraph状态定义"""
    # 输入信息
    original_query: str
    intent: str
    
    # 规划信息
    plan: str
    research_queries: List[str]
    
    # 研究信息
    researched_data: str
    research_iteration: int
    max_iterations: int
    
    # 批判信息
    critique_feedback: str
    needs_more_research: bool
    
    # 最终输出
    final_report: str
    
    # 错误处理
    error_message: str
    success: bool


class LangGraphWorkflow:
    """LangGraph工作流类"""
    
    def __init__(self):
        """初始化LangGraph工作流"""
        # 初始化所有Agent
        self.classifier = QueryClassifierAgent()
        self.planner = ChiefPlannerAgent()
        self.researcher = WebResearcherAgent()
        self.critic = CriticAnalystAgent()
        self.writer = ReportWriterAgent()
        
        # 初始化搜索工具
        self.search_tools = SearchToolsManager()
        
        # 构建图
        self.graph = self._build_graph()
        
        logger.info("LangGraph工作流初始化成功")
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph状态图"""
        # 创建状态图
        workflow = StateGraph(GraphState)
        
        # 添加节点
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("critique", self._critique_node)
        workflow.add_node("write_report", self._write_report_node)
        
        # 设置入口点
        workflow.set_entry_point("classify")
        
        # 添加边
        workflow.add_edge("classify", "plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "critique")
        
        # 条件边：从critique到research或write_report
        workflow.add_conditional_edges(
            "critique",
            self._should_continue,
            {
                "continue": "research",
                "finish": "write_report"
            }
        )
        
        workflow.add_edge("write_report", END)
        
        # 编译图
        return workflow.compile()
    
    def _classify_node(self, state: GraphState) -> GraphState:
        """查询分类节点"""
        logger.info("执行查询分类节点")
        
        try:
            intent = self.classifier.classify_query(state["original_query"])
            state["intent"] = intent
            state["success"] = True
            logger.info(f"查询分类完成: {intent}")
        except Exception as e:
            logger.error(f"查询分类失败: {str(e)}")
            state["error_message"] = str(e)
            state["success"] = False
        
        return state
    
    def _plan_node(self, state: GraphState) -> GraphState:
        """规划节点"""
        logger.info("执行规划节点")
        
        try:
            plan_result = self.planner.create_research_plan(
                state["original_query"], 
                state["intent"]
            )
            
            if plan_result["success"]:
                state["plan"] = plan_result["plan"]
                # 从计划中提取搜索查询（简单实现）
                state["research_queries"] = self._extract_search_queries(plan_result["plan"])
                state["success"] = True
                logger.info("规划完成")
            else:
                state["error_message"] = plan_result.get("error", "规划失败")
                state["success"] = False
                
        except Exception as e:
            logger.error(f"规划失败: {str(e)}")
            state["error_message"] = str(e)
            state["success"] = False
        
        return state
    
    def _research_node(self, state: GraphState) -> GraphState:
        """研究节点"""
        logger.info(f"执行研究节点 (第{state.get('research_iteration', 1)}轮)")
        
        try:
            # 增加迭代计数
            state["research_iteration"] = state.get("research_iteration", 0) + 1
            
            # 执行研究
            research_result = self.researcher.research_topic({
                "plan": state["plan"],
                "query": state["original_query"],
                "intent": state["intent"]
            })
            
            if research_result["success"]:
                # 累积研究数据
                new_data = research_result["research_data"]
                existing_data = state.get("researched_data", "")
                
                if existing_data:
                    state["researched_data"] = f"{existing_data}\n\n--- 第{state['research_iteration']}轮研究 ---\n{new_data}"
                else:
                    state["researched_data"] = new_data
                
                state["success"] = True
                logger.info(f"第{state['research_iteration']}轮研究完成")
            else:
                state["error_message"] = research_result.get("error", "研究失败")
                state["success"] = False
                
        except Exception as e:
            logger.error(f"研究失败: {str(e)}")
            state["error_message"] = str(e)
            state["success"] = False
        
        return state
    
    def _critique_node(self, state: GraphState) -> GraphState:
        """批判节点"""
        logger.info("执行批判节点")
        
        try:
            critique_result = self.critic.critique_research(
                state["researched_data"],
                state["original_query"]
            )
            
            if critique_result["success"]:
                state["critique_feedback"] = critique_result["critique"]
                state["needs_more_research"] = critique_result["needs_more_research"]
                state["success"] = True
                logger.info("批判分析完成")
            else:
                state["error_message"] = critique_result.get("error", "批判分析失败")
                state["success"] = False
                
        except Exception as e:
            logger.error(f"批判分析失败: {str(e)}")
            state["error_message"] = str(e)
            state["success"] = False
        
        return state
    
    def _write_report_node(self, state: GraphState) -> GraphState:
        """报告撰写节点"""
        logger.info("执行报告撰写节点")
        
        try:
            final_report = self.writer.write_report(
                state["researched_data"],
                state["intent"],
                state["original_query"]
            )
            
            state["final_report"] = final_report
            state["success"] = True
            logger.info("报告撰写完成")
            
        except Exception as e:
            logger.error(f"报告撰写失败: {str(e)}")
            state["error_message"] = str(e)
            state["success"] = False
        
        return state
    
    def _should_continue(self, state: GraphState) -> str:
        """决定是否继续研究的条件函数"""
        # 检查是否有错误
        if not state.get("success", True):
            logger.info("检测到错误，结束工作流")
            return "finish"
        
        # 检查是否达到最大迭代次数
        max_iterations = state.get("max_iterations", 3)
        current_iteration = state.get("research_iteration", 0)
        
        if current_iteration >= max_iterations:
            logger.info(f"达到最大迭代次数 ({max_iterations})，结束研究")
            return "finish"
        
        # 检查批判结果
        needs_more_research = state.get("needs_more_research", False)
        
        if needs_more_research:
            logger.info("批判分析认为需要更多研究，继续研究")
            return "continue"
        else:
            logger.info("批判分析认为研究充分，进入报告撰写")
            return "finish"
    
    def _extract_search_queries(self, plan: str) -> List[str]:
        """从研究计划中提取搜索查询（智能版）"""
        import re
        
        queries = []
        
        # 方法1: 使用LLM智能提取（推荐）
        try:
            # 构建提取提示
            extract_prompt = f"""
请从以下研究计划中提取5个最重要的搜索查询词，用于进行技术调研。

研究计划内容：
{plan}

要求：
1. 提取最核心的技术术语和概念
2. 优先提取具体的产品名称（如CrewAI、Autogen）
3. 包含相关的技术概念（如多智能体、协作机制等）
4. 每个查询词应该是独立的、可搜索的
5. 返回格式：每行一个查询词

请直接返回查询词，不要添加其他说明：
"""
            
            # 使用分类器LLM进行智能提取
            if hasattr(self, 'classifier') and self.classifier and hasattr(self.classifier, 'llm'):
                try:
                    response = None
                    
                    # 尝试不同的调用方法
                    if hasattr(self.classifier.llm, 'invoke'):
                        # LangChain 风格的调用
                        response = self.classifier.llm.invoke(extract_prompt)
                        logger.info("使用 invoke 方法调用LLM")
                    elif hasattr(self.classifier.llm, 'call'):
                        # CrewAI 风格的调用
                        response = self.classifier.llm.call(extract_prompt)
                        logger.info("使用 call 方法调用LLM")
                    elif hasattr(self.classifier.llm, 'generate'):
                        # 其他可能的调用方法
                        response = self.classifier.llm.generate([extract_prompt])
                        logger.info("使用 generate 方法调用LLM")
                    elif hasattr(self.classifier.llm, 'predict'):
                        # 预测方法
                        response = self.classifier.llm.predict(extract_prompt)
                        logger.info("使用 predict 方法调用LLM")
                    else:
                        logger.warning(f"LLM对象没有可用的调用方法，可用方法: {dir(self.classifier.llm)}")
                        raise AttributeError("LLM对象没有可用的调用方法")
                    
                    if response is not None:
                        # 处理不同类型的响应
                        response_text = ""
                        
                        if hasattr(response, 'content'):
                            response_text = response.content
                        elif hasattr(response, 'text'):
                            response_text = response.text
                        elif hasattr(response, 'generations') and response.generations:
                            # 处理 generate 方法的响应
                            response_text = response.generations[0][0].text
                        elif isinstance(response, str):
                            response_text = response
                        else:
                            response_text = str(response)
                        
                        llm_queries = response_text.strip().split('\n')
                        
                        # 清理LLM返回的查询
                        for query in llm_queries:
                            query = query.strip()
                            # 移除编号和多余符号
                            query = re.sub(r'^\d+[\.\)]\s*', '', query)
                            query = re.sub(r'^[-*]\s*', '', query)
                            query = query.strip()
                            
                            if query and len(query) > 2:
                                queries.append(query)
                        
                        if queries:
                            logger.info(f"LLM智能提取到搜索查询: {queries}")
                            return queries[:5]
                        else:
                            logger.warning("LLM返回的查询为空")
                    else:
                        logger.warning("LLM调用返回None")
                        
                except Exception as e:
                    logger.warning(f"LLM提取失败: {e}")
                    # 如果LLM提取失败，使用默认查询
                    queries = ["CrewAI", "Autogen", "多智能体协作", "Multi-agent system", "技术对比"]
                    logger.info(f"使用默认查询: {queries}")
                    return queries[:5]
            else:
                logger.warning("分类器或LLM不可用")
                # 如果分类器不可用，使用默认查询
                queries = ["CrewAI", "Autogen", "多智能体协作", "Multi-agent system", "技术对比"]
                logger.info(f"使用默认查询: {queries}")
                return queries[:5]
        
        except Exception as e:
            logger.warning(f"LLM提取异常: {e}")
            # 如果出现异常，使用默认查询
            queries = ["CrewAI", "Autogen", "多智能体协作", "Multi-agent system", "技术对比"]
            logger.info(f"使用默认查询: {queries}")
            return queries[:5]
        
        # 方法2: 基于结构的智能解析（备用）
        # queries = self._parse_structured_content(plan)
        # if queries:
        #     logger.info(f"结构化解析提取到搜索查询: {queries}")
        #     return queries[:5]
        
        return queries[:5]
    
    def _parse_structured_content(self, plan: str) -> List[str]:
        """基于内容结构的智能解析"""
        import re
        
        queries = []
        
        # 查找关键搜索词列表部分
        lines = plan.split('\n')
        in_keyword_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 检测关键词列表开始
            if re.search(r'关键.*?搜索.*?词|搜索.*?词.*?列表|关键词.*?列表', line, re.IGNORECASE):
                in_keyword_section = True
                continue
            
            # 在关键词部分提取内容
            if in_keyword_section:
                # 跳过空行
                if not line:
                    continue
                
                # 如果遇到新的主要章节，停止提取
                if re.match(r'\*\*\d+\.|##\s*\d+\.', line):
                    break
                
                # 提取列表项中的内容
                if line.startswith('*') and ':' in line:
                    # 处理 * **CrewAI:** 格式
                    colon_pos = line.find(':')
                    if colon_pos != -1:
                        content = line[colon_pos + 1:].strip()
                        # 清理内容
                        content = re.sub(r'^\*+\s*', '', content)
                        content = content.strip()
                        
                        if content:
                            # 分割逗号分隔的内容
                            if ',' in content:
                                items = [item.strip() for item in content.split(',')]
                                for item in items:
                                    if len(item) > 2:
                                        queries.append(item)
                            else:
                                queries.append(content)
        
        # 去重和清理
        unique_queries = []
        seen = set()
        
        for query in queries:
            query = query.strip()
            # 清理特殊字符，保留中英文、数字、空格
            query = re.sub(r'[^\w\s\u4e00-\u9fff]', '', query)
            query = query.strip()
            
            if query and len(query) > 2 and query not in seen:
                seen.add(query)
                unique_queries.append(query)
        
        return unique_queries
    
    
    def execute(self, query: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        执行LangGraph工作流
        
        Args:
            query: 用户查询
            max_iterations: 最大迭代次数
            
        Returns:
            工作流执行结果
        """
        logger.info(f"开始执行LangGraph工作流，查询: {query}")
        
        # 检查LangSmith配置
        langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        if langsmith_enabled:
            logger.info("LangSmith追踪已启用，执行轨迹将发送到LangSmith控制台")
        
        # 初始化状态
        initial_state = GraphState(
            original_query=query,
            intent="",
            plan="",
            research_queries=[],
            researched_data="",
            research_iteration=0,
            max_iterations=max_iterations,
            critique_feedback="",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        try:
            # 执行图 - LangGraph会自动与LangSmith集成
            final_state = self.graph.invoke(initial_state)
            
            logger.info("LangGraph工作流执行完成")
            
            # 构建返回结果
            result = {
                "success": final_state.get("success", False),
                "query": query,
                "intent": final_state.get("intent", ""),
                "final_report": final_state.get("final_report", ""),
                "research_iterations": final_state.get("research_iteration", 0),
                "error": final_state.get("error_message", ""),
                "langsmith_enabled": langsmith_enabled
            }
            
            # 如果启用了LangSmith，添加追踪信息
            if langsmith_enabled:
                result["langsmith_info"] = {
                    "project": os.getenv("LANGCHAIN_PROJECT", "deepdive-analyst"),
                    "trace_url": "https://smith.langchain.com/",
                    "message": "请访问LangSmith控制台查看详细的执行轨迹"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"LangGraph工作流执行失败: {str(e)}")
            return {
                "success": False,
                "query": query,
                "final_report": "",
                "error": str(e),
                "langsmith_enabled": langsmith_enabled
            }
    
    def get_workflow_summary(self, results: Dict[str, Any]) -> str:
        """
        获取工作流执行摘要
        
        Args:
            results: 工作流执行结果
            
        Returns:
            工作流摘要
        """
        if not results["success"]:
            return f"LangGraph工作流执行失败: {results.get('error', '未知错误')}"
        
        summary = f"""
# DeepDive Analyst LangGraph工作流执行摘要

## 查询信息
- **原始查询**: {results['query']}
- **查询意图**: {results['intent']}
- **研究迭代次数**: {results.get('research_iterations', 0)}

## 执行结果
✅ **工作流执行成功**

## 最终报告
{results['final_report']}
"""
        
        return summary
