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
        """从研究计划中提取搜索查询（简单实现）"""
        # 这里是一个简单的实现，实际应用中可能需要更复杂的NLP处理
        queries = []
        
        # 查找包含"搜索"、"查询"等关键词的句子
        lines = plan.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ['搜索', '查询', '关键词', 'search', 'query']):
                # 提取可能的查询词
                if ':' in line:
                    query_part = line.split(':', 1)[1].strip()
                    if query_part:
                        queries.append(query_part)
        
        # 如果没有找到明确的查询，返回默认查询
        if not queries:
            queries = ["技术调研", "最佳实践"]
        
        return queries[:5]  # 限制查询数量
    
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
