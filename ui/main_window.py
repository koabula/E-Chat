#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 主窗口界面

实现三栏布局：侧边栏 + 联系人列表 + 聊天界面
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional

# 导入UI组件
from ui.sidebar import Sidebar
from ui.chat_list import ChatList
from ui.chat_interface import ChatInterface
# 导入语言管理器和主题配置
from src.language_manager import language_manager
from ui.theme_config import theme, get_color, get_font


class MainWindow(ctk.CTk):
    """主窗口类"""
    
    def __init__(self, app):
        """初始化主窗口"""
        super().__init__()
        
        self.app = app  # 保存应用实例引用
        self.child_windows = []  # 跟踪子窗口实例
        
        # 窗口基本设置
        self.setup_window()
        
        # 创建主要布局
        self.create_layout()
        
        # 绑定事件
        self.bind_events()
        
        print("🖼️ 主窗口初始化完成")
    
    def setup_window(self):
        """设置窗口基本属性"""
        # 窗口标题和图标
        self.title(language_manager.t("app_title"))
        
        # 从配置读取窗口大小和位置
        try:
            ui_config = self.app.config_manager.get_ui_config()
            window_size = ui_config.get('window_size', '1200x800')
            window_position = ui_config.get('window_position', 'center')
            
            # 解析窗口大小
            if 'x' in window_size:
                window_width, window_height = map(int, window_size.split('x'))
            else:
                window_width, window_height = 1200, 800
            
            # 计算窗口位置
            if window_position == 'center':
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                center_x = int(screen_width/2 - window_width/2)
                center_y = int(screen_height/2 - window_height/2)
                self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            else:
                # 使用保存的位置
                self.geometry(f"{window_width}x{window_height}")
        except Exception as e:
            print(f"❌ 读取窗口配置失败，使用默认值: {e}")
            # 使用默认值
            window_width, window_height = 1200, 800
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)
            self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # 设置最小窗口大小
        self.minsize(800, 600)
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_layout(self):
        """创建现代化主要布局"""
        # 设置现代化背景色
        self.configure(fg_color=get_color("gray_50"))
        
        # 配置网格权重
        self.grid_columnconfigure(0, weight=0)  # 侧边栏，固定宽度
        self.grid_columnconfigure(1, weight=0)  # 联系人列表，固定宽度
        self.grid_columnconfigure(2, weight=1)  # 聊天界面，自适应
        self.grid_rowconfigure(0, weight=1)
        
        # 创建现代化侧边栏
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        
        # 创建现代化联系人列表
        self.chat_list = ChatList(self)
        self.chat_list.grid(row=0, column=1, sticky="nsew", padx=(0, 1))
        
        # 创建现代化聊天界面
        self.chat_interface = ChatInterface(self)
        self.chat_interface.grid(row=0, column=2, sticky="nsew")
        
        print("📐 现代化主窗口布局创建完成")
    
    def bind_events(self):
        """绑定窗口事件"""
        # 窗口大小改变事件
        self.bind("<Configure>", self.on_window_resize)
        
        # 键盘快捷键
        self.bind_all("<Control-q>", lambda e: self.on_closing())
        self.bind_all("<Control-w>", lambda e: self.on_closing())
        
        print("⌨️ 窗口事件绑定完成")
    
    def on_window_resize(self, event):
        """窗口大小改变事件处理"""
        if event.widget == self:
            # 可以在这里处理窗口大小改变的逻辑
            pass
    
    def on_closing(self):
        """窗口关闭事件处理"""
        print("🔄 正在关闭主窗口...")
        
        # 保存窗口大小和位置
        self.save_window_state()
        
        # 通知应用程序关闭
        if self.app:
            self.app.shutdown()
        else:
            self.destroy()
    
    def save_window_state(self):
        """保存窗口状态"""
        try:
            # 获取当前窗口几何信息
            geometry = self.geometry()
            
            # 解析几何信息：widthxheight+x+y
            if '+' in geometry or '-' in geometry:
                # 分离尺寸和位置
                if '+' in geometry:
                    size_part, pos_part = geometry.split('+', 1)
                    window_size = size_part
                elif '-' in geometry:
                    size_part, pos_part = geometry.split('-', 1)
                    window_size = size_part
                else:
                    window_size = geometry
            else:
                window_size = geometry
            
            # 保存窗口配置
            self.app.config_manager.set_ui_config(
                window_size=window_size,
                window_position='saved'
            )
            self.app.config_manager.save_config()
            
            print(f"💾 窗口状态已保存: {window_size}")
            
        except Exception as e:
            print(f"❌ 保存窗口状态失败: {e}")
    
    def switch_to_settings(self):
        """切换到设置界面"""
        try:
            from ui.settings_window import SettingsWindow
            settings_window = SettingsWindow(self, self.app)
            
            # 添加到子窗口跟踪列表
            self.child_windows.append(settings_window)
            
            # 设置窗口关闭时从列表中移除
            def on_settings_close():
                if settings_window in self.child_windows:
                    self.child_windows.remove(settings_window)
                settings_window.destroy()
            
            settings_window.protocol("WM_DELETE_WINDOW", on_settings_close)
            
            print("⚙️ 设置窗口已打开")
        except Exception as e:
            print(f"❌ 打开设置窗口失败: {e}")
    
    def show_add_contact_dialog(self):
        """显示添加联系人对话框"""
        try:
            from ui.add_contact_window import AddContactWindow
            
            def on_contact_added(contact):
                """添加联系人成功后的回调"""
                # 刷新联系人列表
                if hasattr(self, 'chat_list') and self.chat_list:
                    self.chat_list.add_contact(contact)
                print(f"✅ 新联系人已添加: {contact['nickname']} ({contact['email']})")
            
            add_contact_window = AddContactWindow(self, self.app, on_contact_added)
            print("➕ 添加联系人窗口已打开")
        except Exception as e:
            print(f"❌ 打开添加联系人窗口失败: {e}")
    
    def update_theme(self, theme: str):
        """更新应用主题"""
        try:
            ctk.set_appearance_mode(theme)
            print(f"🎨 {language_manager.t('theme_switched')}: {theme}")
            
            # 递归更新所有组件的颜色
            self.refresh_all_components()
            
            # 通知各个组件更新主题（如果它们有update_theme方法）
            if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'update_theme'):
                self.sidebar.update_theme(theme)
                
            if hasattr(self, 'chat_list') and hasattr(self.chat_list, 'update_theme'):
                self.chat_list.update_theme(theme)
            
            if hasattr(self, 'chat_interface') and hasattr(self.chat_interface, 'update_theme'):
                self.chat_interface.update_theme(theme)
            
            # 通知所有子窗口更新主题
            self.update_child_windows_theme(theme)
            
            # 强制刷新界面
            self.update_idletasks()
            self.update()
            
            print(f"✅ 主题更新完成: {theme}")
            
        except Exception as e:
            print(f"❌ 主题切换失败: {e}")
    
    def refresh_all_components(self):
        """递归刷新所有组件的主题"""
        try:
            # 强制更新主窗口主题
            if hasattr(self, '_apply_appearance_mode'):
                self._apply_appearance_mode(ctk.get_appearance_mode())
            
            # 递归更新所有子组件
            self._refresh_widget_recursively(self)
            
            # 额外等待一下让CustomTkinter完成主题应用
            self.after(100, self._delayed_refresh)
            
        except Exception as e:
            print(f"❌ 刷新组件失败: {e}")
    
    def _delayed_refresh(self):
        """延迟刷新，确保主题完全应用"""
        try:
            self.update_idletasks()
        except:
            pass
    
    def _refresh_widget_recursively(self, widget):
        """递归刷新widget及其子组件"""
        try:
            # 强制所有CustomTkinter组件应用新主题
            if hasattr(widget, '_apply_appearance_mode'):
                try:
                    widget._apply_appearance_mode(ctk.get_appearance_mode())
                except:
                    pass
            
            # 特殊处理不同类型的组件
            if isinstance(widget, ctk.CTkFrame):
                # 框架组件 - 检查是否有特定的颜色设置需求
                if hasattr(widget, 'configure'):
                    try:
                        # 不强制设置颜色，让CustomTkinter自动处理
                        pass
                    except:
                        pass
                        
            elif isinstance(widget, ctk.CTkLabel):
                # 标签组件 - 确保文本颜色正确
                try:
                    # 让CustomTkinter自动处理，不手动设置颜色
                    pass
                except:
                    pass
                    
            elif isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                # 输入框组件 - 让CustomTkinter自动处理
                try:
                    pass
                except:
                    pass
                    
            elif isinstance(widget, ctk.CTkButton):
                # 按钮组件 - 让CustomTkinter自动处理
                try:
                    pass
                except:
                    pass
            
            # 递归处理子组件
            try:
                children = widget.winfo_children()
                for child in children:
                    self._refresh_widget_recursively(child)
            except:
                pass
                
        except Exception as e:
            # 静默处理异常，避免中断整个刷新过程
            pass
    
    def update_child_windows_theme(self, theme_mode: str):
        """通知所有子窗口更新主题"""
        try:
            # 清理已关闭的窗口引用
            self.child_windows = [win for win in self.child_windows if win.winfo_exists()]
            
            # 更新所有子窗口主题
            for window in self.child_windows:
                if hasattr(window, 'update_theme'):
                    try:
                        window.update_theme(theme_mode)
                    except Exception as e:
                        print(f"⚠️ 更新子窗口主题失败: {e}")
            
            print(f"🔄 已通知 {len(self.child_windows)} 个子窗口更新主题")
            
        except Exception as e:
            print(f"❌ 更新子窗口主题失败: {e}")
    
    def update_language(self, language_code: str):
        """更新应用语言"""
        try:
            language_manager.set_language(language_code)
            
            # 更新窗口标题
            self.title(language_manager.t("app_title"))
            
            # 通知所有组件更新语言
            self.sidebar.update_language()
            self.chat_list.update_language()
            self.chat_interface.update_language()
            
            print(f"🌐 语言已切换为: {language_code}")
        except Exception as e:
            print(f"❌ 语言切换失败: {e}")
    
    def get_window_info(self):
        """获取窗口信息"""
        return {
            "geometry": self.geometry(),
            "state": self.state(),
            "focus": self.focus_get()
        } 