#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 现代化消息气泡组件

用于显示聊天消息的可重用组件，支持现代化设计和动画效果
"""

import customtkinter as ctk
from typing import Dict, Optional
from datetime import datetime
# 导入主题配置
from ui.theme_config import theme, get_color, get_font


class MessageBubble(ctk.CTkFrame):
    """消息气泡组件"""
    
    def __init__(self, parent, message: Dict, **kwargs):
        """
        初始化现代化消息气泡
        
        Args:
            parent: 父容器
            message: 消息数据字典，包含：
                - sender: 发送者邮箱
                - content: 消息内容
                - timestamp: 时间戳
                - is_sent: 是否为发送的消息
                - message_type: 消息类型 (text, image, file)
        """
        # 根据消息类型设置现代化样式
        self.message = message
        self.is_sent = message.get("is_sent", False)
        
        # 修复消息颜色配置 - 确保暗色模式兼容
        if self.is_sent:
            # 我方发送的消息：蓝色背景
            bubble_color = get_color("primary")
        else:
            # 对方消息：在亮色模式用浅灰，暗色模式用深灰
            bubble_color = get_color("gray_100")
        
        super().__init__(
            parent,
            fg_color=bubble_color,
            corner_radius=theme.RADIUS["xl"],  # 更大的圆角
            **kwargs
        )
        
        # 创建消息内容
        self.create_content()
    
    def create_content(self):
        """创建消息内容"""
        message_type = self.message.get("message_type", "text")
        
        if message_type == "text":
            self.create_text_content()
        elif message_type == "image":
            self.create_image_content()
        elif message_type == "file":
            self.create_file_content()
        else:
            self.create_text_content()  # 默认为文本
    
    def create_text_content(self):
        """创建现代化文本消息内容"""
        # 修复文字颜色配置
        if self.is_sent:
            # 我方发送的消息：白色字体
            text_color = get_color("white")
            timestamp_color = get_color("white", 0.8)
        else:
            # 对方消息：黑色字体
            text_color = get_color("gray_800")
            timestamp_color = get_color("gray_500")
        
        # 主要内容容器 - 减少内边距
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=theme.SPACING["sm"], pady=theme.SPACING["sm"])
        
        # 创建消息和时间戳的组合容器
        message_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        message_container.pack(fill="both", expand=True)
        message_container.grid_columnconfigure(0, weight=1)
        
        # 使用标准的CTkTextbox，避免兼容性问题
        message_text = ctk.CTkTextbox(
            message_container,
            wrap="word",
            width=280,  # 稍微减小宽度给时间戳留空间
            height=40,  # 固定初始高度
            font=get_font("message"),
            text_color=text_color,
            fg_color="transparent",
            border_width=0,
            corner_radius=0
        )
        
        # 插入消息内容
        message_text.insert("0.0", self.message["content"])
        message_text.configure(state="disabled")  # 设置为只读，但仍可选中复制
        
        # 计算合适的高度 - 更紧凑
        lines = self.message["content"].count('\n') + 1
        char_width = 30  # 每行大约字符数
        text_lines = max(lines, len(self.message["content"]) // char_width + 1)
        text_height = min(max(text_lines * 22, 26), 180)  # 减小最小高度和行高
        
        message_text.configure(height=text_height)
        message_text.grid(row=0, column=0, sticky="ew", pady=0)
        
        # 绑定右键菜单
        self.add_context_menu(message_text)
        
        # 时间戳 - 放在右下角，更小的字体
        timestamp_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=16)
        timestamp_frame.pack(fill="x", pady=(2, 0))  # 减少上边距
        
        # 创建时间戳和状态的右下角容器
        meta_frame = ctk.CTkFrame(timestamp_frame, fg_color="transparent")
        meta_frame.pack(side="right")  # 始终在右下角
        
        # 时间戳标签 - 更小的字体
        timestamp_label = ctk.CTkLabel(
            meta_frame,
            text=self.format_timestamp(self.message.get("timestamp")),
            font=get_font("xs"),  # 使用最小字体
            text_color=timestamp_color,
            height=14
        )
        
        if self.is_sent:
            # 发送消息：状态 + 时间
            self.add_modern_message_status(meta_frame, timestamp_color)
            timestamp_label.pack(side="right", padx=(theme.SPACING["xs"], 0))
        else:
            # 接收消息：只显示时间
            timestamp_label.pack(side="right")
    
    def add_modern_message_status(self, parent, color):
        """添加现代化消息状态指示器"""
        status = self.message.get("status", "sent")
        
        # 现代化状态图标 - 更简洁
        status_icons = {
            "sending": "○",     # 发送中
            "sent": "✓",        # 已发送
            "delivered": "✓✓",  # 已送达  
            "read": "✓✓",       # 已读
            "error": "⚠"        # 发送失败
        }
        
        # 状态颜色
        status_colors = {
            "sending": get_color("gray_400"),
            "sent": color,
            "delivered": color,
            "read": get_color("info"),       # 已读用蓝色
            "error": get_color("danger")
        }
        
        # 状态指示器 - 更小的尺寸
        status_label = ctk.CTkLabel(
            parent,
            text=status_icons.get(status, "✓"),
            font=get_font("xs"),
            text_color=status_colors.get(status, color),
            width=16,
            height=16
        )
        status_label.pack(side="right", padx=(0, theme.SPACING["xs"]))
    
    def create_image_content(self):
        """创建现代化图片消息内容"""
        text_color = get_color("white") if self.is_sent else get_color("gray_800")
        timestamp_color = get_color("white", 0.7) if self.is_sent else get_color("gray_400")
        
        # 图片容器 - 更紧凑的设计
        image_frame = ctk.CTkFrame(
            self, 
            fg_color="transparent"
        )
        image_frame.pack(fill="both", expand=True, padx=theme.SPACING["md"], pady=theme.SPACING["md"])
        
        # 现代化图片占位符 - 圆角更大
        placeholder_frame = ctk.CTkFrame(
            image_frame,
            fg_color=get_color("gray_100") if not self.is_sent else get_color("primary_light"),
            corner_radius=theme.RADIUS["lg"],
            height=150,
            width=200
        )
        placeholder_frame.pack(pady=(0, theme.SPACING["xs"]))
        placeholder_frame.pack_propagate(False)
        
        # 图片图标 - 更现代的样式
        icon_label = ctk.CTkLabel(
            placeholder_frame,
            text="🖼️",
            font=get_font("4xl"),
            text_color=text_color
        )
        icon_label.place(relx=0.5, rely=0.4, anchor="center")
        
        # 图片说明 - 更细致的文字
        desc_label = ctk.CTkLabel(
            placeholder_frame,
            text="图片",
            font=get_font("sm"),
            text_color=get_color("gray_600")
        )
        desc_label.place(relx=0.5, rely=0.65, anchor="center")
        
        # 时间戳 - 统一样式
        self.add_compact_timestamp(image_frame, timestamp_color)
    
    def create_file_content(self):
        """创建现代化文件消息内容"""
        text_color = get_color("white") if self.is_sent else get_color("gray_800")
        timestamp_color = get_color("white", 0.7) if self.is_sent else get_color("gray_400")
        
        # 文件容器
        file_container = ctk.CTkFrame(self, fg_color="transparent")
        file_container.pack(fill="both", expand=True, padx=theme.SPACING["md"], pady=theme.SPACING["md"])
        
        # 文件信息框 - 现代化设计
        file_info_frame = ctk.CTkFrame(
            file_container,
            fg_color=get_color("gray_50") if not self.is_sent else get_color("primary_light"),
            corner_radius=theme.RADIUS["lg"],
            height=70
        )
        file_info_frame.pack(fill="x", pady=(0, theme.SPACING["xs"]))
        file_info_frame.pack_propagate(False)
        
        # 文件图标 - 更大更清晰
        file_icon = ctk.CTkLabel(
            file_info_frame,
            text="📄",
            font=get_font("2xl"),
            text_color=text_color
        )
        file_icon.place(relx=0.12, rely=0.5, anchor="center")
        
        # 文件信息
        file_name = self.message.get("file_name", "文件.txt")
        file_size = self.message.get("file_size", "未知大小")
        
        # 文件名 - 可选中的文本
        file_name_text = ctk.CTkTextbox(
            file_info_frame,
            width=140,
            height=20,
            font=get_font("base", "bold"),
            text_color=text_color,
            fg_color="transparent",
            border_width=0,
            corner_radius=0
        )
        file_name_text.insert("0.0", file_name)
        file_name_text.configure(state="disabled")
        file_name_text.place(relx=0.25, rely=0.35, anchor="w")
        
        # 文件大小
        file_size_label = ctk.CTkLabel(
            file_info_frame,
            text=file_size,
            font=get_font("xs"),
            text_color=get_color("gray_500"),
            anchor="w"
        )
        file_size_label.place(relx=0.25, rely=0.65, anchor="w")
        
        # 时间戳
        self.add_compact_timestamp(file_container, timestamp_color)
    
    def format_timestamp(self, timestamp) -> str:
        """格式化时间戳"""
        if not timestamp:
            return datetime.now().strftime("%H:%M")
        
        if isinstance(timestamp, str):
            return timestamp
        
        try:
            if isinstance(timestamp, datetime):
                return timestamp.strftime("%H:%M")
            else:
                return str(timestamp)
        except:
            return datetime.now().strftime("%H:%M")
    
    def update_message(self, message: Dict):
        """更新消息"""
        self.message = message
        self.bubble.update_message(message)
    
    def add_compact_timestamp(self, container, timestamp_color):
        """添加紧凑的时间戳显示"""
        timestamp_label = ctk.CTkLabel(
            container,
            text=self.format_timestamp(self.message.get("timestamp")),
            font=get_font("xs"),
            text_color=timestamp_color,
            height=16
        )
        
        if self.is_sent:
            timestamp_label.pack(anchor="e", pady=(0, 2))
        else:
            timestamp_label.pack(anchor="w", pady=(0, 2))

    def add_context_menu(self, textbox):
        """为文本框添加右键上下文菜单"""
        def show_context_menu(event):
            try:
                import tkinter as tk
                context_menu = tk.Menu(textbox, tearoff=0)
                
                # 添加复制选项
                context_menu.add_command(
                    label="复制",
                    command=lambda: self.copy_text_content(textbox)
                )
                
                # 添加全选选项
                context_menu.add_command(
                    label="全选",
                    command=lambda: self.select_all_text(textbox)
                )
                
                context_menu.tk_popup(event.x_root, event.y_root)
            except Exception as e:
                print(f"❌ 显示右键菜单失败: {e}")
            finally:
                try:
                    context_menu.grab_release()
                except:
                    pass
        
        textbox.bind("<Button-3>", show_context_menu)
    
    def copy_text_content(self, textbox):
        """复制文本框内容"""
        try:
            # 临时启用编辑状态
            textbox.configure(state="normal")
            
            # 获取选中的文本
            try:
                selected_text = textbox.selection_get()
                if selected_text:
                    textbox.clipboard_clear()
                    textbox.clipboard_append(selected_text)
                    print(f"📋 已复制选中文本: {selected_text[:50]}...")
                else:
                    # 如果没有选中文本，复制全部内容
                    all_text = textbox.get("0.0", "end-1c")
                    if all_text:
                        textbox.clipboard_clear()
                        textbox.clipboard_append(all_text)
                        print(f"📋 已复制全部文本: {all_text[:50]}...")
            except:
                # 如果没有选中文本，复制全部内容
                all_text = textbox.get("0.0", "end-1c")
                if all_text:
                    textbox.clipboard_clear()
                    textbox.clipboard_append(all_text)
                    print(f"📋 已复制全部文本: {all_text[:50]}...")
            
            # 恢复只读状态
            textbox.configure(state="disabled")
        except Exception as e:
            print(f"❌ 复制失败: {e}")
    
    def select_all_text(self, textbox):
        """选中所有文本"""
        try:
            textbox.configure(state="normal")
            textbox.tag_add("sel", "0.0", "end-1c")
            textbox.configure(state="disabled")
        except Exception as e:
            print(f"❌ 全选失败: {e}")


class MessageContainer(ctk.CTkFrame):
    """消息容器，包含消息气泡和布局"""
    
    def __init__(self, parent, message: Dict, **kwargs):
        """
        初始化现代化消息容器
        
        Args:
            parent: 父容器
            message: 消息数据
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.message = message
        self.is_sent = message.get("is_sent", False)
        
        # 配置网格 - 现代化布局
        self.grid_columnconfigure(0, weight=1)
        
        # 创建消息气泡
        self.create_modern_message_bubble()
    
    def create_modern_message_bubble(self):
        """创建现代化消息气泡布局"""
        # 消息气泡 - 参考微信、Telegram等现代聊天软件的设计
        self.bubble = MessageBubble(self, self.message)
        
        # 现代化布局：发送消息靠右，接收消息靠左，减少边距
        if self.is_sent:
            # 发送消息：右对齐，左侧留更多空间
            self.bubble.grid(
                row=0, 
                column=0, 
                sticky="e", 
                padx=(60, theme.SPACING["sm"]),  # 减少右边距
                pady=theme.SPACING["xs"]
            )
        else:
            # 接收消息：左对齐，右侧留更多空间
            self.bubble.grid(
                row=0, 
                column=0, 
                sticky="w", 
                padx=(theme.SPACING["sm"], 60),  # 减少左边距
                pady=theme.SPACING["xs"]
            ) 