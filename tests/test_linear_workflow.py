"""
线性工作流测试模块
"""

import pytest
from unittest.mock import Mock, patch
from src.workflows.linear_workflow import LinearWorkflow


class TestLinearWorkflow:
    """线性工作流测试"""
    
    @patch('langchain_openai.ChatOpenAI')
    def test_execute_success(self, mock_llm):
        """测试工作流执行成功"""
        # 模拟所有Agent的成功响应
        mock_classifier = Mock()
        mock_classifier.classify_query.return_value = "deep_dive"
        
        mock_planner = Mock()
        mock_planner.create_research_plan.return_value = {
            'plan': 'Test plan',
            'success': True
        }
        
        mock_researcher = Mock()
        mock_researcher.research_topic.return_value = {
            'research_data': 'Test research data',
            'success': True
        }
        
        mock_critic = Mock()
        mock_critic.critique_research.return_value = {
            'critique': 'Test critique',
            'needs_more_research': False,
            'success': True
        }
        
        mock_writer = Mock()
        mock_writer.write_report.return_value = 'Test report'
        
        # 创建模拟工作流
        workflow = LinearWorkflow()
        workflow.classifier = mock_classifier
        workflow.planner = mock_planner
        workflow.researcher = mock_researcher
        workflow.critic = mock_critic
        workflow.writer = mock_writer
        
        # 执行测试
        result = workflow.execute("Test query")
        
        assert result['success'] is True
        assert result['query'] == "Test query"
        assert len(result['steps']) == 5
        assert result['final_report'] == 'Test report'
    
    @patch('langchain_openai.ChatOpenAI')
    def test_execute_failure(self, mock_llm):
        """测试工作流执行失败"""
        # 模拟Agent失败
        mock_classifier = Mock()
        mock_classifier.classify_query.side_effect = Exception("Test error")
        
        workflow = LinearWorkflow()
        workflow.classifier = mock_classifier
        
        result = workflow.execute("Test query")
        
        assert result['success'] is False
        assert 'error' in result
        assert result['error'] == "Test error"
    
    @patch('langchain_openai.ChatOpenAI')
    def test_get_workflow_summary(self, mock_llm):
        """测试工作流摘要生成"""
        workflow = LinearWorkflow()
        
        # 测试成功结果
        success_results = {
            'success': True,
            'query': 'Test query',
            'steps': [
                {'step': 'classification', 'intent': 'deep_dive', 'success': True},
                {'step': 'planning', 'success': True},
                {'step': 'research', 'success': True},
                {'step': 'critique', 'success': True},
                {'step': 'writing', 'success': True}
            ],
            'final_report': 'Test report'
        }
        
        summary = workflow.get_workflow_summary(success_results)
        assert 'DeepDive Analyst 工作流执行摘要' in summary
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
