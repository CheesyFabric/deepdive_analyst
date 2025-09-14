# Project\_Plan

## 目录

- [项目总结：DeepDive Analyst](#项目总结DeepDive-Analyst)
  - [1. 项目名称](#1-项目名称)
  - [2. 项目构想 ](#2-项目构想-)
  - [3. 核心功能与亮点 (Core Features & Highlights)](#3-核心功能与亮点-Core-Features--Highlights)
  - [4. 技术栈 (Tech Stack)](#4-技术栈-Tech-Stack)
  - [5. 项目配置](#5-项目配置)
  - [6. 具体实现方法与步骤 (Implementation Method & Steps)](#6-具体实现方法与步骤-Implementation-Method--Steps)
  - [7. 最终交付成果 (Final Deliverable)](#7-最终交付成果-Final-Deliverable)
  - [8. 错误处理与日志记录 (Error Handling & Logging)](#8-错误处理与日志记录-Error-Handling--Logging)
- [如何实现智能模板选择机制](#如何实现智能模板选择机制)
  - [第一步：定义多种报告模板](#第一步定义多种报告模板)
  - [第二步：创建“查询意图分类”Agent](#第二步创建查询意图分类Agent)
  - [第三步：在LangGraph中实现动态路由](#第三步在LangGraph中实现动态路由)
- [如何定义Agent角色和工作流 (使用CrewAI + LangGraph)](#如何定义Agent角色和工作流-使用CrewAI--LangGraph)

### **项目总结：DeepDive Analyst**

#### 1. 项目名称

**DeepDive Analyst**: AI技术专家调研与分析智能体团队。

#### 2. 项目构想&#x20;

- **功能目标**: 构建一个自动化的、基于多智能体协作的系统，能够针对用户提出的复杂IT技术问题，进行深入的信息检索、分析、整合，并生成一份结构化、高质量的调研报告。这是一个专注于IT技术领域深度调研的Multi-Agent系统。用户可以提出一个具有开放性和比较性的问题，例如：“详细对比一下CrewAI和Autogen在实现多智能体协作方面的异同点和各自的最佳应用场景”，或者“调研一下目前最主流的几个开源LLM模型在代码生成能力上的表现，并提供一个总结报告”。

#### 3. 核心功能与亮点 (Core Features & Highlights)

- **多智能体协作**: 系统由多个职责明确的Agent（如意图分类、规划、研究、批判、撰写报告）协作完成任务，展示了清晰的模块化设计。
- **非线性工作流**: 利用LangGraph实现“**研究-批判-修正**”的迭代循环，模拟了专家进行研究时的真实思考过程，是项目技术深度的核心体现。
- **智能模板选择**: 系统能首先理解用户的**查询意图**（如“对比” vs “深度解析”），并动态选择最合适的报告模板进行内容生成，使输出结果更具针对性和专业性。
- **可解释的工作过程**: 整个复杂的内部工作流可以通过LangSmith等工具进行可视化，便于调试，也极具面试演示价值。

#### 4. 技术栈 (Tech Stack)

- **Agent框架**: CrewAI
- **工作流编排**: LangGraph
- **核心工具**: 搜索引擎API (如Tavily), Python网页抓取库
- **用户交互**: 命令行界面库 (Python`argparse`或`Typer`)
- **可观测性**: LangSmith (可选，但强烈推荐)

#### 5. 项目配置

- **API密钥**: 通过`.env`文件加载。
- **LLM模型**: 在`config.py`中定义，例如`LLM_MODEL = "Deepseek-R1"`，方便未来切换模型。
- **Agent Prompts**: 建议将所有Agent的`role`,`goal`,`backstory`以及分类器的Prompt都统一放在`config.py`或一个YAML文件中进行管理，而不是硬编码在代码里。

***

#### 6. 具体实现方法与步骤 (Implementation Method & Steps)

这是一个完整的端到端工作流程：

**第零步：用户交互 (Interaction)**

- 用户通过**命令行界面 (CLI)** 启动任务。
- 命令格式: `python main.py research --query "你的研究问题" --output "report.md"`

**第一步：意图识别与模板选择 (Intent Classification & Template Selection)**

- `Query_Classifier_Agent` （查询意图分类员）首先接收用户的查询，它将查询分类为预定义的类型之一（`comparison`,`deep_dive`,`survey`,`tutorial`），输出一个标准化的分类标签。
- 分类结果（例如`intent = "comparison"`）被存入LangGraph的全局状态（State）中，供后续步骤使用。
- **实现**: 这是一个简单的分类任务，非常适合用LLM完成。你可以给它一个这样的Prompt:
  ```markdown 
  你是一个AI助手，负责将用户的技术查询分类到以下四种类型之一：
  1. comparison: 当用户明确要求比较两个或多个事物时。
  2. deep_dive: 当用户要求深入解释单个概念、技术或项目时。
  3. survey: 当用户要求盘点或调研某个领域的主要参与者或技术时。
  4. tutorial: 当用户询问如何完成某项具体的技术任务时。

  请只输出最终的分类标签，不要有任何其他解释。

  用户查询: "{{query}}"

  分类标签:
  ```


**第二步：规划分解 (Planning & Decomposition)**

- `Chief_Planner_Agent`  (首席规划师)  接收用户查询，并将其分解成一个高层次、结构化的研究计划（例如，需要搜索哪些关键词，需要关注哪些方面）。

**第三步：迭代式研究与批判循环 (Iterative Research & Critique Loop -项目核心**)

- 此步骤在LangGraph中通过一个循环结构实现。
- **a. 研究 (Research)**:`Web_Researcher_Agent` (网络研究员) 根据规划，执行网络搜索和信息提取，将初步结果存入State。
- **b. 批判 (Critique)**:`Critic_Analyst_Agent`  (批判性分析师) 审查`Web_Researcher_Agent`收集到的信息。判断信息是否全面、是否存在矛盾、是否跑题。它还可以根据已有信息，提出新的、更深入的调研方向。
- **c. 路由 (Routing)**:
  - 如果`Critic_Analyst_Agent`  认为信息**不充分**，它会提出补充意见，工作流**返回**到步骤a，让`Web_Researcher_Agent` 带着新的指令进行补充研究。
  - 如果`Critic_Analyst_Agent`  认为信息**已足够**，则**跳出循环**，进入下一步。

**第四步：报告生成 (Report Generation)**

- `Report_Writer_Agent`  (报告撰写师) 被激活。
- 它会从State中读取两个关键信息：
  1. 经过多轮研究和批判后，最终确认的**所有研究数据**。
  2. 在第一步中识别出的**查询意图（****`intent`****）**。
- 当所有调研和分析都完成后，它负责将零散的信息整合成一篇逻辑清晰、结构完整的Markdown报告。它还会根据`intent`从预定义的模板库中选择**对应的Markdown报告模板**，并将研究数据填充进去，生成最终报告。

**第五步：最终产出 (Output)**

- 系统将生成的、结构精美的Markdown字符串写入用户在CLI中指定的输出文件（例如`report.md`）。

#### 7. 最终交付成果 (Final Deliverable)

- 一个可以通过命令行灵活调用的Python程序。
- 一份根据用户查询意图动态生成的、结构化、内容详实的Markdown格式调研报告。

#### 8. 错误处理与日志记录 (Error Handling & Logging)

真实世界中，网络请求可能会失败，API可能会超时。我要创建一个健壮的系统，因此需要处理这些异常，在每个关键步骤加上日志打印，从而方便调试和回溯问题。

***

### 如何实现智能模板选择机制

#### 第一步：定义多种报告模板

首先，我们需要根据用户可能提出的问题类型，预先设计几个不同的模板。以下是几个常见的类型及其对应的模板结构：

**1. 对比分析报告 (Comparison Report)**

- **intent**: `comparison`
- **触发查询示例**: “对比CrewAI和Autogen”、“比较一下Ollama和vLLM的优劣”
- **模板结构**:
  - 摘要 (TL;DR)
  - 核心特性并列对比 (Side-by-Side Feature Table)
  - 各自的优缺点 (Pros and Cons)
  - 最佳应用场景 (Best Use Cases)
  - 代码示例
  - 参考来源

**2. 深度解析报告 (In-Depth Topic Report)**

- **intent**: `deep_dive`
- **触发查询示例**: “深入解释一下Transformer架构”、“LangGraph的工作原理是什么？”
- **模板结构**:
  - 摘要 (TL;DR)
  - 核心概念与背景 (Core Concepts & Background)
  - 关键工作机制/架构详解 (Key Mechanisms / Architecture)
  - 代码实现/伪代码示例 (Code Implementation / Pseudocode)
  - 应用与影响 (Applications & Impact)
  - 参考来源

**3. 技术巡览报告 (Landscape/Survey Report)**

- **intent**: `survey`
- **触发查询示例**: “盘点一下目前主流的开源向量数据库”、“有哪些好用的开源LLM可观测性平台？”
- **模板结构**:
  - 摘要 (TL;DR)
  - 市场主要玩家/项目列表 (List of Key Players/Projects)
  - 分类与归纳 (Categorization, e.g., by license, architecture)
  - 关键特性对比 (Feature Comparison Matrix)
  - 未来趋势展望 (Future Trends)
  - 参考来源

**4. 实践指南报告 (How-To/Tutorial Report)**

- **intent**: `tutorial`
- **触发查询示例**: “如何使用LoRA微调一个模型？”、“本地部署Mistral模型的步骤是什么？”
- **模板结构**:
  - 摘要 (TL;DR)
  - 前置准备与环境要求 (Prerequisites & Environment)
  - 分步操作指南 (Step-by-Step Guide)
  - 常见问题与解决方案 (FAQ & Troubleshooting)
  - 代码/脚本示例 (Code/Script Examples)
  - 参考来源

#### 第二步：创建“查询意图分类”Agent

这是实现动态选择的核心。在整个工作流开始之前，我们需要一个专门的Agent来“预处理”用户的查询。

- **Agent角色**:`Query_Classifier_Agent` (查询意图分类员)
- **职责**:
  1. 接收用户输入的原始查询。
  2. 判断该查询属于我们预定义的哪种类型（`comparison`,`deep_dive`,`survey`,`tutorial`）。
  3. 输出一个标准化的分类标签。
- **实现**: 这是一个简单的分类任务，非常适合用LLM完成。你可以给它一个这样的Prompt:
  ```markdown 
  你是一个AI助手，负责将用户的技术查询分类到以下四种类型之一：
  1. comparison: 当用户明确要求比较两个或多个事物时。
  2. deep_dive: 当用户要求深入解释单个概念、技术或项目时。
  3. survey: 当用户要求盘点或调研某个领域的主要参与者或技术时。
  4. tutorial: 当用户询问如何完成某项具体的技术任务时。
  请只输出最终的分类标签，不要有任何其他解释。
  用户查询: "{{query}}"
  分类标签:
  ```


#### 第三步：在LangGraph中实现动态路由

现在，你的LangGraph工作流将变得更加智能。

1. **起始节点**: 工作流的第一个节点就是运行`Query_Classifier_Agent`，得到意图标签（例如`intent = "comparison"`），并将其存入Graph的State中。
2. **条件路由 (Conditional Edge)**: 从起始节点出来，连接一个**条件路由**。这个路由会检查State中的`intent`值，并根据该值决定接下来应该调用哪一套分析逻辑或Agent组合。虽然对于这个项目，后续的研究步骤可能相似，但这一步在架构上是清晰的。
3. **动态Prompt注入**: 最关键的一步。当工作流进行到最后的`Report_Writer_Agent`时，你需要动态地将对应的模板注入到它的Prompt中。
   - 你可以将所有模板结构存储在一个Python字典或单独的`templates.py`文件中。
   - `Report_Writer_Agent`的Prompt可以这样设计：
   ```python 
   # 从templates模块加载模板
   from templates import REPORT_TEMPLATES

   # 在运行Agent时...
   intent = state['intent'] # 从LangGraph的状态中获取意图
   template_structure = REPORT_TEMPLATES[intent]

   prompt = f"""
   你是一个顶级的技术报告撰写专家。
   请根据以下收集到的信息，撰写一份专业的、详尽的调研报告。
   你必须严格遵循下面的Markdown模板结构来组织你的报告内容：

   ---模板开始---
   {template_structure}
   ---模板结束---

   收集到的信息如下：
   {researched_data}
   """
   ```


### 如何**定义Agent角色**和**工作流** (使用CrewAI + LangGraph)

1. **定义Agent角色 (CrewAI):**
   - `Query_Classifier_Agent` (意图分类师):
     - **职责**: 将用户最初的、高层次的问题分类成不同的意图：`comparison`,`deep_dive`,`survey`,`tutorial`。
   - `Chief_Planner_Agent` (首席规划师):
     - **职责**: 接收用户最初的、高层次的问题。
     - **产出**: 将问题分解成一个结构化的调研计划（Search Queries List, Topics to Cover）。这是整个流程的起点。
   - `Web_Researcher_Agent` (网络研究员):
     - **职责**: 根据规划师给出的关键词列表，执行网络搜索，访问URL，提取关键信息。
     - **工具**:`TavilySearchTool`(或任何其他搜索API),`WebsiteReadTool` (抓取并清理网页内容)。
   - `Critic_Analyst_Agent` (批判性分析师):
     - **职责**: 核心角色！负责审查`Web_Researcher_Agent`收集到的信息。判断信息是否全面、是否存在矛盾、是否跑题。它还可以根据已有信息，提出新的、更深入的调研方向。
     - **产出**: 对当前调研结果的评价，以及给`Web_Researcher_Agent`的“补充调研”指令。
   - `Report_Writer_Agent` (报告撰写师):
     - **职责**: 当所有调研和分析都完成后，它负责整合零散的信息，还会根据第一步中识别出的**查询意图（****`intent`****）**从预定义的模板库中选择**对应的Markdown报告模板**，并将研究数据填充进去，生成最终报告。
2. **定义工作流 (LangGraph) - “调研-批判-修正”循环：** &#x20;

   这是一个比线性流程有趣得多的图结构。
   - **State (状态)**: 定义一个图的状态对象，包含`original_query`,`intent`,`plan`,`researched_data`(一个信息列表),`critique_feedback`,`final_report`。
   - **Nodes (节点)**:
     - `classify_node` : 执行`Query_Classifier_Agent` 。
     - `plan_node`: 执行`Chief_Planner_Agent`。
     - `research_node`: 执行`Web_Researcher_Agent`。
     - `critique_node`: 执行`Critic_Analyst_Agent`。
     - `write_report_node`: 执行`Report_Writer_Agent`。
   - **Edges (边) - 流程的核心:**
     - `classify_node` ->`plan_node`: 分类完成后开始规划。
     - `plan_node`->`research_node`: 规划完成后开始研究。
     - `research_node`->`critique_node`: 研究完一轮后，交给批判家评估。
     - **条件边 (Conditional Edge) from**\*\*`critique_node`\*\*:
       - **IF**`critique_feedback`指出需要补充信息 ->**LOOP BACK** to`research_node` (带着新的补充指令)。
       - **IF**`critique_feedback`认为信息完整 ->**PROCEED** to`write_report_node`。
     - `write_report_node`->**END**.
