#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 确保当前目录在路径中，以便正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入主程序并运行
from PyQt5.QtWidgets import QApplication
from app import MainApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_()) 