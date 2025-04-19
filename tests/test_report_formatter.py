#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
报告格式化模块测试
"""

import unittest
import os
import sys
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.report_formatter import ReportFormatter

class TestReportFormatter(unittest.TestCase):
    """
    测试报告格式化器类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        # 创建模拟市场数据
        dates = pd.date_range('2023-01-01', periods=24, freq='H')
        self.mock_market_data = pd.DataFrame({
            'open': [39000.0] * 24,
            'high': [40000.0] * 24,
            'low': [38000.0] * 24,
            'close': [39500.0] * 24,
            'volume': [1000.0] * 24,
            'symbol': ['BTC/USDT'] * 24,
            'timeframe': ['1h'] * 24,
            'exchange': ['gateio'] * 24,
            'funding_rate': [0.0001] * 24
        }, index=dates)
        
        # 创建模拟分析结果
        self.mock_analysis_result = {
            'symbol': 'BTC/USDT',
            'timeframe': '1h',
            'indicators': {
                'ma_20': 39000.0,
                'ma_50': 38000.0,
                'rsi': 65.0,
                'macd': 100.0,
                'macd_signal': 50.0,
                'macd_hist': 50.0,
                'k': 70.0,
                'd': 60.0,
                'j': 80.0,
                'bb_upper': 41000.0,
                'bb_middle': 40000.0,
                'bb_lower': 39000.0,
                'bb_width': 0.05
            },
            'support_resistance': {
                'support': [39000.0, 38000.0],
                'resistance': [41000.0, 42000.0]
            },
            'market_structure': {
                'structure': 'bullish',
                'strength': 75.0,
                'description': '看涨结构，价格站在大多数均线上方'
            },
            'sentiment': {
                'overall': 'bullish',
                'long_short_ratio': 1.5,
                'state': 'normal',
                'funding_rate_impact': 'neutral'
            },
            'trend': {
                'direction': 'uptrend',
                'strength': 70.0,
                'description': '强劲上升趋势，均线多头排列'
            },
            'volatility': {
                'current': 0.02,
                'average': 0.015,
                'state': 'normal',
                'description': '正常波动，市场稳定'
            },
            'last_price': 39500.0
        }
        
        # 创建模拟交易信号
        self.mock_signal = {
            'symbol': 'BTC/USDT',
            'timeframe': '1h',
            'direction': 'long',
            'score': 70.0,
            'entry_price': 39500.0,
            'stop_loss': 38700.0,
            'target_price': 41100.0,
            'risk_params': {
                'risk_percent': 2.0,
                'reward_percent': 4.0,
                'risk_reward_ratio': 2.0,
                'suggested_leverage': 10,
                'position_size_percent': 20.0,
                'volatility': 2.0
            },
            'signal_strength': {
                'stars': 4,
                'reliability': '较为可靠',
                'timing': '可以考虑'
            },
            'timestamp': datetime.now()
        }
        
        # 创建模拟配置
        self.mock_config = {
            'exchanges': {
                'gateio': {
                    'api_key': 'test_api_key',
                    'secret_key': 'test_secret_key'
                }
            }
        }
        
        # 创建报告格式化器实例
        self.formatter = ReportFormatter()
    
    def test_format(self):
        """
        测试报告格式化
        """
        report = self.formatter.format(
            symbol='BTC/USDT',
            timeframe='1h',
            market_data=self.mock_market_data,
            analysis_result=self.mock_analysis_result,
            signal=self.mock_signal,
            config=self.mock_config
        )
        
        # 验证报告是否为字符串
        self.assertIsInstance(report, str)
        
        # 验证报告是否包含关键信息
        self.assertIn('BTC/USDT', report)
        self.assertIn('1小时', report)
        self.assertIn('当前价格', report)
        self.assertIn('资金费率', report)
        self.assertIn('市场情绪', report)
        self.assertIn('关键价位', report)
        self.assertIn('技术分析', report)
        self.assertIn('信号强度', report)
        self.assertIn('交易建议', report)
        self.assertIn('风险管理', report)
    
    def test_get_sentiment_description(self):
        """
        测试市场情绪描述生成
        """
        # 测试看涨情绪
        sentiment = self.formatter._get_sentiment_description({
            'sentiment': {'overall': 'bullish'}
        })
        self.assertEqual(sentiment, '看涨')
        
        # 测试看跌情绪
        sentiment = self.formatter._get_sentiment_description({
            'sentiment': {'overall': 'bearish'}
        })
        self.assertEqual(sentiment, '看跌')
        
        # 测试中性情绪
        sentiment = self.formatter._get_sentiment_description({
            'sentiment': {'overall': 'neutral'}
        })
        self.assertEqual(sentiment, '中性')
    
    def test_format_key_levels(self):
        """
        测试关键价位格式化
        """
        result = self.formatter._format_key_levels(
            39500.0,
            self.mock_analysis_result
        )
        
        self.assertIsInstance(result, str)
        self.assertIn('强阻力位', result)
        self.assertIn('弱阻力位', result)
        self.assertIn('当前价格', result)
        self.assertIn('强支撑位', result)
        self.assertIn('弱支撑位', result)

if __name__ == '__main__':
    unittest.main()