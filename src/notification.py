#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通知模块

负责将分析报告和交易信号通过各种渠道（如Telegram）发送给用户。
"""

import logging
import requests
import json
from utils.logger import get_logger

class TelegramNotifier:
    """
    Telegram通知类
    
    通过Telegram机器人API发送消息。
    """
    
    def __init__(self, config):
        """
        初始化Telegram通知器
        
        Args:
            config: Telegram配置字典，包含token和chat_id
        """
        self.logger = get_logger('telegram_notifier')
        self.token = config.get('token')
        self.chat_id = config.get('chat_id')
        self.enabled = config.get('enabled', False)
        
        if not self.token or not self.chat_id:
            self.logger.warning("Telegram配置不完整，无法发送通知")
            self.enabled = False
        
        if self.enabled:
            self.logger.info("Telegram通知器初始化完成")
        else:
            self.logger.info("Telegram通知器已禁用")
    
    def send_message(self, message):
        """
        发送消息
        
        Args:
            message: 要发送的消息文本
            
        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            self.logger.debug("Telegram通知器已禁用，跳过发送")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info("消息发送成功")
                return True
            else:
                self.logger.error(f"发送消息失败: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送消息时出错: {e}", exc_info=True)
            return False

class ConsoleNotifier:
    """
    控制台通知类
    
    将消息输出到控制台。
    """
    
    def __init__(self):
        """
        初始化控制台通知器
        """
        self.logger = get_logger('console_notifier')
        self.logger.info("控制台通知器初始化完成")
    
    def send_message(self, message):
        """
        发送消息到控制台
        
        Args:
            message: 要发送的消息文本
            
        Returns:
            bool: 是否发送成功
        """
        try:
            print("\n" + "="*80)
            print(message)
            print("="*80 + "\n")
            return True
            
        except Exception as e:
            self.logger.error(f"输出消息时出错: {e}", exc_info=True)
            return False

class FileNotifier:
    """
    文件通知类
    
    将消息保存到文件。
    """
    
    def __init__(self, filename="signals.log"):
        """
        初始化文件通知器
        
        Args:
            filename: 输出文件名
        """
        self.logger = get_logger('file_notifier')
        self.filename = filename
        self.logger.info(f"文件通知器初始化完成，输出文件: {filename}")
    
    def send_message(self, message):
        """
        将消息保存到文件
        
        Args:
            message: 要保存的消息文本
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*80 + "\n")
                f.write(message)
                f.write("\n" + "="*80 + "\n")
            
            self.logger.info(f"消息已保存到文件: {self.filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存消息到文件时出错: {e}", exc_info=True)
            return False