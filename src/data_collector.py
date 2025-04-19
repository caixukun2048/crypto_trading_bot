#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据采集模块

负责从交易所API获取现货和合约市场数据。
"""

import time
import logging
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
from utils.logger import get_logger
from utils.helpers import timestamp_to_datetime, normalize_symbol

class DataCollector:
    """
    数据采集器类
    
    负责从交易所获取现货和合约市场数据，支持多个交易所、多个交易对和多个时间周期。
    """
    
    def __init__(self, exchanges, symbols, timeframes):
        """
        初始化数据采集器
        
        Args:
            exchanges: 交易所配置字典
            symbols: 交易对列表
            timeframes: 时间周期列表
        """
        self.logger = get_logger('data_collector')
        self.exchanges = self._init_exchanges(exchanges)
        self.symbols = [normalize_symbol(s) for s in symbols]
        self.timeframes = timeframes
        self.logger.info(f"数据采集器初始化完成，交易所: {list(self.exchanges.keys())}, "
                         f"交易对: {self.symbols}, 时间周期: {self.timeframes}")
    
    def _init_exchanges(self, exchange_configs):
        """
        初始化交易所API
        
        Args:
            exchange_configs: 交易所配置字典
            
        Returns:
            dict: 交易所API实例字典
        """
        exchanges = {}
        
        for name, config in exchange_configs.items():
            try:
                # 获取ccxt中对应的交易所类
                exchange_class = getattr(ccxt, name)
                
                # 创建交易所实例
                exchange = exchange_class({
                    'apiKey': config.get('api_key'),
                    'secret': config.get('secret_key'),
                    'timeout': 30000,  # 30秒超时
                    'enableRateLimit': True,  # 启用请求频率限制
                })
                
                # 如果配置了使用测试网络
                if config.get('use_testnet', False):
                    if hasattr(exchange, 'set_sandbox_mode'):
                        exchange.set_sandbox_mode(True)
                    else:
                        self.logger.warning(f"交易所 {name} 不支持测试网络模式")
                
                # 加载市场
                exchange.load_markets()
                
                exchanges[name] = exchange
                self.logger.info(f"成功初始化交易所 {name}")
                
            except Exception as e:
                self.logger.error(f"初始化交易所 {name} 失败: {e}")
        
        if not exchanges:
            raise ValueError("没有成功初始化任何交易所")
        
        return exchanges
    
    def collect_data(self):
        """
        采集所有配置的交易对和时间周期的数据
        
        Returns:
            dict: 采集到的数据，格式为 {(symbol, timeframe): dataframe}
        """
        self.logger.info("开始采集市场数据")
        market_data = {}
        
        # 使用第一个交易所作为数据源
        exchange_name = list(self.exchanges.keys())[0]
        exchange = self.exchanges[exchange_name]
        
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                try:
                    # 采集K线数据
                    ohlcv_data = self._fetch_ohlcv(exchange, symbol, timeframe)
                    
                    # 采集现货Ticker数据
                    spot_ticker = self._fetch_spot_ticker(exchange, symbol)
                    
                    # 采集合约相关数据
                    funding_rate = self._fetch_funding_rate(exchange, symbol)
                    open_interest = self._fetch_open_interest(exchange, symbol)
                    
                    # 将所有数据整合到一个DataFrame中
                    df = self._process_data(ohlcv_data, spot_ticker, funding_rate, open_interest, symbol, timeframe)
                    
                    # 存储数据
                    market_data[(symbol, timeframe)] = df
                    
                    self.logger.info(f"成功采集 {symbol} 的 {timeframe} 周期数据")
                    
                except Exception as e:
                    self.logger.error(f"采集 {symbol} 的 {timeframe} 周期数据失败: {e}")
        
        self.logger.info(f"数据采集完成，共采集 {len(market_data)} 组数据")
        return market_data
    
    def _fetch_ohlcv(self, exchange, symbol, timeframe, limit=100):
        """
        获取K线数据
        
        Args:
            exchange: 交易所API实例
            symbol: 交易对
            timeframe: 时间周期
            limit: 获取的K线数量
            
        Returns:
            list: K线数据列表
        """
        self.logger.debug(f"获取 {symbol} 的 {timeframe} K线数据")
        
        try:
            # 尝试获取合约市场的K线数据
            if hasattr(exchange, 'fapiPublicGetKlines') and 'futures' in exchange.markets.get(symbol, {}):
                # 针对Binance等交易所的合约API
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit, params={'contractType': 'perpetual'})
            else:
                # 普通现货K线
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            return ohlcv
        
        except Exception as e:
            self.logger.error(f"获取 {symbol} 的 {timeframe} K线数据失败: {e}")
            # 返回空列表表示失败
            return []
    
    def _fetch_spot_ticker(self, exchange, symbol):
        """
        获取现货市场ticker数据
        
        Args:
            exchange: 交易所API实例
            symbol: 交易对
            
        Returns:
            dict: Ticker数据
        """
        self.logger.debug(f"获取 {symbol} 的现货Ticker数据")
        
        try:
            ticker = exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            self.logger.error(f"获取 {symbol} 的现货Ticker数据失败: {e}")
            return {}
    
    def _fetch_funding_rate(self, exchange, symbol):
        """
        获取资金费率
        
        Args:
            exchange: 交易所API实例
            symbol: 交易对
            
        Returns:
            float: 资金费率
        """
        self.logger.debug(f"获取 {symbol} 的资金费率")
        
        try:
            if hasattr(exchange, 'fetchFundingRate'):
                funding_rate = exchange.fetchFundingRate(symbol)
                return funding_rate.get('fundingRate', 0)
            else:
                self.logger.warning(f"交易所 {exchange.id} 不支持获取资金费率")
                return 0
        except Exception as e:
            self.logger.error(f"获取 {symbol} 的资金费率失败: {e}")
            return 0
    
    def _fetch_open_interest(self, exchange, symbol):
        """
        获取未平仓合约数据
        
        Args:
            exchange: 交易所API实例
            symbol: 交易对
            
        Returns:
            float: 未平仓合约价值
        """
        self.logger.debug(f"获取 {symbol} 的未平仓合约数据")
        
        try:
            if hasattr(exchange, 'fetchOpenInterest'):
                open_interest = exchange.fetchOpenInterest(symbol)
                return open_interest.get('openInterestAmount', 0)
            else:
                self.logger.warning(f"交易所 {exchange.id} 不支持获取未平仓合约数据")
                return 0
        except Exception as e:
            self.logger.error(f"获取 {symbol} 的未平仓合约数据失败: {e}")
            return 0
    
    def _process_data(self, ohlcv_data, spot_ticker, funding_rate, open_interest, symbol, timeframe):
        """
        处理并整合所有采集到的数据
        
        Args:
            ohlcv_data: K线数据
            spot_ticker: 现货Ticker数据
            funding_rate: 资金费率
            open_interest: 未平仓合约数据
            symbol: 交易对
            timeframe: 时间周期
            
        Returns:
            pandas.DataFrame: 处理后的数据
        """
        # 创建K线数据的DataFrame
        if ohlcv_data:
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = df['timestamp'].apply(lambda x: timestamp_to_datetime(x))
            df.set_index('timestamp', inplace=True)
        else:
            # 如果没有K线数据，创建空DataFrame
            df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        
        # 添加其他数据
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        df['exchange'] = list(self.exchanges.keys())[0]
        
        # 添加现货数据
        if spot_ticker:
            df['spot_last'] = spot_ticker.get('last', 0)
            df['spot_bid'] = spot_ticker.get('bid', 0)
            df['spot_ask'] = spot_ticker.get('ask', 0)
            df['spot_volume'] = spot_ticker.get('volume', 0)
        
        # 添加合约特有数据
        df['funding_rate'] = funding_rate
        df['open_interest'] = open_interest
        
        # 计算期现差
        if 'spot_last' in df.columns and not df.empty:
            df['basis'] = (df['close'] - df['spot_last']) / df['spot_last']
        
        return df