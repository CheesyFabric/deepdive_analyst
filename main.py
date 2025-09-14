#!/usr/bin/env python3
"""
DeepDive Analyst - AI技术专家调研与分析智能体团队
主程序入口文件

这是一个基于多智能体协作的系统，能够针对用户提出的复杂IT技术问题，
进行深入的信息检索、分析、整合，并生成结构化、高质量的调研报告。
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# 初始化控制台和Typer应用
console = Console()
app = typer.Typer(
    name="DeepDive Analyst",
    help="AI技术专家调研与分析智能体团队",
    add_completion=False
)


@app.command()
def research(
    query: str = typer.Option(..., "--query", "-q", help="研究问题或查询"),
    output: str = typer.Option("report.md", "--output", "-o", help="输出报告文件路径"),
    max_iterations: int = typer.Option(3, "--max-iterations", "-i", help="最大研究迭代次数"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细日志"),
    template: str = typer.Option("auto", "--template", "-t", help="指定报告模板类型 (comparison/deep_dive/survey/tutorial/auto)")
):
    """
    执行深度技术调研分析
    
    Args:
        query: 用户提出的技术问题
        output: 输出报告的文件路径
        max_iterations: 最大研究迭代次数
        verbose: 是否显示详细日志
        template: 报告模板类型
    """
    # 配置日志级别
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    console.print(Panel.fit(
        Text("DeepDive Analyst", style="bold blue"),
        title="欢迎使用",
        border_style="blue"
    ))
    
    # 显示参数信息
    console.print(f"[green]✓[/green] 收到查询: {query}")
    console.print(f"[green]✓[/green] 输出文件: {output}")
    console.print(f"[green]✓[/green] 最大迭代次数: {max_iterations}")
    console.print(f"[green]✓[/green] 报告模板: {template}")
    console.print(f"[green]✓[/green] 详细日志: {'开启' if verbose else '关闭'}")
    
    try:
        # 导入工作流
        from src.workflows.langgraph_workflow import LangGraphWorkflow
        
        # 创建并执行工作流
        console.print("[blue]🚀[/blue] 开始执行LangGraph调研工作流...")
        workflow = LangGraphWorkflow()
        
        # 如果指定了模板类型，覆盖自动分类
        if template != "auto":
            console.print(f"[yellow]📝[/yellow] 使用指定模板: {template}")
            # 这里可以添加模板覆盖逻辑
        
        results = workflow.execute(query, max_iterations=max_iterations)
        
        if results['success']:
            # 保存报告到文件
            with open(output, 'w', encoding='utf-8') as f:
                f.write(results['final_report'])
            
            console.print(f"[green]✅[/green] 调研完成！报告已保存到: {output}")
            
            # 显示统计信息
            console.print(f"[blue]📊[/blue] 研究迭代次数: {results.get('research_iterations', 0)}")
            console.print(f"[blue]📊[/blue] 查询意图: {results.get('intent', '未知')}")
            
            # 显示工作流摘要
            if verbose:
                summary = workflow.get_workflow_summary(results)
                console.print(Panel(
                    summary,
                    title="工作流执行摘要",
                    border_style="green"
                ))
        else:
            console.print(f"[red]❌[/red] 调研失败: {results.get('error', '未知错误')}")
            
    except ImportError as e:
        console.print(f"[red]❌[/red] 导入错误: {str(e)}")
        console.print("[yellow]💡[/yellow] 请确保已安装所有依赖: pip install -r requirements.txt")
    except Exception as e:
        console.print(f"[red]❌[/red] 执行错误: {str(e)}")
        if verbose:
            import traceback
            console.print(f"[red]详细错误信息:[/red]\n{traceback.format_exc()}")


@app.command()
def version():
    """显示版本信息"""
    console.print("[bold blue]DeepDive Analyst v1.0.0[/bold blue]")
    console.print("AI技术专家调研与分析智能体团队")
    console.print("\n[bold]技术栈:[/bold]")
    console.print("- CrewAI: 多智能体协作框架")
    console.print("- LangGraph: 工作流编排")
    console.print("- Tavily: 网络搜索API")
    console.print("- OpenAI: 大语言模型")


@app.command()
def config():
    """显示当前配置信息"""
    try:
        from src.configs.config import Config
        
        console.print("[bold blue]DeepDive Analyst 配置信息[/bold blue]")
        console.print(f"[green]✓[/green] LLM模型: {Config.LLM_MODEL}")
        console.print(f"[green]✓[/green] 模型温度: {Config.LLM_TEMPERATURE}")
        console.print(f"[green]✓[/green] 最大搜索结果: {Config.MAX_SEARCH_RESULTS}")
        console.print(f"[green]✓[/green] 搜索超时: {Config.SEARCH_TIMEOUT}秒")
        console.print(f"[green]✓[/green] 默认输出文件: {Config.DEFAULT_OUTPUT_FILE}")
        
        # 检查API密钥状态
        console.print("\n[bold]API密钥状态:[/bold]")
        openai_status = "✅ 已配置" if Config.OPENAI_API_KEY else "❌ 未配置"
        tavily_status = "✅ 已配置" if Config.TAVILY_API_KEY else "❌ 未配置"
        langsmith_status = "✅ 已配置" if Config.LANGCHAIN_API_KEY else "❌ 未配置"
        
        console.print(f"[green]OpenAI API:[/green] {openai_status}")
        console.print(f"[green]Tavily API:[/green] {tavily_status}")
        console.print(f"[green]LangSmith API:[/green] {langsmith_status}")
        
    except ImportError as e:
        console.print(f"[red]❌[/red] 配置加载失败: {str(e)}")


@app.command()
def examples():
    """显示使用示例"""
    console.print("[bold blue]DeepDive Analyst 使用示例[/bold blue]")
    
    console.print("\n[bold]1. 对比分析示例:[/bold]")
    console.print("[green]python main.py research --query \"对比React和Vue的优缺点\" --template comparison[/green]")
    
    console.print("\n[bold]2. 深度解析示例:[/bold]")
    console.print("[green]python main.py research --query \"深入解释Docker容器技术\" --template deep_dive[/green]")
    
    console.print("\n[bold]3. 技术巡览示例:[/bold]")
    console.print("[green]python main.py research --query \"盘点目前主流的机器学习框架\" --template survey[/green]")
    
    console.print("\n[bold]4. 实践指南示例:[/bold]")
    console.print("[green]python main.py research --query \"如何使用Kubernetes部署应用\" --template tutorial[/green]")
    
    console.print("\n[bold]5. 高级选项示例:[/bold]")
    console.print("[green]python main.py research --query \"你的查询\" --max-iterations 5 --verbose --output custom_report.md[/green]")


@app.command()
def test():
    """运行测试套件"""
    console.print("[blue]🧪[/blue] 开始运行测试套件...")
    
    try:
        import subprocess
        import sys
        
        # 运行pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅[/green] 所有测试通过！")
            console.print(result.stdout)
        else:
            console.print("[red]❌[/red] 测试失败")
            console.print(result.stdout)
            console.print(result.stderr)
            
    except Exception as e:
        console.print(f"[red]❌[/red] 测试运行失败: {str(e)}")
        console.print("[yellow]💡[/yellow] 请确保已安装pytest: pip install pytest")


if __name__ == "__main__":
    app()
