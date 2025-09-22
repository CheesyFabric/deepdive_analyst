"""
更新后的CriticAnalystAgent测试模块
测试集成动态评分系统的CriticAnalystAgent
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.base_agents import CriticAnalystAgent


class TestUpdatedCriticAnalystAgent:
    """更新后的CriticAnalystAgent测试"""
    
    @patch('src.agents.base_agents.Config.get_llm_config')
    @patch('src.agents.base_agents.LLMFactory.create_llm')
    def test_init_with_scoring_manager(self, mock_create_llm, mock_get_config):
        """测试初始化时包含评分管理器"""
        mock_get_config.return_value = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key',
            'temperature': 0.1,
            'max_tokens': 4000,
            'timeout': 30,
            'max_retries': 3
        }
        mock_create_llm.return_value = Mock()
        
        agent = CriticAnalystAgent()
        
        assert hasattr(agent, 'scoring_manager')
        assert agent.scoring_manager is not None
    
    @patch('src.agents.base_agents.Config.get_llm_config')
    @patch('src.agents.base_agents.LLMFactory.create_llm')
    def test_critique_research_with_iteration(self, mock_create_llm, mock_get_config):
        """测试带迭代次数的批判分析"""
        mock_get_config.return_value = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key',
            'temperature': 0.1,
            'max_tokens': 4000,
            'timeout': 30,
            'max_retries': 3
        }
        mock_create_llm.return_value = Mock()
        
        agent = CriticAnalystAgent()
        
        # 模拟execute_task方法
        mock_result = Mock()
        mock_result.success = True
        mock_result.result = '{"critique": "测试批判", "completeness_score": 7, "accuracy_score": 8, "needs_more_research": false}'
        agent.execute_task = Mock(return_value=mock_result)
        
        # 模拟scoring_manager的方法
        agent.scoring_manager._get_progressive_critique_standards = Mock(return_value={
            'focus': '基础信息完整性',
            'threshold': 6,
            'tolerance': 0.8
        })
        
        agent.scoring_manager.calculate_dynamic_score = Mock(return_value={
            'completeness_score': 8,
            'accuracy_score': 9,
            'overall_score': 8.5,
            'needs_more_research': False,
            'quality_metrics': {'information_density': 0.8},
            'adjustment_factors': {'iteration_bonus': 0.5},
            'critique_standards': {'focus': '基础信息完整性'}
        })
        
        result = agent.critique_research(
            research_data="测试研究数据",
            original_query="测试查询",
            iteration=1
        )
        
        assert result['success'] is True
        assert result['completeness_score'] == 8
        assert result['accuracy_score'] == 9
        assert result['overall_score'] == 8.5
        assert result['iteration'] == 1
        assert 'quality_metrics' in result
        assert 'adjustment_factors' in result
        assert 'critique_standards' in result
    
    @patch('src.agents.base_agents.Config.get_llm_config')
    @patch('src.agents.base_agents.LLMFactory.create_llm')
    def test_critique_research_iteration_progression(self, mock_create_llm, mock_get_config):
        """测试迭代轮次的批判标准变化"""
        mock_get_config.return_value = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key',
            'temperature': 0.1,
            'max_tokens': 4000,
            'timeout': 30,
            'max_retries': 3
        }
        mock_create_llm.return_value = Mock()
        
        agent = CriticAnalystAgent()
        
        # 模拟execute_task方法
        mock_result = Mock()
        mock_result.success = True
        mock_result.result = '{"critique": "测试批判", "completeness_score": 7, "accuracy_score": 8, "needs_more_research": false}'
        agent.execute_task = Mock(return_value=mock_result)
        
        # 测试不同迭代轮次的批判标准
        test_cases = [
            (1, '基础信息完整性', 6),
            (2, '信息准确性', 7),
            (3, '深度分析', 8)
        ]
        
        for iteration, expected_focus, expected_threshold in test_cases:
            agent.scoring_manager._get_progressive_critique_standards = Mock(return_value={
                'focus': expected_focus,
                'threshold': expected_threshold,
                'tolerance': 0.8
            })
            
            agent.scoring_manager.calculate_dynamic_score = Mock(return_value={
                'completeness_score': 7,
                'accuracy_score': 8,
                'overall_score': 7.5,
                'needs_more_research': False,
                'quality_metrics': {},
                'adjustment_factors': {},
                'critique_standards': {'focus': expected_focus}
            })
            
            result = agent.critique_research(
                research_data="测试研究数据",
                original_query="测试查询",
                iteration=iteration
            )
            
            # 验证批判标准被正确调用
            agent.scoring_manager._get_progressive_critique_standards.assert_called_with(iteration)
            
            # 验证动态评分被正确调用
            agent.scoring_manager.calculate_dynamic_score.assert_called()
    
    @patch('src.agents.base_agents.Config.get_llm_config')
    @patch('src.agents.base_agents.LLMFactory.create_llm')
    def test_critique_research_error_handling(self, mock_create_llm, mock_get_config):
        """测试错误处理"""
        mock_get_config.return_value = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key',
            'temperature': 0.1,
            'max_tokens': 4000,
            'timeout': 30,
            'max_retries': 3
        }
        mock_create_llm.return_value = Mock()
        
        agent = CriticAnalystAgent()
        
        # 模拟execute_task失败
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "LLM调用失败"
        agent.execute_task = Mock(return_value=mock_result)
        
        # 模拟scoring_manager的方法
        agent.scoring_manager.calculate_dynamic_score = Mock(return_value={
            'completeness_score': 5,
            'accuracy_score': 5,
            'overall_score': 5.0,
            'needs_more_research': True,
            'quality_metrics': {},
            'adjustment_factors': {},
            'critique_standards': {}
        })
        
        result = agent.critique_research(
            research_data="测试研究数据",
            original_query="测试查询",
            iteration=1
        )
        
        assert result['success'] is False
        assert result['error'] == "LLM调用失败"
        assert result['needs_more_research'] is True
    
    @patch('src.agents.base_agents.Config.get_llm_config')
    @patch('src.agents.base_agents.LLMFactory.create_llm')
    def test_critique_research_json_parsing_fallback(self, mock_create_llm, mock_get_config):
        """测试JSON解析失败时的回退处理"""
        mock_get_config.return_value = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key',
            'temperature': 0.1,
            'max_tokens': 4000,
            'timeout': 30,
            'max_retries': 3
        }
        mock_create_llm.return_value = Mock()
        
        agent = CriticAnalystAgent()
        
        # 模拟execute_task返回非JSON格式的结果
        mock_result = Mock()
        mock_result.success = True
        mock_result.result = "这不是一个有效的JSON格式的响应"
        agent.execute_task = Mock(return_value=mock_result)
        
        # 模拟scoring_manager的方法
        agent.scoring_manager.calculate_dynamic_score = Mock(return_value={
            'completeness_score': 5,
            'accuracy_score': 5,
            'overall_score': 5.0,
            'needs_more_research': True,
            'quality_metrics': {},
            'adjustment_factors': {},
            'critique_standards': {}
        })
        
        result = agent.critique_research(
            research_data="测试研究数据",
            original_query="测试查询",
            iteration=1
        )
        
        assert result['success'] is True
        assert result['critique'] == "这不是一个有效的JSON格式的响应"
        assert result['completeness_score'] == 5
        assert result['accuracy_score'] == 5
    
    @patch('src.agents.base_agents.Config.get_llm_config')
    @patch('src.agents.base_agents.LLMFactory.create_llm')
    def test_critique_research_with_search_tools(self, mock_create_llm, mock_get_config):
        """测试带搜索工具的批判分析"""
        mock_get_config.return_value = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key',
            'temperature': 0.1,
            'max_tokens': 4000,
            'timeout': 30,
            'max_retries': 3
        }
        mock_create_llm.return_value = Mock()
        
        # 模拟搜索工具
        mock_search_tools = Mock()
        mock_search_tools.comprehensive_search = Mock(return_value=[
            {'title': '测试标题', 'url': 'http://test.com'}
        ])
        
        agent = CriticAnalystAgent(search_tools=mock_search_tools)
        
        # 模拟execute_task方法
        mock_result = Mock()
        mock_result.success = True
        mock_result.result = '{"critique": "测试批判", "completeness_score": 7, "accuracy_score": 8, "needs_more_research": false}'
        agent.execute_task = Mock(return_value=mock_result)
        
        # 模拟scoring_manager的方法
        agent.scoring_manager._get_progressive_critique_standards = Mock(return_value={
            'focus': '基础信息完整性',
            'threshold': 6,
            'tolerance': 0.8
        })
        
        agent.scoring_manager.calculate_dynamic_score = Mock(return_value={
            'completeness_score': 8,
            'accuracy_score': 9,
            'overall_score': 8.5,
            'needs_more_research': False,
            'quality_metrics': {},
            'adjustment_factors': {},
            'critique_standards': {}
        })
        
        result = agent.critique_research(
            research_data="Python是一种编程语言",
            original_query="Python编程",
            iteration=1
        )
        
        
        assert result['success'] is True
        assert result['completeness_score'] == 8
        assert result['accuracy_score'] == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
