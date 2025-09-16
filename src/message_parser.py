#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 消息解析模块

负责E-Chat消息格式的定义、创建、解析和验证
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import uuid

# 导入工具类
from src.utils import MessageUtils, SecurityUtils, DataValidator


class MessageParser:
    """E-Chat消息解析器"""
    
    # E-Chat消息格式版本
    MESSAGE_VERSION = "1.0"
    
    # E-Chat邮件主题前缀
    SUBJECT_PREFIX = "[E-Chat]"
    
    # 支持的消息类型
    MESSAGE_TYPES = ["text", "file", "image", "status", "system"]
    
    def __init__(self):
        """初始化消息解析器"""
        self.app_info = {
            "app": "E-Chat",
            "version": "1.0.0",
            "protocol_version": self.MESSAGE_VERSION
        }
        
        print("📧 消息解析器初始化完成")
    
    # ==================== 消息创建 ====================
    
    def create_text_message(self, sender: str, recipient: str, content: str) -> Dict[str, Any]:
        """创建文本消息"""
        return self._create_base_message(sender, recipient, "text", {"text": content})
    
    def create_file_message(self, sender: str, recipient: str, content: str, 
                          file_name: str, file_size: int, file_data: bytes = None) -> Dict[str, Any]:
        """创建文件消息"""
        file_content = {
            "text": content,
            "file_name": file_name,
            "file_size": file_size
        }
        
        # 如果有文件数据，进行base64编码
        if file_data:
            file_content["file_data"] = base64.b64encode(file_data).decode('utf-8')
            file_content["encoding"] = "base64"
        
        return self._create_base_message(sender, recipient, "file", file_content)
    
    def create_status_message(self, sender: str, recipient: str, status_type: str, 
                            status_data: Dict = None) -> Dict[str, Any]:
        """创建状态消息（在线/离线/正在输入等）"""
        status_content = {
            "status_type": status_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if status_data:
            status_content.update(status_data)
        
        return self._create_base_message(sender, recipient, "status", status_content)
    
    def _create_base_message(self, sender: str, recipient: str, message_type: str, 
                           content: Dict[str, Any]) -> Dict[str, Any]:
        """创建基础消息结构"""
        # 验证输入
        if not DataValidator.validate_email(sender):
            raise ValueError(f"发送者邮箱格式无效: {sender}")
        
        if not DataValidator.validate_email(recipient):
            raise ValueError(f"接收者邮箱格式无效: {recipient}")
        
        if message_type not in self.MESSAGE_TYPES:
            raise ValueError(f"不支持的消息类型: {message_type}")
        
        # 创建消息
        message = {
            "version": self.MESSAGE_VERSION,
            "message_id": MessageUtils.generate_message_id(),
            "type": message_type,
            "sender": sender,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "client_info": self.app_info.copy()
        }
        
        return message
    
    # ==================== 邮件格式化 ====================
    
    def format_email_subject(self, message: Dict[str, Any]) -> str:
        """格式化邮件主题"""
        message_type = message.get("type", "text")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message_id = message.get("message_id", "unknown")
        
        # 提取消息ID的后8位
        short_id = message_id.split('_')[-1][:8] if '_' in message_id else message_id[:8]
        
        subject = f"{self.SUBJECT_PREFIX} {message_type}_{timestamp}_{short_id}"
        
        return subject
    
    def create_email_message(self, message: Dict[str, Any], smtp_config: Dict[str, Any]) -> MIMEMultipart:
        """创建邮件消息对象"""
        try:
            # 创建邮件对象
            email_msg = MIMEMultipart()
            
            # 设置邮件头
            email_msg['From'] = smtp_config.get('username', message['sender'])
            email_msg['To'] = message['recipient']
            email_msg['Subject'] = self.format_email_subject(message)
            
            # 设置自定义头部（用于识别E-Chat消息）
            email_msg['X-E-Chat-Version'] = self.MESSAGE_VERSION
            email_msg['X-E-Chat-Type'] = message['type']
            email_msg['X-E-Chat-Message-ID'] = message['message_id']
            
            # 创建消息体
            message_body = self.format_message_body(message)
            
            # 添加文本部分
            text_part = MIMEText(message_body, 'plain', 'utf-8')
            email_msg.attach(text_part)
            
            # 如果是文件消息且包含文件数据，添加附件
            if message['type'] == 'file' and 'file_data' in message['content']:
                self._attach_file_to_email(email_msg, message)
            
            return email_msg
            
        except Exception as e:
            raise Exception(f"创建邮件消息失败: {e}")
    
    def format_message_body(self, message: Dict[str, Any]) -> str:
        """格式化消息体为JSON字符串"""
        try:
            # 创建消息体的副本，移除可能很大的文件数据
            body_message = message.copy()
            
            # 如果是文件消息，处理文件数据
            if message['type'] == 'file' and 'file_data' in message['content']:
                # 不在邮件正文中包含文件数据，而是作为附件
                body_content = body_message['content'].copy()
                if 'file_data' in body_content:
                    body_content['has_attachment'] = True
                    del body_content['file_data']  # 移除大数据，避免邮件正文过大
                body_message['content'] = body_content
            
            # 格式化为JSON
            json_body = json.dumps(body_message, ensure_ascii=False, indent=2)
            
            # 添加人类可读的头部信息
            readable_header = f"""
E-Chat Message
==============
From: {message['sender']}
To: {message['recipient']}
Type: {message['type']}
Time: {message['timestamp']}

Raw Message Data:
-----------------
"""
            
            return readable_header + json_body
            
        except Exception as e:
            raise Exception(f"格式化消息体失败: {e}")
    
    def _attach_file_to_email(self, email_msg: MIMEMultipart, message: Dict[str, Any]):
        """将文件附加到邮件"""
        try:
            content = message['content']
            file_name = content.get('file_name', 'attachment')
            file_data = content.get('file_data', '')
            
            if not file_data:
                return
            
            # 解码base64文件数据
            file_bytes = base64.b64decode(file_data.encode('utf-8'))
            
            # 创建附件
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file_bytes)
            encoders.encode_base64(attachment)
            
            # 设置附件头
            clean_filename = SecurityUtils.sanitize_filename(file_name)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{clean_filename}"'
            )
            
            email_msg.attach(attachment)
            
        except Exception as e:
            print(f"❌ 添加邮件附件失败: {e}")
    
    # ==================== 消息解析 ====================
    
    def is_echat_message(self, email_subject: str) -> bool:
        """检查是否为E-Chat消息"""
        return email_subject.startswith(self.SUBJECT_PREFIX)
    
    def parse_email_subject(self, subject: str) -> Dict[str, str]:
        """解析邮件主题"""
        if not self.is_echat_message(subject):
            return {}
        
        try:
            # 移除前缀
            content = subject[len(self.SUBJECT_PREFIX):].strip()
            
            # 使用工具函数解析
            return MessageUtils.parse_email_subject(self.SUBJECT_PREFIX + " " + content)
            
        except Exception as e:
            print(f"❌ 解析邮件主题失败: {e}")
            return {}
    
    def parse_message_body(self, body: str) -> Optional[Dict[str, Any]]:
        """解析消息体"""
        try:
            # 查找JSON数据部分
            json_start = body.find('{')
            if json_start == -1:
                # 如果没找到JSON，当作普通文本处理
                return self._create_fallback_message(body)
            
            json_part = body[json_start:]
            
            # 尝试解析JSON
            message_data = json.loads(json_part)
            
            # 验证消息格式
            if self._validate_message_format(message_data):
                return message_data
            else:
                print("⚠️ 消息格式验证失败，当作普通文本处理")
                return self._create_fallback_message(body)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}，当作普通文本处理")
            return self._create_fallback_message(body)
        except Exception as e:
            print(f"❌ 解析消息体失败: {e}")
            return None
    
    def _create_fallback_message(self, body: str) -> Dict[str, Any]:
        """创建降级消息（用于非E-Chat格式的邮件）"""
        return {
            "version": "unknown",
            "type": "text",
            "content": {
                "text": body.strip()
            },
            "client_info": {
                "app": "Unknown",
                "version": "Unknown"
            },
            "fallback": True  # 标记为降级消息
        }
    
    def _validate_message_format(self, message: Dict[str, Any]) -> bool:
        """验证消息格式"""
        required_fields = ["version", "type", "content"]
        
        for field in required_fields:
            if field not in message:
                print(f"⚠️ 缺少必需字段: {field}")
                return False
        
        # 验证消息类型
        if message["type"] not in self.MESSAGE_TYPES:
            print(f"⚠️ 不支持的消息类型: {message['type']}")
            return False
        
        # 验证内容结构
        if not isinstance(message["content"], dict):
            print("⚠️ 消息内容格式错误")
            return False
        
        return True
    
    def extract_attachments_from_email(self, email_msg) -> List[Dict[str, Any]]:
        """从邮件中提取附件"""
        attachments = []
        
        try:
            for part in email_msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        # 获取文件数据
                        file_data = part.get_payload(decode=True)
                        
                        attachment_info = {
                            "filename": SecurityUtils.sanitize_filename(filename),
                            "size": len(file_data) if file_data else 0,
                            "data": base64.b64encode(file_data).decode('utf-8') if file_data else ""
                        }
                        
                        attachments.append(attachment_info)
        
        except Exception as e:
            print(f"❌ 提取附件失败: {e}")
        
        return attachments
    
    # ==================== 消息验证和工具 ====================
    
    def validate_message_content(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """验证消息内容"""
        try:
            # 检查基本结构
            if not self._validate_message_format(message):
                return False, "消息格式无效"
            
            # 验证发送者和接收者邮箱
            if 'sender' in message and not DataValidator.validate_email(message['sender']):
                return False, f"发送者邮箱格式无效: {message['sender']}"
            
            if 'recipient' in message and not DataValidator.validate_email(message['recipient']):
                return False, f"接收者邮箱格式无效: {message['recipient']}"
            
            # 根据消息类型验证内容
            message_type = message['type']
            content = message['content']
            
            if message_type == 'text':
                if 'text' not in content:
                    return False, "文本消息缺少text字段"
                
                text_content = content['text']
                if not DataValidator.validate_message_length(text_content):
                    return False, "消息内容过长"
            
            elif message_type == 'file':
                required_fields = ['file_name', 'file_size']
                for field in required_fields:
                    if field not in content:
                        return False, f"文件消息缺少{field}字段"
                
                # 验证文件大小
                file_size = content['file_size']
                if not isinstance(file_size, int) or file_size < 0:
                    return False, "文件大小无效"
                
                # 验证文件名
                file_name = content['file_name']
                if not file_name or len(file_name.strip()) == 0:
                    return False, "文件名无效"
            
            return True, "消息验证通过"
            
        except Exception as e:
            return False, f"消息验证出错: {e}"
    
    def get_message_summary(self, message: Dict[str, Any]) -> str:
        """获取消息摘要"""
        try:
            message_type = message.get('type', 'unknown')
            content = message.get('content', {})
            
            if message_type == 'text':
                text = content.get('text', '')
                return text[:50] + "..." if len(text) > 50 else text
            
            elif message_type == 'file':
                file_name = content.get('file_name', '未知文件')
                file_size = content.get('file_size', 0)
                from src.utils import FormatUtils
                size_str = FormatUtils.format_file_size(file_size)
                return f"📎 {file_name} ({size_str})"
            
            elif message_type == 'status':
                status_type = content.get('status_type', '未知状态')
                return f"📊 状态: {status_type}"
            
            else:
                return f"📧 {message_type}消息"
                
        except Exception as e:
            return "📧 消息"
    
    def get_message_display_time(self, message: Dict[str, Any]) -> str:
        """获取消息显示时间"""
        try:
            timestamp_str = message.get('timestamp', '')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                from src.utils import format_time
                return format_time(timestamp)
            else:
                return datetime.now().strftime("%H:%M")
        except Exception:
            return datetime.now().strftime("%H:%M")
    
    def merge_message_with_attachments(self, message: Dict[str, Any], 
                                     attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """将附件信息合并到消息中"""
        if not attachments:
            return message
        
        # 创建消息副本
        merged_message = message.copy()
        
        # 如果是文件消息，合并附件数据
        if message['type'] == 'file' and attachments:
            attachment = attachments[0]  # 假设只有一个附件
            merged_message['content'].update({
                'file_data': attachment['data'],
                'file_size': attachment['size'],
                'encoding': 'base64'
            })
        
        # 添加附件列表
        merged_message['attachments'] = attachments
        
        return merged_message
    
    # ==================== 统计和调试 ====================
    
    def get_parser_stats(self) -> Dict[str, Any]:
        """获取解析器统计信息"""
        return {
            "version": self.MESSAGE_VERSION,
            "supported_types": self.MESSAGE_TYPES,
            "app_info": self.app_info
        }
    
    def debug_message_structure(self, message: Dict[str, Any]) -> str:
        """调试消息结构"""
        try:
            return json.dumps(message, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Debug失败: {e}"


# 创建全局消息解析器实例
message_parser = MessageParser() 