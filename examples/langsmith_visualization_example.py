#!/usr/bin/env python3
"""
LangSmith 可视化示例
演示如何在 DeepDive Analyst 项目中启用和使用 LangSmith 可视化功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.workflows.langgraph_workflow import LangGraphWorkflow
from src.configs.config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def setup_langsmith_environment():
    """设置 LangSmith 环境变量"""
    console.print("[bold blue]🔧 设置 LangSmith 环境变量[/bold blue]")
    
    # 检查环境变量
    required_vars = [
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_API_KEY", 
        "LANGCHAIN_PROJECT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        console.print(f"[red]❌ 缺少环境变量: {', '.join(missing_vars)}[/red]")
        console.print("[yellow]💡 请在 .env 文件中添加以下配置:[/yellow]")
        console.print("""
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=deepdive-analyst
        """)
        return False
    else:
        console.print("[green]✅ LangSmith 环境变量配置正确[/green]")
        return True


def demonstrate_workflow_visualization():
    """演示工作流可视化"""
    console.print("\n[bold blue]🚀 演示 LangGraph 工作流可视化[/bold blue]")
    
    # 创建测试查询
    test_queries = [
        {
            "query": "对比React和Vue的优缺点",
            "description": "对比分析查询 - 将展示完整的迭代循环"
        },
        {
            "query": "深入解释Docker容器技术",
            "description": "深度解析查询 - 将展示单次研究流程"
        },
        {
            "query": "盘点目前主流的机器学习框架",
            "description": "技术巡览查询 - 将展示多轮研究过程"
        }
    ]
    
    # 创建表格显示测试查询
    table = Table(title="测试查询列表")
    table.add_column("查询", style="cyan")
    table.add_column("描述", style="green")
    table.add_column("预期可视化", style="yellow")
    
    for i, test in enumerate(test_queries, 1):
        table.add_row(
            test["query"],
            test["description"],
            f"查看 LangSmith 控制台中的运行 #{i}"
        )
    
    console.print(table)
    
    return test_queries


def run_visualization_demo():
    """运行可视化演示"""
    console.print("\n[bold blue]🎯 开始可视化演示[/bold blue]")
    
    # 检查 LangSmith 配置
    if not setup_langsmith_environment():
        return
    
    # 显示测试查询
    test_queries = demonstrate_workflow_visualization()
    
    # 创建 LangGraph 工作流
    console.print("\n[blue]📊 初始化 LangGraph 工作流...[/blue]")
    workflow = LangGraphWorkflow()
    
    # 执行测试查询
    for i, test in enumerate(test_queries, 1):
        console.print(f"\n[bold green]执行测试查询 #{i}[/bold green]")
        console.print(f"[cyan]查询:[/cyan] {test['query']}")
        console.print(f"[cyan]描述:[/cyan] {test['description']}")
        
        try:
            # 执行工作流
            console.print("[yellow]⏳ 正在执行工作流...[/yellow]")
            results = workflow.execute(
                query=test["query"],
                max_iterations=2  # 限制迭代次数以便快速演示
            )
            
            if results["success"]:
                console.print("[green]✅ 工作流执行成功[/green]")
                console.print(f"[blue]📈 研究迭代次数:[/blue] {results.get('research_iterations', 0)}")
                console.print(f"[blue]📝 查询意图:[/blue] {results.get('intent', '未知')}")
                console.print(f"[blue]📄 报告长度:[/blue] {len(results.get('final_report', ''))} 字符")
                
                # 显示 LangSmith 追踪信息
                console.print("\n[bold magenta]🔍 LangSmith 追踪信息[/bold magenta]")
                console.print("请在 LangSmith 控制台中查看详细的执行轨迹:")
                console.print("1. 访问 https://smith.langchain.com/")
                console.print("2. 选择项目: deepdive-analyst")
                console.print("3. 查看最新的运行记录")
                console.print("4. 点击查看详细的执行轨迹和可视化")
                
            else:
                console.print(f"[red]❌ 工作流执行失败:[/red] {results.get('error', '未知错误')}")
                
        except Exception as e:
            console.print(f"[red]❌ 执行异常:[/red] {str(e)}")
        
        # 等待用户确认继续
        if i < len(test_queries):
            console.print("\n[yellow]按 Enter 继续下一个测试...[/yellow]")
            input()


def show_langsmith_features():
    """显示 LangSmith 功能特性"""
    console.print("\n[bold blue]🌟 LangSmith 可视化功能特性[/bold blue]")
    
    features = [
        {
            "功能": "工作流执行轨迹",
            "描述": "可视化整个 LangGraph 工作流的执行过程",
            "价值": "理解多智能体协作流程"
        },
        {
            "功能": "Agent 协作监控",
            "描述": "追踪每个 Agent 的输入输出和执行时间",
            "价值": "优化 Agent 性能和协作效率"
        },
        {
            "功能": "迭代循环可视化",
            "描述": "展示研究-批判-修正的循环过程",
            "价值": "调试复杂的迭代逻辑"
        },
        {
            "功能": "性能分析",
            "描述": "分析 Token 使用、执行时间和成本",
            "价值": "优化系统性能和成本控制"
        },
        {
            "功能": "错误追踪",
            "描述": "详细的错误信息和调试上下文",
            "价值": "快速定位和解决问题"
        },
        {
            "功能": "实时监控",
            "描述": "实时查看系统运行状态",
            "价值": "生产环境监控和告警"
        }
    ]
    
    # 创建功能表格
    table = Table(title="LangSmith 功能特性")
    table.add_column("功能", style="cyan", width=20)
    table.add_column("描述", style="green", width=40)
    table.add_column("价值", style="yellow", width=30)
    
    for feature in features:
        table.add_row(
            feature["功能"],
            feature["描述"],
            feature["价值"]
        )
    
    console.print(table)


def show_visualization_examples():
    """显示可视化示例"""
    console.print("\n[bold blue]📊 LangSmith 可视化示例[/bold blue]")
    
    examples = [
        {
            "场景": "工作流概览",
            "可视化": "流程图显示节点执行顺序",
            "数据": "classify → plan → research → critique → write_report"
        },
        {
            "场景": "Agent 执行详情",
            "可视化": "每个 Agent 的输入输出和执行时间",
            "数据": "QueryClassifierAgent: 0.5s, 150 tokens"
        },
        {
            "场景": "迭代循环追踪",
            "可视化": "循环条件和状态变化",
            "数据": "needs_more_research: true → continue"
        },
        {
            "场景": "性能指标",
            "可视化": "Token 使用、执行时间、成本统计",
            "数据": "总时间: 25.8s, 总 Token: 4550"
        },
        {
            "场景": "错误分析",
            "可视化": "错误堆栈和调试信息",
            "数据": "APIError: Tavily rate limit exceeded"
        }
    ]
    
    # 创建示例表格
    table = Table(title="可视化示例")
    table.add_column("场景", style="cyan", width=20)
    table.add_column("可视化", style="green", width=30)
    table.add_column("数据示例", style="yellow", width=40)
    
    for example in examples:
        table.add_row(
            example["场景"],
            example["可视化"],
            example["数据"]
        )
    
    console.print(table)


def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold blue]LangSmith 可视化演示[/bold blue]\n"
        "DeepDive Analyst 项目 LangSmith 集成示例",
        title="欢迎",
        border_style="blue"
    ))
    
    # 显示功能特性
    show_langsmith_features()
    
    # 显示可视化示例
    show_visualization_examples()
    
    # 运行演示
    console.print("\n[bold yellow]是否开始可视化演示？[/bold yellow]")
    console.print("1. 是 - 运行完整的可视化演示")
    console.print("2. 否 - 仅显示配置信息")
    
    choice = input("\n请选择 (1/2): ").strip()
    
    if choice == "1":
        run_visualization_demo()
    else:
        console.print("\n[blue]📋 配置信息:[/blue]")
        console.print("请在 .env 文件中配置 LangSmith:")
        console.print("""
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=deepdive-analyst
        """)
        console.print("\n[yellow]💡 配置完成后，运行以下命令开始演示:[/yellow]")
        console.print("python examples/langsmith_visualization_example.py")
    
    console.print("\n[green]✅ 演示完成！[/green]")
    console.print("[blue]🔗 更多信息请查看:[/blue] docs/LangSmith_Visualization_Guide.md")


if __name__ == "__main__":
    main()
