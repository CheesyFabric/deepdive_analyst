"""
LLM 工厂类
负责创建和管理不同的LLM实例
"""

from typing import Dict, Any, Optional, List
from loguru import logger
from .base_llm import BaseLLM, LLMConfig
from .providers import (
    OpenAIProvider,
    GeminiProvider,
    QwenProvider,
    AnthropicProvider
)


class LLMFactory:
    """LLM工厂类"""
    
    # 支持的提供商映射
    PROVIDERS = {
        'openai': OpenAIProvider,
        'gemini': GeminiProvider,
        'qwen': QwenProvider,
        'anthropic': AnthropicProvider
    }
    
    @classmethod
    def create_llm(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> BaseLLM:
        """
        创建LLM实例
        
        Args:
            provider: LLM提供商 (openai, gemini, qwen, anthropic)
            model: 模型名称
            api_key: API密钥
            temperature: 温度参数
            max_tokens: 最大token数
            base_url: 基础URL
            timeout: 超时时间
            max_retries: 最大重试次数
            extra_params: 额外参数
            
        Returns:
            LLM实例
            
        Raises:
            ValueError: 不支持的提供商
            ImportError: 缺少必要的依赖
        """
        provider = provider.lower()
        
        if provider not in self.PROVIDERS:
            available_providers = list(self.PROVIDERS.keys())
            raise ValueError(f"不支持的LLM提供商: {provider}。支持的提供商: {available_providers}")
        
        # 创建配置
        config = LLMConfig(
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            extra_params=extra_params
        )
        
        # 获取提供商类
        provider_class = self.PROVIDERS[provider]
        
        try:
            # 创建实例
            llm_instance = provider_class(config)
            logger.info(f"成功创建LLM实例: {provider}:{model}")
            return llm_instance
        except Exception as e:
            logger.error(f"创建LLM实例失败: {provider}:{model}, 错误: {str(e)}")
            raise
    
    @classmethod
    def create_from_config(cls, config_dict: Dict[str, Any]) -> BaseLLM:
        """
        从配置字典创建LLM实例
        
        Args:
            config_dict: 配置字典
            
        Returns:
            LLM实例
        """
        required_fields = ['provider', 'model']
        for field in required_fields:
            if field not in config_dict:
                raise ValueError(f"配置缺少必需字段: {field}")
        
        return cls.create_llm(**config_dict)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """
        获取支持的提供商列表
        
        Returns:
            支持的提供商列表
        """
        return list(cls.PROVIDERS.keys())
    
    @classmethod
    def get_available_models(cls, provider: str) -> List[str]:
        """
        获取指定提供商的可用模型列表
        
        Args:
            provider: LLM提供商
            
        Returns:
            可用模型列表
        """
        provider = provider.lower()
        
        if provider not in cls.PROVIDERS:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        try:
            # 创建临时实例来获取模型列表
            provider_class = cls.PROVIDERS[provider]
            temp_config = LLMConfig(
                provider=provider,
                model="dummy",  # 临时模型名
                api_key="dummy"  # 临时API密钥
            )
            temp_instance = provider_class(temp_config)
            return temp_instance.get_available_models()
        except Exception as e:
            logger.warning(f"无法获取{provider}的模型列表: {str(e)}")
            # 返回默认模型列表
            default_models = {
                'openai': ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                'gemini': ["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash"],
                'qwen': ["qwen-turbo", "qwen-plus", "qwen-max"],
                'anthropic': ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
            }
            return default_models.get(provider, [])
    
    @classmethod
    def validate_provider_config(cls, provider: str, config_dict: Dict[str, Any]) -> bool:
        """
        验证提供商配置
        
        Args:
            provider: LLM提供商
            config_dict: 配置字典
            
        Returns:
            配置是否有效
        """
        provider = provider.lower()
        
        if provider not in cls.PROVIDERS:
            return False
        
        # 检查必需字段
        required_fields = ['model']
        for field in required_fields:
            if field not in config_dict:
                return False
        
        # 检查API密钥
        if not config_dict.get('api_key'):
            return False
        
        return True
    
    @classmethod
    def get_provider_info(cls, provider: str) -> Dict[str, Any]:
        """
        获取提供商信息
        
        Args:
            provider: LLM提供商
            
        Returns:
            提供商信息字典
        """
        provider = provider.lower()
        
        if provider not in cls.PROVIDERS:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        info = {
            'name': provider,
            'class': cls.PROVIDERS[provider].__name__,
            'available_models': cls.get_available_models(provider),
            'description': cls._get_provider_description(provider)
        }
        
        return info
    
    @classmethod
    def _get_provider_description(cls, provider: str) -> str:
        """获取提供商描述"""
        descriptions = {
            'openai': 'OpenAI GPT系列模型，包括GPT-4和GPT-3.5',
            'gemini': 'Google Gemini系列模型，包括Gemini Pro和Flash',
            'qwen': '阿里通义千问系列模型，包括Qwen Turbo和Max',
            'anthropic': 'Anthropic Claude系列模型，包括Claude 3.5 Sonnet'
        }
        return descriptions.get(provider, '未知提供商')
