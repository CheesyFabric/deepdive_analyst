# LangSmith 可视化实现指南

## 概述

LangSmith 是 LangChain 生态系统中的可观测性平台，为 DeepDive Analyst 项目提供强大的工作流可视化和调试功能。本指南将详细说明如何启用和配置 LangSmith，以及如何利用其可视化功能来监控和分析多智能体工作流。

## 1. LangSmith 配置与启用

### 1.1 环境变量配置

首先，需要在项目根目录创建 `.env` 文件（如果不存在）：

```bash
# 复制环境配置模板
cp .env.example .env
```

在 `.env` 文件中添加以下 LangSmith 配置：

```env
# LangSmith 配置
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=deepdive-analyst
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 1.2 获取 LangSmith API 密钥

1. 访问 [LangSmith 官网](https://smith.langchain.com/)
2. 注册并登录账户
3. 在设置页面创建 API 密钥
4. 将密钥复制到 `.env` 文件中

### 1.3 验证配置

使用以下命令验证 LangSmith 配置：

```bash
python main.py config
```

如果配置正确，您会看到：
```
✅ LangSmith API: 已配置
```

## 2. LangSmith 可视化功能详解

### 2.1 工作流执行轨迹可视化

启用 LangSmith 后，每次执行调研任务时，都会在 LangSmith 控制台中生成详细的执行轨迹：

#### 2.1.1 节点执行顺序
```
classify → plan → research → critique → (循环) → write_report
```

#### 2.1.2 状态变化追踪
- **输入状态**: `original_query`, `intent`
- **规划状态**: `plan`, `research_queries`
- **研究状态**: `researched_data`, `research_iteration`
- **批判状态**: `critique_feedback`, `needs_more_research`
- **输出状态**: `final_report`

### 2.2 Agent 协作可视化

#### 2.2.1 QueryClassifierAgent 轨迹
```json
{
  "agent": "QueryClassifierAgent",
  "input": "对比React和Vue的优缺点",
  "output": "comparison",
  "execution_time": "0.5s",
  "tokens_used": 150
}
```

#### 2.2.2 ChiefPlannerAgent 轨迹
```json
{
  "agent": "ChiefPlannerAgent",
  "input": {
    "query": "对比React和Vue的优缺点",
    "intent": "comparison"
  },
  "output": {
    "plan": "详细的研究计划...",
    "research_queries": ["React vs Vue", "性能对比", "生态系统对比"]
  },
  "execution_time": "2.1s",
  "tokens_used": 800
}
```

#### 2.2.3 WebResearcherAgent 轨迹
```json
{
  "agent": "WebResearcherAgent",
  "input": {
    "plan": "研究计划...",
    "query": "对比React和Vue的优缺点",
    "intent": "comparison"
  },
  "output": {
    "research_data": "收集到的技术信息...",
    "sources": ["source1.com", "source2.com"]
  },
  "execution_time": "15.3s",
  "tokens_used": 1200
}
```

#### 2.2.4 CriticAnalystAgent 轨迹
```json
{
  "agent": "CriticAnalystAgent",
  "input": {
    "researched_data": "研究数据...",
    "original_query": "对比React和Vue的优缺点"
  },
  "output": {
    "critique": "批判分析结果...",
    "needs_more_research": true,
    "feedback": "需要更多关于性能测试的数据"
  },
  "execution_time": "3.2s",
  "tokens_used": 900
}
```

#### 2.2.5 ReportWriterAgent 轨迹
```json
{
  "agent": "ReportWriterAgent",
  "input": {
    "researched_data": "最终研究数据...",
    "intent": "comparison",
    "original_query": "对比React和Vue的优缺点"
  },
  "output": {
    "final_report": "# React vs Vue 对比分析报告..."
  },
  "execution_time": "4.7s",
  "tokens_used": 1500
}
```

### 2.3 迭代循环可视化

#### 2.3.1 循环条件判断
```json
{
  "condition": "should_continue",
  "input": {
    "research_iteration": 2,
    "max_iterations": 3,
    "needs_more_research": true
  },
  "output": "continue",
  "reason": "批判分析认为需要更多研究"
}
```

#### 2.3.2 循环终止条件
```json
{
  "condition": "should_continue",
  "input": {
    "research_iteration": 3,
    "max_iterations": 3,
    "needs_more_research": false
  },
  "output": "finish",
  "reason": "达到最大迭代次数或研究充分"
}
```

## 3. LangSmith 控制台使用指南

### 3.1 访问 LangSmith 控制台

1. 登录 [LangSmith 控制台](https://smith.langchain.com/)
2. 选择项目：`deepdive-analyst`
3. 查看运行历史和执行轨迹

### 3.2 主要功能区域

#### 3.2.1 运行列表 (Runs)
- 显示所有执行记录
- 包含执行时间、状态、输入输出摘要
- 支持按时间、状态、Agent 筛选

#### 3.2.2 执行轨迹 (Trace)
- 详细的执行流程图
- 节点间的数据流向
- 每个步骤的执行时间
- 错误和异常信息

#### 3.2.3 性能分析 (Analytics)
- Token 使用统计
- 执行时间分析
- 成本计算
- 错误率统计

#### 3.2.4 评估 (Evaluations)
- 输出质量评估
- 自定义评估指标
- 批量评估结果

## 4. 实际使用示例

### 4.1 执行调研任务

```bash
# 启用详细日志模式
python main.py research --query "对比React和Vue的优缺点" --verbose --max-iterations 3
```

### 4.2 在 LangSmith 中查看结果

1. **打开 LangSmith 控制台**
2. **找到对应的运行记录**
3. **点击查看详细轨迹**

### 4.3 分析执行流程

#### 4.3.1 工作流概览
```
开始 → 分类 → 规划 → 研究 → 批判 → [循环] → 撰写报告 → 结束
```

#### 4.3.2 关键指标
- **总执行时间**: 25.8s
- **迭代次数**: 2
- **Token 消耗**: 4550
- **API 调用次数**: 12
- **成功率**: 100%

#### 4.3.3 性能瓶颈分析
- **最慢节点**: WebResearcherAgent (15.3s)
- **最快节点**: QueryClassifierAgent (0.5s)
- **优化建议**: 考虑并行搜索或缓存机制

## 5. 高级可视化功能

### 5.1 自定义标签和元数据

在代码中添加自定义标签：

```python
# 在 LangGraphWorkflow 中添加
def execute(self, query: str, max_iterations: int = 3) -> Dict[str, Any]:
    # 添加自定义标签
    with langsmith.trace(
        name="deepdive_research",
        tags=["research", "multi-agent", "langgraph"],
        metadata={
            "query_type": "comparison",
            "max_iterations": max_iterations,
            "user_id": "anonymous"
        }
    ):
        # 执行工作流
        final_state = self.graph.invoke(initial_state)
```

### 5.2 错误追踪和调试

#### 5.2.1 错误可视化
```json
{
  "error": {
    "type": "APIError",
    "message": "Tavily API rate limit exceeded",
    "node": "research",
    "timestamp": "2024-01-15T10:30:00Z",
    "retry_count": 3
  }
}
```

#### 5.2.2 调试信息
- 详细的错误堆栈
- 输入输出快照
- 环境变量状态
- 网络请求详情

### 5.3 性能优化建议

#### 5.3.1 基于数据的优化
- 识别最耗时的节点
- 分析 Token 使用模式
- 优化 API 调用频率
- 调整超时设置

#### 5.3.2 成本优化
- 监控 Token 消耗
- 优化 Prompt 长度
- 选择合适的模型
- 实现缓存机制

## 6. 最佳实践

### 6.1 配置建议

1. **生产环境**: 启用完整的追踪和监控
2. **开发环境**: 启用基本追踪，关闭详细日志
3. **测试环境**: 启用错误追踪，监控异常

### 6.2 安全考虑

1. **API 密钥**: 使用环境变量，不要硬编码
2. **敏感数据**: 避免在追踪中记录敏感信息
3. **访问控制**: 限制 LangSmith 项目的访问权限

### 6.3 性能考虑

1. **追踪开销**: 监控追踪对性能的影响
2. **数据存储**: 定期清理旧的追踪数据
3. **网络延迟**: 考虑 LangSmith 服务的网络延迟

## 7. 故障排除

### 7.1 常见问题

#### 7.1.1 LangSmith 未启用
**症状**: 控制台中没有执行记录
**解决方案**: 检查环境变量配置

#### 7.1.2 API 密钥无效
**症状**: 出现认证错误
**解决方案**: 重新生成并更新 API 密钥

#### 7.1.3 追踪数据不完整
**症状**: 部分节点没有追踪信息
**解决方案**: 检查 LangGraph 版本兼容性

### 7.2 调试步骤

1. **验证配置**: 使用 `python main.py config` 检查配置
2. **测试连接**: 执行简单任务验证连接
3. **查看日志**: 检查详细日志输出
4. **联系支持**: 如问题持续，联系 LangSmith 支持

## 8. 总结

LangSmith 为 DeepDive Analyst 项目提供了强大的可视化能力：

- **实时监控**: 跟踪多智能体工作流的执行过程
- **性能分析**: 识别瓶颈和优化机会
- **错误调试**: 快速定位和解决问题
- **成本控制**: 监控 Token 使用和 API 成本
- **质量评估**: 评估输出质量和系统性能

通过合理配置和使用 LangSmith，您可以更好地理解、调试和优化这个复杂的 AI 调研系统。
