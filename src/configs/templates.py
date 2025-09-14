"""
报告模板模块
包含各种类型的Markdown报告模板
"""

from typing import Dict, Any


class ReportTemplates:
    """报告模板类"""
    
    # 对比分析报告模板
    COMPARISON_TEMPLATE = """
# {title}

## 📋 摘要 (TL;DR)
{summary}

## 🔍 核心特性对比

| 特性 | {option_a} | {option_b} |
|------|------------|------------|
{feature_comparison_table}

## ✅ 优缺点分析

### {option_a}
**优点:**
{option_a_pros}

**缺点:**
{option_a_cons}

### {option_b}
**优点:**
{option_b_pros}

**缺点:**
{option_b_cons}

## 🎯 最佳应用场景

### {option_a} 适用场景
{option_a_use_cases}

### {option_b} 适用场景
{option_b_use_cases}

## 💻 代码示例

### {option_a} 示例
```python
{option_a_code_example}
```

### {option_b} 示例
```python
{option_b_code_example}
```

## 📊 性能对比
{performance_comparison}

## 🚀 迁移建议
{migration_advice}

## 📚 参考来源
{sources}
"""
    
    # 深度解析报告模板
    DEEP_DIVE_TEMPLATE = """
# {title}

## 📋 摘要 (TL;DR)
{summary}

## 🎯 核心概念与背景
{core_concepts}

## 🏗️ 关键工作机制/架构详解

### 整体架构
{architecture_overview}

### 核心组件
{core_components}

### 工作流程
{workflow_diagram}

## 💻 代码实现/伪代码示例

### 核心算法
```python
{core_algorithm}
```

### 实现细节
```python
{implementation_details}
```

## 🔧 配置与部署
{configuration_deployment}

## 📈 性能优化
{performance_optimization}

## 🌟 应用与影响

### 实际应用案例
{real_world_applications}

### 行业影响
{industry_impact}

## 🔮 未来发展趋势
{future_trends}

## ⚠️ 注意事项与限制
{limitations_considerations}

## 📚 参考来源
{sources}
"""
    
    # 技术巡览报告模板
    SURVEY_TEMPLATE = """
# {title}

## 📋 摘要 (TL;DR)
{summary}

## 🏢 主要参与者/项目列表

### 开源项目
{open_source_projects}

### 商业产品
{commercial_products}

### 学术研究
{academic_research}

## 📊 分类与归纳

### 按许可证分类
{license_categorization}

### 按架构分类
{architecture_categorization}

### 按应用领域分类
{domain_categorization}

## 🔍 关键特性对比矩阵

| 项目/产品 | 特性1 | 特性2 | 特性3 | 特性4 | 评分 |
|-----------|-------|-------|-------|-------|------|
{feature_comparison_matrix}

## 📈 市场趋势分析
{market_trends}

## 🚀 技术创新点
{innovation_points}

## 🔮 未来趋势展望

### 短期趋势 (1-2年)
{short_term_trends}

### 中期趋势 (3-5年)
{medium_term_trends}

### 长期趋势 (5年以上)
{long_term_trends}

## 💡 选择建议
{selection_recommendations}

## 📚 参考来源
{sources}
"""
    
    # 实践指南报告模板
    TUTORIAL_TEMPLATE = """
# {title}

## 📋 摘要 (TL;DR)
{summary}

## 🛠️ 前置准备与环境要求

### 系统要求
{system_requirements}

### 软件依赖
{software_dependencies}

### 环境配置
{environment_setup}

## 📝 分步操作指南

### 步骤 1: {step1_title}
{step1_content}

### 步骤 2: {step2_title}
{step2_content}

### 步骤 3: {step3_title}
{step3_content}

### 步骤 4: {step4_title}
{step4_content}

### 步骤 5: {step5_title}
{step5_content}

## 🔧 完整代码示例

### 主程序
```python
{main_code_example}
```

### 配置文件
```yaml
{config_example}
```

### 测试代码
```python
{test_code_example}
```

## ❓ 常见问题与解决方案

### Q1: {question1}
**A:** {answer1}

### Q2: {question2}
**A:** {answer2}

### Q3: {question3}
**A:** {answer3}

## ⚠️ 注意事项
{important_notes}

## 🚀 进阶技巧
{advanced_tips}

## 📊 性能优化建议
{performance_tips}

## 🔗 相关资源
{related_resources}

## 📚 参考来源
{sources}
"""


class TemplateProcessor:
    """模板处理器类"""
    
    def __init__(self):
        """初始化模板处理器"""
        self.templates = {
            'comparison': ReportTemplates.COMPARISON_TEMPLATE,
            'deep_dive': ReportTemplates.DEEP_DIVE_TEMPLATE,
            'survey': ReportTemplates.SURVEY_TEMPLATE,
            'tutorial': ReportTemplates.TUTORIAL_TEMPLATE
        }
    
    def get_template(self, intent: str) -> str:
        """
        根据意图获取对应的模板
        
        Args:
            intent: 查询意图
            
        Returns:
            对应的模板字符串
        """
        return self.templates.get(intent, self.templates['deep_dive'])
    
    def process_template(self, intent: str, data: Dict[str, Any]) -> str:
        """
        处理模板，填充数据
        
        Args:
            intent: 查询意图
            data: 要填充的数据
            
        Returns:
            处理后的报告内容
        """
        template = self.get_template(intent)
        
        # 为缺失的字段提供默认值
        default_values = self._get_default_values(intent)
        for key, value in default_values.items():
            if key not in data:
                data[key] = value
        
        try:
            return template.format(**data)
        except KeyError as e:
            # 如果模板中有未提供的字段，使用占位符
            return template.format(**{k: v if k in data else f"[{k}]" for k, v in data.items()})
    
    def _get_default_values(self, intent: str) -> Dict[str, str]:
        """
        获取默认值
        
        Args:
            intent: 查询意图
            
        Returns:
            默认值字典
        """
        defaults = {
            'title': '技术调研报告',
            'summary': '本报告提供了详细的技术调研结果。',
            'sources': '本报告基于网络搜索和公开资料整理而成。'
        }
        
        if intent == 'comparison':
            defaults.update({
                'option_a': '选项A',
                'option_b': '选项B',
                'feature_comparison_table': '| 特性 | 选项A | 选项B |\n|------|-------|-------|\n| 特性1 | 值A1 | 值B1 |\n| 特性2 | 值A2 | 值B2 |',
                'option_a_pros': '- 优点1\n- 优点2',
                'option_a_cons': '- 缺点1\n- 缺点2',
                'option_b_pros': '- 优点1\n- 优点2',
                'option_b_cons': '- 缺点1\n- 缺点2',
                'option_a_use_cases': '- 场景1\n- 场景2',
                'option_b_use_cases': '- 场景1\n- 场景2',
                'option_a_code_example': '# 选项A代码示例\nprint("Hello from A")',
                'option_b_code_example': '# 选项B代码示例\nprint("Hello from B")',
                'performance_comparison': '性能对比分析结果',
                'migration_advice': '迁移建议和注意事项'
            })
        elif intent == 'deep_dive':
            defaults.update({
                'core_concepts': '核心概念和背景介绍',
                'architecture_overview': '整体架构概述',
                'core_components': '核心组件说明',
                'workflow_diagram': '工作流程图',
                'core_algorithm': '# 核心算法\n# 算法实现代码',
                'implementation_details': '# 实现细节\n# 详细实现代码',
                'configuration_deployment': '配置和部署说明',
                'performance_optimization': '性能优化建议',
                'real_world_applications': '实际应用案例',
                'industry_impact': '行业影响分析',
                'future_trends': '未来发展趋势',
                'limitations_considerations': '注意事项和限制'
            })
        elif intent == 'survey':
            defaults.update({
                'open_source_projects': '开源项目列表',
                'commercial_products': '商业产品列表',
                'academic_research': '学术研究列表',
                'license_categorization': '按许可证分类',
                'architecture_categorization': '按架构分类',
                'domain_categorization': '按应用领域分类',
                'feature_comparison_matrix': '| 项目 | 特性1 | 特性2 | 特性3 | 特性4 | 评分 |\n|------|-------|-------|-------|-------|------|\n| 项目A | ✓ | ✗ | ✓ | ✗ | 8/10 |',
                'market_trends': '市场趋势分析',
                'innovation_points': '技术创新点',
                'short_term_trends': '短期趋势',
                'medium_term_trends': '中期趋势',
                'long_term_trends': '长期趋势',
                'selection_recommendations': '选择建议'
            })
        elif intent == 'tutorial':
            defaults.update({
                'system_requirements': '系统要求说明',
                'software_dependencies': '软件依赖列表',
                'environment_setup': '环境配置步骤',
                'step1_title': '准备环境',
                'step1_content': '第一步详细说明',
                'step2_title': '安装依赖',
                'step2_content': '第二步详细说明',
                'step3_title': '配置设置',
                'step3_content': '第三步详细说明',
                'step4_title': '运行测试',
                'step4_content': '第四步详细说明',
                'step5_title': '部署应用',
                'step5_content': '第五步详细说明',
                'main_code_example': '# 主程序代码\nprint("Hello World")',
                'config_example': '# 配置文件\ndebug: true\nport: 8080',
                'test_code_example': '# 测试代码\ndef test_function():\n    assert True',
                'question1': '常见问题1',
                'answer1': '问题1的答案',
                'question2': '常见问题2',
                'answer2': '问题2的答案',
                'question3': '常见问题3',
                'answer3': '问题3的答案',
                'important_notes': '重要注意事项',
                'advanced_tips': '进阶技巧',
                'performance_tips': '性能优化建议',
                'related_resources': '相关资源链接'
            })
        
        return defaults


# 全局模板处理器实例
template_processor = TemplateProcessor()
