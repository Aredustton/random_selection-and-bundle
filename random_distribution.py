import random
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QSpinBox, QGroupBox,
                           QFormLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt

class RandomDistributionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 角色和物品输入区域
        input_layout = QHBoxLayout()
        
        # 角色输入组
        roles_group = QGroupBox("角色列表")
        roles_layout = QVBoxLayout()
        
        roles_label = QLabel("请输入角色列表（支持多种格式）：")
        self.roles_input = QTextEdit()
        self.roles_input.setPlaceholderText("支持多种格式：\n"
                                           "1. 张三 李四 王五\n"
                                           "2. 张三,李四,王五\n"
                                           "3. 张三;李四;王五\n"
                                           "4. 张三 2\n李四\n王五 3\n"
                                           "5. 张三(2), 李四, 王五(3)")
        
        roles_layout.addWidget(roles_label)
        roles_layout.addWidget(self.roles_input)
        roles_group.setLayout(roles_layout)
        
        # 物品输入组
        items_group = QGroupBox("物品列表")
        items_layout = QVBoxLayout()
        
        items_label = QLabel("请输入物品列表（支持多种格式）：")
        self.items_input = QTextEdit()
        self.items_input.setPlaceholderText("支持多种格式：\n"
                                           "1. 苹果 10\n香蕉 5\n橙子 8\n"
                                           "2. 苹果(10), 香蕉(5), 橙子(8)\n"
                                           "3. 苹果:10, 香蕉:5, 橙子:8\n"
                                           "4. 苹果10个, 香蕉5个, 橙子8个")
        
        items_layout.addWidget(items_label)
        items_layout.addWidget(self.items_input)
        items_group.setLayout(items_layout)
        
        input_layout.addWidget(roles_group)
        input_layout.addWidget(items_group)
        
        # 分配设置区域
        settings_group = QGroupBox("分配设置")
        settings_layout = QVBoxLayout()
        
        # 启用个性化分配设置
        self.use_custom_allocation = QCheckBox("使用角色输入框中指定的物品数量")
        self.use_custom_allocation.setChecked(True)
        settings_layout.addWidget(self.use_custom_allocation)
        
        # 分割线
        settings_layout.addWidget(QLabel("--- 或者使用统一设置 ---"))
        
        # 每人分配数量（统一设置）
        unified_layout = QHBoxLayout()
        unified_label = QLabel("每人统一分配物品数量：")
        self.items_per_person = QSpinBox()
        self.items_per_person.setMinimum(1)
        self.items_per_person.setMaximum(100)
        self.items_per_person.setValue(1)
        self.items_per_person.setEnabled(False)  # 默认禁用，因为默认使用个性化设置
        
        unified_layout.addWidget(unified_label)
        unified_layout.addWidget(self.items_per_person)
        unified_layout.addStretch()
        
        # 连接复选框信号
        self.use_custom_allocation.stateChanged.connect(self.toggle_allocation_mode)
        
        settings_layout.addLayout(unified_layout)
        settings_group.setLayout(settings_layout)
        
        # 结果显示区域
        result_group = QGroupBox("分配结果")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget(0, 0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.distribute_button = QPushButton("开始分配")
        self.distribute_button.clicked.connect(self.distribute_items)
        self.clear_button = QPushButton("清空")
        self.clear_button.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.distribute_button)
        button_layout.addWidget(self.clear_button)
        
        # 添加所有组件到主布局
        main_layout.addLayout(input_layout, 3)
        main_layout.addWidget(settings_group, 1)
        main_layout.addWidget(result_group, 4)
        main_layout.addLayout(button_layout)
        
    def toggle_allocation_mode(self, state):
        """切换分配模式"""
        self.items_per_person.setEnabled(not state)
        
    def parse_roles(self, text):
        """解析输入的角色列表，返回角色名和对应分配数量，支持多种格式"""
        roles_data = {}  # 角色名 -> 分配数量
        
        # 如果没有任何输入，返回空字典
        if not text.strip():
            return roles_data
            
        # 情况1: 一行多个角色，用分隔符(空格、逗号、分号)分隔
        if '\n' not in text and any(sep in text for sep in [' ', ',', ';']):
            # 尝试按照逗号和分号拆分
            if ',' in text:
                parts = text.split(',')
            elif ';' in text:
                parts = text.split(';')
            else:
                parts = text.split()
                
            for part in parts:
                if not part.strip():
                    continue
                    
                # 检查是否有括号格式的数量 例如: 张三(2)
                match = re.search(r'(.*?)\s*[\(（](\d+)[\)）]', part)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    roles_data[name] = max(1, count)
                else:
                    roles_data[part.strip()] = 1
                    
        else:
            # 情况2: 每行一个角色，可能带数量
            lines = text.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                    
                # 检查是否有括号格式的数量 例如: 张三(2)
                match = re.search(r'(.*?)\s*[\(（](\d+)[\)）]', line)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    roles_data[name] = max(1, count)
                else:
                    # 检查是否有空格后的数字 例如: 张三 2
                    parts = line.strip().split()
                    if len(parts) > 1 and parts[-1].isdigit():
                        name = ' '.join(parts[:-1])
                        count = int(parts[-1])
                        roles_data[name] = max(1, count)
                    else:
                        roles_data[line.strip()] = 1
                        
        return roles_data
        
    def parse_items(self, text):
        """解析输入的物品列表，支持多种格式"""
        items = {}  # 物品名称 -> 数量
        
        # 如果没有任何输入，返回空字典
        if not text.strip():
            return items
            
        # 分情况处理不同格式
        if ',' in text and ('\n' not in text or text.count(',') > text.count('\n')):
            # 逗号分隔格式: 苹果(10), 香蕉(5), 橙子(8) 或 苹果:10, 香蕉:5, 橙子:8
            parts = text.split(',')
            for part in parts:
                if not part.strip():
                    continue
                    
                # 尝试匹配不同格式
                # 格式1: 苹果(10)
                match = re.search(r'(.*?)\s*[\(（](\d+)[\)）]', part)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                    continue
                    
                # 格式2: 苹果:10 或 苹果：10
                match = re.search(r'(.*?)\s*[:：]\s*(\d+)', part)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                    continue
                    
                # 格式3: 苹果10个
                match = re.search(r'(.*?)(\d+)[个|份|件|样|箱]', part)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                    continue
                    
                # 格式4: 苹果 10
                match = re.search(r'(.*?)\s+(\d+)$', part)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                else:
                    # 如果没有数量，默认为1
                    items[part.strip()] = 1
        else:
            # 每行一个物品格式
            lines = text.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                    
                # 尝试匹配不同格式
                # 格式1: 苹果(10)
                match = re.search(r'(.*?)\s*[\(（](\d+)[\)）]', line)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                    continue
                    
                # 格式2: 苹果:10 或 苹果：10
                match = re.search(r'(.*?)\s*[:：]\s*(\d+)', line)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                    continue
                    
                # 格式3: 苹果10个
                match = re.search(r'(.*?)(\d+)[个|份|件|样|箱]', line)
                if match:
                    name = match.group(1).strip()
                    count = int(match.group(2))
                    items[name] = count
                    continue
                    
                # 格式4: 最后尝试空格分隔: 苹果 10
                parts = line.strip().split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    name = ' '.join(parts[:-1])
                    count = int(parts[-1])
                    items[name] = count
                else:
                    # 如果没有数量标识，默认为1
                    items[line.strip()] = 1
                    
        return items
        
    def distribute_items(self):
        """随机分配物品给角色"""
        roles_text = self.roles_input.toPlainText().strip()
        items_text = self.items_input.toPlainText().strip()
        
        if not roles_text or not items_text:
            QMessageBox.warning(self, "警告", "请先输入角色和物品列表！")
            return
            
        use_custom = self.use_custom_allocation.isChecked()
        roles_data = self.parse_roles(roles_text)
        items_dict = self.parse_items(items_text)
        
        if not roles_data:
            QMessageBox.warning(self, "警告", "未能解析到有效的角色！")
            return
            
        if not items_dict:
            QMessageBox.warning(self, "警告", "未能解析到有效的物品！")
            return
            
        # 计算所需物品总数
        if use_custom:
            # 使用自定义分配
            total_items_needed = sum(roles_data.values())
        else:
            # 使用统一分配
            items_per_person = self.items_per_person.value()
            for role in roles_data:
                roles_data[role] = items_per_person
            total_items_needed = len(roles_data) * items_per_person
        
        # 创建物品池
        items_pool = []
        for item_name, count in items_dict.items():
            items_pool.extend([item_name] * count)
            
        if len(items_pool) < total_items_needed:
            QMessageBox.warning(self, "警告", f"物品总数({len(items_pool)})不足以分配给所有角色(需要{total_items_needed})！")
            return
            
        # 随机打乱物品
        random.shuffle(items_pool)
        
        # 分配物品
        distribution = {role: [] for role in roles_data.keys()}
        current_idx = 0
        
        for role, count in roles_data.items():
            end_idx = current_idx + count
            distribution[role] = items_pool[current_idx:end_idx]
            current_idx = end_idx
            
        # 统计剩余物品
        remaining_items = items_pool[total_items_needed:]
        remaining_count = {}
        for item in remaining_items:
            remaining_count[item] = remaining_count.get(item, 0) + 1
            
        # 显示分配结果
        self.display_results(distribution, remaining_count)
        
    def display_results(self, distribution, remaining):
        """在表格中显示分配结果"""
        if not distribution:
            return
            
        # 获取所有分配的物品种类
        all_items = set()
        for items in distribution.values():
            all_items.update(items)
            
        # 按字母顺序排序物品
        sorted_items = sorted(all_items)
        
        # 设置表格大小
        self.result_table.setRowCount(len(distribution) + 1)  # +1 行用于显示剩余
        self.result_table.setColumnCount(len(sorted_items) + 1)  # +1 列用于显示角色名
        
        # 设置表头
        headers = ["角色"] + sorted_items
        self.result_table.setHorizontalHeaderLabels(headers)
        
        # 填充表格
        for row, (role, items) in enumerate(distribution.items()):
            # 角色名称
            self.result_table.setItem(row, 0, QTableWidgetItem(role))
            
            # 物品数量
            for col, item_name in enumerate(sorted_items, 1):
                count = items.count(item_name)
                if count > 0:
                    self.result_table.setItem(row, col, QTableWidgetItem(str(count)))
                else:
                    self.result_table.setItem(row, col, QTableWidgetItem(""))
                    
        # 最后一行显示剩余物品
        self.result_table.setItem(len(distribution), 0, QTableWidgetItem("剩余"))
        for col, item_name in enumerate(sorted_items, 1):
            count = remaining.get(item_name, 0)
            if count > 0:
                self.result_table.setItem(len(distribution), col, QTableWidgetItem(str(count)))
            else:
                self.result_table.setItem(len(distribution), col, QTableWidgetItem(""))
                
    def clear_all(self):
        """清空所有输入和结果"""
        self.roles_input.clear()
        self.items_input.clear()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(0)
        self.items_per_person.setValue(1) 