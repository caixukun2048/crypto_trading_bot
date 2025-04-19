#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
辅助函数模块

此模块提供各种辅助功能和实用工具函数。
"""

import time
import datetime
import pytz
import numpy as np
import pandas as pd

def timestamp_to_datetime(timestamp, timezone='Asia/Shanghai'):
    """
    将时间戳转换为指定时区的datetime对象
    
    Args:
        timestamp: Unix时间戳（毫秒）
        timezone: 时区名称
        
    Returns:
        datetime: 转换后的datetime对象
    """
    # 确保时间戳是毫秒
    if timestamp > 10**12:
        # 已经是毫秒时间戳
        ts = timestamp / 1000
    else:
        # 秒时间戳
        ts = timestamp
    
    dt_utc = datetime.datetime.fromtimestamp(ts, tz=pytz.UTC)
    dt_local = dt_utc.astimezone(pytz.timezone(timezone))
    
    return dt_local

def format_datetime(dt, format_str='%Y/%m/%d %H:%M:%S'):
    """
    格式化datetime对象为字符串
    
    Args:
        dt: datetime对象
        format_str: 格式字符串
        
    Returns:
        str: 格式化后的时间字符串
    """
    return dt.strftime(format_str)

def round_price(price, decimals=None):
    """
    根据价格大小自动或固定精度四舍五入
    
    Args:
        price: 价格数值
        decimals: 小数位数，如果为None则自动确定
        
    Returns:
        float: 四舍五入后的价格
    """
    if decimals is not None:
        return round(price, decimals)
    
    # 自动确定小数位数
    if price >= 1000:
        return round(price, 1)
    elif price >= 100:
        return round(price, 2)
    elif price >= 10:
        return round(price, 3)
    elif price >= 1:
        return round(price, 4)
    elif price >= 0.1:
        return round(price, 5)
    else:
        return round(price, 6)

def format_price(price, decimals=None):
    """
    格式化价格显示
    
    Args:
        price: 价格数值
        decimals: 小数位数，如果为None则自动确定
        
    Returns:
        str: 格式化后的价格字符串
    """
    rounded_price = round_price(price, decimals)
    
    # 确定小数位数
    if decimals is None:
        if price >= 1000:
            decimals = 1
        elif price >= 100:
            decimals = 2
        elif price >= 10:
            decimals = 3
        elif price >= 1:
            decimals = 4
        elif price >= 0.1:
            decimals = 5
        else:
            decimals = 6
    
    # 格式化价格
    format_str = f"{{:.{decimals}f}}"
    return format_str.format(rounded_price)

def format_percentage(value, decimals=2):
    """
    格式化百分比显示
    
    Args:
        value: 百分比值（小数形式，如0.1234表示12.34%）
        decimals: 小数位数
        
    Returns:
        str: 格式化后的百分比字符串
    """
    percentage = value * 100
    format_str = f"{{:.{decimals}f}}%"
    return format_str.format(percentage)

def calculate_change_percentage(current, previous):
    """
    计算变化百分比
    
    Args:
        current: 当前值
        previous: 之前的值
        
    Returns:
        float: 变化百分比（小数形式）
    """
    if previous == 0:
        return 0
    
    return (current - previous) / previous

def normalize_symbol(symbol):
    """
    标准化交易对符号，确保格式一致
    
    Args:
        symbol: 交易对符号，如'BTC/USDT'或'BTCUSDT'
        
    Returns:
        str: 标准化后的交易对符号，格式为'BTC/USDT'
    """
    # 已经是标准格式
    if '/' in symbol:
        return symbol
    
    # 常见的稳定币
    stablecoins = ['USDT', 'USD', 'USDC', 'BUSD', 'DAI', 'TUSD']
    
    # 尝试识别交易对
    for stablecoin in stablecoins:
        if symbol.endswith(stablecoin):
            base = symbol[:-len(stablecoin)]
            quote = stablecoin
            return f"{base}/{quote}"
    
    # 如果无法识别，尝试提取最后3或4个字符作为计价币
    if len(symbol) > 4:
        base = symbol[:-4]
        quote = symbol[-4:]
        return f"{base}/{quote}"
    elif len(symbol) > 3:
        base = symbol[:-3]
        quote = symbol[-3:]
        return f"{base}/{quote}"
    
    # 无法解析时原样返回
    return symbol