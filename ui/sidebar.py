#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 侧边栏组件

包含设置、添加联系人、主题切换等功能按钮
现代化设计，支持悬停效果和动画
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional
# 导入UI组件
from ui.enhanced_components import HoverButton
# 导入语言管理器和主题配置
from src.language_manager import language_manager
from ui.theme_config import theme, get_color, get_font


class Sidebar(ctk.CTkFrame):
    """侧边栏组件"""
    
    def __init__(self, parent):
        """初始化侧边栏"""
        super().__init__(
            parent, 
            width=theme.SIZES["sidebar_width"], 
            corner_radius=0,
            fg_color=get_color("gray_50")
        )
        
        self.parent = parent
        self.button_animations = {}  # 存储按钮动画状态
        
        # 固定宽度
        self.grid_propagate(False)
        
        # 创建按钮
        self.create_buttons()
        
        # 初始化按钮状态
        self.initialize_button_states()
        
        print("📱 现代化侧边栏初始化完成")
    
    def create_buttons(self):
        """创建现代化侧边栏按钮"""
        # 现代化按钮配置 - 移除不支持的参数
        button_config = {
            "width": 50,
            "height": 50,
            "corner_radius": theme.RADIUS["lg"],
            "font": get_font("xl", "normal"),
            "fg_color": "transparent",
            "text_color": get_color("gray_600"),
            "border_width": 0,
        }
        
        # 按钮定义
        buttons_data = [
            ("settings", theme.ICONS["settings"], self.on_settings_click, "设置"),
            ("add_contact", theme.ICONS["add_contact"], self.on_add_contact_click, "添加联系人"),
            ("theme", theme.ICONS["theme_light"], self.on_theme_click, "主题切换"),
            ("notifications", theme.ICONS["notifications"], self.on_notification_click, "通知设置"),
            ("help", theme.ICONS["help"], self.on_help_click, "帮助"),
            ("language", "🌍", self.on_language_click, "语言设置"),
        ]
        
        # 创建增强按钮 
        for i, (name, icon, command, tooltip) in enumerate(buttons_data):
            btn = HoverButton(
                self,
                text=icon,
                command=command,  # 直接使用command参数
                **button_config
            )
            btn.grid(row=i, column=0, pady=(theme.SPACING["base"], theme.SPACING["sm"]), 
                    padx=theme.SPACING["base"])
            
            # 保存按钮引用
            setattr(self, f"{name}_btn", btn)
            
            # 添加工具提示(伪实现)
            self.add_tooltip(btn, tooltip)
        
        # 添加弹性空间
        self.grid_rowconfigure(len(buttons_data), weight=1)
        
        # 现代化状态指示器
        self.create_status_indicator(len(buttons_data) + 1)
    
    def create_status_indicator(self, row):
        """创建现代化状态指示器"""
        # 状态容器
        status_frame = ctk.CTkFrame(
            self,
            width=40,
            height=40,
            corner_radius=theme.RADIUS["full"],
            fg_color=get_color("success"),
            border_width=2,
            border_color=get_color("white")
        )
        status_frame.grid(row=row, column=0, pady=(0, theme.SPACING["lg"]))
        status_frame.grid_propagate(False)
        
        # 状态图标
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text=theme.ICONS["online"],
            font=get_font("base"),
            text_color=get_color("white")
        )
        self.status_indicator.place(relx=0.5, rely=0.5, anchor="center")
        
        # 保存状态框架引用
        self.status_frame = status_frame
    
    def add_tooltip(self, widget, text):
        """添加工具提示功能"""
        def on_enter(event):
            # 这里可以实现真正的工具提示，目前作为占位符
            pass
        
        def on_leave(event):
            pass
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def initialize_button_states(self):
        """初始化按钮状态"""
        # HoverButton已经内置了悬停效果，不需要额外添加
        pass
    
    def on_settings_click(self):
        """设置按钮点击事件"""
        try:
            print("⚙️ 设置按钮被点击")
            if hasattr(self.parent, 'switch_to_settings'):
                self.parent.switch_to_settings()
            else:
                print("⚠️  父级没有 switch_to_settings 方法")
        except Exception as e:
            print(f"❌ 设置按钮点击失败: {e}")
    
    def on_add_contact_click(self):
        """添加联系人按钮点击事件"""
        try:
            print("➕ 添加联系人按钮被点击")
            if hasattr(self.parent, 'show_add_contact_dialog'):
                self.parent.show_add_contact_dialog()
            else:
                print("⚠️  父级没有 show_add_contact_dialog 方法")
        except Exception as e:
            print(f"❌ 添加联系人按钮点击失败: {e}")
    
    def on_theme_click(self):
        """主题切换按钮点击事件"""
        try:
            print("🎨 主题切换按钮被点击")
            
            # 获取当前主题模式
            current_mode = ctk.get_appearance_mode()
            
            # 切换主题
            if current_mode == "Dark":
                new_mode = "light"
                new_icon = theme.ICONS["theme_light"]
            else:
                new_mode = "dark"
                new_icon = theme.ICONS["theme_dark"]
            
            # 应用新主题
            ctk.set_appearance_mode(new_mode)
            
            # 更新按钮图标
            self.theme_btn.configure(text=new_icon)
            
            print(f"🎨 主题已切换到: {new_mode}")
            
            # 保存主题设置到配置文件
            try:
                if hasattr(self.parent, 'app') and self.parent.app.config_manager:
                    self.parent.app.config_manager.set_ui_config(theme=new_mode)
                    self.parent.app.config_manager.save_config()
                    print(f"💾 主题设置已保存: {new_mode}")
            except Exception as e:
                print(f"❌ 保存主题设置失败: {e}")
            
            # 通知主窗口更新所有组件
            try:
                if hasattr(self.parent, 'update_theme'):
                    self.parent.update_theme(new_mode)
            except Exception as e:
                print(f"❌ 更新界面主题失败: {e}")
                
        except Exception as e:
            print(f"❌ 主题切换失败: {e}")
    
    def on_notification_click(self):
        """通知设置按钮点击事件"""
        print("🔔 通知设置按钮被点击")
        # TODO: 实现通知设置功能
    
    def on_help_click(self):
        """帮助按钮点击事件"""
        print("❓ 帮助按钮被点击")
        self.show_help_dialog()
    
    def on_language_click(self):
        """语言切换按钮点击事件"""
        try:
            # 获取当前语言
            current_lang = language_manager.current_language
            
            # 切换语言
            if current_lang == "zh":
                new_lang = "en"
            else:
                new_lang = "zh"
            
            print(f"🌐 {language_manager.t('language_switched')}: {current_lang} -> {new_lang}")
            
            # 更新语言
            if hasattr(self.parent, 'update_language'):
                self.parent.update_language(new_lang)
            else:
                print("⚠️  父级没有 update_language 方法")
            
            # 保存语言设置到配置文件
            try:
                if hasattr(self.parent, 'app') and self.parent.app.config_manager:
                    self.parent.app.config_manager.set_ui_config(language=new_lang)
                    self.parent.app.config_manager.save_config()
                    print(f"💾 语言设置已保存: {new_lang}")
            except Exception as e:
                print(f"❌ 保存语言设置失败: {e}")
                
        except Exception as e:
            print(f"❌ 语言切换失败: {e}")
    
    def show_help_dialog(self):
        """显示帮助对话框"""
        help_window = ctk.CTkToplevel(self)
        help_window.title(language_manager.t("help_title"))
        help_window.geometry("400x350")
        help_window.resizable(False, False)
        
        # 居中显示
        help_window.transient(self.parent)
        help_window.grab_set()
        
        # 帮助内容
        help_text = language_manager.t("help_content")
        
        help_label = ctk.CTkLabel(
            help_window,
            text=help_text,
            justify="left",
            font=("Arial", 12)
        )
        help_label.pack(pady=20, padx=20, fill="both", expand=True)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            help_window,
            text=language_manager.t("close"),
            command=help_window.destroy
        )
        close_btn.pack(pady=(0, 20))
    
    def update_status_indicator(self, status: str):
        """更新现代化状态指示器"""
        try:
            # 定义状态配置
            status_configs = {
                "online": {
                    "color": get_color("success"),
                    "icon": theme.ICONS["online"],
                    "text_color": get_color("white")
                },
                "offline": {
                    "color": get_color("offline"),
                    "icon": theme.ICONS["offline"],
                    "text_color": get_color("white")
                },
                "away": {
                    "color": get_color("away"),
                    "icon": theme.ICONS["away"],
                    "text_color": get_color("white")
                },
                "busy": {
                    "color": get_color("busy"),
                    "icon": theme.ICONS["busy"],
                    "text_color": get_color("white")
                },
                "error": {
                    "color": get_color("danger"),
                    "icon": theme.ICONS["error"],
                    "text_color": get_color("white")
                }
            }
            
            config = status_configs.get(status, status_configs["offline"])
            
            # 更新状态框架和指示器
            self.status_frame.configure(fg_color=config["color"])
            self.status_indicator.configure(
                text=config["icon"],
                text_color=config["text_color"]
            )
            
            print(f"📡 状态更新: {status}")
            
        except Exception as e:
            print(f"❌ 更新状态指示器失败: {e}")
    
    def update_language(self):
        """更新组件语言"""
        # 侧边栏本身主要是图标按钮，无需大量文本更新
        # 状态指示器颜色含义保持不变
        pass
    
    def set_button_state(self, button_name: str, enabled: bool):
        """设置按钮状态"""
        buttons = {
            "settings": self.settings_btn,
            "add_contact": self.add_contact_btn,
            "theme": self.theme_btn,
            "notification": self.notification_btn,
            "help": self.help_btn,
            "language": self.language_btn
        }
        
        if button_name in buttons:
            state = "normal" if enabled else "disabled"
            buttons[button_name].configure(state=state) 