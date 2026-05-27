#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Module - Performance Analysis and Bottleneck Detection
性能分析与瓶颈检测模块
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """严重程度枚举"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DiagnosticIssue:
    """诊断问题数据类"""
    
    category: str
    message: str
    severity: Severity
    suggestion: str
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "category": self.category,
            "message": self.message,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
        }


@dataclass
class PerformanceScore:
    """性能评分数据类"""
    
    overall: float  # 总体评分 0-100
    dns_score: float = 0.0
    connect_score: float = 0.0
    tls_score: float = 0.0
    ttfb_score: float = 0.0
    download_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "overall": round(self.overall, 1),
            "dns": round(self.dns_score, 1),
            "connect": round(self.connect_score, 1),
            "tls": round(self.tls_score, 1),
            "ttfb": round(self.ttfb_score, 1),
            "download": round(self.download_score, 1),
        }


class PerformanceAnalyzer:
    """性能分析器"""
    
    # 性能阈值配置（毫秒）
    THRESHOLDS = {
        "dns": {"good": 50, "warning": 200},
        "connect": {"good": 100, "warning": 300},
        "tls": {"good": 100, "warning": 300},
        "ttfb": {"good": 200, "warning": 500},
        "download": {"good": 500, "warning": 2000},
        "total": {"good": 1000, "warning": 3000},
    }
    
    def __init__(self):
        """初始化性能分析器"""
        self._issues: List[DiagnosticIssue] = []
    
    def analyze(self, timing_result) -> Tuple[PerformanceScore, List[DiagnosticIssue]]:
        """
        分析计时结果
        
        Args:
            timing_result: TimingResult对象
            
        Returns:
            (性能评分, 问题列表)
        """
        self._issues.clear()
        
        if timing_result.error:
            self._issues.append(DiagnosticIssue(
                category="error",
                message=f"请求失败: {timing_result.error}",
                severity=Severity.CRITICAL,
                suggestion="检查网络连接和URL有效性",
            ))
            return PerformanceScore(overall=0.0), self._issues
        
        # 计算各阶段评分
        dns_score = self._calculate_score(timing_result.dns_time, "dns")
        connect_score = self._calculate_score(timing_result.connect_time, "connect")
        tls_score = self._calculate_score(timing_result.tls_time, "tls")
        ttfb_score = self._calculate_score(timing_result.first_byte_time, "ttfb")
        download_score = self._calculate_score(timing_result.download_time, "download")
        
        # 检测问题
        self._check_dns(timing_result.dns_time)
        self._check_connect(timing_result.connect_time)
        self._check_tls(timing_result.tls_time)
        self._check_ttfb(timing_result.first_byte_time)
        self._check_download(timing_result.download_time)
        
        # 计算总体评分（加权平均）
        weights = {"dns": 0.15, "connect": 0.15, "tls": 0.15, "ttfb": 0.35, "download": 0.20}
        overall = (
            dns_score * weights["dns"] +
            connect_score * weights["connect"] +
            tls_score * weights["tls"] +
            ttfb_score * weights["ttfb"] +
            download_score * weights["download"]
        )
        
        score = PerformanceScore(
            overall=overall,
            dns_score=dns_score,
            connect_score=connect_score,
            tls_score=tls_score,
            ttfb_score=ttfb_score,
            download_score=download_score,
        )
        
        return score, self._issues
    
    def _calculate_score(self, value: float, category: str) -> float:
        """计算单项评分"""
        thresholds = self.THRESHOLDS.get(category, {"good": 100, "warning": 300})
        
        if value <= thresholds["good"]:
            return 100.0
        elif value <= thresholds["warning"]:
            # 线性插值
            ratio = (value - thresholds["good"]) / (thresholds["warning"] - thresholds["good"])
            return 100.0 - ratio * 40.0
        else:
            # 超过警告阈值
            excess = value - thresholds["warning"]
            penalty = min(50.0, excess / thresholds["warning"] * 20.0)
            return max(0.0, 60.0 - penalty)
    
    def _check_dns(self, dns_time: float):
        """检查DNS解析"""
        if dns_time > self.THRESHOLDS["dns"]["warning"]:
            self._issues.append(DiagnosticIssue(
                category="dns",
                message=f"DNS解析耗时过长: {dns_time:.1f}ms",
                severity=Severity.WARNING,
                suggestion="考虑使用更快的DNS服务器或启用DNS缓存",
                metric_value=dns_time,
                threshold=self.THRESHOLDS["dns"]["warning"],
            ))
        elif dns_time > self.THRESHOLDS["dns"]["good"]:
            self._issues.append(DiagnosticIssue(
                category="dns",
                message=f"DNS解析时间偏高: {dns_time:.1f}ms",
                severity=Severity.INFO,
                suggestion="DNS解析速度可接受，但仍有优化空间",
                metric_value=dns_time,
                threshold=self.THRESHOLDS["dns"]["good"],
            ))
    
    def _check_connect(self, connect_time: float):
        """检查TCP连接"""
        if connect_time > self.THRESHOLDS["connect"]["warning"]:
            self._issues.append(DiagnosticIssue(
                category="connect",
                message=f"TCP连接耗时过长: {connect_time:.1f}ms",
                severity=Severity.WARNING,
                suggestion="检查网络延迟，考虑使用CDN或就近服务器",
                metric_value=connect_time,
                threshold=self.THRESHOLDS["connect"]["warning"],
            ))
    
    def _check_tls(self, tls_time: float):
        """检查TLS握手"""
        if tls_time > self.THRESHOLDS["tls"]["warning"]:
            self._issues.append(DiagnosticIssue(
                category="tls",
                message=f"TLS握手耗时过长: {tls_time:.1f}ms",
                severity=Severity.WARNING,
                suggestion="考虑启用TLS会话复用或使用更轻量的加密套件",
                metric_value=tls_time,
                threshold=self.THRESHOLDS["tls"]["warning"],
            ))
    
    def _check_ttfb(self, ttfb: float):
        """检查首字节时间"""
        if ttfb > self.THRESHOLDS["ttfb"]["warning"]:
            self._issues.append(DiagnosticIssue(
                category="ttfb",
                message=f"首字节时间过长: {ttfb:.1f}ms",
                severity=Severity.CRITICAL,
                suggestion="服务器响应缓慢，检查后端性能和数据库查询",
                metric_value=ttfb,
                threshold=self.THRESHOLDS["ttfb"]["warning"],
            ))
        elif ttfb > self.THRESHOLDS["ttfb"]["good"]:
            self._issues.append(DiagnosticIssue(
                category="ttfb",
                message=f"首字节时间偏高: {ttfb:.1f}ms",
                severity=Severity.WARNING,
                suggestion="服务器响应速度可优化",
                metric_value=ttfb,
                threshold=self.THRESHOLDS["ttfb"]["good"],
            ))
    
    def _check_download(self, download_time: float):
        """检查下载时间"""
        if download_time > self.THRESHOLDS["download"]["warning"]:
            self._issues.append(DiagnosticIssue(
                category="download",
                message=f"内容下载耗时过长: {download_time:.1f}ms",
                severity=Severity.WARNING,
                suggestion="考虑启用压缩、使用CDN或优化资源大小",
                metric_value=download_time,
                threshold=self.THRESHOLDS["download"]["warning"],
            ))


class BottleneckDetector:
    """瓶颈检测器"""
    
    def __init__(self):
        """初始化瓶颈检测器"""
        pass
    
    def detect(self, timing_result) -> Optional[str]:
        """
        检测性能瓶颈
        
        Args:
            timing_result: TimingResult对象
            
        Returns:
            瓶颈阶段名称，如果没有明显瓶颈则返回None
        """
        if timing_result.error or timing_result.total_time == 0:
            return None
        
        # 计算各阶段占比
        stages = {
            "dns": timing_result.dns_time,
            "connect": timing_result.connect_time,
            "tls": timing_result.tls_time,
            "request": timing_result.request_time,
            "ttfb": timing_result.first_byte_time,
            "download": timing_result.download_time,
        }
        
        total = sum(stages.values())
        if total == 0:
            return None
        
        # 找出占比最大的阶段
        max_stage = max(stages.items(), key=lambda x: x[1])
        max_ratio = max_stage[1] / total
        
        # 如果某阶段占比超过50%，认为是瓶颈
        if max_ratio > 0.5:
            return max_stage[0]
        
        return None
    
    def get_recommendations(self, bottleneck: Optional[str]) -> List[str]:
        """
        获取优化建议
        
        Args:
            bottleneck: 瓶颈阶段
            
        Returns:
            建议列表
        """
        recommendations = {
            "dns": [
                "使用更快的DNS服务器（如8.8.8.8或1.1.1.1）",
                "启用DNS预解析",
                "配置本地DNS缓存",
            ],
            "connect": [
                "使用CDN加速",
                "选择就近的服务器节点",
                "优化网络路由",
            ],
            "tls": [
                "启用TLS会话复用",
                "使用更轻量的加密套件",
                "考虑使用HTTP/2或HTTP/3",
            ],
            "request": [
                "减少请求体大小",
                "压缩请求数据",
            ],
            "ttfb": [
                "优化后端代码性能",
                "优化数据库查询",
                "启用服务器端缓存",
                "使用异步处理",
            ],
            "download": [
                "启用Gzip/Brotli压缩",
                "使用CDN分发静态资源",
                "减少响应体大小",
                "实现分块传输",
            ],
        }
        
        if bottleneck and bottleneck in recommendations:
            return recommendations[bottleneck]
        
        return []
