#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
信号生成模块测试
"""

import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.signal_generator import SignalGenerator

class TestSignalGenerator(unittest.TestCase):
    """
    测试信号生成器类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.signal_params = {
            'thresholds': {
                'strong_buy': 80,
                'buy': 60,
                'neutral': 40,
                'sell': 20,
                'strong_sell': 0
            },
            'weights': {
                'trend': 0.3,
                'oscillators': 0.3,
                'volume': 0.2,
                'sentiment': 0.2
            }
        }
        
        # 创建模拟分析结果
        self.mock_analysis_result = {
            'symbol': 'BTC/USDT',
            'timeframe': '1h',
            'last_price': 40000.0,
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
                'atr': 800.0
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
            }
        }
        
        # 创建信号生成器实例
        self.generator = SignalGenerator(self.signal_params)
    
    def test_calculate_score(self):
        """
        测试综合得分计算
        """
        score = self.generator._calculate_score(self.mock_analysis_result)
        
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 100)
    
    def test_determine_direction(self):
        """
        测试交易方向确定
        """
        # 测试多头信号
        direction = self.generator._determine_direction(70, self.mock_analysis_result)
        self.assertEqual(direction, 'long')
        
        # 测试空头信号
        direction = self.generator._determine_direction(15, self.mock_analysis_result)
        self.assertEqual(direction, 'short')
        
        # 测试中性信号
        direction = self.generator._determine_direction(50, self.mock_analysis_result)
        self.assertEqual(direction, 'neutral')
    
    def test_determine_stop_loss(self):
        """
        测试止损位确定
        """
        # 测试多头止损
        stop_loss = self.generator._determine_stop_loss('long', 40000.0, self.mock_analysis_result)
        self.assertLess(stop_loss, 40000.0)
        
        # 测试空头止损
        stop_loss = self.generator._determine_stop_loss('short', 40000.0, self.mock_analysis_result)
        self.assertGreater(stop_loss, 40000.0)
    
    def test_determine_target_price(self):
        """
        测试目标价格确定
        """
        # 测试多头目标价
        target = self.generator._determine_target_price('long', 40000.0, 39000.0, self.mock_analysis_result)
        self.assertGreater(target, 40000.0)
        
        # 测试空头目标价
        target = self.generator._determine_target_price('short', 40000.0, 41000.0, self.mock_analysis_result)
        self.assertLess(target, 40000.0)
    
    def test_generate_signal(self):
        """
        测试信号生成
        """
        signal = self.generator.generate_signal(self.mock_analysis_result)
        
        self.assertIsInstance(signal, dict)
        self.assertEqual(signal['symbol'], 'BTC/USDT')
        self.assertEqual(signal['timeframe'], '1h')
        self.assertIn(signal['direction'], ['long', 'short', 'neutral'])
        self.assertIn('entry_price', signal)
        self.assertIn('stop_loss', signal)
        self.assertIn('target_price', signal)
        self.assertIn('risk_params', signal)
        self.assertIn('signal_strength', signal)

if __name__ == '__main__':
    unittest.main()