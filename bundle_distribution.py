import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QSpinBox, QGroupBox,
                           QFormLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QComboBox, QLineEdit,
                           QGridLayout)
from PyQt5.QtCore import Qt

class CharacterInfo:
    def __init__(self, name, condition1_values=None, condition2=None, condition2_value=0):
        self.name = name
        self.condition1_values = condition1_values or {}  # 捆序谷 -> 数量
        self.condition2 = condition2  # "躺吃", "无效推车", "有效推车"
        self.condition2_value = condition2_value  # 当 condition2 为 "有效推车" 时的数值
        
    def __repr__(self):
        return f"{self.name}: {self.condition1_values}, {self.condition2}({self.condition2_value})"

class BundleDistributionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.characters = []  # 保存所有角色信息
        self.condition1_types = []  # 保存所有捆序谷类型
        self.initUI()
        
    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 上捆条件1设置区域
        condition1_group = QGroupBox("条件1 捆序谷")
        condition1_layout = QVBoxLayout()
        
        # 捆序谷类型输入
        condition1_types_layout = QHBoxLayout()
        condition1_types_label = QLabel("请输入捆序谷类型（逗号分隔）：")
        self.condition1_types_input = QLineEdit()
        self.condition1_types_input.setPlaceholderText("例如：A,B,C")
        condition1_types_layout.addWidget(condition1_types_label)
        condition1_types_layout.addWidget(self.condition1_types_input)
        
        # 捆序谷优先级设置
        priority_layout = QHBoxLayout()
        priority_label = QLabel("请设置优先级（格式：A>B=C）：")
        self.priority_input = QLineEdit()
        self.priority_input.setPlaceholderText("例如：A>B=C")
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_input)
        
        condition1_layout.addLayout(condition1_types_layout)
        condition1_layout.addLayout(priority_layout)
        condition1_group.setLayout(condition1_layout)
        
        # 角色信息输入区域
        character_group = QGroupBox("角色设置")
        character_layout = QGridLayout()
        
        # 角色输入部分
        self.character_name_input = QLineEdit()
        self.character_name_input.setPlaceholderText("角色名称")
        character_layout.addWidget(QLabel("角色名称:"), 0, 0)
        character_layout.addWidget(self.character_name_input, 0, 1)
        
        # 条件1输入部分
        self.condition1_type_select = QComboBox()
        self.condition1_value_input = QSpinBox()
        self.condition1_value_input.setMinimum(0)
        self.condition1_value_input.setMaximum(100)
        character_layout.addWidget(QLabel("捆序谷类型:"), 1, 0)
        character_layout.addWidget(self.condition1_type_select, 1, 1)
        character_layout.addWidget(QLabel("数量:"), 1, 2)
        character_layout.addWidget(self.condition1_value_input, 1, 3)
        
        # 条件2输入部分
        self.condition2_select = QComboBox()
        self.condition2_select.addItems(["躺吃", "无效推车", "有效推车"])
        self.condition2_select.currentTextChanged.connect(self.toggle_condition2_value)
        
        self.condition2_value_input = QSpinBox()
        self.condition2_value_input.setMinimum(0)
        self.condition2_value_input.setMaximum(100)
        self.condition2_value_input.setEnabled(False)  # 仅当选择"有效推车"时启用
        
        character_layout.addWidget(QLabel("推车情况:"), 2, 0)
        character_layout.addWidget(self.condition2_select, 2, 1)
        character_layout.addWidget(QLabel("数值:"), 2, 2)
        character_layout.addWidget(self.condition2_value_input, 2, 3)
        
        # 添加/编辑按钮
        button_layout = QHBoxLayout()
        self.add_character_button = QPushButton("添加角色")
        self.add_character_button.clicked.connect(self.add_character)
        button_layout.addWidget(self.add_character_button)
        
        character_layout.addLayout(button_layout, 3, 0, 1, 4)
        character_group.setLayout(character_layout)
        
        # 角色列表显示
        characters_list_group = QGroupBox("已添加角色")
        characters_list_layout = QVBoxLayout()
        
        self.characters_display = QTextEdit()
        self.characters_display.setReadOnly(True)
        
        characters_list_layout.addWidget(self.characters_display)
        characters_list_group.setLayout(characters_list_layout)
        
        # 分配设置区域
        distribution_settings_group = QGroupBox("分配设置")
        distribution_settings_layout = QFormLayout()
        
        # 物品数量设置
        self.items_count = QSpinBox()
        self.items_count.setMinimum(1)
        self.items_count.setMaximum(1000)
        distribution_settings_layout.addRow("物品数量:", self.items_count)
        
        # 分配按钮
        self.distribute_button = QPushButton("开始分配")
        self.distribute_button.clicked.connect(self.distribute_items)
        distribution_settings_layout.addRow("", self.distribute_button)
        
        distribution_settings_group.setLayout(distribution_settings_layout)
        
        # 结果显示区域
        result_group = QGroupBox("分配结果")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["角色", "分配物品数量"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # 清空按钮
        clear_button = QPushButton("清空所有")
        clear_button.clicked.connect(self.clear_all)
        
        # 添加所有组件到主布局
        main_layout.addWidget(condition1_group)
        main_layout.addWidget(character_group)
        main_layout.addWidget(characters_list_group)
        main_layout.addWidget(distribution_settings_group)
        main_layout.addWidget(result_group)
        main_layout.addWidget(clear_button)
        
    def toggle_condition2_value(self, text):
        """当条件2选择变化时，启用或禁用数值输入"""
        self.condition2_value_input.setEnabled(text == "有效推车")
        
    def update_condition1_types(self):
        """更新条件1类型下拉菜单"""
        types_text = self.condition1_types_input.text().strip()
        if not types_text:
            return
            
        types = [t.strip() for t in types_text.split(",") if t.strip()]
        self.condition1_types = types
        
        # 更新下拉菜单
        current_text = self.condition1_type_select.currentText()
        self.condition1_type_select.clear()
        self.condition1_type_select.addItems(types)
        
        # 尝试恢复之前选择的值
        index = self.condition1_type_select.findText(current_text)
        if index >= 0:
            self.condition1_type_select.setCurrentIndex(index)
            
    def add_character(self):
        """添加角色到列表"""
        name = self.character_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入角色名称！")
            return
            
        # 检查条件1类型是否已设置
        if not self.condition1_types:
            self.update_condition1_types()
            if not self.condition1_types:
                QMessageBox.warning(self, "警告", "请先设置捆序谷类型！")
                return
                
        condition1_type = self.condition1_type_select.currentText()
        condition1_value = self.condition1_value_input.value()
        
        condition2 = self.condition2_select.currentText()
        condition2_value = self.condition2_value_input.value() if condition2 == "有效推车" else 0
        
        # 查找是否已存在该角色
        for char in self.characters:
            if char.name == name:
                # 更新现有角色的条件1值
                char.condition1_values[condition1_type] = condition1_value
                char.condition2 = condition2
                char.condition2_value = condition2_value
                break
        else:
            # 新建角色
            character = CharacterInfo(
                name, 
                {condition1_type: condition1_value}, 
                condition2, 
                condition2_value
            )
            self.characters.append(character)
            
        # 更新显示
        self.update_characters_display()
        
        # 清空输入
        self.character_name_input.clear()
        self.condition1_value_input.setValue(0)
        self.condition2_select.setCurrentIndex(0)
        self.condition2_value_input.setValue(0)
        
    def update_characters_display(self):
        """更新角色列表显示"""
        text = []
        for char in self.characters:
            condition1_text = ", ".join([f"{t}({v})" for t, v in char.condition1_values.items()])
            condition2_text = char.condition2
            if char.condition2 == "有效推车":
                condition2_text += f"({char.condition2_value})"
                
            text.append(f"{char.name}: {condition1_text}, {condition2_text}")
            
        self.characters_display.setText("\n".join(text))
        
    def parse_priority(self):
        """解析优先级设置"""
        priority_text = self.priority_input.text().strip()
        if not priority_text:
            # 如果未设置优先级，默认所有类型相等
            return {t: 1 for t in self.condition1_types}
            
        # 解析形如 A>B=C 的格式
        priorities = {}
        priority_level = len(self.condition1_types)
        
        for part in priority_text.split(">"):
            equals = part.split("=")
            for item in equals:
                item = item.strip()
                if item in self.condition1_types:
                    priorities[item] = priority_level
            priority_level -= 1
            
        # 检查是否所有类型都有优先级
        for t in self.condition1_types:
            if t not in priorities:
                priorities[t] = 1  # 默认最低优先级
                
        return priorities
        
    def get_total_condition1_count(self, char):
        """获取一个角色的所有条件1物品总数"""
        return sum(char.condition1_values.values())
        
    def distribute_items(self):
        """开始分配物品"""
        if not self.characters:
            QMessageBox.warning(self, "警告", "请先添加角色！")
            return
            
        items_count = self.items_count.value()
        if items_count <= 0:
            QMessageBox.warning(self, "警告", "物品数量必须大于0！")
            return
            
        # 解析优先级
        priorities = self.parse_priority()
        
        # 分类角色
        laying_chars = {}  # 躺吃: {条件1类型: [角色, ...], ...}
        invalid_push_chars = {}  # 无效推车: {条件1类型: [角色, ...], ...}
        valid_push_chars = []  # 有效推车: [(角色, 数值), ...]
        
        for char in self.characters:
            if char.condition2 == "躺吃":
                for cond1_type, value in char.condition1_values.items():
                    for _ in range(value):
                        if cond1_type not in laying_chars:
                            laying_chars[cond1_type] = []
                        laying_chars[cond1_type].append(char)
                        
            elif char.condition2 == "无效推车":
                for cond1_type, value in char.condition1_values.items():
                    for _ in range(value):
                        if cond1_type not in invalid_push_chars:
                            invalid_push_chars[cond1_type] = []
                        invalid_push_chars[cond1_type].append(char)
                        
            elif char.condition2 == "有效推车":
                total_count = self.get_total_condition1_count(char)
                valid_push_chars.append((char, char.condition2_value, total_count))
                
        # 按优先级排序条件1类型
        sorted_cond1_types = sorted(self.condition1_types, key=lambda x: -priorities.get(x, 0))
        
        # 开始分配
        distribution = {char.name: 0 for char in self.characters}
        remaining = items_count
        
        # 1. 先分配躺吃类
        for cond1_type in sorted_cond1_types:
            if cond1_type in laying_chars and laying_chars[cond1_type]:
                chars = laying_chars[cond1_type]
                if remaining >= len(chars):
                    # 如果物品足够，每人分配1个
                    for char in chars:
                        distribution[char.name] += 1
                        remaining -= 1
                else:
                    # 如果物品不足，随机选择
                    selected = random.sample(chars, remaining)
                    for char in selected:
                        distribution[char.name] += 1
                    remaining = 0
                    break
                    
        # 2. 然后分配无效推车类
        if remaining > 0:
            for cond1_type in sorted_cond1_types:
                if cond1_type in invalid_push_chars and invalid_push_chars[cond1_type]:
                    chars = invalid_push_chars[cond1_type]
                    if remaining >= len(chars):
                        # 如果物品足够，每人分配1个
                        for char in chars:
                            distribution[char.name] += 1
                            remaining -= 1
                    else:
                        # 如果物品不足，随机选择
                        selected = random.sample(chars, remaining)
                        for char in selected:
                            distribution[char.name] += 1
                        remaining = 0
                        break
                        
        # 3. 最后分配有效推车类
        if remaining > 0 and valid_push_chars:
            # 过滤掉无法分配的角色（有效推车值 >= 总物品数）
            eligible_chars = [(char, push_val, total) for char, push_val, total in valid_push_chars 
                             if push_val < total]
                             
            if eligible_chars:
                # 计算每个角色可分配的最大数量
                max_allocation = {char.name: total - push_val for char, push_val, total in eligible_chars}
                
                # 确定总共可分配的最大数量
                total_max = sum(max_allocation.values())
                
                if remaining <= total_max:
                    # 按角色的最大分配量等比例分配
                    while remaining > 0 and max_allocation:
                        # 计算每个角色的权重
                        weights = {name: max_val for name, max_val in max_allocation.items() if max_val > 0}
                        if not weights:
                            break
                            
                        # 随机选择一个角色
                        names = list(weights.keys())
                        weights_list = [weights[name] for name in names]
                        chosen_name = random.choices(names, weights=weights_list, k=1)[0]
                        
                        # 分配物品
                        distribution[chosen_name] += 1
                        max_allocation[chosen_name] -= 1
                        remaining -= 1
                else:
                    # 如果剩余物品比总最大值还多，那么先将每个角色分配到最大值
                    for name, max_val in max_allocation.items():
                        distribution[name] += max_val
                        remaining -= max_val
        
        # 显示分配结果
        self.display_results(distribution, remaining)
        
    def display_results(self, distribution, remaining):
        """显示分配结果"""
        # 设置表格大小
        self.result_table.setRowCount(len(distribution) + 1)  # +1 行用于显示剩余
        
        # 填充表格
        for row, (name, count) in enumerate(distribution.items()):
            self.result_table.setItem(row, 0, QTableWidgetItem(name))
            self.result_table.setItem(row, 1, QTableWidgetItem(str(count)))
            
        # 最后一行显示剩余物品
        self.result_table.setItem(len(distribution), 0, QTableWidgetItem("剩余"))
        self.result_table.setItem(len(distribution), 1, QTableWidgetItem(str(remaining)))
        
        # 如果有剩余物品，显示提示
        if remaining > 0:
            QMessageBox.information(self, "提示", f"分配完成，还有 {remaining} 个物品剩余。")
            
    def clear_all(self):
        """清空所有"""
        self.characters = []
        self.condition1_types = []
        self.condition1_types_input.clear()
        self.priority_input.clear()
        self.character_name_input.clear()
        self.condition1_type_select.clear()
        self.condition1_value_input.setValue(0)
        self.condition2_select.setCurrentIndex(0)
        self.condition2_value_input.setValue(0)
        self.characters_display.clear()
        self.items_count.setValue(1)
        self.result_table.setRowCount(0) 