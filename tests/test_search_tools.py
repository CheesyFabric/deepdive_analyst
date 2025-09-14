"""
搜索工具测试模块
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.tools.search_tools import SearchToolsManager, WebScrapingTool, SearchResult


class TestWebScrapingTool:
    """网页抓取工具测试"""
    
    def test_init(self):
        """测试初始化"""
        tool = WebScrapingTool(timeout=10)
        assert tool.timeout == 10
        assert tool.session is not None
    
    def test_clean_text(self):
        """测试文本清理功能"""
        tool = WebScrapingTool()
        
        # 测试清理多余空白
        dirty_text = "   line1   \n\n   line2   \n   \n   line3   "
        cleaned = tool._clean_text(dirty_text)
        expected = "line1\nline2\nline3"
        assert cleaned == expected
    
    @patch('requests.Session.get')
    def test_scrape_url_success(self, mock_get):
        """测试成功抓取URL"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><head><title>Test Page</title></head><body><p>Test content</p></body></html>'
        mock_get.return_value = mock_response
        
        tool = WebScrapingTool()
        result = tool.scrape_url("https://example.com")
        
        assert result['url'] == "https://example.com"
        assert result['title'] == "Test Page"
        assert "Test content" in result['content']
        assert result['status_code'] == 200
    
    @patch('requests.Session.get')
    def test_scrape_url_failure(self, mock_get):
        """测试抓取URL失败"""
        # 模拟请求异常
        mock_get.side_effect = Exception("Network error")
        
        tool = WebScrapingTool()
        result = tool.scrape_url("https://example.com")
        
        assert result['url'] == "https://example.com"
        assert result['title'] == ""
        assert result['content'] == ""
        assert 'error' in result


class TestSearchToolsManager:
    """搜索工具管理器测试"""
    
    def test_init_without_tavily(self):
        """测试在没有Tavily API密钥时初始化"""
        with patch.dict(os.environ, {}, clear=True):
            manager = SearchToolsManager()
            assert manager.tavily_tool is None
            assert manager.web_scraping_tool is not None
    
    @patch('src.tools.search_tools.TavilySearchTool')
    def test_init_with_tavily(self, mock_tavily_class):
        """测试在有Tavily API密钥时初始化"""
        mock_tavily_instance = Mock()
        mock_tavily_class.return_value = mock_tavily_instance
        
        manager = SearchToolsManager("test_api_key")
        assert manager.tavily_tool == mock_tavily_instance
        assert manager.web_scraping_tool is not None


class TestSearchResult:
    """搜索结果测试"""
    
    def test_search_result_creation(self):
        """测试搜索结果创建"""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            content="Test content",
            score=0.95,
            published_date="2024-01-01"
        )
        
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.content == "Test content"
        assert result.score == 0.95
        assert result.published_date == "2024-01-01"


if __name__ == "__main__":
    pytest.main([__file__])
