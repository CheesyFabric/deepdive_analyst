#!/usr/bin/env python3
"""
LLM 配置管理脚本
帮助用户配置和管理不同的LLM提供商
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

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

def show_llm_providers():
    """显示支持的LLM提供商"""
    console.print("\n[bold blue]🤖 支持的LLM提供商[/bold blue]")
    
    providers_info = [
        {
            "提供商": "OpenAI",
            "模型": "GPT-4, GPT-3.5",
            "API密钥": "OPENAI_API_KEY",
            "获取地址": "https://platform.openai.com/api-keys",
            "特点": "功能强大，支持多种任务"
        },
        {
            "提供商": "Google Gemini",
            "模型": "Gemini Pro, Gemini Flash",
            "API密钥": "GEMINI_API_KEY",
            "获取地址": "https://makersuite.google.com/app/apikey",
            "特点": "Google开发，多模态支持"
        },
        {
            "提供商": "阿里通义千问",
            "模型": "Qwen Turbo, Qwen Max",
            "API密钥": "QWEN_API_KEY",
            "获取地址": "https://dashscope.console.aliyun.com/",
            "特点": "中文优化，国内访问友好"
        },
        {
            "提供商": "Anthropic",
            "模型": "Claude 3.5 Sonnet",
            "API密钥": "ANTHROPIC_API_KEY",
            "获取地址": "https://console.anthropic.com/",
            "特点": "安全性高，长文本处理"
        }
    ]
    
    table = Table(title="LLM提供商信息")
    table.add_column("提供商", style="cyan")
    table.add_column("模型", style="green")
    table.add_column("API密钥环境变量", style="yellow")
    table.add_column("获取地址", style="blue")
    table.add_column("特点", style="magenta")
    
    for info in providers_info:
        table.add_row(
            info["提供商"],
            info["模型"],
            info["API密钥"],
            info["获取地址"],
            info["特点"]
        )
    
    console.print(table)

def get_provider_choice():
    """获取用户选择的提供商"""
    console.print("\n[bold blue]选择LLM提供商[/bold blue]")
    
    providers = ["openai", "gemini", "qwen", "anthropic"]
    
    console.print("请选择要配置的LLM提供商:")
    for i, provider in enumerate(providers, 1):
        console.print(f"{i}. {provider.upper()}")
    
    while True:
        try:
            choice = int(Prompt.ask("请输入选择 (1-4)", default="1"))
            if 1 <= choice <= 4:
                return providers[choice - 1]
            else:
                console.print("[red]❌[/red] 请输入1-4之间的数字")
        except ValueError:
            console.print("[red]❌[/red] 请输入有效的数字")

def get_api_key(provider):
    """获取API密钥"""
    provider_info = {
        "openai": {
            "name": "OpenAI",
            "url": "https://platform.openai.com/api-keys",
            "env_var": "OPENAI_API_KEY"
        },
        "gemini": {
            "name": "Google Gemini",
            "url": "https://makersuite.google.com/app/apikey",
            "env_var": "GEMINI_API_KEY"
        },
        "qwen": {
            "name": "阿里通义千问",
            "url": "https://dashscope.console.aliyun.com/",
            "env_var": "QWEN_API_KEY"
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "url": "https://console.anthropic.com/",
            "env_var": "ANTHROPIC_API_KEY"
        }
    }
    
    info = provider_info[provider]
    
    console.print(f"\n[bold blue]配置 {info['name']} API密钥[/bold blue]")
    console.print(f"请访问: {info['url']}")
    console.print("获取API密钥后，请粘贴到下方")
    
    api_key = Prompt.ask(f"请输入 {info['name']} API密钥", password=True)
    return api_key, info['env_var']

def get_model_choice(provider):
    """获取模型选择"""
    models = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "gemini": ["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash", "gemini/gemini-1.0-pro"],
        "qwen": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen2-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
    }
    
    available_models = models.get(provider, ["default"])
    
    console.print(f"\n[bold blue]选择 {provider.upper()} 模型[/bold blue]")
    console.print("可用模型:")
    for i, model in enumerate(available_models, 1):
        console.print(f"{i}. {model}")
    
    while True:
        try:
            choice = int(Prompt.ask("请选择模型", default="1"))
            if 1 <= choice <= len(available_models):
                return available_models[choice - 1]
            else:
                console.print(f"[red]❌[/red] 请输入1-{len(available_models)}之间的数字")
        except ValueError:
            console.print("[red]❌[/red] 请输入有效的数字")

def update_env_file(provider, api_key, env_var, model):
    """更新.env文件"""
    env_file = Path(".env")
    if not env_file.exists():
        create_env_file()
    
    # 读取现有内容
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 更新配置
    content = content.replace("LLM_PROVIDER=openai", f"LLM_PROVIDER={provider}")
    content = content.replace("LLM_MODEL=gpt-4o-mini", f"LLM_MODEL={model}")
    content = content.replace(f"{env_var}=your_{provider}_api_key_here", f"{env_var}={api_key}")
    
    # 写回文件
    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)
    
    console.print("[green]✅[/green] .env 文件已更新")

def verify_configuration():
    """验证配置"""
    console.print("\n[bold blue]🔍 验证配置[/bold blue]")
    
    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from src.configs.config import Config
        from src.llm.llm_factory import LLMFactory
        
        # 检查LLM配置
        llm_config = Config.get_llm_config()
        
        table = Table(title="LLM配置状态")
        table.add_column("配置项", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("值", style="yellow")
        
        # 检查各个配置项
        config_items = [
            ("提供商", llm_config['provider']),
            ("模型", llm_config['model']),
            ("温度", str(llm_config['temperature'])),
            ("最大Token数", str(llm_config['max_tokens'])),
            ("API密钥", "已配置" if llm_config['api_key'] else "未配置")
        ]
        
        for item, value in config_items:
            status = "✅ 已配置" if value and value != "未配置" else "❌ 未配置"
            table.add_row(item, status, str(value))
        
        console.print(table)
        
        # 验证配置有效性
        if Config.validate_llm_config():
            console.print("[green]✅[/green] LLM配置验证成功！")
            
            # 尝试创建LLM实例
            try:
                llm_instance = LLMFactory.create_llm(**llm_config)
                console.print(f"[green]✅[/green] LLM实例创建成功: {llm_instance}")
                return True
            except Exception as e:
                console.print(f"[red]❌[/red] LLM实例创建失败: {str(e)}")
                return False
        else:
            console.print("[red]❌[/red] LLM配置验证失败")
            return False
            
    except ImportError as e:
        console.print(f"[red]❌[/red] 导入失败: {str(e)}")
        console.print("[yellow]💡[/yellow] 请确保已安装所有依赖")
        return False

def show_next_steps():
    """显示后续步骤"""
    console.print("\n[bold blue]🚀 后续步骤[/bold blue]")
    
    steps = [
        "运行配置检查: python main.py config",
        "查看LLM提供商信息: python main.py llm",
        "执行测试调研: python main.py research --query '测试查询' --verbose",
        "运行可视化演示: python examples/langsmith_visualization_example.py"
    ]
    
    for i, step in enumerate(steps, 1):
        console.print(f"[green]{i}.[/green] {step}")
    
    console.print("\n[yellow]💡[/yellow] 提示: 现在您可以使用不同的LLM提供商进行技术调研了！")

def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold blue]LLM 配置管理[/bold blue]\n"
        "为 DeepDive Analyst 项目配置多LLM提供商支持",
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
    
    # 显示LLM提供商信息
    show_llm_providers()
    
    # 获取用户选择
    if Confirm.ask("是否现在配置LLM提供商？"):
        provider = get_provider_choice()
        api_key, env_var = get_api_key(provider)
        model = get_model_choice(provider)
        
        if api_key:
            update_env_file(provider, api_key, env_var, model)
            console.print("[green]✅[/green] LLM配置完成")
        else:
            console.print("[red]❌[/red] 未提供API密钥")
            return
    else:
        console.print("[yellow]💡[/yellow] 您可以稍后手动编辑 .env 文件来配置LLM")
        return
    
    # 最终验证
    console.print("\n[bold blue]🔍 最终验证[/bold blue]")
    if verify_configuration():
        show_next_steps()
    else:
        console.print("[red]❌[/red] 配置验证失败，请检查配置")

if __name__ == "__main__":
    main()
