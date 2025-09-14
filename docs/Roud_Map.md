# Roud_Map

# DeepDive Analyst 开发路线图

本路线图将指导你分阶段、迭代式地构建DeepDive Analyst项目，确保每个阶段都有明确的目标和可验证的产出。这种方法有助于管理复杂性，让你在每个节点都能获得有效的反馈。

***

### 阶段一：项目初始化与环境配置 (Phase 1: Project Initialization & Setup)

**目标 (Goal):**

搭建项目的基本骨架，创建标准化的目录结构，并确保所有依赖都已正确安装。为后续的编码工作做好准备。

**关键任务 (Key Tasks):**

- [ ] 项目主目录 `Deepdive_Analyst`已创建好，使用 `requirements.txt`文件定义项目依赖。
- [ ] 创建清晰的目录结构 (`src/agents`, `src/tools`, `src/workflows`, `src/configs`, `main.py`)。
- [ ] 初始化Python虚拟环境并进入虚拟环境安装所有依赖。
- [ ] 创建并配置`.env`文件，填入`TAVILY_API_KEY`等必要的API密钥。

**成果物 (Deliverables):**

- 一个空的、但结构完整的项目框架。
- 虚拟环境已激活，所有库已安装。
- 可以成功运行一个只打印 "Hello, World!" 的 `main.py`。

***

### 阶段二：核心工具与Agent的MVP实现 (Phase 2: Core Tools & Agents MVP)

**目标 (Goal):**

创建并独立测试项目最核心的“积木”——搜索工具和基础Agent。确保这些基础单元能够正常工作，为后续的流程编排打下基础。

**关键任务 (Key Tasks):**

- [ ] 在 `src/tools/` 目录下，创建并测试 `SearchTools`，确保Tavily API可以被成功调用。
- [ ] 在 `src/agents/` 目录下，定义 `ResearcherAgent` 和 `CriticAnalystAgent` 的角色、目标和背景故事（`role`, `goal`, `backstory`）。
- [ ] 使用CrewAI的`Task`和`Crew`，在`main.py`中创建一个临时的**线性**工作流，验证两个Agent可以按顺序接收输入并产生输出。

**成果物 (Deliverables):**

- `SearchTools` 能够独立运行并返回搜索结果。
- 一个可以运行的简单Crew，能够完成“研究 -> 批判”的线性流程，并将最终结果打印到控制台。

***

### 阶段三：核心循环工作流搭建 (Phase 3: Core Loop Workflow with LangGraph)

**目标 (Goal):**

用LangGraph替换临时的线性工作流，实现项目的灵魂——“研究-批判-修正”的迭代循环。

**关键任务 (Key Tasks):**

- [ ] 在 `src/workflows/` 目录下，创建`research_workflow.py`。
- [ ] 定义LangGraph的`StateGraph`和包含所有必要字段的`GraphState`。
- [ ] 创建`research_node`和`critique_node`，并将它们与对应的Agent逻辑绑定。
- [ ] 编写`should_continue`条件路由函数，根据`CriticAnalystAgent`的输出来决定流程走向（继续研究或结束）。
- [ ] 将所有节点和边连接起来，构建一个完整的、可运行的图（Graph）。

**成果物 (Deliverables):**

- 一个封装了LangGraph工作流的函数，该函数接收一个查询，能够执行多轮研究和批判，并返回最终的研究数据。
- 可以通过日志或打印输出来观察到循环确实在发生。

***

### 阶段四：集成智能模板机制 (Phase 4: Integrate Intelligent Templating)

**目标 (Goal):**

为项目增加“智能”，使其能够理解用户意图并产出格式化、专业化的报告。

**关键任务 (Key Tasks):**

- [ ] 在 `src/configs/` 目录下，创建`templates.py`文件，并定义至少四种不同的Markdown报告模板。
- [ ] 在 `src/agents/` 目录下，创建`QueryClassifierAgent`，并为其编写高效的分类Prompt。
- [ ] 在 `src/agents/` 目录下，创建`ReportWriterAgent`，其Prompt应设计为可以动态接收并使用模板。
- [ ] 修改LangGraph工作流，在最开始增加一个`classify_node`，并将`intent`存入`GraphState`。
- [ ] 在图的末端增加`write_report_node`，确保它能根据`intent`正确调用模板生成报告。

**成果物 (Deliverables):**

- 工作流现在可以根据不同的输入查询（例如“对比A和B” vs “解释C”），在最终输出时应用不同的Markdown模板。
- 整个流程从输入查询到输出格式化的报告，实现了自动化。

***

### 阶段五：构建CLI并完成端到端整合 (Phase 5: Build CLI & Final Integration)

**目标 (Goal):**

将后台的所有智能逻辑，通过一个简洁的用户接口暴露出来，完成项目的最终整合，使其成为一个可交付、可演示的完整应用。

**关键任务 (Key Tasks):**

- [ ] 使用`Typer`或`argparse`库重构`main.py`，创建一个专业的命令行界面。
- [ ] CLI应支持`--query`和`--output`参数。
- [ ] 将LangGraph工作流与CLI命令进行绑定。
- [ ] 增加必要的日志记录，在命令行运行时可以显示关键步骤的进度（例如 "正在分类查询...", "开始第一轮研究..."）。
- [ ] 编写`README.md`文件，说明项目的功能、如何安装和使用。

**成果物 (Deliverables):**

- 一个完整的命令行工具。用户可以通过`python main.py research --query "..."`来运行整个流程。
- 项目根目录下有一份清晰的`README.md`，方便他人理解和使用你的项目。
