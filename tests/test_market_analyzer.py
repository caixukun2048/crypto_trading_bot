#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
市场分析模块测试
"""

import unittest
import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_analyzer import MarketAnalyzer

class TestMarketAnalyzer(unittest.TestCase):
    """
    测试市场分析器类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.analysis_params = {
            'ma_periods': [5, 10, 20],
            'rsi': {
                'period': 14,
                'overbought': 70,
                'oversold': 30
            },
            'macd': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            },
            'bollinger': {
                'period': 20,
                'std_dev': 2
            }
        }
        
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=100, freq='H')
        
        # 模拟一个上升趋势的价格序列
        close = np.linspace(100, 150, 100) + np.random.normal(0, 3, 100)
        high = close + np.random.uniform(1, 5, 100)
        low = close - np.random.uniform(1, 5, 100)
        open_price = close - np.random.normal(0, 2, 100)
        volume = np.random.uniform(100, 1000, 100)
        
        self.test_data = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'symbol': 'BTC/USDT',
            'timeframe': '1h',
            'exchange': 'gateio',
            'funding_rate': np.random.uniform(-0.001, 0.001, 100)
        }, index=dates)
        
        # 创建市场分析器实例
        self.analyzer = MarketAnalyzer(self.analysis_params)
    
    @patch('talib.SMA')
    def test_calculate_indicators(self, mock_sma):
        """
        测试技术指标计算
        """
        # 模拟talib.SMA返回值
        mock_sma.return_value = np.array([110.0] * 100)
        
        # 调用_calculate_indicators方法
        indicators = self.analyzer._calculate_indicators(self.test_data)
        
        # 验证结果
        self.assertIsInstance(indicators, dict)
        self.assertIn('ma_5', indicators)
        mock_sma.assert_called()
    
    def test_identify_support_resistance(self):
        """
        测试支撑阻力位识别
        """
        result = self.analyzer._identify_support_resistance(self.test_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('support', result)
        self.assertIn('resistance', result)
        self.assertIsInstance(result['support'], list)
        self.assertIsInstance(result['resistance'], list)
    
    def test_analyze_market_structure(self):
        """
        测试市场结构分析
        """
        # 创建一个简单的indicators字典
        mock_indicators = {
            'ma_20': 110.0,
            'ma_50': 105.0,
            'rsi': 65.0,
            'macd': 0.5,
            'macd_signal': 0.3,
            'macd_hist': 0.2,
            'bb_upper': 120.0,
            'bb_middle': 110.0,
            'bb_lower': 100.0
        }
        
        result = self.analyzer._analyze_market_structure(self.test_data, mock_indicators)
        
        self.assertIsInstance(result, dict)
        self.assertIn('structure', result)
        self.assertIn('strength', result)
        self.assertIn('description', result)
    
    def test_analyze(self):
        """
        测试总体分析方法
        """
        # 此测试仅验证方法是否能正常运行
        with patch.object(self.analyzer, '_calculate_indicators', return_value={}):
            with patch.object(self.analyzer, '_identify_support_resistance', return_value={'support': [], 'resistance': []}):
                with patch.object(self.analyzer, '_analyze_market_structure', return_value={}):
                    with patch.object(self.analyzer, '_analyze_sentiment', return_value={}):
                        with patch.object(self.analyzer, '_determine_trend', return_value={}):
                            with patch.object(self.analyzer, '_analyze_volatility', return_value={}):
                                result = self.analyzer.analyze(self.test_data, 'BTC/USDT', '1h')
                                
                                self.assertIsInstance(result, dict)
                                self.assertEqual(result['symbol'], 'BTC/USDT')
                                self.assertEqual(result['timeframe'], '1h')

if __name__ == '__main__':
    unittest.main()