"""
LLM 提供商实现
支持多种LLM提供商的实现
"""

import os
from typing import Any, Dict, List, Optional, Iterator
from loguru import logger
from .base_llm import BaseLLM, LLMConfig, LLMResponse


class OpenAIProvider(BaseLLM):
    """OpenAI LLM 提供商"""
    
    def _initialize_client(self):
        """初始化OpenAI客户端"""
        try:
            from langchain_openai import ChatOpenAI
            self._client = ChatOpenAI(
                model=self.config.model,
                temperature=self.config.temperature,
                api_key=self.config.api_key,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
                **(self.config.extra_params or {})
            )
            logger.info(f"OpenAI客户端初始化成功: {self.config.model}")
        except ImportError:
            logger.error("langchain_openai 未安装，请运行: pip install langchain-openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {str(e)}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本"""
        try:
            response = self._client.invoke(prompt)
            return LLMResponse(
                content=response.content,
                usage=getattr(response, 'usage_metadata', None),
                model=self.config.model,
                finish_reason=getattr(response, 'finish_reason', None),
                success=True
            )
        except Exception as e:
            logger.error(f"OpenAI生成失败: {str(e)}")
            return LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[LLMResponse]:
        """流式生成文本"""
        try:
            for chunk in self._client.stream(prompt):
                yield LLMResponse(
                    content=chunk.content,
                    model=self.config.model,
                    success=True
                )
        except Exception as e:
            logger.error(f"OpenAI流式生成失败: {str(e)}")
            yield LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]


class GeminiProvider(BaseLLM):
    """Google Gemini LLM 提供商"""
    
    def _initialize_client(self):
        """初始化Gemini客户端"""
        try:
            import google.generativeai as genai
            
            # 配置API密钥
            genai.configure(api_key=self.config.api_key)
            
            # 处理模型名称格式
            model_name = self.config.model
            if model_name.startswith('gemini/'):
                model_name = model_name.replace('gemini/', '')
            
            # 创建模型
            self._client = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    'temperature': self.config.temperature,
                    'max_output_tokens': self.config.max_tokens,
                    **(self.config.extra_params or {})
                }
            )
            logger.info(f"Gemini客户端初始化成功: {model_name}")
        except ImportError:
            logger.error("google-generativeai 未安装，请运行: pip install google-generativeai")
            raise
        except Exception as e:
            logger.error(f"Gemini客户端初始化失败: {str(e)}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本"""
        try:
            response = self._client.generate_content(prompt)
            return LLMResponse(
                content=response.text,
                model=self.config.model,
                success=True
            )
        except Exception as e:
            logger.error(f"Gemini生成失败: {str(e)}")
            return LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[LLMResponse]:
        """流式生成文本"""
        try:
            response = self._client.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield LLMResponse(
                        content=chunk.text,
                        model=self.config.model,
                        success=True
                    )
        except Exception as e:
            logger.error(f"Gemini流式生成失败: {str(e)}")
            yield LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "gemini/gemini-1.5-pro",
            "gemini/gemini-1.5-flash",
            "gemini/gemini-1.0-pro",
            "gemini/gemini-pro-vision"
        ]


class QwenProvider(BaseLLM):
    """阿里通义千问 LLM 提供商"""
    
    def _initialize_client(self):
        """初始化Qwen客户端"""
        try:
            from dashscope import Generation
            
            self._client = Generation()
            logger.info(f"Qwen客户端初始化成功: {self.config.model}")
        except ImportError:
            logger.error("dashscope 未安装，请运行: pip install dashscope")
            raise
        except Exception as e:
            logger.error(f"Qwen客户端初始化失败: {str(e)}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本"""
        try:
            response = self._client.call(
                model=self.config.model,
                prompt=prompt,
                api_key=self.config.api_key,
                **(self.config.extra_params or {})
            )
            
            if response.status_code == 200:
                return LLMResponse(
                    content=response.output.text,
                    model=self.config.model,
                    success=True
                )
            else:
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=f"Qwen API错误: {response.message}"
                )
        except Exception as e:
            logger.error(f"Qwen生成失败: {str(e)}")
            return LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[LLMResponse]:
        """流式生成文本"""
        try:
            responses = self._client.call(
                model=self.config.model,
                prompt=prompt,
                api_key=self.config.api_key,
                stream=True,
                **(self.config.extra_params or {})
            )
            
            for response in responses:
                if response.status_code == 200:
                    yield LLMResponse(
                        content=response.output.text,
                        model=self.config.model,
                        success=True
                    )
                else:
                    yield LLMResponse(
                        content="",
                        success=False,
                        error_message=f"Qwen API错误: {response.message}"
                    )
        except Exception as e:
            logger.error(f"Qwen流式生成失败: {str(e)}")
            yield LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "qwen-turbo",
            "qwen-plus",
            "qwen-max",
            "qwen-max-longcontext",
            "qwen2-turbo",
            "qwen2-plus",
            "qwen2-max"
        ]


class AnthropicProvider(BaseLLM):
    """Anthropic Claude LLM 提供商"""
    
    def _initialize_client(self):
        """初始化Anthropic客户端"""
        try:
            from langchain_anthropic import ChatAnthropic
            
            self._client = ChatAnthropic(
                model=self.config.model,
                temperature=self.config.temperature,
                api_key=self.config.api_key,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
                **(self.config.extra_params or {})
            )
            logger.info(f"Anthropic客户端初始化成功: {self.config.model}")
        except ImportError:
            logger.error("langchain_anthropic 未安装，请运行: pip install langchain-anthropic")
            raise
        except Exception as e:
            logger.error(f"Anthropic客户端初始化失败: {str(e)}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本"""
        try:
            response = self._client.invoke(prompt)
            return LLMResponse(
                content=response.content,
                usage=getattr(response, 'usage_metadata', None),
                model=self.config.model,
                finish_reason=getattr(response, 'finish_reason', None),
                success=True
            )
        except Exception as e:
            logger.error(f"Anthropic生成失败: {str(e)}")
            return LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[LLMResponse]:
        """流式生成文本"""
        try:
            for chunk in self._client.stream(prompt):
                yield LLMResponse(
                    content=chunk.content,
                    model=self.config.model,
                    success=True
                )
        except Exception as e:
            logger.error(f"Anthropic流式生成失败: {str(e)}")
            yield LLMResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
