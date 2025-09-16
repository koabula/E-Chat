#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 增强UI组件

现代化的自定义组件，提供更好的用户体验
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable, Any
from ui.theme_config import theme, get_color, get_font


class SelectableMessageText(ctk.CTkTextbox):
    """可选中复制的聊天消息文本组件"""
    
    def __init__(self, parent, text: str = "", **kwargs):
        """
        初始化可选中的消息文本
        
        Args:
            parent: 父容器
            text: 显示的文本内容
        """
        # 设置默认样式 - 移除不支持透明度的属性
        default_kwargs = {
            "font": get_font("message"),
            "wrap": "word",
            "border_width": 0,
            "corner_radius": 0,
            "fg_color": "transparent",
            "activate_scrollbars": False
            # 移除scrollbar相关的透明度设置，因为某些版本不支持
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        # 插入文本内容
        if text:
            self.insert("0.0", text)
        
        # 设置为只读，但保持可选中复制
        self.configure(state="disabled")
        
        # 计算合适的高度
        self.auto_resize_height(text)
        
        # 绑定右键菜单
        self.bind("<Button-3>", self.show_context_menu)
    
    def auto_resize_height(self, text: str):
        """根据文本内容自动调整高度"""
        if not text:
            self.configure(height=30)
            return
        
        # 计算文本行数
        lines = text.count('\n') + 1
        char_width = 25  # 每行大约字符数 (根据字体大小估算)
        wrapped_lines = max(lines, len(text) // char_width + 1)
        
        # 计算高度 (每行约24px，最小30px，最大200px)
        line_height = 24
        min_height = 30
        max_height = 200
        
        text_height = min(max(wrapped_lines * line_height, min_height), max_height)
        self.configure(height=text_height)
    
    def show_context_menu(self, event):
        """显示右键上下文菜单"""
        context_menu = tk.Menu(self, tearoff=0)
        
        # 添加复制选项
        context_menu.add_command(
            label="复制",
            command=self.copy_selected_text
        )
        
        # 添加全选选项
        context_menu.add_command(
            label="全选",
            command=self.select_all_text
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass
        finally:
            context_menu.grab_release()
    
    def copy_selected_text(self):
        """复制选中的文本到剪贴板"""
        try:
            # 临时启用编辑状态以获取选中的文本
            self.configure(state="normal")
            
            # 获取选中的文本
            try:
                selected_text = self.selection_get()
                if selected_text:
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                    print(f"📋 已复制文本: {selected_text[:50]}...")
                else:
                    # 如果没有选中文本，复制全部内容
                    all_text = self.get("0.0", "end-1c")
                    if all_text:
                        self.clipboard_clear()
                        self.clipboard_append(all_text)
                        print(f"📋 已复制全部文本: {all_text[:50]}...")
            except tk.TclError:
                # 如果没有选中文本，复制全部内容
                all_text = self.get("0.0", "end-1c")
                if all_text:
                    self.clipboard_clear()
                    self.clipboard_append(all_text)
                    print(f"📋 已复制全部文本: {all_text[:50]}...")
            
            # 恢复只读状态
            self.configure(state="disabled")
        except Exception as e:
            print(f"❌ 复制失败: {e}")
    
    def select_all_text(self):
        """选中所有文本"""
        try:
            self.configure(state="normal")
            self.tag_add("sel", "0.0", "end-1c")
            self.configure(state="disabled")
        except Exception as e:
            print(f"❌ 全选失败: {e}")
    
    def update_text(self, new_text: str):
        """更新文本内容"""
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.insert("0.0", new_text)
        self.configure(state="disabled")
        self.auto_resize_height(new_text)


class ModernEntry(ctk.CTkEntry):
    """现代化输入框组件"""
    
    def __init__(self, parent, placeholder_text: str = "", **kwargs):
        """现代化输入框初始化"""
        default_kwargs = {
            "font": get_font("base"),
            "corner_radius": theme.RADIUS["lg"],
            "border_width": 1,
            "border_color": get_color("gray_300"),
            "fg_color": get_color("white"),
            "placeholder_text": placeholder_text
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        # 绑定聚焦效果
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """聚焦时的效果"""
        self.configure(
            border_color=get_color("primary"),
            border_width=2
        )
    
    def _on_focus_out(self, event):
        """失去聚焦时的效果"""
        self.configure(
            border_color=get_color("gray_300"),
            border_width=1
        )


class HoverButton(ctk.CTkButton):
    """现代化悬停按钮"""
    
    def __init__(self, parent, **kwargs):
        """现代化按钮初始化"""
        default_kwargs = {
            "font": get_font("base"),
            "corner_radius": theme.RADIUS["lg"],
            "hover_color": get_color("primary_hover"),
            "fg_color": get_color("primary")
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)


class SelectableFrame(ctk.CTkFrame):
    """可选中的框架组件"""
    
    def __init__(self, parent, on_click: Optional[Callable] = None, **kwargs):
        """可选中框架初始化"""
        default_kwargs = {
            "corner_radius": theme.RADIUS["lg"],
            "fg_color": get_color("white")
            # 移除hover_color参数，CTkFrame不支持
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        self.on_click = on_click
        self.is_selected = False
        self.normal_color = get_color("white")
        self.hover_color = get_color("gray_50")
        self.selected_color = get_color("primary_light")
        
        # 绑定点击和悬停事件到主框架
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # 设置鼠标手型光标
        self.configure(cursor="hand2")
    
    def _on_click(self, event):
        """点击事件处理"""
        self.select()
        if self.on_click:
            self.on_click()
        return "break"  # 阻止事件继续传播
    
    def _on_enter(self, event):
        """鼠标进入事件"""
        if not self.is_selected:
            self.configure(fg_color=self.hover_color)
    
    def _on_leave(self, event):
        """鼠标离开事件"""
        if not self.is_selected:
            self.configure(fg_color=self.normal_color)
    
    def select(self):
        """选中状态"""
        self.is_selected = True
        self.configure(fg_color=self.selected_color)
    
    def deselect(self):
        """取消选中状态"""
        self.is_selected = False
        self.configure(fg_color=self.normal_color)
    
    def bind_all_children(self):
        """递归绑定所有子组件的点击事件"""
        def bind_recursive(widget):
            try:
                # 绑定点击事件
                widget.bind("<Button-1>", self._on_click)
                # 绑定悬停事件
                widget.bind("<Enter>", self._on_enter)
                widget.bind("<Leave>", self._on_leave)
                # 设置鼠标手型光标
                widget.configure(cursor="hand2")
                
                # 递归处理子组件
                for child in widget.winfo_children():
                    bind_recursive(child)
            except Exception:
                # 忽略无法绑定的组件
                pass
        
        # 延迟绑定，确保所有子组件都已创建
        self.after(1, lambda: bind_recursive(self))


class StatusIndicator(ctk.CTkFrame):
    """状态指示器组件"""
    
    def __init__(self, parent, status: str = "offline", **kwargs):
        """状态指示器初始化"""
        default_kwargs = {
            "width": 12,
            "height": 12,
            "corner_radius": 6
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        self.set_status(status)
    
    def set_status(self, status: str):
        """设置状态"""
        status_colors = {
            "online": get_color("online"),
            "offline": get_color("offline"),
            "busy": get_color("busy"),
            "away": get_color("away")
        }
        
        color = status_colors.get(status, get_color("offline"))
        self.configure(fg_color=color) 