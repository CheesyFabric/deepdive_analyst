# DeepDive Analyst

AI技术专家调研与分析智能体团队

## 项目简介

DeepDive Analyst 是一个基于多智能体协作的自动化技术调研系统。它能够针对用户提出的复杂IT技术问题，进行深入的信息检索、分析、整合，并生成结构化、高质量的调研报告。

## 核心特性

- **多智能体协作**: 系统由多个职责明确的Agent协作完成任务
- **非线性工作流**: 利用LangGraph实现"研究-批判-修正"的迭代循环
- **智能模板选择**: 根据查询意图动态选择最合适的报告模板
- **可解释的工作过程**: 支持LangSmith等工具进行可视化调试

## 技术栈

- **Agent框架**: CrewAI
- **工作流编排**: LangGraph
- **核心工具**: Tavily搜索API, Python网页抓取库
- **用户交互**: Typer命令行界面
- **可观测性**: LangSmith (可选)

## 安装与配置

### 1. 环境要求

- Python 3.13.5
- 虚拟环境 (推荐)

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置API密钥

复制 `.env.example` 文件为 `.env` 并填入真实的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下API密钥：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here

# Tavily 搜索API配置
TAVILY_API_KEY=your_tavily_api_key_here

# LangSmith 配置 (可选)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=deepdive-analyst
```

## 使用方法

### 基本用法

```bash
# 执行技术调研
python main.py research --query "对比CrewAI和Autogen在实现多智能体协作方面的异同点" --output "comparison_report.md"

# 查看帮助
python main.py --help

# 查看版本信息
python main.py version

# 查看配置信息
python main.py config

# 查看使用示例
python main.py examples

# 运行测试套件
python main.py test
```

### 高级用法

```bash
# 使用指定模板类型
python main.py research --query "对比React和Vue的优缺点" --template comparison

# 设置最大迭代次数
python main.py research --query "深入解释Docker容器技术" --max-iterations 5

# 启用详细日志
python main.py research --query "盘点目前主流的机器学习框架" --verbose

# 组合使用多个选项
python main.py research --query "如何使用Kubernetes部署应用" --template tutorial --max-iterations 3 --verbose --output "k8s_guide.md"
```

### 支持的查询类型

系统支持以下四种查询类型：

1. **对比分析** (comparison): "对比A和B的优劣"
2. **深度解析** (deep_dive): "深入解释X的工作原理"
3. **技术巡览** (survey): "盘点Y领域的主要技术"
4. **实践指南** (tutorial): "如何使用Z完成某项任务"

## 项目结构

```
DeepDive_Analyst/
├── src/
│   ├── agents/          # 智能体实现
│   ├── tools/           # 外部工具集成
│   ├── workflows/       # LangGraph工作流
│   └── configs/         # 配置文件
├── tests/               # 测试文件
├── docs/                # 项目文档
├── main.py             # 主程序入口
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```

## 开发路线图

项目按照以下阶段进行开发：

1. **阶段一**: 项目初始化与环境配置 ✅
2. **阶段二**: 核心工具与Agent的MVP实现
3. **阶段三**: 核心循环工作流搭建
4. **阶段四**: 集成智能模板机制
5. **阶段五**: 构建CLI并完成端到端整合

## 贡献指南

1. 遵循PEP 8编码规范
2. 为所有公共函数添加文档字符串
3. 使用pytest编写单元测试
4. 保持函数短小，专注于单一职责

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过GitHub Issues联系我们。
