#!/usr/bin/env python3
"""
LangSmith 快速设置脚本
帮助用户快速配置 LangSmith 环境
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def check_env_file():
    """检查 .env 文件是否存在"""
    env_file = Path(".env")
    if env_file.exists():
        console.print("[green]✅[/green] .env 文件已存在")
        return True
    else:
        console.print("[yellow]⚠️[/yellow] .env 文件不存在")
        return False

def create_env_file():
    """创建 .env 文件"""
    env_content = """# DeepDive Analyst 环境配置
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
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API 配置
GEMINI_API_KEY=your_gemini_api_key_here

# 阿里通义千问 API 配置
QWEN_API_KEY=your_qwen_api_key_here

# Anthropic Claude API 配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Tavily 搜索API配置
TAVILY_API_KEY=your_tavily_api_key_here

# LangSmith 配置 (可选，但强烈推荐)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=deepdive-analyst
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# 搜索配置
MAX_SEARCH_RESULTS=10
SEARCH_TIMEOUT=30

# 报告配置
DEFAULT_OUTPUT_FILE=report.md
MAX_REPORT_LENGTH=10000
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    console.print("[green]✅[/green] .env 文件已创建")

def get_langsmith_api_key():
    """获取 LangSmith API 密钥"""
    console.print("\n[bold blue]🔑 LangSmith API 密钥配置[/bold blue]")
    console.print("请按照以下步骤获取 LangSmith API 密钥:")
    console.print("1. 访问 https://smith.langchain.com/")
    console.print("2. 注册并登录账户")
    console.print("3. 在设置页面创建 API 密钥")
    console.print("4. 复制密钥并粘贴到下方")
    
    api_key = Prompt.ask("请输入 LangSmith API 密钥", password=True)
    return api_key

def update_env_file(api_key: str):
    """更新 .env 文件中的 LangSmith API 密钥"""
    env_file = Path(".env")
    if not env_file.exists():
        create_env_file()
    
    # 读取现有内容
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换 API 密钥
    content = content.replace("your_langsmith_api_key_here", api_key)
    
    # 写回文件
    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)
    
    console.print("[green]✅[/green] LangSmith API 密钥已更新")

def verify_configuration():
    """验证配置"""
    console.print("\n[bold blue]🔍 验证配置[/bold blue]")
    
    # 检查环境变量
    required_vars = [
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_API_KEY",
        "LANGCHAIN_PROJECT"
    ]
    
    table = Table(title="配置状态")
    table.add_column("配置项", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("值", style="yellow")
    
    all_configured = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            status = "✅ 已配置"
            display_value = value[:20] + "..." if len(value) > 20 else value
        else:
            status = "❌ 未配置"
            display_value = "未设置"
            all_configured = False
        
        table.add_row(var, status, display_value)
    
    console.print(table)
    
    return all_configured

def show_next_steps():
    """显示后续步骤"""
    console.print("\n[bold blue]🚀 后续步骤[/bold blue]")
    
    steps = [
        "运行测试命令验证配置: python main.py config",
        "执行示例调研: python main.py research --query '对比React和Vue的优缺点' --verbose",
        "访问 LangSmith 控制台查看执行轨迹: https://smith.langchain.com/",
        "运行可视化演示: python examples/langsmith_visualization_example.py"
    ]
    
    for i, step in enumerate(steps, 1):
        console.print(f"[green]{i}.[/green] {step}")
    
    console.print("\n[yellow]💡 提示:[/yellow] 启用 LangSmith 后，每次执行调研任务都会在 LangSmith 控制台中生成详细的执行轨迹和可视化图表")

def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold blue]LangSmith 快速设置[/bold blue]\n"
        "为 DeepDive Analyst 项目配置 LangSmith 可视化功能",
        title="欢迎",
        border_style="blue"
    ))
    
    # 检查 .env 文件
    if not check_env_file():
        if Confirm.ask("是否创建 .env 文件？"):
            create_env_file()
        else:
            console.print("[red]❌[/red] 需要 .env 文件才能继续配置")
            return
    
    # 检查 LangSmith 配置
    if not verify_configuration():
        console.print("\n[yellow]⚠️[/yellow] LangSmith 配置不完整")
        
        if Confirm.ask("是否现在配置 LangSmith？"):
            api_key = get_langsmith_api_key()
            if api_key:
                update_env_file(api_key)
                console.print("[green]✅[/green] LangSmith 配置完成")
            else:
                console.print("[red]❌[/red] 未提供 API 密钥")
                return
        else:
            console.print("[yellow]💡[/yellow] 您可以稍后手动编辑 .env 文件来配置 LangSmith")
            return
    
    # 最终验证
    console.print("\n[bold blue]🔍 最终验证[/bold blue]")
    if verify_configuration():
        console.print("[green]✅[/green] LangSmith 配置验证成功！")
        show_next_steps()
    else:
        console.print("[red]❌[/red] 配置验证失败，请检查 .env 文件")

if __name__ == "__main__":
    main()
