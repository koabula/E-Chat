#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Chat 邮件即时通讯软件 - 主程序入口

基于CustomTkinter的现代化邮件即时通讯客户端
使用电子邮件协议实现实时通讯功能
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """主程序入口"""
    try:
        # 导入主应用类
        from src.app import EChatApp
        
        # 创建并运行应用
        app = EChatApp()
        app.run()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖包: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 