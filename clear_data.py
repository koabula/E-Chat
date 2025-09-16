#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 数据清理脚本

清除测试数据，让用户从干净状态开始
"""

import os
import sys
from pathlib import Path

def clear_database():
    """清理数据库"""
    database_file = Path("database.db")
    
    if database_file.exists():
        try:
            database_file.unlink()
            print("✅ 已删除数据库文件 database.db")
        except Exception as e:
            print(f"❌ 删除数据库文件失败: {e}")
            return False
    else:
        print("ℹ️ 数据库文件不存在")
    
    return True

def clear_config():
    """清理配置文件（可选）"""
    config_file = Path("config.ini")
    
    if config_file.exists():
        try:
            config_file.unlink()
            print("✅ 已删除配置文件 config.ini")
        except Exception as e:
            print(f"❌ 删除配置文件失败: {e}")
            return False
    else:
        print("ℹ️ 配置文件不存在")
    
    return True

def main():
    """主函数"""
    print("🧹 E-Chat 数据清理工具")
    print("=" * 40)
    
    # 确认操作
    choice = input("是否要清理所有数据？这将删除:\n- 所有联系人\n- 所有聊天记录\n- 邮箱配置\n\n请输入 'yes' 确认，或按Enter取消: ")
    
    if choice.lower() != 'yes':
        print("👋 操作已取消")
        return
    
    print("\n🧹 开始清理数据...")
    
    # 清理数据库
    if not clear_database():
        sys.exit(1)
    
    # 询问是否清理配置
    clear_config_choice = input("\n是否也要清理邮箱配置？(y/N): ")
    if clear_config_choice.lower() in ['y', 'yes']:
        if not clear_config():
            sys.exit(1)
    
    print("\n✅ 数据清理完成！")
    print("现在可以重新启动 E-Chat，从干净状态开始使用。")

if __name__ == "__main__":
    main() 