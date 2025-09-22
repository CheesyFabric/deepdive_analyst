"""
安全的日志工具模块
用于在资源清理时安全地记录日志，避免 I/O 错误
"""

from loguru import logger
import threading
import atexit
from typing import Optional


class SafeLogger:
    """安全的日志记录器"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._closed = False
        self._register_cleanup()
    
    def _register_cleanup(self):
        """注册清理函数"""
        atexit.register(self._cleanup)
    
    def _cleanup(self):
        """清理资源"""
        with self._lock:
            self._closed = True
    
    def debug(self, message: str) -> None:
        """安全地记录调试信息"""
        if self._closed:
            return
        
        try:
            with self._lock:
                if not self._closed:
                    logger.debug(message)
        except Exception:
            # 忽略日志记录错误，避免在清理时出现异常
            pass
    
    def info(self, message: str) -> None:
        """安全地记录信息"""
        if self._closed:
            return
        
        try:
            with self._lock:
                if not self._closed:
                    logger.info(message)
        except Exception:
            pass
    
    def warning(self, message: str) -> None:
        """安全地记录警告"""
        if self._closed:
            return
        
        try:
            with self._lock:
                if not self._closed:
                    logger.warning(message)
        except Exception:
            pass
    
    def error(self, message: str) -> None:
        """安全地记录错误"""
        if self._closed:
            return
        
        try:
            with self._lock:
                if not self._closed:
                    logger.error(message)
        except Exception:
            pass


# 创建全局安全日志记录器实例
safe_logger = SafeLogger()


def safe_log_debug(message: str) -> None:
    """安全地记录调试信息的便捷函数"""
    safe_logger.debug(message)


def safe_log_info(message: str) -> None:
    """安全地记录信息的便捷函数"""
    safe_logger.info(message)


def safe_log_warning(message: str) -> None:
    """安全地记录警告的便捷函数"""
    safe_logger.warning(message)


def safe_log_error(message: str) -> None:
    """安全地记录错误的便捷函数"""
    safe_logger.error(message)
