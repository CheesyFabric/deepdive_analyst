"""
LLM 基础抽象类
定义统一的LLM接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM配置数据类"""
    provider: str
    model: str
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class BaseLLM(ABC):
    """LLM基础抽象类"""
    
    def __init__(self, config: LLMConfig):
        """
        初始化LLM
        
        Args:
            config: LLM配置
        """
        self.config = config
        self._client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """初始化LLM客户端"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 额外参数
            
        Returns:
            LLM响应
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs):
        """
        流式生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 额外参数
            
        Yields:
            LLM响应块
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表
        
        Returns:
            模型列表
        """
        pass
    
    def validate_config(self) -> bool:
        """
        验证配置
        
        Returns:
            配置是否有效
        """
        if not self.config.api_key:
            return False
        if not self.config.model:
            return False
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            'provider': self.config.provider,
            'model': self.config.model,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens,
            'base_url': self.config.base_url
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.config.provider}:{self.config.model}"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"BaseLLM(provider={self.config.provider}, model={self.config.model})"
