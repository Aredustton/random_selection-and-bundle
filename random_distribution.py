import random
import re
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QSpinBox, QGroupBox,
                           QFormLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QCheckBox, QApplication,
                           QDialog, QDialogButtonBox, QDoubleSpinBox, QFileDialog)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QClipboard
import csv

class EditableTableWidget(QTableWidget):
    """自定义可编辑表格，支持从Excel直接复制粘贴数据"""
    def __init__(self, rows=10, columns=2, headers=None):
        super().__init__(rows, columns)
        
        if headers is None:
            headers = ["名称", "数量"]
        
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, columns):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # 启用复制粘贴
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
    def keyPressEvent(self, event):
        """处理键盘事件，支持复制粘贴操作"""
        if event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
            self.pasteFromClipboard()
        elif event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            self.copyToClipboard()
        else:
            super().keyPressEvent(event)
    
    def copyToClipboard(self):
        """将选中的表格数据复制到剪贴板"""
        selected = self.selectedRanges()
        if not selected:
            return
            
        text = ""
        for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
            row_text = []
            for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                item = self.item(r, c)
                if item and item.text():
                    row_text.append(item.text())
                else:
                    row_text.append("")
            text += "\t".join(row_text) + "\n"
            
        QApplication.clipboard().setText(text)
            
    def pasteFromClipboard(self):
        """从剪贴板粘贴数据到表格"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasText():
            # 获取剪贴板文本
            text = mime_data.text()
            
            # 解析文本（按行分割）
            rows = text.split('\n')
            if not rows:
                return
                
            # 获取当前选中的单元格
            current_row = self.currentRow()
            current_column = self.currentColumn()
            
            # 如果没有选中单元格，则从第一行开始
            if current_row < 0:
                current_row = 0
            if current_column < 0:
                current_column = 0
                
            # 确保表格有足够的行
            if current_row + len(rows) > self.rowCount():
                self.setRowCount(current_row + len(rows))
                
            # 填充数据到表格
            for i, row_text in enumerate(rows):
                if not row_text.strip():
                    continue
                    
                # 按制表符或多个空格分割列
                columns = re.split(r'\t+|\s{2,}', row_text.strip())
                
                for j, cell_text in enumerate(columns):
                    # 跳过超出表格列数的数据
                    if current_column + j >= self.columnCount():
                        break
                        
                    # 创建单元格项并设置文本
                    item = QTableWidgetItem(cell_text.strip())
                    self.setItem(current_row + i, current_column + j, item)
    
    def getTableData(self, numeric_columns=None):
        """获取表格数据，返回名称->数量的字典"""
        if numeric_columns is None:
            numeric_columns = [1]  # 默认第二列为数值
            
        data = {}
        for row in range(self.rowCount()):
            name_item = self.item(row, 0)
            
            if name_item and name_item.text().strip():
                name = name_item.text().strip()
                
                # 获取数量列的值
                values = []
                for col in numeric_columns:
                    if col < self.columnCount():
                        value_item = self.item(row, col)
                        if value_item and value_item.text().strip():
                            try:
                                value = float(value_item.text().strip())
                                if value <= 0:
                                    value = 1 if col == 1 else 0
                            except ValueError:
                                value = 1 if col == 1 else 0
                        else:
                            value = 1 if col == 1 else 0
                        values.append(value)
                    else:
                        values.append(1 if col == 1 else 0)
                
                # 如果只有一个数值列，直接存储值
                if len(numeric_columns) == 1:
                    data[name] = values[0]
                else:
                    # 否则存储元组/列表
                    data[name] = values
                
        return data
    
    def loadData(self, data_dict, columns=None):
        """从字典加载数据到表格"""
        if columns is None:
            columns = [1]  # 默认加载到第二列
            
        self.clearContents()
        self.setRowCount(max(10, len(data_dict)))
        
        for row, (name, values) in enumerate(data_dict.items()):
            # 设置名称
            self.setItem(row, 0, QTableWidgetItem(name))
            
            # 判断值是否为列表/元组
            if isinstance(values, (list, tuple)):
                for i, value in enumerate(values):
                    if i < len(columns) and columns[i] < self.columnCount():
                        self.setItem(row, columns[i], QTableWidgetItem(str(value)))
            else:
                # 单个值
                if columns[0] < self.columnCount():
                    self.setItem(row, columns[0], QTableWidgetItem(str(values)))
    
    def exportToExcel(self, filename):
        """导出表格数据到CSV文件"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                
                # 写入表头
                headers = []
                for col in range(self.columnCount()):
                    headers.append(self.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # 写入数据
                for row in range(self.rowCount()):
                    row_data = []
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item and item.text():
                            row_data.append(item.text())
                        else:
                            row_data.append("")
                    writer.writerow(row_data)
            
            return True
        except Exception as e:
            print(f"导出数据时出错: {e}")
            return False

class FullGiftCalculatorDialog(QDialog):
    """满赠计算对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("满赠计算")
        self.setMinimumSize(600, 400)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 消费输入表格
        consumption_group = QGroupBox("消费金额输入")
        consumption_layout = QVBoxLayout()
        
        consumption_label = QLabel("请输入角色和消费金额（支持从Excel直接复制）：")
        self.consumption_table = EditableTableWidget(10, 2, ["角色名称", "消费金额"])
        
        consumption_layout.addWidget(consumption_label)
        consumption_layout.addWidget(self.consumption_table)
        consumption_group.setLayout(consumption_layout)
        
        # 满赠规则设置
        rule_group = QGroupBox("满赠规则")
        rule_layout = QFormLayout()
        
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.01, 100000.00)
        self.threshold_spinbox.setValue(100.00)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setSingleStep(10.00)
        # 简化输入框，仅显示数字
        self.threshold_spinbox.setPrefix("")
        self.threshold_spinbox.setSuffix("")
        
        threshold_label = QLabel("满<b>每</b>多少元赠送1份:")
        rule_layout.addRow(threshold_label, self.threshold_spinbox)
        rule_group.setLayout(rule_layout)
        
        # 计算结果表格
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout()
        
        result_label = QLabel("角色可获得的赠送数量（使用去尾法计算）:")
        self.result_table = EditableTableWidget(10, 2, ["角色名称", "赠送数量"])
        
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("计算")
        self.calculate_button.clicked.connect(self.calculate_gifts)
        self.import_button = QPushButton("导入到随机分配")
        self.import_button.clicked.connect(self.accept)
        self.export_button = QPushButton("导出结果")
        self.export_button.clicked.connect(self.export_results)
        
        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)
        
        # 对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        
        # 添加所有组件到主布局
        layout.addWidget(consumption_group)
        layout.addWidget(rule_group)
        layout.addWidget(result_group)
        layout.addLayout(button_layout)
        layout.addWidget(button_box)
        
    def calculate_gifts(self):
        """计算每个角色可获得的赠送数量"""
        consumption_data = self.consumption_table.getTableData()
        threshold = self.threshold_spinbox.value()
        
        if not consumption_data:
            QMessageBox.warning(self, "警告", "请先输入角色消费数据！")
            return
            
        if threshold <= 0:
            QMessageBox.warning(self, "警告", "满赠阈值必须大于0！")
            return
            
        # 计算赠送数量（使用去尾法）
        gift_data = {}
        for name, amount in consumption_data.items():
            # 使用去尾法计算赠送数量
            gift_count = int(amount / threshold)  # 去尾取整
            # 只保存赠送数量大于0的记录
            if gift_count > 0:
                gift_data[name] = gift_count
            
        # 显示结果
        self.result_table.loadData(gift_data)
        
        # 如果没有赠送结果，显示提示
        if not gift_data:
            QMessageBox.information(self, "提示", "根据当前消费金额和满赠规则，没有角色达到满赠条件。")
    
    def export_results(self):
        """导出计算结果到Excel"""
        if self.result_table.rowCount() <= 0 or not self.result_table.item(0, 0):
            QMessageBox.warning(self, "警告", "没有可导出的数据！请先计算满赠结果。")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出满赠计算结果", "", "CSV文件 (*.csv)"
        )
        
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
                
            if self.result_table.exportToExcel(filename):
                QMessageBox.information(self, "成功", f"数据已成功导出到 {filename}")
            else:
                QMessageBox.warning(self, "失败", "导出数据时出错")
        
    def getCalculatedData(self):
        """获取计算结果数据"""
        return self.result_table.getTableData()

class RandomDistributionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 前置功能按钮
        preprocess_layout = QHBoxLayout()
        self.fullgift_button = QPushButton("满赠计算")
        self.fullgift_button.clicked.connect(self.show_fullgift_calculator)
        preprocess_layout.addWidget(self.fullgift_button)
        preprocess_layout.addStretch()
        
        # 角色和物品输入区域
        input_layout = QHBoxLayout()
        
        # 角色输入组
        roles_group = QGroupBox("角色列表")
        roles_layout = QVBoxLayout()
        
        roles_label = QLabel("请输入角色列表（支持直接从Excel复制）：")
        self.roles_table = EditableTableWidget(10, 2)
        
        # 使用说明
        roles_help = QLabel("提示：第一列为角色名称，第二列为需要分配的物品数量")
        roles_help.setStyleSheet("color: gray;")
        
        roles_layout.addWidget(roles_label)
        roles_layout.addWidget(self.roles_table)
        roles_layout.addWidget(roles_help)
        roles_group.setLayout(roles_layout)
        
        # 物品输入组
        items_group = QGroupBox("物品列表")
        items_layout = QVBoxLayout()
        
        items_label = QLabel("请输入物品列表（支持直接从Excel复制）：")
        self.items_table = EditableTableWidget(10, 2)
        
        # 使用说明
        items_help = QLabel("提示：第一列为物品名称，第二列为物品数量")
        items_help.setStyleSheet("color: gray;")
        
        items_layout.addWidget(items_label)
        items_layout.addWidget(self.items_table)
        items_layout.addWidget(items_help)
        items_group.setLayout(items_layout)
        
        input_layout.addWidget(roles_group)
        input_layout.addWidget(items_group)
        
        # 分配设置区域
        settings_group = QGroupBox("分配设置")
        settings_layout = QVBoxLayout()
        
        # 启用个性化分配设置
        self.use_custom_allocation = QCheckBox("使用角色输入表中指定的物品数量")
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
        
        # 添加一个显示统计信息的标签
        self.stats_label = QLabel()
        result_layout.addWidget(self.stats_label)
        
        self.result_table = QTableWidget(0, 0)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.distribute_button = QPushButton("开始分配")
        self.distribute_button.clicked.connect(self.distribute_items)
        self.export_button = QPushButton("导出结果")
        self.export_button.clicked.connect(self.export_results)
        self.clear_button = QPushButton("清空")
        self.clear_button.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.distribute_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.clear_button)
        
        # 添加所有组件到主布局
        main_layout.addLayout(preprocess_layout)
        main_layout.addLayout(input_layout, 3)
        main_layout.addWidget(settings_group, 1)
        main_layout.addWidget(result_group, 4)
        main_layout.addLayout(button_layout)
        
    def show_fullgift_calculator(self):
        """显示满赠计算器对话框"""
        dialog = FullGiftCalculatorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 用户点击了"导入到随机分配"
            calculated_data = dialog.getCalculatedData()
            if calculated_data:
                # 导入数据到角色列表
                self.roles_table.loadData(calculated_data)
                QMessageBox.information(self, "成功", f"满赠计算结果已导入到角色列表！共导入{len(calculated_data)}个角色。")
            else:
                QMessageBox.warning(self, "提示", "没有满足满赠条件的角色，未导入任何数据。")
    
    def export_results(self):
        """导出分配结果到Excel"""
        if self.result_table.rowCount() <= 0 or not self.result_table.item(0, 0):
            QMessageBox.warning(self, "警告", "没有可导出的数据！请先进行随机分配。")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出分配结果", "", "CSV文件 (*.csv)"
        )
        
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
                
            try:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    
                    # 写入表头
                    headers = []
                    for col in range(self.result_table.columnCount()):
                        item = self.result_table.horizontalHeaderItem(col)
                        if item:
                            headers.append(item.text())
                        else:
                            headers.append(f"列{col+1}")
                    writer.writerow(headers)
                    
                    # 写入数据
                    for row in range(self.result_table.rowCount()):
                        row_data = []
                        for col in range(self.result_table.columnCount()):
                            item = self.result_table.item(row, col)
                            if item and item.text():
                                row_data.append(item.text())
                            else:
                                row_data.append("")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "成功", f"分配结果已成功导出到 {filename}")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"导出数据时出错: {e}")
        
    def toggle_allocation_mode(self, state):
        """切换分配模式"""
        self.items_per_person.setEnabled(not state)
        
    def distribute_items(self):
        """随机分配物品给角色"""
        try:
            # 从表格获取角色和物品数据
            roles_data = self.roles_table.getTableData()
            items_dict = self.items_table.getTableData()
            
            if not roles_data:
                QMessageBox.warning(self, "警告", "请先输入角色列表！")
                return
                
            if not items_dict:
                QMessageBox.warning(self, "警告", "请先输入物品列表！")
                return
                
            # 输出调试信息到控制台
            print("解析到的角色数据:", roles_data)
            print("解析到的物品数据:", items_dict)
            
            use_custom = self.use_custom_allocation.isChecked()
            
            # 计算所需物品总数
            if use_custom:
                # 使用自定义分配
                try:
                    total_items_needed = sum(int(count) for count in roles_data.values())
                except (ValueError, TypeError):
                    # 如果转换失败，尝试使用浮点数然后转为整数
                    total_items_needed = sum(int(float(count)) for count in roles_data.values())
            else:
                # 使用统一分配
                items_per_person = self.items_per_person.value()
                for role in roles_data:
                    roles_data[role] = items_per_person
                total_items_needed = len(roles_data) * items_per_person
            
            # 创建物品池
            items_pool = []
            total_available_items = 0
            
            for item_name, count in items_dict.items():
                try:
                    # 尝试转换为整数
                    item_count = int(count)
                except (ValueError, TypeError):
                    # 如果失败，尝试先转为浮点数再转为整数
                    try:
                        item_count = int(float(count))
                    except (ValueError, TypeError):
                        # 如果还是失败，使用默认值1
                        print(f"警告: 物品 '{item_name}' 的数量 '{count}' 无法转换为数字，使用默认值1")
                        item_count = 1
                
                # 确保数量为正整数
                item_count = max(1, item_count)
                
                items_pool.extend([item_name] * item_count)
                total_available_items += item_count
                
            # 更新统计信息
            stats_text = (f"角色数量: {len(roles_data)}, 需要物品总数: {total_items_needed}, "
                         f"可用物品总数: {total_available_items}, 剩余物品: {total_available_items - total_items_needed}")
            self.stats_label.setText(stats_text)
            
            if total_available_items < total_items_needed:
                QMessageBox.warning(self, "警告", 
                                   f"物品总数({total_available_items})不足以分配给所有角色(需要{total_items_needed})！\n"
                                   f"角色数量: {len(roles_data)}, 各角色需要物品数量总和: {total_items_needed}")
                return
                
            # 随机打乱物品
            random.shuffle(items_pool)
            
            # 分配物品
            distribution = {role: [] for role in roles_data.keys()}
            current_idx = 0
            
            for role, count in roles_data.items():
                try:
                    # 尝试转换为整数
                    role_count = int(count)
                except (ValueError, TypeError):
                    # 如果失败，尝试先转为浮点数再转为整数
                    try:
                        role_count = int(float(count))
                    except (ValueError, TypeError):
                        # 如果还是失败，使用默认值1
                        print(f"警告: 角色 '{role}' 的数量 '{count}' 无法转换为数字，使用默认值1")
                        role_count = 1
                        
                # 确保数量为正整数
                role_count = max(1, role_count)
                
                # 计算结束索引
                end_idx = current_idx + role_count
                
                # 确保不会超出物品池的范围
                if end_idx > len(items_pool):
                    end_idx = len(items_pool)
                    print(f"警告: 物品池不足，角色 '{role}' 请求 {role_count} 个物品，但只分配了 {end_idx - current_idx} 个")
                
                # 分配物品
                distribution[role] = items_pool[current_idx:end_idx]
                current_idx = end_idx
                
                # 如果已经用完了所有物品，就退出循环
                if current_idx >= len(items_pool):
                    break
                
            # 统计剩余物品
            remaining_items = items_pool[current_idx:]
            remaining_count = {}
            for item in remaining_items:
                remaining_count[item] = remaining_count.get(item, 0) + 1
                
            # 显示分配结果
            self.display_results(distribution, remaining_count)
            
        except Exception as e:
            # 捕获所有异常，防止程序崩溃
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "错误", 
                               f"随机分配过程中发生错误:\n{str(e)}\n\n详细信息:\n{error_details}")
            print(f"错误: {str(e)}")
            print(f"详细信息:\n{error_details}")
        
    def display_results(self, distribution, remaining):
        """在表格中显示分配结果"""
        if not distribution:
            return
            
        # 获取所有分配的物品种类和剩余物品种类
        all_items = set()
        for items in distribution.values():
            all_items.update(items)
        all_items.update(remaining.keys())
            
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
        self.roles_table.clearContents()
        self.items_table.clearContents()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(0)
        self.stats_label.clear()
        self.items_per_person.setValue(1) 