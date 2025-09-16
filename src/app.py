#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 主应用类

负责整个应用的生命周期管理，协调各个组件的交互
"""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
import sys
import threading
import time

# 导入UI组件
from ui.main_window import MainWindow
# 导入语言管理器
from src.language_manager import language_manager
# 导入数据层组件
from src.database_manager import DatabaseManager
from src.config_manager import ConfigManager
# 导入邮件功能组件
from src.email_manager import EmailManager
from src.message_parser import message_parser


class EChatApp:
    """E-Chat主应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.app_name = "E-Chat"
        self.version = "1.0.0"
        self.running = True
        
        # 设置CustomTkinter默认主题
        ctk.set_default_color_theme("blue")  # 蓝色主题
        # 外观主题将在配置加载后设置
        
        # 初始化主窗口
        self.main_window = None
        
        # 初始化各个管理器
        self.config_manager = None
        self.database_manager = None
        self.email_manager = None
        self.language_manager = language_manager
        
        print(f"🚀 {self.app_name} v{self.version} 正在启动...")
    
    def initialize_managers(self):
        """初始化各个管理器模块"""
        try:
            # 初始化配置管理器
            print("🔧 正在初始化配置管理器...")
            self.config_manager = ConfigManager()
            
            # 应用界面设置（主题、语言等）
            self.apply_ui_settings()
            
            # 初始化数据库管理器
            print("🗄️ 正在初始化数据库管理器...")
            self.database_manager = DatabaseManager()
            
            # 从数据库加载真实联系人数据（替代示例数据）
            self.load_real_contacts()
            
            # 初始化邮件管理器
            print("📬 正在初始化邮件管理器...")
            self.email_manager = EmailManager(self.config_manager, self.database_manager)
            
            # 设置邮件回调函数
            self.email_manager.set_callbacks(
                message_received=self.on_message_received,
                connection_status=self.on_connection_status_changed,
                error=self.on_email_error
            )
            
            print("📦 管理器模块初始化成功")
            
        except Exception as e:
            print(f"❌ 管理器初始化失败: {e}")
            return False
        
        return True
    
    def apply_ui_settings(self):
        """应用界面设置（启动时调用）"""
        try:
            print("🎨 正在应用界面设置...")
            
            # 获取UI配置
            ui_config = self.config_manager.get_ui_config()
            
            # 应用主题设置
            theme = ui_config.get('theme', 'dark')
            print(f"🎨 应用主题: {theme}")
            ctk.set_appearance_mode(theme)
            
            # 应用语言设置
            language = ui_config.get('language', 'zh')
            print(f"🌐 应用语言: {language}")
            language_manager.set_language(language)
            
            # 字体大小设置在主窗口创建时应用
            font_size = ui_config.get('font_size', 12)
            print(f"🔤 字体大小: {font_size}px")
            
            print("✅ 界面设置应用完成")
            
        except Exception as e:
            print(f"❌ 应用界面设置失败: {e}")
    
    def create_main_window(self):
        """创建主窗口"""
        try:
            self.main_window = MainWindow(self)
            print("🖼️ 主窗口创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 主窗口创建失败: {e}")
            return False
    
    def run(self):
        """运行应用"""
        try:
            # 初始化各个组件
            if not self.initialize_managers():
                print("❌ 应用初始化失败")
                return
            
            # 创建主窗口
            if not self.create_main_window():
                print("❌ 主窗口创建失败")
                return
            
            print("✅ E-Chat 启动成功！")
            
            # 启动邮件服务
            self.start_email_services()
            
            # 运行主循环
            self.main_window.mainloop()
            
        except KeyboardInterrupt:
            print("\n👋 用户中断，正在退出...")
            self.shutdown()
        except Exception as e:
            print(f"❌ 运行时错误: {e}")
            self.shutdown()
    
    def load_real_contacts(self):
        """从数据库加载真实联系人数据"""
        try:
            # 检查数据库中是否有联系人
            contacts = self.database_manager.get_contacts()
            
            if not contacts:
                print(f"📋 {language_manager.t('no_contacts_db')}")
            else:
                print(f"📋 从数据库加载了 {len(contacts)} 个联系人")
                
        except Exception as e:
            print(f"❌ 加载联系人数据失败: {e}")
    
    def start_email_services(self):
        """启动邮件服务"""
        try:
            if self.email_manager:
                # 检查邮件配置
                email_config = self.config_manager.get_email_config()
                if email_config['username'] and email_config['password']:
                    # 启动邮件轮询
                    self.email_manager.start_polling()
                    # 启动发送线程
                    self.email_manager.start_send_thread()
                    print("✅ 邮件服务已启动")
                else:
                    print("⚠️ 邮件配置不完整，请先配置邮箱")
        except Exception as e:
            print(f"❌ 启动邮件服务失败: {e}")
    
    def stop_email_services(self):
        """停止邮件服务"""
        try:
            if self.email_manager:
                self.email_manager.stop_polling()
                self.email_manager.stop_send_thread()
                print("✅ 邮件服务已停止")
        except Exception as e:
            print(f"❌ 停止邮件服务失败: {e}")
    
    # ==================== 邮件回调函数 ====================
    
    def on_message_received(self, message: dict):
        """收到新消息时的回调"""
        try:
            sender_email = message.get('sender', 'Unknown')
            print(f"📬 收到新消息: {sender_email}")
            
            # 通知UI更新
            if self.main_window and hasattr(self.main_window, 'chat_list'):
                # 获取消息内容摘要
                content = message.get('content', {})
                text_content = content.get('text', '')
                message_summary = text_content[:30] + "..." if len(text_content) > 30 else text_content
                
                # 清理发送者邮箱地址（移除显示名称）
                if '<' in sender_email and '>' in sender_email:
                    clean_sender_email = sender_email.split('<')[1].split('>')[0]
                else:
                    clean_sender_email = sender_email
                
                # 智能更新联系人列表 - 只更新相关联系人
                success = self.main_window.chat_list.update_contact_message(
                    email=clean_sender_email,
                    last_message=message_summary,
                    unread_count=1  # 新消息未读计数
                )
                
                if not success:
                    print("⚠️ 联系人更新失败，可能是新联系人")
                
                # 如果当前正在和发送者聊天，直接添加新消息而不重新加载历史
                current_contact = self.main_window.chat_interface.get_current_contact()
                if current_contact and current_contact.get('email') == clean_sender_email:
                    # 创建UI消息对象
                    from datetime import datetime
                    import time
                    
                    ui_message = {
                        "id": message.get('id', f"received_{int(time.time() * 1000)}"),
                        "sender": clean_sender_email,
                        "content": text_content,
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "is_sent": False
                    }
                    
                    # 直接添加新消息而不重新加载整个历史
                    self.main_window.after(0, lambda: self.main_window.chat_interface.add_new_message(ui_message))
                    print(f"✅ 已添加新消息到当前聊天: {text_content[:30]}...")
            
        except Exception as e:
            print(f"❌ 处理收到消息回调失败: {e}")
    
    def on_connection_status_changed(self, connection_type: str, status: bool):
        """连接状态变化时的回调"""
        try:
            status_text = "连接成功" if status else "连接断开"
            print(f"🔗 {connection_type.upper()} {status_text}")
            
            # 通知UI更新连接状态
            if self.main_window and hasattr(self.main_window, 'sidebar'):
                if status:
                    self.main_window.sidebar.update_status_indicator("online")
                else:
                    self.main_window.sidebar.update_status_indicator("offline")
            
        except Exception as e:
            print(f"❌ 处理连接状态回调失败: {e}")
    
    def on_email_error(self, error_type: str, error_message: str):
        """邮件错误时的回调"""
        try:
            print(f"❌ 邮件错误 ({error_type}): {error_message}")
            
            # 通知UI显示错误状态
            if self.main_window and hasattr(self.main_window, 'sidebar'):
                self.main_window.sidebar.update_status_indicator("error")
            
        except Exception as e:
            print(f"❌ 处理邮件错误回调失败: {e}")
    
    def send_message(self, recipient: str, content: str):
        """发送消息的公共接口"""
        try:
            if self.email_manager:
                success = self.email_manager.send_message_async(recipient, content)
                if success:
                    print(f"📤 消息已发送: {recipient}")
                return success
            else:
                print("❌ 邮件管理器未初始化")
                return False
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False
    
    def shutdown(self):
        """关闭应用"""
        print("🔄 正在关闭 E-Chat...")
        
        self.running = False
        
        # 关闭各个管理器
        try:
            # 停止邮件服务
            self.stop_email_services()
            
            if self.email_manager:
                self.email_manager.cleanup()
            
            if self.database_manager:
                self.database_manager.close()
            
            if self.config_manager:
                # 保存配置
                self.config_manager.save_config()
            
        except Exception as e:
            print(f"⚠️ 关闭管理器时出现错误: {e}")
        
        # 关闭主窗口
        if self.main_window:
            try:
                self.main_window.destroy()
            except:
                pass
        
        print("👋 E-Chat 已关闭")
    
    def get_app_info(self):
        """获取应用信息"""
        return {
            "name": self.app_name,
            "version": self.version,
            "running": self.running
        } 