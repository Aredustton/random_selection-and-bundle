import random
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QSpinBox, QGroupBox,
                           QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt

class RandomNameTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 角色输入区域
        input_group = QGroupBox("角色输入")
        input_layout = QVBoxLayout()
        
        # 角色输入说明
        input_label = QLabel("请输入角色列表（支持空格、逗号、分号、回车等分隔）：")
        self.name_input = QTextEdit()
        self.name_input.setPlaceholderText("例如：张三 李四,王五;赵六\n或者：\n张三 2\n李四 3\n（数字代表重复次数）")
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.name_input)
        input_group.setLayout(input_layout)
        
        # 抽取设置区域
        settings_group = QGroupBox("抽取设置")
        settings_layout = QFormLayout()
        
        # 抽取数量设置
        draw_count_layout = QHBoxLayout()
        self.draw_count = QSpinBox()
        self.draw_count.setMinimum(1)
        self.draw_count.setMaximum(1000)
        self.draw_count.setValue(1)
        draw_count_layout.addWidget(self.draw_count)
        
        settings_layout.addRow("抽取数量：", draw_count_layout)
        settings_group.setLayout(settings_layout)
        
        # 结果显示区域
        result_group = QGroupBox("抽取结果")
        result_layout = QVBoxLayout()
        
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        
        result_layout.addWidget(self.result_display)
        result_group.setLayout(result_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.draw_button = QPushButton("开始抽取")
        self.draw_button.clicked.connect(self.draw_random_names)
        self.clear_button = QPushButton("清空")
        self.clear_button.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.draw_button)
        button_layout.addWidget(self.clear_button)
        
        # 添加所有组件到主布局
        main_layout.addWidget(input_group, 3)
        main_layout.addWidget(settings_group, 1)
        main_layout.addWidget(result_group, 3)
        main_layout.addLayout(button_layout)
        
    def parse_names(self, text):
        """解析输入的角色列表"""
        names = []
        
        # 按行分割
        lines = text.strip().split("\n")
        
        for line in lines:
            if not line.strip():
                continue
                
            # 处理每行
            items = re.split(r'[,;\s]+', line.strip())
            
            i = 0
            while i < len(items):
                if i + 1 < len(items) and items[i+1].isdigit():
                    # 如果下一项是数字，将当前名称重复指定次数
                    names.extend([items[i]] * int(items[i+1]))
                    i += 2
                else:
                    names.append(items[i])
                    i += 1
        
        return names
        
    def draw_random_names(self):
        """随机抽取指定数量的角色"""
        text = self.name_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "请先输入角色列表！")
            return
            
        names = self.parse_names(text)
        if not names:
            QMessageBox.warning(self, "警告", "未能解析到有效的角色名称！")
            return
            
        draw_count = self.draw_count.value()
        
        if draw_count > 0:
            # 随机抽取
            result = random.choices(names, k=draw_count)
            
            # 显示结果
            result_text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(result)])
            self.result_display.setText(result_text)
        else:
            QMessageBox.warning(self, "警告", "抽取数量必须大于0！")
    
    def clear_all(self):
        """清空所有输入和结果"""
        self.name_input.clear()
        self.result_display.clear()
        self.draw_count.setValue(1) 