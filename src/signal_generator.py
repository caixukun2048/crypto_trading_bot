#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
信号生成模块

负责根据市场分析结果生成交易信号和具体的交易建议。
"""

import numpy as np
import pandas as pd
import logging
from utils.logger import get_logger

class SignalGenerator:
    """
    信号生成器类
    
    根据市场分析结果生成交易信号，包括交易方向、入场点位、止损位、目标位等。
    """
    
    def __init__(self, params):
        """
        初始化信号生成器
        
        Args:
            params: 信号生成参数字典
        """
        self.logger = get_logger('signal_generator')
        self.params = params
        self.logger.info("信号生成器初始化完成")
    
    def generate_signal(self, analysis_result):
        """
        生成交易信号
        
        Args:
            analysis_result: 市场分析结果字典
            
        Returns:
            dict: 交易信号字典
        """
        if analysis_result is None:
            self.logger.warning("分析结果为空，无法生成信号")
            return None
        
        try:
            # 提取必要的分析结果
            indicators = analysis_result.get('indicators', {})
            support_resistance = analysis_result.get('support_resistance', {})
            market_structure = analysis_result.get('market_structure', {})
            sentiment = analysis_result.get('sentiment', {})
            trend = analysis_result.get('trend', {})
            volatility = analysis_result.get('volatility', {})
            
            # 获取当前价格
            current_price = analysis_result.get('last_price')
            if current_price is None:
                self.logger.warning("当前价格为空，无法生成信号")
                return None
            
            # 计算综合得分
            score = self._calculate_score(analysis_result)
            
            # 确定交易方向
            direction = self._determine_direction(score, analysis_result)
            
            # 确定入场点位
            entry_price = self._determine_entry_price(direction, current_price, analysis_result)
            
            # 确定止损位
            stop_loss = self._determine_stop_loss(direction, entry_price, analysis_result)
            
            # 确定目标位
            target_price = self._determine_target_price(direction, entry_price, stop_loss, analysis_result)
            
            # 计算风险参数
            risk_params = self._calculate_risk_parameters(entry_price, stop_loss, target_price, direction, analysis_result)
            
            # 评估信号强度
            signal_strength = self._evaluate_signal_strength(score, analysis_result)
            
            # 构建交易信号
            signal = {
                'symbol': analysis_result.get('symbol'),
                'timeframe': analysis_result.get('timeframe'),
                'direction': direction,
                'score': score,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_params': risk_params,
                'signal_strength': signal_strength,
                'timestamp': pd.Timestamp.now()
            }
            
            self.logger.info(f"生成交易信号: {signal['symbol']} {signal['timeframe']} {signal['direction']} "
                            f"入场: {signal['entry_price']:.2f} 止损: {signal['stop_loss']:.2f} "
                            f"目标: {signal['target_price']:.2f} 强度: {signal['signal_strength']['stars']}/5")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"生成交易信号时出错: {e}", exc_info=True)
            return None
    
    def _calculate_score(self, analysis_result):
        """
        计算综合得分
        
        Args:
            analysis_result: 市场分析结果字典
            
        Returns:
            float: 综合得分 (0-100)
        """
        try:
            # 提取各部分分析结果
            market_structure = analysis_result.get('market_structure', {})
            sentiment = analysis_result.get('sentiment', {})
            trend = analysis_result.get('trend', {})
            indicators = analysis_result.get('indicators', {})
            
            # 获取权重参数
            weights = self.params.get('weights', {
                'trend': 0.3,
                'oscillators': 0.3,
                'volume': 0.2,
                'sentiment': 0.2
            })
            
            # 趋势得分 (0-100)
            trend_score = 0
            if trend.get('direction') == 'uptrend':
                trend_score = min(100, 50 + trend.get('strength', 0))
            elif trend.get('direction') == 'downtrend':
                trend_score = max(0, 50 - trend.get('strength', 0))
            else:
                trend_score = 50  # 横盘
            
            # 震荡指标得分 (0-100)
            oscillator_score = 50  # 默认中性
            
            # RSI贡献
            rsi = indicators.get('rsi')
            if rsi is not None:
                if rsi > 70:
                    oscillator_score += 20
                elif rsi > 60:
                    oscillator_score += 10
                elif rsi < 30:
                    oscillator_score -= 20
                elif rsi < 40:
                    oscillator_score -= 10
            
            # MACD贡献
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            macd_hist = indicators.get('macd_hist')
            
            if macd is not None and macd_signal is not None and macd_hist is not None:
                if macd > macd_signal and macd_hist > 0:
                    oscillator_score += 15
                elif macd > macd_signal and macd_hist < 0:
                    oscillator_score += 5
                elif macd < macd_signal and macd_hist < 0:
                    oscillator_score -= 15
                elif macd < macd_signal and macd_hist > 0:
                    oscillator_score -= 5
            
            # 限制在0-100范围内
            oscillator_score = max(0, min(100, oscillator_score))
            
            # 成交量得分 (0-100)
            volume_score = 50  # 默认中性
            
            # 市场情绪得分 (0-100)
            sentiment_score = 50  # 默认中性
            
            if sentiment.get('overall') == 'bullish':
                sentiment_score = 75
            elif sentiment.get('overall') == 'bearish':
                sentiment_score = 25
            
            # 根据资金费率调整
            if sentiment.get('funding_rate_impact') == 'long_pay':
                sentiment_score -= 10
            elif sentiment.get('funding_rate_impact') == 'short_pay':
                sentiment_score += 10
            
            # 根据市场状态调整
            if sentiment.get('state') == 'overbought':
                sentiment_score = max(30, sentiment_score - 20)
            elif sentiment.get('state') == 'oversold':
                sentiment_score = min(70, sentiment_score + 20)
            
            # 限制在0-100范围内
            sentiment_score = max(0, min(100, sentiment_score))
            
            # 计算最终得分
            final_score = (
                trend_score * weights['trend'] +
                oscillator_score * weights['oscillators'] +
                volume_score * weights['volume'] +
                sentiment_score * weights['sentiment']
            )
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"计算综合得分时出错: {e}", exc_info=True)
            return 50  # 出错时返回中性得分
    
    def _determine_direction(self, score, analysis_result):
        """
        确定交易方向
        
        Args:
            score: 综合得分
            analysis_result: 市场分析结果字典
            
        Returns:
            str: 交易方向 ('long', 'short', 'neutral')
        """
        try:
            # 获取阈值参数
            thresholds = self.params.get('thresholds', {
                'strong_buy': 80,
                'buy': 60,
                'neutral': 40,
                'sell': 20,
                'strong_sell': 0
            })
            
            # 根据得分确定初始方向
            if score >= thresholds['buy']:
                direction = 'long'
            elif score <= thresholds['sell']:
                direction = 'short'
            else:
                direction = 'neutral'
            
            # 考虑其他因素进行调整
            current_price = analysis_result.get('last_price')
            
            return direction
            
        except Exception as e:
            self.logger.error(f"确定交易方向时出错: {e}", exc_info=True)
            return 'neutral'  # 出错时返回中性
    
    def _determine_entry_price(self, direction, current_price, analysis_result):
        """
        确定入场点位
        
        Args:
            direction: 交易方向
            current_price: 当前价格
            analysis_result: 市场分析结果字典
            
        Returns:
            float: 入场价格
        """
        try:
            # 直接使用当前价格作为入场价格
            return current_price
            
        except Exception as e:
            self.logger.error(f"确定入场点位时出错: {e}", exc_info=True)
            return current_price  # 出错时返回当前价格
    
    def _determine_stop_loss(self, direction, entry_price, analysis_result):
        """
        确定止损位置
        
        Args:
            direction: 交易方向
            entry_price: 入场价格
            analysis_result: 市场分析结果字典
            
        Returns:
            float: 止损价格
        """
        try:
            # 提取必要的分析结果
            support_resistance = analysis_result.get('support_resistance', {})
            volatility = analysis_result.get('volatility', {})
            indicators = analysis_result.get('indicators', {})
            
            # 获取支撑位和阻力位
            supports = support_resistance.get('support', [])
            resistances = support_resistance.get('resistance', [])
            
            # 获取ATR值
            atr = indicators.get('atr', 0)
            if atr == 0 or atr is None:
                # 如果没有ATR值，使用价格的一定百分比
                atr = entry_price * 0.01  # 默认使用1%
            
            if direction == 'long':
                # 做多止损: 使用最近的支撑位，或者入场价减去ATR的倍数
                if supports and len(supports) > 0:
                    nearest_support = max([s for s in supports if s < entry_price], default=entry_price * 0.98)
                    # 确保止损位不要太近
                    if (entry_price - nearest_support) / entry_price < 0.01:
                        stop_loss = entry_price * 0.98  # 至少2%的止损
                    else:
                        stop_loss = nearest_support
                else:
                    # 没有支撑位时，使用ATR的2倍作为止损距离
                    stop_loss = entry_price - (2 * atr)
            
            elif direction == 'short':
                # 做空止损: 使用最近的阻力位，或者入场价加上ATR的倍数
                if resistances and len(resistances) > 0:
                    nearest_resistance = min([r for r in resistances if r > entry_price], default=entry_price * 1.02)
                    # 确保止损位不要太近
                    if (nearest_resistance - entry_price) / entry_price < 0.01:
                        stop_loss = entry_price * 1.02  # 至少2%的止损
                    else:
                        stop_loss = nearest_resistance
                else:
                    # 没有阻力位时，使用ATR的2倍作为止损距离
                    stop_loss = entry_price + (2 * atr)
            
            else:  # neutral
                stop_loss = entry_price  # 中性不设止损
            
            return stop_loss
            
        except Exception as e:
            self.logger.error(f"确定止损位置时出错: {e}", exc_info=True)
            # 出错时使用默认止损 (2%)
            if direction == 'long':
                return entry_price * 0.98
            elif direction == 'short':
                return entry_price * 1.02
            else:
                return entry_price
    
    def _determine_target_price(self, direction, entry_price, stop_loss, analysis_result):
        """
        确定目标价格
        
        Args:
            direction: 交易方向
            entry_price: 入场价格
            stop_loss: 止损价格
            analysis_result: 市场分析结果字典
            
        Returns:
            float: 目标价格
        """
        try:
            # 提取必要的分析结果
            support_resistance = analysis_result.get('support_resistance', {})
            
            # 获取支撑位和阻力位
            supports = support_resistance.get('support', [])
            resistances = support_resistance.get('resistance', [])
            
            # 计算止损距离
            stop_distance = abs(entry_price - stop_loss)
            
            # 初始化风险回报比
            risk_reward = 2.0  # 默认风险回报比为2
            
            if direction == 'long':
                # 做多目标: 使用风险回报比或最近的阻力位
                target_by_risk = entry_price + (risk_reward * stop_distance)
                
                if resistances and len(resistances) > 0:
                    next_resistance = min([r for r in resistances if r > entry_price], default=target_by_risk)
                    # 选择更近的那个
                    target_price = min(target_by_risk, next_resistance)
                else:
                    target_price = target_by_risk
            
            elif direction == 'short':
                # 做空目标: 使用风险回报比或最近的支撑位
                target_by_risk = entry_price - (risk_reward * stop_distance)
                
                if supports and len(supports) > 0:
                    next_support = max([s for s in supports if s < entry_price], default=target_by_risk)
                    # 选择更近的那个
                    target_price = max(target_by_risk, next_support)
                else:
                    target_price = target_by_risk
            
            else:  # neutral
                target_price = entry_price  # 中性不设目标价
            
            return target_price
            
        except Exception as e:
            self.logger.error(f"确定目标价格时出错: {e}", exc_info=True)
            # 出错时使用默认目标 (风险回报比2)
            stop_distance = abs(entry_price - stop_loss)
            if direction == 'long':
                return entry_price + (2 * stop_distance)
            elif direction == 'short':
                return entry_price - (2 * stop_distance)
            else:
                return entry_price
    
    def _calculate_risk_parameters(self, entry_price, stop_loss, target_price, direction, analysis_result):
        """
        计算风险管理参数
        
        Args:
            entry_price: 入场价格
            stop_loss: 止损价格
            target_price: 目标价格
            direction: 交易方向
            analysis_result: 市场分析结果字典
            
        Returns:
            dict: 风险管理参数字典
        """
        try:
            # 提取必要的分析结果
            volatility = analysis_result.get('volatility', {})
            
            # 计算风险和收益
            risk_percent = abs(entry_price - stop_loss) / entry_price
            reward_percent = abs(target_price - entry_price) / entry_price
            
            # 计算风险回报比
            risk_reward_ratio = reward_percent / risk_percent if risk_percent > 0 else 0
            
            # 建议杠杆倍数 (根据波动率和风险百分比)
            current_volatility = volatility.get('current', 0.01)
            if current_volatility < 0.01:
                current_volatility = 0.01  # 避免除以零
            
            # 根据市场波动情况确定基础杠杆
            if current_volatility < 0.02:  # 低波动
                base_leverage = 10
            elif current_volatility < 0.05:  # 中等波动
                base_leverage = 5
            else:  # 高波动
                base_leverage = 3
            
            # 根据风险调整杠杆
            adjusted_leverage = min(base_leverage, 0.5 / risk_percent) if risk_percent > 0 else base_leverage
            
            # 确保杠杆不超过最大值
            max_leverage = 20  # 最大杠杆倍数
            suggested_leverage = min(int(adjusted_leverage), max_leverage)
            
            # 建议仓位大小 (基于风险和杠杆)
            position_size_percent = min(0.1 * risk_reward_ratio, 0.3)  # 最大30%仓位
            
            # 构建风险参数
            risk_params = {
                'risk_percent': risk_percent * 100,  # 百分比形式
                'reward_percent': reward_percent * 100,  # 百分比形式
                'risk_reward_ratio': risk_reward_ratio,
                'suggested_leverage': suggested_leverage,
                'position_size_percent': position_size_percent * 100,  # 百分比形式
                'volatility': current_volatility * 100  # 百分比形式
            }
            
            return risk_params
            
        except Exception as e:
            self.logger.error(f"计算风险参数时出错: {e}", exc_info=True)
            # 出错时返回默认风险参数
            return {
                'risk_percent': 2.0,
                'reward_percent': 4.0,
                'risk_reward_ratio': 2.0,
                'suggested_leverage': 5,
                'position_size_percent': 20.0,
                'volatility': 3.0
            }
    
    def _evaluate_signal_strength(self, score, analysis_result):
        """
        评估信号强度
        
        Args:
            score: 综合得分
            analysis_result: 市场分析结果字典
            
        Returns:
            dict: 信号强度评估结果
        """
        try:
            # 获取阈值参数
            thresholds = self.params.get('thresholds', {
                'strong_buy': 80,
                'buy': 60,
                'neutral': 40,
                'sell': 20,
                'strong_sell': 0
            })
            
            # 计算星级 (1-5星)
            if score >= thresholds['strong_buy'] or score <= thresholds['strong_sell']:
                stars = 5  # 强烈信号
            elif score >= thresholds['buy'] or score <= thresholds['sell']:
                stars = 4  # 明确信号
            elif score >= 55 or score <= 45:
                stars = 3  # 中等信号
            elif score >= 52 or score <= 48:
                stars = 2  # 弱信号
            else:
                stars = 1  # 极弱信号
            
            # 信号可信度
            if stars >= 4:
                reliability = '高度可靠'
            elif stars >= 3:
                reliability = '较为可靠'
            elif stars >= 2:
                reliability = '一般可靠'
            else:
                reliability = '参考为主'
            
            # 交易时机
            if stars >= 4:
                timing = '建议进场'
            elif stars >= 3:
                timing = '可以考虑'
            elif stars >= 2:
                timing = '等待确认'
            else:
                timing = '暂不操作'
            
            # 返回信号强度评估结果
            return {
                'stars': stars,
                'reliability': reliability,
                'timing': timing
            }
            
        except Exception as e:
            self.logger.error(f"评估信号强度时出错: {e}", exc_info=True)
            # 出错时返回默认评估
            return {
                'stars': 3,
                'reliability': '一般可靠',
                'timing': '等待确认'
            }