"""
_extract_search_queries 方法的单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.workflows.langgraph_workflow import LangGraphWorkflow


class TestExtractSearchQueries:
    """测试 _extract_search_queries 方法"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.workflow = LangGraphWorkflow()
    
    def test_llm_invoke_success(self):
        """测试LLM invoke方法成功的情况"""
        # 模拟LLM响应
        mock_response = Mock()
        mock_response.content = """CrewAI
Autogen
多智能体协作
Multi-agent system
技术对比"""
        
        # 模拟分类器的LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = """**研究计划：CrewAI与Autogen多智能体协作能力对比分析**

**2. 关键搜索词列表:**

* **CrewAI:** CrewAI, Crew AI, Crew.ai
* **Autogen:** Autogen, AutoGen, Autogen AI"""
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
        
        # 验证LLM被调用
        mock_llm.invoke.assert_called_once()
    
    def test_llm_call_success(self):
        """测试LLM call方法成功的情况"""
        # 模拟LLM响应
        mock_response = """CrewAI
Autogen
多智能体协作
Multi-agent system
技术对比"""
        
        # 模拟分类器的LLM（没有invoke方法，但有call方法）
        mock_llm = Mock()
        mock_llm.invoke = None  # 没有invoke方法
        mock_llm.call.return_value = mock_response
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        
    
    
    def test_llm_predict_success(self):
        """测试LLM predict方法成功的情况"""
        # 模拟predict方法的响应
        mock_response = """CrewAI
Autogen
多智能体协作
Multi-agent system
技术对比"""
        
        # 模拟分类器的LLM
        mock_llm = Mock()
        mock_llm.invoke = None
        mock_llm.call = None
        mock_llm.generate = None
        mock_llm.predict.return_value = mock_response
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        
    
    def test_llm_no_available_methods(self):
        """测试LLM没有任何可用方法的情况"""
        # 模拟分类器的LLM（没有任何调用方法）
        mock_llm = Mock()
        mock_llm.invoke = None
        mock_llm.call = None
        mock_llm.generate = None
        mock_llm.predict = None
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该返回默认查询）
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
    
    def test_llm_call_exception(self):
        """测试LLM调用抛出异常的情况"""
        # 模拟分类器的LLM（调用时抛出异常）
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM调用失败")
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该返回默认查询）
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
    
    def test_no_classifier(self):
        """测试没有分类器的情况"""
        # 不设置分类器
        self.workflow.classifier = None
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该返回默认查询）
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
    
    def test_classifier_no_llm(self):
        """测试分类器没有LLM属性的情况"""
        # 模拟分类器（没有LLM属性）
        self.workflow.classifier = Mock()
        del self.workflow.classifier.llm  # 删除LLM属性
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该返回默认查询）
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
    
    def test_llm_response_cleaning(self):
        """测试LLM响应清理功能"""
        # 模拟LLM响应（包含需要清理的内容）
        mock_response = Mock()
        mock_response.content = """1. CrewAI
2. Autogen
- 多智能体协作
* Multi-agent system
技术对比"""
        
        # 模拟分类器的LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该清理掉编号和符号）
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
        
        # 验证清理效果
        for query in result:
            assert not query.startswith(('1.', '2.', '-', '*'))
    
    def test_llm_response_empty(self):
        """测试LLM返回空响应的情况"""
        # 模拟LLM响应（空内容）
        mock_response = Mock()
        mock_response.content = ""
        
        # 模拟分类器的LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该返回默认查询）
        assert len(result) == 0

    
    def test_llm_response_none(self):
        """测试LLM返回None的情况"""
        # 模拟分类器的LLM（返回None）
        mock_llm = Mock()
        mock_llm.invoke.return_value = None
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 测试数据
        test_plan = "**研究计划：CrewAI与Autogen多智能体协作能力对比分析**"
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果（应该返回默认查询）
        assert len(result) == 0
    
    def test_complex_plan_extraction(self):
        """测试复杂研究计划的提取"""
        # 模拟LLM响应
        mock_response = Mock()
        mock_response.content = """CrewAI
Autogen
多智能体协作
Multi-agent system
技术对比"""
        
        # 模拟分类器的LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        self.workflow.classifier = Mock()
        self.workflow.classifier.llm = mock_llm
        
        # 复杂的测试数据
        test_plan = """**研究计划：CrewAI与Autogen多智能体协作能力对比分析**

**1. 研究目标:**

系统性地比较和分析CrewAI和Autogen在实现多智能体协作方面的异同点，最终形成一份详尽的对比报告，涵盖技术架构、协作机制、应用场景以及优缺点等方面。

**2. 关键搜索词列表:**

* **CrewAI:** CrewAI, Crew AI, Crew.ai, Crew AI documentation, Crew AI architecture, Crew AI multi-agent system, Crew AI case studies
* **Autogen:** Autogen, AutoGen, Autogen AI, Autogen documentation, Autogen architecture, Autogen multi-agent system, Autogen framework, Autogen examples, Autogen use cases
* **多智能体系统:** Multi-agent system (MAS), Multi-agent system architecture, Multi-agent collaboration, Distributed artificial intelligence (DAI), Agent-based modeling (ABM), 多智能体协作, 分布式人工智能, 基于智能体的建模
* **协作机制:** Communication protocols, Coordination mechanisms, Cooperation strategies, Conflict resolution, Negotiation, Task allocation, 信息共享, 任务分配, 冲突解决
* **应用场景:** Robotics, Game AI, Simulation, Supply chain management, Traffic control, 资源调度, 机器人控制, 游戏人工智能

**3. 需要关注的技术方面:**

* **架构设计:** 两种平台的多智能体系统架构（例如，集中式、分布式、混合式），以及它们如何支持多智能体间的通信和协调。
* **通信机制:** 分析两种平台支持的通信协议和机制，例如点对点通信、广播通信、基于消息队列的通信等。
* **协作策略:** 研究两种平台支持的协作策略，例如竞争、合作、混合策略等。
* **智能体行为:** 分析两种平台如何定义和管理智能体行为，包括智能体的感知、决策和行动能力。
* **知识表示与推理:** 研究两种平台如何表示和推理智能体的知识，例如使用知识图谱、本体论等技术。
* **应用案例:** 收集和分析两种平台的实际应用案例，以了解其在不同场景下的性能和效果。
* **编程接口和易用性:** 评估两种平台提供的编程接口和开发工具的易用性和效率。"""
        
        # 执行测试
        result = self.workflow._extract_search_queries(test_plan)
        
        # 验证结果
        assert len(result) == 5
        assert "CrewAI" in result
        assert "Autogen" in result
        assert "多智能体协作" in result
        assert "Multi-agent system" in result
        assert "技术对比" in result
        
        # 验证LLM被调用
        mock_llm.invoke.assert_called_once()
        
        # 验证调用参数包含研究计划
        call_args = mock_llm.invoke.call_args[0][0]
        assert "CrewAI与Autogen多智能体协作能力对比分析" in call_args
        assert "关键搜索词列表" in call_args


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])

