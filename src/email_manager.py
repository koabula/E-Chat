#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 邮件管理模块

负责SMTP邮件发送、IMAP邮件接收、邮件轮询和连接管理
"""

import smtplib
import imaplib
import email
import threading
import time
import ssl
import socket
import base64
import binascii
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import queue
import json

# 导入项目模块
from src.config_manager import ConfigManager
from src.database_manager import DatabaseManager
from src.message_parser import message_parser
from src.utils import DataValidator, SecurityUtils


class EmailConnection:
    """邮件连接管理类"""
    
    def __init__(self, server: str, port: int, use_ssl: bool = True, timeout: int = 30):
        """初始化连接参数"""
        self.server = server
        self.port = port
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.connection = None
        self.last_used = None
        self.is_connected = False
    
    def connect(self, username: str, password: str):
        """建立连接（由子类实现）"""
        raise NotImplementedError
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            try:
                self.connection.quit()
            except:
                # 如果正常退出失败，尝试强制关闭
                try:
                    if hasattr(self.connection, 'close'):
                        self.connection.close()
                except:
                    pass
            finally:
                self.connection = None
                self.is_connected = False
                self.last_used = None
    
    def is_alive(self) -> bool:
        """检查连接是否有效"""
        if not self.connection or not self.is_connected:
            return False
        
        # 检查连接是否超时
        if self.last_used:
            time_since_last_use = datetime.now() - self.last_used
            if time_since_last_use > timedelta(minutes=10):  # 10分钟超时
                return False
        
        # 对于SMTP连接，尝试发送NOOP命令来测试连接有效性
        if hasattr(self.connection, 'noop'):
            try:
                self.connection.noop()
                return True
            except Exception:
                self.is_connected = False
                return False
        
        return True
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used = datetime.now()


class SMTPConnection(EmailConnection):
    """SMTP连接管理"""
    
    def connect(self, username: str, password: str) -> bool:
        """建立SMTP连接"""
        try:
            # 创建SMTP连接
            if self.use_ssl:
                self.connection = smtplib.SMTP_SSL(self.server, self.port, timeout=self.timeout)
            else:
                self.connection = smtplib.SMTP(self.server, self.port, timeout=self.timeout)
                if self.port == 587:  # STARTTLS
                    self.connection.starttls()
            
            # 登录
            self.connection.login(username, password)
            self.is_connected = True
            self.update_last_used()
            
            print(f"✅ SMTP连接成功: {self.server}:{self.port}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP连接失败: {e}")
            self.is_connected = False
            return False


class IMAPConnection(EmailConnection):
    """IMAP连接管理"""
    
    def connect(self, username: str, password: str) -> bool:
        """建立IMAP连接"""
        try:
            # 创建IMAP连接
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            
            # 登录
            self.connection.login(username, password)
            
            # 针对126/163邮箱，发送ID信息以解决 "Unsafe Login" 问题
            # 参考: https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2eda07326646e6eb0
            if self.server.endswith(('126.com', '163.com')):
                try:
                    # 检查服务器是否支持ID命令
                    typ, caps = self.connection.capability()
                    print(f"🔍 服务器CAPABILITY: {caps}")
                    
                    # 对于126/163邮箱，强制发送ID，不管CAPABILITY怎么说
                    print("ℹ️ 检测到126/163邮箱，强制发送客户端ID信息...")
                    
                    # 构建ID命令参数 - 使用正确的IMAP格式
                    client_info = [
                        "name", "E-Chat",
                        "version", "1.0.0", 
                        "vendor", "E-Chat Project",
                        "support-email", "support@echat.com"
                    ]
                    
                    # 手动发送ID命令 - 使用更底层的方法
                    import socket
                    
                    # 获取下一个标签
                    tag = self.connection._new_tag()
                    
                    # 构建完整的ID命令
                    id_params = "(" + " ".join([f'"{item}"' for item in client_info]) + ")"
                    command = f'{tag} ID {id_params}\r\n'
                    
                    print(f"📤 发送ID命令: {command.strip()}")
                    
                    # 直接通过socket发送
                    self.connection.sock.send(command.encode('utf-8'))
                    
                    # 读取响应
                    response = self.connection.sock.recv(1024).decode('utf-8')
                    print(f"📥 服务器响应: {response.strip()}")
                    
                    if f'{tag} OK' in response:
                        print("✅ IMAP ID 发送成功")
                    else:
                        print(f"⚠️ IMAP ID 可能失败，响应: {response}")

                except Exception as e:
                    # 即使ID失败也继续尝试，某些服务器可能不支持
                    print(f"⚠️ 发送 IMAP ID 时发生错误: {e}")

            self.is_connected = True
            self.update_last_used()
            
            print(f"✅ IMAP连接成功: {self.server}:{self.port}")
            return True
            
        except Exception as e:
            print(f"❌ IMAP连接失败: {e}")
            self.is_connected = False
            return False


class EmailManager:
    """邮件管理器主类"""
    
    @staticmethod
    def _decode_imap_utf7(encoded_str: str) -> str:
        """解码IMAP Modified UTF-7编码的文件夹名"""
        try:
            # IMAP Modified UTF-7解码
            # 替换 & 为 +, - 为 =
            if not encoded_str.startswith('&') or not encoded_str.endswith('-'):
                return encoded_str
            
            # 移除首尾的 & 和 -
            b64_str = encoded_str[1:-1]
            
            if not b64_str:  # 空字符串，可能是 &- (表示 &)
                return '&'
            
            # 替换 , 为 /
            b64_str = b64_str.replace(',', '/')
            
            # 补齐Base64字符串
            missing_padding = len(b64_str) % 4
            if missing_padding:
                b64_str += '=' * (4 - missing_padding)
            
            # Base64解码
            decoded_bytes = base64.b64decode(b64_str)
            
            # UTF-16BE解码
            decoded_str = decoded_bytes.decode('utf-16be')
            
            return decoded_str
            
        except Exception:
            # 解码失败，返回原始字符串
            return encoded_str
    
    @staticmethod
    def _encode_imap_utf7(unicode_str: str) -> str:
        """编码字符串为IMAP Modified UTF-7格式"""
        try:
            # 如果是纯ASCII，直接返回
            if unicode_str.isascii():
                return unicode_str
            
            # 编码为UTF-16BE
            utf16_bytes = unicode_str.encode('utf-16be')
            
            # Base64编码
            b64_str = base64.b64encode(utf16_bytes).decode('ascii')
            
            # 替换 / 为 ,
            b64_str = b64_str.replace('/', ',')
            
            # 移除末尾的 =
            b64_str = b64_str.rstrip('=')
            
            # 添加 & 和 -
            return f'&{b64_str}-'
            
        except Exception:
            return unicode_str
    
    def __init__(self, config_manager: ConfigManager, database_manager: DatabaseManager):
        """初始化邮件管理器"""
        self.config_manager = config_manager
        self.database_manager = database_manager
        
        # 连接管理
        self.smtp_connection = None
        self.imap_connection = None
        self.connection_lock = threading.RLock()
        
        # 轮询控制
        self.polling_thread = None
        self.polling_running = False
        self.polling_interval = 30  # 默认30秒轮询间隔
        
        # IDLE模式控制
        self.idle_thread = None
        self.idle_running = False
        self.idle_enabled = False
        self.idle_supported = None  # None=未测试, True=支持, False=不支持
        
        # 消息队列
        self.send_queue = queue.Queue()
        self.send_thread = None
        self.send_running = False
        
        # 事件回调
        self.message_received_callback = None
        self.connection_status_callback = None
        self.error_callback = None
        
        # 统计信息
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "connections_established": 0,
            "errors": 0,
            "last_poll_time": None,
            "last_send_time": None
        }
        
        print("📬 邮件管理器初始化完成")
    
    # ==================== 配置和初始化 ====================
    
    def update_config(self, email_config: Dict[str, Any]) -> bool:
        """更新邮件配置"""
        try:
            # 验证配置
            if not self._validate_email_config(email_config):
                return False
            
            # 保存配置
            self.config_manager.set_email_config(
                smtp_server=email_config['smtp_server'],
                smtp_port=email_config['smtp_port'],
                imap_server=email_config['imap_server'],
                imap_port=email_config['imap_port'],
                username=email_config['username'],
                password=email_config['password'],
                use_ssl=email_config.get('use_ssl', True)
            )
            
            # 重新建立连接
            self.disconnect_all()
            
            print("✅ 邮件配置更新成功")
            return True
            
        except Exception as e:
            print(f"❌ 邮件配置更新失败: {e}")
            return False
    
    def _validate_email_config(self, config: Dict[str, Any]) -> bool:
        """验证邮件配置"""
        required_fields = ['smtp_server', 'smtp_port', 'imap_server', 'imap_port', 'username', 'password']
        
        for field in required_fields:
            if not config.get(field):
                print(f"❌ 邮件配置验证失败: {field} 不能为空")
                return False
        
        # 验证端口号
        if not DataValidator.validate_port(config['smtp_port']):
            print("❌ SMTP端口号无效")
            return False
        
        if not DataValidator.validate_port(config['imap_port']):
            print("❌ IMAP端口号无效")
            return False
        
        # 验证邮箱格式
        if not DataValidator.validate_email(config['username']):
            print("❌ 邮箱格式无效")
            return False
        
        return True
    
    def set_callbacks(self, message_received: Callable = None, 
                     connection_status: Callable = None, error: Callable = None):
        """设置回调函数"""
        self.message_received_callback = message_received
        self.connection_status_callback = connection_status
        self.error_callback = error
    
    # ==================== 连接管理 ====================
    
    def connect_smtp(self) -> bool:
        """建立SMTP连接"""
        with self.connection_lock:
            try:
                email_config = self.config_manager.get_email_config()
                
                if not email_config['username'] or not email_config['password']:
                    print("❌ 邮件配置不完整，无法建立SMTP连接")
                    return False
                
                # 断开现有连接
                if self.smtp_connection:
                    self.smtp_connection.disconnect()
                
                # 创建新连接
                self.smtp_connection = SMTPConnection(
                    server=email_config['smtp_server'],
                    port=email_config['smtp_port'],
                    use_ssl=email_config['use_ssl'],
                    timeout=email_config['timeout']
                )
                
                # 建立连接
                success = self.smtp_connection.connect(
                    email_config['username'],
                    email_config['password']
                )
                
                if success:
                    self.stats['connections_established'] += 1
                    self._notify_connection_status('smtp', True)
                else:
                    self.stats['errors'] += 1
                    self._notify_connection_status('smtp', False)
                
                return success
                
            except Exception as e:
                print(f"❌ SMTP连接建立失败: {e}")
                self.stats['errors'] += 1
                self._notify_connection_status('smtp', False)
                return False
    
    def connect_imap(self) -> bool:
        """建立IMAP连接"""
        with self.connection_lock:
            try:
                email_config = self.config_manager.get_email_config()
                
                if not email_config['username'] or not email_config['password']:
                    print("❌ 邮件配置不完整，无法建立IMAP连接")
                    return False
                
                # 断开现有连接
                if self.imap_connection:
                    self.imap_connection.disconnect()
                
                # 创建新连接
                self.imap_connection = IMAPConnection(
                    server=email_config['imap_server'],
                    port=email_config['imap_port'],
                    use_ssl=email_config['use_ssl'],
                    timeout=email_config['timeout']
                )
                
                # 建立连接
                success = self.imap_connection.connect(
                    email_config['username'],
                    email_config['password']
                )
                
                if success:
                    self.stats['connections_established'] += 1
                    self._notify_connection_status('imap', True)
                else:
                    self.stats['errors'] += 1
                    self._notify_connection_status('imap', False)
                
                return success
                
            except Exception as e:
                print(f"❌ IMAP连接建立失败: {e}")
                self.stats['errors'] += 1
                self._notify_connection_status('imap', False)
                return False
    
    def disconnect_all(self):
        """断开所有连接"""
        with self.connection_lock:
            if self.smtp_connection:
                self.smtp_connection.disconnect()
                self.smtp_connection = None
                self._notify_connection_status('smtp', False)
            
            if self.imap_connection:
                self.imap_connection.disconnect()
                self.imap_connection = None
                self._notify_connection_status('imap', False)
    
    def check_connections(self) -> Dict[str, bool]:
        """检查连接状态"""
        smtp_ok = self.smtp_connection and self.smtp_connection.is_alive()
        imap_ok = self.imap_connection and self.imap_connection.is_alive()
        
        return {
            'smtp': smtp_ok,
            'imap': imap_ok,
            'configured': bool(self.config_manager.get_email_config()['username'])
        }
    
    def _notify_connection_status(self, connection_type: str, status: bool):
        """通知连接状态变化"""
        if self.connection_status_callback:
            try:
                self.connection_status_callback(connection_type, status)
            except Exception as e:
                print(f"❌ 连接状态回调执行失败: {e}")
    
    def _notify_error(self, error_type: str, error_message: str):
        """通知错误"""
        if self.error_callback:
            try:
                self.error_callback(error_type, error_message)
            except Exception as e:
                print(f"❌ 错误回调执行失败: {e}")
    
    # ==================== 邮件发送 ====================
    
    def send_message_async(self, recipient: str, content: str, message_type: str = "text") -> bool:
        """异步发送消息"""
        try:
            # 获取当前用户邮箱
            email_config = self.config_manager.get_email_config()
            sender = email_config['username']
            
            if not sender:
                print("❌ 发送者邮箱未配置")
                return False
            
            # 创建消息
            if message_type == "text":
                message = message_parser.create_text_message(sender, recipient, content)
            else:
                print(f"❌ 暂不支持的消息类型: {message_type}")
                return False
            
            # 添加到发送队列
            self.send_queue.put(message)
            
            # 启动发送线程（如果没有运行）
            if not self.send_running:
                self.start_send_thread()
            
            print(f"📤 消息已加入发送队列: {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ 消息发送准备失败: {e}")
            return False
    
    def send_message_sync(self, message: Dict[str, Any]) -> bool:
        """同步发送消息"""
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # 检查SMTP连接
                if not self.smtp_connection or not self.smtp_connection.is_alive():
                    print("🔗 SMTP 连接无效，尝试重新连接...")
                    if not self.connect_smtp():
                        print("❌ SMTP 重连失败")
                        return False
                    print("🔗 SMTP 连接成功")
                
                # 获取配置
                email_config = self.config_manager.get_email_config()
                
                # 创建邮件对象
                email_msg = message_parser.create_email_message(message, email_config)
                
                # 发送邮件
                self.smtp_connection.connection.send_message(email_msg)
                self.smtp_connection.update_last_used()
                
                # 更新统计
                self.stats['messages_sent'] += 1
                self.stats['last_send_time'] = datetime.now()
                
                # 保存到数据库
                self.database_manager.add_message(
                    contact_email=message['recipient'],
                    sender_email=message['sender'],
                    receiver_email=message['recipient'],
                    content=message['content']['text'],
                    message_type=message['type'],
                    message_id=message['message_id'],
                    is_sent=True
                )
                
                print(f"✅ 消息发送成功: {message['recipient']}")
                return True
                
            except Exception as e:
                print(f"❌ 消息发送失败 (尝试 {retry_count + 1}/{max_retries + 1}): {e}")
                
                # 重置连接状态
                if self.smtp_connection:
                    self.smtp_connection.is_connected = False
                    self.smtp_connection.connection = None
                
                retry_count += 1
                
                # 如果还有重试机会，等待一下再重试
                if retry_count <= max_retries:
                    print(f"⏳ 等待 2 秒后重试...")
                    time.sleep(2)
                
        # 所有重试都失败了
        self.stats['errors'] += 1
        self._notify_error('send', str(e))
        print(f"❌ 邮件错误 (send): {str(e)}")
        return False
    
    def start_send_thread(self):
        """启动发送线程"""
        if self.send_running:
            return
        
        self.send_running = True
        self.send_thread = threading.Thread(target=self._send_worker, daemon=True)
        self.send_thread.start()
        print("📤 邮件发送线程已启动")
    
    def stop_send_thread(self):
        """停止发送线程"""
        self.send_running = False
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.join(timeout=5)
        print("📤 邮件发送线程已停止")
    
    def _send_worker(self):
        """发送线程工作函数"""
        while self.send_running:
            try:
                # 从队列获取消息（超时1秒）
                message = self.send_queue.get(timeout=1)
                
                # 发送消息
                success = self.send_message_sync(message)
                
                if not success:
                    # 发送失败，重新加入队列（最多重试3次）
                    retry_count = message.get('_retry_count', 0)
                    if retry_count < 3:
                        message['_retry_count'] = retry_count + 1
                        self.send_queue.put(message)
                        time.sleep(5)  # 等待5秒后重试
                
                self.send_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 发送线程错误: {e}")
                time.sleep(1)
    
    # ==================== 邮件接收 ====================
    
    def start_polling(self, interval: int = None):
        """启动邮件轮询（支持IDLE+轮询混合模式）"""
        if self.polling_running:
            print("⚠️ 邮件轮询已在运行")
            return
        
        # 获取配置
        app_config = self.config_manager.get_app_config()
        self.idle_enabled = app_config.get('idle_enabled', False)
        polling_mode = app_config.get('polling_mode', 'auto')
        
        if interval:
            self.polling_interval = interval
        else:
            if polling_mode == 'auto':
                # 智能模式：根据IDLE支持情况自动调整
                if self.idle_enabled and self.idle_supported:
                    self.polling_interval = 900  # 15分钟备用轮询
                    print("🚀 启用智能模式: IDLE主推送 + 15分钟备用轮询")
                else:
                    self.polling_interval = 30   # 30秒高频轮询
                    print("⚡ 启用智能模式: 30秒高频轮询")
            else:
                # 手动模式
                self.polling_interval = app_config.get('polling_interval', 30)
                print(f"⚙️ 启用手动模式: {self.polling_interval}秒轮询")
        
        self.polling_running = True
        self.polling_thread = threading.Thread(target=self._polling_worker, daemon=True)
        self.polling_thread.start()
        
        # 如果启用了IDLE且支持，同时启动IDLE模式
        if self.idle_enabled and self.idle_supported:
            self.start_idle()
        
        print(f"📥 邮件服务已启动，轮询间隔: {self.polling_interval}秒")
    
    def stop_polling(self):
        """停止邮件轮询"""
        self.polling_running = False
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=10)
        
        # 同时停止IDLE模式
        self.stop_idle()
        
        print("📥 邮件服务已停止")
    
    def start_idle(self):
        """启动IMAP IDLE模式"""
        if self.idle_running:
            print("⚠️ IDLE模式已在运行")
            return
        
        if not self.idle_enabled or not self.idle_supported:
            print("⚠️ IDLE模式未启用或不支持")
            return
        
        self.idle_running = True
        self.idle_thread = threading.Thread(target=self._idle_worker, daemon=True)
        self.idle_thread.start()
        print("🚀 IMAP IDLE实时推送已启动")
    
    def stop_idle(self):
        """停止IMAP IDLE模式"""
        if not self.idle_running:
            return
        
        self.idle_running = False
        if self.idle_thread and self.idle_thread.is_alive():
            # 通过发送DONE来中断IDLE
            try:
                if self.imap_connection and self.imap_connection.connection:
                    self.imap_connection.connection.sock.send(b'DONE\r\n')
            except:
                pass
            
            self.idle_thread.join(timeout=5)
        
        print("🚀 IMAP IDLE实时推送已停止")
    
    def _polling_worker(self):
        """轮询工作线程"""
        while self.polling_running:
            try:
                # 检查新邮件
                self.check_new_messages()
                
                # 更新轮询时间
                self.stats['last_poll_time'] = datetime.now()
                
                # 等待下次轮询
                for _ in range(self.polling_interval):
                    if not self.polling_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ 邮件轮询错误: {e}")
                self.stats['errors'] += 1
                self._notify_error('polling', str(e))
                time.sleep(5)  # 错误后等待5秒
    
    def _idle_worker(self):
        """IDLE工作线程 - 处理实时推送"""
        print("🚀 IDLE工作线程已启动")
        
        while self.idle_running:
            try:
                # 确保IMAP连接可用
                if not self.imap_connection or not self.imap_connection.is_alive():
                    print("🔗 IDLE: IMAP连接无效，尝试重新连接...")
                    if not self.connect_imap():
                        print("❌ IDLE: IMAP重连失败，等待10秒后重试")
                        time.sleep(10)
                        continue
                
                # 选择收件箱
                inbox_folder = self._find_inbox_folder()
                if not inbox_folder:
                    print("❌ IDLE: 无法找到收件箱文件夹")
                    time.sleep(30)
                    continue
                
                select_status, select_data = self.imap_connection.connection.select(inbox_folder)
                if select_status != 'OK':
                    print(f"❌ IDLE: 选择文件夹失败: {select_status}")
                    time.sleep(30)
                    continue
                
                # 开始IDLE监听
                print("📡 IDLE: 开始监听邮件推送...")
                if self._idle_listen():
                    # IDLE成功接收到更新，检查新邮件
                    print("📬 IDLE: 检测到邮件更新，正在检查新邮件...")
                    self.check_new_messages()
                
                # 每次IDLE结束后短暂等待
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ IDLE工作线程错误: {e}")
                time.sleep(10)  # 错误后等待10秒
        
        print("🚀 IDLE工作线程已退出")
    
    def _idle_listen(self) -> bool:
        """执行IDLE监听，返回是否接收到更新"""
        try:
            # 发送IDLE命令
            tag = self.imap_connection.connection._new_tag()
            command = f'{tag} IDLE\r\n'
            
            self.imap_connection.connection.sock.send(command.encode('utf-8'))
            
            # 读取初始响应
            self.imap_connection.connection.sock.settimeout(5)
            response = self.imap_connection.connection.sock.recv(1024).decode('utf-8')
            
            if '+ idling' not in response.lower() and '+ waiting' not in response.lower():
                print(f"❌ IDLE: 启动失败: {response}")
                self.imap_connection.connection.sock.settimeout(None)
                return False
            
            print("📡 IDLE: 监听已激活，等待邮件推送...")
            
            # 设置较长的超时（28分钟，低于30分钟的RFC限制）
            self.imap_connection.connection.sock.settimeout(28 * 60)
            
            # 监听更新
            while self.idle_running:
                try:
                    response = self.imap_connection.connection.sock.recv(1024).decode('utf-8')
                    if response:
                        print(f"📡 IDLE: 收到推送: {response.strip()}")
                        
                        # 检查是否有新邮件或变化
                        if 'EXISTS' in response or 'EXPUNGE' in response or 'RECENT' in response:
                            print("🎉 IDLE: 检测到邮件变化！")
                            # 发送DONE结束IDLE
                            self.imap_connection.connection.sock.send(b'DONE\r\n')
                            # 读取DONE响应
                            self.imap_connection.connection.sock.recv(1024)
                            self.imap_connection.connection.sock.settimeout(None)
                            return True
                        
                        # 检查是否是IDLE结束响应
                        if tag in response and 'OK' in response:
                            print("📡 IDLE: 正常结束")
                            self.imap_connection.connection.sock.settimeout(None)
                            return False
                    
                except socket.timeout:
                    print("⏰ IDLE: 超时，重新启动IDLE监听")
                    # 发送DONE结束当前IDLE
                    try:
                        self.imap_connection.connection.sock.send(b'DONE\r\n')
                        self.imap_connection.connection.sock.recv(1024)
                    except:
                        pass
                    self.imap_connection.connection.sock.settimeout(None)
                    return False
                
                except Exception as e:
                    print(f"❌ IDLE: 监听过程中出错: {e}")
                    self.imap_connection.connection.sock.settimeout(None)
                    return False
            
            # 如果循环退出（idle_running = False），发送DONE
            try:
                self.imap_connection.connection.sock.send(b'DONE\r\n')
                self.imap_connection.connection.sock.recv(1024)
            except:
                pass
            
            self.imap_connection.connection.sock.settimeout(None)
            return False
            
        except Exception as e:
            print(f"❌ IDLE: 监听失败: {e}")
            try:
                self.imap_connection.connection.sock.settimeout(None)
            except:
                pass
            return False
    
    def _list_imap_folders(self) -> List[str]:
        """列出所有IMAP文件夹"""
        try:
            if not self.imap_connection or not self.imap_connection.connection:
                return []
            
            # 列出所有文件夹
            status, folders = self.imap_connection.connection.list()
            if status != 'OK':
                print(f"❌ IMAP LIST 命令失败: {status}")
                return []
            
            folder_names = []
            for folder in folders:
                try:
                    # 解析文件夹名称
                    if isinstance(folder, bytes):
                        folder_str = folder.decode('utf-8', errors='ignore')
                    else:
                        folder_str = str(folder)
                    
                    # IMAP LIST 响应格式：(flags) "delimiter" "folder_name"
                    # 尝试多种解析方法
                    folder_name = None
                    
                    # 方法1：查找最后一组引号中的内容
                    if '"' in folder_str:
                        parts = folder_str.split('"')
                        if len(parts) >= 3:
                            folder_name = parts[-2]
                    
                    # 方法2：如果没有引号，尝试提取最后一个空格后的内容
                    if not folder_name:
                        parts = folder_str.strip().split()
                        if parts:
                            folder_name = parts[-1]
                    
                    # 方法3：直接使用整个字符串作为备选
                    if not folder_name:
                        folder_name = folder_str.strip()
                    
                    if folder_name and folder_name not in folder_names:
                        folder_names.append(folder_name)
                        
                except Exception as e:
                    print(f"⚠️ 解析文件夹名称失败: {e}")
                    continue
            
            return folder_names
            
        except Exception as e:
            print(f"❌ 列出文件夹失败: {e}")
            return []

    def _find_inbox_folder(self) -> Optional[str]:
        """智能查找收件箱文件夹"""
        try:
            if not self.imap_connection or not self.imap_connection.connection:
                return None
            
            # 获取所有文件夹
            available_folders = self._list_imap_folders()
            if not available_folders:
                print("❌ 无法获取文件夹列表")
                return None
            
            print(f"🗂️ 可用文件夹列表: {available_folders}")
            
            # 解码文件夹名并显示
            decoded_folders = {}
            for folder in available_folders:
                decoded = self._decode_imap_utf7(folder)
                decoded_folders[folder] = decoded
                if folder != decoded:
                    print(f"📁 {folder} -> {decoded}")
            
            # 首先检查用户自定义的收件箱文件夹
            email_config = self.config_manager.get_email_config()
            custom_inbox = email_config.get('inbox_folder', '').strip()
            
            if custom_inbox:
                # 用户指定了自定义收件箱
                if custom_inbox in available_folders:
                    print(f"✅ 使用用户指定的收件箱: {custom_inbox}")
                    return custom_inbox
                else:
                    print(f"⚠️ 用户指定的收件箱文件夹不存在: {custom_inbox}")
            
            # 自动查找收件箱 - 优先级列表
            priority_folders = [
                'INBOX',  # 标准IMAP收件箱
                lambda f: self._decode_imap_utf7(f).lower() in ['收件箱', 'inbox', '邮箱'],
                lambda f: 'inbox' in self._decode_imap_utf7(f).lower(),
                lambda f: '收件' in self._decode_imap_utf7(f),
                # 如果以上都没有，使用第一个文件夹
                lambda f: True
            ]
            
            for priority in priority_folders:
                if isinstance(priority, str):
                    # 直接匹配文件夹名
                    if priority in available_folders:
                        print(f"✅ 自动选择收件箱: {priority}")
                        return priority
                else:
                    # 使用函数匹配
                    for folder in available_folders:
                        if priority(folder):
                            decoded_name = self._decode_imap_utf7(folder)
                            print(f"✅ 自动选择收件箱: {folder} ({decoded_name})")
                            return folder
            
            return None
            
        except Exception as e:
            print(f"❌ 查找收件箱文件夹失败: {e}")
            return None

    def check_new_messages(self) -> List[Dict[str, Any]]:
        """检查新邮件"""
        try:
            # 检查IMAP连接
            if not self.imap_connection or not self.imap_connection.is_alive():
                if not self.connect_imap():
                    return []
            
            # 智能查找收件箱文件夹
            inbox_folder = self._find_inbox_folder()
            if not inbox_folder:
                print("❌ 无法找到合适的收件箱文件夹")
                return []
            
            # 选择文件夹
            try:
                select_status, select_data = self.imap_connection.connection.select(inbox_folder)
                if select_status != 'OK':
                    print(f"❌ 选择文件夹失败: {inbox_folder} - {select_status}")
                    return []
                
                msg_count = select_data[0].decode() if select_data else "0"
                print(f"✅ 成功选择文件夹: {inbox_folder} ({msg_count} 条消息)")
                
            except Exception as e:
                print(f"❌ 选择文件夹 '{inbox_folder}' 失败: {e}")
                return []
            
            # 搜索未读邮件
            status, message_ids = self.imap_connection.connection.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("❌ 搜索邮件失败")
                return []
            
            new_messages = []
            
            for msg_id in message_ids[0].split():
                try:
                    # 获取邮件
                    message_data = self._fetch_email(msg_id)
                    if message_data:
                        new_messages.append(message_data)
                        
                except Exception as e:
                    print(f"❌ 处理邮件失败: {e}")
                    continue
            
            self.imap_connection.update_last_used()
            
            if new_messages:
                print(f"📬 收到 {len(new_messages)} 封新邮件")
                self.stats['messages_received'] += len(new_messages)
            
            return new_messages
            
        except Exception as e:
            print(f"❌ 检查新邮件失败: {e}")
            self.stats['errors'] += 1
            return []
    
    def _fetch_email(self, msg_id: bytes) -> Optional[Dict[str, Any]]:
        """获取单封邮件"""
        try:
            # 获取邮件数据
            status, msg_data = self.imap_connection.connection.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # 解析邮件
            email_msg = email.message_from_bytes(msg_data[0][1])
            
            # 检查是否为E-Chat消息
            subject = email_msg.get('Subject', '')
            if not message_parser.is_echat_message(subject):
                print(f"⚠️ 跳过非E-Chat邮件: {subject}")
                return None
            
            # 解析邮件内容
            sender = email_msg.get('From', '')
            recipient = email_msg.get('To', '')
            
            # 提取邮件正文
            body = self._extract_email_body(email_msg)
            
            # 解析消息
            parsed_message = message_parser.parse_message_body(body)
            
            if not parsed_message:
                print("❌ 消息解析失败")
                return None
            
            # 提取附件
            attachments = message_parser.extract_attachments_from_email(email_msg)
            
            # 合并附件信息
            if attachments:
                parsed_message = message_parser.merge_message_with_attachments(parsed_message, attachments)
            
            # 添加邮件头信息
            parsed_message['email_sender'] = sender
            parsed_message['email_recipient'] = recipient
            parsed_message['email_subject'] = subject
            parsed_message['email_msg_id'] = msg_id.decode()
            
            # 保存到数据库
            self._save_received_message(parsed_message)
            
            # 通知消息接收
            if self.message_received_callback:
                try:
                    self.message_received_callback(parsed_message)
                except Exception as e:
                    print(f"❌ 消息接收回调执行失败: {e}")
            
            return parsed_message
            
        except Exception as e:
            print(f"❌ 获取邮件失败: {e}")
            return None
    
    def _extract_email_body(self, email_msg) -> str:
        """提取邮件正文"""
        body = ""
        
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset() or 'utf-8'
                    body_bytes = part.get_payload(decode=True)
                    if body_bytes:
                        body = body_bytes.decode(charset, errors='ignore')
                        break
        else:
            charset = email_msg.get_content_charset() or 'utf-8'
            body_bytes = email_msg.get_payload(decode=True)
            if body_bytes:
                body = body_bytes.decode(charset, errors='ignore')
        
        return body
    
    def _save_received_message(self, message: Dict[str, Any]):
        """保存接收到的消息到数据库"""
        try:
            # 提取发送者邮箱
            sender_email = message.get('sender', message.get('email_sender', ''))
            
            # 清理邮箱地址（移除显示名称）
            if '<' in sender_email and '>' in sender_email:
                sender_email = sender_email.split('<')[1].split('>')[0]
            
            # 获取消息内容
            content = message.get('content', {})
            text_content = content.get('text', '')
            
            # 保存到数据库
            self.database_manager.add_message(
                contact_email=sender_email,
                sender_email=sender_email,
                receiver_email=self.config_manager.get_email_config()['username'],
                content=text_content,
                message_type=message.get('type', 'text'),
                message_id=message.get('message_id', ''),
                is_sent=False
            )
            
            print(f"💾 消息已保存到数据库: {sender_email}")
            
        except Exception as e:
            print(f"❌ 保存接收消息失败: {e}")
    
    # ==================== 统计和管理 ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        connections = self.check_connections()
        
        return {
            **self.stats,
            'connections': connections,
            'polling_running': self.polling_running,
            'idle_running': self.idle_running,
            'idle_enabled': self.idle_enabled,
            'idle_supported': self.idle_supported,
            'send_running': self.send_running,
            'queue_size': self.send_queue.qsize()
        }
    
    def test_connections(self) -> Dict[str, Any]:
        """测试邮件连接"""
        results = {
            'smtp': {'success': False, 'error': None},
            'imap': {'success': False, 'error': None, 'folders': []}
        }
        
        # 测试SMTP
        try:
            if self.connect_smtp():
                results['smtp']['success'] = True
            else:
                results['smtp']['error'] = "连接失败"
        except Exception as e:
            results['smtp']['error'] = str(e)
        
        # 测试IMAP
        try:
            if self.connect_imap():
                results['imap']['success'] = True
                # 列出可用文件夹
                folders = self._list_imap_folders()
                results['imap']['folders'] = folders
                print(f"🗂️ IMAP 可用文件夹: {folders}")
            else:
                results['imap']['error'] = "连接失败"
        except Exception as e:
            results['imap']['error'] = str(e)
        
        return results
    
    def test_idle_support(self) -> bool:
        """测试IMAP IDLE支持"""
        try:
            print("🔍 开始测试IMAP IDLE支持...")
            
            # 确保IMAP连接可用
            if not self.imap_connection or not self.imap_connection.is_alive():
                if not self.connect_imap():
                    print("❌ IMAP连接失败，无法测试IDLE")
                    self.idle_supported = False
                    return False
            
            # 检查服务器能力
            try:
                typ, data = self.imap_connection.connection.capability()
                if typ != 'OK':
                    print(f"❌ 获取服务器能力失败: {typ}")
                    self.idle_supported = False
                    return False
                
                capabilities = data[0].decode('utf-8', errors='ignore').upper()
                print(f"📋 服务器能力: {capabilities}")
                
                if 'IDLE' in capabilities:
                    print("✅ 服务器支持IDLE命令")
                    
                    # 进一步测试IDLE命令
                    if self._test_idle_command():
                        self.idle_supported = True
                        # 保存测试结果到配置
                        self.config_manager.set_app_config(idle_test_result=True)
                        self.config_manager.save_config()
                        print("🎉 IDLE功能测试成功")
                        return True
                    else:
                        print("❌ IDLE命令测试失败")
                        self.idle_supported = False
                        self.config_manager.set_app_config(idle_test_result=False)
                        self.config_manager.save_config()
                        return False
                else:
                    print("❌ 服务器不支持IDLE命令")
                    self.idle_supported = False
                    self.config_manager.set_app_config(idle_test_result=False)
                    self.config_manager.save_config()
                    return False
                    
            except Exception as e:
                print(f"❌ 检查服务器能力时出错: {e}")
                self.idle_supported = False
                return False
                
        except Exception as e:
            print(f"❌ IDLE支持测试失败: {e}")
            self.idle_supported = False
            return False
    
    def _test_idle_command(self) -> bool:
        """测试IDLE命令是否可用"""
        try:
            # 选择收件箱
            inbox_folder = self._find_inbox_folder()
            if not inbox_folder:
                print("❌ 无法找到收件箱文件夹")
                return False
            
            # 选择文件夹
            select_status, select_data = self.imap_connection.connection.select(inbox_folder)
            if select_status != 'OK':
                print(f"❌ 选择文件夹失败: {select_status}")
                return False
            
            # 尝试发送IDLE命令
            tag = self.imap_connection.connection._new_tag()
            command = f'{tag} IDLE\r\n'
            
            print("📤 发送IDLE命令进行测试...")
            self.imap_connection.connection.sock.send(command.encode('utf-8'))
            
            # 读取响应（设置超时）
            self.imap_connection.connection.sock.settimeout(5)
            response = self.imap_connection.connection.sock.recv(1024).decode('utf-8')
            print(f"📥 IDLE响应: {response.strip()}")
            
            # 检查响应是否表明IDLE开始
            if '+ idling' in response.lower() or '+ waiting' in response.lower():
                print("✅ IDLE命令启动成功")
                
                # 立即发送DONE结束IDLE
                self.imap_connection.connection.sock.send(b'DONE\r\n')
                response = self.imap_connection.connection.sock.recv(1024).decode('utf-8')
                print(f"📥 DONE响应: {response.strip()}")
                
                # 重置超时
                self.imap_connection.connection.sock.settimeout(None)
                return True
            else:
                print(f"❌ IDLE命令未正确启动: {response}")
                # 重置超时
                self.imap_connection.connection.sock.settimeout(None)
                return False
                
        except Exception as e:
            print(f"❌ 测试IDLE命令时出错: {e}")
            # 重置超时
            try:
                self.imap_connection.connection.sock.settimeout(None)
            except:
                pass
            return False
    
    def debug_imap_folders(self):
        """调试IMAP文件夹 - 手动调用来诊断收件箱问题"""
        try:
            print("🔍 开始调试IMAP文件夹...")
            
            if not self.connect_imap():
                print("❌ IMAP连接失败")
                return
            
            # 列出所有文件夹
            folders = self._list_imap_folders()
            print(f"📁 发现 {len(folders)} 个文件夹:")
            for i, folder in enumerate(folders, 1):
                print(f"  {i}. '{folder}'")
            
            # 尝试选择每个文件夹
            print("\n🧪 测试文件夹选择:")
            for folder in folders:
                try:
                    status, data = self.imap_connection.connection.select(folder)
                    if status == 'OK':
                        msg_count = data[0].decode() if data else "未知"
                        print(f"  ✅ '{folder}' - 可选择 ({msg_count} 条消息)")
                    else:
                        print(f"  ❌ '{folder}' - 选择失败: {status}")
                except Exception as e:
                    print(f"  ❌ '{folder}' - 异常: {e}")
            
        except Exception as e:
            print(f"❌ 调试IMAP文件夹失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        print("🔄 正在清理邮件管理器...")
        
        # 停止线程
        self.stop_polling()  # 这会同时停止IDLE
        self.stop_send_thread()
        
        # 断开连接
        self.disconnect_all()
        
        print("✅ 邮件管理器清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup() 