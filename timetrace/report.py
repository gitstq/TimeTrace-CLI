#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Module - Multi-Format Report Generator
多格式报告生成模块
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        self._template_dir = Path(__file__).parent / "templates"
    
    def generate_json(self, timing_result, score=None, issues=None) -> str:
        """
        生成JSON报告
        
        Args:
            timing_result: TimingResult对象
            score: PerformanceScore对象
            issues: 问题列表
            
        Returns:
            JSON字符串
        """
        report = {
            "meta": {
                "generator": "TimeTrace-CLI",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
            },
            "request": {
                "url": timing_result.url,
                "method": timing_result.method,
            },
            "timing": timing_result.to_dict()["timing"],
            "response": {
                "status_code": timing_result.status_code,
                "size_bytes": timing_result.response_size,
                "headers": timing_result.headers,
            },
        }
        
        if score:
            report["performance"] = score.to_dict()
        
        if issues:
            report["diagnostics"] = {
                "issues": [issue.to_dict() for issue in issues],
                "issue_count": len(issues),
            }
        
        if timing_result.error:
            report["error"] = timing_result.error
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def generate_html(self, timing_result, score=None, issues=None) -> str:
        """
        生成HTML报告
        
        Args:
            timing_result: TimingResult对象
            score: PerformanceScore对象
            issues: 问题列表
            
        Returns:
            HTML字符串
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TimeTrace Report - {timing_result.url}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            padding: 30px 0;
            border-bottom: 1px solid #3a3a5a;
            margin-bottom: 30px;
        }}
        .header h1 {{ 
            font-size: 2em;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .card {{ 
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h2 {{ 
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .url-display {{ 
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            word-break: break-all;
            font-family: monospace;
        }}
        .timing-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .timing-item {{ 
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
        }}
        .timing-item .label {{ color: #888; font-size: 0.9em; }}
        .timing-item .value {{ 
            font-size: 1.5em; 
            font-weight: bold;
            color: #00d4ff;
        }}
        .score-display {{ 
            text-align: center;
            padding: 30px;
        }}
        .score-circle {{ 
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: conic-gradient(#00d4ff 0deg, #00d4ff {score.overall * 3.6 if score else 0}deg, #333 {score.overall * 3.6 if score else 0}deg);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }}
        .score-circle .inner {{ 
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: #1a1a2e;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .score-circle .score {{ 
            font-size: 2.5em;
            font-weight: bold;
            color: #00d4ff;
        }}
        .waterfall {{ 
            margin-top: 20px;
        }}
        .waterfall-row {{ 
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .waterfall-label {{ 
            width: 100px;
            font-size: 0.9em;
        }}
        .waterfall-bar-container {{ 
            flex: 1;
            height: 25px;
            background: rgba(0,0,0,0.3);
            border-radius: 4px;
            position: relative;
        }}
        .waterfall-bar {{ 
            height: 100%;
            border-radius: 4px;
            position: absolute;
        }}
        .issue {{ 
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        .issue.critical {{ background: rgba(255,0,0,0.1); border-color: #ff4444; }}
        .issue.warning {{ background: rgba(255,165,0,0.1); border-color: #ffa500; }}
        .issue.info {{ background: rgba(0,150,255,0.1); border-color: #0096ff; }}
        .issue .message {{ font-weight: bold; margin-bottom: 5px; }}
        .issue .suggestion {{ color: #888; font-size: 0.9em; }}
        .footer {{ 
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏱️ TimeTrace Report</h1>
            <p>HTTP Request Timing Analysis</p>
        </div>
        
        <div class="card">
            <h2>📍 Request Info</h2>
            <div class="url-display">{timing_result.url}</div>
            <p style="margin-top: 10px;">
                <strong>Method:</strong> {timing_result.method} | 
                <strong>Status:</strong> {timing_result.status_code} | 
                <strong>Size:</strong> {timing_result.response_size} bytes
            </p>
        </div>
        
        <div class="card">
            <h2>⏱️ Timing Breakdown</h2>
            <div class="timing-grid">
                <div class="timing-item">
                    <div class="label">DNS Lookup</div>
                    <div class="value">{timing_result.dns_time:.1f}ms</div>
                </div>
                <div class="timing-item">
                    <div class="label">TCP Connect</div>
                    <div class="value">{timing_result.connect_time:.1f}ms</div>
                </div>
                <div class="timing-item">
                    <div class="label">TLS Handshake</div>
                    <div class="value">{timing_result.tls_time:.1f}ms</div>
                </div>
                <div class="timing-item">
                    <div class="label">Request Sent</div>
                    <div class="value">{timing_result.request_time:.1f}ms</div>
                </div>
                <div class="timing-item">
                    <div class="label">First Byte (TTFB)</div>
                    <div class="value">{timing_result.first_byte_time:.1f}ms</div>
                </div>
                <div class="timing-item">
                    <div class="label">Content Download</div>
                    <div class="value">{timing_result.download_time:.1f}ms</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <strong style="font-size: 1.3em; color: #00d4ff;">Total: {timing_result.total_time:.1f}ms</strong>
            </div>
        </div>
"""
        
        # 添加性能评分
        if score:
            html += f"""
        <div class="card">
            <h2>📊 Performance Score</h2>
            <div class="score-display">
                <div class="score-circle">
                    <div class="inner">
                        <span class="score">{score.overall:.0f}</span>
                    </div>
                </div>
                <p>Overall Performance Score</p>
            </div>
        </div>
"""
        
        # 添加问题列表
        if issues:
            html += """
        <div class="card">
            <h2>🔍 Diagnostics</h2>
"""
            for issue in issues:
                html += f"""
            <div class="issue {issue.severity.value}">
                <div class="message">{issue.message}</div>
                <div class="suggestion">💡 {issue.suggestion}</div>
            </div>
"""
            html += """
        </div>
"""
        
        html += f"""
        <div class="footer">
            <p>Generated by TimeTrace-CLI v1.0.0 | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_markdown(self, timing_result, score=None, issues=None) -> str:
        """
        生成Markdown报告
        
        Args:
            timing_result: TimingResult对象
            score: PerformanceScore对象
            issues: 问题列表
            
        Returns:
            Markdown字符串
        """
        md = f"""# ⏱️ TimeTrace Report

## 📍 Request Info

| Property | Value |
|----------|-------|
| **URL** | `{timing_result.url}` |
| **Method** | {timing_result.method} |
| **Status** | {timing_result.status_code} |
| **Size** | {timing_result.response_size} bytes |
| **Timestamp** | {timing_result.timestamp} |

## ⏱️ Timing Breakdown

| Stage | Time (ms) |
|-------|-----------|
| DNS Lookup | `{timing_result.dns_time:.2f}` |
| TCP Connect | `{timing_result.connect_time:.2f}` |
| TLS Handshake | `{timing_result.tls_time:.2f}` |
| Request Sent | `{timing_result.request_time:.2f}` |
| First Byte (TTFB) | `{timing_result.first_byte_time:.2f}` |
| Content Download | `{timing_result.download_time:.2f}` |
| **Total** | **`{timing_result.total_time:.2f}`** |

"""
        
        if score:
            md += f"""## 📊 Performance Score

| Category | Score |
|----------|-------|
| **Overall** | **{score.overall:.1f}/100** |
| DNS | {score.dns_score:.1f} |
| Connect | {score.connect_score:.1f} |
| TLS | {score.tls_score:.1f} |
| TTFB | {score.ttfb_score:.1f} |
| Download | {score.download_score:.1f} |

"""
        
        if issues:
            md += """## 🔍 Diagnostics

"""
            for issue in issues:
                emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(issue.severity.value, "•")
                md += f"""### {emoji} {issue.category.upper()}

**Issue:** {issue.message}

**Suggestion:** {issue.suggestion}

"""
        
        md += f"""---

*Generated by TimeTrace-CLI v1.0.0 | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        return md
    
    def save_report(self, content: str, filepath: str, format_type: str = "json"):
        """
        保存报告到文件
        
        Args:
            content: 报告内容
            filepath: 文件路径
            format_type: 格式类型
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path.absolute())
