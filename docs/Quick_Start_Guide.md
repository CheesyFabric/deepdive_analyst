# 快速开始指南

## 概述

本指南将帮助您快速设置和运行 DeepDive Analyst 项目，支持多种LLM提供商。

## 1. 环境准备

### 1.1 系统要求
- Python 3.13.5
- 虚拟环境（推荐）
- 至少一个LLM提供商的API密钥

### 1.2 克隆项目
```bash
git clone <repository-url>
cd DeepDive_Analyst
```

## 2. 安装依赖

### 2.1 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

## 3. 配置环境

### 3.1 快速配置（推荐）
```bash
# 使用配置脚本
python scripts/setup_llm.py
```

### 3.2 手动配置
```bash
# 复制环境配置模板
cp env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

### 3.3 最小配置示例
```env
# 最小配置 - 使用OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-actual-openai-key-here
TAVILY_API_KEY=your-actual-tavily-key-here
```

## 4. 验证配置

### 4.1 检查配置状态
```bash
python main.py config
```

### 4.2 查看LLM提供商信息
```bash
python main.py llm
```

### 4.3 测试LLM连接
```bash
python examples/multi_llm_example.py
```

## 5. 运行第一个调研

### 5.1 基本调研
```bash
python main.py research --query "对比React和Vue的优缺点"
```

### 5.2 详细调研
```bash
python main.py research --query "深入解释Docker容器技术" --verbose --max-iterations 3
```

### 5.3 指定模板类型
```bash
python main.py research --query "盘点目前主流的机器学习框架" --template survey
```

## 6. 常用命令

### 6.1 查看帮助
```bash
python main.py --help
python main.py research --help
```

### 6.2 查看版本信息
```bash
python main.py version
```

### 6.3 查看使用示例
```bash
python main.py examples
```

### 6.4 运行测试
```bash
python main.py test
```

## 7. 切换LLM提供商

### 7.1 切换到Gemini
```bash
# 编辑 .env 文件
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-pro
GEMINI_API_KEY=your-gemini-key-here
```

### 7.2 切换到Qwen
```bash
# 编辑 .env 文件
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
QWEN_API_KEY=your-qwen-key-here
```

### 7.3 切换到Claude
```bash
# 编辑 .env 文件
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your-anthropic-key-here
```

## 8. 高级功能

### 8.1 启用LangSmith追踪
```bash
# 编辑 .env 文件
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key-here
LANGCHAIN_PROJECT=deepdive-analyst
```

### 8.2 自定义输出
```bash
python main.py research --query "你的查询" --output "custom_report.md"
```

### 8.3 调整研究参数
```bash
python main.py research --query "你的查询" --max-iterations 5 --verbose
```

## 9. 故障排除

### 9.1 常见问题

**问题**: 导入错误
```bash
# 解决方案
pip install -r requirements.txt
```

**问题**: API密钥错误
```bash
# 解决方案
python main.py config  # 检查配置状态
```

**问题**: 网络连接问题
```bash
# 解决方案
# 检查网络连接和防火墙设置
```

### 9.2 获取帮助
- 查看项目文档：`docs/` 目录
- 运行帮助命令：`python main.py --help`
- 查看配置指南：[环境配置指南](Environment_Configuration_Guide.md)

## 10. 下一步

### 10.1 探索功能
- 尝试不同的查询类型
- 测试不同的LLM提供商
- 启用LangSmith追踪

### 10.2 自定义配置
- 调整LLM参数
- 配置自定义模板
- 设置高级选项

### 10.3 贡献项目
- 报告问题
- 提交功能请求
- 贡献代码

## 11. 总结

通过本指南，您应该能够：
- ✅ 成功安装和配置项目
- ✅ 运行第一个技术调研
- ✅ 切换不同的LLM提供商
- ✅ 使用高级功能

如果遇到问题，请参考故障排除部分或查看详细文档。

祝您使用愉快！🚀
