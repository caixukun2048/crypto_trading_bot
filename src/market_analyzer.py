#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
市场分析模块

负责对采集到的市场数据进行分析，计算各种技术指标和识别市场结构。
"""

import numpy as np
import pandas as pd
import logging
import talib
from utils.logger import get_logger
from utils.helpers import format_price, format_percentage

class MarketAnalyzer:
    """
    市场分析器类
    
    负责分析市场数据，计算技术指标，识别支撑/阻力位，分析市场结构等。
    """
    
    def __init__(self, params):
        """
        初始化市场分析器
        
        Args:
            params: 分析参数字典
        """
        self.logger = get_logger('market_analyzer')
        self.params = params
        self.logger.info("市场分析器初始化完成")
    
    def analyze(self, data, symbol, timeframe):
        """
        分析市场数据
        
        Args:
            data: 市场数据DataFrame
            symbol: 交易对
            timeframe: 时间周期
            
        Returns:
            dict: 分析结果字典
        """
        self.logger.info(f"开始分析 {symbol} 的 {timeframe} 周期数据")
        
        if data is None or data.empty:
            self.logger.warning(f"{symbol} 的 {timeframe} 周期数据为空，无法分析")
            return None
        
        try:
            # 复制数据，避免修改原始数据
            df = data.copy()
            
            # 计算基本技术指标
            indicators = self._calculate_indicators(df)
            
            # 识别支撑阻力位
            support_resistance = self._identify_support_resistance(df)
            
            # 分析市场结构
            market_structure = self._analyze_market_structure(df, indicators)
            
            # 分析市场情绪
            sentiment = self._analyze_sentiment(df, indicators)
            
            # 判断趋势
            trend = self._determine_trend(df, indicators)
            
            # 分析波动率
            volatility = self._analyze_volatility(df)
            
            # 整合所有分析结果
            analysis_result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'indicators': indicators,
                'support_resistance': support_resistance,
                'market_structure': market_structure,
                'sentiment': sentiment,
                'trend': trend,
                'volatility': volatility,
                'last_price': df['close'].iloc[-1] if not df.empty else None,
                'data': df
            }
            
            self.logger.info(f"{symbol} 的 {timeframe} 周期数据分析完成")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"分析 {symbol} 的 {timeframe} 周期数据时出错: {e}", exc_info=True)
            return None
    
    def _calculate_indicators(self, df):
        """
        计算技术指标
        
        Args:
            df: 数据DataFrame
            
        Returns:
            dict: 技术指标字典
        """
        indicators = {}
        
        try:
            # 确保有足够的数据
            if len(df) < 50:
                self.logger.warning("数据量不足，无法计算某些技术指标")
                return indicators
            
            # 提取价格数据
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            volume = df['volume'].values
            
            # 计算移动平均线
            for period in self.params.get('ma_periods', [5, 10, 20, 50, 100, 200]):
                if len(close) >= period:
                    ma = talib.SMA(close, timeperiod=period)
                    indicators[f'ma_{period}'] = ma[-1]
            
            # 计算指数移动平均线
            for period in self.params.get('ma_periods', [5, 10, 20, 50, 100, 200]):
                if len(close) >= period:
                    ema = talib.EMA(close, timeperiod=period)
                    indicators[f'ema_{period}'] = ema[-1]
            
            # 计算RSI
            rsi_period = self.params.get('rsi', {}).get('period', 14)
            if len(close) >= rsi_period:
                rsi = talib.RSI(close, timeperiod=rsi_period)
                indicators['rsi'] = rsi[-1]
            
            # 计算MACD
            macd_params = self.params.get('macd', {})
            fast_period = macd_params.get('fast_period', 12)
            slow_period = macd_params.get('slow_period', 26)
            signal_period = macd_params.get('signal_period', 9)
            
            if len(close) >= slow_period + signal_period:
                macd, macd_signal, macd_hist = talib.MACD(
                    close, 
                    fastperiod=fast_period, 
                    slowperiod=slow_period, 
                    signalperiod=signal_period
                )
                indicators['macd'] = macd[-1]
                indicators['macd_signal'] = macd_signal[-1]
                indicators['macd_hist'] = macd_hist[-1]
            
            # 计算KDJ
            kdj_params = self.params.get('kdj', {})
            k_period = kdj_params.get('k_period', 9)
            d_period = kdj_params.get('d_period', 3)
            j_period = kdj_params.get('j_period', 3)
            
            if len(close) >= k_period + d_period:
                k, d = talib.STOCH(
                    high, 
                    low, 
                    close, 
                    fastk_period=k_period, 
                    slowk_period=d_period, 
                    slowd_period=j_period
                )
                indicators['k'] = k[-1]
                indicators['d'] = d[-1]
                # 计算J值: 3*K - 2*D
                indicators['j'] = 3 * k[-1] - 2 * d[-1]
            
            # 计算布林带
            bb_params = self.params.get('bollinger', {})
            bb_period = bb_params.get('period', 20)
            bb_std = bb_params.get('std_dev', 2)
            
            if len(close) >= bb_period:
                upper, middle, lower = talib.BBANDS(
                    close, 
                    timeperiod=bb_period, 
                    nbdevup=bb_std, 
                    nbdevdn=bb_std, 
                    matype=0
                )
                indicators['bb_upper'] = upper[-1]
                indicators['bb_middle'] = middle[-1]
                indicators['bb_lower'] = lower[-1]
                # 计算带宽
                indicators['bb_width'] = (upper[-1] - lower[-1]) / middle[-1]
            
            # 计算ATR
            atr_period = 14
            if len(close) >= atr_period:
                atr = talib.ATR(high, low, close, timeperiod=atr_period)
                indicators['atr'] = atr[-1]
                # 计算ATR百分比
                indicators['atr_percent'] = atr[-1] / close[-1]
            
            # 计算抛物线转向指标 (SAR)
            if len(close) >= 15:
                sar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
                indicators['sar'] = sar[-1]
            
            # 计算CCI (商品通道指数)
            cci_period = 14
            if len(close) >= cci_period:
                cci = talib.CCI(high, low, close, timeperiod=cci_period)
                indicators['cci'] = cci[-1]
            
            # 计算OBV (能量潮)
            if len(close) >= 2:
                obv = talib.OBV(close, volume)
                indicators['obv'] = obv[-1]
                # 计算OBV变化率
                indicators['obv_change'] = (obv[-1] - obv[-10]) / abs(obv[-10]) if abs(obv[-10]) > 0 else 0
            
            # 添加一些自定义指标...
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"计算技术指标时出错: {e}", exc_info=True)
            return indicators
    
    def _identify_support_resistance(self, df, n_levels=2):
        """
        识别支撑和阻力位
        
        Args:
            df: 数据DataFrame
            n_levels: 识别的支撑/阻力位数量
            
        Returns:
            dict: 支撑和阻力位字典
        """
        result = {
            'support': [],
            'resistance': []
        }
        
        try:
            # 确保有足够的数据
            if len(df) < 30:
                self.logger.warning("数据量不足，无法识别支撑阻力位")
                return result
            
            # 获取最近的价格数据
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            current_price = close[-1]
            
            # 识别局部高点和低点
            local_highs = []
            local_lows = []
            
            for i in range(2, len(df) - 2):
                # 局部高点: 比前后两个点都高
                if high[i] > high[i-1] and high[i] > high[i-2] and high[i] > high[i+1] and high[i] > high[i+2]:
                    local_highs.append((i, high[i]))
                
                # 局部低点: 比前后两个点都低
                if low[i] < low[i-1] and low[i] < low[i-2] and low[i] < low[i+1] and low[i] < low[i+2]:
                    local_lows.append((i, low[i]))
            
            # 合并相近的点 (价格差距小于0.5%的点)
            def merge_levels(levels, threshold=0.005):
                if not levels:
                    return []
                
                # 按价格排序
                sorted_levels = sorted(levels, key=lambda x: x[1])
                merged = []
                current = sorted_levels[0]
                
                for i in range(1, len(sorted_levels)):
                    if abs(sorted_levels[i][1] - current[1]) / current[1] < threshold:
                        # 相近点，取平均
                        current = (
                            (current[0] + sorted_levels[i][0]) / 2, 
                            (current[1] + sorted_levels[i][1]) / 2
                        )
                    else:
                        merged.append(current)
                        current = sorted_levels[i]
                
                merged.append(current)
                return merged
            
            # 合并相近点
            local_highs = merge_levels(local_highs)
            local_lows = merge_levels(local_lows)
            
            # 按照与当前价格的距离排序
            highs_above = [(i, price) for i, price in local_highs if price > current_price]
            highs_above.sort(key=lambda x: x[1])
            
            lows_below = [(i, price) for i, price in local_lows if price < current_price]
            lows_below.sort(key=lambda x: x[1], reverse=True)
            
            # 选择最近的n_levels个阻力位和支撑位
            result['resistance'] = [price for _, price in highs_above[:n_levels]]
            result['support'] = [price for _, price in lows_below[:n_levels]]
            
            # 如果支撑位或阻力位不足，添加基于ATR的额外位置
            if len(result['resistance']) < n_levels:
                atr = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)[-1]
                additional_levels = n_levels - len(result['resistance'])
                for i in range(additional_levels):
                    # 添加基于ATR的阻力位
                    result['resistance'].append(current_price * (1 + 0.5 * (i + 1) * atr / current_price))
            
            if len(result['support']) < n_levels:
                atr = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)[-1]
                additional_levels = n_levels - len(result['support'])
                for i in range(additional_levels):
                    # 添加基于ATR的支撑位
                    result['support'].append(current_price * (1 - 0.5 * (i + 1) * atr / current_price))
            
            # 确保支撑和阻力位按照远近顺序排列
            result['resistance'].sort()
            result['support'].sort(reverse=True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"识别支撑阻力位时出错: {e}", exc_info=True)
            return result
    
    def _analyze_market_structure(self, df, indicators):
        """
        分析市场结构
        
        Args:
            df: 数据DataFrame
            indicators: 技术指标字典
            
        Returns:
            dict: 市场结构分析结果
        """
        result = {
            'structure': 'neutral',  # neutral, bullish, bearish
            'strength': 0,  # 0-100
            'description': ''
        }
        
        try:
            # 确保有足够的数据
            if len(df) < 20:
                self.logger.warning("数据量不足，无法分析市场结构")
                return result
            
            close = df['close'].values
            current_price = close[-1]
            
            # 分析价格相对于移动平均线的位置
            ma_count_above = 0
            ma_count_below = 0
            ma_total = 0
            
            for key, value in indicators.items():
                if key.startswith('ma_') and value is not None:
                    ma_total += 1
                    if current_price > value:
                        ma_count_above += 1
                    else:
                        ma_count_below += 1
            
            # 计算移动平均线趋势得分
            ma_score = 0
            if ma_total > 0:
                ma_score = (ma_count_above / ma_total) * 100
            
            # 分析RSI
            rsi_score = 0
            if 'rsi' in indicators and indicators['rsi'] is not None:
                rsi = indicators['rsi']
                if rsi > 70:
                    rsi_score = 90
                elif rsi > 60:
                    rsi_score = 70
                elif rsi > 50:
                    rsi_score = 60
                elif rsi > 40:
                    rsi_score = 40
                elif rsi > 30:
                    rsi_score = 30
                else:
                    rsi_score = 10
            
            # 分析MACD
            macd_score = 50
            if all(k in indicators for k in ['macd', 'macd_signal', 'macd_hist']):
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                macd_hist = indicators['macd_hist']
                
                if macd is not None and macd_signal is not None and macd_hist is not None:
                    if macd > macd_signal and macd_hist > 0:
                        macd_score = 80
                    elif macd > macd_signal and macd_hist < 0:
                        macd_score = 60
                    elif macd < macd_signal and macd_hist < 0:
                        macd_score = 20
                    else:
                        macd_score = 40
            
            # 分析布林带位置
            bb_score = 50
            if all(k in indicators for k in ['bb_upper', 'bb_middle', 'bb_lower']):
                bb_upper = indicators['bb_upper']
                bb_middle = indicators['bb_middle']
                bb_lower = indicators['bb_lower']
                
                if bb_upper is not None and bb_middle is not None and bb_lower is not None:
                    if current_price > bb_upper:
                        bb_score = 90
                    elif current_price > bb_middle:
                        bb_score = 70
                    elif current_price < bb_lower:
                        bb_score = 10
                    elif current_price < bb_middle:
                        bb_score = 30
                    else:
                        bb_score = 50
            
            # 组合所有得分
            strength = (ma_score * 0.4 + rsi_score * 0.2 + macd_score * 0.2 + bb_score * 0.2)
            
            # 确定市场结构
            if strength >= 70:
                structure = 'bullish'
                description = '看涨结构，价格站在大多数均线上方'
            elif strength <= 30:
                structure = 'bearish'
                description = '看跌结构，价格站在大多数均线下方'
            else:
                structure = 'neutral'
                description = '中性结构，价格在均线附近波动'
            
            # 返回结果
            result['structure'] = structure
            result['strength'] = strength
            result['description'] = description
            
            return result
            
        except Exception as e:
            self.logger.error(f"分析市场结构时出错: {e}", exc_info=True)
            return result
    
    def _analyze_sentiment(self, df, indicators):
        """
        分析市场情绪
        
        Args:
            df: 数据DataFrame
            indicators: 技术指标字典
            
        Returns:
            dict: 市场情绪分析结果
        """
        result = {
            'overall': 'neutral',  # bullish, bearish, neutral
            'long_short_ratio': 1.0,
            'state': 'normal',  # overbought, oversold, normal
            'funding_rate_impact': 'neutral'  # long_pay, short_pay, neutral
        }
        
        try:
            # 解析资金费率影响
            if 'funding_rate' in df and not df.empty:
                funding_rate = df['funding_rate'].iloc[-1]
                if funding_rate > 0.0001:  # 正费率，多单付费
                    result['funding_rate_impact'] = 'long_pay'
                elif funding_rate < -0.0001:  # 负费率，空单付费
                    result['funding_rate_impact'] = 'short_pay'
            
            # 分析技术指标情绪
            if 'rsi' in indicators and indicators['rsi'] is not None:
                rsi = indicators['rsi']
                if rsi > 70:
                    result['state'] = 'overbought'
                elif rsi < 30:
                    result['state'] = 'oversold'
            
            # 计算情绪得分
            sentiment_score = 50  # 默认中性
            
            # RSI贡献
            if 'rsi' in indicators and indicators['rsi'] is not None:
                rsi = indicators['rsi']
                sentiment_score += (rsi - 50) * 0.5  # RSI对情绪的贡献
            
            # MACD贡献
            if 'macd_hist' in indicators and indicators['macd_hist'] is not None:
                macd_hist = indicators['macd_hist']
                if macd_hist > 0:
                    sentiment_score += 10 * (min(1, macd_hist / 0.01))  # 正MACD直方图增加多头情绪
                else:
                    sentiment_score -= 10 * (min(1, abs(macd_hist) / 0.01))  # 负MACD直方图增加空头情绪
            
            # KDJ贡献
            if all(k in indicators for k in ['k', 'd']):
                k = indicators['k']
                d = indicators['d']
                if k is not None and d is not None:
                    if k > d:  # 金叉情况
                        sentiment_score += 5
                    elif k < d:  # 死叉情况
                        sentiment_score -= 5
                    
                    # 超买超卖
                    if k > 80:
                        sentiment_score += 5
                    elif k < 20:
                        sentiment_score -= 5
            
            # 根据资金费率调整情绪
            if 'funding_rate' in df and not df.empty:
                funding_rate = df['funding_rate'].iloc[-1]
                sentiment_score -= funding_rate * 1000  # 正费率降低多头情绪，负费率增加多头情绪
            
            # 确定多空比例 (根据情绪得分)
            ratio = 1.0
            if sentiment_score > 50:
                ratio = 1.0 + (sentiment_score - 50) / 10
            elif sentiment_score < 50:
                ratio = 1.0 / (1.0 + (50 - sentiment_score) / 10)
            
            result['long_short_ratio'] = round(ratio, 2)
            
            # 确定总体情绪
            if sentiment_score >= 70:
                result['overall'] = 'bullish'
            elif sentiment_score <= 30:
                result['overall'] = 'bearish'
            else:
                result['overall'] = 'neutral'
            
            return result
            
        except Exception as e:
            self.logger.error(f"分析市场情绪时出错: {e}", exc_info=True)
            return result
    
    def _determine_trend(self, df, indicators):
        """
        判断市场趋势
        
        Args:
            df: 数据DataFrame
            indicators: 技术指标字典
            
        Returns:
            dict: 趋势分析结果
        """
        result = {
            'direction': 'sideways',  # uptrend, downtrend, sideways
            'strength': 0,  # 0-100
            'description': ''
        }
        
        try:
            # 确保有足够的数据
            if len(df) < 20:
                self.logger.warning("数据量不足，无法判断趋势")
                return result
            
            close = df['close'].values
            current_price = close[-1]
            
            # 检查均线排列
            ma_aligned_up = True
            ma_aligned_down = True
            ma_values = []
            
            # 收集各周期均线值
            for period in [5, 10, 20, 50, 100]:
                key = f'ma_{period}'
                if key in indicators and indicators[key] is not None:
                    ma_values.append((period, indicators[key]))
            
            # 按周期排序
            ma_values.sort(key=lambda x: x[0])
            
            # 检查均线是否依次排列（多头排列或空头排列）
            if len(ma_values) >= 3:
                for i in range(len(ma_values) - 1):
                    if ma_values[i][1] > ma_values[i + 1][1]:
                        ma_aligned_up = False
                    if ma_values[i][1] < ma_values[i + 1][1]:
                        ma_aligned_down = False
            
            # 计算价格相对于远期均线的位置
            ma_50 = indicators.get('ma_50')
            ma_100 = indicators.get('ma_100')
            ma_200 = indicators.get('ma_200')
            
            above_ma50 = ma_50 is not None and current_price > ma_50
            above_ma100 = ma_100 is not None and current_price > ma_100
            above_ma200 = ma_200 is not None and current_price > ma_200
            
            # 计算ADX (趋势强度指标)
            adx = 0
            try:
                adx = talib.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)[-1]
            except:
                pass
            
            # 确定趋势方向和强度
            if ma_aligned_up and above_ma50 and above_ma100:
                direction = 'uptrend'
                strength = min(100, 50 + adx / 2)
                if adx > 25:
                    description = '强劲上升趋势，均线多头排列'
                else:
                    description = '温和上升趋势，均线多头排列'
            elif ma_aligned_down and not above_ma50 and not above_ma100:
                direction = 'downtrend'
                strength = min(100, 50 + adx / 2)
                if adx > 25:
                    description = '强劲下降趋势，均线空头排列'
                else:
                    description = '温和下降趋势，均线空头排列'
            else:
                direction = 'sideways'
                strength = max(0, adx - 15)
                description = '横盘整理，无明确趋势'
            
            # 返回结果
            result['direction'] = direction
            result['strength'] = strength
            result['description'] = description
            
            return result
            
        except Exception as e:
            self.logger.error(f"判断趋势时出错: {e}", exc_info=True)
            return result
    
    def _analyze_volatility(self, df):
        """
        分析市场波动率
        
        Args:
            df: 数据DataFrame
            
        Returns:
            dict: 波动率分析结果
        """
        result = {
            'current': 0,  # 当前波动率
            'average': 0,  # 平均波动率
            'state': 'normal',  # high, normal, low
            'description': ''
        }
        
        try:
            # 确保有足够的数据
            if len(df) < 20:
                self.logger.warning("数据量不足，无法分析波动率")
                return result
            
            # 计算日波动率 (基于收盘价的标准差)
            returns = df['close'].pct_change().dropna()
            current_volatility = returns.std() * np.sqrt(365)  # 年化波动率
            result['current'] = current_volatility
            
            # 计算平均波动率 (20日)
            avg_volatility = returns.rolling(window=20).std().mean() * np.sqrt(365)
            result['average'] = avg_volatility
            
            # 判断波动状态
            if current_volatility > avg_volatility * 1.5:
                result['state'] = 'high'
                result['description'] = '高波动性，市场剧烈震荡'
            elif current_volatility < avg_volatility * 0.5:
                result['state'] = 'low'
                result['description'] = '低波动性，市场平静'
            else:
                result['state'] = 'normal'
                result['description'] = '正常波动，市场稳定'
            
            return result
            
        except Exception as e:
            self.logger.error(f"分析波动率时出错: {e}", exc_info=True)
            return result