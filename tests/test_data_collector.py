#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据采集模块测试
"""

import unittest
import os
import sys
import pandas as pd
from unittest.mock import MagicMock, patch

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collector import DataCollector

class TestDataCollector(unittest.TestCase):
    """
    测试数据采集器类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.mock_config = {
            'gateio': {
                'api_key': 'test_api_key',
                'secret_key': 'test_secret_key',
                'use_testnet': True
            }
        }
        self.symbols = ['BTC/USDT', 'ETH/USDT']
        self.timeframes = ['1h', '4h']
        
        # 创建模拟交易所
        self.mock_exchange = MagicMock()
        self.mock_exchange.id = 'gateio'
        self.mock_exchange.load_markets.return_value = None
        
        # 模拟OHLCV数据
        self.mock_ohlcv = [
            [1577836800000, 7200.0, 7300.0, 7100.0, 7250.0, 100.0],
            [1577840400000, 7250.0, 7400.0, 7200.0, 7350.0, 200.0]
        ]
        self.mock_exchange.fetch_ohlcv.return_value = self.mock_ohlcv
        
        # 模拟ticker数据
        self.mock_ticker = {
            'last': 7350.0,
            'bid': 7340.0,
            'ask': 7360.0,
            'volume': 1000.0
        }
        self.mock_exchange.fetch_ticker.return_value = self.mock_ticker
    
    @patch('ccxt.gateio')
    def test_init_exchanges(self, mock_ccxt_gateio):
        """
        测试交易所初始化
        """
        mock_ccxt_gateio.return_value = self.mock_exchange
        
        collector = DataCollector(self.mock_config, self.symbols, self.timeframes)
        self.assertEqual(list(collector.exchanges.keys()), ['gateio'])
        self.assertEqual(collector.symbols, self.symbols)
        self.assertEqual(collector.timeframes, self.timeframes)
    
    @patch('ccxt.gateio')
    def test_fetch_ohlcv(self, mock_ccxt_gateio):
        """
        测试获取K线数据
        """
        mock_ccxt_gateio.return_value = self.mock_exchange
        
        collector = DataCollector(self.mock_config, self.symbols, self.timeframes)
        result = collector._fetch_ohlcv(self.mock_exchange, 'BTC/USDT', '1h')
        
        self.assertEqual(result, self.mock_ohlcv)
        self.mock_exchange.fetch_ohlcv.assert_called_once_with('BTC/USDT', '1h', limit=100)

if __name__ == '__main__':
    unittest.main()