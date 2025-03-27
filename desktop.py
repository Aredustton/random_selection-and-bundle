#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut():
    """创建桌面快捷方式"""
    try:
        # 获取当前脚本路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 创建桌面快捷方式
        desktop = winshell.desktop()
        path = os.path.join(desktop, "多功能随机工具.lnk")
        
        # 获取启动脚本的完整路径
        target = os.path.join(current_dir, "start.pyw")
        wDir = current_dir
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = os.path.join(current_dir, "app.py")  # 使用主程序作为图标
        shortcut.save()
        
        print("桌面快捷方式创建成功！")
        return True
    except Exception as e:
        print(f"创建快捷方式时出错: {e}")
        return False

if __name__ == "__main__":
    create_shortcut()
    input("按Enter键退出...") 