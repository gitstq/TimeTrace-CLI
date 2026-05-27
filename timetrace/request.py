#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Request Module - HTTP Request Builder and Executor
HTTP请求构建与执行模块
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class RequestConfig:
    """请求配置数据类"""
    
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    timeout: float = 30.0
    follow_redirects: bool = True
    verify_ssl: bool = True
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "body": self.body,
            "timeout": self.timeout,
            "follow_redirects": self.follow_redirects,
            "verify_ssl": self.verify_ssl,
        }


class RequestBuilder:
    """HTTP请求构建器"""
    
    def __init__(self):
        """初始化请求构建器"""
        self._config: Optional[RequestConfig] = None
    
    def url(self, url: str) -> "RequestBuilder":
        """设置URL"""
        self._validate_url(url)
        if self._config is None:
            self._config = RequestConfig(url=url)
        else:
            self._config.url = url
        return self
    
    def method(self, method: str) -> "RequestBuilder":
        """设置请求方法"""
        method = method.upper()
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        if method not in valid_methods:
            raise ValueError(f"无效的HTTP方法: {method}")
        if self._config:
            self._config.method = method
        return self
    
    def header(self, key: str, value: str) -> "RequestBuilder":
        """添加请求头"""
        if self._config:
            self._config.headers[key] = value
        return self
    
    def headers(self, headers: Dict[str, str]) -> "RequestBuilder":
        """批量设置请求头"""
        if self._config:
            self._config.headers.update(headers)
        return self
    
    def json_body(self, data: Any) -> "RequestBuilder":
        """设置JSON请求体"""
        if self._config:
            self._config.body = json.dumps(data)
            self._config.headers["Content-Type"] = "application/json"
        return self
    
    def text_body(self, text: str) -> "RequestBuilder":
        """设置文本请求体"""
        if self._config:
            self._config.body = text
        return self
    
    def timeout(self, seconds: float) -> "RequestBuilder":
        """设置超时时间"""
        if self._config:
            self._config.timeout = seconds
        return self
    
    def build(self) -> RequestConfig:
        """构建请求配置"""
        if self._config is None:
            raise ValueError("未设置URL")
        return self._config
    
    def _validate_url(self, url: str):
        """验证URL格式"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"无效的URL格式: {url}")
            if parsed.scheme not in ["http", "https"]:
                raise ValueError(f"不支持的协议: {parsed.scheme}")
        except Exception as e:
            raise ValueError(f"URL解析错误: {e}")


class RequestExecutor:
    """HTTP请求执行器"""
    
    def __init__(self):
        """初始化请求执行器"""
        self._history: List[RequestConfig] = []
    
    def execute(self, config: RequestConfig) -> Dict:
        """
        执行HTTP请求（简化版，实际计时由TimingAnalyzer完成）
        
        Args:
            config: 请求配置
            
        Returns:
            执行结果字典
        """
        self._history.append(config)
        
        return {
            "url": config.url,
            "method": config.method,
            "headers": config.headers,
            "body": config.body,
            "timestamp": self._get_timestamp(),
        }
    
    def get_history(self) -> List[RequestConfig]:
        """获取请求历史"""
        return self._history.copy()
    
    def clear_history(self):
        """清空历史"""
        self._history.clear()
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


class RequestCollection:
    """请求集合管理器"""
    
    def __init__(self):
        """初始化请求集合"""
        self._requests: Dict[str, RequestConfig] = {}
    
    def add(self, name: str, config: RequestConfig):
        """添加命名请求"""
        self._requests[name] = config
    
    def get(self, name: str) -> Optional[RequestConfig]:
        """获取命名请求"""
        return self._requests.get(name)
    
    def remove(self, name: str):
        """移除命名请求"""
        if name in self._requests:
            del self._requests[name]
    
    def list_names(self) -> List[str]:
        """列出所有请求名称"""
        return list(self._requests.keys())
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {name: config.to_dict() for name, config in self._requests.items()}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RequestCollection":
        """从字典创建"""
        collection = cls()
        for name, config_dict in data.items():
            config = RequestConfig(
                url=config_dict.get("url", ""),
                method=config_dict.get("method", "GET"),
                headers=config_dict.get("headers", {}),
                body=config_dict.get("body"),
                timeout=config_dict.get("timeout", 30.0),
            )
            collection.add(name, config)
        return collection
