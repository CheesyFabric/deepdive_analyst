"""
线性工作流模块
用于测试Agent的基本功能，实现简单的"研究-批判"流程
"""

from typing import Dict, Any, List
from loguru import logger
from src.agents.base_agents import (
    QueryClassifierAgent,
    ChiefPlannerAgent,
    WebResearcherAgent,
    CriticAnalystAgent,
    ReportWriterAgent
)


class LinearWorkflow:
    """线性工作流类"""
    
    def __init__(self):
        """初始化线性工作流"""
        self.classifier = QueryClassifierAgent()
        self.planner = ChiefPlannerAgent()
        self.researcher = WebResearcherAgent()
        self.critic = CriticAnalystAgent()
        self.writer = ReportWriterAgent()
        
        logger.info("线性工作流初始化成功")
    
    def execute(self, query: str) -> Dict[str, Any]:
        """
        执行完整的线性工作流
        
        Args:
            query: 用户查询
            
        Returns:
            工作流执行结果
        """
        logger.info(f"开始执行线性工作流，查询: {query}")
        
        results = {
            'query': query,
            'steps': [],
            'final_report': '',
            'success': False,
            'error': None
        }
        
        try:
            # 步骤1: 查询分类
            logger.info("步骤1: 查询意图分类")
            intent = self.classifier.classify_query(query)
            results['steps'].append({
                'step': 'classification',
                'intent': intent,
                'success': True
            })
            logger.info(f"查询分类完成: {intent}")
            
            # 步骤2: 制定研究计划
            logger.info("步骤2: 制定研究计划")
            plan_result = self.planner.create_research_plan(query, intent)
            results['steps'].append({
                'step': 'planning',
                'plan': plan_result.get('plan', ''),
                'success': plan_result.get('success', False)
            })
            logger.info("研究计划制定完成")
            
            # 步骤3: 执行研究
            logger.info("步骤3: 执行网络研究")
            research_result = self.researcher.research_topic(plan_result)
            results['steps'].append({
                'step': 'research',
                'research_data': research_result.get('research_data', ''),
                'success': research_result.get('success', False)
            })
            logger.info("网络研究完成")
            
            # 步骤4: 批判性分析
            logger.info("步骤4: 批判性分析")
            research_data = research_result.get('research_data', '')
            critique_result = self.critic.critique_research(research_data, query)
            results['steps'].append({
                'step': 'critique',
                'critique': critique_result.get('critique', ''),
                'needs_more_research': critique_result.get('needs_more_research', False),
                'success': critique_result.get('success', False)
            })
            logger.info("批判性分析完成")
            
            # 步骤5: 撰写报告
            logger.info("步骤5: 撰写最终报告")
            final_report = self.writer.write_report(research_data, intent, query)
            results['final_report'] = final_report
            results['steps'].append({
                'step': 'writing',
                'success': True
            })
            logger.info("报告撰写完成")
            
            results['success'] = True
            logger.info("线性工作流执行成功")
            
        except Exception as e:
            logger.error(f"线性工作流执行失败: {str(e)}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def get_workflow_summary(self, results: Dict[str, Any]) -> str:
        """
        获取工作流执行摘要
        
        Args:
            results: 工作流执行结果
            
        Returns:
            工作流摘要
        """
        if not results['success']:
            return f"工作流执行失败: {results.get('error', '未知错误')}"
        
        summary = f"""
# DeepDive Analyst 工作流执行摘要

## 查询信息
- **原始查询**: {results['query']}
- **查询意图**: {results['steps'][0]['intent']}

## 执行步骤
"""
        
        step_names = {
            'classification': '查询意图分类',
            'planning': '制定研究计划',
            'research': '执行网络研究',
            'critique': '批判性分析',
            'writing': '撰写最终报告'
        }
        
        for i, step in enumerate(results['steps'], 1):
            step_name = step_names.get(step['step'], step['step'])
            status = "✅ 成功" if step['success'] else "❌ 失败"
            summary += f"{i}. **{step_name}**: {status}\n"
        
        summary += f"\n## 最终报告\n{results['final_report']}"
        
        return summary
