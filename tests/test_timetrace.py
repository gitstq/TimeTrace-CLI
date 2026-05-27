#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for TimeTrace-CLI
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from timetrace.timing import TimingResult, TimingAnalyzer
from timetrace.request import RequestBuilder, RequestConfig
from timetrace.analysis import PerformanceAnalyzer, BottleneckDetector, Severity
from timetrace.report import ReportGenerator
from timetrace.utils import validate_url, parse_headers, format_bytes, format_duration


class TestTimingResult(unittest.TestCase):
    """Test TimingResult class"""
    
    def test_create_timing_result(self):
        """Test creating a timing result"""
        result = TimingResult(
            url="https://example.com",
            method="GET",
            dns_time=50.0,
            connect_time=100.0,
            tls_time=80.0,
            request_time=10.0,
            first_byte_time=200.0,
            download_time=150.0,
            status_code=200,
            response_size=1024
        )
        
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.method, "GET")
        self.assertEqual(result.dns_time, 50.0)
        self.assertEqual(result.status_code, 200)
    
    def test_to_dict(self):
        """Test converting to dictionary"""
        result = TimingResult(
            url="https://example.com",
            dns_time=50.0,
            total_time=500.0
        )
        
        data = result.to_dict()
        
        self.assertIn("url", data)
        self.assertIn("timing", data)
        self.assertEqual(data["url"], "https://example.com")
    
    def test_get_waterfall_data(self):
        """Test getting waterfall data"""
        result = TimingResult(
            url="https://example.com",
            dns_time=50.0,
            connect_time=100.0,
            tls_time=80.0,
            first_byte_time=200.0,
            download_time=150.0
        )
        
        waterfall = result.get_waterfall_data()
        
        self.assertEqual(len(waterfall), 5)
        self.assertEqual(waterfall[0][0], "DNS")


class TestRequestBuilder(unittest.TestCase):
    """Test RequestBuilder class"""
    
    def test_build_simple_request(self):
        """Test building a simple request"""
        builder = RequestBuilder()
        config = builder.url("https://example.com").method("GET").build()
        
        self.assertEqual(config.url, "https://example.com")
        self.assertEqual(config.method, "GET")
    
    def test_build_request_with_headers(self):
        """Test building request with headers"""
        builder = RequestBuilder()
        config = (
            builder
            .url("https://example.com")
            .header("Content-Type", "application/json")
            .header("Authorization", "Bearer token")
            .build()
        )
        
        self.assertEqual(config.headers["Content-Type"], "application/json")
        self.assertEqual(config.headers["Authorization"], "Bearer token")
    
    def test_build_post_request(self):
        """Test building POST request"""
        builder = RequestBuilder()
        config = (
            builder
            .url("https://example.com/api")
            .method("POST")
            .json_body({"name": "test"})
            .build()
        )
        
        self.assertEqual(config.method, "POST")
        self.assertIn("Content-Type", config.headers)
    
    def test_invalid_url(self):
        """Test invalid URL validation"""
        builder = RequestBuilder()
        
        with self.assertRaises(ValueError):
            builder.url("invalid-url").build()
    
    def test_invalid_method(self):
        """Test invalid method validation"""
        builder = RequestBuilder()
        
        with self.assertRaises(ValueError):
            builder.url("https://example.com").method("INVALID").build()


class TestPerformanceAnalyzer(unittest.TestCase):
    """Test PerformanceAnalyzer class"""
    
    def test_analyze_good_performance(self):
        """Test analyzing good performance"""
        result = TimingResult(
            url="https://example.com",
            dns_time=20.0,
            connect_time=50.0,
            tls_time=50.0,
            first_byte_time=100.0,
            download_time=200.0,
            status_code=200
        )
        
        analyzer = PerformanceAnalyzer()
        score, issues = analyzer.analyze(result)
        
        self.assertGreater(score.overall, 70)
        self.assertEqual(len(issues), 0)
    
    def test_analyze_poor_performance(self):
        """Test analyzing poor performance"""
        result = TimingResult(
            url="https://example.com",
            dns_time=500.0,
            connect_time=1000.0,
            tls_time=800.0,
            first_byte_time=2000.0,
            download_time=5000.0,
            status_code=200
        )
        
        analyzer = PerformanceAnalyzer()
        score, issues = analyzer.analyze(result)
        
        self.assertLess(score.overall, 50)
        self.assertGreater(len(issues), 0)
    
    def test_analyze_error(self):
        """Test analyzing error result"""
        result = TimingResult(
            url="https://example.com",
            error="Connection failed"
        )
        
        analyzer = PerformanceAnalyzer()
        score, issues = analyzer.analyze(result)
        
        self.assertEqual(score.overall, 0.0)
        self.assertGreater(len(issues), 0)


class TestBottleneckDetector(unittest.TestCase):
    """Test BottleneckDetector class"""
    
    def test_detect_dns_bottleneck(self):
        """Test detecting DNS bottleneck"""
        result = TimingResult(
            url="https://example.com",
            dns_time=800.0,
            connect_time=100.0,
            tls_time=100.0,
            first_byte_time=100.0,
            download_time=100.0,
            request_time=10.0,
            status_code=200
        )
        result.total_time = 1210.0  # Set total time
        
        detector = BottleneckDetector()
        bottleneck = detector.detect(result)
        
        self.assertEqual(bottleneck, "dns")
    
    def test_detect_ttfb_bottleneck(self):
        """Test detecting TTFB bottleneck"""
        result = TimingResult(
            url="https://example.com",
            dns_time=50.0,
            connect_time=50.0,
            tls_time=50.0,
            first_byte_time=2000.0,
            download_time=100.0,
            request_time=10.0,
            status_code=200
        )
        result.total_time = 2260.0  # Set total time
        
        detector = BottleneckDetector()
        bottleneck = detector.detect(result)
        
        self.assertEqual(bottleneck, "ttfb")
    
    def test_get_recommendations(self):
        """Test getting recommendations"""
        detector = BottleneckDetector()
        
        recommendations = detector.get_recommendations("dns")
        self.assertGreater(len(recommendations), 0)
        
        recommendations = detector.get_recommendations("ttfb")
        self.assertGreater(len(recommendations), 0)


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator class"""
    
    def test_generate_json_report(self):
        """Test generating JSON report"""
        result = TimingResult(
            url="https://example.com",
            dns_time=50.0,
            connect_time=100.0,
            total_time=500.0,
            status_code=200
        )
        
        generator = ReportGenerator()
        json_report = generator.generate_json(result)
        
        self.assertIn('"url": "https://example.com"', json_report)
        self.assertIn('"dns_ms"', json_report)
    
    def test_generate_html_report(self):
        """Test generating HTML report"""
        result = TimingResult(
            url="https://example.com",
            dns_time=50.0,
            total_time=500.0,
            status_code=200
        )
        
        generator = ReportGenerator()
        html_report = generator.generate_html(result)
        
        self.assertIn("<!DOCTYPE html>", html_report)
        self.assertIn("https://example.com", html_report)
    
    def test_generate_markdown_report(self):
        """Test generating Markdown report"""
        result = TimingResult(
            url="https://example.com",
            dns_time=50.0,
            total_time=500.0,
            status_code=200
        )
        
        generator = ReportGenerator()
        md_report = generator.generate_markdown(result)
        
        self.assertIn("# ⏱️ TimeTrace Report", md_report)
        self.assertIn("https://example.com", md_report)


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_validate_url_valid(self):
        """Test validating valid URLs"""
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://example.com/path"))
        self.assertTrue(validate_url("https://example.com:8080/path?query=1"))
    
    def test_validate_url_invalid(self):
        """Test validating invalid URLs"""
        self.assertFalse(validate_url("invalid-url"))
        self.assertFalse(validate_url("ftp://example.com"))
        self.assertFalse(validate_url(""))
    
    def test_parse_headers(self):
        """Test parsing headers"""
        headers = parse_headers(["Content-Type: application/json", "Authorization: Bearer token"])
        
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer token")
    
    def test_format_bytes(self):
        """Test formatting bytes"""
        self.assertEqual(format_bytes(500), "500.0 B")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1048576), "1.0 MB")
    
    def test_format_duration(self):
        """Test formatting duration"""
        self.assertEqual(format_duration(500), "500.0ms")
        self.assertEqual(format_duration(1500), "1.50s")


if __name__ == "__main__":
    unittest.main()
