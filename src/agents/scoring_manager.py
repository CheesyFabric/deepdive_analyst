"""
评分管理模块
实现动态评分调整、渐进式批判标准和信息质量评估
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from loguru import logger
import re
import math


@dataclass
class ScoringCriteria:
    """评分标准数据类"""
    completeness_weight: float = 0.4
    accuracy_weight: float = 0.3
    consistency_weight: float = 0.2
    relevance_weight: float = 0.1
    
    # 迭代调整参数
    iteration_bonus: float = 0.0  # 迭代奖励
    complexity_factor: float = 1.0  # 复杂度因子


@dataclass
class QualityMetrics:
    """信息质量指标"""
    information_density: float  # 信息密度 (0-1)
    consistency_score: float   # 一致性评分 (0-1)
    completeness_score: float   # 完整性评分 (0-1)
    relevance_score: float     # 相关性评分 (0-1)
    contradiction_count: int   # 矛盾数量
    coverage_ratio: float      # 覆盖率 (0-1)


class DynamicScoringManager:
    """动态评分管理器"""
    
    def __init__(self):
        """初始化评分管理器"""
        self.scoring_history: List[Dict[str, Any]] = []
        logger.info("动态评分管理器初始化成功")
    
    def calculate_dynamic_score(self, 
                              base_scores: Dict[str, int], 
                              iteration: int, 
                              research_data: str,
                              original_query: str) -> Dict[str, Any]:
        """
        计算动态调整后的评分
        
        Args:
            base_scores: 基础评分字典
            iteration: 当前迭代次数
            research_data: 研究数据
            original_query: 原始查询
            
        Returns:
            调整后的评分结果
        """
        logger.info(f"计算第{iteration}轮动态评分")
        
        # 获取质量指标
        quality_metrics = self._assess_information_quality(research_data, original_query, iteration)
        
        # 获取渐进式批判标准
        critique_standards = self._get_progressive_critique_standards(iteration)
        
        # 计算调整因子
        adjustment_factors = self._calculate_adjustment_factors(iteration, quality_metrics)
        
        # 应用动态调整
        adjusted_scores = self._apply_dynamic_adjustment(base_scores, adjustment_factors)
        
        # 计算综合评分
        overall_score = self._calculate_overall_score(adjusted_scores, quality_metrics)
        
        # 决定是否需要更多研究
        needs_more_research = self._determine_research_continuation(
            overall_score, iteration, quality_metrics, critique_standards
        )
        
        result = {
            'completeness_score': adjusted_scores['completeness'],
            'accuracy_score': adjusted_scores['accuracy'],
            'overall_score': overall_score,
            'needs_more_research': needs_more_research,
            'quality_metrics': quality_metrics,
            'adjustment_factors': adjustment_factors,
            'critique_standards': critique_standards,
            'iteration': iteration
        }
        
        # 记录评分历史
        self.scoring_history.append(result)
        
        logger.info(f"第{iteration}轮评分: 完整性={adjusted_scores['completeness']}, "
                   f"准确性={adjusted_scores['accuracy']}, 综合={overall_score}")
        
        return result
    
    def _assess_information_quality(self, 
                                  research_data: str, 
                                  original_query: str, 
                                  iteration: int) -> QualityMetrics:
        """
        评估信息质量
        
        Args:
            research_data: 研究数据
            original_query: 原始查询
            iteration: 迭代次数
            
        Returns:
            质量指标
        """
        # 计算信息密度
        information_density = self._calculate_information_density(research_data)
        
        # 计算一致性评分
        consistency_score = self._calculate_consistency_score(research_data)
        
        # 计算完整性评分
        completeness_score = self._calculate_completeness_score(research_data, original_query)
        
        # 计算相关性评分
        relevance_score = self._calculate_relevance_score(research_data, original_query)
        
        # 计算矛盾数量
        contradiction_count = self._count_contradictions(research_data)
        
        # 计算覆盖率
        coverage_ratio = self._calculate_coverage_ratio(research_data, original_query)
        
        return QualityMetrics(
            information_density=information_density,
            consistency_score=consistency_score,
            completeness_score=completeness_score,
            relevance_score=relevance_score,
            contradiction_count=contradiction_count,
            coverage_ratio=coverage_ratio
        )
    
    def _calculate_information_density(self, research_data: str) -> float:
        """计算信息密度"""
        if not research_data.strip():
            return 0.0
        
        # 计算有效信息比例
        lines = research_data.split('\n')
        meaningful_lines = [line for line in lines if len(line.strip()) > 10]
        
        # 计算技术术语密度
        tech_terms = len(re.findall(r'\b[A-Z][a-zA-Z]*[A-Z][a-zA-Z]*\b', research_data))
        total_words = len(research_data.split())
        
        density = (len(meaningful_lines) / len(lines)) * 0.6 + (tech_terms / max(total_words, 1)) * 0.4
        return min(density, 1.0)
    
    def _calculate_consistency_score(self, research_data: str) -> float:
        """计算一致性评分"""
        if not research_data.strip():
            return 0.0
        
        # 检测矛盾表述
        contradiction_patterns = [
            r'(但是|然而|不过|但是|however|but)',
            r'(相反|相反地|on the contrary)',
            r'(不一致|矛盾|inconsistent|contradict)',
            r'(错误|错误地|incorrect|wrong)'
        ]
        
        contradiction_count = sum(len(re.findall(pattern, research_data, re.IGNORECASE)) 
                                for pattern in contradiction_patterns)
        
        # 计算一致性评分 (矛盾越少，一致性越高)
        consistency = max(0.0, 1.0 - (contradiction_count * 0.1))
        return min(consistency, 1.0)
    
    def _calculate_completeness_score(self, research_data: str, original_query: str) -> float:
        """计算完整性评分"""
        if not research_data.strip():
            return 0.0
        
        # 提取查询中的关键概念
        query_concepts = self._extract_key_concepts(original_query)
        
        # 检查研究数据中是否包含这些概念
        covered_concepts = 0
        for concept in query_concepts:
            if concept.lower() in research_data.lower():
                covered_concepts += 1
        
        # 计算覆盖率
        coverage = covered_concepts / max(len(query_concepts), 1)
        
        # 考虑信息长度
        length_factor = min(len(research_data) / 1000, 1.0)  # 1000字符为基准
        
        completeness = coverage * 0.7 + length_factor * 0.3
        return min(completeness, 1.0)
    
    def _calculate_relevance_score(self, research_data: str, original_query: str) -> float:
        """计算相关性评分"""
        if not research_data.strip():
            return 0.0
        
        # 提取查询关键词
        query_keywords = self._extract_keywords(original_query)
        
        # 计算关键词在研究数据中的出现频率
        relevance_score = 0.0
        for keyword in query_keywords:
            if keyword.lower() in research_data.lower():
                relevance_score += 1
        
        relevance = relevance_score / max(len(query_keywords), 1)
        return min(relevance, 1.0)
    
    def _count_contradictions(self, research_data: str) -> int:
        """计算矛盾数量"""
        contradiction_indicators = [
            '但是', '然而', '不过', '但是', 'however', 'but',
            '相反', '相反地', 'on the contrary',
            '不一致', '矛盾', 'inconsistent', 'contradict',
            '错误', '错误地', 'incorrect', 'wrong'
        ]
        
        count = 0
        for indicator in contradiction_indicators:
            count += len(re.findall(re.escape(indicator), research_data, re.IGNORECASE))
        
        return count
    
    def _calculate_coverage_ratio(self, research_data: str, original_query: str) -> float:
        """计算覆盖率"""
        query_concepts = self._extract_key_concepts(original_query)
        covered_concepts = sum(1 for concept in query_concepts 
                             if concept.lower() in research_data.lower())
        
        return covered_concepts / max(len(query_concepts), 1)
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """提取关键概念"""
        # 提取技术术语
        tech_patterns = [
            r'\b[A-Z][a-zA-Z]*[A-Z][a-zA-Z]*\b',  # CamelCase
            r'\b[a-z]+-[a-z]+\b',  # kebab-case
            r'\b[a-z]+_[a-z]+\b',  # snake_case
        ]
        
        concepts = []
        for pattern in tech_patterns:
            concepts.extend(re.findall(pattern, text))
        
        # 提取重要名词
        important_nouns = re.findall(r'\b(?:技术|框架|工具|平台|系统|方法|算法|模型|架构|设计|实现|开发|部署|管理|优化|性能|安全|测试|监控|分析|处理|存储|网络|数据库|API|接口|服务|应用|程序|代码|软件|硬件|设备|环境|配置|设置|参数|变量|函数|类|对象|数据|信息|内容|文档|报告|结果|效果|影响|优势|缺点|问题|挑战|解决方案|最佳实践|经验|案例|示例|教程|指南|手册|规范|标准|协议|格式|类型|结构|流程|步骤|过程|阶段|周期|时间|空间|资源|成本|效率|质量|可靠性|可用性|扩展性|兼容性|稳定性|灵活性|易用性|可维护性|可读性|可测试性|可重用性|可移植性|可扩展性|可配置性|可定制性|可集成性|可操作性|可管理性|可监控性|可分析性|可预测性|可控制性|可调节性|可优化性|可改进性|可升级性|可更新性|可修复性|可恢复性|可备份性|可恢复性|可复制性|可分发性|可传播性|可分享性|可协作性|可沟通性|可理解性|可学习性|可掌握性|可应用性|可实践性|可操作性|可执行性|可实施性|可实现性|可完成性|可达成性|可成功性|可有效性|可有用性|可价值性|可意义性|可重要性|可关键性|可核心性|可基础性|可根本性|可本质性|可核心性|可关键性|可重要性|可价值性|可意义性|可有用性|可有效性|可成功性|可达成性|可完成性|可实现性|可实施性|可执行性|可操作性|可实践性|可应用性|可掌握性|可学习性|可理解性|可沟通性|可协作性|可分享性|可传播性|可分发性|可复制性|可恢复性|可备份性|可恢复性|可修复性|可更新性|可升级性|可改进性|可优化性|可调节性|可控制性|可预测性|可分析性|可监控性|可管理性|可操作性|可集成性|可定制性|可配置性|可扩展性|可移植性|可重用性|可测试性|可读性|可维护性|易用性|灵活性|稳定性|兼容性|扩展性|可用性|可靠性|质量|效率|成本|资源|空间|时间|周期|阶段|过程|步骤|流程|结构|类型|格式|协议|标准|规范|手册|指南|教程|示例|案例|经验|最佳实践|解决方案|挑战|问题|缺点|优势|影响|效果|结果|报告|文档|内容|信息|数据|对象|类|函数|变量|参数|设置|配置|环境|设备|硬件|软件|代码|程序|应用|服务|接口|API|数据库|网络|存储|处理|分析|监控|测试|安全|性能|优化|管理|部署|开发|实现|设计|架构|模型|算法|方法|平台|工具|框架|技术)\b', text, re.IGNORECASE)
        
        return list(set(concepts + important_nouns))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '但', '然而', '不过', '但是', 
                     'the', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'and', 'or', 'but'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]  # 返回前10个关键词
    
    def _get_progressive_critique_standards(self, iteration: int) -> Dict[str, Any]:
        """
        获取渐进式批判标准
        
        Args:
            iteration: 迭代次数
            
        Returns:
            批判标准字典
        """
        if iteration == 1:
            return {
                'focus': '基础信息完整性',
                'threshold': 6,
                'tolerance': 0.8,  # 容忍度
                'emphasis': 'completeness'
            }
        elif iteration == 2:
            return {
                'focus': '信息准确性',
                'threshold': 7,
                'tolerance': 0.7,
                'emphasis': 'accuracy'
            }
        elif iteration == 3:
            return {
                'focus': '深度分析',
                'threshold': 8,
                'tolerance': 0.6,
                'emphasis': 'consistency'
            }
        else:
            return {
                'focus': '综合质量',
                'threshold': 8,
                'tolerance': 0.5,
                'emphasis': 'overall'
            }
    
    def _calculate_adjustment_factors(self, 
                                    iteration: int, 
                                    quality_metrics: QualityMetrics) -> Dict[str, float]:
        """
        计算调整因子
        
        Args:
            iteration: 迭代次数
            quality_metrics: 质量指标
            
        Returns:
            调整因子字典
        """
        # 基础调整因子
        base_factors = {
            'iteration_bonus': 0.0,
            'complexity_penalty': 0.0,
            'consistency_bonus': 0.0,
            'density_bonus': 0.0
        }
        
        # 迭代奖励 (前两轮给予奖励)
        if iteration <= 2:
            base_factors['iteration_bonus'] = (3 - iteration) * 0.5
        
        # 复杂度惩罚 (信息越多，要求越严格)
        if iteration > 2:
            base_factors['complexity_penalty'] = (iteration - 2) * 0.2
        
        # 一致性奖励
        if quality_metrics.consistency_score > 0.8:
            base_factors['consistency_bonus'] = 0.3
        elif quality_metrics.consistency_score > 0.6:
            base_factors['consistency_bonus'] = 0.1
        
        # 信息密度奖励
        if quality_metrics.information_density > 0.7:
            base_factors['density_bonus'] = 0.2
        elif quality_metrics.information_density > 0.5:
            base_factors['density_bonus'] = 0.1
        
        return base_factors
    
    def _apply_dynamic_adjustment(self, 
                                base_scores: Dict[str, int], 
                                adjustment_factors: Dict[str, float]) -> Dict[str, int]:
        """
        应用动态调整
        
        Args:
            base_scores: 基础评分
            adjustment_factors: 调整因子
            
        Returns:
            调整后的评分
        """
        adjusted_scores = {}
        
        for score_type, base_score in base_scores.items():
            # 计算总调整量
            total_adjustment = (
                adjustment_factors['iteration_bonus'] +
                adjustment_factors['consistency_bonus'] +
                adjustment_factors['density_bonus'] -
                adjustment_factors['complexity_penalty']
            )
            
            # 应用调整
            adjusted_score = base_score + total_adjustment
            
            # 确保评分在1-10范围内
            adjusted_score = max(1, min(10, round(adjusted_score)))
            
            adjusted_scores[score_type] = adjusted_score
        
        return adjusted_scores
    
    def _calculate_overall_score(self, 
                                adjusted_scores: Dict[str, int], 
                                quality_metrics: QualityMetrics) -> float:
        """
        计算综合评分
        
        Args:
            adjusted_scores: 调整后的评分
            quality_metrics: 质量指标
            
        Returns:
            综合评分
        """
        # 权重配置
        weights = {
            'completeness': 0.3,
            'accuracy': 0.3,
            'consistency': 0.2,
            'relevance': 0.2
        }
        
        # 计算加权平均
        overall_score = (
            adjusted_scores['completeness'] * weights['completeness'] +
            adjusted_scores['accuracy'] * weights['accuracy'] +
            quality_metrics.consistency_score * 10 * weights['consistency'] +
            quality_metrics.relevance_score * 10 * weights['relevance']
        )
        
        return round(overall_score, 1)
    
    def _determine_research_continuation(self, 
                                       overall_score: float, 
                                       iteration: int, 
                                       quality_metrics: QualityMetrics,
                                       critique_standards: Dict[str, Any]) -> bool:
        """
        决定是否需要继续研究
        
        Args:
            overall_score: 综合评分
            iteration: 迭代次数
            quality_metrics: 质量指标
            critique_standards: 批判标准
            
        Returns:
            是否需要更多研究
        """
        threshold = critique_standards['threshold']
        tolerance = critique_standards['tolerance']
        
        # 调整阈值
        adjusted_threshold = threshold * tolerance
        
        # 如果评分低于调整后的阈值，需要更多研究
        if overall_score < adjusted_threshold:
            return True
        
        # 如果矛盾太多，需要更多研究
        if quality_metrics.contradiction_count > 3:
            return True
        
        # 如果覆盖率太低，需要更多研究
        if quality_metrics.coverage_ratio < 0.6:
            return True
        
        # 如果已经达到最大迭代次数，停止研究
        if iteration >= 3:
            return False
        
        return False
    
    def get_scoring_trend(self) -> Dict[str, Any]:
        """
        获取评分趋势分析
        
        Returns:
            评分趋势信息
        """
        if len(self.scoring_history) < 2:
            return {'trend': 'insufficient_data', 'analysis': '需要更多数据来分析趋势'}
        
        scores = [entry['overall_score'] for entry in self.scoring_history]
        
        # 计算趋势
        if len(scores) >= 2:
            trend_direction = 'improving' if scores[-1] > scores[0] else 'declining'
            trend_strength = abs(scores[-1] - scores[0])
        else:
            trend_direction = 'stable'
            trend_strength = 0
        
        return {
            'trend': trend_direction,
            'strength': trend_strength,
            'scores': scores,
            'analysis': f"评分趋势: {trend_direction}, 变化强度: {trend_strength:.1f}"
        }
