"""
LangGraph工作流测试模块
"""

import pytest
from unittest.mock import Mock, patch
from src.workflows.langgraph_workflow import LangGraphWorkflow, GraphState


class TestLangGraphWorkflow:
    """LangGraph工作流测试"""
    
    @patch('langchain_openai.ChatOpenAI')
    def test_init(self, mock_llm):
        """测试工作流初始化"""
        workflow = LangGraphWorkflow()
        assert workflow.classifier is not None
        assert workflow.planner is not None
        assert workflow.researcher is not None
        assert workflow.critic is not None
        assert workflow.writer is not None
        assert workflow.graph is not None
    
    @patch('langchain_openai.ChatOpenAI')
    def test_classify_node(self, mock_llm):
        """测试分类节点"""
        workflow = LangGraphWorkflow()
        
        # 模拟分类器
        workflow.classifier.classify_query = Mock(return_value="deep_dive")
        
        state = GraphState(
            original_query="Test query",
            intent="",
            plan="",
            research_queries=[],
            researched_data="",
            research_iteration=0,
            max_iterations=3,
            critique_feedback="",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        result_state = workflow._classify_node(state)
        
        assert result_state["intent"] == "deep_dive"
        assert result_state["success"] is True
    
    @patch('langchain_openai.ChatOpenAI')
    def test_plan_node(self, mock_llm):
        """测试规划节点"""
        workflow = LangGraphWorkflow()
        
        # 模拟规划器
        workflow.planner.create_research_plan = Mock(return_value={
            'plan': 'Test plan',
            'success': True
        })
        
        state = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="",
            research_queries=[],
            researched_data="",
            research_iteration=0,
            max_iterations=3,
            critique_feedback="",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        result_state = workflow._plan_node(state)
        
        assert result_state["plan"] == "Test plan"
        assert result_state["success"] is True
    
    @patch('langchain_openai.ChatOpenAI')
    def test_research_node(self, mock_llm):
        """测试研究节点"""
        workflow = LangGraphWorkflow()
        
        # 模拟研究员
        workflow.researcher.research_topic = Mock(return_value={
            'research_data': 'Test research data',
            'success': True
        })
        
        state = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="Test plan",
            research_queries=["test query"],
            researched_data="",
            research_iteration=0,
            max_iterations=3,
            critique_feedback="",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        result_state = workflow._research_node(state)
        
        assert "Test research data" in result_state["researched_data"]
        assert result_state["research_iteration"] == 1
        assert result_state["success"] is True
    
    @patch('langchain_openai.ChatOpenAI')
    def test_critique_node(self, mock_llm):
        """测试批判节点"""
        workflow = LangGraphWorkflow()
        
        # 模拟批判分析师
        workflow.critic.critique_research = Mock(return_value={
            'critique': 'Test critique',
            'needs_more_research': False,
            'success': True
        })
        
        state = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="Test plan",
            research_queries=["test query"],
            researched_data="Test research data",
            research_iteration=1,
            max_iterations=3,
            critique_feedback="",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        result_state = workflow._critique_node(state)
        
        assert result_state["critique_feedback"] == "Test critique"
        assert result_state["needs_more_research"] is False
        assert result_state["success"] is True
    
    @patch('langchain_openai.ChatOpenAI')
    def test_write_report_node(self, mock_llm):
        """测试报告撰写节点"""
        workflow = LangGraphWorkflow()
        
        # 模拟报告撰写师
        workflow.writer.write_report = Mock(return_value="Test report")
        
        state = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="Test plan",
            research_queries=["test query"],
            researched_data="Test research data",
            research_iteration=1,
            max_iterations=3,
            critique_feedback="Test critique",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        result_state = workflow._write_report_node(state)
        
        assert result_state["final_report"] == "Test report"
        assert result_state["success"] is True
    
    @patch('langchain_openai.ChatOpenAI')
    def test_should_continue_logic(self, mock_llm):
        """测试是否继续的逻辑"""
        workflow = LangGraphWorkflow()
        
        # 测试需要继续研究的情况
        state_continue = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="Test plan",
            research_queries=["test query"],
            researched_data="Test research data",
            research_iteration=1,
            max_iterations=3,
            critique_feedback="Test critique",
            needs_more_research=True,
            final_report="",
            error_message="",
            success=True
        )
        
        result = workflow._should_continue(state_continue)
        assert result == "continue"
        
        # 测试不需要继续研究的情况
        state_finish = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="Test plan",
            research_queries=["test query"],
            researched_data="Test research data",
            research_iteration=1,
            max_iterations=3,
            critique_feedback="Test critique",
            needs_more_research=False,
            final_report="",
            error_message="",
            success=True
        )
        
        result = workflow._should_continue(state_finish)
        assert result == "finish"
        
        # 测试达到最大迭代次数的情况
        state_max_iter = GraphState(
            original_query="Test query",
            intent="deep_dive",
            plan="Test plan",
            research_queries=["test query"],
            researched_data="Test research data",
            research_iteration=3,
            max_iterations=3,
            critique_feedback="Test critique",
            needs_more_research=True,
            final_report="",
            error_message="",
            success=True
        )
        
        result = workflow._should_continue(state_max_iter)
        assert result == "finish"
    
    @patch('langchain_openai.ChatOpenAI')
    def test_extract_search_queries(self, mock_llm):
        """测试搜索查询提取"""
        workflow = LangGraphWorkflow()
        
        plan = """
        研究计划：
        1. 搜索关键词：Python编程
        2. 查询：最佳实践
        3. 其他内容
        """
        
        queries = workflow._extract_search_queries(plan)
        
        assert len(queries) > 0
        assert "Python编程" in queries or "最佳实践" in queries
    
    @patch('langchain_openai.ChatOpenAI')
    def test_get_workflow_summary(self, mock_llm):
        """测试工作流摘要生成"""
        workflow = LangGraphWorkflow()
        
        # 测试成功结果
        success_results = {
            'success': True,
            'query': 'Test query',
            'intent': 'deep_dive',
            'research_iterations': 2,
            'final_report': 'Test report'
        }
        
        summary = workflow.get_workflow_summary(success_results)
        assert 'LangGraph工作流执行摘要' in summary
        assert 'Test query' in summary
        assert 'deep_dive' in summary
        assert 'Test report' in summary
        
        # 测试失败结果
        failure_results = {
            'success': False,
            'error': 'Test error'
        }
        
        summary = workflow.get_workflow_summary(failure_results)
        assert '工作流执行失败' in summary
        assert 'Test error' in summary


if __name__ == "__main__":
    pytest.main([__file__])
