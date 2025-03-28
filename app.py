import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                           QTextEdit, QSpinBox, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QLineEdit, QGridLayout,
                           QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from random_name import RandomNameTab
from random_distribution import RandomDistributionTab
from bundle_distribution import BundleDistributionTab

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("随机满赠上捆工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(main_widget)
        
        # 创建选项卡部件
        tab_widget = QTabWidget()
        
        # 添加三个功能选项卡
        self.random_name_tab = RandomNameTab()
        self.random_distribution_tab = RandomDistributionTab()
        self.bundle_distribution_tab = BundleDistributionTab()
        
        tab_widget.addTab(self.random_name_tab, "随机上捆")
        tab_widget.addTab(self.random_distribution_tab, "随机分配")
        tab_widget.addTab(self.bundle_distribution_tab, "一键上捆")
        
        main_layout.addWidget(tab_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_()) 