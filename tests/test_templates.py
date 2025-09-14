"""
模板测试模块
"""

import pytest
from src.configs.templates import ReportTemplates, TemplateProcessor


class TestReportTemplates:
    """报告模板测试"""
    
    def test_comparison_template_exists(self):
        """测试对比模板存在"""
        assert ReportTemplates.COMPARISON_TEMPLATE is not None
        assert "{title}" in ReportTemplates.COMPARISON_TEMPLATE
        assert "{summary}" in ReportTemplates.COMPARISON_TEMPLATE
    
    def test_deep_dive_template_exists(self):
        """测试深度解析模板存在"""
        assert ReportTemplates.DEEP_DIVE_TEMPLATE is not None
        assert "{title}" in ReportTemplates.DEEP_DIVE_TEMPLATE
        assert "{summary}" in ReportTemplates.DEEP_DIVE_TEMPLATE
    
    def test_survey_template_exists(self):
        """测试技术巡览模板存在"""
        assert ReportTemplates.SURVEY_TEMPLATE is not None
        assert "{title}" in ReportTemplates.SURVEY_TEMPLATE
        assert "{summary}" in ReportTemplates.SURVEY_TEMPLATE
    
    def test_tutorial_template_exists(self):
        """测试实践指南模板存在"""
        assert ReportTemplates.TUTORIAL_TEMPLATE is not None
        assert "{title}" in ReportTemplates.TUTORIAL_TEMPLATE
        assert "{summary}" in ReportTemplates.TUTORIAL_TEMPLATE


class TestTemplateProcessor:
    """模板处理器测试"""
    
    def test_init(self):
        """测试初始化"""
        processor = TemplateProcessor()
        assert processor.templates is not None
        assert len(processor.templates) == 4
    
    def test_get_template(self):
        """测试获取模板"""
        processor = TemplateProcessor()
        
        # 测试有效意图
        template = processor.get_template("comparison")
        assert template == ReportTemplates.COMPARISON_TEMPLATE
        
        template = processor.get_template("deep_dive")
        assert template == ReportTemplates.DEEP_DIVE_TEMPLATE
        
        template = processor.get_template("survey")
        assert template == ReportTemplates.SURVEY_TEMPLATE
        
        template = processor.get_template("tutorial")
        assert template == ReportTemplates.TUTORIAL_TEMPLATE
        
        # 测试无效意图（应该返回默认模板）
        template = processor.get_template("invalid")
        assert template == ReportTemplates.DEEP_DIVE_TEMPLATE
    
    def test_process_template_comparison(self):
        """测试处理对比模板"""
        processor = TemplateProcessor()
        
        data = {
            'title': 'Python vs JavaScript 对比',
            'summary': '这是一份Python和JavaScript的对比报告',
            'option_a': 'Python',
            'option_b': 'JavaScript',
            'sources': '参考来源列表'
        }
        
        result = processor.process_template("comparison", data)
        
        assert "Python vs JavaScript 对比" in result
        assert "这是一份Python和JavaScript的对比报告" in result
        assert "Python" in result
        assert "JavaScript" in result
    
    def test_process_template_deep_dive(self):
        """测试处理深度解析模板"""
        processor = TemplateProcessor()
        
        data = {
            'title': 'React Hooks 深度解析',
            'summary': '这是一份React Hooks的深度解析报告',
            'core_concepts': 'React Hooks的核心概念',
            'sources': '参考来源列表'
        }
        
        result = processor.process_template("deep_dive", data)
        
        assert "React Hooks 深度解析" in result
        assert "这是一份React Hooks的深度解析报告" in result
        assert "React Hooks的核心概念" in result
    
    def test_process_template_survey(self):
        """测试处理技术巡览模板"""
        processor = TemplateProcessor()
        
        data = {
            'title': '前端框架技术巡览',
            'summary': '这是一份前端框架的技术巡览报告',
            'open_source_projects': 'React, Vue, Angular',
            'sources': '参考来源列表'
        }
        
        result = processor.process_template("survey", data)
        
        assert "前端框架技术巡览" in result
        assert "这是一份前端框架的技术巡览报告" in result
        assert "React, Vue, Angular" in result
    
    def test_process_template_tutorial(self):
        """测试处理实践指南模板"""
        processor = TemplateProcessor()
        
        data = {
            'title': 'Docker 部署指南',
            'summary': '这是一份Docker部署的实践指南',
            'system_requirements': 'Linux系统要求',
            'sources': '参考来源列表'
        }
        
        result = processor.process_template("tutorial", data)
        
        assert "Docker 部署指南" in result
        assert "这是一份Docker部署的实践指南" in result
        assert "Linux系统要求" in result
    
    def test_process_template_with_missing_fields(self):
        """测试处理模板时缺失字段的情况"""
        processor = TemplateProcessor()
        
        # 只提供部分数据
        data = {
            'title': '测试报告',
            'summary': '测试摘要'
        }
        
        # 应该不会抛出异常，会使用默认值
        result = processor.process_template("comparison", data)
        
        assert "测试报告" in result
        assert "测试摘要" in result
        # 应该包含默认值
        assert "选项A" in result or "选项B" in result
    
    def test_get_default_values(self):
        """测试获取默认值"""
        processor = TemplateProcessor()
        
        # 测试对比模板的默认值
        defaults = processor._get_default_values("comparison")
        assert "option_a" in defaults
        assert "option_b" in defaults
        assert "feature_comparison_table" in defaults
        
        # 测试深度解析模板的默认值
        defaults = processor._get_default_values("deep_dive")
        assert "core_concepts" in defaults
        assert "architecture_overview" in defaults
        
        # 测试技术巡览模板的默认值
        defaults = processor._get_default_values("survey")
        assert "open_source_projects" in defaults
        assert "commercial_products" in defaults
        
        # 测试实践指南模板的默认值
        defaults = processor._get_default_values("tutorial")
        assert "system_requirements" in defaults
        assert "software_dependencies" in defaults


if __name__ == "__main__":
    pytest.main([__file__])
