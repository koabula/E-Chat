#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 配置管理模块

负责处理应用配置文件、用户设置和邮箱配置
"""

import configparser
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from cryptography.fernet import Fernet
import base64
import json

# 导入语言管理器
from src.language_manager import language_manager


class ConfigManager:
    """配置管理器 - 负责所有配置的读取、保存和加密"""
    
    def __init__(self, config_file: str = "config.ini"):
        """初始化配置管理器"""
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.encryption_key = None
        
        # 加载配置
        self.load_config()
        
        # 初始化加密
        self.init_encryption()
        
        print("⚙️ 配置管理器初始化完成")
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file, encoding='utf-8')
                print(f"✅ 配置文件加载成功: {self.config_file}")
            else:
                # 创建默认配置
                self.create_default_config()
                print(f"📝 创建默认配置文件: {self.config_file}")
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        try:
            # 邮件配置
            self.config['email'] = {
                'smtp_server': '',
                'smtp_port': '587',
                'imap_server': '',
                'imap_port': '993',
                'username': '',
                'password_encrypted': '',
                'use_ssl': 'true',
                'timeout': '30'
            }
            
            # 界面配置
            self.config['ui'] = {
                'theme': 'light',
                'language': 'en',
                'font_size': '12',
                'font_family': 'Arial',
                'window_size': '1200x800',
                'window_position': 'center',
                'auto_hide_to_tray': 'false'
            }
            
            # 应用配置
            self.config['app'] = {
                'auto_start': 'false',
                'notifications': 'true',
                'sound_notifications': 'true',
                'polling_interval': '30',
                'idle_enabled': 'true',
                'polling_mode': 'auto',
                'idle_test_result': '',
                'max_message_length': '5000',
                'auto_save_draft': 'true',
                'keep_message_history': 'true',
                'max_history_days': '365'
            }
            
            # 安全配置
            self.config['security'] = {
                'auto_lock': 'false',
                'lock_timeout': '300',
                'remember_password': 'false',
                'encryption_enabled': 'true'
            }
            
            # 高级配置
            self.config['advanced'] = {
                'debug_mode': 'false',
                'log_level': 'INFO',
                'max_log_size': '10',
                'backup_enabled': 'true',
                'backup_interval': '7'
            }
            
            # 保存默认配置
            self.save_config()
            
        except Exception as e:
            print(f"❌ 创建默认配置失败: {e}")
            raise
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            print(f"💾 配置文件保存成功: {self.config_file}")
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
            raise
    
    # ==================== 通用配置操作 ====================
    
    def get(self, section: str, key: str, default: Any = None, value_type: type = str) -> Any:
        """获取配置值"""
        try:
            if not self.config.has_section(section):
                return default
            
            if not self.config.has_option(section, key):
                return default
            
            value = self.config.get(section, key)
            
            # 类型转换
            if value_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif value_type == int:
                return int(value)
            elif value_type == float:
                return float(value)
            elif value_type == list:
                return json.loads(value)
            elif value_type == dict:
                return json.loads(value)
            else:
                return value
                
        except Exception as e:
            print(f"❌ 获取配置失败: {section}.{key} - {e}")
            return default
    
    def set(self, section: str, key: str, value: Any):
        """设置配置值"""
        try:
            # 确保section存在
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            # 转换值为字符串
            if isinstance(value, bool):
                str_value = str(value).lower()
            elif isinstance(value, (list, dict)):
                str_value = json.dumps(value)
            else:
                str_value = str(value)
            
            self.config.set(section, key, str_value)
            
        except Exception as e:
            print(f"❌ 设置配置失败: {section}.{key} - {e}")
            raise
    
    def has_section(self, section: str) -> bool:
        """检查section是否存在"""
        return self.config.has_section(section)
    
    def has_option(self, section: str, key: str) -> bool:
        """检查配置项是否存在"""
        return self.config.has_option(section, key)
    
    def remove_option(self, section: str, key: str) -> bool:
        """删除配置项"""
        try:
            if self.config.has_section(section):
                return self.config.remove_option(section, key)
            return False
        except Exception as e:
            print(f"❌ 删除配置失败: {section}.{key} - {e}")
            return False
    
    # ==================== 邮件配置 ====================
    
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        return {
            'smtp_server': self.get('email', 'smtp_server', ''),
            'smtp_port': self.get('email', 'smtp_port', 587, int),
            'imap_server': self.get('email', 'imap_server', ''),
            'imap_port': self.get('email', 'imap_port', 993, int),
            'username': self.get('email', 'username', ''),
            'password': self.get_decrypted_password(),
            'use_ssl': self.get('email', 'use_ssl', True, bool),
            'timeout': self.get('email', 'timeout', 30, int),
            'inbox_folder': self.get('email', 'inbox_folder', '')  # 自定义收件箱文件夹
        }
    
    def set_email_config(self, smtp_server: str, smtp_port: int, imap_server: str, 
                        imap_port: int, username: str, password: str, use_ssl: bool = True,
                        inbox_folder: str = ''):
        """设置邮件配置"""
        try:
            self.set('email', 'smtp_server', smtp_server)
            self.set('email', 'smtp_port', smtp_port)
            self.set('email', 'imap_server', imap_server)
            self.set('email', 'imap_port', imap_port)
            self.set('email', 'username', username)
            self.set('email', 'use_ssl', use_ssl)
            self.set('email', 'inbox_folder', inbox_folder)
            
            # 加密存储密码
            self.set_encrypted_password(password)
            
            print("✅ 邮件配置保存成功")
        except Exception as e:
            print(f"❌ 邮件配置保存失败: {e}")
            raise
    
    # ==================== UI配置 ====================
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取界面配置"""
        return {
            'theme': self.get('ui', 'theme', 'dark'),
            'language': self.get('ui', 'language', 'en'),
            'font_size': self.get('ui', 'font_size', 12, int),
            'font_family': self.get('ui', 'font_family', 'Arial'),
            'window_size': self.get('ui', 'window_size', '1200x800'),
            'window_position': self.get('ui', 'window_position', 'center'),
            'auto_hide_to_tray': self.get('ui', 'auto_hide_to_tray', False, bool)
        }
    
    def set_ui_config(self, **kwargs):
        """设置界面配置"""
        try:
            for key, value in kwargs.items():
                if key in ['theme', 'language', 'font_size', 'font_family', 
                          'window_size', 'window_position', 'auto_hide_to_tray']:
                    self.set('ui', key, value)
            
            print("✅ 界面配置保存成功")
        except Exception as e:
            print(f"❌ 界面配置保存失败: {e}")
            raise
    
    # ==================== 应用配置 ====================
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        sound_value = self.get('app', 'sound', None, bool)
        if sound_value is None:
            # 向后兼容：如果没有'sound'字段，尝试'sound_notifications'
            sound_value = self.get('app', 'sound_notifications', True, bool)
        
        return {
            'auto_start': self.get('app', 'auto_start', False, bool),
            'notifications': self.get('app', 'notifications', True, bool),
            'sound': sound_value,
            'sound_notifications': self.get('app', 'sound_notifications', True, bool),
            'polling_interval': self.get('app', 'polling_interval', 30, int),
            'idle_enabled': self.get('app', 'idle_enabled', True, bool),
            'polling_mode': self.get('app', 'polling_mode', 'auto'),
            'idle_test_result': self.get('app', 'idle_test_result', None),
            'max_message_length': self.get('app', 'max_message_length', 5000, int),
            'auto_save_draft': self.get('app', 'auto_save_draft', True, bool),
            'keep_message_history': self.get('app', 'keep_message_history', True, bool),
            'max_history_days': self.get('app', 'max_history_days', 365, int)
        }
    
    def set_app_config(self, **kwargs):
        """设置应用配置"""
        try:
            for key, value in kwargs.items():
                if key in ['auto_start', 'notifications', 'sound', 'sound_notifications', 
                          'polling_interval', 'idle_enabled', 'polling_mode', 'idle_test_result',
                          'max_message_length', 'auto_save_draft', 'keep_message_history', 'max_history_days']:
                    self.set('app', key, value)
            
            print("✅ 应用配置保存成功")
        except Exception as e:
            print(f"❌ 应用配置保存失败: {e}")
            raise
    
    # ==================== 密码加密 ====================
    
    def init_encryption(self):
        """初始化加密密钥"""
        try:
            key_file = Path("encryption.key")
            
            if key_file.exists():
                # 加载现有密钥
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # 生成新密钥
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                
                # 设置文件权限（仅所有者可读写）
                os.chmod(key_file, 0o600)
            
            print("🔐 加密系统初始化完成")
            
        except Exception as e:
            print(f"❌ 加密系统初始化失败: {e}")
            # 使用默认密钥（不安全，仅用于开发）
            self.encryption_key = base64.urlsafe_b64encode(b'development_key_not_secure!' + b'0' * 11)
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        try:
            if not data:
                return ""
            
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"❌ 数据加密失败: {e}")
            return data  # 返回原始数据（不安全）
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            if not encrypted_data:
                return ""
            
            fernet = Fernet(self.encryption_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            print(f"❌ 数据解密失败: {e}")
            return encrypted_data  # 返回原始数据
    
    def set_encrypted_password(self, password: str):
        """设置加密密码"""
        encrypted_password = self.encrypt_data(password)
        self.set('email', 'password_encrypted', encrypted_password)
    
    def get_decrypted_password(self) -> str:
        """获取解密密码"""
        encrypted_password = self.get('email', 'password_encrypted', '')
        if encrypted_password:
            return self.decrypt_data(encrypted_password)
        return ''
    
    # ==================== 语言配置同步 ====================
    
    def sync_language_setting(self):
        """同步语言设置到语言管理器"""
        try:
            current_language = self.get('ui', 'language', 'en')
            language_manager.set_language(current_language)
            print(f"🌐 语言设置已同步: {current_language}")
        except Exception as e:
            print(f"❌ 语言设置同步失败: {e}")
    
    def update_language_setting(self, language_code: str):
        """更新语言设置"""
        try:
            self.set('ui', 'language', language_code)
            language_manager.set_language(language_code)
            self.save_config()
            print(f"🌐 语言设置已更新: {language_code}")
        except Exception as e:
            print(f"❌ 语言设置更新失败: {e}")
            raise
    
    # ==================== 配置验证 ====================
    
    def validate_email_config(self) -> bool:
        """验证邮件配置"""
        config = self.get_email_config()
        
        required_fields = ['smtp_server', 'imap_server', 'username']
        for field in required_fields:
            if not config.get(field):
                print(f"❌ 邮件配置验证失败: {field} 不能为空")
                return False
        
        # 验证端口号
        if not (1 <= config['smtp_port'] <= 65535):
            print(f"❌ 邮件配置验证失败: SMTP端口号无效")
            return False
        
        if not (1 <= config['imap_port'] <= 65535):
            print(f"❌ 邮件配置验证失败: IMAP端口号无效")
            return False
        
        print("✅ 邮件配置验证通过")
        return True
    
    def validate_ui_config(self) -> bool:
        """验证界面配置"""
        config = self.get_ui_config()
        
        # 验证主题
        if config['theme'] not in ['light', 'dark']:
            print(f"❌ 界面配置验证失败: 主题无效")
            return False
        
        # 验证语言
        if config['language'] not in ['en', 'zh']:
            print(f"❌ 界面配置验证失败: 语言无效")
            return False
        
        # 验证字体大小
        if not (8 <= config['font_size'] <= 72):
            print(f"❌ 界面配置验证失败: 字体大小无效")
            return False
        
        print("✅ 界面配置验证通过")
        return True
    
    # ==================== 配置备份和恢复 ====================
    
    def backup_config(self, backup_path: str) -> bool:
        """备份配置文件"""
        try:
            import shutil
            shutil.copy2(self.config_file, backup_path)
            print(f"✅ 配置文件备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 配置文件备份失败: {e}")
            return False
    
    def restore_config(self, backup_path: str) -> bool:
        """恢复配置文件"""
        try:
            import shutil
            shutil.copy2(backup_path, self.config_file)
            self.load_config()
            print(f"✅ 配置文件恢复成功: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 配置文件恢复失败: {e}")
            return False
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        try:
            self.config.clear()
            self.create_default_config()
            print("✅ 配置已重置为默认值")
        except Exception as e:
            print(f"❌ 配置重置失败: {e}")
            raise
    
    # ==================== 配置导入导出 ====================
    
    def export_config(self, export_path: str, include_password: bool = False) -> bool:
        """导出配置（JSON格式）"""
        try:
            config_dict = {}
            
            for section_name in self.config.sections():
                config_dict[section_name] = {}
                for key, value in self.config.items(section_name):
                    # 是否包含密码
                    if not include_password and 'password' in key:
                        continue
                    config_dict[section_name][key] = value
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置导出成功: {export_path}")
            return True
        except Exception as e:
            print(f"❌ 配置导出失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """导入配置（JSON格式）"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            for section_name, section_data in config_dict.items():
                if not self.config.has_section(section_name):
                    self.config.add_section(section_name)
                
                for key, value in section_data.items():
                    self.config.set(section_name, key, str(value))
            
            self.save_config()
            print(f"✅ 配置导入成功: {import_path}")
            return True
        except Exception as e:
            print(f"❌ 配置导入失败: {e}")
            return False 