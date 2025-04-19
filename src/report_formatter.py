#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
报告格式化模块

负责将分析结果和交易信号格式化为可读性强的文本报告。
"""

import time
from datetime import datetime
import logging
from utils.logger import get_logger
from utils.helpers import format_price, format_percentage

class ReportFormatter:
    """
    报告格式化器类
    
    将分析结果和交易信号转换为格式化的文本报告。
    """
    
    def __init__(self):
        """
        初始化报告格式化器
        """
        self.logger = get_logger('report_formatter')
        self.logger.info("报告格式化器初始化完成")
    
    def format(self, symbol, timeframe, market_data, analysis_result, signal, config):
        """
        格式化分析报告
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            market_data: 市场数据DataFrame
            analysis_result: 市场分析结果字典
            signal: 交易信号字典
            config: 配置字典
            
        Returns:
            str: 格式化后的报告文本
        """
        try:
            if market_data is None or market_data.empty:
                self.logger.warning(f"无法格式化报告: {symbol} {timeframe} 的市场数据为空")
                return "无法生成报告: 数据不足"
            
            if analysis_result is None:
                self.logger.warning(f"无法格式化报告: {symbol} {timeframe} 的分析结果为空")
                return "无法生成报告: 分析结果为空"
            
            if signal is None:
                self.logger.warning(f"无法格式化报告: {symbol} {timeframe} 的交易信号为空")
                return "无法生成报告: 无交易信号"
            
            # 获取当前价格
            current_price = analysis_result.get('last_price')
            if current_price is None and not market_data.empty:
                current_price = market_data['close'].iloc[-1]
            
            # 获取趋势方向
            trend_direction = analysis_result.get('trend', {}).get('direction', 'sideways')
            trend_emoji = "📈" if trend_direction == "uptrend" else "📉" if trend_direction == "downtrend" else "➡️"
            
            # 获取1小时涨跌幅
            change_percent = 0
            if not market_data.empty and len(market_data) > 1:
                previous_close = market_data['close'].iloc[-2]
                change_percent = ((current_price - previous_close) / previous_close) * 100
            
            # 获取资金费率
            funding_rate = 0
            if 'funding_rate' in market_data and not market_data.empty:
                funding_rate = market_data['funding_rate'].iloc[-1]
            
            # 构建报告标题
            report_title = self._get_report_title(timeframe, trend_direction)
            
            # 构建主报告
            report = [
                report_title,
                "",
                f"💰 当前价格: ${format_price(current_price)}",
                f"{trend_emoji} {timeframe}涨跌: {change_percent:.2f}%",
                f"🔵 资金费率: {funding_rate:.6f}% ({self._get_funding_rate_description(funding_rate)})",
                f"🌡️ 市场情绪：{self._get_sentiment_description(analysis_result)}",
                f"• 多空比例：{self._get_long_short_ratio(analysis_result)}",
                f"• 市场状态：{self._get_market_state(analysis_result)}",
                "",
                "📍 关键价位：",
                self._format_key_levels(current_price, analysis_result),
                "",
                "📊 技术分析：",
                self._format_technical_analysis(analysis_result),
                "",
                "💫 其他数据：",
                self._format_additional_data(market_data),
                "",
                f"【信号强度】{self._get_signal_strength_stars(signal)}",
                f"• 信号可信度: {signal.get('signal_strength', {}).get('reliability', '一般可靠')}",
                f"• 建议交易时机: {signal.get('signal_strength', {}).get('timing', '等待确认')}",
                "",
                "📈 交易建议："
            ]
            
            # 添加交易建议
            trade_advice = self._format_trade_advice(signal)
            report.extend(trade_advice)
            
            # 添加风险管理
            risk_management = self._format_risk_management(signal)
            report.extend(risk_management)
            
            # 添加更新时间和数据来源
            now = datetime.now()
            report.extend([
                "",
                f"⏰ 更新时间: {now.strftime('%m/%d/%Y, %I:%M:%S %p')}",
                f"📈 数据来源: {config['exchanges'].get('exchange_name', list(config['exchanges'].keys())[0])} ({timeframe}周期)",
                "机器人版本：v1.0.0"
            ])
            
            # 合并成最终报告
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"格式化报告时出错: {e}", exc_info=True)
            return f"格式化报告时出错: {e}"
    
    def _get_report_title(self, timeframe, trend_direction):
        """获取报告标题"""
        timeframe_map = {
            '1m': '1分钟',
            '5m': '5分钟',
            '15m': '15分钟',
            '30m': '30分钟',
            '1h': '1小时',
            '4h': '4小时',
            '1d': '日线',
            '1w': '周线'
        }
        
        # 转换时间周期显示
        display_timeframe = timeframe_map.get(timeframe, timeframe)
        
        # 趋势方向显示
        if trend_direction == 'uptrend':
            direction_text = "[上涨]"
        elif trend_direction == 'downtrend':
            direction_text = "[下跌]"
        else:
            direction_text = "[震荡]"
        
        return f" {display_timeframe}行情分析 {direction_text}"
    
    def _get_funding_rate_description(self, funding_rate):
        """获取资金费率描述"""
        if funding_rate > 0.0001:
            return "正向，多单支付费用"
        elif funding_rate < -0.0001:
            return "负向，空单支付费用"
        else:
            return "中性，费用极低"
    
    def _get_sentiment_description(self, analysis_result):
        """获取市场情绪描述"""
        sentiment = analysis_result.get('sentiment', {})
        overall = sentiment.get('overall', 'neutral')
        
        if overall == 'bullish':
            return "看涨"
        elif overall == 'bearish':
            return "看跌"
        else:
            return "中性"
    
    def _get_long_short_ratio(self, analysis_result):
        """获取多空比例"""
        sentiment = analysis_result.get('sentiment', {})
        ratio = sentiment.get('long_short_ratio', 1.0)
        
        if ratio > 1:
            return f"{ratio:.1f}:1"
        elif ratio < 1:
            return f"1:{(1/ratio):.1f}"
        else:
            return "1:1"
    
    def _get_market_state(self, analysis_result):
        """获取市场状态"""
        sentiment = analysis_result.get('sentiment', {})
        state = sentiment.get('state', 'normal')
        
        if state == 'overbought':
            return "超买状态"
        elif state == 'oversold':
            return "超卖状态"
        else:
            return "正常波动"
    
    def _format_key_levels(self, current_price, analysis_result):
        """格式化关键价位"""
        support_resistance = analysis_result.get('support_resistance', {})
        resistances = support_resistance.get('resistance', [])
        supports = support_resistance.get('support', [])
        
        lines = []
        
        # 添加阻力位
        if resistances and len(resistances) >= 2:
            lines.append(f"• 强阻力位：${format_price(resistances[1])}")
        if resistances and len(resistances) >= 1:
            lines.append(f"• 弱阻力位：${format_price(resistances[0])}")
        
        # 添加当前价格
        lines.append(f"• 当前价格：${format_price(current_price)} ⬅️")
        
        # 添加支撑位
        if supports and len(supports) >= 1:
            lines.append(f"• 弱支撑位：${format_price(supports[0])}")
        if supports and len(supports) >= 2:
            lines.append(f"• 强支撑位：${format_price(supports[1])}")
        
        return "\n".join(lines)
    
    def _format_technical_analysis(self, analysis_result):
        """格式化技术分析"""
        indicators = analysis_result.get('indicators', {})
        trend = analysis_result.get('trend', {})
        
        lines = ["【趋势研判】"]
        
        # 均线分析
        ma_20 = indicators.get('ma_20')
        ma_50 = indicators.get('ma_50')
        if ma_20 is not None and ma_50 is not None:
            lines.append(f"• 均线系统：MA{format_price(ma_20)}和MA{format_price(ma_50)}"
                         f"{'上方' if analysis_result.get('last_price', 0) > ma_20 else '下方'}，"
                         f"{'短期和中期趋势向上' if analysis_result.get('last_price', 0) > ma_20 and analysis_result.get('last_price', 0) > ma_50 else '短期和中期趋势向下' if analysis_result.get('last_price', 0) < ma_20 and analysis_result.get('last_price', 0) < ma_50 else '趋势分歧'}")
        
        # 布林带分析
        bb_upper = indicators.get('bb_upper')
        bb_middle = indicators.get('bb_middle')
        bb_lower = indicators.get('bb_lower')
        bb_width = indicators.get('bb_width')
        
        if all(x is not None for x in [bb_upper, bb_middle, bb_lower, bb_width]):
            current_price = analysis_result.get('last_price', 0)
            if current_price > bb_upper:
                bb_position = "上轨上方，超买状态"
            elif current_price > bb_middle:
                bb_position = "中轨上方，偏强运行"
            elif current_price < bb_lower:
                bb_position = "下轨下方，超卖状态"
            else:
                bb_position = "中轨下方，偏弱运行"
            
            lines.append(f"• 布林通道：{bb_position}，通道宽度{bb_width*100:.2f}%")
        
        lines.append("【技术指标】")
        
        # RSI分析
        rsi = indicators.get('rsi')
        if rsi is not None:
            if rsi > 70:
                rsi_desc = "处于超买区域，短期可能回调"
            elif rsi > 60:
                rsi_desc = "处于中性偏多区域，短期偏强"
            elif rsi > 40:
                rsi_desc = "处于中性区域，无明显偏向"
            elif rsi > 30:
                rsi_desc = "处于中性偏空区域，短期偏弱"
            else:
                rsi_desc = "处于超卖区域，短期可能反弹"
            
            lines.append(f"• RSI({rsi:.2f})：{rsi_desc}")
        
        # KDJ分析
        k = indicators.get('k')
        d = indicators.get('d')
        j = indicators.get('j')
        
        if all(x is not None for x in [k, d, j]):
            if k > d:
                kdj_desc = "金叉形成，显示上涨动能"
            else:
                kdj_desc = "死叉形成，显示下跌动能"
            
            lines.append(f"• KDJ：{kdj_desc}，K值{k:.2f}，D值{d:.2f}")
        
        # MACD分析
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        macd_hist = indicators.get('macd_hist')
        
        if all(x is not None for x in [macd, macd_signal, macd_hist]):
            if macd > macd_signal:
                if macd_hist > indicators.get('macd_hist_1', 0):
                    macd_desc = "柱状图扩大，上涨动能增强"
                else:
                    macd_desc = "柱状图收窄，上涨动能减弱"
            else:
                if macd_hist < indicators.get('macd_hist_1', 0):
                    macd_desc = "柱状图扩大，下跌动能增强"
                else:
                    macd_desc = "柱状图收窄，下跌动能减弱"
            
            lines.append(f"• MACD：{macd_desc}")
        
        return "\n".join(lines)
    
    def _format_additional_data(self, market_data):
        """格式化额外数据"""
        if market_data is None or market_data.empty:
            return "数据不足"
        
        # 获取最大行数
        max_rows = len(market_data)
        
        # 获取24小时数据
        high_24h = market_data['high'].max()
        low_24h = market_data['low'].min()
        volume_24h = market_data['volume'].sum()
        
        # 获取最近一小时数据
        if max_rows >= 2:
            high_1h = market_data['high'].iloc[-1]
            low_1h = market_data['low'].iloc[-1]
            volume_1h = market_data['volume'].iloc[-1]
        else:
            high_1h = low_1h = volume_1h = None
        
        lines = []
        lines.append(f"• 24h最高: ${format_price(high_24h)}")
        lines.append(f"• 24h最低: ${format_price(low_24h)}")
        lines.append(f"• 24h成交量: {volume_24h:,.2f} {market_data['symbol'].iloc[0].split('/')[0]}")
        
        if all(x is not None for x in [high_1h, low_1h, volume_1h]):
            lines.append(f"• 1小时最高: ${format_price(high_1h)}")
            lines.append(f"• 1小时最低: ${format_price(low_1h)}")
            lines.append(f"• 1小时成交量: {volume_1h:,.2f} {market_data['symbol'].iloc[0].split('/')[0]}")
        
        return "\n".join(lines)
    
    def _get_signal_strength_stars(self, signal):
        """获取信号强度星级"""
        stars = signal.get('signal_strength', {}).get('stars', 3)
        return "⭐" * stars + "️️️⭐️" * (5 - stars) + f" ({stars}/5)"
    
    def _format_trade_advice(self, signal):
        """格式化交易建议"""
        direction = signal.get('direction', 'neutral')
        entry_price = signal.get('entry_price')
        stop_loss = signal.get('stop_loss')
        target_price = signal.get('target_price')
        
        lines = []
        
        if direction == 'long':
            lines.append("【操作方向】做多")
        elif direction == 'short':
            lines.append("【操作方向】做空")
        else:
            lines.append("【操作方向】观望")
            return lines
        
        # 计算风险和收益百分比
        risk_percent = abs(entry_price - stop_loss) / entry_price * 100
        reward_percent = abs(target_price - entry_price) / entry_price * 100
        
        lines.append(f"• 建议{direction=='long'and'做多'or'做空'}点位: ${format_price(entry_price)}")
        lines.append(f"• 止损位: ${format_price(stop_loss)} ({risk_percent:.2f}%)")
        lines.append(f"• 目标位: ${format_price(target_price)} ({reward_percent:.2f}%)")
        
        return lines
    
    def _format_risk_management(self, signal):
        """格式化风险管理建议"""
        risk_params = signal.get('risk_params', {})
        
        lines = ["", "⚠️ 风险管理："]
        
        # 建议杠杆
        leverage = risk_params.get('suggested_leverage', 5)
        volatility = risk_params.get('volatility', 3.0)
        lines.append(f"• 建议杠杆: {leverage}倍 "
                     f"({'高' if leverage >= 10 else '中' if leverage >= 5 else '低'}杠杆，"
                     f"{'高' if volatility >= 5 else '中' if volatility >= 2 else '低'}波动行情)")
        
        # 建议仓位
        position_size = risk_params.get('position_size_percent', 20.0)
        lines.append(f"• 建议仓位: {position_size:.1f}% "
                     f"({'激进' if position_size >= 30 else '适中' if position_size >= 10 else '保守'}仓位)")
        
        # 预期收益率
        reward_percent = risk_params.get('reward_percent', 4.0)
        lines.append(f"• 预期收益率: {reward_percent:.2f}%")
        
        # 最大回撤
        risk_percent = risk_params.get('risk_percent', 2.0)
        lines.append(f"• 最大回撤: {risk_percent:.2f}%")
        
        # 风险回报比
        risk_reward_ratio = risk_params.get('risk_reward_ratio', 2.0)
        lines.append(f"• 风险回报比: {risk_reward_ratio:.2f} "
                     f"({'优秀' if risk_reward_ratio >= 3 else '良好' if risk_reward_ratio >= 2 else '一般' if risk_reward_ratio >= 1.5 else '较差'})")
        
        # 市场波动性
        lines.append(f"• 市场波动性: {volatility:.2f}% "
                     f"({'高' if volatility >= 5 else '中' if volatility >= 2 else '低'}波动)")
        
        return lines