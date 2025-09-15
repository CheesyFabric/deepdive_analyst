#!/usr/bin/env python3
"""
多LLM使用示例
演示如何在DeepDive Analyst项目中使用不同的LLM提供商
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm.llm_factory import LLMFactory
from src.configs.config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()


def show_llm_providers():
    """显示支持的LLM提供商"""
    console.print("[bold blue]🤖 支持的LLM提供商[/bold blue]")
    
    providers = LLMFactory.get_supported_providers()
    
    table = Table(title="LLM提供商信息")
    table.add_column("提供商", style="cyan")
    table.add_column("描述", style="green")
    table.add_column("可用模型", style="yellow")
    
    for provider in providers:
        try:
            info = LLMFactory.get_provider_info(provider)
            models = info['available_models'][:3]  # 只显示前3个模型
            models_str = ', '.join(models) + ('...' if len(info['available_models']) > 3 else '')
            
            table.add_row(
                provider.upper(),
                info['description'],
                models_str
            )
        except Exception as e:
            table.add_row(provider.upper(), "获取信息失败", str(e))
    
    console.print(table)


def test_llm_provider(provider: str, model: str, api_key: str):
    """测试LLM提供商"""
    console.print(f"\n[bold blue]🧪 测试 {provider.upper()} 提供商[/bold blue]")
    
    try:
        # 创建LLM实例
        llm = LLMFactory.create_llm(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )
        
        console.print(f"[green]✅[/green] LLM实例创建成功: {llm}")
        
        # 测试生成
        test_prompt = "请用一句话介绍人工智能的发展历程。"
        console.print(f"[yellow]📝[/yellow] 测试提示: {test_prompt}")
        
        response = llm.generate(test_prompt)
        
        if response.success:
            console.print(f"[green]✅[/green] 生成成功!")
            console.print(f"[blue]📄[/blue] 响应内容: {response.content}")
            
            if response.usage:
                console.print(f"[blue]📊[/blue] Token使用: {response.usage}")
        else:
            console.print(f"[red]❌[/red] 生成失败: {response.error_message}")
            
        return response.success
        
    except Exception as e:
        console.print(f"[red]❌[/red] 测试失败: {str(e)}")
        return False


def interactive_llm_test():
    """交互式LLM测试"""
    console.print("\n[bold blue]🎯 交互式LLM测试[/bold blue]")
    
    # 显示提供商
    show_llm_providers()
    
    # 获取用户选择
    providers = LLMFactory.get_supported_providers()
    console.print("\n请选择要测试的LLM提供商:")
    for i, provider in enumerate(providers, 1):
        console.print(f"{i}. {provider.upper()}")
    
    while True:
        try:
            choice = int(Prompt.ask("请输入选择", default="1"))
            if 1 <= choice <= len(providers):
                selected_provider = providers[choice - 1]
                break
            else:
                console.print(f"[red]❌[/red] 请输入1-{len(providers)}之间的数字")
        except ValueError:
            console.print("[red]❌[/red] 请输入有效的数字")
    
    # 获取模型选择
    try:
        models = LLMFactory.get_available_models(selected_provider)
        console.print(f"\n{selected_provider.upper()} 可用模型:")
        for i, model in enumerate(models, 1):
            console.print(f"{i}. {model}")
        
        while True:
            try:
                model_choice = int(Prompt.ask("请选择模型", default="1"))
                if 1 <= model_choice <= len(models):
                    selected_model = models[model_choice - 1]
                    break
                else:
                    console.print(f"[red]❌[/red] 请输入1-{len(models)}之间的数字")
            except ValueError:
                console.print("[red]❌[/red] 请输入有效的数字")
    except Exception as e:
        console.print(f"[yellow]⚠️[/yellow] 无法获取模型列表: {str(e)}")
        selected_model = Prompt.ask("请输入模型名称")
    
    # 获取API密钥
    api_key = Prompt.ask(f"请输入 {selected_provider.upper()} API密钥", password=True)
    
    if not api_key:
        console.print("[red]❌[/red] 未提供API密钥")
        return
    
    # 执行测试
    success = test_llm_provider(selected_provider, selected_model, api_key)
    
    if success:
        console.print(f"\n[green]🎉[/green] {selected_provider.upper()} 测试成功!")
    else:
        console.print(f"\n[red]💥[/red] {selected_provider.upper()} 测试失败!")


def test_current_config():
    """测试当前配置的LLM"""
    console.print("\n[bold blue]⚙️ 测试当前配置的LLM[/bold blue]")
    
    try:
        # 获取当前配置
        llm_config = Config.get_llm_config()
        
        console.print(f"[cyan]当前配置:[/cyan]")
        console.print(f"  提供商: {llm_config['provider']}")
        console.print(f"  模型: {llm_config['model']}")
        console.print(f"  API密钥: {'已配置' if llm_config['api_key'] else '未配置'}")
        
        if not llm_config['api_key']:
            console.print("[red]❌[/red] 当前配置缺少API密钥")
            return
        
        # 测试当前配置
        success = test_llm_provider(
            llm_config['provider'],
            llm_config['model'],
            llm_config['api_key']
        )
        
        if success:
            console.print(f"\n[green]🎉[/green] 当前LLM配置测试成功!")
        else:
            console.print(f"\n[red]💥[/red] 当前LLM配置测试失败!")
            
    except Exception as e:
        console.print(f"[red]❌[/red] 测试当前配置失败: {str(e)}")


def compare_providers():
    """比较不同提供商"""
    console.print("\n[bold blue]📊 比较不同LLM提供商[/bold blue]")
    
    # 这里可以实现一个简单的比较测试
    # 使用相同的提示词测试不同的提供商
    
    test_prompt = "请解释什么是机器学习，并给出一个简单的例子。"
    console.print(f"[yellow]📝[/yellow] 测试提示: {test_prompt}")
    
    # 这里需要用户提供多个API密钥
    console.print("\n[yellow]💡[/yellow] 要比较不同提供商，请确保在.env文件中配置了多个API密钥")
    console.print("然后可以运行: python main.py research --query '你的查询' --verbose")


def show_usage_examples():
    """显示使用示例"""
    console.print("\n[bold blue]📚 使用示例[/bold blue]")
    
    examples = [
        {
            "场景": "使用OpenAI GPT-4",
            "配置": "LLM_PROVIDER=openai\nLLM_MODEL=gpt-4o\nOPENAI_API_KEY=your_key",
            "命令": "python main.py research --query '对比React和Vue'"
        },
        {
            "场景": "使用Google Gemini",
            "配置": "LLM_PROVIDER=gemini\nLLM_MODEL=gemini-1.5-pro\nGEMINI_API_KEY=your_key",
            "命令": "python main.py research --query '深入解释Docker'"
        },
        {
            "场景": "使用阿里通义千问",
            "配置": "LLM_PROVIDER=qwen\nLLM_MODEL=qwen-max\nQWEN_API_KEY=your_key",
            "命令": "python main.py research --query '盘点机器学习框架'"
        },
        {
            "场景": "使用Anthropic Claude",
            "配置": "LLM_PROVIDER=anthropic\nLLM_MODEL=claude-3-5-sonnet-20241022\nANTHROPIC_API_KEY=your_key",
            "命令": "python main.py research --query '如何使用Kubernetes'"
        }
    ]
    
    table = Table(title="LLM使用示例")
    table.add_column("场景", style="cyan")
    table.add_column("配置", style="green")
    table.add_column("命令", style="yellow")
    
    for example in examples:
        table.add_row(
            example["场景"],
            example["配置"],
            example["命令"]
        )
    
    console.print(table)


def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold blue]多LLM使用示例[/bold blue]\n"
        "演示DeepDive Analyst项目的多LLM提供商支持",
        title="欢迎",
        border_style="blue"
    ))
    
    while True:
        console.print("\n[bold blue]请选择操作:[/bold blue]")
        console.print("1. 显示LLM提供商信息")
        console.print("2. 测试当前配置的LLM")
        console.print("3. 交互式LLM测试")
        console.print("4. 比较不同提供商")
        console.print("5. 显示使用示例")
        console.print("6. 退出")
        
        choice = Prompt.ask("请输入选择 (1-6)", default="1")
        
        if choice == "1":
            show_llm_providers()
        elif choice == "2":
            test_current_config()
        elif choice == "3":
            interactive_llm_test()
        elif choice == "4":
            compare_providers()
        elif choice == "5":
            show_usage_examples()
        elif choice == "6":
            console.print("[green]👋[/green] 再见!")
            break
        else:
            console.print("[red]❌[/red] 无效选择，请重新输入")
        
        if choice != "6":
            if not Confirm.ask("是否继续？", default=True):
                break
    
    console.print("\n[green]✅[/green] 示例演示完成!")
    console.print("[blue]💡[/blue] 更多信息请查看:")
    console.print("  - 配置管理: python scripts/setup_llm.py")
    console.print("  - LLM信息: python main.py llm")
    console.print("  - 配置检查: python main.py config")


if __name__ == "__main__":
    main()
