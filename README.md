<div align="center">

# ⏱️ TimeTrace-CLI

**Lightweight Terminal HTTP Request Timing Analysis & Visualization Engine**

**轻量级终端HTTP请求计时分析与可视化引擎**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**TimeTrace-CLI** is a lightweight, zero-dependency terminal tool for analyzing HTTP request timing with beautiful visualizations. It breaks down every stage of your HTTP requests (DNS → TCP → TLS → Request → TTFB → Download) and helps you identify performance bottlenecks instantly.

**Why TimeTrace-CLI?**
- 🔍 **Detailed Timing Breakdown** - Measure every phase of your HTTP requests
- 📊 **Visual Waterfall Charts** - See timing distribution at a glance
- 🚨 **Performance Diagnostics** - Automatic bottleneck detection with suggestions
- 📈 **Comparison Mode** - Compare multiple requests side by side
- 📄 **Multi-Format Reports** - Export to JSON, HTML, or Markdown
- 🖥️ **TUI Dashboard** - Interactive terminal interface
- ⚡ **Zero Dependencies** - Pure Python standard library, no external packages needed

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Timing Analysis** | DNS, TCP, TLS, Request, TTFB, Download timing |
| 📊 **Waterfall Chart** | Visual representation of request phases |
| 🎯 **Performance Score** | 0-100 score with detailed breakdown |
| 🚨 **Bottleneck Detection** | Automatic identification of slow stages |
| 💡 **Smart Suggestions** | Optimization recommendations |
| 📈 **Comparison View** | Compare multiple requests |
| 📄 **Report Export** | JSON, HTML, Markdown formats |
| 🖥️ **TUI Dashboard** | Interactive terminal interface |

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/TimeTrace-CLI.git
cd TimeTrace-CLI

# Install
pip install -e .

# Or run directly
python -m timetrace.main https://example.com
```

#### Basic Usage

```bash
# Analyze a URL
timetrace https://example.com

# POST request with JSON body
timetrace https://api.example.com/users -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'

# Multiple requests comparison
timetrace https://example.com https://api.example.com --compare

# Generate HTML report
timetrace https://example.com --report report.html --format html

# Launch TUI dashboard
timetrace https://example.com --tui

# Show waterfall chart
timetrace https://example.com --waterfall
```

### 📖 Detailed Usage

#### Command Line Options

```
timetrace [OPTIONS] URL [URL...]

Positional Arguments:
  URL                   One or more URLs to analyze

Request Options:
  -X, --method METHOD   HTTP method (default: GET)
  -H, --header HEADER   Request headers (format: 'Key: Value')
  -d, --data DATA       Request body data
  --timeout SECONDS     Request timeout (default: 30)

Output Options:
  -o, --output FILE     Output file for report
  --format FORMAT       Report format: json, html, markdown
  --tui                 Launch TUI dashboard
  --waterfall           Show waterfall chart
  --compare             Compare multiple requests
  -q, --quiet           Quiet mode (only output report)

Analysis Options:
  --no-analyze          Skip performance analysis
  --repeat N            Repeat each request N times
```

#### Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║   ⏱️  TimeTrace-CLI                                           ║
║   Lightweight HTTP Request Timing Analysis Engine             ║
╚═══════════════════════════════════════════════════════════════╝

ℹ️  Analyzing: https://example.com

============================================================
  📊 Timing Analysis Result
============================================================

  URL: https://example.com
  Method: GET
  Status: 200
  Size: 1256 bytes

  ⏱️  Timing Breakdown:
      DNS Lookup:         45.23 ms
      TCP Connect:        89.56 ms
      TLS Handshake:      67.34 ms
      Request Sent:        5.12 ms
      First Byte:        234.78 ms
      Download:          156.89 ms
      ─────────────────────────────
      TOTAL:             598.92 ms

  📈 Performance Score: 72.5/100

  🔍 Detected Bottleneck: TTFB

============================================================
```

### 💡 Design Philosophy

TimeTrace-CLI was built with these principles in mind:

1. **Zero Dependencies** - Uses only Python standard library for maximum portability
2. **Developer-Friendly** - Clear output, intuitive commands, helpful suggestions
3. **Performance First** - Lightweight and fast, doesn't slow down your workflow
4. **Visual Clarity** - Beautiful terminal output that's easy to read

### 📦 Project Structure

```
TimeTrace-CLI/
├── timetrace/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # CLI entry point
│   ├── timing.py        # Timing analysis core
│   ├── request.py       # Request builder
│   ├── analysis.py      # Performance analysis
│   ├── tui.py           # Terminal UI
│   ├── report.py        # Report generation
│   └── utils.py         # Utilities
├── tests/
│   └── test_timetrace.py
├── setup.py
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**TimeTrace-CLI** 是一款轻量级、零依赖的终端HTTP请求计时分析与可视化工具。它能够精确测量HTTP请求的每个阶段（DNS → TCP → TLS → 请求 → 首字节 → 下载），帮助您快速定位性能瓶颈。

**为什么选择 TimeTrace-CLI？**
- 🔍 **详细计时分析** - 测量HTTP请求的每个阶段
- 📊 **可视化瀑布图** - 直观展示时间分布
- 🚨 **性能诊断** - 自动检测瓶颈并提供优化建议
- 📈 **对比模式** - 多请求并行对比分析
- 📄 **多格式报告** - 支持JSON、HTML、Markdown导出
- 🖥️ **TUI仪表盘** - 交互式终端界面
- ⚡ **零依赖** - 纯Python标准库实现，无需安装额外包

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **计时分析** | DNS、TCP、TLS、请求、首字节、下载各阶段计时 |
| 📊 **瀑布图** | 请求阶段可视化展示 |
| 🎯 **性能评分** | 0-100分详细评分 |
| 🚨 **瓶颈检测** | 自动识别耗时阶段 |
| 💡 **智能建议** | 针对性优化建议 |
| 📈 **对比视图** | 多请求对比分析 |
| 📄 **报告导出** | JSON、HTML、Markdown格式 |
| 🖥️ **TUI仪表盘** | 交互式终端界面 |

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/TimeTrace-CLI.git
cd TimeTrace-CLI

# 安装
pip install -e .

# 或直接运行
python -m timetrace.main https://example.com
```

#### 基本用法

```bash
# 分析单个URL
timetrace https://example.com

# POST请求（JSON格式）
timetrace https://api.example.com/users -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'

# 多请求对比
timetrace https://example.com https://api.example.com --compare

# 生成HTML报告
timetrace https://example.com --report report.html --format html

# 启动TUI仪表盘
timetrace https://example.com --tui

# 显示瀑布图
timetrace https://example.com --waterfall
```

### 📖 详细使用指南

#### 命令行参数

```
timetrace [选项] URL [URL...]

位置参数:
  URL                   要分析的一个或多个URL

请求选项:
  -X, --method METHOD   HTTP方法（默认: GET）
  -H, --header HEADER   请求头（格式: 'Key: Value'）
  -d, --data DATA       请求体数据
  --timeout SECONDS     请求超时时间（默认: 30）

输出选项:
  -o, --output FILE     报告输出文件
  --format FORMAT       报告格式: json, html, markdown
  --tui                 启动TUI仪表盘
  --waterfall           显示瀑布图
  --compare             对比多个请求
  -q, --quiet           静默模式（仅输出报告）

分析选项:
  --no-analyze          跳过性能分析
  --repeat N            重复每个请求N次
```

### 💡 设计思路

TimeTrace-CLI 的设计遵循以下原则：

1. **零依赖** - 仅使用Python标准库，最大化可移植性
2. **开发者友好** - 清晰的输出、直观的命令、有用的建议
3. **性能优先** - 轻量快速，不影响工作流程
4. **视觉清晰** - 美观的终端输出，易于阅读

### 🤝 贡献指南

欢迎贡献代码！请随时提交Pull Request。

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 📄 开源协议

本项目采用MIT协议 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 專案介紹

**TimeTrace-CLI** 是一款輕量級、零依賴的終端HTTP請求計時分析與視覺化工具。它能夠精確測量HTTP請求的每個階段（DNS → TCP → TLS → 請求 → 首位元組 → 下載），幫助您快速定位效能瓶頸。

**為什麼選擇 TimeTrace-CLI？**
- 🔍 **詳細計時分析** - 測量HTTP請求的每個階段
- 📊 **視覺化瀑布圖** - 直觀展示時間分佈
- 🚨 **效能診斷** - 自動檢測瓶頸並提供優化建議
- 📈 **對比模式** - 多請求並行對比分析
- 📄 **多格式報告** - 支援JSON、HTML、Markdown匯出
- 🖥️ **TUI儀表板** - 互動式終端介面
- ⚡ **零依賴** - 純Python標準庫實現，無需安裝額外套件

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **計時分析** | DNS、TCP、TLS、請求、首位元組、下載各階段計時 |
| 📊 **瀑布圖** | 請求階段視覺化展示 |
| 🎯 **效能評分** | 0-100分詳細評分 |
| 🚨 **瓶頸檢測** | 自動識別耗時階段 |
| 💡 **智慧建議** | 針對性優化建議 |
| 📈 **對比視圖** | 多請求對比分析 |
| 📄 **報告匯出** | JSON、HTML、Markdown格式 |
| 🖥️ **TUI儀表板** | 互動式終端介面 |

### 🚀 快速開始

#### 安裝

```bash
# 複製儲存庫
git clone https://github.com/gitstq/TimeTrace-CLI.git
cd TimeTrace-CLI

# 安裝
pip install -e .

# 或直接執行
python -m timetrace.main https://example.com
```

#### 基本用法

```bash
# 分析單個URL
timetrace https://example.com

# POST請求（JSON格式）
timetrace https://api.example.com/users -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'

# 多請求對比
timetrace https://example.com https://api.example.com --compare

# 生成HTML報告
timetrace https://example.com --report report.html --format html

# 啟動TUI儀表板
timetrace https://example.com --tui

# 顯示瀑布圖
timetrace https://example.com --waterfall
```

### 📄 開源協議

本專案採用MIT協議 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Made with ❤️ by TimeTrace Team**

</div>
