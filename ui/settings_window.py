#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 设置窗口

提供邮箱配置、主题设置、应用偏好等设置功能
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional
import threading

# 导入语言管理器和主题配置
from src.language_manager import language_manager
from ui.theme_config import theme, get_color, get_font


class SettingsWindow(ctk.CTkToplevel):
    """设置窗口类"""
    
    def __init__(self, parent, app):
        """初始化设置窗口"""
        super().__init__(parent)
        
        self.parent = parent
        self.app = app
        self.config_manager = app.config_manager
        self.email_manager = app.email_manager
        
        # 窗口设置
        self.setup_window()
        
        # 创建界面
        self.create_widgets()
        
        # 加载当前设置
        self.load_current_settings()
        
        print("设置窗口初始化完成")
    
    def setup_window(self):
        """设置现代化窗口属性"""
        self.title(language_manager.t("settings_title"))
        self.geometry("650x550")
        self.resizable(False, False)
        
        # 现代化窗口样式 - 使用动态背景色
        self.configure(fg_color=get_color("background"))
        
        # 居中显示
        self.transient(self.parent)
        self.grab_set()
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def get_checkbox_style(self):
        """获取优化后的复选框样式配置"""
        return {
            "checkbox_width": 18,
            "checkbox_height": 18,
            "corner_radius": theme.RADIUS["sm"],
            "border_width": 2,
            "fg_color": get_color("primary"),
            "hover_color": get_color("primary_hover"),
            "checkmark_color": get_color("white"),
            "text_color": get_color("gray_800"),
            "font": get_font("base")
        }
    
    def get_radio_style(self):
        """获取优化后的单选按钮样式配置"""
        return {
            "radiobutton_width": 16,
            "radiobutton_height": 16,
            "border_width_unchecked": 2,
            "border_width_checked": 4,
            "fg_color": get_color("primary"),
            "hover_color": get_color("primary_hover"),
            "text_color": get_color("gray_800"),
            "font": get_font("base")
        }
    
    def create_widgets(self):
        """创建简化的界面元素"""
        # 直接创建标签页容器（移除多余的main_frame）
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=theme.RADIUS["lg"],
            border_width=1,
            border_color=get_color("gray_200"),
            segmented_button_fg_color=get_color("gray_100"),
            segmented_button_selected_color=get_color("primary"),
            segmented_button_selected_hover_color=get_color("primary_hover"),
            text_color=get_color("text_primary")
        )
        self.tabview.pack(fill="both", expand=True, padx=theme.SPACING["md"], pady=theme.SPACING["md"])
        
        # 邮箱设置标签页
        self.email_tab = self.tabview.add(language_manager.t('email_settings'))
        self.create_email_settings(self.email_tab)
        
        # 应用设置标签页
        self.app_tab = self.tabview.add(language_manager.t('app_settings'))
        self.create_app_settings(self.app_tab)
        
        # 底部按钮区域
        self.create_bottom_buttons(self)
    
    def create_email_settings(self, parent):
        """创建现代化邮箱设置界面"""
        # 现代化滚动框架
        scrollable = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=get_color("gray_300"),
            scrollbar_button_hover_color=get_color("gray_400")
        )
        scrollable.pack(fill="both", expand=True, padx=theme.SPACING["sm"], pady=theme.SPACING["sm"])
        
        # SMTP设置卡片
        smtp_card = self.create_settings_card(
            scrollable, 
            f"SMTP {language_manager.t('send_settings')}"
        )
        smtp_card.pack(fill="x", pady=(0, theme.SPACING["md"]))
        
        # SMTP服务器
        self.create_input_field(
            smtp_card, 
            language_manager.t("smtp_server"), 
            "smtp.gmail.com"
        )
        self.smtp_server_entry = self.current_entry
        
        # SMTP端口
        self.create_input_field(
            smtp_card, 
            language_manager.t("smtp_port"), 
            "587"
        )
        self.smtp_port_entry = self.current_entry
        
        # IMAP设置卡片
        imap_card = self.create_settings_card(
            scrollable, 
            f"IMAP {language_manager.t('receive_settings')}"
        )
        imap_card.pack(fill="x", pady=(0, theme.SPACING["md"]))
        
        # IMAP服务器
        self.create_input_field(
            imap_card, 
            language_manager.t("imap_server"), 
            "imap.gmail.com"
        )
        self.imap_server_entry = self.current_entry
        
        # IMAP端口
        self.create_input_field(
            imap_card, 
            language_manager.t("imap_port"), 
            "993"
        )
        self.imap_port_entry = self.current_entry
        
        # 账户设置卡片
        account_card = self.create_settings_card(
            scrollable, 
            language_manager.t('account_settings')
        )
        account_card.pack(fill="x")
        
        # 邮箱地址
        self.create_input_field(
            account_card, 
            language_manager.t("email_address"), 
            "your@email.com"
        )
        self.email_entry = self.current_entry
        
        # 密码
        self.create_input_field(
            account_card, 
            language_manager.t("password"), 
            "••••••••",
            show="*"
        )
        self.password_entry = self.current_entry
        
        # 测试连接按钮（直接在卡片上放置，移除button_frame）
        self.test_btn = ctk.CTkButton(
            account_card, 
            text=language_manager.t('test_connection'),
            corner_radius=theme.RADIUS["md"],
            font=get_font("base"),
            fg_color=get_color("info"),
            hover_color=get_color("primary_hover"),
            command=self.test_email_connection,
            width=140,
            height=32,
            text_color=get_color("white")
        )
        self.test_btn.pack(padx=theme.SPACING["md"], pady=(theme.SPACING["sm"], theme.SPACING["xs"]))
        
        # 连接状态显示
        self.connection_status = ctk.CTkLabel(
            account_card, 
            text="", 
            font=get_font("sm"),
            text_color=get_color("gray_600")
        )
        self.connection_status.pack(padx=theme.SPACING["md"], pady=(0, theme.SPACING["sm"]))
    

    
    def create_app_settings(self, parent):
        """创建简化的应用设置"""
        scrollable = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=get_color("gray_300"),
            scrollbar_button_hover_color=get_color("gray_400")
        )
        scrollable.pack(fill="both", expand=True, padx=theme.SPACING["sm"], pady=theme.SPACING["sm"])
        
        # 启动设置 - 简化的卡片
        startup_card = self.create_settings_card(scrollable, language_manager.t('startup_settings'))
        startup_card.pack(fill="x", pady=(0, theme.SPACING["sm"]))
        
        self.auto_start_checkbox = ctk.CTkCheckBox(
            startup_card, 
            text=language_manager.t("auto_start"),
            font=get_font("base"),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=theme.RADIUS["sm"],
            border_width=2,
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            checkmark_color=get_color("white"),
            text_color=get_color("gray_800")
        )
        self.auto_start_checkbox.pack(anchor="w", padx=theme.SPACING["md"], pady=theme.SPACING["sm"])
        
        # 通知设置 - 简化的卡片
        notification_card = self.create_settings_card(scrollable, language_manager.t('notification_settings'))
        notification_card.pack(fill="x", pady=(0, theme.SPACING["sm"]))
        
        self.notifications_checkbox = ctk.CTkCheckBox(
            notification_card, 
            text=language_manager.t("enable_notifications"),
            font=get_font("base"),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=theme.RADIUS["sm"],
            border_width=2,
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            checkmark_color=get_color("white"),
            text_color=get_color("gray_800")
        )
        self.notifications_checkbox.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["sm"], theme.SPACING["xs"]))
        
        self.sound_checkbox = ctk.CTkCheckBox(
            notification_card, 
            text=language_manager.t("enable_sound"),
            font=get_font("base"),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=theme.RADIUS["sm"],
            border_width=2,
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            checkmark_color=get_color("white"),
            text_color=get_color("gray_800")
        )
        self.sound_checkbox.pack(anchor="w", padx=theme.SPACING["md"], pady=(0, theme.SPACING["sm"]))
        
        # 邮件轮询设置 - 简化的卡片
        polling_card = self.create_settings_card(scrollable, language_manager.t('polling_settings'))
        polling_card.pack(fill="x")
        
        # IDLE模式设置 - 直接在卡片内
        self.idle_enabled_checkbox = ctk.CTkCheckBox(
            polling_card, 
            text=language_manager.t('enable_idle_push'), 
            command=self.on_idle_mode_toggle,
            font=get_font("base"),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=theme.RADIUS["sm"],
            border_width=2,
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            checkmark_color=get_color("white"),
            text_color=get_color("gray_800")
        )
        self.idle_enabled_checkbox.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["sm"], theme.SPACING["xs"]))
        
        # IDLE状态和测试按钮 - 水平布局
        idle_status_frame = ctk.CTkFrame(polling_card, fg_color="transparent")
        idle_status_frame.pack(fill="x", padx=theme.SPACING["md"], pady=(0, theme.SPACING["xs"]))
        
        self.test_idle_btn = ctk.CTkButton(
            idle_status_frame, 
            text=language_manager.t('test_idle_support'), 
            command=self.test_idle_support, 
            width=140, 
            height=30,
            font=get_font("sm"),
            corner_radius=theme.RADIUS["md"],
            fg_color=get_color("info"),
            hover_color=get_color("primary_hover"),
            text_color=get_color("white")
        )
        self.test_idle_btn.pack(side="left")
        
        self.idle_status_label = ctk.CTkLabel(
            idle_status_frame, 
            text="", 
            font=get_font("sm")
        )
        self.idle_status_label.pack(side="left", padx=(theme.SPACING["sm"], 0))
        
        # IDLE说明
        idle_info = ctk.CTkLabel(
            polling_card, 
            text=language_manager.t('idle_mode_info'), 
            font=get_font("xs"), 
            text_color=get_color("gray_500")
        )
        idle_info.pack(anchor="w", padx=theme.SPACING["md"], pady=(0, theme.SPACING["sm"]))
        
        # 轮询间隔设置 - 直接在卡片内
        interval_label = ctk.CTkLabel(
            polling_card, 
            text=language_manager.t('polling_interval_label'),
            font=get_font("base")
        )
        interval_label.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["sm"], theme.SPACING["xs"]))
        
        # 轮询模式选择
        self.polling_mode_var = ctk.StringVar(value="auto")
        
        self.auto_mode_radio = ctk.CTkRadioButton(
            polling_card, 
            text=language_manager.t("smart_mode"), 
            variable=self.polling_mode_var, 
            value="auto",
            command=self.on_polling_mode_change,
            font=get_font("base"),
            radiobutton_width=16,
            radiobutton_height=16,
            border_width_unchecked=2,
            border_width_checked=4,
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            text_color=get_color("gray_800")
        )
        self.auto_mode_radio.pack(anchor="w", padx=theme.SPACING["md"], pady=theme.SPACING["xs"])
        
        self.manual_mode_radio = ctk.CTkRadioButton(
            polling_card, 
            text=language_manager.t("manual_mode"), 
            variable=self.polling_mode_var, 
            value="manual",
            command=self.on_polling_mode_change,
            font=get_font("base"),
            radiobutton_width=16,
            radiobutton_height=16,
            border_width_unchecked=2,
            border_width_checked=4,
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            text_color=get_color("gray_800")
        )
        self.manual_mode_radio.pack(anchor="w", padx=theme.SPACING["md"], pady=theme.SPACING["xs"])
        
        # 手动轮询间隔设置
        interval_time_label = ctk.CTkLabel(
            polling_card, 
            text=language_manager.t("interval_time_seconds"),
            font=get_font("base")
        )
        interval_time_label.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["sm"], theme.SPACING["xs"]))
        
        self.polling_interval_slider = ctk.CTkSlider(
            polling_card, 
            from_=5, 
            to=900, 
            number_of_steps=179,
            height=20,
            button_length=16,
            button_corner_radius=8,
            fg_color=get_color("gray_200"),
            progress_color=get_color("primary"),
            button_color=get_color("primary"),
            button_hover_color=get_color("primary_hover")
        )
        self.polling_interval_slider.pack(fill="x", padx=theme.SPACING["md"], pady=theme.SPACING["xs"])
        
        self.polling_interval_label = ctk.CTkLabel(
            polling_card, 
            text=f"30 {language_manager.t('seconds')}",
            font=get_font("sm")
        )
        self.polling_interval_label.pack(anchor="w", padx=theme.SPACING["md"])
        
        # 智能模式说明
        self.auto_mode_info = ctk.CTkLabel(
            polling_card, 
            text=language_manager.t('smart_mode_info_idle'), 
            font=get_font("xs"), 
            text_color=get_color("gray_500")
        )
        self.auto_mode_info.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["xs"], theme.SPACING["sm"]))
        
        # 绑定滑块事件
        self.polling_interval_slider.configure(command=self.on_polling_interval_change)
    
    def create_bottom_buttons(self, parent):
        """创建简化的底部按钮"""
        # 简化的按钮区域
        button_frame = ctk.CTkFrame(
            parent, 
            fg_color=get_color("gray_50"),
            corner_radius=theme.RADIUS["md"],
            height=60
        )
        button_frame.pack(fill="x", pady=(theme.SPACING["md"], theme.SPACING["sm"]))
        button_frame.pack_propagate(False)
        
        # 按钮样式配置
        button_config = {
            "width": 100,
            "height": 32,
            "corner_radius": theme.RADIUS["md"],
            "font": get_font("base")
        }
        
        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text=language_manager.t('cancel'),
            fg_color=get_color("gray_400"),
            hover_color=get_color("gray_500"),
            command=self.on_closing, 
            **button_config
        )
        cancel_btn.pack(side="right", padx=(theme.SPACING["sm"], theme.SPACING["md"]), pady=theme.SPACING["sm"])
        
        # 应用按钮
        apply_btn = ctk.CTkButton(
            button_frame, 
            text=language_manager.t('apply'),
            fg_color=get_color("secondary"),
            hover_color=get_color("secondary_hover"),
            command=self.apply_settings, 
            **button_config
        )
        apply_btn.pack(side="right", padx=(0, theme.SPACING["sm"]), pady=theme.SPACING["sm"])
        
        # 确定按钮
        ok_btn = ctk.CTkButton(
            button_frame, 
            text=language_manager.t('ok'),
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            command=self.save_and_close, 
            **button_config
        )
        ok_btn.pack(side="right", padx=(0, theme.SPACING["sm"]), pady=theme.SPACING["sm"])
    
    def create_settings_card(self, parent, title):
        """创建简化的设置卡片"""
        # 卡片容器
        card = ctk.CTkFrame(
            parent,
            fg_color=get_color("white"),
            corner_radius=theme.RADIUS["md"],
            border_width=1,
            border_color=get_color("gray_200")
        )
        
        # 标题
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=get_font("base", "bold"),
            text_color=get_color("gray_800"),
            anchor="w"
        )
        title_label.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["sm"], theme.SPACING["xs"]))
        
        return card
    
    def create_input_field(self, parent, label_text, placeholder="", show=None):
        """创建简化的输入字段"""
        # 标签
        label = ctk.CTkLabel(
            parent,
            text=f"{label_text}:",
            font=get_font("sm"),
            text_color=get_color("gray_700"),
            anchor="w"
        )
        label.pack(anchor="w", padx=theme.SPACING["md"], pady=(theme.SPACING["xs"], 1))
        
        # 输入框配置
        entry_config = {
            "height": 32,
            "corner_radius": theme.RADIUS["sm"],
            "font": get_font("base"),
            "fg_color": get_color("gray_50"),
            "border_width": 1,
            "border_color": get_color("gray_300"),
            "placeholder_text_color": get_color("gray_400"),
            "text_color": get_color("gray_800")
        }
        
        if show:
            entry_config["show"] = show
            
        if placeholder:
            entry_config["placeholder_text"] = placeholder
            
        # 输入框
        entry = ctk.CTkEntry(parent, **entry_config)
        entry.pack(fill="x", padx=theme.SPACING["md"], pady=(0, theme.SPACING["sm"]))
        
        # 聚焦效果
        def on_focus_in(event):
            entry.configure(border_color=get_color("primary"))
        
        def on_focus_out(event):
            entry.configure(border_color=get_color("gray_300"))
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
        # 保存当前输入框引用（用于外部访问）
        self.current_entry = entry
    
    def load_current_settings(self):
        """加载当前设置"""
        try:
            # 加载邮箱设置
            email_config = self.config_manager.get_email_config()
            self.smtp_server_entry.insert(0, email_config.get('smtp_server', ''))
            self.smtp_port_entry.insert(0, str(email_config.get('smtp_port', '')))
            self.imap_server_entry.insert(0, email_config.get('imap_server', ''))
            self.imap_port_entry.insert(0, str(email_config.get('imap_port', '')))
            self.email_entry.insert(0, email_config.get('username', ''))
            
            # 如果已有密码，显示占位符提示
            existing_password = email_config.get('password', '')
            if existing_password:
                self.password_entry.configure(placeholder_text=language_manager.t("password_saved_placeholder"))
            else:
                self.password_entry.configure(placeholder_text="••••••••")
            
            # 加载UI设置
            ui_config = self.config_manager.get_ui_config()
            
            # UI设置已移除，跳过
            
            # 加载应用设置
            app_config = self.config_manager.get_app_config()
            self.auto_start_checkbox.select() if app_config.get('auto_start', False) else self.auto_start_checkbox.deselect()
            self.notifications_checkbox.select() if app_config.get('notifications', True) else self.notifications_checkbox.deselect()
            self.sound_checkbox.select() if app_config.get('sound', True) else self.sound_checkbox.deselect()
            
            # 加载IDLE和轮询设置
            idle_enabled = app_config.get('idle_enabled', True)  # 默认启用
            polling_mode = app_config.get('polling_mode', 'auto')  # 默认智能模式
            polling_interval = app_config.get('polling_interval', 30)
            
            # 设置IDLE状态
            if idle_enabled:
                self.idle_enabled_checkbox.select()
            else:
                self.idle_enabled_checkbox.deselect()
            
            # 设置轮询模式
            self.polling_mode_var.set(polling_mode)
            
            # 设置轮询间隔
            self.polling_interval_slider.set(polling_interval)
            self.on_polling_interval_change(polling_interval)
            
            # 应用轮询模式设置
            self.on_polling_mode_change()
            
            # 如果启用了IDLE，检查之前的测试结果
            if idle_enabled:
                idle_test_result = app_config.get('idle_test_result', None)
                if idle_test_result is True:
                    self.idle_status_label.configure(text=language_manager.t("idle_supported"), text_color="green")
                elif idle_test_result is False:
                    self.idle_status_label.configure(text=language_manager.t("idle_not_supported"), text_color="red")
                else:
                    self.idle_status_label.configure(text=language_manager.t("idle_test_pending"), text_color="orange")
            
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def on_font_size_change(self, value):
        """字体大小改变事件"""
        self.font_size_label.configure(text=str(int(value)))
    
    def on_polling_interval_change(self, value):
        """轮询间隔改变事件"""
        interval = int(value)
        if interval >= 60:
            minutes = interval // 60
            seconds = interval % 60
            if seconds == 0:
                if minutes == 1:
                    text = f"{minutes} {language_manager.t('minute')}"
                else:
                    text = f"{minutes} {language_manager.t('minutes')}"
            else:
                text = f"{minutes} {language_manager.t('minutes')} {seconds} {language_manager.t('seconds')}"
        else:
            text = f"{interval} {language_manager.t('seconds')}"
        self.polling_interval_label.configure(text=text)
    
    def on_idle_mode_toggle(self):
        """IDLE模式开关切换事件"""
        if self.idle_enabled_checkbox.get():
            # 启用IDLE时，建议切换到智能模式
            if self.polling_mode_var.get() == "manual":
                self.polling_mode_var.set("auto")
                self.on_polling_mode_change()
            self.idle_status_label.configure(text=language_manager.t("idle_test_pending"), text_color="orange")
        else:
            self.idle_status_label.configure(text="", text_color="gray")
    
    def on_polling_mode_change(self):
        """轮询模式改变事件"""
        if self.polling_mode_var.get() == "auto":
            # 智能模式 - 隐藏手动设置
            self.polling_interval_slider.configure(state="disabled")
            self.auto_mode_info.configure(text_color=get_color("warning"))
            
            # 根据IDLE状态设置建议值
            if hasattr(self, 'idle_enabled_checkbox') and self.idle_enabled_checkbox.get():
                suggested_interval = 900  # 15分钟
                self.auto_mode_info.configure(text=language_manager.t("smart_mode_info_idle"))
            else:
                suggested_interval = 30   # 30秒
                self.auto_mode_info.configure(text=language_manager.t("smart_mode_info_no_idle"))
            
            self.polling_interval_slider.set(suggested_interval)
            self.on_polling_interval_change(suggested_interval)
        else:
            # 手动模式 - 显示手动设置
            self.polling_interval_slider.configure(state="normal")
            self.auto_mode_info.configure(text_color=get_color("gray_500"))
    
    def test_idle_support(self):
        """测试IMAP IDLE支持"""
        def test_thread():
            try:
                self.test_idle_btn.configure(state="disabled", text=language_manager.t("testing_idle"))
                self.idle_status_label.configure(text=language_manager.t("testing_connection"), text_color="orange")
                
                # 获取邮箱配置
                email_config = self.config_manager.get_email_config()
                if not all([email_config.get('imap_server'), email_config.get('username'), email_config.get('password')]):
                    raise ValueError(language_manager.t("complete_email_config_first"))
                
                # 测试IDLE支持
                idle_supported = self.email_manager.test_idle_support() if self.email_manager else False
                
                if idle_supported:
                    self.idle_status_label.configure(text=language_manager.t("idle_supported"), text_color="green")
                    # 自动启用IDLE并切换到智能模式
                    self.idle_enabled_checkbox.select()
                    if self.polling_mode_var.get() == "manual":
                        self.polling_mode_var.set("auto")
                        self.on_polling_mode_change()
                    
                    # 显示成功提示
                    self.after(100, lambda: messagebox.showinfo(
                        language_manager.t("idle_test_success_title"), 
                        language_manager.t("idle_test_success_message")
                    ))
                else:
                    self.idle_status_label.configure(text=language_manager.t("idle_not_supported"), text_color="red")
                    # 自动禁用IDLE并调整为高频轮询
                    self.idle_enabled_checkbox.deselect()
                    if self.polling_mode_var.get() == "auto":
                        self.polling_interval_slider.set(30)
                        self.on_polling_interval_change(30)
                    
                    # 显示建议提示
                    self.after(100, lambda: messagebox.showwarning(
                        language_manager.t("idle_not_supported_title"), 
                        language_manager.t("idle_not_supported_message")
                    ))
                    
            except Exception as e:
                error_msg = str(e)
                self.idle_status_label.configure(text=f"{language_manager.t('idle_test_failed')}: {error_msg}", text_color="red")
                self.after(100, lambda: messagebox.showerror(language_manager.t("idle_test_failed"), f"{language_manager.t('idle_test_failed')}:\n{error_msg}"))
            finally:
                self.test_idle_btn.configure(state="normal", text=language_manager.t("test_idle_support"))
        
        # 在新线程中执行测试
        threading.Thread(target=test_thread, daemon=True).start()
    
    def test_email_connection(self):
        """测试邮件连接"""
        def test_thread():
            try:
                self.test_btn.configure(state="disabled", text=language_manager.t("testing"))
                self.connection_status.configure(text=language_manager.t("testing_connection"), text_color="orange")
                
                # 获取设置值
                smtp_server = self.smtp_server_entry.get().strip()
                smtp_port = int(self.smtp_port_entry.get().strip() or "587")
                imap_server = self.imap_server_entry.get().strip()
                imap_port = int(self.imap_port_entry.get().strip() or "993")
                username = self.email_entry.get().strip()
                password = self.password_entry.get().strip()
                
                if not all([smtp_server, imap_server, username, password]):
                    raise ValueError(language_manager.t("incomplete_settings"))
                
                # 测试连接（使用邮件管理器的测试方法）
                if hasattr(self.email_manager, 'test_connection'):
                    success = self.email_manager.test_connection(
                        smtp_server, smtp_port, imap_server, imap_port, username, password
                    )
                    
                    if success:
                        self.connection_status.configure(text=language_manager.t("connection_success"), text_color="green")
                    else:
                        self.connection_status.configure(text=language_manager.t("connection_failed"), text_color="red")
                else:
                    # 简单验证
                    if "@" in username and "." in smtp_server and "." in imap_server:
                        self.connection_status.configure(text=language_manager.t("settings_valid"), text_color="green")
                    else:
                        self.connection_status.configure(text=language_manager.t("invalid_settings"), text_color="red")
                
            except Exception as e:
                self.connection_status.configure(text=str(e), text_color="red")
            finally:
                self.test_btn.configure(state="normal", text=language_manager.t("test_connection"))
        
        # 在新线程中执行测试
        threading.Thread(target=test_thread, daemon=True).start()
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 获取邮箱设置值
            smtp_server = self.smtp_server_entry.get().strip()
            smtp_port = int(self.smtp_port_entry.get().strip() or "587")
            imap_server = self.imap_server_entry.get().strip()
            imap_port = int(self.imap_port_entry.get().strip() or "993")
            username = self.email_entry.get().strip()
            password = self.password_entry.get().strip()
            
            # 如果密码为空但之前有保存的密码，使用已保存的密码
            if not password:
                existing_config = self.config_manager.get_email_config()
                existing_password = existing_config.get('password', '')
                if existing_password:
                    password = existing_password
            
            # 只有当所有必填字段都填写时才保存邮箱配置
            if smtp_server and imap_server and username and password:
                self.config_manager.set_email_config(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    imap_server=imap_server,
                    imap_port=imap_port,
                    username=username,
                    password=password
                )
            elif smtp_server or imap_server or username:
                # 部分填写的情况下，给出提示但不报错
                messagebox.showwarning(
                    language_manager.t("warning"),
                    language_manager.t("incomplete_email_config")
                )
            
            # 保存应用设置
            app_config = {
                'auto_start': self.auto_start_checkbox.get(),
                'notifications': self.notifications_checkbox.get(),
                'sound': self.sound_checkbox.get(),
                'idle_enabled': self.idle_enabled_checkbox.get(),
                'polling_mode': self.polling_mode_var.get(),
                'polling_interval': int(self.polling_interval_slider.get())
            }
            self.config_manager.set_app_config(**app_config)
            
            # 保存配置文件
            self.config_manager.save_config()
            
            # 重启邮件服务以应用新的轮询设置
            self.restart_email_services()
            
            messagebox.showinfo(language_manager.t("success"), language_manager.t("settings_applied"))
            
        except Exception as e:
            messagebox.showerror(language_manager.t("error"), f"{language_manager.t('save_failed')}: {str(e)}")
    
    def save_and_close(self):
        """保存设置并关闭窗口"""
        self.apply_settings()
        self.destroy()
    
    def restart_email_services(self):
        """重启邮件服务以应用新设置"""
        try:
            if hasattr(self.parent, 'email_manager') and self.parent.email_manager:
                print("重启邮件服务以应用新的轮询设置...")
                
                # 停止现有的邮件服务
                self.parent.email_manager.stop_polling()
                self.parent.email_manager.stop_send_thread()
                
                # 短暂等待确保线程完全停止
                import time
                time.sleep(1)
                
                # 重新启动邮件服务
                email_config = self.config_manager.get_email_config()
                if email_config['username'] and email_config['password']:
                    self.parent.email_manager.start_polling()
                    self.parent.email_manager.start_send_thread()
                    print("邮件服务已重启，新的轮询设置已生效")
                else:
                    print("邮件配置不完整，未启动轮询服务")
        except Exception as e:
            print(f"重启邮件服务失败: {e}")
    
    def on_closing(self):
        """窗口关闭事件"""
        self.destroy()
    
    def apply_ui_settings(self, ui_config):
        """立即应用界面设置"""
        try:
            # 应用语言设置
            current_lang = language_manager.get_language()
            new_lang = ui_config['language']
            if current_lang != new_lang:
                print(f"应用语言设置: {current_lang} -> {new_lang}")
                if hasattr(self.parent, 'update_language'):
                    self.parent.update_language(new_lang)
                else:
                    language_manager.set_language(new_lang)
                
                # 更新当前设置窗口的语言
                self.update_settings_language()
            
            # 应用字体大小设置
            font_size = ui_config['font_size']
            print(f"应用字体大小设置: {font_size}")
            # 字体大小会在下次重启时生效
            
        except Exception as e:
            print(f"应用界面设置失败: {e}")
    
    def update_theme(self, theme_mode: str):
        """更新设置窗口主题"""
        try:
            print(f"更新设置窗口主题: {theme_mode}")
            
            # 强制更新设置窗口主题
            if hasattr(self, '_apply_appearance_mode'):
                self._apply_appearance_mode(ctk.get_appearance_mode())
            
            # 递归更新所有组件
            self._refresh_components_recursively(self)
            
            # 延迟刷新确保主题完全应用
            self.after(100, self._delayed_refresh)
            
            print(f"设置窗口主题更新完成: {theme_mode}")
            
        except Exception as e:
            print(f"更新设置窗口主题失败: {e}")
    
    def _delayed_refresh(self):
        """延迟刷新，确保主题完全应用"""
        try:
            self.update_idletasks()
        except:
            pass
    
    def _refresh_components_recursively(self, widget):
        """递归更新设置窗口的所有组件主题"""
        try:
            # 强制所有CustomTkinter组件应用新主题
            if hasattr(widget, '_apply_appearance_mode'):
                try:
                    widget._apply_appearance_mode(ctk.get_appearance_mode())
                except:
                    pass
            
            # 递归处理子组件
            try:
                children = widget.winfo_children()
                for child in children:
                    self._refresh_components_recursively(child)
            except:
                pass
                
        except Exception as e:
            # 静默处理异常
            pass
    
    def update_settings_language(self):
        """更新设置窗口的语言显示"""
        try:
            # 更新窗口标题
            self.title(language_manager.t("settings_title"))
            
            # 更新标签页标题
            self.tabview.set(language_manager.t("email_settings"))
            
            print("设置窗口语言已更新")
        except Exception as e:
            print(f"更新设置窗口语言失败: {e}") 