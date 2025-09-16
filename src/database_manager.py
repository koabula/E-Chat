#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 数据库管理模块

使用SQLite进行本地数据存储，包含联系人、消息和设置数据
"""

import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json
import logging

# 导入语言管理器
from src.language_manager import language_manager


class DatabaseManager:
    """数据库管理器 - 负责SQLite数据库的所有操作"""
    
    def __init__(self, db_path: str = "database.db"):
        """初始化数据库管理器"""
        self.db_path = Path(db_path)
        self.connection = None
        self.lock = threading.RLock()  # 线程安全锁
        
        # 初始化数据库
        self.init_database()
        
        print("📊 数据库管理器初始化完成")
    
    def init_database(self):
        """初始化数据库和表结构"""
        try:
            self.connect()
            self.create_tables()
            self.init_default_data()
            print("✅ 数据库初始化成功")
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
    
    def connect(self):
        """连接到数据库"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂为字典格式
            self.connection.row_factory = sqlite3.Row
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def create_tables(self):
        """创建数据表结构"""
        with self.lock:
            cursor = self.connection.cursor()
            
            try:
                # 创建联系人表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        nickname TEXT NOT NULL,
                        avatar_path TEXT,
                        last_message_time TIMESTAMP,
                        last_message_content TEXT,
                        unread_count INTEGER DEFAULT 0,
                        is_blocked BOOLEAN DEFAULT FALSE,
                        is_online BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建消息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        contact_email TEXT NOT NULL,
                        message_id TEXT UNIQUE,
                        sender_email TEXT NOT NULL,
                        receiver_email TEXT NOT NULL,
                        content TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        attachment_path TEXT,
                        is_read BOOLEAN DEFAULT FALSE,
                        is_sent BOOLEAN DEFAULT TRUE,
                        sent_at TIMESTAMP,
                        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (contact_email) REFERENCES contacts (email) ON DELETE CASCADE
                    )
                """)
                
                # 创建设置表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        data_type TEXT DEFAULT 'string',
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引以提高查询性能
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_contact ON messages(contact_email)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_time ON messages(sent_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)")
                
                self.connection.commit()
                print("📋 数据表创建完成")
                
            except Exception as e:
                self.connection.rollback()
                print(f"❌ 数据表创建失败: {e}")
                raise
            finally:
                cursor.close()
    
    def init_default_data(self):
        """初始化默认数据"""
        with self.lock:
            # 初始化默认设置
            default_settings = [
                ("theme", "dark", "string", "应用主题"),
                ("language", "en", "string", "界面语言"),
                ("font_size", "12", "integer", "字体大小"),
                ("window_size", "1200x800", "string", "窗口大小"),
                ("auto_start", "false", "boolean", "开机自启"),
                ("notifications", "true", "boolean", "消息通知"),
                ("polling_interval", "30", "integer", "邮件轮询间隔(秒)"),
                ("max_message_length", "5000", "integer", "最大消息长度"),
                ("email_smtp_server", "", "string", "SMTP服务器"),
                ("email_smtp_port", "587", "integer", "SMTP端口"),
                ("email_imap_server", "", "string", "IMAP服务器"),
                ("email_imap_port", "993", "integer", "IMAP端口"),
                ("email_username", "", "string", "邮箱用户名"),
                ("email_password_encrypted", "", "string", "加密密码"),
            ]
            
            for key, value, data_type, description in default_settings:
                self.set_setting(key, value, data_type, description, init_mode=True)
    
    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = True) -> Any:
        """执行数据库查询"""
        with self.lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    self.connection.commit()
                    return cursor.rowcount
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor
                    
            except Exception as e:
                self.connection.rollback()
                print(f"❌ 数据库查询失败: {query[:50]}... - {e}")
                raise
            finally:
                cursor.close()
    
    # ==================== 联系人相关操作 ====================
    
    def add_contact(self, email: str, nickname: str, avatar_path: str = None) -> bool:
        """添加联系人"""
        try:
            query = """
                INSERT INTO contacts (email, nickname, avatar_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """
            now = datetime.now()
            self.execute_query(query, (email, nickname, avatar_path, now, now))
            print(f"✅ 添加联系人成功: {nickname} ({email})")
            return True
        except sqlite3.IntegrityError:
            print(f"⚠️ 联系人已存在: {email}")
            return False
        except Exception as e:
            print(f"❌ 添加联系人失败: {e}")
            return False
    
    def get_contacts(self, include_blocked: bool = False) -> List[Dict]:
        """获取所有联系人"""
        try:
            query = "SELECT * FROM contacts"
            if not include_blocked:
                query += " WHERE is_blocked = FALSE"
            query += " ORDER BY last_message_time DESC, nickname ASC"
            
            rows = self.execute_query(query)
            contacts = []
            
            for row in rows:
                contact = dict(row)
                # 转换数据类型
                contact['unread_count'] = contact['unread_count'] or 0
                contact['is_blocked'] = bool(contact['is_blocked'])
                contact['is_online'] = bool(contact['is_online'])
                contacts.append(contact)
            
            return contacts
        except Exception as e:
            print(f"❌ 获取联系人失败: {e}")
            return []
    
    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取联系人"""
        try:
            query = "SELECT * FROM contacts WHERE email = ?"
            row = self.execute_query(query, (email,), fetch_one=True)
            
            if row:
                contact = dict(row)
                contact['unread_count'] = contact['unread_count'] or 0
                contact['is_blocked'] = bool(contact['is_blocked'])
                contact['is_online'] = bool(contact['is_online'])
                return contact
            return None
        except Exception as e:
            print(f"❌ 获取联系人失败: {e}")
            return None
    
    def update_contact(self, email: str, **kwargs) -> bool:
        """更新联系人信息"""
        try:
            # 构建更新语句
            set_parts = []
            params = []
            
            for key, value in kwargs.items():
                if key in ['nickname', 'avatar_path', 'last_message_time', 'last_message_content', 
                          'unread_count', 'is_blocked', 'is_online']:
                    set_parts.append(f"{key} = ?")
                    params.append(value)
            
            if not set_parts:
                return True
            
            # 添加更新时间
            set_parts.append("updated_at = ?")
            params.append(datetime.now())
            params.append(email)
            
            query = f"UPDATE contacts SET {', '.join(set_parts)} WHERE email = ?"
            rows_affected = self.execute_query(query, params)
            
            return rows_affected > 0
        except Exception as e:
            print(f"❌ 更新联系人失败: {e}")
            return False
    
    def delete_contact(self, email: str) -> bool:
        """删除联系人（同时删除相关消息）"""
        try:
            query = "DELETE FROM contacts WHERE email = ?"
            rows_affected = self.execute_query(query, (email,))
            
            if rows_affected > 0:
                print(f"✅ 删除联系人成功: {email}")
                return True
            return False
        except Exception as e:
            print(f"❌ 删除联系人失败: {e}")
            return False
    
    # ==================== 消息相关操作 ====================
    
    def add_message(self, contact_email: str, sender_email: str, receiver_email: str,
                   content: str, message_type: str = 'text', message_id: str = None,
                   attachment_path: str = None, is_sent: bool = True) -> bool:
        """添加消息"""
        try:
            query = """
                INSERT INTO messages (contact_email, message_id, sender_email, receiver_email,
                                    content, message_type, attachment_path, is_sent, sent_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            now = datetime.now()
            self.execute_query(query, (
                contact_email, message_id, sender_email, receiver_email,
                content, message_type, attachment_path, is_sent, now, now
            ))
            
            # 更新联系人的最后消息信息
            self.update_contact(contact_email,
                              last_message_time=now,
                              last_message_content=content)
            
            # 如果是接收的消息，增加未读计数
            if not is_sent:
                contact = self.get_contact_by_email(contact_email)
                if contact:
                    new_unread = (contact.get('unread_count', 0) or 0) + 1
                    self.update_contact(contact_email, unread_count=new_unread)
            
            return True
        except Exception as e:
            print(f"❌ 添加消息失败: {e}")
            return False
    
    def get_messages(self, contact_email: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取与指定联系人的消息记录"""
        try:
            query = """
                SELECT * FROM messages 
                WHERE contact_email = ?
                ORDER BY sent_at ASC, created_at ASC
                LIMIT ? OFFSET ?
            """
            rows = self.execute_query(query, (contact_email, limit, offset))
            
            messages = []
            for row in rows:
                message = dict(row)
                message['is_read'] = bool(message['is_read'])
                message['is_sent'] = bool(message['is_sent'])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ 获取消息失败: {e}")
            return []
    
    def mark_messages_as_read(self, contact_email: str) -> bool:
        """标记消息为已读"""
        try:
            # 标记消息为已读
            query = "UPDATE messages SET is_read = TRUE WHERE contact_email = ? AND is_read = FALSE"
            self.execute_query(query, (contact_email,))
            
            # 清除未读计数
            self.update_contact(contact_email, unread_count=0)
            
            return True
        except Exception as e:
            print(f"❌ 标记消息已读失败: {e}")
            return False
    
    def delete_messages(self, contact_email: str) -> bool:
        """删除与指定联系人的所有消息"""
        try:
            query = "DELETE FROM messages WHERE contact_email = ?"
            rows_affected = self.execute_query(query, (contact_email,))
            
            # 清空联系人的最后消息信息
            self.update_contact(contact_email,
                              last_message_time=None,
                              last_message_content=None,
                              unread_count=0)
            
            print(f"✅ 删除消息成功: {rows_affected} 条消息")
            return True
        except Exception as e:
            print(f"❌ 删除消息失败: {e}")
            return False
    
    # ==================== 设置相关操作 ====================
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取设置值"""
        try:
            query = "SELECT value, data_type FROM settings WHERE key = ?"
            row = self.execute_query(query, (key,), fetch_one=True)
            
            if row:
                value, data_type = row['value'], row['data_type']
                
                # 根据数据类型转换值
                if data_type == 'boolean':
                    return value.lower() in ('true', '1', 'yes')
                elif data_type == 'integer':
                    return int(value)
                elif data_type == 'float':
                    return float(value)
                elif data_type == 'json':
                    return json.loads(value)
                else:
                    return value
            
            return default
        except Exception as e:
            print(f"❌ 获取设置失败: {key} - {e}")
            return default
    
    def set_setting(self, key: str, value: Any, data_type: str = 'string', 
                   description: str = None, init_mode: bool = False) -> bool:
        """设置配置值"""
        try:
            # 转换值为字符串
            if isinstance(value, bool):
                str_value = str(value).lower()
                data_type = 'boolean'
            elif isinstance(value, int):
                str_value = str(value)
                data_type = 'integer'
            elif isinstance(value, float):
                str_value = str(value)
                data_type = 'float'
            elif isinstance(value, (dict, list)):
                str_value = json.dumps(value)
                data_type = 'json'
            else:
                str_value = str(value)
            
            # 检查是否存在
            existing = self.execute_query("SELECT key FROM settings WHERE key = ?", (key,), fetch_one=True)
            
            if existing and not init_mode:
                # 更新现有设置
                query = "UPDATE settings SET value = ?, data_type = ?, description = ?, updated_at = ? WHERE key = ?"
                self.execute_query(query, (str_value, data_type, description, datetime.now(), key))
            elif not existing:
                # 插入新设置
                query = "INSERT INTO settings (key, value, data_type, description, updated_at) VALUES (?, ?, ?, ?, ?)"
                self.execute_query(query, (key, str_value, data_type, description, datetime.now()))
            
            return True
        except Exception as e:
            print(f"❌ 设置配置失败: {key} - {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        try:
            query = "SELECT key, value, data_type FROM settings"
            rows = self.execute_query(query)
            
            settings = {}
            for row in rows:
                key, value, data_type = row['key'], row['value'], row['data_type']
                
                # 转换数据类型
                if data_type == 'boolean':
                    settings[key] = value.lower() in ('true', '1', 'yes')
                elif data_type == 'integer':
                    settings[key] = int(value)
                elif data_type == 'float':
                    settings[key] = float(value)
                elif data_type == 'json':
                    settings[key] = json.loads(value)
                else:
                    settings[key] = value
            
            return settings
        except Exception as e:
            print(f"❌ 获取所有设置失败: {e}")
            return {}
    
    # ==================== 搜索和统计 ====================
    
    def search_contacts(self, keyword: str) -> List[Dict]:
        """搜索联系人"""
        try:
            query = """
                SELECT * FROM contacts 
                WHERE (nickname LIKE ? OR email LIKE ?) AND is_blocked = FALSE
                ORDER BY nickname ASC
            """
            keyword_pattern = f"%{keyword}%"
            rows = self.execute_query(query, (keyword_pattern, keyword_pattern))
            
            contacts = []
            for row in rows:
                contact = dict(row)
                contact['unread_count'] = contact['unread_count'] or 0
                contact['is_blocked'] = bool(contact['is_blocked'])
                contact['is_online'] = bool(contact['is_online'])
                contacts.append(contact)
            
            return contacts
        except Exception as e:
            print(f"❌ 搜索联系人失败: {e}")
            return []
    
    def search_messages(self, keyword: str, contact_email: str = None) -> List[Dict]:
        """搜索消息"""
        try:
            query = "SELECT * FROM messages WHERE content LIKE ?"
            params = [f"%{keyword}%"]
            
            if contact_email:
                query += " AND contact_email = ?"
                params.append(contact_email)
            
            query += " ORDER BY sent_at DESC LIMIT 100"
            
            rows = self.execute_query(query, params)
            
            messages = []
            for row in rows:
                message = dict(row)
                message['is_read'] = bool(message['is_read'])
                message['is_sent'] = bool(message['is_sent'])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ 搜索消息失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            stats = {}
            
            # 联系人统计
            stats['total_contacts'] = self.execute_query("SELECT COUNT(*) as count FROM contacts", fetch_one=True)['count']
            stats['blocked_contacts'] = self.execute_query("SELECT COUNT(*) as count FROM contacts WHERE is_blocked = TRUE", fetch_one=True)['count']
            stats['online_contacts'] = self.execute_query("SELECT COUNT(*) as count FROM contacts WHERE is_online = TRUE", fetch_one=True)['count']
            
            # 消息统计
            stats['total_messages'] = self.execute_query("SELECT COUNT(*) as count FROM messages", fetch_one=True)['count']
            stats['unread_messages'] = self.execute_query("SELECT SUM(unread_count) as count FROM contacts", fetch_one=True)['count'] or 0
            stats['sent_messages'] = self.execute_query("SELECT COUNT(*) as count FROM messages WHERE is_sent = TRUE", fetch_one=True)['count']
            stats['received_messages'] = self.execute_query("SELECT COUNT(*) as count FROM messages WHERE is_sent = FALSE", fetch_one=True)['count']
            
            return stats
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}
    
    # ==================== 数据管理 ====================
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据库"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ 数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            return False
    
    def vacuum_database(self) -> bool:
        """优化数据库"""
        try:
            self.execute_query("VACUUM")
            print("✅ 数据库优化完成")
            return True
        except Exception as e:
            print(f"❌ 数据库优化失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        with self.lock:
            if self.connection:
                self.connection.close()
                self.connection = None
                print("📊 数据库连接已关闭")
    
    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close() 