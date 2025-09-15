# 环境配置指南

## 概述

本文档详细说明如何配置 DeepDive Analyst 项目的环境变量，特别是多LLM提供商的支持。

## 1. 环境配置文件

### 1.1 配置文件位置
- **模板文件**: `env.example` - 包含所有配置项的模板
- **实际配置**: `.env` - 用户的实际配置文件（需要手动创建）

### 1.2 创建配置文件
```bash
# 复制模板文件
cp env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

## 2. LLM提供商配置

### 2.1 基础LLM配置
```env
# LLM 提供商配置
LLM_PROVIDER=openai                    # 提供商: openai, gemini, qwen, anthropic
LLM_MODEL=gpt-4o-mini                 # 模型名称
LLM_TEMPERATURE=0.1                   # 温度参数 (0.0-2.0)
LLM_MAX_TOKENS=4000                   # 最大Token数
LLM_TIMEOUT=30                        # 超时时间(秒)
LLM_MAX_RETRIES=3                     # 最大重试次数

# LLM 基础URL配置（用于自定义部署）
LLM_BASE_URL=                         # 可选，用于私有部署
```

### 2.2 OpenAI配置
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

**支持的模型**:
- `gpt-4o` - GPT-4 Omni
- `gpt-4o-mini` - GPT-4 Omni Mini (推荐)
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-4` - GPT-4
- `gpt-3.5-turbo` - GPT-3.5 Turbo

**获取API密钥**: https://platform.openai.com/api-keys

### 2.3 Google Gemini配置
```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-1.5-pro
GEMINI_API_KEY=your_gemini_api_key_here
```

**支持的模型**:
- `gemini/gemini-1.5-pro` - Gemini 1.5 Pro (推荐)
- `gemini/gemini-1.5-flash` - Gemini 1.5 Flash
- `gemini/gemini-1.0-pro` - Gemini 1.0 Pro

**获取API密钥**: https://makersuite.google.com/app/apikey

### 2.4 阿里通义千问配置
```env
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
QWEN_API_KEY=your_qwen_api_key_here
```

**支持的模型**:
- `qwen-max` - Qwen Max (推荐)
- `qwen-plus` - Qwen Plus
- `qwen-turbo` - Qwen Turbo
- `qwen2-turbo` - Qwen2 Turbo
- `qwen2-plus` - Qwen2 Plus
- `qwen2-max` - Qwen2 Max

**获取API密钥**: https://dashscope.console.aliyun.com/

### 2.5 Anthropic Claude配置
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**支持的模型**:
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet (推荐)
- `claude-3-5-haiku-20241022` - Claude 3.5 Haiku
- `claude-3-opus-20240229` - Claude 3 Opus
- `claude-3-sonnet-20240229` - Claude 3 Sonnet
- `claude-3-haiku-20240307` - Claude 3 Haiku

**获取API密钥**: https://console.anthropic.com/

## 3. 其他服务配置

### 3.1 Tavily搜索API
```env
TAVILY_API_KEY=your_tavily_api_key_here
```

**获取API密钥**: https://tavily.com/

### 3.2 LangSmith配置（可选）
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=deepdive-analyst
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

**获取API密钥**: https://smith.langchain.com/

## 4. 应用配置

### 4.1 搜索配置
```env
MAX_SEARCH_RESULTS=10                 # 最大搜索结果数
SEARCH_TIMEOUT=30                     # 搜索超时时间(秒)
```

### 4.2 报告配置
```env
DEFAULT_OUTPUT_FILE=report.md         # 默认输出文件名
MAX_REPORT_LENGTH=10000               # 最大报告长度
```

## 5. 配置示例

### 5.1 完整配置示例
```env
# DeepDive Analyst 环境配置
# 请填入真实的 API 密钥

# LLM 提供商配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# LLM 基础URL配置（用于自定义部署）
LLM_BASE_URL=

# OpenAI API 配置
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Google Gemini API 配置
GEMINI_API_KEY=your-actual-gemini-key-here

# 阿里通义千问 API 配置
QWEN_API_KEY=your-actual-qwen-key-here

# Anthropic Claude API 配置
ANTHROPIC_API_KEY=your-actual-anthropic-key-here

# Tavily 搜索API配置
TAVILY_API_KEY=your-actual-tavily-key-here

# LangSmith 配置 (可选，但强烈推荐)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-actual-langsmith-key-here
LANGCHAIN_PROJECT=deepdive-analyst
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# 搜索配置
MAX_SEARCH_RESULTS=10
SEARCH_TIMEOUT=30

# 报告配置
DEFAULT_OUTPUT_FILE=report.md
MAX_REPORT_LENGTH=10000
```

### 5.2 最小配置示例（仅OpenAI）
```env
# 最小配置 - 仅使用OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-actual-openai-key-here
TAVILY_API_KEY=your-actual-tavily-key-here
```

## 6. 配置验证

### 6.1 检查配置
```bash
# 检查当前配置
python main.py config

# 查看LLM提供商信息
python main.py llm
```

### 6.2 测试配置
```bash
# 运行多LLM示例
python examples/multi_llm_example.py

# 执行测试调研
python main.py research --query "测试查询" --verbose
```

## 7. 常见问题

### 7.1 配置问题
**Q: 如何切换LLM提供商？**
A: 修改 `.env` 文件中的 `LLM_PROVIDER` 和对应的API密钥。

**Q: 如何验证配置是否正确？**
A: 运行 `python main.py config` 检查配置状态。

**Q: 支持自定义部署的LLM吗？**
A: 是的，通过设置 `LLM_BASE_URL` 可以支持自定义部署。

### 7.2 API密钥问题
**Q: API密钥在哪里获取？**
A: 各提供商的官方文档中都有详细的获取步骤。

**Q: API密钥安全吗？**
A: 是的，API密钥存储在本地 `.env` 文件中，不会被提交到版本控制。

**Q: 可以同时配置多个提供商吗？**
A: 可以，但一次只能使用一个提供商。

### 7.3 性能问题
**Q: 如何优化LLM性能？**
A: 调整 `LLM_TEMPERATURE`、`LLM_MAX_TOKENS` 等参数。

**Q: 如何减少API调用成本？**
A: 使用较小的模型，减少 `LLM_MAX_TOKENS`，优化提示词。

## 8. 最佳实践

### 8.1 安全实践
- 永远不要将API密钥提交到版本控制
- 定期轮换API密钥
- 使用环境变量管理敏感信息

### 8.2 性能优化
- 根据任务选择合适的模型
- 调整温度参数以获得最佳结果
- 监控Token使用情况

### 8.3 成本控制
- 使用较小的模型进行测试
- 设置合理的Token限制
- 监控API使用情况

## 9. 故障排除

### 9.1 配置错误
```bash
# 检查环境变量是否正确加载
python -c "from src.configs.config import Config; print(Config.get_llm_config())"
```

### 9.2 API错误
- 检查API密钥是否正确
- 确认API配额是否充足
- 检查网络连接

### 9.3 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt
```

## 10. 总结

通过正确配置环境变量，您可以：
- 灵活切换不同的LLM提供商
- 优化性能和成本
- 确保系统的安全性和稳定性

建议使用配置脚本 `python scripts/setup_llm.py` 来快速设置环境配置。
