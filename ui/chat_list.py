#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 聊天列表组件

显示联系人列表，支持搜索和选择功能
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Optional, Callable
# 导入语言管理器和主题配置
from src.language_manager import language_manager
from ui.theme_config import theme, get_color, get_font
from ui.enhanced_components import SelectableFrame, ModernEntry, StatusIndicator


class ChatList(ctk.CTkFrame):
    """聊天列表组件"""
    
    def __init__(self, parent):
        """初始化现代化聊天列表"""
        super().__init__(
            parent, 
            width=theme.SIZES["chat_list_width"], 
            corner_radius=0,
            fg_color=get_color("white"),
            border_width=1,
            border_color=get_color("gray_200")
        )
        
        self.parent = parent
        self.selected_contact = None
        self.contacts = []  # 联系人列表
        self.contact_widgets = {}  # 存储联系人UI组件的映射
        
        # 固定宽度
        self.grid_propagate(False)
        
        # 创建界面元素
        self.create_widgets()
        
        # 添加示例数据
        self.add_sample_contacts()
        
        print("👥 现代化聊天列表初始化完成")
    
    def create_widgets(self):
        """创建界面元素"""
        # 配置网格权重
        self.grid_rowconfigure(1, weight=1)  # 让联系人列表可伸缩
        self.grid_columnconfigure(0, weight=1)
        
        # 顶部搜索区域
        self.create_search_area()
        
        # 联系人列表区域
        self.create_contact_list()
    
    def create_search_area(self):
        """创建现代化搜索区域"""
        # 现代化搜索框容器
        search_frame = ctk.CTkFrame(
            self, 
            height=70, 
            corner_radius=0,
            fg_color=get_color("gray_50"),
            border_width=1,
            border_color=get_color("gray_200")
        )
        search_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        search_frame.grid_propagate(False)
        search_frame.grid_columnconfigure(0, weight=1)
        
        # 现代化搜索输入框
        self.search_entry = ModernEntry(
            search_frame,
            placeholder_text=f"{theme.ICONS['search']} {language_manager.t('search_contacts')}",
            height=40,
            corner_radius=theme.RADIUS["full"],
            fg_color=get_color("white"),
            placeholder_text_color=get_color("gray_400")
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=theme.SPACING["lg"], pady=theme.SPACING["md"])
        
        # 绑定搜索事件
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # 添加搜索框聚焦效果
        self.add_search_focus_effect()
    
    def create_contact_list(self):
        """创建现代化联系人列表"""
        # 现代化滚动框架
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_button_color=get_color("gray_300"),
            scrollbar_button_hover_color=get_color("gray_400")
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        print("📜 现代化联系人列表区域创建完成")
        
    def add_search_focus_effect(self):
        """为搜索框添加聚焦效果"""
        def on_focus_in(event):
            self.search_entry.configure(
                border_color=get_color("primary"),
                border_width=2
            )
        
        def on_focus_out(event):
            self.search_entry.configure(
                border_color=get_color("gray_300"),
                border_width=1
            )
        
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
    
    def add_sample_contacts(self):
        """加载联系人数据"""
        # 尝试从数据库加载联系人
        if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'database_manager'):
            try:
                db_contacts = self.parent.app.database_manager.get_contacts()
                
                # 清空现有联系人列表以避免重复
                self.contacts.clear()
                
                for contact in db_contacts:
                    # 转换数据库格式到UI格式
                    ui_contact = {
                        "email": contact["email"],
                        "nickname": contact["nickname"],
                        "last_message": contact["last_message_content"] or "",
                        "last_time": self.format_time(contact["last_message_time"]) if contact["last_message_time"] else "",
                        "unread_count": contact["unread_count"],
                        "online": contact["is_online"]
                    }
                    self.contacts.append(ui_contact)
                
                # 刷新UI显示
                self.refresh_contact_list()
                
                if db_contacts:
                    print(f"📋 从数据库加载了 {len(db_contacts)} 个联系人")
                else:
                    print(f"📋 {language_manager.t('no_contacts_please_add')}")
            except Exception as e:
                print(f"❌ 从数据库加载联系人失败: {e}")
                # 添加一些示例联系人用于演示
                self.add_demo_contacts()
        else:
            print("📋 数据库不可用，添加演示联系人") 
            self.add_demo_contacts()
    
    def add_contact(self, contact_data: Dict):
        """添加联系人到列表"""
        # 检查是否已存在该联系人
        for i, existing_contact in enumerate(self.contacts):
            if existing_contact["email"] == contact_data["email"]:
                # 更新现有联系人信息
                self.contacts[i] = contact_data
                self.refresh_contact_list()
                return
        
        # 如果不存在，则添加新联系人
        self.contacts.append(contact_data)
        self.refresh_contact_list()
    
    def update_contact_message(self, email: str, last_message: str, unread_count: int = 0):
        """更新联系人的最后消息和未读计数"""
        try:
            # 查找并更新联系人信息
            for i, contact in enumerate(self.contacts):
                if contact["email"] == email:
                    self.contacts[i]["last_message"] = last_message
                    self.contacts[i]["unread_count"] = unread_count
                    # 设置当前时间
                    from datetime import datetime
                    current_time = datetime.now()
                    self.contacts[i]["last_time"] = self.format_time(current_time)
                    
                    # 安全地更新UI
                    self.safe_refresh_contact_list()
                    return True
            
            # 如果联系人不存在，从数据库重新加载
            print(f"⚠️ 联系人 {email} 不在列表中，重新加载联系人列表")
            self.add_sample_contacts()
            return False
            
        except Exception as e:
            print(f"❌ 更新联系人消息失败: {e}")
            return False
    
    def safe_refresh_contact_list(self):
        """安全地刷新联系人列表，避免GUI错误"""
        try:
            # 使用after方法确保在主线程中执行UI更新
            self.after(0, self.refresh_contact_list)
        except Exception as e:
            print(f"❌ 安全刷新联系人列表失败: {e}")

    def refresh_contact_list(self, filter_text: str = ""):
        """刷新联系人列表显示"""
        try:
            # 清除现有联系人显示
            for widget in self.scrollable_frame.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass  # 忽略已经被销毁的widget
            
            # 清除联系人组件映射
            self.contact_widgets.clear()
            
            # 过滤联系人
            filtered_contacts = self.filter_contacts(filter_text)
            
            if not filtered_contacts:
                # 显示空状态
                empty_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=language_manager.t("no_contacts"),
                    font=get_font("base"),
                    text_color=get_color("gray_500"),
                    justify="center"
                )
                empty_label.grid(row=0, column=0, pady=50)
                return
            
            # 显示联系人
            for i, contact in enumerate(filtered_contacts):
                try:
                    contact_item = self.create_contact_item(contact, i)
                    contact_item.grid(row=i, column=0, sticky="ew", padx=theme.SPACING["sm"], pady=theme.SPACING["xs"])
                    # 保存联系人组件映射
                    self.contact_widgets[contact["email"]] = contact_item
                except Exception as e:
                    print(f"❌ 创建联系人项失败: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ 刷新联系人列表失败: {e}")
    
    def filter_contacts(self, filter_text: str) -> List[Dict]:
        """根据搜索文本过滤联系人"""
        if not filter_text:
            return self.contacts
        
        filter_text = filter_text.lower()
        filtered = []
        
        for contact in self.contacts:
            # 搜索昵称和邮箱
            if (filter_text in contact["nickname"].lower() or 
                filter_text in contact["email"].lower()):
                filtered.append(contact)
        
        return filtered
    
    def create_contact_item(self, contact: Dict, index: int) -> ctk.CTkFrame:
        """创建现代化单个联系人条目"""
        # 现代化联系人条目框架 - 使用增强组件
        item_frame = SelectableFrame(
            self.scrollable_frame,
            height=76,
            corner_radius=theme.RADIUS["md"],
            fg_color="transparent",
            on_click=lambda: self.select_contact(contact)
        )
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # 现代化头像区域 (左侧)
        avatar_size = theme.SIZES["avatar_lg"]
        avatar_frame = ctk.CTkFrame(
            item_frame, 
            width=avatar_size, 
            height=avatar_size, 
            corner_radius=avatar_size//2,
            fg_color=get_color("primary"),
            border_width=2,
            border_color=get_color("white")
        )
        avatar_frame.grid(row=0, column=0, padx=(theme.SPACING["md"], theme.SPACING["sm"]), pady=theme.SPACING["md"], sticky="nsew")
        avatar_frame.grid_propagate(False)
        
        # 现代化头像文字 (姓名首字母)
        avatar_text = contact["nickname"][0].upper() if contact["nickname"] else "?"
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=avatar_text,
            font=get_font("md", "bold"),
            text_color=get_color("white")
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 现代化信息区域 (中间)
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(0, theme.SPACING["sm"]), pady=theme.SPACING["md"])
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 现代化联系人姓名和时间
        name_time_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_time_frame.grid(row=0, column=0, sticky="ew", pady=(0, theme.SPACING["xs"]))
        name_time_frame.grid_columnconfigure(0, weight=1)
        
        # 现代化姓名
        name_label = ctk.CTkLabel(
            name_time_frame,
            text=contact["nickname"],
            font=get_font("contact_name", "bold"),
            text_color=get_color("gray_800"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w")
        
        # 现代化时间
        time_label = ctk.CTkLabel(
            name_time_frame,
            text=contact["last_time"],
            font=get_font("xs"),
            text_color=get_color("gray_500"),
            anchor="e"
        )
        time_label.grid(row=0, column=1, sticky="e", padx=(theme.SPACING["sm"], 0))
        
        # 现代化最后消息和未读计数
        message_badge_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        message_badge_frame.grid(row=1, column=0, sticky="ew")
        message_badge_frame.grid_columnconfigure(0, weight=1)
        
        # 现代化最后消息
        message_text = contact["last_message"]
        if len(message_text) > 25:  # 限制消息长度
            message_text = message_text[:25] + "..."
        
        message_label = ctk.CTkLabel(
            message_badge_frame,
            text=message_text,
            font=get_font("last_message"),
            text_color=get_color("gray_600"),
            anchor="w"
        )
        message_label.grid(row=0, column=0, sticky="w")
        
        # 现代化未读计数徽章
        unread_count = contact.get("unread_count", 0)
        if unread_count > 0:
            badge_text = str(unread_count) if unread_count < 100 else "99+"
            unread_badge = ctk.CTkLabel(
                message_badge_frame,
                text=badge_text,
                font=get_font("xs", "bold"),
                text_color=get_color("white"),
                fg_color=get_color("danger"),
                corner_radius=10,
                width=20,
                height=20
            )
            unread_badge.grid(row=0, column=1, sticky="e", padx=(theme.SPACING["sm"], 0))
        
        # 现代化在线状态指示器
        if contact["online"]:
            status_indicator = StatusIndicator(
                item_frame,
                status="online"
            )
            status_indicator.grid(row=0, column=2, sticky="ne", padx=(0, theme.SPACING["md"]), pady=theme.SPACING["md"])
        
        # 保存组件引用
        item_frame.contact_data = contact
        item_frame.contact_index = index
        
        # 使用SelectableFrame的新方法绑定所有子组件
        item_frame.bind_all_children()
        
        return item_frame
    
    def bind_contact_click(self, widget: ctk.CTkFrame, contact: Dict):
        """绑定联系人点击事件"""
        def on_click(event=None):
            print(f"🖱️ 点击联系人: {contact['nickname']}")
            self.select_contact(contact)
            return "break"  # 阻止事件传播
        
        # 为主widget绑定点击事件
        widget.bind("<Button-1>", on_click)
        widget.configure(cursor="hand2")
        
        # 递归绑定所有子组件
        def bind_recursive(w):
            try:
                w.bind("<Button-1>", on_click)
                if hasattr(w, 'configure'):
                    w.configure(cursor="hand2")
            except:
                pass
            
            for child in w.winfo_children():
                bind_recursive(child)
        
        bind_recursive(widget)
    
    def select_contact(self, contact: Dict):
        """选择联系人"""
        self.selected_contact = contact
        
        # 标记消息为已读（清除小红点）
        self.mark_as_read(contact["email"])
        
        # 更新选中状态显示
        self.update_selection_display()
        
        # 通知父组件切换聊天界面
        if hasattr(self.parent, 'chat_interface'):
            self.parent.chat_interface.switch_contact(contact)
        
        print(f"👤 选择联系人: {contact['nickname']} ({contact['email']})")
    
    def update_selection_display(self):
        """更新现代化选中状态显示"""
        # 重置所有联系人的选中状态
        for email, widget in self.contact_widgets.items():
            try:
                if hasattr(widget, 'set_selected'):
                    widget.set_selected(False)
                else:
                    widget.configure(fg_color="transparent")
            except:
                pass
        
        # 高亮选中的联系人
        if self.selected_contact and self.selected_contact["email"] in self.contact_widgets:
            try:
                selected_widget = self.contact_widgets[self.selected_contact["email"]]
                if hasattr(selected_widget, 'set_selected'):
                    selected_widget.set_selected(True)
                else:
                    selected_widget.configure(fg_color=get_color("primary", 0.15))
            except:
                pass
    
    def on_search_change(self, event=None):
        """搜索框内容改变事件"""
        search_text = self.search_entry.get()
        self.refresh_contact_list(search_text)
        print(f"🔍 搜索: {search_text}")
    
    def update_contact_status(self, email: str, status: str):
        """更新联系人状态"""
        for contact in self.contacts:
            if contact["email"] == email:
                contact["online"] = (status == "online")
                break
        
        self.refresh_contact_list(self.search_entry.get())
    
    def update_last_message(self, email: str, message: str, time: str):
        """更新联系人最后消息"""
        for contact in self.contacts:
            if contact["email"] == email:
                contact["last_message"] = message
                contact["last_time"] = time
                break
        
        self.refresh_contact_list(self.search_entry.get())
    
    def format_time(self, timestamp):
        """格式化时间显示"""
        if not timestamp:
            return ""
        
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
            
            # 使用工具函数格式化时间
            from src.utils import format_time
            return format_time(dt)
        except Exception:
            return str(timestamp)
    
    def mark_as_read(self, email: str):
        """标记消息为已读"""
        # 更新本地数据
        for contact in self.contacts:
            if contact["email"] == email:
                contact["unread_count"] = 0
                break
        
        # 更新数据库
        if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'database_manager'):
            try:
                self.parent.app.database_manager.mark_messages_as_read(email)
            except Exception as e:
                print(f"❌ 数据库标记已读失败: {e}")
        
        self.refresh_contact_list(self.search_entry.get())
    
    def update_language(self):
        """更新组件语言"""
        # 更新搜索框占位符
        self.search_entry.configure(placeholder_text=language_manager.t("search_contacts"))
        
        # 重新加载联系人数据（不使用示例数据）
        self.contacts.clear()
        self.add_sample_contacts()
        
        # 刷新显示
        self.refresh_contact_list(self.search_entry.get())
        
        # 恢复选中状态显示
        self.update_selection_display()
    
    def get_selected_contact(self) -> Optional[Dict]:
        """获取当前选中的联系人"""
        return self.selected_contact 