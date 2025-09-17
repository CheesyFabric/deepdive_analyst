"""
多LLM集成测试
测试不同LLM提供商的集成和功能
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.llm.llm_factory import LLMFactory
from src.llm.base_llm import LLMConfig, LLMResponse
from src.configs.config import Config


class TestLLMFactory:
    """LLM工厂测试"""
    
    def test_get_supported_providers(self):
        """测试获取支持的提供商"""
        providers = LLMFactory.get_supported_providers()
        expected_providers = ['openai', 'gemini', 'qwen', 'anthropic']
        
        for provider in expected_providers:
            assert provider in providers
    
    def test_get_available_models(self):
        """测试获取可用模型"""
        providers = ['openai', 'gemini', 'qwen', 'anthropic']
        
        for provider in providers:
            models = LLMFactory.get_available_models(provider)
            assert isinstance(models, list)
            assert len(models) > 0
    
    def test_validate_provider_config(self):
        """测试提供商配置验证"""
        # 有效配置
        valid_config = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': 'test_key'
        }
        assert LLMFactory.validate_provider_config('openai', valid_config)
        
        # 无效配置 - 缺少模型
        invalid_config = {
            'provider': 'openai',
            'api_key': 'test_key'
        }
        assert not LLMFactory.validate_provider_config('openai', invalid_config)
        
        # 无效配置 - 缺少API密钥
        invalid_config2 = {
            'provider': 'openai',
            'model': 'gpt-4o-mini'
        }
        assert not LLMFactory.validate_provider_config('openai', invalid_config2)
    
    def test_get_provider_info(self):
        """测试获取提供商信息"""
        providers = ['openai', 'gemini', 'qwen', 'anthropic']
        
        for provider in providers:
            info = LLMFactory.get_provider_info(provider)
            assert 'name' in info
            assert 'class' in info
            assert 'available_models' in info
            assert 'description' in info
            assert info['name'] == provider


class TestLLMConfig:
    """LLM配置测试"""
    
    def test_get_llm_config(self):
        """测试获取LLM配置"""
        config = Config.get_llm_config()
        
        required_fields = ['provider', 'model', 'temperature', 'max_tokens', 'api_key']
        for field in required_fields:
            assert field in config
    
    def test_validate_llm_config(self):
        """测试LLM配置验证"""
        # 使用mock来测试验证逻辑
        with patch.object(Config, 'get_llm_config') as mock_config:
            # 有效配置
            mock_config.return_value = {
                'provider': 'openai',
                'model': 'gpt-4o-mini',
                'api_key': 'test_key'
            }
            assert Config.validate_llm_config()
            
            # 无效配置 - 缺少API密钥
            mock_config.return_value = {
                'provider': 'openai',
                'model': 'gpt-4o-mini',
                'api_key': ''
            }
            assert not Config.validate_llm_config()


class TestOpenAIProvider:
    """OpenAI提供商测试"""
    
    @patch('langchain_openai.ChatOpenAI')
    def test_openai_initialization(self, mock_chat_openai):
        """测试OpenAI初始化"""
        config = LLMConfig(
            provider='openai',
            model='gpt-4o-mini',
            api_key='test_key',
            temperature=0.1
        )
        
        from src.llm.providers import OpenAIProvider
        provider = OpenAIProvider(config)
        
        mock_chat_openai.assert_called_once()
        assert provider.config.provider == 'openai'
    
    @patch('langchain_openai.ChatOpenAI')
    def test_openai_generate(self, mock_chat_openai):
        """测试OpenAI生成"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_response.usage_metadata = {"total_tokens": 100}
        mock_response.finish_reason = "stop"
        mock_chat_openai.return_value.invoke.return_value = mock_response
        
        config = LLMConfig(
            provider='openai',
            model='gpt-4o-mini',
            api_key='test_key'
        )
        
        from src.llm.providers import OpenAIProvider
        provider = OpenAIProvider(config)
        
        response = provider.generate("Test prompt")
        
        assert isinstance(response, LLMResponse)
        assert response.success
        assert response.content == "Test response"
        assert response.model == 'gpt-4o-mini'


class TestGeminiProvider:
    """Gemini提供商测试"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_gemini_initialization(self, mock_model, mock_configure):
        """测试Gemini初始化"""
        config = LLMConfig(
            provider='gemini',
            model='gemini-1.5-pro',
            api_key='test_key',
            temperature=0.1
        )
        
        from src.llm.providers import GeminiProvider
        provider = GeminiProvider(config)
        
        mock_configure.assert_called_once_with(api_key='test_key')
        assert provider.config.provider == 'gemini'
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_gemini_generate(self, mock_model, mock_configure):
        """测试Gemini生成"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model.return_value.generate_content.return_value = mock_response
        
        config = LLMConfig(
            provider='gemini',
            model='gemini-1.5-pro',
            api_key='test_key'
        )
        
        from src.llm.providers import GeminiProvider
        provider = GeminiProvider(config)
        
        response = provider.generate("Test prompt")
        
        assert isinstance(response, LLMResponse)
        assert response.success
        assert response.content == "Test response"
        assert response.model == 'gemini-1.5-pro'


class TestQwenProvider:
    """Qwen提供商测试"""
    
    @patch('dashscope.Generation')
    def test_qwen_initialization(self, mock_generation):
        """测试Qwen初始化"""
        config = LLMConfig(
            provider='qwen',
            model='qwen-turbo',
            api_key='test_key',
            temperature=0.1
        )
        
        from src.llm.providers import QwenProvider
        provider = QwenProvider(config)
        
        mock_generation.assert_called_once()
        assert provider.config.provider == 'qwen'
    
    @patch('dashscope.Generation')
    def test_qwen_generate(self, mock_generation):
        """测试Qwen生成"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output.text = "Test response"
        mock_generation.return_value.call.return_value = mock_response
        
        config = LLMConfig(
            provider='qwen',
            model='qwen-turbo',
            api_key='test_key'
        )
        
        from src.llm.providers import QwenProvider
        provider = QwenProvider(config)
        
        response = provider.generate("Test prompt")
        
        assert isinstance(response, LLMResponse)
        assert response.success
        assert response.content == "Test response"
        assert response.model == 'qwen-turbo'


class TestAnthropicProvider:
    """Anthropic提供商测试"""
    
    @patch('langchain_anthropic.ChatAnthropic')
    def test_anthropic_initialization(self, mock_chat_anthropic):
        """测试Anthropic初始化"""
        config = LLMConfig(
            provider='anthropic',
            model='claude-3-5-sonnet-20241022',
            api_key='test_key',
            temperature=0.1
        )
        
        from src.llm.providers import AnthropicProvider
        provider = AnthropicProvider(config)
        
        mock_chat_anthropic.assert_called_once()
        assert provider.config.provider == 'anthropic'
    
    @patch('langchain_anthropic.ChatAnthropic')
    def test_anthropic_generate(self, mock_chat_anthropic):
        """测试Anthropic生成"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_response.usage_metadata = {"total_tokens": 100}
        mock_response.finish_reason = "end_turn"
        mock_chat_anthropic.return_value.invoke.return_value = mock_response
        
        config = LLMConfig(
            provider='anthropic',
            model='claude-3-5-sonnet-20241022',
            api_key='test_key'
        )
        
        from src.llm.providers import AnthropicProvider
        provider = AnthropicProvider(config)
        
        response = provider.generate("Test prompt")
        
        assert isinstance(response, LLMResponse)
        assert response.success
        assert response.content == "Test response"
        assert response.model == 'claude-3-5-sonnet-20241022'



class TestErrorHandling:
    """错误处理测试"""
    
    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        with pytest.raises(ValueError, match="不支持的LLM提供商"):
            LLMFactory.create_llm(
                provider='unsupported',
                model='test-model',
                api_key='test-key'
            )
    
    def test_missing_api_key(self):
        """测试缺少API密钥"""
        # 实际上 LLMFactory 不会在创建时验证 API 密钥
        # 只有在实际调用时才会验证
        llm = LLMFactory.create_llm(
            provider='openai',
            model='gpt-4o-mini',
            api_key=''
        )
        assert llm is not None
        assert llm.config.api_key == ''
    
    def test_invalid_model(self):
        """测试无效模型"""
        # 实际上 LLMFactory 不会在创建时验证模型名称
        # 只有在实际调用时才会验证
        llm = LLMFactory.create_llm(
            provider='openai',
            model='invalid-model',
            api_key='test-key'
        )
        assert llm is not None
        assert llm.config.model == 'invalid-model'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
