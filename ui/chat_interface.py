#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 聊天界面组件

显示聊天消息和提供消息发送功能
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Optional
from datetime import datetime
# 导入语言管理器和主题配置
from src.language_manager import language_manager
from ui.theme_config import theme, get_color, get_font
from ui.components.message_bubble import MessageContainer
from ui.enhanced_components import ModernEntry, HoverButton


class ChatInterface(ctk.CTkFrame):
    """聊天界面组件"""
    
    def __init__(self, parent):
        """初始化聊天界面"""
        super().__init__(parent, corner_radius=0)
        
        self.parent = parent
        self.current_contact = None
        self.messages = []  # 当前聊天的消息列表
        self.typing_indicator = None  # 打字指示器
        self.last_message_date = None  # 用于时间分组
        
        # 创建界面元素
        self.create_widgets()
        
        # 显示欢迎界面
        self.show_welcome_screen()
        
        print("💬 聊天界面初始化完成")
    
    def create_widgets(self):
        """创建界面元素"""
        # 配置网格权重
        self.grid_rowconfigure(1, weight=1)  # 消息显示区域可伸缩
        self.grid_columnconfigure(0, weight=1)
        
        # 顶部联系人信息栏
        self.create_contact_header()
        
        # 中间消息显示区域
        self.create_message_area()
        
        # 底部消息输入区域
        self.create_input_area()
    
    def create_contact_header(self):
        """创建现代化顶部联系人信息栏"""
        self.header_frame = ctk.CTkFrame(
            self, 
            height=70, 
            corner_radius=0,
            fg_color=get_color("white"),
            border_width=1,
            border_color=get_color("gray_200")
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # 现代化联系人头像
        self.contact_avatar = ctk.CTkFrame(
            self.header_frame, 
            width=theme.SIZES["avatar_lg"], 
            height=theme.SIZES["avatar_lg"], 
            corner_radius=theme.SIZES["avatar_lg"]//2,
            fg_color=get_color("primary"),
            border_width=2,
            border_color=get_color("white")
        )
        self.contact_avatar.grid(row=0, column=0, padx=(theme.SPACING["lg"], theme.SPACING["md"]), pady=theme.SPACING["md"])
        self.contact_avatar.grid_propagate(False)
        
        # 头像文字 - 现代化字体
        self.avatar_label = ctk.CTkLabel(
            self.contact_avatar,
            text="?",
            font=get_font("lg", "bold"),
            text_color=get_color("white")
        )
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 现代化联系人信息
        info_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", pady=theme.SPACING["md"])
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 联系人姓名 - 现代化样式
        self.contact_name = ctk.CTkLabel(
            info_frame,
            text=language_manager.t("select_contact_to_start"),
            font=get_font("lg", "bold"),
            text_color=get_color("gray_800"),
            anchor="w"
        )
        self.contact_name.grid(row=0, column=0, sticky="w", pady=(0, theme.SPACING["xs"]))
        
        # 在线状态 - 现代化样式
        self.contact_status = ctk.CTkLabel(
            info_frame,
            text="",
            font=get_font("sm"),
            text_color=get_color("gray_500"),
            anchor="w"
        )
        self.contact_status.grid(row=1, column=0, sticky="w")
        
        # 现代化功能按钮区域
        button_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, padx=(theme.SPACING["sm"], theme.SPACING["lg"]), pady=theme.SPACING["md"])
        
        # 现代化更多选项按钮 - 移除不支持的参数
        self.more_btn = ctk.CTkButton(
            button_frame,
            text=theme.ICONS["more"],
            width=36,
            height=36,
            corner_radius=theme.RADIUS["full"],
            font=get_font("md"),
            fg_color="transparent",
            text_color=get_color("gray_600"),
            command=self.show_more_options
        )
        self.more_btn.grid(row=0, column=0)
    
    def create_message_area(self):
        """创建现代化消息显示区域"""
        # 现代化滚动框架用于显示消息
        self.message_scrollable = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color=get_color("gray_50"),
            scrollbar_button_color=get_color("gray_300"),
            scrollbar_button_hover_color=get_color("gray_400")
        )
        self.message_scrollable.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.message_scrollable.grid_columnconfigure(0, weight=1)
        
        print("📜 现代化消息显示区域创建完成")
    
    def create_input_area(self):
        """创建现代化消息输入区域"""
        # 输入区域主容器 - 添加底部留白
        input_area = ctk.CTkFrame(
            self, 
            height=80,  # 增加高度以提供更好的视觉效果
            corner_radius=0,
            fg_color=get_color("white"),
            border_width=1,
            border_color=get_color("gray_200")
        )
        input_area.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        input_area.grid_propagate(False)
        input_area.grid_columnconfigure(0, weight=1)
        
        # 简化的输入容器 - 只保留输入框和发送按钮
        input_container = ctk.CTkFrame(input_area, fg_color="transparent")
        input_container.grid(row=0, column=0, sticky="ew", padx=theme.SPACING["lg"], pady=theme.SPACING["md"])
        input_container.grid_columnconfigure(0, weight=1)
        
        # 现代化消息输入框
        self.message_entry = ctk.CTkTextbox(
            input_container,
            height=50,
            corner_radius=theme.RADIUS["lg"],
            font=get_font("base"),
            wrap="word",
            border_width=1,
            border_color=get_color("gray_300"),
            fg_color=get_color("gray_50")
        )
        
        # 添加输入框聚焦效果
        self.add_textbox_focus_effect()
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(0, theme.SPACING["md"]))
        
        # 现代化发送按钮 - 使用CustomTkinter的hover_color参数
        self.send_btn = ctk.CTkButton(
            input_container,
            text=theme.ICONS["send"],
            width=50,
            height=50,
            corner_radius=theme.RADIUS["full"],
            font=get_font("md", "bold"),
            fg_color=get_color("primary"),
            hover_color=get_color("primary_hover"),
            text_color=get_color("white"),
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=1)
        
        # 绑定快捷键
        self.message_entry.bind("<Return>", self.on_enter_key)
        self.message_entry.bind("<Control-Return>", self.on_ctrl_enter)
        
        # 初始状态禁用输入
        self.set_input_enabled(False)
    
    def add_textbox_focus_effect(self):
        """为输入框添加聚焦效果"""
        def on_focus_in(event):
            try:
                self.message_entry.configure(
                    border_color=get_color("primary"),
                    border_width=2
                )
            except:
                pass
        
        def on_focus_out(event):
            try:
                self.message_entry.configure(
                    border_color=get_color("gray_300"),
                    border_width=1
                )
            except:
                pass
        
        self.message_entry.bind("<FocusIn>", on_focus_in)
        self.message_entry.bind("<FocusOut>", on_focus_out)
    
    def show_welcome_screen(self):
        """显示现代化欢迎界面"""
        # 清除现有内容
        for widget in self.message_scrollable.winfo_children():
            widget.destroy()
        
        # 配置滚动区域的网格
        self.message_scrollable.grid_rowconfigure(0, weight=1)
        self.message_scrollable.grid_columnconfigure(0, weight=1)
        
        # 现代化欢迎内容容器
        welcome_container = ctk.CTkFrame(
            self.message_scrollable,
            fg_color="transparent"
        )
        welcome_container.grid(row=0, column=0, sticky="")
        
        # 现代化欢迎图标
        welcome_icon = ctk.CTkLabel(
            welcome_container,
            text="💬",
            font=get_font("4xl"),
            text_color=get_color("primary")
        )
        welcome_icon.pack(pady=(0, theme.SPACING["xl"]))
        
        # 现代化欢迎标题
        welcome_title = ctk.CTkLabel(
            welcome_container,
            text=language_manager.t("welcome_title"),
            font=get_font("2xl", "bold"),
            text_color=get_color("gray_800")
        )
        welcome_title.pack(pady=(0, theme.SPACING["md"]))
        
        # 现代化欢迎说明
        welcome_desc = ctk.CTkLabel(
            welcome_container,
            text=language_manager.t("welcome_desc"),
            font=get_font("base"),
            text_color=get_color("gray_500"),
            justify="center"
        )
        welcome_desc.pack()
    
    def switch_contact(self, contact: Dict):
        """切换到指定联系人的聊天"""
        self.current_contact = contact
        
        # 更新头部信息
        self.update_contact_header(contact)
        
        # 加载聊天记录
        self.load_chat_history(contact)
        
        # 启用输入区域
        self.set_input_enabled(True)
        
        print(f"💬 切换到与 {contact['nickname']} 的聊天")
    
    def update_contact_header(self, contact: Dict):
        """更新联系人头部信息"""
        # 更新头像
        avatar_text = contact["nickname"][0].upper() if contact["nickname"] else "?"
        self.avatar_label.configure(text=avatar_text)
        
        # 更新姓名
        self.contact_name.configure(text=contact["nickname"])
        
        # 更新状态
        status_text = language_manager.t("status_online") if contact["online"] else language_manager.t("status_offline")
        status_color = "green" if contact["online"] else "gray60"
        self.contact_status.configure(
            text=f"{contact['email']} • {status_text}",
            text_color=status_color
        )
    
    def load_chat_history(self, contact: Dict):
        """加载聊天历史记录"""
        # 清除现有消息
        for widget in self.message_scrollable.winfo_children():
            widget.destroy()
        
        # 尝试从数据库加载消息
        try:
            if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'database_manager'):
                db_messages = self.parent.app.database_manager.get_messages(contact["email"])
                
                if db_messages:
                    # 转换数据库格式到UI格式，按时间排序
                    self.messages = []
                    for msg in db_messages:
                        ui_message = {
                            "id": msg.get("id", ""),  # 添加消息ID用于去重
                            "sender": msg.get("sender_email", ""),
                            "content": msg.get("content", ""),
                            "timestamp": self.format_db_timestamp(msg.get("sent_at")),
                            "is_sent": msg.get("is_sent", False)
                        }
                        self.messages.append(ui_message)
                    
                    # 按时间排序确保消息顺序正确
                    self.messages.sort(key=lambda x: x.get("id", 0))
                    
                    print(f"📜 从数据库加载了 {len(db_messages)} 条消息")
                    self.display_messages()
                    # 加载完成后自动滚动到底部显示最新消息
                    self.scroll_to_bottom()
                    return
        except Exception as e:
            print(f"❌ 从数据库加载消息失败: {e}")
        
        # 如果数据库没有消息，添加一些示例消息用于演示
        self.messages = self.create_demo_messages(contact)
        print(f"📭 与 {contact['nickname']} 的聊天记录为空，显示演示消息")
        
        # 显示消息列表
        self.display_messages()
        # 滚动到底部
        self.scroll_to_bottom()
    
    def create_demo_messages(self, contact: Dict):
        """创建演示消息"""
        return [
            {
                "id": 1,
                "sender": contact["email"],
                "content": f"你好！我是 {contact['nickname']}",
                "timestamp": "09:30",
                "is_sent": False
            },
            {
                "id": 2,
                "sender": "me@example.com",
                "content": "你好！很高兴认识你！",
                "timestamp": "09:32",
                "is_sent": True
            },
            {
                "id": 3,
                "sender": contact["email"],
                "content": contact.get("last_message", "这是一条示例消息"),
                "timestamp": contact.get("last_time", "10:00"),
                "is_sent": False
            }
        ]
    
    def display_messages(self):
        """显示消息列表"""
        for i, message in enumerate(self.messages):
            self.add_message_bubble(message, i)
    
    def add_message_bubble(self, message: Dict, row: int):
        """添加现代化消息气泡"""
        # 使用新的MessageContainer组件
        message_container = MessageContainer(self.message_scrollable, message)
        message_container.grid(
            row=row, 
            column=0, 
            sticky="ew", 
            padx=theme.SPACING["md"], 
            pady=theme.SPACING["sm"]
        )
    
    def add_new_message(self, message: Dict):
        """添加新消息（用于实时接收）"""
        # 检查消息是否已存在（防重复）
        message_id = message.get("id", "")
        if message_id and any(msg.get("id") == message_id for msg in self.messages):
            print(f"⚠️ 消息已存在，跳过重复添加: {message_id}")
            return
        
        # 添加到消息列表
        self.messages.append(message)
        
        # 显示新消息气泡
        self.add_message_bubble(message, len(self.messages) - 1)
        
        # 平滑滚动到底部显示新消息
        self.scroll_to_bottom_smooth()
        
        print(f"📬 已添加新消息: {message.get('content', '')[:30]}...")
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.after(100, lambda: self.message_scrollable._parent_canvas.yview_moveto(1.0))
    
    def scroll_to_bottom_smooth(self):
        """平滑滚动到底部"""
        def smooth_scroll():
            try:
                canvas = self.message_scrollable._parent_canvas
                current_pos = canvas.canvasy(0) / canvas.bbox("all")[3]
                target_pos = 1.0
                
                # 如果已经在底部附近，直接跳转
                if abs(current_pos - target_pos) < 0.1:
                    canvas.yview_moveto(1.0)
                    return
                
                # 平滑滚动动画
                step = 0.15
                next_pos = current_pos + (target_pos - current_pos) * step
                canvas.yview_moveto(next_pos)
                
                # 继续动画或完成
                if abs(next_pos - target_pos) > 0.01:
                    self.after(16, smooth_scroll)  # ~60fps
                else:
                    canvas.yview_moveto(1.0)
            except:
                # fallback到普通滚动
                self.scroll_to_bottom()
        
        self.after(50, smooth_scroll)
    
    def send_message(self):
        """发送消息"""
        if not self.current_contact:
            return
        
        # 获取消息内容
        content = self.message_entry.get("1.0", "end-1c").strip()
        if not content:
            return
        
        # 添加发送动画效果
        self.add_send_animation()
        
        # 生成唯一消息ID
        import time
        message_id = f"msg_{int(time.time() * 1000)}"
        
        # 创建消息对象
        message = {
            "id": message_id,
            "sender": "me@example.com",
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M"),
            "is_sent": True,
            "status": "sending"  # 添加状态字段
        }
        
        # 添加到消息列表并显示
        self.add_new_message(message)
        
        # 清空输入框
        self.message_entry.delete("1.0", "end")
        
        # 保存消息到数据库
        if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'database_manager'):
            try:
                self.parent.app.database_manager.add_message(
                    contact_email=self.current_contact["email"],
                    sender_email="me@example.com",
                    receiver_email=self.current_contact["email"],
                    content=content,
                    is_sent=True
                )
            except Exception as e:
                print(f"❌ 保存消息到数据库失败: {e}")
        
        # 更新聊天列表中的最后消息
        if hasattr(self.parent, 'chat_list'):
            self.parent.chat_list.update_last_message(
                self.current_contact["email"], 
                content, 
                datetime.now().strftime("%H:%M")
            )
        
        # 发送真实邮件
        if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'send_message'):
            try:
                success = self.parent.app.send_message(self.current_contact["email"], content)
                if success:
                    print(f"📤 邮件已发送给 {self.current_contact['nickname']}: {content}")
                    # 更新消息状态为已发送
                    self.update_message_status(message_id, "sent")
                    self.update_message_status_in_ui(message_id, "sent")
                else:
                    print(f"❌ 邮件发送失败")
                    self.update_message_status(message_id, "failed")
                    self.update_message_status_in_ui(message_id, "failed")
            except Exception as e:
                print(f"❌ 发送邮件出错: {e}")
                self.update_message_status(message_id, "failed")
                self.update_message_status_in_ui(message_id, "failed")
        else:
            print(f"📤 模拟发送消息给 {self.current_contact['nickname']}: {content}")
            # 模拟发送成功
            self.after(1000, lambda: self.update_message_status(message_id, "sent"))
            self.after(1000, lambda: self.update_message_status_in_ui(message_id, "sent"))
            # 模拟自动回复（仅在邮件功能不可用时）
            self.simulate_reply()
    
    def update_message_status(self, message_id: str, status: str):
        """更新消息状态"""
        # 在实际项目中，这里可以更新消息的发送状态图标
        # 例如：发送中(○)、已发送(✓)、已读(✓✓)、失败(❌)
        print(f"📋 消息 {message_id} 状态更新为: {status}")
    
    def simulate_reply(self):
        """模拟自动回复（仅用于测试）"""
        if not self.current_contact:
            return
        
        # 显示打字指示器
        self.show_typing_indicator(self.current_contact["nickname"])
        
        # 延迟回复（模拟打字时间）
        reply_delay = 3000  # 3秒
        self.after(reply_delay, self._add_auto_reply)
    
    def _add_auto_reply(self):
        """添加自动回复消息"""
        # 隐藏打字指示器
        self.hide_typing_indicator()
        
        replies = language_manager.t("auto_replies")
        
        import random, time
        reply_content = random.choice(replies)
        
        # 生成唯一回复消息ID
        message_id = f"reply_{int(time.time() * 1000)}"
        
        message = {
            "id": message_id,
            "sender": self.current_contact["email"],
            "content": reply_content,
            "timestamp": datetime.now().strftime("%H:%M"),
            "is_sent": False
        }
        
        # 使用新的添加消息方法
        self.add_new_message(message)
        
        # 保存自动回复到数据库
        if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'database_manager'):
            try:
                self.parent.app.database_manager.add_message(
                    contact_email=self.current_contact["email"],
                    sender_email=self.current_contact["email"],
                    receiver_email="me@example.com",
                    content=reply_content,
                    is_sent=False
                )
            except Exception as e:
                print(f"❌ 保存自动回复到数据库失败: {e}")
        
        # 更新聊天列表中的最后消息（自动回复）
        if hasattr(self.parent, 'chat_list'):
            self.parent.chat_list.update_last_message(
                self.current_contact["email"], 
                reply_content, 
                datetime.now().strftime("%H:%M")
            )
    
    def on_enter_key(self, event):
        """处理Enter键事件"""
        # Shift+Enter 或 Ctrl+Enter 换行，单独Enter发送
        if event.state & 0x1:  # Shift键被按下
            return  # 允许换行
        elif event.state & 0x4:  # Ctrl键被按下
            return  # 允许换行
        else:
            # 单独Enter键发送消息
            self.send_message()
            return "break"  # 阻止默认行为
    
    def on_ctrl_enter(self, event):
        """处理Ctrl+Enter换行"""
        return  # 允许换行
    
    def set_input_enabled(self, enabled: bool):
        """设置输入区域是否可用"""
        state = "normal" if enabled else "disabled"
        
        # 只控制发送按钮的状态
        self.send_btn.configure(state=state)
        
        if not enabled:
            self.message_entry.delete("1.0", "end")
            self.message_entry.insert("1.0", language_manager.t("please_select_contact"))
        else:
            placeholder = language_manager.t("please_select_contact")
            if placeholder in self.message_entry.get("1.0", "end"):
                self.message_entry.delete("1.0", "end")
    
    def attach_file(self):
        """附件功能 - 已移除"""
        pass
    
    def show_emoji_picker(self):
        """显示表情选择器 - 已移除"""
        pass
    
    def show_more_options(self):
        """显示更多选项 - 已移除"""
        pass
    
    def clear_chat(self):
        """清空聊天记录"""
        self.messages.clear()
        for widget in self.message_scrollable.winfo_children():
            widget.destroy()
    
    def format_db_timestamp(self, timestamp):
        """格式化数据库时间戳"""
        if not timestamp:
            return datetime.now().strftime("%H:%M")
        
        try:
            from datetime import datetime
            if isinstance(timestamp, str):
                # 尝试解析时间字符串
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    return timestamp
            else:
                dt = timestamp
            
            return dt.strftime("%H:%M")
        except Exception:
            return datetime.now().strftime("%H:%M")
    
    def get_current_contact(self):
        """获取当前选中的联系人"""
        return self.current_contact
    
    def update_language(self):
        """更新组件语言"""
        # 更新发送按钮
        self.send_btn.configure(text=language_manager.t("send"))
        
        # 如果没有选中联系人，更新联系人名称
        if not self.current_contact:
            self.contact_name.configure(text=language_manager.t("select_contact_to_start"))
            
            # 重新显示欢迎界面
            self.show_welcome_screen()
        else:
            # 如果有选中联系人，重新加载聊天记录
            self.load_chat_history(self.current_contact)
            # 更新联系人状态文本
            self.update_contact_header(self.current_contact)
    
    def get_current_contact(self) -> Optional[Dict]:
        """获取当前聊天联系人"""
        return self.current_contact 

    def show_typing_indicator(self, contact_name: str):
        """显示打字指示器"""
        if self.typing_indicator:
            return  # 已经在显示
        
        # 创建打字指示器
        typing_frame = ctk.CTkFrame(
            self.message_scrollable,
            fg_color=get_color("gray_100"),
            corner_radius=theme.RADIUS["lg"]
        )
        typing_frame.grid(
            row=len(self.messages), 
            column=0, 
            sticky="w", 
            padx=(theme.SPACING["md"], theme.SPACING["4xl"]), 
            pady=theme.SPACING["sm"]
        )
        
        # 打字动画文本
        typing_label = ctk.CTkLabel(
            typing_frame,
            text=f"{contact_name} 正在输入...",
            font=get_font("sm"),
            text_color=get_color("gray_600")
        )
        typing_label.pack(padx=theme.SPACING["md"], pady=theme.SPACING["sm"])
        
        self.typing_indicator = typing_frame
        
        # 自动滚动到底部
        self.scroll_to_bottom_smooth()
        
        # 添加打字动画效果
        self.animate_typing_dots(typing_label)
    
    def hide_typing_indicator(self):
        """隐藏打字指示器"""
        if self.typing_indicator:
            self.typing_indicator.destroy()
            self.typing_indicator = None
    
    def animate_typing_dots(self, label: ctk.CTkLabel):
        """打字指示器动画"""
        if not self.typing_indicator:
            return
        
        current_text = label.cget("text")
        base_text = current_text.split(" 正在输入")[0] + " 正在输入"
        
        dots_count = current_text.count(".")
        if dots_count >= 3:
            new_text = base_text
        else:
            new_text = current_text + "."
        
        label.configure(text=new_text)
        
        # 继续动画
        if self.typing_indicator:
            self.after(500, lambda: self.animate_typing_dots(label))
    
    def add_message_with_time_group(self, message: Dict, row: int):
        """添加消息并处理时间分组"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 如果是新的一天，添加日期分隔符
        if self.last_message_date != current_date:
            self.add_date_separator(current_date, row)
            row += 1
            self.last_message_date = current_date
        
        # 添加消息气泡
        message_container = MessageContainer(self.message_scrollable, message)
        message_container.grid(
            row=row, 
            column=0, 
            sticky="ew", 
            padx=theme.SPACING["md"], 
            pady=theme.SPACING["sm"]
        )
        
        return row + 1
    
    def add_date_separator(self, date_str: str, row: int):
        """添加日期分隔符"""
        # 格式化日期显示
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.now().date()
            
            if date_obj.date() == today:
                display_text = "今天"
            elif (today - date_obj.date()).days == 1:
                display_text = "昨天"
            else:
                display_text = date_obj.strftime("%m月%d日")
        except:
            display_text = date_str
        
        # 创建日期分隔符
        separator_frame = ctk.CTkFrame(
            self.message_scrollable,
            fg_color="transparent",
            height=40
        )
        separator_frame.grid(row=row, column=0, sticky="ew", pady=theme.SPACING["lg"])
        separator_frame.grid_propagate(False)
        
        # 日期标签
        date_label = ctk.CTkLabel(
            separator_frame,
            text=display_text,
            font=get_font("xs"),
            text_color=get_color("gray_500"),
            fg_color=get_color("gray_100"),
            corner_radius=theme.RADIUS["full"]
        )
        date_label.pack(pady=theme.SPACING["sm"])
    
    def add_message_status_indicator(self, message: Dict, container):
        """添加消息状态指示器"""
        if not message.get("is_sent", False):
            return  # 只为发送的消息添加状态
        
        status_frame = ctk.CTkFrame(container, fg_color="transparent")
        status_frame.pack(side="bottom", anchor="e", padx=theme.SPACING["sm"])
        
        # 根据消息状态显示不同图标
        message_id = message.get("id", "")
        if "failed" in message_id:
            status_icon = "❌"
            status_color = get_color("danger")
        elif "sent" in message_id:
            status_icon = "✓"
            status_color = get_color("success")
        else:
            status_icon = "○"  # 发送中
            status_color = get_color("gray_400")
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_icon,
            font=get_font("xs"),
            text_color=status_color
        )
        status_label.pack(side="right")
    
    def update_message_status_in_ui(self, message_id: str, status: str):
        """在UI中更新消息状态"""
        # 遍历消息组件，找到对应的消息并更新状态
        for widget in self.message_scrollable.winfo_children():
            if hasattr(widget, 'message_id') and widget.message_id == message_id:
                # 更新状态指示器
                self.refresh_message_status(widget, status)
                break
    
    def refresh_message_status(self, message_widget, status: str):
        """刷新消息状态指示器"""
        # 这里可以更新消息组件的状态显示
        # 在实际项目中会根据具体的消息组件结构来实现
        print(f"🔄 更新消息状态: {status}")
    
    def add_send_animation(self):
        """添加发送消息动画效果"""
        # 发送按钮动画
        original_color = self.send_btn.cget("fg_color")
        
        # 点击动画
        self.send_btn.configure(fg_color=get_color("primary_dark"))
        self.after(100, lambda: self.send_btn.configure(fg_color=original_color))
        
        # 输入框动画
        self.message_entry.configure(border_color=get_color("success"))
        self.after(200, lambda: self.message_entry.configure(border_color=get_color("gray_300")))
    
    def show_message_preview(self, content: str):
        """显示消息预览效果"""
        # 为长消息显示预览
        if len(content) > 100:
            preview = content[:100] + "..."
            # 可以在这里添加展开/收起功能
            return preview
        return content 