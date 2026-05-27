#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Module - CLI Entry Point
命令行入口模块
"""

import sys
import argparse
from typing import List, Optional

from .timing import TimingAnalyzer, TimingResult
from .request import RequestBuilder, RequestConfig
from .analysis import PerformanceAnalyzer, BottleneckDetector
from .report import ReportGenerator
from .tui import TUIDashboard
from .utils import (
    print_banner, print_error, print_warning, print_success, print_info,
    validate_url, parse_headers, print_table, format_duration
)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="timetrace",
        description="⏱️ TimeTrace-CLI - Lightweight HTTP Request Timing Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic timing analysis
  timetrace https://example.com

  # POST request with JSON body
  timetrace https://api.example.com/users -X POST -H "Content-Type: application/json" -d '{"name":"test"}'

  # Multiple requests comparison
  timetrace https://example.com https://api.example.com --compare

  # Generate HTML report
  timetrace https://example.com --report report.html --format html

  # Launch TUI dashboard
  timetrace https://example.com --tui
        """
    )
    
    # 位置参数：URL
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more URLs to analyze"
    )
    
    # 请求配置
    parser.add_argument(
        "-X", "--method",
        default="GET",
        help="HTTP method (default: GET)"
    )
    parser.add_argument(
        "-H", "--header",
        action="append",
        default=[],
        help="Request headers (format: 'Key: Value')"
    )
    parser.add_argument(
        "-d", "--data",
        help="Request body data"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)"
    )
    
    # 输出选项
    parser.add_argument(
        "-o", "--output",
        help="Output file path for report"
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "markdown", "md"],
        default="json",
        help="Report format (default: json)"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch TUI dashboard"
    )
    parser.add_argument(
        "--waterfall",
        action="store_true",
        help="Show waterfall chart"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple requests"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode (only output report)"
    )
    
    # 分析选项
    parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Skip performance analysis"
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat each request (default: 1)"
    )
    
    # 其他选项
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def analyze_url(url: str, args) -> Optional[TimingResult]:
    """
    分析单个URL
    
    Args:
        url: URL字符串
        args: 命令行参数
        
    Returns:
        TimingResult对象
    """
    # 验证URL
    if not validate_url(url):
        print_error(f"Invalid URL: {url}")
        return None
    
    # 构建请求配置
    headers = parse_headers(args.header)
    
    # 创建分析器
    analyzer = TimingAnalyzer(timeout=args.timeout)
    
    if not args.quiet:
        print_info(f"Analyzing: {url}")
    
    # 执行分析
    result = analyzer.analyze(
        url=url,
        method=args.method,
        headers=headers if headers else None,
        data=args.data.encode() if args.data else None
    )
    
    return result


def display_result(result: TimingResult, args):
    """
    显示分析结果
    
    Args:
        result: TimingResult对象
        args: 命令行参数
    """
    if result.error:
        print_error(result.error)
        return
    
    # 性能分析
    score = None
    issues = None
    bottleneck = None
    
    if not args.no_analyze:
        perf_analyzer = PerformanceAnalyzer()
        score, issues = perf_analyzer.analyze(result)
        
        detector = BottleneckDetector()
        bottleneck = detector.detect(result)
    
    # TUI模式
    if args.tui or args.waterfall:
        dashboard = TUIDashboard()
        try:
            if args.waterfall:
                dashboard.display_waterfall(result)
            else:
                dashboard.display_result(result, score, issues)
        finally:
            dashboard.cleanup()
        return
    
    # 控制台输出
    print()
    print("=" * 60)
    print(f"  📊 Timing Analysis Result")
    print("=" * 60)
    print()
    
    print(f"  URL: {result.url}")
    print(f"  Method: {result.method}")
    print(f"  Status: {result.status_code}")
    print(f"  Size: {result.response_size} bytes")
    print()
    
    print("  ⏱️  Timing Breakdown:")
    print(f"      DNS Lookup:      {result.dns_time:>8.2f} ms")
    print(f"      TCP Connect:     {result.connect_time:>8.2f} ms")
    print(f"      TLS Handshake:   {result.tls_time:>8.2f} ms")
    print(f"      Request Sent:    {result.request_time:>8.2f} ms")
    print(f"      First Byte:      {result.first_byte_time:>8.2f} ms")
    print(f"      Download:        {result.download_time:>8.2f} ms")
    print(f"      ─────────────────────────────")
    print(f"      TOTAL:           {result.total_time:>8.2f} ms")
    print()
    
    if score:
        print(f"  📈 Performance Score: {score.overall:.1f}/100")
        print()
    
    if bottleneck:
        print(f"  🔍 Detected Bottleneck: {bottleneck.upper()}")
        print()
    
    if issues:
        print("  ⚠️  Issues Found:")
        for issue in issues[:5]:
            symbol = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(
                issue.severity.value, "•"
            )
            print(f"      {symbol} {issue.message}")
        print()
    
    print("=" * 60)
    print()


def generate_report(results: List[TimingResult], args):
    """
    生成报告
    
    Args:
        results: TimingResult列表
        args: 命令行参数
    """
    if not args.output or not results:
        return
    
    generator = ReportGenerator()
    
    # 获取第一个结果进行分析
    result = results[0]
    
    # 性能分析
    score = None
    issues = None
    
    if not args.no_analyze:
        perf_analyzer = PerformanceAnalyzer()
        score, issues = perf_analyzer.analyze(result)
    
    # 生成报告
    if args.format == "json":
        content = generator.generate_json(result, score, issues)
    elif args.format == "html":
        content = generator.generate_html(result, score, issues)
    elif args.format in ["markdown", "md"]:
        content = generator.generate_markdown(result, score, issues)
    else:
        content = generator.generate_json(result, score, issues)
    
    # 保存报告
    filepath = generator.save_report(content, args.output, args.format)
    print_success(f"Report saved to: {filepath}")


def compare_results(results: List[TimingResult]):
    """
    对比多个结果
    
    Args:
        results: TimingResult列表
    """
    if len(results) < 2:
        return
    
    print()
    print("=" * 80)
    print("  📊 Comparison View")
    print("=" * 80)
    print()
    
    headers = ["#", "URL", "DNS", "Connect", "TLS", "TTFB", "Total", "Status"]
    rows = []
    
    for i, result in enumerate(results):
        rows.append([
            str(i + 1),
            result.url[:40] + "..." if len(result.url) > 40 else result.url,
            f"{result.dns_time:.1f}",
            f"{result.connect_time:.1f}",
            f"{result.tls_time:.1f}",
            f"{result.first_byte_time:.1f}",
            f"{result.total_time:.1f}",
            str(result.status_code)
        ])
    
    print_table(headers, rows)
    print()
    
    # 统计信息
    successful = [r for r in results if r.error is None]
    if successful:
        avg_total = sum(r.total_time for r in successful) / len(successful)
        min_total = min(r.total_time for r in successful)
        max_total = max(r.total_time for r in successful)
        
        print(f"  Statistics ({len(successful)} successful requests):")
        print(f"      Average Total Time: {avg_total:.2f} ms")
        print(f"      Min Total Time: {min_total:.2f} ms")
        print(f"      Max Total Time: {max_total:.2f} ms")
        print()


def cli(args: Optional[List[str]] = None):
    """
    CLI入口函数
    
    Args:
        args: 命令行参数列表
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 打印Banner
    if not parsed_args.quiet:
        print_banner()
    
    # 分析所有URL
    results = []
    
    for url in parsed_args.urls:
        for _ in range(parsed_args.repeat):
            result = analyze_url(url, parsed_args)
            if result:
                results.append(result)
                
                # 显示结果（非对比模式）
                if not parsed_args.compare and len(parsed_args.urls) == 1:
                    display_result(result, parsed_args)
    
    # 对比模式
    if parsed_args.compare and len(results) > 1:
        compare_results(results)
    
    # 生成报告
    if parsed_args.output:
        generate_report(results, parsed_args)
    
    return 0


def main():
    """主入口"""
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
