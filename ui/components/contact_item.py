#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 联系人条目组件

用于在联系人列表中显示的可重用组件
"""

import customtkinter as ctk
from typing import Dict, Callable, Optional


class ContactItem(ctk.CTkFrame):
    """联系人条目组件"""
    
    def __init__(self, parent, contact: Dict, on_click: Optional[Callable] = None, **kwargs):
        """
        初始化联系人条目
        
        Args:
            parent: 父容器
            contact: 联系人数据字典，包含：
                - email: 邮箱地址
                - nickname: 昵称
                - last_message: 最后消息
                - last_time: 最后消息时间
                - unread_count: 未读消息数
                - online: 是否在线
            on_click: 点击回调函数
        """
        super().__init__(
            parent,
            height=70,
            corner_radius=8,
            cursor="hand2",
            **kwargs
        )
        
        self.contact = contact
        self.on_click = on_click
        self.selected = False
        
        # 固定高度
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        
        # 创建内容
        self.create_content()
        
        # 绑定点击事件
        self.bind_click_events()
    
    def create_content(self):
        """创建联系人条目内容"""
        # 头像区域 (左侧)
        self.create_avatar()
        
        # 信息区域 (中间)
        self.create_info_area()
        
        # 状态和徽章区域 (右侧)
        self.create_status_area()
    
    def create_avatar(self):
        """创建头像区域"""
        self.avatar_frame = ctk.CTkFrame(
            self,
            width=50,
            height=50,
            corner_radius=25,
            fg_color=self.get_avatar_color()
        )
        self.avatar_frame.grid(row=0, column=0, padx=(10, 8), pady=10, sticky="nsew")
        self.avatar_frame.grid_propagate(False)
        
        # 头像文字 (姓名首字母)
        avatar_text = self.contact["nickname"][0].upper() if self.contact["nickname"] else "?"
        self.avatar_label = ctk.CTkLabel(
            self.avatar_frame,
            text=avatar_text,
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def create_info_area(self):
        """创建信息区域"""
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        # 第一行：姓名和时间
        name_time_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        name_time_frame.grid(row=0, column=0, sticky="ew", pady=(5, 2))
        name_time_frame.grid_columnconfigure(0, weight=1)
        
        # 姓名
        self.name_label = ctk.CTkLabel(
            name_time_frame,
            text=self.contact["nickname"],
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        self.name_label.grid(row=0, column=0, sticky="w")
        
        # 时间
        self.time_label = ctk.CTkLabel(
            name_time_frame,
            text=self.contact.get("last_time", ""),
            font=("Arial", 10),
            text_color="gray60",
            anchor="e"
        )
        self.time_label.grid(row=0, column=1, sticky="e", padx=(5, 0))
        
        # 第二行：最后消息和未读计数
        message_badge_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        message_badge_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        message_badge_frame.grid_columnconfigure(0, weight=1)
        
        # 最后消息
        last_message = self.contact.get("last_message", "")
        # 限制消息长度
        if len(last_message) > 30:
            last_message = last_message[:30] + "..."
        
        self.message_label = ctk.CTkLabel(
            message_badge_frame,
            text=last_message,
            font=("Arial", 11),
            text_color="gray70",
            anchor="w"
        )
        self.message_label.grid(row=0, column=0, sticky="w")
        
        # 未读消息计数
        unread_count = self.contact.get("unread_count", 0)
        if unread_count > 0:
            self.unread_badge = ctk.CTkLabel(
                message_badge_frame,
                text=str(unread_count),
                font=("Arial", 9, "bold"),
                text_color="white",
                fg_color="red",
                corner_radius=10,
                width=20,
                height=20
            )
            self.unread_badge.grid(row=0, column=1, sticky="e", padx=(5, 0))
    
    def create_status_area(self):
        """创建状态区域"""
        # 在线状态指示器
        if self.contact.get("online", False):
            self.status_indicator = ctk.CTkLabel(
                self,
                text="●",
                font=("Arial", 8),
                text_color="green"
            )
            self.status_indicator.grid(row=0, column=2, sticky="ne", padx=(0, 8), pady=8)
    
    def get_avatar_color(self) -> str:
        """根据姓名生成头像颜色"""
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", 
            "#FECA57", "#FF9FF3", "#54A0FF", "#5F27CD",
            "#00D2D3", "#FF9F43", "#FD79A8", "#E17055"
        ]
        
        # 基于邮箱地址生成颜色索引
        email = self.contact.get("email", "")
        color_index = sum(ord(c) for c in email) % len(colors)
        return colors[color_index]
    
    def bind_click_events(self):
        """绑定点击事件"""
        def on_click_handler(event=None):
            if self.on_click:
                self.on_click(self.contact)
            return "break"
        
        # 为主widget和所有子组件绑定点击事件
        def bind_recursive(widget):
            try:
                widget.bind("<Button-1>", on_click_handler)
                if hasattr(widget, 'configure'):
                    widget.configure(cursor="hand2")
            except:
                pass
            
            for child in widget.winfo_children():
                bind_recursive(child)
        
        bind_recursive(self)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.selected = selected
        
        if selected:
            # 选中状态：蓝色背景
            self.configure(fg_color=("lightblue", "darkblue"))
        else:
            # 普通状态：默认背景色
            self.configure(fg_color=("gray90", "gray13"))
    
    def update_contact(self, contact: Dict):
        """更新联系人信息"""
        self.contact = contact
        
        # 更新姓名
        self.name_label.configure(text=contact["nickname"])
        
        # 更新头像文字
        avatar_text = contact["nickname"][0].upper() if contact["nickname"] else "?"
        self.avatar_label.configure(text=avatar_text)
        
        # 更新头像颜色
        self.avatar_frame.configure(fg_color=self.get_avatar_color())
        
        # 更新最后消息
        last_message = contact.get("last_message", "")
        if len(last_message) > 30:
            last_message = last_message[:30] + "..."
        self.message_label.configure(text=last_message)
        
        # 更新时间
        self.time_label.configure(text=contact.get("last_time", ""))
        
        # 更新未读计数
        self.update_unread_count(contact.get("unread_count", 0))
        
        # 更新在线状态
        self.update_online_status(contact.get("online", False))
    
    def update_unread_count(self, count: int):
        """更新未读消息计数"""
        # 移除现有的未读徽章
        if hasattr(self, 'unread_badge'):
            self.unread_badge.destroy()
            delattr(self, 'unread_badge')
        
        # 如果有未读消息，创建新徽章
        if count > 0:
            # 重新获取父容器
            message_badge_frame = None
            for child in self.info_frame.winfo_children():
                if child.grid_info()['row'] == 1:
                    message_badge_frame = child
                    break
            
            if message_badge_frame:
                self.unread_badge = ctk.CTkLabel(
                    message_badge_frame,
                    text=str(count),
                    font=("Arial", 9, "bold"),
                    text_color="white",
                    fg_color="red",
                    corner_radius=10,
                    width=20,
                    height=20
                )
                self.unread_badge.grid(row=0, column=1, sticky="e", padx=(5, 0))
    
    def update_online_status(self, online: bool):
        """更新在线状态"""
        # 移除现有的状态指示器
        if hasattr(self, 'status_indicator'):
            self.status_indicator.destroy()
            delattr(self, 'status_indicator')
        
        # 如果在线，创建状态指示器
        if online:
            self.status_indicator = ctk.CTkLabel(
                self,
                text="●",
                font=("Arial", 8),
                text_color="green"
            )
            self.status_indicator.grid(row=0, column=2, sticky="ne", padx=(0, 8), pady=8)
    
    def get_contact_data(self) -> Dict:
        """获取联系人数据"""
        return self.contact 