#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUI Module - Terminal User Interface Dashboard
终端用户界面仪表盘模块
"""

import sys
import curses
from typing import Dict, List, Optional
from datetime import datetime


class TUIDashboard:
    """TUI仪表盘"""
    
    # 颜色定义
    COLORS = {
        "title": 1,
        "success": 2,
        "warning": 3,
        "error": 4,
        "info": 5,
        "highlight": 6,
    }
    
    # 阶段颜色映射
    STAGE_COLORS = {
        "DNS": 5,      # 蓝色
        "Connect": 6,  # 青色
        "TLS": 4,      # 红色
        "Request": 3,  # 黄色
        "TTFB": 2,     # 绿色
        "Download": 1, # 默认
    }
    
    def __init__(self):
        """初始化TUI仪表盘"""
        self._stdscr = None
        self._initialized = False
    
    def init(self):
        """初始化curses"""
        self._stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self._stdscr.keypad(True)
        curses.curs_set(0)
        
        # 初始化颜色
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_WHITE, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_RED, -1)
            curses.init_pair(5, curses.COLOR_CYAN, -1)
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)
        
        self._initialized = True
    
    def cleanup(self):
        """清理curses"""
        if self._initialized and self._stdscr:
            curses.nocbreak()
            self._stdscr.keypad(False)
            curses.echo()
            curses.endwin()
            self._initialized = False
    
    def display_result(self, timing_result, score=None, issues=None):
        """
        显示计时结果
        
        Args:
            timing_result: TimingResult对象
            score: PerformanceScore对象
            issues: 问题列表
        """
        if not self._initialized:
            self.init()
        
        self._stdscr.clear()
        height, width = self._stdscr.getmaxyx()
        
        # 标题
        title = "⏱️  TimeTrace-CLI - HTTP Request Timing Analysis"
        self._stdscr.addstr(0, (width - len(title)) // 2, title, 
                           curses.color_pair(self.COLORS["title"]) | curses.A_BOLD)
        
        # URL信息
        y = 2
        self._stdscr.addstr(y, 2, f"URL: ", curses.A_BOLD)
        self._stdscr.addstr(y, 7, timing_result.url[:width - 10])
        
        y += 1
        self._stdscr.addstr(y, 2, f"Method: {timing_result.method}  |  Status: ", curses.A_BOLD)
        status_color = self.COLORS["success"] if 200 <= timing_result.status_code < 300 else self.COLORS["error"]
        self._stdscr.addstr(y, len(f"Method: {timing_result.method}  |  Status: "), 
                           str(timing_result.status_code), curses.color_pair(status_color) | curses.A_BOLD)
        
        # 计时详情
        y += 2
        self._stdscr.addstr(y, 2, "━━━ Timing Breakdown ━━━", 
                           curses.color_pair(self.COLORS["info"]) | curses.A_BOLD)
        
        y += 1
        timing_data = [
            ("DNS Lookup", timing_result.dns_time, "ms"),
            ("TCP Connect", timing_result.connect_time, "ms"),
            ("TLS Handshake", timing_result.tls_time, "ms"),
            ("Request Sent", timing_result.request_time, "ms"),
            ("First Byte (TTFB)", timing_result.first_byte_time, "ms"),
            ("Content Download", timing_result.download_time, "ms"),
        ]
        
        max_time = max(t[1] for t in timing_data) if timing_data else 1
        
        for label, value, unit in timing_data:
            y += 1
            # 标签
            self._stdscr.addstr(y, 4, f"{label}:")
            # 数值
            self._stdscr.addstr(y, 25, f"{value:.2f} {unit}")
            # 进度条
            bar_width = min(30, width - 45)
            filled = int(bar_width * value / max_time) if max_time > 0 else 0
            bar = "█" * filled + "░" * (bar_width - filled)
            self._stdscr.addstr(y, 40, bar, curses.color_pair(self.COLORS["info"]))
        
        # 总时间
        y += 1
        self._stdscr.addstr(y, 2, "─" * (width - 4))
        y += 1
        self._stdscr.addstr(y, 4, "TOTAL:", curses.A_BOLD)
        self._stdscr.addstr(y, 25, f"{timing_result.total_time:.2f} ms", 
                           curses.color_pair(self.COLORS["highlight"]) | curses.A_BOLD)
        
        # 性能评分
        if score:
            y += 2
            self._stdscr.addstr(y, 2, "━━━ Performance Score ━━━", 
                               curses.color_pair(self.COLORS["info"]) | curses.A_BOLD)
            y += 1
            
            score_color = self.COLORS["success"] if score.overall >= 70 else (
                self.COLORS["warning"] if score.overall >= 40 else self.COLORS["error"]
            )
            self._stdscr.addstr(y, 4, f"Overall Score: {score.overall:.1f}/100", 
                               curses.color_pair(score_color) | curses.A_BOLD)
            
            # 评分条
            y += 1
            bar_width = min(40, width - 10)
            filled = int(bar_width * score.overall / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            self._stdscr.addstr(y, 4, bar, curses.color_pair(score_color))
        
        # 问题列表
        if issues:
            y += 2
            self._stdscr.addstr(y, 2, "━━━ Issues & Suggestions ━━━", 
                               curses.color_pair(self.COLORS["warning"]) | curses.A_BOLD)
            
            for issue in issues[:5]:  # 最多显示5个问题
                y += 1
                severity_symbol = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(
                    issue.severity.value, "•"
                )
                color = self.COLORS.get(issue.severity.value, self.COLORS["info"])
                msg = f"{severity_symbol} {issue.message}"[:width - 6]
                self._stdscr.addstr(y, 4, msg, curses.color_pair(color))
        
        # 响应信息
        y = height - 4
        self._stdscr.addstr(y, 2, "━━━ Response Info ━━━", 
                           curses.color_pair(self.COLORS["info"]) | curses.A_BOLD)
        y += 1
        self._stdscr.addstr(y, 4, f"Size: {timing_result.response_size} bytes  |  ")
        self._stdscr.addstr(y, 4 + len(f"Size: {timing_result.response_size} bytes  |  "), 
                           f"Timestamp: {timing_result.timestamp}")
        
        # 底部提示
        self._stdscr.addstr(height - 1, 2, "Press any key to exit...", curses.A_DIM)
        
        self._stdscr.refresh()
        self._stdscr.getch()
    
    def display_waterfall(self, timing_result):
        """
        显示瀑布图
        
        Args:
            timing_result: TimingResult对象
        """
        if not self._initialized:
            self.init()
        
        self._stdscr.clear()
        height, width = self._stdscr.getmaxyx()
        
        # 标题
        title = "📊 Waterfall Chart"
        self._stdscr.addstr(0, (width - len(title)) // 2, title, 
                           curses.color_pair(self.COLORS["title"]) | curses.A_BOLD)
        
        # URL
        self._stdscr.addstr(2, 2, f"URL: {timing_result.url[:width - 10]}")
        
        # 瀑布图
        waterfall_data = timing_result.get_waterfall_data()
        if waterfall_data:
            max_time = max(start + duration for _, start, duration in waterfall_data)
            
            y = 4
            chart_width = min(60, width - 25)
            
            for stage, start, duration in waterfall_data:
                # 阶段名称
                self._stdscr.addstr(y, 2, f"{stage:12}")
                
                # 时间轴
                start_pos = int(chart_width * start / max_time) if max_time > 0 else 0
                duration_width = int(chart_width * duration / max_time) if max_time > 0 else 1
                
                # 空白部分
                self._stdscr.addstr(y, 16, " " * start_pos)
                
                # 阶段条
                color = self.STAGE_COLORS.get(stage, 1)
                bar = "█" * max(1, duration_width)
                self._stdscr.addstr(y, 16 + start_pos, bar, curses.color_pair(color))
                
                # 时间标注
                time_str = f"{duration:.1f}ms"
                if 16 + start_pos + duration_width + 2 + len(time_str) < width:
                    self._stdscr.addstr(y, 16 + start_pos + duration_width + 2, time_str)
                
                y += 1
        
        # 图例
        y = height - 6
        self._stdscr.addstr(y, 2, "Legend:", curses.A_BOLD)
        y += 1
        legend_items = list(self.STAGE_COLORS.items())[:6]
        x = 2
        for stage, color in legend_items:
            self._stdscr.addstr(y, x, "█", curses.color_pair(color))
            self._stdscr.addstr(y, x + 1, stage)
            x += len(stage) + 4
        
        # 底部提示
        self._stdscr.addstr(height - 1, 2, "Press any key to exit...", curses.A_DIM)
        
        self._stdscr.refresh()
        self._stdscr.getch()
    
    def display_comparison(self, results: List):
        """
        显示多请求对比
        
        Args:
            results: TimingResult列表
        """
        if not self._initialized:
            self.init()
        
        self._stdscr.clear()
        height, width = self._stdscr.getmaxyx()
        
        # 标题
        title = "📈 Comparison View"
        self._stdscr.addstr(0, (width - len(title)) // 2, title, 
                           curses.color_pair(self.COLORS["title"]) | curses.A_BOLD)
        
        # 表头
        y = 2
        headers = ["#", "URL", "DNS", "Connect", "TLS", "TTFB", "Total", "Status"]
        col_widths = [4, 30, 10, 10, 10, 10, 10, 8]
        
        x = 2
        for header, w in zip(headers, col_widths):
            self._stdscr.addstr(y, x, header[:w-1], curses.A_BOLD)
            x += w
        
        # 数据行
        for i, result in enumerate(results[:height - 5]):
            y += 1
            x = 2
            
            # 序号
            self._stdscr.addstr(y, x, str(i + 1))
            x += col_widths[0]
            
            # URL
            url_display = result.url[:col_widths[1]-1] if len(result.url) > col_widths[1]-1 else result.url
            self._stdscr.addstr(y, x, url_display)
            x += col_widths[1]
            
            # DNS
            self._stdscr.addstr(y, x, f"{result.dns_time:.1f}")
            x += col_widths[2]
            
            # Connect
            self._stdscr.addstr(y, x, f"{result.connect_time:.1f}")
            x += col_widths[3]
            
            # TLS
            self._stdscr.addstr(y, x, f"{result.tls_time:.1f}")
            x += col_widths[4]
            
            # TTFB
            self._stdscr.addstr(y, x, f"{result.first_byte_time:.1f}")
            x += col_widths[5]
            
            # Total
            self._stdscr.addstr(y, x, f"{result.total_time:.1f}")
            x += col_widths[6]
            
            # Status
            status_color = self.COLORS["success"] if 200 <= result.status_code < 300 else self.COLORS["error"]
            self._stdscr.addstr(y, x, str(result.status_code), 
                               curses.color_pair(status_color) | curses.A_BOLD)
        
        # 底部提示
        self._stdscr.addstr(height - 1, 2, "Press any key to exit...", curses.A_DIM)
        
        self._stdscr.refresh()
        self._stdscr.getch()


def create_dashboard() -> TUIDashboard:
    """创建TUI仪表盘实例"""
    return TUIDashboard()
