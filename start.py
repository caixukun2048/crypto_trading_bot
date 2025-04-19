#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
虚拟货币合约分析交易系统
版本: v1.0.0

此脚本为主启动文件，用于初始化并运行合约分析系统。
"""

import os
import sys
import time
import yaml
import logging
import argparse
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from src.data_collector import DataCollector
from src.market_analyzer import MarketAnalyzer
from src.signal_generator import SignalGenerator
from src.report_formatter import ReportFormatter
from src.notification import TelegramNotifier
from utils.logger import setup_logger

def load_config(config_path):
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        dict: 配置参数字典
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='加密货币合约分析交易系统')
    parser.add_argument('-c', '--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('-s', '--symbol', help='指定交易对，例如 BTC/USDT')
    parser.add_argument('-t', '--timeframe', help='指定时间周期，例如 1h, 4h, 1d')
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger('crypto_bot', log_level)
    logger.info("启动加密货币合约分析系统...")
    
    # 加载配置
    try:
        config = load_config(args.config)
        logger.info(f"成功加载配置文件: {args.config}")
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return
    
    # 初始化组件
    try:
        # 数据采集器
        data_collector = DataCollector(
            exchanges=config['exchanges'],
            symbols=config['symbols'] if not args.symbol else [args.symbol],
            timeframes=config['timeframes'] if not args.timeframe else [args.timeframe]
        )
        
        # 市场分析器
        market_analyzer = MarketAnalyzer(config['analysis_params'])
        
        # 信号生成器
        signal_generator = SignalGenerator(config['signal_params'])
        
        # 报告格式化器
        report_formatter = ReportFormatter()
        
        # 通知模块
        if config['telegram']['enabled']:
            notifier = TelegramNotifier(config['telegram'])
        else:
            notifier = None
        
        logger.info("所有组件初始化完成")
    except Exception as e:
        logger.error(f"初始化组件失败: {e}")
        return
    
    # 运行分析流程
    try:
        logger.info("开始执行分析流程")
        
        # 采集市场数据
        market_data = data_collector.collect_data()
        logger.info(f"成功采集数据: {len(market_data)} 个交易对")
        
        # 遍历所有交易对和时间周期
        for symbol in data_collector.symbols:
            for timeframe in data_collector.timeframes:
                
                logger.info(f"分析 {symbol} 的 {timeframe} 周期数据")
                
                # 获取该交易对的数据
                symbol_data = market_data.get((symbol, timeframe))
                if symbol_data is None:
                    logger.warning(f"未找到 {symbol} 的 {timeframe} 周期数据")
                    continue
                
                # 进行市场分析
                analysis_result = market_analyzer.analyze(symbol_data, symbol, timeframe)
                
                # 生成交易信号
                signal = signal_generator.generate_signal(analysis_result)
                
                # 格式化报告
                report = report_formatter.format(
                    symbol=symbol,
                    timeframe=timeframe,
                    market_data=symbol_data,
                    analysis_result=analysis_result,
                    signal=signal,
                    config=config
                )
                
                # 输出报告
                print("\n" + "="*80)
                print(report)
                print("="*80 + "\n")
                
                # 发送通知
                if notifier:
                    notifier.send_message(report)
                
                # 短暂暂停，避免API请求过于频繁
                time.sleep(1)
                
        logger.info("分析流程执行完成")
        
    except Exception as e:
        logger.error(f"执行分析流程时出错: {e}", exc_info=True)
    
    logger.info("系统运行结束")

if __name__ == "__main__":
    main()