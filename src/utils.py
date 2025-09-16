#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 工具函数和数据验证模块

包含各种实用函数、数据验证和格式化功能
"""

import re
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
import base64


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱地址格式"""
        if not email or not isinstance(email, str):
            return False
        
        # 邮箱正则表达式
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    @staticmethod
    def validate_password(password: str, min_length: int = 6) -> Tuple[bool, str]:
        """验证密码强度"""
        if not password or not isinstance(password, str):
            return False, "密码不能为空"
        
        if len(password) < min_length:
            return False, f"密码长度至少需要{min_length}位"
        
        # 检查是否包含特殊字符（可选）
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     return False, "密码应包含至少一个特殊字符"
        
        return True, "密码强度合格"
    
    @staticmethod
    def validate_port(port: Union[str, int]) -> bool:
        """验证端口号"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_message_length(message: str, max_length: int = 5000) -> bool:
        """验证消息长度"""
        if not isinstance(message, str):
            return False
        return len(message) <= max_length
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 25) -> Tuple[bool, str]:
        """验证文件大小"""
        try:
            file_size = Path(file_path).stat().st_size
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                return False, f"文件大小不能超过{max_size_mb}MB"
            
            return True, "文件大小合规"
        except FileNotFoundError:
            return False, "文件不存在"
        except Exception as e:
            return False, f"文件验证失败: {e}"
    
    @staticmethod
    def validate_file_type(file_path: str, allowed_types: List[str] = None) -> Tuple[bool, str]:
        """验证文件类型"""
        if allowed_types is None:
            allowed_types = ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.gif']
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext not in allowed_types:
                return False, f"不支持的文件类型: {file_ext}"
            
            return True, "文件类型合规"
        except Exception as e:
            return False, f"文件类型验证失败: {e}"
    
    @staticmethod
    def validate_nickname(nickname: str) -> Tuple[bool, str]:
        """验证昵称"""
        if not nickname or not isinstance(nickname, str):
            return False, "昵称不能为空"
        
        nickname = nickname.strip()
        
        if len(nickname) < 1:
            return False, "昵称不能为空"
        
        if len(nickname) > 50:
            return False, "昵称长度不能超过50个字符"
        
        # 检查特殊字符
        if re.search(r'[<>"\\/|?*]', nickname):
            return False, "昵称包含非法字符"
        
        return True, "昵称格式正确"


class FormatUtils:
    """格式化工具类"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    @staticmethod
    def format_timestamp(timestamp: datetime, format_type: str = 'auto') -> str:
        """格式化时间戳"""
        now = datetime.now()
        
        if format_type == 'auto':
            # 自动选择格式
            diff = now - timestamp
            
            if diff.days == 0:
                # 今天 - 显示时间
                return timestamp.strftime("%H:%M")
            elif diff.days == 1:
                # 昨天
                return "昨天"
            elif diff.days < 7:
                # 一周内 - 显示星期
                weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                return weekdays[timestamp.weekday()]
            else:
                # 超过一周 - 显示日期
                return timestamp.strftime("%m/%d")
        
        elif format_type == 'full':
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        elif format_type == 'date':
            return timestamp.strftime("%Y-%m-%d")
        elif format_type == 'time':
            return timestamp.strftime("%H:%M:%S")
        else:
            return timestamp.strftime(format_type)
    
    @staticmethod
    def format_message_preview(message: str, max_length: int = 30) -> str:
        """格式化消息预览"""
        if not message:
            return ""
        
        # 移除换行符和多余空格
        cleaned = re.sub(r'\s+', ' ', message.strip())
        
        if len(cleaned) <= max_length:
            return cleaned
        
        return cleaned[:max_length] + "..."
    
    @staticmethod
    def format_contact_name(email: str, nickname: str = None) -> str:
        """格式化联系人显示名称"""
        if nickname and nickname.strip():
            return nickname.strip()
        
        # 从邮箱提取用户名
        if '@' in email:
            return email.split('@')[0]
        
        return email


class MessageUtils:
    """消息处理工具类"""
    
    @staticmethod
    def generate_message_id() -> str:
        """生成唯一消息ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"echat_{timestamp}_{unique_id}"
    
    @staticmethod
    def create_email_subject(message_type: str = "text", extra_info: str = "") -> str:
        """创建邮件主题"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = uuid.uuid4().hex[:6]
        
        subject = f"[E-Chat] {message_type}_{timestamp}_{random_id}"
        
        if extra_info:
            subject += f"_{extra_info}"
        
        return subject
    
    @staticmethod
    def parse_email_subject(subject: str) -> Dict[str, str]:
        """解析邮件主题"""
        if not subject.startswith("[E-Chat]"):
            return {}
        
        try:
            # 移除前缀
            content = subject[9:].strip()
            parts = content.split('_')
            
            if len(parts) >= 3:
                return {
                    'message_type': parts[0],
                    'timestamp': parts[1],
                    'random_id': parts[2],
                    'extra_info': '_'.join(parts[3:]) if len(parts) > 3 else ''
                }
        except Exception:
            pass
        
        return {}
    
    @staticmethod
    def create_message_body(sender: str, recipient: str, content: str, 
                          message_type: str = "text", attachment_info: Dict = None) -> str:
        """创建消息体（JSON格式）"""
        message_data = {
            "version": "1.0",
            "type": message_type,
            "sender": sender,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat(),
            "content": {
                "text": content
            },
            "client_info": {
                "app": "E-Chat",
                "version": "1.0.0"
            }
        }
        
        if attachment_info:
            message_data["content"].update(attachment_info)
        
        return json.dumps(message_data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def parse_message_body(body: str) -> Dict[str, Any]:
        """解析消息体"""
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            # 如果不是JSON格式，当作普通文本处理
            return {
                "version": "1.0",
                "type": "text",
                "content": {
                    "text": body
                },
                "client_info": {
                    "app": "Unknown",
                    "version": "Unknown"
                }
            }


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """对密码进行哈希处理"""
        if salt is None:
            salt = uuid.uuid4().hex
        
        # 使用SHA-256进行哈希
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """验证密码"""
        computed_hash, _ = SecurityUtils.hash_password(password, salt)
        return computed_hash == password_hash
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """生成随机令牌"""
        return base64.urlsafe_b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)[:length].decode()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，移除危险字符"""
        # 移除或替换危险字符
        safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 移除前后空格和点
        safe_chars = safe_chars.strip('. ')
        
        # 限制长度
        if len(safe_chars) > 255:
            name, ext = Path(filename).stem, Path(filename).suffix
            safe_chars = name[:255-len(ext)] + ext
        
        return safe_chars


class ConfigUtils:
    """配置工具类"""
    
    @staticmethod
    def parse_window_size(size_str: str) -> Tuple[int, int]:
        """解析窗口大小字符串"""
        try:
            if 'x' in size_str:
                width, height = size_str.split('x')
                return int(width), int(height)
        except ValueError:
            pass
        
        # 默认大小
        return 1200, 800
    
    @staticmethod
    def format_window_size(width: int, height: int) -> str:
        """格式化窗口大小为字符串"""
        return f"{width}x{height}"
    
    @staticmethod
    def get_default_email_servers(provider: str) -> Dict[str, Any]:
        """获取常用邮件服务商的默认配置"""
        servers = {
            'gmail': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'use_ssl': True
            },
            'outlook': {
                'smtp_server': 'smtp-mail.outlook.com',
                'smtp_port': 587,
                'imap_server': 'outlook.office365.com',
                'imap_port': 993,
                'use_ssl': True
            },
            'yahoo': {
                'smtp_server': 'smtp.mail.yahoo.com',
                'smtp_port': 587,
                'imap_server': 'imap.mail.yahoo.com',
                'imap_port': 993,
                'use_ssl': True
            },
            'qq': {
                'smtp_server': 'smtp.qq.com',
                'smtp_port': 587,
                'imap_server': 'imap.qq.com',
                'imap_port': 993,
                'use_ssl': True
            },
            '163': {
                'smtp_server': 'smtp.163.com',
                'smtp_port': 25,
                'imap_server': 'imap.163.com',
                'imap_port': 993,
                'use_ssl': True
            }
        }
        
        return servers.get(provider.lower(), {})


class LogUtils:
    """日志工具类"""
    
    @staticmethod
    def format_log_entry(level: str, message: str, extra_data: Dict = None) -> str:
        """格式化日志条目"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        if extra_data:
            extra_str = json.dumps(extra_data, ensure_ascii=False)
            log_entry += f" | {extra_str}"
        
        return log_entry
    
    @staticmethod
    def clean_old_logs(log_dir: str, days_to_keep: int = 30):
        """清理旧日志文件"""
        try:
            log_path = Path(log_dir)
            if not log_path.exists():
                return
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for log_file in log_path.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    print(f"删除旧日志文件: {log_file}")
        
        except Exception as e:
            print(f"清理日志文件失败: {e}")


# 常用验证函数的快捷方式
def is_valid_email(email: str) -> bool:
    """验证邮箱地址"""
    return DataValidator.validate_email(email)

def is_valid_port(port: Union[str, int]) -> bool:
    """验证端口号"""
    return DataValidator.validate_port(port)

def format_time(timestamp: datetime, format_type: str = 'auto') -> str:
    """格式化时间"""
    return FormatUtils.format_timestamp(timestamp, format_type)

def generate_msg_id() -> str:
    """生成消息ID"""
    return MessageUtils.generate_message_id()

def clean_filename(filename: str) -> str:
    """清理文件名"""
    return SecurityUtils.sanitize_filename(filename) 