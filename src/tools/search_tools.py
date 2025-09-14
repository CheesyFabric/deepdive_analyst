"""
搜索工具模块
集成Tavily搜索API和其他网络搜索功能
"""

import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from loguru import logger

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None
    logger.warning("Tavily客户端未安装，请运行: pip install tavily-python")


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None


class TavilySearchTool:
    """Tavily搜索工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Tavily搜索工具
        
        Args:
            api_key: Tavily API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY环境变量未设置")
        
        if TavilyClient is None:
            raise ImportError("Tavily客户端未安装，请运行: pip install tavily-python")
        
        self.client = TavilyClient(api_key=self.api_key)
        logger.info("Tavily搜索工具初始化成功")
    
    def search(
        self, 
        query: str, 
        max_results: int = 10,
        search_depth: str = "advanced",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        执行搜索查询
        
        Args:
            query: 搜索查询字符串
            max_results: 最大结果数量
            search_depth: 搜索深度 ("basic" 或 "advanced")
            include_domains: 包含的域名列表
            exclude_domains: 排除的域名列表
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"开始搜索: {query}")
            
            # 构建搜索参数
            search_params = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": True,
                "include_raw_content": True
            }
            
            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            
            # 执行搜索
            response = self.client.search(**search_params)
            
            # 解析结果
            results = []
            for item in response.get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    published_date=item.get("published_date")
                )
                results.append(result)
            
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise
    
    def search_with_context(
        self, 
        query: str, 
        context: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """
        基于上下文进行搜索
        
        Args:
            query: 搜索查询字符串
            context: 上下文信息
            max_results: 最大结果数量
            
        Returns:
            搜索结果列表
        """
        # 将上下文信息整合到查询中
        enhanced_query = f"{query} {context}"
        return self.search(enhanced_query, max_results)


class WebScrapingTool:
    """网页抓取工具"""
    
    def __init__(self, timeout: int = 30):
        """
        初始化网页抓取工具
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("网页抓取工具初始化成功")
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        抓取指定URL的内容
        
        Args:
            url: 要抓取的URL
            
        Returns:
            包含标题、内容和元数据的字典
        """
        try:
            logger.info(f"开始抓取URL: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析HTML内容
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # 提取主要内容（优先选择article、main等标签）
            content_selectors = [
                'article',
                'main',
                '.content',
                '.post-content',
                '.entry-content',
                'body'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text().strip()
                    break
            
            # 如果没有找到特定内容区域，使用整个body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text().strip()
            
            # 清理内容
            content = self._clean_text(content)
            
            result = {
                'url': url,
                'title': title_text,
                'content': content,
                'status_code': response.status_code,
                'content_length': len(content)
            }
            
            logger.info(f"抓取完成，内容长度: {len(content)} 字符")
            return result
            
        except requests.RequestException as e:
            logger.error(f"抓取URL失败: {str(e)}")
            return {
                'url': url,
                'title': "",
                'content': "",
                'error': str(e),
                'status_code': 0
            }
        except Exception as e:
            logger.error(f"解析内容失败: {str(e)}")
            return {
                'url': url,
                'title': "",
                'content': "",
                'error': str(e),
                'status_code': 0
            }
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # 只保留非空行
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        批量抓取多个URL
        
        Args:
            urls: URL列表
            
        Returns:
            抓取结果列表
        """
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
            # 添加延迟避免过于频繁的请求
            time.sleep(1)
        
        return results


class SearchToolsManager:
    """搜索工具管理器"""
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        """
        初始化搜索工具管理器
        
        Args:
            tavily_api_key: Tavily API密钥
        """
        self.tavily_tool = None
        self.web_scraping_tool = WebScrapingTool()
        
        # 尝试初始化Tavily工具
        try:
            self.tavily_tool = TavilySearchTool(tavily_api_key)
            logger.info("搜索工具管理器初始化成功")
        except Exception as e:
            logger.warning(f"Tavily工具初始化失败: {str(e)}")
    
    def comprehensive_search(
        self, 
        query: str, 
        max_results: int = 10,
        scrape_content: bool = True
    ) -> List[Dict[str, Any]]:
        """
        综合搜索功能
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            scrape_content: 是否抓取详细内容
            
        Returns:
            综合搜索结果
        """
        results = []
        
        # 使用Tavily搜索
        if self.tavily_tool:
            try:
                search_results = self.tavily_tool.search(query, max_results)
                
                for result in search_results:
                    result_dict = {
                        'title': result.title,
                        'url': result.url,
                        'content': result.content,
                        'score': result.score,
                        'published_date': result.published_date,
                        'source': 'tavily'
                    }
                    
                    # 如果需要抓取详细内容
                    if scrape_content and result.url:
                        scraped_content = self.web_scraping_tool.scrape_url(result.url)
                        if scraped_content.get('content'):
                            result_dict['detailed_content'] = scraped_content['content']
                    
                    results.append(result_dict)
                    
            except Exception as e:
                logger.error(f"Tavily搜索失败: {str(e)}")
        
        logger.info(f"综合搜索完成，返回 {len(results)} 个结果")
        return results
