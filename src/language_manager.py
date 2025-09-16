#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 语言管理模块

支持中英文双语言切换
"""

import json
from typing import Dict, Any
from pathlib import Path


class LanguageManager:
    """语言管理器"""
    
    def __init__(self):
        """初始化语言管理器"""
        self.current_language = "en"  # 默认英文
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """加载翻译数据"""
        # 内置翻译数据
        self.translations = {
            "en": {
                # 应用基本信息
                "app_title": "E-Chat - Email Instant Messaging",
                "version": "Version",
                
                # 主窗口
                "select_contact_to_start": "Select a contact to start chatting",
                
                # 侧边栏
                "settings": "Settings",
                "add_contact": "Add Contact", 
                "theme": "Theme",
                "notifications": "Notifications",
                "help": "Help",
                "online": "Online",
                "offline": "Offline",
                "connecting": "Connecting",
                "error": "Error",
                
                # 聊天列表
                "search_contacts": "Search contacts...",
                "yesteay": "Yesterday",
                "monday": "Monday",
                
                # 聊天界面
                "welcome_title": "Welcome to E-Chat",
                "welcome_desc": "Select a contact on the left to start chatting\nor click ➕ to add a new contact",
                "please_select_contact": "Please select a contact first...",
                "no_contacts": "No contacts\nClick ➕ to add a contact and start chatting",
                "send": "Send",
                "attach_file": "Attach File",
                "emoji_picker": "Emoji Picker",
                "more_options": "More Options",
                
                # 帮助对话框
                "help_title": "Help",
                "help_content": """E-Chat Email Instant Messaging

Shortcuts:
• Ctrl+Q / Ctrl+W: Exit application
• Enter: Send message
• Ctrl+Enter: New line

Features:
• ⚙️ Settings: Configure email and app settings
• ➕ Add Contact: Add new chat contacts
• 🌙/☀️ Theme: Switch dark/light theme
• 🔔 Notifications: Configure message notifications

Version: 1.0.0""",
                "close": "Close",
                
                # 状态和消息
                "status_online": "Online",
                "status_offline": "Offline",
                "message_sent": "Message sent to",
                "contact_selected": "Selected contact",
                "search": "Search",
                "theme_switched": "Theme switched to",
                "no_contacts_db": "No contacts in database, please use the ➕ button to add contacts and start chatting",
                "no_contacts_please_add": "No contacts, please click the ➕ button to add contacts",
                
                # 自动回复
                "auto_replies": [
                    "Got it, thanks!",
                    "Thanks for your message.",
                    "Will reply later.",
                    "Processing...",
                    "👍"
                ],
                
                # 设置相关
                "language": "Language",
                "chinese": "中文",
                "english": "English",
                
                # 设置窗口
                "settings_title": "Settings",
                "email_settings": "Email Settings",
                "ui_settings": "Interface Settings",
                "app_settings": "Application Settings",
                "send_settings": "Send Settings",
                "receive_settings": "Receive Settings",
                "account_settings": "Account Settings",
                "smtp_server": "SMTP Server",
                "smtp_port": "SMTP Port",
                "imap_server": "IMAP Server",
                "imap_port": "IMAP Port",
                "email_address": "Email Address",
                "password": "Password",
                "password_saved_placeholder": "Password saved (leave empty to keep current)",
                "test_connection": "Test Connection",
                "theme_settings": "Theme Settings",
                "theme_info_text": "Theme can be switched using the moon/sun button in the sidebar. Current theme will be remembered on next startup.",
                "language_settings": "Language Settings",
                "font_settings": "Font Settings",
                "font_size": "Font Size",
                "startup_settings": "Startup Settings",
                "auto_start": "Start with system",
                "notification_settings": "Notification Settings",
                "enable_notifications": "Enable notifications",
                "enable_sound": "Enable sound",
                "polling_settings": "Email Polling Settings",
                "polling_interval": "Polling Interval",
                "seconds": "seconds",
                
                # IDLE推送设置
                "enable_idle_push": "Enable IMAP IDLE Real-time Push (Recommended)",
                "test_idle_support": "Test IDLE",
                "idle_mode_info": "IDLE mode enables second-level push, recommend 15-minute backup polling",
                "polling_interval_label": "Polling Interval:",
                "smart_mode": "Smart Mode (Recommended)",
                "manual_mode": "Manual Mode",
                "interval_time_seconds": "Interval Time (seconds):",
                "smart_mode_info_idle": "Smart Mode: 15 minutes when IDLE available, 30 seconds when unavailable",
                "smart_mode_info_no_idle": "Smart Mode: 30 seconds polling when IDLE not used",
                "testing_idle": "Testing...",
                "idle_test_pending": "Please click to test IDLE support",
                "idle_supported": "Server supports IDLE, real-time push enabled",
                "idle_not_supported": "Server does not support IDLE",
                "idle_test_success_title": "IDLE Test Successful",
                "idle_test_success_message": "🎉 Your email server supports IMAP IDLE!\n\n✅ Real-time push mode has been automatically enabled\n⏰ Polling interval adjusted to 15-minute backup mode\n🚀 You will now experience second-level email push!",
                "idle_not_supported_title": "IDLE Not Supported",
                "idle_not_supported_message": "⚠️ Your email server does not support IMAP IDLE\n\n🔄 Recommend using 30-second polling for better real-time performance\n💡 Consider switching to an email provider that supports IDLE",
                "idle_test_failed": "IDLE support test failed",
                "complete_email_config_first": "Please complete email configuration first",
                
                # 时间单位
                "minutes": "minutes",
                "minute": "minute",
                "cancel": "Cancel",
                "apply": "Apply",
                "ok": "OK",
                "success": "Success",
                "error": "Error",
                "testing": "Testing",
                "testing_connection": "Testing connection...",
                "connection_success": "Connection successful",
                "connection_failed": "Connection failed",
                "settings_valid": "Settings are valid",
                "invalid_settings": "Invalid settings",
                "incomplete_settings": "Please fill in all required fields",
                "incomplete_email_config": "Email configuration is incomplete. Please fill in all fields (SMTP/IMAP servers, email address, and password) to enable email functionality.",
                "settings_applied": "Settings have been applied successfully",
                "save_failed": "Failed to save settings",
                
                # 添加联系人窗口
                "add_contact_title": "Add Contact",
                "add_new_contact": "Add New Contact",
                "nickname": "Nickname",
                "note": "Note",
                "optional": "optional",
                "email_placeholder": "Enter email address...",
                "nickname_placeholder": "Enter nickname...",
                "suggest_nickname": "Suggest",
                "clear": "Clear",
                "warning": "Warning",
                "enter_email_first": "Please enter an email address first",
                "enter_nickname_first": "Please enter a nickname",
                "invalid_email_format": "Invalid email format",
                "contact_exists": "Contact exists",
                "email_format_valid": "Email format is valid",
                "email_format_invalid": "Email format is invalid",
                "contact_already_exists": "Contact already exists",
                "email_available": "Email is available",
                "nickname_required": "Nickname is required",
                "contact_added_successfully": "Contact added successfully",
                "add_contact_failed": "Failed to add contact",
                "database_error": "Database error",
                
                # 联系人示例
                "sample_contacts": {
                    "alice": {
                        "nickname": "Alice Smith",
                        "last_message": "Hello! How are you doing?",
                        "time": "10:30"
                    },
                    "bob": {
                        "nickname": "Bob Johnson", 
                        "last_message": "Is the meeting material ready for tomorrow?",
                        "time": "Yesterday"
                    },
                    "carol": {
                        "nickname": "Carol Wilson",
                        "last_message": "How's the research project going?",
                        "time": "Monday"
                    }
                },
                
                # 示例聊天记录
                "sample_messages": {
                    "received1": "Hello! How are you doing?",
                    "sent1": "Pretty good, been busy with work. How about you?",
                    "received2": "Same here, lots of projects lately. Want to hang out this weekend?"
                },
                "send_settings_desc": "Configure outgoing email server settings",
                "receive_settings_desc": "Configure incoming email server settings", 
                "account_settings_desc": "Configure your email account information",
            },
            
            "zh": {
                # 应用基本信息
                "app_title": "E-Chat - 邮件即时通讯",
                "version": "版本",
                
                # 主窗口
                "select_contact_to_start": "选择一个联系人开始聊天",
                
                # 侧边栏
                "settings": "设置",
                "add_contact": "添加联系人",
                "theme": "主题",
                "notifications": "通知",
                "help": "帮助",
                "online": "在线",
                "offline": "离线",
                "connecting": "连接中",
                "error": "错误",
                
                # 聊天列表
                "search_contacts": "搜索联系人...",
                "yesterday": "昨天",
                "monday": "周一",
                
                # 聊天界面
                "welcome_title": "欢迎使用 E-Chat",
                "welcome_desc": "选择左侧的联系人开始聊天\n或点击 ➕ 添加新的联系人",
                "please_select_contact": "请先选择一个联系人...",
                "no_contacts": "暂无联系人\n点击 ➕ 添加联系人开始聊天",
                "send": "发送",
                "attach_file": "附件",
                "emoji_picker": "表情",
                "more_options": "更多选项",
                
                # 帮助对话框
                "help_title": "帮助",
                "help_content": """E-Chat 邮件即时通讯软件

快捷键：
• Ctrl+Q / Ctrl+W: 退出应用
• Enter: 发送消息
• Ctrl+Enter: 换行

功能说明：
• ⚙️ 设置: 配置邮箱和应用设置
• ➕ 添加联系人: 添加新的聊天联系人
• 🌙/☀️ 主题: 切换深色/浅色主题
• 🔔 通知: 配置消息通知设置

版本: 1.0.0""",
                "close": "关闭",
                
                # 状态和消息
                "status_online": "在线",
                "status_offline": "离线", 
                "message_sent": "消息已发送给",
                "contact_selected": "选择联系人",
                "search": "搜索",
                "theme_switched": "主题已切换为",
                "no_contacts_db": "数据库中暂无联系人，请通过 ➕ 按钮添加联系人开始聊天",
                "no_contacts_please_add": "暂无联系人，请点击 ➕ 按钮添加联系人",
                
                # 自动回复
                "auto_replies": [
                    "好的，我知道了！",
                    "谢谢你的消息。",
                    "稍后回复你。",
                    "收到，正在处理中...",
                    "👍"
                ],
                
                # 设置相关
                "language": "语言",
                "chinese": "中文",
                "english": "English",
                
                # 设置窗口
                "settings_title": "设置",
                "email_settings": "邮箱设置",
                "ui_settings": "界面设置",
                "app_settings": "应用设置",
                "send_settings": "发送设置",
                "receive_settings": "接收设置",
                "account_settings": "账户设置",
                "smtp_server": "SMTP 服务器",
                "smtp_port": "SMTP 端口",
                "imap_server": "IMAP 服务器",
                "imap_port": "IMAP 端口",
                "email_address": "邮箱地址",
                "password": "密码",
                "password_saved_placeholder": "密码已保存（留空则保持当前密码）",
                "test_connection": "测试连接",
                "theme_settings": "主题设置",
                "theme_info_text": "主题可以通过侧边栏的月亮/太阳按钮切换。当前主题会在下次启动时自动恢复。",
                "language_settings": "语言设置",
                "font_settings": "字体设置",
                "font_size": "字体大小",
                "startup_settings": "启动设置",
                "auto_start": "开机自启动",
                "notification_settings": "通知设置",
                "enable_notifications": "启用通知",
                "enable_sound": "启用声音",
                "polling_settings": "邮件轮询设置",
                "polling_interval": "轮询间隔",
                "seconds": "秒",
                
                # IDLE推送设置
                "enable_idle_push": "启用IMAP IDLE实时推送 (推荐)",
                "test_idle_support": "测试IDLE",
                "idle_mode_info": "IDLE模式可实现秒级推送，建议同时设置15分钟备用轮询",
                "polling_interval_label": "轮询间隔:",
                "smart_mode": "智能模式 (推荐)",
                "manual_mode": "手动设置",
                "interval_time_seconds": "间隔时间 (秒):",
                "smart_mode_info_idle": "智能模式: IDLE可用时15分钟，不可用时30秒",
                "smart_mode_info_no_idle": "智能模式: 不使用IDLE时30秒轮询",
                "testing_idle": "测试中...",
                "idle_test_pending": "请点击测试IDLE支持",
                "idle_supported": "服务器支持IDLE，已启用实时推送",
                "idle_not_supported": "服务器不支持IDLE",
                "idle_test_success_title": "IDLE测试成功",
                "idle_test_success_message": "🎉 您的邮箱服务器支持IMAP IDLE！\n\n✅ 已自动启用实时推送模式\n⏰ 轮询间隔已调整为15分钟备用模式\n🚀 现在您将获得秒级的邮件推送体验！",
                "idle_not_supported_title": "IDLE不支持",
                "idle_not_supported_message": "⚠️ 您的邮箱服务器不支持IMAP IDLE功能\n\n🔄 建议使用30秒轮询间隔获得较好的实时性\n💡 您可以考虑更换支持IDLE的邮箱服务商",
                "idle_test_failed": "IDLE支持测试失败",
                "complete_email_config_first": "请先完整配置邮箱信息",
                
                # 时间单位
                "minutes": "分钟",
                "minute": "分钟",
                "cancel": "取消",
                "apply": "应用",
                "ok": "确定",
                "success": "成功",
                "error": "错误",
                "testing": "测试中",
                "testing_connection": "正在测试连接...",
                "connection_success": "连接成功",
                "connection_failed": "连接失败",
                "settings_valid": "设置有效",
                "invalid_settings": "设置无效",
                "incomplete_settings": "请填写所有必填字段",
                "incomplete_email_config": "邮箱配置不完整。请填写所有字段（SMTP/IMAP服务器、邮箱地址和密码）以启用邮件功能。",
                "settings_applied": "设置已成功应用",
                "save_failed": "保存设置失败",
                
                # 添加联系人窗口
                "add_contact_title": "添加联系人",
                "add_new_contact": "添加新联系人",
                "nickname": "昵称",
                "note": "备注",
                "optional": "可选",
                "email_placeholder": "请输入邮箱地址...",
                "nickname_placeholder": "请输入昵称...",
                "suggest_nickname": "建议",
                "clear": "清空",
                "warning": "警告",
                "enter_email_first": "请先输入邮箱地址",
                "enter_nickname_first": "请输入昵称",
                "invalid_email_format": "邮箱格式无效",
                "contact_exists": "联系人已存在",
                "email_format_valid": "邮箱格式正确",
                "email_format_invalid": "邮箱格式错误",
                "contact_already_exists": "联系人已存在",
                "email_available": "邮箱可用",
                "nickname_required": "昵称不能为空",
                "contact_added_successfully": "联系人添加成功",
                "add_contact_failed": "添加联系人失败",
                "database_error": "数据库错误",
                
                # 联系人示例
                "sample_contacts": {
                    "alice": {
                        "nickname": "Alice Smith",
                        "last_message": "你好！最近怎么样？",
                        "time": "10:30"
                    },
                    "bob": {
                        "nickname": "Bob Johnson",
                        "last_message": "明天会议的资料准备好了吗？",
                        "time": "昨天"
                    },
                    "carol": {
                        "nickname": "Carol Wilson", 
                        "last_message": "研究项目进展如何？",
                        "time": "周一"
                    }
                },
                
                # 示例聊天记录
                "sample_messages": {
                    "received1": "你好！最近怎么样？",
                    "sent1": "还不错，工作挺忙的。你呢？",
                    "received2": "我也是，最近项目比较多。周末有空一起出来聊聊？"
                },
                "send_settings_desc": "配置邮件发送服务器设置",
                "receive_settings_desc": "配置邮件接收服务器设置", 
                "account_settings_desc": "配置邮箱账户信息"
            }
        }
    
    def set_language(self, language_code: str):
        """设置当前语言"""
        if language_code in self.translations:
            self.current_language = language_code
            print(f"🌐 语言切换为: {language_code}")
            return True
        return False
    
    def get_language(self) -> str:
        """获取当前语言"""
        return self.current_language
    
    def t(self, key: str, default: str = None) -> str:
        """翻译文本"""
        try:
            # 支持嵌套键，如 "sample_contacts.alice.nickname"
            keys = key.split('.')
            value = self.translations[self.current_language]
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            return key  # 如果找不到翻译，返回原键
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表"""
        return {
            "en": self.t("english"),
            "zh": self.t("chinese")
        }
    
    def get_sample_contacts(self) -> list:
        """获取示例联系人数据"""
        contacts_data = self.t("sample_contacts")
        
        return [
            {
                "email": "alice@example.com",
                "nickname": contacts_data["alice"]["nickname"],
                "last_message": contacts_data["alice"]["last_message"],
                "last_time": contacts_data["alice"]["time"],
                "unread_count": 2,
                "online": True
            },
            {
                "email": "bob@company.com",
                "nickname": contacts_data["bob"]["nickname"],
                "last_message": contacts_data["bob"]["last_message"],
                "last_time": contacts_data["bob"]["time"],
                "unread_count": 0,
                "online": False
            },
            {
                "email": "carol@university.edu",
                "nickname": contacts_data["carol"]["nickname"],
                "last_message": contacts_data["carol"]["last_message"],
                "last_time": contacts_data["carol"]["time"],
                "unread_count": 1,
                "online": True
            }
        ]
    
    def get_sample_messages(self, contact_email: str) -> list:
        """获取示例聊天记录 - 根据不同联系人生成不同的对话内容"""
        
        # 根据不同联系人生成不同的对话内容
        if contact_email == "alice@example.com":
            if self.current_language == "zh":
                return [
                    {
                        "sender": contact_email,
                        "content": "你好！最近怎么样？",
                        "timestamp": "10:25",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "还不错，工作挺忙的。你呢？",
                        "timestamp": "10:28", 
                        "is_sent": True
                    },
                    {
                        "sender": contact_email,
                        "content": "我也是，最近项目比较多。周末有空一起出来聊聊？",
                        "timestamp": "10:30",
                        "is_sent": False
                    }
                ]
            else:
                return [
                    {
                        "sender": contact_email,
                        "content": "Hello! How are you doing?",
                        "timestamp": "10:25",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "Pretty good, been busy with work. How about you?",
                        "timestamp": "10:28", 
                        "is_sent": True
                    },
                    {
                        "sender": contact_email,
                        "content": "Same here, lots of projects lately. Want to hang out this weekend?",
                        "timestamp": "10:30",
                        "is_sent": False
                    }
                ]
        
        elif contact_email == "bob@company.com":
            if self.current_language == "zh":
                return [
                    {
                        "sender": contact_email,
                        "content": "明天会议的资料准备好了吗？",
                        "timestamp": "昨天 14:20",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "已经准备好了，会在会议前发给大家。",
                        "timestamp": "昨天 14:25", 
                        "is_sent": True
                    },
                    {
                        "sender": contact_email,
                        "content": "太好了，那我们明天见！",
                        "timestamp": "昨天 14:30",
                        "is_sent": False
                    }
                ]
            else:
                return [
                    {
                        "sender": contact_email,
                        "content": "Is the meeting material ready for tomorrow?",
                        "timestamp": "Yesterday 14:20",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "Yes, it's ready. I'll send it to everyone before the meeting.",
                        "timestamp": "Yesterday 14:25", 
                        "is_sent": True
                    },
                    {
                        "sender": contact_email,
                        "content": "Great! See you tomorrow then!",
                        "timestamp": "Yesterday 14:30",
                        "is_sent": False
                    }
                ]
        
        elif contact_email == "carol@university.edu":
            if self.current_language == "zh":
                return [
                    {
                        "sender": contact_email,
                        "content": "研究项目进展如何？",
                        "timestamp": "周一 09:15",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "进展顺利，已经完成了第一阶段的实验。",
                        "timestamp": "周一 09:20", 
                        "is_sent": True
                    },
                    {
                        "sender": contact_email,
                        "content": "太棒了！能分享一下初步结果吗？",
                        "timestamp": "周一 09:25",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "当然可以，我整理一下数据发给你。",
                        "timestamp": "周一 09:30", 
                        "is_sent": True
                    }
                ]
            else:
                return [
                    {
                        "sender": contact_email,
                        "content": "How's the research project going?",
                        "timestamp": "Monday 09:15",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "Going well! We've completed the first phase of experiments.",
                        "timestamp": "Monday 09:20", 
                        "is_sent": True
                    },
                    {
                        "sender": contact_email,
                        "content": "That's wonderful! Could you share some preliminary results?",
                        "timestamp": "Monday 09:25",
                        "is_sent": False
                    },
                    {
                        "sender": "me@example.com",
                        "content": "Of course! Let me organize the data and send it to you.",
                        "timestamp": "Monday 09:30", 
                        "is_sent": True
                    }
                ]
        
        else:
            # 默认消息（用于新联系人）
            messages_data = self.t("sample_messages")
            return [
                {
                    "sender": contact_email,
                    "content": messages_data["received1"],
                    "timestamp": "10:25",
                    "is_sent": False
                },
                {
                    "sender": "me@example.com",
                    "content": messages_data["sent1"],
                    "timestamp": "10:28", 
                    "is_sent": True
                },
                {
                    "sender": contact_email,
                    "content": messages_data["received2"],
                    "timestamp": "10:30",
                    "is_sent": False
                }
            ]


# 全局语言管理器实例
language_manager = LanguageManager() 