#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 主题配置系统

定义现代化的UI设计规范，包括颜色、字体、间距、圆角等
"""

import customtkinter as ctk
from typing import Dict, Any

class ThemeConfig:
    """主题配置类"""
    
    # 主色调系统
    COLORS = {
        # 品牌主色
        "primary": "#4A90E2",        # 现代蓝
        "primary_hover": "#357ABD",   # 主色悬停
        "primary_dark": "#2E5B8B",    # 主色深色
        "primary_light": "#6BA3E8",   # 主色浅色
        "secondary": "#7B68EE",       # 优雅紫
        "secondary_hover": "#6A56DD", # 辅色悬停
        
        # 功能色彩
        "success": "#28A745",         # 成功绿
        "success_light": "#D4EDDA",   # 成功背景
        "warning": "#FFC107",         # 警告黄
        "warning_light": "#FFF3CD",   # 警告背景
        "danger": "#DC3545",          # 危险红
        "danger_light": "#F8D7DA",    # 危险背景
        "info": "#17A2B8",           # 信息青
        "info_light": "#D1ECF1",     # 信息背景
        
        # 中性色阶（更丰富的灰度系统）
        "white": "#FFFFFF",
        "gray_50": "#F9FAFB",        # 最浅灰
        "gray_100": "#F3F4F6",       # 浅灰背景
        "gray_200": "#E5E7EB",       # 边框灰
        "gray_300": "#D1D5DB",       # 输入框边框
        "gray_400": "#9CA3AF",       # 禁用文字
        "gray_500": "#6B7280",       # 次要文字
        "gray_600": "#4B5563",       # 正常文字
        "gray_700": "#374151",       # 重要文字
        "gray_800": "#1F2937",       # 标题文字
        "gray_900": "#111827",       # 最深文字
        "black": "#000000",
        
        # 透明度系列
        "overlay": "rgba(0, 0, 0, 0.5)",     # 遮罩
        "overlay_light": "rgba(0, 0, 0, 0.2)", # 浅遮罩
        "shadow": "rgba(0, 0, 0, 0.1)",      # 阴影
        "shadow_dark": "rgba(0, 0, 0, 0.25)", # 深阴影
        
        # 状态指示色
        "online": "#28A745",          # 在线绿
        "offline": "#6B7280",         # 离线灰
        "busy": "#FFC107",            # 忙碌黄
        "away": "#17A2B8",            # 离开青
        
        # 特殊效果色
        "gradient_start": "#4A90E2",  # 渐变起始
        "gradient_end": "#7B68EE",    # 渐变结束
    }
    
    # 字体系统
    FONTS = {
        # 字体族
        "family": ["Microsoft YaHei UI", "SF Pro Display", "Helvetica Neue", "Arial", "sans-serif"],
        
        # 字体大小 (现代化聊天软件标准)
        "xs": 10,      # 时间戳、状态信息
        "sm": 12,      # 小标签、辅助信息
        "base": 14,    # 基础文字、输入框
        "lg": 16,      # 聊天消息内容 (主要文字)
        "xl": 18,      # 重要文字、标题
        "2xl": 20,     # 大标题
        "3xl": 24,     # 更大标题
        "4xl": 28,     # 超大标题
        
        # 聊天专用字体大小
        "message": 16,      # 聊天消息文本
        "message_meta": 10, # 时间戳、状态等元信息
        "contact_name": 15, # 联系人名称
        "last_message": 13, # 最后消息预览
        
        # 字重
        "normal": "normal",
        "medium": "normal",  # CustomTkinter doesn't support medium
        "bold": "bold",
    }
    
    # 间距系统
    SPACING = {
        "xs": 4,       # 极小间距
        "sm": 8,       # 小间距
        "base": 12,    # 基础间距
        "md": 16,      # 中等间距
        "lg": 20,      # 大间距
        "xl": 24,      # 超大间距
        "2xl": 32,     # 更大间距
        "3xl": 48,     # 巨大间距
    }
    
    # 圆角系统
    RADIUS = {
        "none": 0,
        "sm": 6,       # 小圆角
        "base": 8,     # 基础圆角
        "md": 10,      # 中等圆角
        "lg": 12,      # 大圆角
        "xl": 16,      # 超大圆角
        "2xl": 20,     # 更大圆角
        "full": 9999,  # 完全圆形
    }
    
    # 组件尺寸
    SIZES = {
        # 按钮尺寸
        "button_sm": {"width": 80, "height": 32},
        "button_base": {"width": 120, "height": 36},
        "button_lg": {"width": 140, "height": 40},
        
        # 输入框尺寸
        "input_sm": {"height": 32},
        "input_base": {"height": 36},
        "input_lg": {"height": 40},
        
        # 侧边栏
        "sidebar_width": 70,
        "chat_list_width": 320,
        
        # 头像尺寸
        "avatar_sm": 32,
        "avatar_base": 40,
        "avatar_lg": 48,
        "avatar_xl": 64,
    }
    
    # 阴影系统
    SHADOWS = {
        "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "base": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    }
    
    # 图标映射 (使用Unicode符号替代Emoji)
    ICONS = {
        # 侧边栏图标
        "settings": "⚙",
        "add_contact": "➕",
        "theme_light": "☀",
        "theme_dark": "🌙",
        "notifications": "🔔",
        "help": "❓",
        "language": "🌐",
        
        # 状态图标
        "online": "🟢",
        "offline": "⚪",
        "away": "🟡",
        "busy": "🔴",
        "error": "⚠",
        
        # 功能图标
        "send": "➤",
        "attach": "📎",
        "emoji": "😊",
        "search": "🔍",
        "more": "⋯",
        "close": "✕",
        "check": "✓",
        "warning": "⚠",
        "info": "ℹ",
    }

# 全局主题实例
theme = ThemeConfig()

def get_color(color_name: str, opacity: float = 1.0) -> tuple:
    """
    获取主题颜色 - 支持亮色和暗色主题
    
    Args:
        color_name: 颜色名称
        opacity: 透明度 (0.0-1.0)
    
    Returns:
        tuple: (light_color, dark_color) - CustomTkinter会自动选择
    """
    try:
        import customtkinter as ctk
        
        # 获取当前外观模式
        current_mode = ctk.get_appearance_mode()
        
        # 为暗色模式定义专门的颜色映射
        dark_mode_colors = {
            # 主色调 - 在暗色模式下保持鲜明
            "primary": "#4A90E2",
            "primary_hover": "#357ABD", 
            "primary_dark": "#2E5B8B",
            "primary_light": "#6BA3E8",
            "secondary": "#7B68EE",
            "secondary_hover": "#6A56DD",
            
            # 功能色彩 - 暗色模式下保持可见性
            "success": "#28A745",
            "success_light": "#1E3A2E",
            "warning": "#FFC107", 
            "warning_light": "#3A3520",
            "danger": "#DC3545",
            "danger_light": "#3A1E20",
            "info": "#17A2B8",
            "info_light": "#1E353A",
            
            # 中性色阶 - 暗色模式反转
            "white": "#1F2937",        # 暗色背景
            "gray_50": "#374151",      # 暗色浅灰
            "gray_100": "#4B5563",     # 暗色组件背景
            "gray_200": "#6B7280",     # 暗色边框
            "gray_300": "#9CA3AF",     # 暗色输入框边框
            "gray_400": "#D1D5DB",     # 暗色禁用文字
            "gray_500": "#E5E7EB",     # 暗色次要文字
            "gray_600": "#F3F4F6",     # 暗色正常文字
            "gray_700": "#F9FAFB",     # 暗色重要文字
            "gray_800": "#FFFFFF",     # 暗色标题文字
            "gray_900": "#FFFFFF",     # 暗色最深文字
            "black": "#FFFFFF",        # 暗色模式下的白字
            
            # 状态指示色 - 保持一致
            "online": "#28A745",
            "offline": "#6B7280", 
            "busy": "#FFC107",
            "away": "#17A2B8",
        }
        
        # 如果是暗色模式，使用暗色映射
        if current_mode == "Dark" and color_name in dark_mode_colors:
            dark_color = dark_mode_colors[color_name]
            light_color = theme.COLORS.get(color_name, dark_color)
        else:
            # 亮色模式或未定义的颜色，使用原始配置
            light_color = theme.COLORS.get(color_name, theme.COLORS.get("gray_500", "#6B7280"))
            dark_color = dark_mode_colors.get(color_name, light_color)
        
        # 处理透明度
        if opacity < 1.0:
            def apply_opacity(hex_color: str, bg_color: str = "#FFFFFF") -> str:
                """将透明度应用到颜色"""
                try:
                    if not hex_color.startswith("#") or len(hex_color) != 7:
                        return hex_color
                    
                    # 解析颜色
                    r = int(hex_color[1:3], 16)
                    g = int(hex_color[3:5], 16) 
                    b = int(hex_color[5:7], 16)
                    
                    # 解析背景色
                    if bg_color.startswith("#") and len(bg_color) == 7:
                        br = int(bg_color[1:3], 16)
                        bg_val = int(bg_color[3:5], 16)
                        bb = int(bg_color[5:7], 16)
                    else:
                        br = bg_val = bb = 255 if current_mode == "Light" else 31  # 默认背景
                    
                    # 混合颜色
                    final_r = int(r * opacity + br * (1 - opacity))
                    final_g = int(g * opacity + bg_val * (1 - opacity))
                    final_b = int(b * opacity + bb * (1 - opacity))
                    
                    return f"#{final_r:02x}{final_g:02x}{final_b:02x}"
                except:
                    return hex_color
            
            # 为亮色和暗色模式分别应用透明度
            light_bg = "#FFFFFF"
            dark_bg = "#1F2937"
            light_color = apply_opacity(light_color, light_bg)
            dark_color = apply_opacity(dark_color, dark_bg)
        
        return (light_color, dark_color)
        
    except Exception as e:
        print(f"❌ 获取颜色失败: {e}, 使用默认颜色")
        # 回退到安全的默认颜色
        default_color = "#6B7280"
        return (default_color, default_color)

def get_font(size: str = "base", weight: str = "normal") -> tuple:
    """获取字体配置"""
    font_family = theme.FONTS["family"]  # 使用预定义的字体族
    font_size = theme.FONTS.get(size, theme.FONTS["base"])
    font_weight = theme.FONTS.get(weight, theme.FONTS["normal"])
    
    return (font_family, font_size, font_weight)

def apply_theme_to_widget(widget, widget_type: str, **custom_style):
    """为widget应用主题样式"""
    style_configs = {
        "button": {
            "corner_radius": theme.RADIUS["base"],
            "font": get_font("base", "normal"),
            "hover_color": theme.COLORS["primary_hover"],
        },
        "frame": {
            "corner_radius": theme.RADIUS["base"],
        },
        "entry": {
            "corner_radius": theme.RADIUS["base"],
            "font": get_font("base"),
            "height": theme.SIZES["input_base"]["height"],
        },
        "label": {
            "font": get_font("base"),
        }
    }
    
    # 获取基础配置
    base_config = style_configs.get(widget_type, {})
    
    # 合并自定义样式
    final_config = {**base_config, **custom_style}
    
    # 应用配置到widget
    try:
        widget.configure(**final_config)
    except Exception as e:
        print(f"❌ 应用主题样式失败: {e}")

def create_gradient_frame(parent, gradient_colors: list, **kwargs) -> ctk.CTkFrame:
    """创建渐变背景框架（简化版，使用单色模拟）"""
    # CustomTkinter不直接支持渐变，使用第一个颜色作为背景
    color = gradient_colors[0] if gradient_colors else theme.COLORS["primary"]
    
    return ctk.CTkFrame(
        parent,
        fg_color=color,
        corner_radius=theme.RADIUS["base"],
        **kwargs
    ) 