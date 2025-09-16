#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 添加联系人窗口

提供添加新联系人的功能，包括邮箱验证、昵称设置等
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
from typing import Optional, Callable

# 导入语言管理器
from src.language_manager import language_manager


class AddContactWindow(ctk.CTkToplevel):
    """添加联系人窗口类"""
    
    def __init__(self, parent, app, on_contact_added: Optional[Callable] = None):
        """初始化添加联系人窗口"""
        super().__init__(parent)
        
        self.parent = parent
        self.app = app
        self.database_manager = app.database_manager
        self.on_contact_added = on_contact_added  # 添加成功后的回调函数
        
        # 窗口设置
        self.setup_window()
        
        # 创建界面
        self.create_widgets()
        
        print("➕ 添加联系人窗口初始化完成")
    
    def setup_window(self):
        """设置窗口属性"""
        self.title(language_manager.t("add_contact_title"))
        self.geometry("400x450")
        self.resizable(False, False)
        
        # 居中显示
        self.transient(self.parent)
        self.grab_set()
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面元素"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="➕ " + language_manager.t("add_new_contact"),
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(30, 40))
        
        # 邮箱地址
        email_label = ctk.CTkLabel(
            self,
            text=language_manager.t("email_address") + " *:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        email_label.pack(anchor="w", padx=30, pady=(10, 5))
        
        self.email_entry = ctk.CTkEntry(
            self,
            width=350,
            height=35,
            placeholder_text=language_manager.t("email_placeholder"),
            font=("Arial", 12)
        )
        self.email_entry.pack(padx=30, pady=(0, 5))
        
        # 邮箱验证状态
        self.email_status = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 10),
            anchor="w"
        )
        self.email_status.pack(anchor="w", padx=30, pady=(0, 20))
        
        # 昵称
        nickname_label = ctk.CTkLabel(
            self,
            text=language_manager.t("nickname") + " *:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        nickname_label.pack(anchor="w", padx=30, pady=(5, 5))
        
        self.nickname_entry = ctk.CTkEntry(
            self,
            width=350,
            height=35,
            placeholder_text=language_manager.t("nickname_placeholder"),
            font=("Arial", 12)
        )
        self.nickname_entry.pack(padx=30, pady=(0, 40))
        
        # 按钮区域
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(20, 30))
        
        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=language_manager.t("cancel"),
            width=120,
            height=40,
            command=self.on_closing
        )
        cancel_btn.pack(side="left", pady=10)
        
        # 添加按钮
        self.add_btn = ctk.CTkButton(
            button_frame,
            text=language_manager.t("add_contact"),
            width=120,
            height=40,
            command=self.add_contact,
            state="disabled"
        )
        self.add_btn.pack(side="right", pady=10)
        
        # 绑定事件
        self.email_entry.bind("<KeyRelease>", self.on_email_change)
        self.email_entry.bind("<FocusOut>", self.validate_email)
        self.nickname_entry.bind("<KeyRelease>", self.on_nickname_change)
        
        # 设置焦点到邮箱输入框
        self.email_entry.focus()
        
        print("✅ 简化的添加联系人界面创建完成")
    

    
    def on_email_change(self, event=None):
        """邮箱输入改变事件"""
        email = self.email_entry.get().strip()
        
        if not email:
            self.email_status.configure(text="", text_color="gray")
            self.check_form_validity()
            return
        
        # 实时格式验证
        if self.is_valid_email_format(email):
            self.email_status.configure(
                text="✓ " + language_manager.t("email_format_valid"),
                text_color="green"
            )
        else:
            self.email_status.configure(
                text="✗ " + language_manager.t("email_format_invalid"),
                text_color="red"
            )
        
        # 自动填充昵称
        if not self.nickname_entry.get().strip() and "@" in email:
            suggested_nickname = email.split("@")[0]
            self.nickname_entry.delete(0, "end")
            self.nickname_entry.insert(0, suggested_nickname)
        
        self.check_form_validity()
    
    def validate_email(self, event=None):
        """验证邮箱（失去焦点时）"""
        email = self.email_entry.get().strip()
        
        if not email:
            return
        
        # 格式验证
        if not self.is_valid_email_format(email):
            self.email_status.configure(
                text="✗ " + language_manager.t("email_format_invalid"),
                text_color="red"
            )
            return
        
        # 检查是否已存在
        if self.is_contact_exists(email):
            self.email_status.configure(
                text="⚠️ " + language_manager.t("contact_already_exists"),
                text_color="orange"
            )
        else:
            self.email_status.configure(
                text="✓ " + language_manager.t("email_available"),
                text_color="green"
            )
        
        self.check_form_validity()
    
    def on_nickname_change(self, event=None):
        """昵称输入改变事件"""
        self.check_form_validity()
    

    
    def is_valid_email_format(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_contact_exists(self, email: str) -> bool:
        """检查联系人是否已存在"""
        try:
            if self.database_manager:
                existing_contacts = self.database_manager.get_contacts()
                return any(contact["email"].lower() == email.lower() for contact in existing_contacts)
        except Exception as e:
            print(f"❌ 检查联系人失败: {e}")
        
        return False
    
    def check_form_validity(self):
        """检查表单有效性"""
        email = self.email_entry.get().strip()
        nickname = self.nickname_entry.get().strip()
        
        # 检查必填字段和格式
        is_valid = (
            email and 
            nickname and 
            self.is_valid_email_format(email) and 
            not self.is_contact_exists(email)
        )
        
        # 更新添加按钮状态
        self.add_btn.configure(state="normal" if is_valid else "disabled")
    
    def add_contact(self):
        """添加联系人"""
        try:
            # 获取表单数据
            email = self.email_entry.get().strip()
            nickname = self.nickname_entry.get().strip()
            
            # 最终验证
            if not self.is_valid_email_format(email):
                messagebox.showerror(
                    language_manager.t("error"),
                    language_manager.t("email_format_invalid")
                )
                return
            
            if self.is_contact_exists(email):
                messagebox.showerror(
                    language_manager.t("error"),
                    language_manager.t("contact_already_exists")
                )
                return
            
            if not nickname:
                messagebox.showerror(
                    language_manager.t("error"),
                    language_manager.t("nickname_required")
                )
                return
            
            # 添加到数据库
            if self.database_manager:
                success = self.database_manager.add_contact(
                    email=email,
                    nickname=nickname
                )
                
                if success:
                    messagebox.showinfo(
                        language_manager.t("success"),
                        language_manager.t("contact_added_successfully")
                    )
                    
                    # 调用回调函数
                    if self.on_contact_added:
                        self.on_contact_added({
                            "email": email,
                            "nickname": nickname,
                            "last_message": "",
                            "last_time": "",
                            "unread_count": 0,
                            "online": False
                        })
                    
                    # 关闭窗口
                    self.destroy()
                else:
                    messagebox.showerror(
                        language_manager.t("error"),
                        language_manager.t("add_contact_failed")
                    )
            else:
                messagebox.showerror(
                    language_manager.t("error"),
                    language_manager.t("database_error")
                )
                
        except Exception as e:
            print(f"❌ 添加联系人失败: {e}")
            messagebox.showerror(
                language_manager.t("error"),
                f"{language_manager.t('add_contact_failed')}: {str(e)}"
            )
    

    
    def on_closing(self):
        """窗口关闭事件"""
        self.destroy() 