import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QSpinBox, QGroupBox,
                           QFormLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QComboBox, QLineEdit,
                           QGridLayout, QFileDialog, QApplication, QDialog,
                           QDialogButtonBox)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QClipboard
import csv
import re

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
    
    def getTableData(self):
        """获取表格数据，返回行数据列表"""
        data = []
        for row in range(self.rowCount()):
            row_data = {}
            all_empty = True
            
            # 检查第一列（角色名）是否有值
            name_item = self.item(row, 0)
            if not name_item or not name_item.text().strip():
                continue
                
            row_data["name"] = name_item.text().strip()
            all_empty = False
            
            # 获取其他列的值
            for col in range(1, self.columnCount()):
                header = self.horizontalHeaderItem(col).text()
                item = self.item(row, col)
                if item and item.text().strip():
                    try:
                        # 对于推车情况列特殊处理
                        if header == "推车情况":
                            value = item.text().strip()
                            # 检查是否包含有效推车的数值
                            if value.startswith("有效推车") and "(" in value and ")" in value:
                                parts = value.split("(")
                                if len(parts) > 1:
                                    push_value_text = parts[1].split(")")[0]
                                    try:
                                        push_value = int(push_value_text)
                                        row_data["condition2"] = "有效推车"
                                        row_data["condition2_value"] = push_value
                                    except ValueError:
                                        row_data["condition2"] = value
                                        row_data["condition2_value"] = 0
                            else:
                                row_data["condition2"] = value
                                row_data["condition2_value"] = 0
                        else:
                            # 捆序谷列，尝试转换为数字
                            try:
                                value = int(item.text().strip())
                            except ValueError:
                                try:
                                    value = int(float(item.text().strip()))
                                except ValueError:
                                    value = 0
                            
                            if value > 0:  # 只存储正数值
                                row_data[header] = value
                                all_empty = False
                    except Exception as e:
                        print(f"处理单元格数据时出错: {e}")
            
            # 如果至少有一个非角色名列有值，则添加该行数据
            if not all_empty:
                data.append(row_data)
                
        return data
    
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

class CharacterInfo:
    def __init__(self, name, condition1_values=None, condition2=None, condition2_value=0):
        self.name = name
        self.condition1_values = condition1_values or {}  # 捆序谷 -> 数量
        self.condition2 = condition2  # "躺吃", "无效推车", "有效推车"
        self.condition2_value = condition2_value  # 当 condition2 为 "有效推车" 时的数值
        
    def __repr__(self):
        return f"{self.name}: {self.condition1_values}, {self.condition2}({self.condition2_value})"

class CharacterTableDialog(QDialog):
    """角色设置表格对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("角色设置")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建表格
        self.table = EditableTableWidget(20, 1)  # 初始只有角色名列
        self.table.setHorizontalHeaderLabels(["CN"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # 添加说明标签
        instruction_label = QLabel("请在下表中输入角色信息，也可以直接从Excel复制粘贴。")
        instruction_label.setStyleSheet("color: #666;")
        
        # 添加表格说明
        table_tips = QLabel("提示: CN=角色名称；捆序谷列填入数量；推车情况列使用下拉框选择")
        table_tips.setStyleSheet("color: #666;")
        
        # 添加工具按钮区域
        tools_layout = QHBoxLayout()
        
        # 添加清空表格按钮
        self.clear_table_button = QPushButton("清空表格")
        self.clear_table_button.clicked.connect(self.clear_table)
        tools_layout.addWidget(self.clear_table_button)
        
        # 添加删除选中行按钮
        self.delete_rows_button = QPushButton("删除选中行")
        self.delete_rows_button.clicked.connect(self.delete_selected_rows)
        tools_layout.addWidget(self.delete_rows_button)
        
        tools_layout.addStretch(1)
        
        # 添加确认取消按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 添加所有组件到布局
        layout.addWidget(instruction_label)
        layout.addWidget(self.table)
        layout.addWidget(table_tips)
        layout.addLayout(tools_layout)
        layout.addWidget(button_box)
        
    def clear_table(self):
        """清空表格内容"""
        if QMessageBox.question(self, "确认", "确定要清空所有数据吗？", 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.table.clearContents()
            # 重新设置推车情况列的下拉框
            self.setupPushConditionComboBoxes()
    
    def delete_selected_rows(self):
        """删除选中的行"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return
            
        if QMessageBox.question(self, "确认", f"确定要删除选中的 {len(selected_rows)} 行吗？", 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 从大到小排序行号，这样删除时不会影响其他行的索引
            for row in sorted(selected_rows, reverse=True):
                self.table.removeRow(row)
            
            # 确保表格至少有20行
            current_rows = self.table.rowCount()
            if current_rows < 20:
                self.table.setRowCount(20)
                # 为新增的行设置推车情况下拉框
                push_condition_col = self.table.columnCount() - 1
                for row in range(current_rows, 20):
                    if push_condition_col >= 0:
                        combo = QComboBox()
                        combo.addItems(["躺吃", "无效推车", "有效推车"])
                        combo.currentTextChanged.connect(lambda text, r=row: self.onPushConditionChanged(text, r))
                        self.table.setCellWidget(row, push_condition_col, combo)
        
    def setHeaders(self, headers):
        """设置表格表头"""
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # 设置列宽
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, len(headers) - 1):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(len(headers) - 1, QHeaderView.Stretch)
        
        # 只为最后一列（推车情况列）添加下拉框
        self.setupPushConditionComboBoxes()
        
    def setupPushConditionComboBoxes(self):
        """为推车情况列添加下拉框"""
        # 确保表格有足够的列
        if self.table.columnCount() < 2:
            return
            
        # 最后一列是推车情况列
        push_condition_col = self.table.columnCount() - 1
        
        # 确保不会为其他列设置下拉框
        for row in range(self.table.rowCount()):
            # 清除之前可能的下拉框
            for col in range(self.table.columnCount() - 1):
                if self.table.cellWidget(row, col) is not None:
                    self.table.removeCellWidget(row, col)
            
            # 为推车情况列设置下拉框
            combo = QComboBox()
            combo.addItems(["躺吃", "无效推车", "有效推车"])
            combo.currentTextChanged.connect(lambda text, r=row: self.onPushConditionChanged(text, r))
            self.table.setCellWidget(row, push_condition_col, combo)
            
    def onPushConditionChanged(self, text, row):
        """当推车情况选择改变时"""
        push_condition_col = self.table.columnCount() - 1
        
        if text == "有效推车":
            # 创建数值输入框和返回按钮的布局
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # 添加数值输入框
            value_input = QSpinBox()
            value_input.setMinimum(0)
            value_input.setMaximum(100)
            value_input.setValue(0)
            value_input.valueChanged.connect(lambda v, r=row: self.onPushValueChanged(v, r))
            layout.addWidget(value_input)
            
            # 添加返回按钮
            back_button = QPushButton("返回")
            back_button.setMaximumWidth(40)
            back_button.clicked.connect(lambda _, r=row: self.resetPushCondition(r))
            layout.addWidget(back_button)
            
            # 设置为表格单元格的小部件
            self.table.setCellWidget(row, push_condition_col, widget)
            
    def resetPushCondition(self, row):
        """重置推车情况为下拉菜单"""
        push_condition_col = self.table.columnCount() - 1
        
        # 重新设置下拉框
        combo = QComboBox()
        combo.addItems(["躺吃", "无效推车", "有效推车"])
        combo.currentTextChanged.connect(lambda text, r=row: self.onPushConditionChanged(text, r))
        self.table.setCellWidget(row, push_condition_col, combo)
            
    def onPushValueChanged(self, value, row):
        """当有效推车数值改变时，保存数值"""
        # 已经在数值输入框中直接保存值，无需额外操作
        pass
        
    def getTableData(self):
        """获取表格数据"""
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            all_empty = True
            
            # 检查第一列（角色名）是否有值
            name_item = self.table.item(row, 0)
            if not name_item or not name_item.text().strip():
                continue
                
            row_data["name"] = name_item.text().strip()
            all_empty = False
            
            # 获取其他列的值
            for col in range(1, self.table.columnCount()):
                header = self.table.horizontalHeaderItem(col).text()
                if header == "推车情况":
                    # 获取推车情况
                    widget = self.table.cellWidget(row, col)
                    if widget:
                        if isinstance(widget, QComboBox):
                            value = widget.currentText()
                            if value == "有效推车":
                                value = "有效推车(0)"
                            row_data["condition2"] = value
                            row_data["condition2_value"] = 0
                        elif isinstance(widget, QWidget) and widget.layout():
                            # 复合小部件，第一个子小部件是QSpinBox
                            for i in range(widget.layout().count()):
                                child_widget = widget.layout().itemAt(i).widget()
                                if isinstance(child_widget, QSpinBox):
                                    push_value = child_widget.value()
                                    row_data["condition2"] = "有效推车"
                                    row_data["condition2_value"] = push_value
                                    break
                else:
                    # 对于捆序谷列，读取单元格内容
                    item = self.table.item(row, col)
                    if item and item.text().strip():
                        try:
                            # 捆序谷列，尝试转换为数字
                            value = item.text().strip()
                            try:
                                value = int(value)
                            except ValueError:
                                try:
                                    value = int(float(value))
                                except ValueError:
                                    value = 0
                            
                            if value > 0:  # 只存储正数值
                                row_data[header] = value
                                all_empty = False
                        except Exception as e:
                            print(f"处理捆序谷数据时出错: {e}")
            
            # 如果至少有一个非角色名列有值，则添加该行数据
            if not all_empty or row_data.get("condition2") == "有效推车":
                data.append(row_data)
                
        return data
        
    def setTableData(self, data):
        """设置表格数据"""
        if not data:
            return
            
        # 确保表格有足够的行
        self.table.setRowCount(max(self.table.rowCount(), len(data)))
        
        # 填充数据
        for row, row_data in enumerate(data):
            # 先设置角色名称和捆序谷数量
            for col in range(self.table.columnCount() - 1):  # 排除最后一列（推车情况）
                header = self.table.horizontalHeaderItem(col).text()
                if header in row_data:
                    self.table.setItem(row, col, QTableWidgetItem(str(row_data[header])))
                    
            # 再设置推车情况
            push_condition_col = self.table.columnCount() - 1
            value = row_data.get("condition2", "躺吃")
            if value == "有效推车":
                # 创建数值输入框和返回按钮的布局
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                
                # 添加数值输入框
                value_input = QSpinBox()
                value_input.setMinimum(0)
                value_input.setMaximum(100)
                value_input.setValue(row_data.get("condition2_value", 0))
                value_input.valueChanged.connect(lambda v, r=row: self.onPushValueChanged(v, r))
                layout.addWidget(value_input)
                
                # 添加返回按钮
                back_button = QPushButton("返回")
                back_button.setMaximumWidth(40)
                back_button.clicked.connect(lambda _, r=row: self.resetPushCondition(r))
                layout.addWidget(back_button)
                
                # 设置为表格单元格的小部件
                self.table.setCellWidget(row, push_condition_col, widget)
            else:
                # 创建下拉框
                combo = QComboBox()
                combo.addItems(["躺吃", "无效推车", "有效推车"])
                combo.setCurrentText(value)
                combo.currentTextChanged.connect(lambda text, r=row: self.onPushConditionChanged(text, r))
                self.table.setCellWidget(row, push_condition_col, combo)

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
        self.condition1_types_input.textChanged.connect(self.update_condition1_types)
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
        character_layout = QVBoxLayout()
        
        # 使用说明
        instruction_label = QLabel("点击下方按钮打开角色设置表格，可以输入角色信息或从Excel复制粘贴。")
        instruction_label.setStyleSheet("color: #666;")
        
        # 打开表格按钮
        self.open_table_button = QPushButton("打开角色设置表格")
        self.open_table_button.clicked.connect(self.show_character_table)
        
        # 导出按钮
        export_import_layout = QHBoxLayout()
        self.export_button = QPushButton("导出表格")
        self.export_button.clicked.connect(self.export_character_table)
        export_import_layout.addWidget(self.export_button)
        export_import_layout.addStretch()
        
        # 加载数据按钮
        self.load_button = QPushButton("从表格获取角色")
        self.load_button.clicked.connect(self.load_characters_from_table)
        export_import_layout.addWidget(self.load_button)
        
        character_layout.addWidget(instruction_label)
        character_layout.addWidget(self.open_table_button)
        character_layout.addLayout(export_import_layout)
        character_group.setLayout(character_layout)
        
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
        
        # 显示角色信息
        self.characters_display = QTextEdit()
        self.characters_display.setReadOnly(True)
        self.characters_display.setMaximumHeight(150)
        
        # 结果表格
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["角色", "分配物品数量"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        result_layout.addWidget(QLabel("已加载的角色信息:"))
        result_layout.addWidget(self.characters_display)
        result_layout.addWidget(QLabel("分配结果:"))
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # 结果操作按钮 - 初始不添加，在有结果时才添加
        self.result_buttons_layout = QHBoxLayout()
        
        result_group.setLayout(result_layout)
        
        # 清空按钮
        clear_button = QPushButton("清空所有")
        clear_button.clicked.connect(self.clear_all)
        
        # 添加所有组件到主布局
        main_layout.addWidget(condition1_group)
        main_layout.addWidget(character_group)
        main_layout.addWidget(distribution_settings_group)
        main_layout.addWidget(result_group)
        main_layout.addWidget(clear_button)
        
        # 创建角色设置对话框
        self.character_dialog = CharacterTableDialog(self)
        
    def update_condition1_types(self):
        """更新捆序谷类型并重建表格列"""
        types_text = self.condition1_types_input.text().strip()
        if not types_text:
            return
            
        # 同时支持中文逗号和英文逗号
        types_text = types_text.replace("，", ",")
        types = [t.strip() for t in types_text.split(",") if t.strip()]
        if not types:
            return
            
        self.condition1_types = types
        
        # 更新对话框表格列
        columns = ["CN"] + types + ["推车情况"]
        self.character_dialog.setHeaders(columns)
        
    def show_character_table(self):
        """显示角色设置表格对话框"""
        if not self.condition1_types:
            QMessageBox.warning(self, "警告", "请先设置捆序谷类型！")
            return
            
        self.character_dialog.exec_()
        
    def export_character_table(self):
        """导出角色表格到CSV文件"""
        if not self.condition1_types:
            QMessageBox.warning(self, "警告", "请先设置捆序谷类型！")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出角色表格", "", "CSV文件 (*.csv)"
        )
        
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
                
            if self.character_dialog.table.exportToExcel(filename):
                QMessageBox.information(self, "成功", f"角色表格已成功导出到 {filename}")
            else:
                QMessageBox.warning(self, "失败", "导出数据时出错")
    
    def load_characters_from_table(self):
        """从表格加载角色数据"""
        if not self.condition1_types:
            QMessageBox.warning(self, "警告", "请先设置捆序谷类型！")
            return
        
        # 获取表格数据
        table_data = self.character_dialog.getTableData()
        
        if not table_data:
            QMessageBox.warning(self, "警告", "表格中没有有效的角色数据！请先填写数据。")
            return
            
        # 清空现有角色
        self.characters = []
        
        # 解析表格数据创建角色
        for row_data in table_data:
            name = row_data.get("name")
            
            if not name:
                continue
                
            # 收集捆序谷数据
            condition1_values = {}
            for cond_type in self.condition1_types:
                if cond_type in row_data and row_data[cond_type] > 0:
                    condition1_values[cond_type] = row_data[cond_type]
            
            # 获取推车情况
            condition2 = row_data.get("condition2", "躺吃")
            condition2_value = row_data.get("condition2_value", 0)
            
            # 创建角色并添加到列表
            character = CharacterInfo(name, condition1_values, condition2, condition2_value)
            self.characters.append(character)
        
        # 更新角色显示
        self.update_characters_display()
        
        QMessageBox.information(self, "成功", f"已成功加载 {len(self.characters)} 个角色信息。")
        
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
        
        # 替换中文符号为英文符号
        priority_text = priority_text.replace("＞", ">").replace("＝", "=").replace("＜", "<")
            
        # 初始化所有捆序谷类型的优先级
        priorities = {t: 0 for t in self.condition1_types}
        
        # 构建关系图
        relations = []  # 存储所有的关系，格式为 (A, B, ">") 表示 A > B
        
        # 检查是否有多个关系表达式（用分号或逗号分隔）
        priority_parts = re.split(r'[;,]', priority_text)
        
        for part in priority_parts:
            part = part.strip()
            if not part:
                continue
                
            # 提取所有的相等组
            equal_groups = []
            
            # 分解 > 和 < 关系
            if ">" in part:
                items = part.split(">")
                for i in range(len(items) - 1):
                    left_group = items[i].strip()
                    right_group = items[i + 1].strip()
                    
                    # 处理等号关系
                    left_items = [item.strip() for item in left_group.split("=") if item.strip()]
                    right_items = [item.strip() for item in right_group.split("=") if item.strip()]
                    
                    # 添加等号组
                    if len(left_items) > 1:
                        equal_groups.append(left_items)
                    if len(right_items) > 1:
                        equal_groups.append(right_items)
                    
                    # 添加大于关系
                    for left_item in left_items:
                        for right_item in right_items:
                            if left_item in self.condition1_types and right_item in self.condition1_types:
                                relations.append((left_item, right_item, ">"))
            
            elif "<" in part:
                items = part.split("<")
                for i in range(len(items) - 1):
                    left_group = items[i].strip()
                    right_group = items[i + 1].strip()
                    
                    # 处理等号关系
                    left_items = [item.strip() for item in left_group.split("=") if item.strip()]
                    right_items = [item.strip() for item in right_group.split("=") if item.strip()]
                    
                    # 添加等号组
                    if len(left_items) > 1:
                        equal_groups.append(left_items)
                    if len(right_items) > 1:
                        equal_groups.append(right_items)
                    
                    # 添加小于关系
                    for left_item in left_items:
                        for right_item in right_items:
                            if left_item in self.condition1_types and right_item in self.condition1_types:
                                relations.append((left_item, right_item, "<"))
            
            elif "=" in part:
                # 处理纯等号关系
                items = [item.strip() for item in part.split("=") if item.strip()]
                if len(items) > 1:
                    equal_groups.append(items)
        
        # 处理等号组中的相等关系
        equal_sets = []
        for group in equal_groups:
            valid_items = [item for item in group if item in self.condition1_types]
            if len(valid_items) > 1:
                equal_sets.append(set(valid_items))
        
        # 合并有交集的等号组
        i = 0
        while i < len(equal_sets):
            j = i + 1
            merged = False
            while j < len(equal_sets):
                if equal_sets[i] & equal_sets[j]:  # 如果两个集合有交集
                    equal_sets[i] |= equal_sets[j]  # 合并
                    equal_sets.pop(j)
                    merged = True
                else:
                    j += 1
            if not merged:
                i += 1
        
        # 构建优先级图
        graph = {t: set() for t in self.condition1_types}  # 表示"大于"关系的图
        for a, b, rel in relations:
            if rel == ">":
                graph[a].add(b)
            elif rel == "<":
                graph[b].add(a)
        
        # 拓扑排序计算优先级
        # 首先检测是否有循环依赖
        visited = {t: 0 for t in self.condition1_types}  # 0:未访问, 1:访问中, 2:已访问
        
        def has_cycle(node, path=None):
            if path is None:
                path = set()
            
            if node in path:
                return True
            
            if visited[node] == 2:
                return False
            
            visited[node] = 1
            path.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in self.condition1_types and has_cycle(neighbor, path):
                    return True
            
            path.remove(node)
            visited[node] = 2
            return False
        
        # 检查是否有循环
        has_circular_dependency = any(has_cycle(t) for t in self.condition1_types if visited[t] == 0)
        
        if has_circular_dependency:
            print("警告: 优先级设置中存在循环依赖，将使用默认优先级")
            QMessageBox.warning(self, "警告", "优先级设置中存在循环依赖，将使用默认优先级")
            return {t: 1 for t in self.condition1_types}
        
        # 重置访问状态
        visited = {t: 0 for t in self.condition1_types}
        
        # 拓扑排序函数
        def topo_sort(node, order=None):
            if order is None:
                order = []
            
            if visited[node] == 2:
                return
            
            visited[node] = 1
            
            for neighbor in graph.get(node, []):
                if neighbor in self.condition1_types and visited[neighbor] != 2:
                    topo_sort(neighbor, order)
            
            visited[node] = 2
            order.append(node)
            return order
        
        # 对每个节点进行拓扑排序
        all_nodes = []
        for t in self.condition1_types:
            if visited[t] == 0:
                topo_sort(t, all_nodes)
        
        # 翻转列表使得优先级从高到低排列
        all_nodes.reverse()
        
        # 赋予优先级值
        current_level = len(self.condition1_types)
        for node in all_nodes:
            priorities[node] = current_level
            current_level -= 1
        
        # 处理相等的节点组
        for equal_set in equal_sets:
            valid_items = [item for item in equal_set if item in self.condition1_types]
            if valid_items:
                # 找出组内最高优先级
                max_priority = max(priorities[item] for item in valid_items)
                # 将组内所有元素设置为相同优先级
                for item in valid_items:
                    priorities[item] = max_priority
        
        # 打印优先级设置用于调试
        print(f"捆序谷优先级: {priorities}")
        print(f"优先级排序: {sorted(self.condition1_types, key=lambda x: -priorities.get(x, 0))}")
                
        return priorities
    
    def get_total_condition1_count(self, char):
        """获取一个角色的所有条件1物品总数"""
        return sum(char.condition1_values.values())
    
    def distribute_items(self):
        """开始分配物品"""
        if not self.characters:
            QMessageBox.warning(self, "警告", "请先加载角色数据！")
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
        
        # 打印调试信息
        print("开始分配物品，总数量:", items_count)
        print("角色总数:", len(self.characters))
        
        for char in self.characters:
            if char.condition2 == "躺吃":
                for cond1_type, value in char.condition1_values.items():
                    for _ in range(int(value)):
                        if cond1_type not in laying_chars:
                            laying_chars[cond1_type] = []
                        laying_chars[cond1_type].append(char)
                        
            elif char.condition2 == "无效推车":
                for cond1_type, value in char.condition1_values.items():
                    for _ in range(int(value)):
                        if cond1_type not in invalid_push_chars:
                            invalid_push_chars[cond1_type] = []
                        invalid_push_chars[cond1_type].append(char)
                        
            elif char.condition2 == "有效推车":
                total_count = self.get_total_condition1_count(char)
                valid_push_chars.append((char, char.condition2_value, total_count))
        
        # 打印分类调试信息
        print("躺吃类角色分布:", {k: len(v) for k, v in laying_chars.items()})
        print("无效推车类角色分布:", {k: len(v) for k, v in invalid_push_chars.items()})
        print("有效推车类角色数:", len(valid_push_chars))
                
        # 按优先级排序条件1类型 - 优先级高的先分配
        # 首先，按照优先级分组，相同优先级的放在一起
        priority_groups = {}
        for cond_type in self.condition1_types:
            priority = priorities.get(cond_type, 0)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(cond_type)
        
        # 然后，对于每个优先级组，随机打乱顺序
        for priority, types in priority_groups.items():
            random.shuffle(types)
            print(f"优先级 {priority} 的捆序谷类型（已随机排序）: {types}")
            
        # 最后，按照优先级从高到低排列所有类型
        sorted_priorities = sorted(priority_groups.keys(), reverse=True)
        sorted_cond1_types = []
        for priority in sorted_priorities:
            sorted_cond1_types.extend(priority_groups[priority])
            
        print("按优先级排序的捆序谷类型（相同优先级随机排序）:", sorted_cond1_types)
        
        # 开始分配
        distribution = {char.name: 0 for char in self.characters}
        remaining = items_count
        
        # 1. 先分配躺吃类
        print("\n开始分配躺吃类...")
        for cond1_type in sorted_cond1_types:
            if cond1_type in laying_chars and laying_chars[cond1_type]:
                chars = laying_chars[cond1_type]
                print(f"  处理躺吃类捆序谷 {cond1_type}，有 {len(chars)} 个角色，优先级 {priorities.get(cond1_type)}")
                if remaining >= len(chars):
                    # 如果物品足够，每人分配1个
                    for char in chars:
                        distribution[char.name] += 1
                        remaining -= 1
                    print(f"  物品足够，每人分配1个，剩余 {remaining} 个")
                else:
                    # 如果物品不足，随机选择
                    selected = random.sample(chars, remaining)
                    for char in selected:
                        distribution[char.name] += 1
                    print(f"  物品不足，随机选择 {remaining} 个角色")
                    remaining = 0
                    break
                    
        # 2. 然后分配无效推车类
        if remaining > 0:
            print("\n开始分配无效推车类...")
            
            # 重新计算相同优先级分组，以确保每次分配时都重新随机化
            priority_groups = {}
            for cond_type in self.condition1_types:
                if cond_type in invalid_push_chars and invalid_push_chars[cond_type]:
                    priority = priorities.get(cond_type, 0)
                    if priority not in priority_groups:
                        priority_groups[priority] = []
                    priority_groups[priority].append(cond_type)
            
            # 随机打乱相同优先级的组
            for priority, types in priority_groups.items():
                random.shuffle(types)
                print(f"无效推车优先级 {priority} 的捆序谷类型（已随机排序）: {types}")
                
            # 按照优先级从高到低排列所有类型
            sorted_priorities = sorted(priority_groups.keys(), reverse=True)
            sorted_invalid_push_types = []
            for priority in sorted_priorities:
                sorted_invalid_push_types.extend(priority_groups[priority])
                
            print("无效推车按优先级排序的捆序谷类型（相同优先级随机排序）:", sorted_invalid_push_types)
            
            # 按新的排序分配无效推车
            for cond1_type in sorted_invalid_push_types:
                chars = invalid_push_chars[cond1_type]
                print(f"  处理无效推车类捆序谷 {cond1_type}，有 {len(chars)} 个角色，优先级 {priorities.get(cond1_type)}")
                if remaining >= len(chars):
                    # 如果物品足够，每人分配1个
                    for char in chars:
                        distribution[char.name] += 1
                        remaining -= 1
                    print(f"  物品足够，每人分配1个，剩余 {remaining} 个")
                else:
                    # 如果物品不足，随机选择
                    selected = random.sample(chars, remaining)
                    for char in selected:
                        distribution[char.name] += 1
                    print(f"  物品不足，随机选择 {remaining} 个角色")
                    remaining = 0
                    break
                        
        # 3. 最后分配有效推车类
        if remaining > 0 and valid_push_chars:
            print("\n开始分配有效推车类...")
            # 过滤掉无法分配的角色（有效推车值 >= 总物品数）
            eligible_chars = [(char, push_val, total) for char, push_val, total in valid_push_chars 
                             if push_val < total]
            print(f"有效推车类中符合条件的角色数: {len(eligible_chars)}")
                             
            if eligible_chars:
                # 计算每个角色可分配的最大数量
                max_allocation = {char.name: total - push_val for char, push_val, total in eligible_chars}
                print(f"每个角色可分配的最大数量: {max_allocation}")
                
                # 确定总共可分配的最大数量
                total_max = sum(max_allocation.values())
                print(f"总共可分配的最大数量: {total_max}")
                
                if remaining <= total_max:
                    # 按角色的最大分配量等比例分配
                    print(f"剩余物品数 {remaining} <= 总最大值 {total_max}，按权重分配")
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
                    print(f"剩余物品数 {remaining} > 总最大值 {total_max}，先将每个角色分配到最大值")
                    for name, max_val in max_allocation.items():
                        distribution[name] += max_val
                        remaining -= max_val
        
        # 打印最终分配结果
        print("\n分配结果:")
        for name, count in distribution.items():
            if count > 0:
                print(f"{name}: {count}个")
        print(f"剩余物品: {remaining}个")
        
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
        
        # 添加复制和导出按钮
        result_buttons_layout = QHBoxLayout()
        
        copy_button = QPushButton("复制结果")
        copy_button.clicked.connect(self.copy_results_to_clipboard)
        result_buttons_layout.addWidget(copy_button)
        
        export_results_button = QPushButton("导出结果")
        export_results_button.clicked.connect(self.export_results_to_csv)
        result_buttons_layout.addWidget(export_results_button)
        
        # 查找结果组框架，添加按钮
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), QGroupBox) and item.widget().title() == "分配结果":
                result_group = item.widget()
                result_layout = result_group.layout()
                result_layout.addLayout(result_buttons_layout)
                break
        
        # 如果有剩余物品，显示提示
        if remaining > 0:
            QMessageBox.information(self, "提示", f"分配完成，还有 {remaining} 个物品剩余。")
            
    def copy_results_to_clipboard(self):
        """将分配结果复制到剪贴板"""
        if self.result_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有可复制的分配结果！")
            return
            
        # 构建结果文本
        result_text = "角色\t分配物品数量\n"
        for row in range(self.result_table.rowCount()):
            name_item = self.result_table.item(row, 0)
            count_item = self.result_table.item(row, 1)
            
            if name_item and count_item:
                result_text += f"{name_item.text()}\t{count_item.text()}\n"
                
        # 复制到剪贴板
        QApplication.clipboard().setText(result_text)
        QMessageBox.information(self, "成功", "分配结果已复制到剪贴板")
        
    def export_results_to_csv(self):
        """将分配结果导出到CSV文件"""
        if self.result_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的分配结果！")
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
                    writer.writerow(["角色", "分配物品数量"])
                    
                    for row in range(self.result_table.rowCount()):
                        name_item = self.result_table.item(row, 0)
                        count_item = self.result_table.item(row, 1)
                        
                        if name_item and count_item:
                            writer.writerow([name_item.text(), count_item.text()])
                
                QMessageBox.information(self, "成功", f"分配结果已成功导出到 {filename}")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"导出数据时出错: {e}")
                
    def clear_all(self):
        """清空所有"""
        self.characters = []
        self.condition1_types = []
        self.condition1_types_input.clear()
        self.priority_input.clear()
        self.character_dialog.table.clearContents()
        self.characters_display.clear()
        self.items_count.setValue(1)
        self.result_table.setRowCount(0) 