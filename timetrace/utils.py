#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils Module - Utility Functions
工具函数模块
"""

import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime


def get_terminal_width() -> int:
    """获取终端宽度"""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def get_terminal_height() -> int:
    """获取终端高度"""
    try:
        import shutil
        return shutil.get_terminal_size().lines
    except Exception:
        return 24


def format_bytes(size: int) -> str:
    """
    格式化字节数
    
    Args:
        size: 字节数
        
    Returns:
        格式化字符串
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_duration(ms: float) -> str:
    """
    格式化持续时间
    
    Args:
        ms: 毫秒数
        
    Returns:
        格式化字符串
    """
    if ms < 1000:
        return f"{ms:.1f}ms"
    elif ms < 60000:
        return f"{ms/1000:.2f}s"
    else:
        return f"{ms/60000:.1f}m"


def print_banner():
    """打印Banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ⏱️  TimeTrace-CLI                                           ║
║   Lightweight HTTP Request Timing Analysis Engine             ║
║   轻量级HTTP请求计时分析与可视化引擎                           ║
║                                                               ║
║   Version: 1.0.0                                              ║
║   License: MIT                                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_error(message: str):
    """打印错误信息"""
    print(f"\033[91m❌ Error: {message}\033[0m", file=sys.stderr)


def print_warning(message: str):
    """打印警告信息"""
    print(f"\033[93m⚠️  Warning: {message}\033[0m")


def print_success(message: str):
    """打印成功信息"""
    print(f"\033[92m✅ {message}\033[0m")


def print_info(message: str):
    """打印信息"""
    print(f"\033[94mℹ️  {message}\033[0m")


def print_table(headers: list, rows: list, title: Optional[str] = None):
    """
    打印表格
    
    Args:
        headers: 表头
        rows: 数据行
        title: 标题
    """
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    
    # 计算列宽
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 打印表头
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(f"\033[1m{header_line}\033[0m")
    print("-" * len(header_line))
    
    # 打印数据行
    for row in rows:
        print(" | ".join(str(c).ljust(w) for c, w in zip(row, col_widths)))


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        是否有效
    """
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ["http", "https"]
    except Exception:
        return False


def parse_headers(header_strings: list) -> Dict[str, str]:
    """
    解析请求头字符串列表
    
    Args:
        header_strings: 请求头字符串列表（格式：Key: Value）
        
    Returns:
        请求头字典
    """
    headers = {}
    for h in header_strings:
        if ":" in h:
            key, value = h.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers


def load_config(filepath: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        filepath: 配置文件路径
        
    Returns:
        配置字典
    """
    import json
    
    path = os.path.expanduser(filepath)
    if not os.path.exists(path):
        return {}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(filepath: str, config: Dict[str, Any]):
    """
    保存配置文件
    
    Args:
        filepath: 配置文件路径
        config: 配置字典
    """
    import json
    
    path = os.path.expanduser(filepath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_color_code(score: float) -> str:
    """
    根据评分获取颜色代码
    
    Args:
        score: 评分（0-100）
        
    Returns:
        ANSI颜色代码
    """
    if score >= 70:
        return "\033[92m"  # 绿色
    elif score >= 40:
        return "\033[93m"  # 黄色
    else:
        return "\033[91m"  # 红色


def reset_color() -> str:
    """重置颜色"""
    return "\033[0m"


def create_progress_bar(current: int, total: int, width: int = 30) -> str:
    """
    创建进度条
    
    Args:
        current: 当前进度
        total: 总数
        width: 进度条宽度
        
    Returns:
        进度条字符串
    """
    if total == 0:
        return "[" + " " * width + "]"
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def timestamp_now() -> str:
    """获取当前时间戳"""
    return datetime.now().isoformat()
