#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timing Module - HTTP Request Timing Analysis Core
HTTP请求计时分析核心模块
"""

import time
import socket
import ssl
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class TimingResult:
    """HTTP请求计时结果数据类"""
    
    # URL信息
    url: str
    method: str = "GET"
    
    # 各阶段计时（毫秒）
    dns_time: float = 0.0
    connect_time: float = 0.0
    tls_time: float = 0.0
    request_time: float = 0.0
    first_byte_time: float = 0.0
    download_time: float = 0.0
    total_time: float = 0.0
    
    # 响应信息
    status_code: int = 0
    response_size: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    
    # 时间戳
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 错误信息
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "url": self.url,
            "method": self.method,
            "timing": {
                "dns_ms": round(self.dns_time, 2),
                "connect_ms": round(self.connect_time, 2),
                "tls_ms": round(self.tls_time, 2),
                "request_ms": round(self.request_time, 2),
                "first_byte_ms": round(self.first_byte_time, 2),
                "download_ms": round(self.download_time, 2),
                "total_ms": round(self.total_time, 2),
            },
            "response": {
                "status_code": self.status_code,
                "size_bytes": self.response_size,
                "headers": self.headers,
            },
            "timestamp": self.timestamp,
            "error": self.error,
        }
    
    def get_waterfall_data(self) -> List[Tuple[str, float, float]]:
        """获取瀑布图数据 (阶段名, 开始时间, 持续时间)"""
        start = 0.0
        waterfall = []
        
        if self.dns_time > 0:
            waterfall.append(("DNS", start, self.dns_time))
            start += self.dns_time
        
        if self.connect_time > 0:
            waterfall.append(("Connect", start, self.connect_time))
            start += self.connect_time
        
        if self.tls_time > 0:
            waterfall.append(("TLS", start, self.tls_time))
            start += self.tls_time
        
        if self.request_time > 0:
            waterfall.append(("Request", start, self.request_time))
            start += self.request_time
        
        if self.first_byte_time > 0:
            waterfall.append(("TTFB", start, self.first_byte_time))
            start += self.first_byte_time
        
        if self.download_time > 0:
            waterfall.append(("Download", start, self.download_time))
        
        return waterfall


class TimingAnalyzer:
    """HTTP请求计时分析器"""
    
    def __init__(self, timeout: float = 30.0):
        """
        初始化计时分析器
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self._results: List[TimingResult] = []
    
    def analyze(self, url: str, method: str = "GET", 
                headers: Optional[Dict[str, str]] = None,
                data: Optional[bytes] = None) -> TimingResult:
        """
        分析HTTP请求计时
        
        Args:
            url: 请求URL
            method: 请求方法
            headers: 请求头
            data: 请求体数据
            
        Returns:
            TimingResult: 计时结果
        """
        result = TimingResult(url=url, method=method)
        
        try:
            # 解析URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            is_https = parsed.scheme == "https"
            
            # 1. DNS解析计时
            dns_start = time.perf_counter()
            try:
                ip = socket.gethostbyname(host)
                result.dns_time = (time.perf_counter() - dns_start) * 1000
            except socket.gaierror as e:
                result.error = f"DNS解析失败: {e}"
                return result
            
            # 2. TCP连接计时
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            connect_start = time.perf_counter()
            try:
                sock.connect((ip, port))
                result.connect_time = (time.perf_counter() - connect_start) * 1000
            except (socket.timeout, ConnectionRefusedError) as e:
                result.error = f"连接失败: {e}"
                sock.close()
                return result
            
            # 3. TLS握手计时（HTTPS）
            if is_https:
                context = ssl.create_default_context()
                tls_start = time.perf_counter()
                try:
                    sock = context.wrap_socket(sock, server_hostname=host)
                    result.tls_time = (time.perf_counter() - tls_start) * 1000
                except ssl.SSLError as e:
                    result.error = f"TLS握手失败: {e}"
                    sock.close()
                    return result
            
            # 4. 发送HTTP请求
            request_line = f"{method} {parsed.path or '/'}{('?' + parsed.query) if parsed.query else ''} HTTP/1.1\r\n"
            request_headers = f"Host: {host}\r\nConnection: close\r\n"
            
            if headers:
                for key, value in headers.items():
                    request_headers += f"{key}: {value}\r\n"
            
            if data:
                request_headers += f"Content-Length: {len(data)}\r\n"
            
            request_data = (request_line + request_headers + "\r\n").encode()
            if data:
                request_data += data
            
            request_start = time.perf_counter()
            sock.sendall(request_data)
            result.request_time = (time.perf_counter() - request_start) * 1000
            
            # 5. 接收首字节（TTFB）
            first_byte_start = time.perf_counter()
            response_data = b""
            try:
                chunk = sock.recv(4096)
                if chunk:
                    result.first_byte_time = (time.perf_counter() - first_byte_start) * 1000
                    response_data += chunk
            except socket.timeout:
                result.error = "接收响应超时"
                sock.close()
                return result
            
            # 6. 下载剩余内容
            download_start = time.perf_counter()
            while True:
                try:
                    chunk = sock.recv(8192)
                    if not chunk:
                        break
                    response_data += chunk
                except socket.timeout:
                    break
            
            result.download_time = (time.perf_counter() - download_start) * 1000
            result.total_time = result.dns_time + result.connect_time + result.tls_time + \
                               result.request_time + result.first_byte_time + result.download_time
            
            sock.close()
            
            # 解析响应
            self._parse_response(response_data, result)
            
        except Exception as e:
            result.error = f"请求异常: {str(e)}"
        
        self._results.append(result)
        return result
    
    def _parse_response(self, response_data: bytes, result: TimingResult):
        """解析HTTP响应"""
        try:
            # 分离头部和主体
            header_end = response_data.find(b"\r\n\r\n")
            if header_end == -1:
                return
            
            headers_data = response_data[:header_end].decode("utf-8", errors="ignore")
            body = response_data[header_end + 4:]
            
            # 解析状态行
            lines = headers_data.split("\r\n")
            if lines:
                status_line = lines[0].split()
                if len(status_line) >= 2:
                    result.status_code = int(status_line[1])
            
            # 解析响应头
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    result.headers[key.strip()] = value.strip()
            
            result.response_size = len(body)
            
        except Exception:
            pass
    
    def get_results(self) -> List[TimingResult]:
        """获取所有计时结果"""
        return self._results.copy()
    
    def clear_results(self):
        """清空结果"""
        self._results.clear()
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self._results:
            return {}
        
        successful = [r for r in self._results if r.error is None]
        
        if not successful:
            return {"total_requests": len(self._results), "failed": len(self._results)}
        
        return {
            "total_requests": len(self._results),
            "successful": len(successful),
            "failed": len(self._results) - len(successful),
            "avg_dns": sum(r.dns_time for r in successful) / len(successful),
            "avg_connect": sum(r.connect_time for r in successful) / len(successful),
            "avg_tls": sum(r.tls_time for r in successful) / len(successful),
            "avg_ttfb": sum(r.first_byte_time for r in successful) / len(successful),
            "avg_total": sum(r.total_time for r in successful) / len(successful),
            "min_total": min(r.total_time for r in successful),
            "max_total": max(r.total_time for r in successful),
        }
