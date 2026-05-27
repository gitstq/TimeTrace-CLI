#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeTrace-CLI Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="timetrace-cli",
    version="1.0.0",
    author="TimeTrace Team",
    author_email="timetrace@example.com",
    description="Lightweight Terminal HTTP Request Timing Analysis & Visualization Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/TimeTrace-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "timetrace=timetrace.main:main",
        ],
    },
    keywords=[
        "http", "timing", "performance", "analysis", "cli", "terminal",
        "network", "monitoring", "debugging", "api-testing", "devtools",
        "waterfall", "latency", "response-time", "ttfb", "dns",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/gitstq/TimeTrace-CLI/issues",
        "Documentation": "https://github.com/gitstq/TimeTrace-CLI#readme",
        "Source Code": "https://github.com/gitstq/TimeTrace-CLI",
    },
)
