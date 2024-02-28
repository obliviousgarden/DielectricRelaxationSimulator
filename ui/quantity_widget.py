from decimal import Decimal
from PyQt5.QtCore import Qt, QModelIndex, QRect, QPoint
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTreeView, QLCDNumber, QSlider, QComboBox, QCheckBox, \
    QTreeWidgetItem, QToolTip
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QPixmap, QCursor
from PyQt5.uic.properties import QtGui

from physical_model.quantity import Equation, Quantity,equation_type_dict
from ui.img.img_info import ImgInfo, img_path_dict
import numpy as np
from typing import List
from utils.tree_node import TreeNode,model_to_tree
# equation_dict = {}  # 一个物理量name对应一个equation
quantity_dict = {}  # 一个物理量name对应一个quantity
widget_dict = {}  # 一个物理量name对应好几个widget
actual_equation_dict = {}  # 这个是实际用来计算的字典
actual_quantity_dict = {}  # 这个是实际用来计算的字典

class MySlider(QSlider):
    def wheelEvent(self, event):
        # 禁用滚轮事件
        event.ignore()

    def keyPressEvent(self, event):
        # 禁用键盘事件
        event.ignore()

class QuantityWidget(QWidget):
    def __init__(self, index: QModelIndex, quantity: Quantity):
        super(QuantityWidget, self).__init__()
        if quantity.name not in quantity_dict:
            quantity_dict[quantity.name] = quantity
        else:
            if not quantity_dict[quantity.name].child_quantity:
                quantity_dict[quantity.name] = quantity
        if quantity.name not in widget_dict:
            widget_dict[quantity.name] = [self]
        else:
            widget_dict[quantity.name].append(self)
        self.description = quantity_dict[quantity.name].description
        self.name = quantity_dict[quantity.name].name
        self.symbol = quantity_dict[quantity.name].symbol
        self.value = quantity_dict[quantity.name].value
        # if self.name == 'f':
        #     print(self.name,self.value)
        self.is_log = quantity_dict[quantity.name].is_log
        self.unit = quantity_dict[quantity.name].unit
        self.min = quantity_dict[quantity.name].min
        self.max = quantity_dict[quantity.name].max
        self.convert_factor = quantity_dict[quantity.name].convert_factor
        self.child_quantity = quantity_dict[quantity.name].child_quantity
        self.scale = (np.log10(self.value) - np.log10(self.min)) / (np.log10(self.max / self.min)) * Decimal("100.0") \
            if self.is_log else (self.value - self.min) / (self.max - self.min) * Decimal("100.0")
        self.fix_flag = quantity.fix_flag

        self.row_index = index.row()
        self.col_index = index.column()
        self.layout = QHBoxLayout()
        self.layout.setObjectName(f"horizontalLayout_{self.row_index}_{self.col_index}")

        label_str = self.symbol
        if self.unit != "1":
            label_str += f"[{self.unit}]"
        self.label = QLabel(label_str)
        self.label.setObjectName(f"label_{self.row_index}_{self.col_index}")
        self.label.setToolTip(f"<html><body>"
                              f"<p><b>{self.description.upper()}</b></p>"
                              f"<p>-----------------------------------------------</p>"
                              f"<p><i><u>Description</u></i>&nbsp;:&nbsp;{self.description}</p>"
                              f"<p><i><u>Name</u></i>&nbsp;:&nbsp;{self.name}</p>"
                              f"<p><i><u>Symbol</u></i>&nbsp;:&nbsp;{self.symbol}</p>"
                              f"<p><i><u>Min.</u></i>&nbsp;:&nbsp;{self.min}</p>"
                              f"<p><i><u>Max.</u></i>&nbsp;:&nbsp;{self.max}</p>"
                              f"<p><i><u>Unit</u></i>&nbsp;:&nbsp;{self.unit}</p>"
                              f"<p><i><u>Convert factor</u></i>&nbsp;:&nbsp;{self.convert_factor}</p>"
                              f"<p><i><u>Is LOG?</u></i>&nbsp;:&nbsp;{self.is_log}</p>"
                              f"<p><i><u>Child parameters</u></i>&nbsp;:&nbsp;{self.child_quantity}</p>"
                              f"</body></html>")
        self.layout.addWidget(self.label)

        self.lcd_number = QLCDNumber()
        self.lcd_number.setDigitCount(8)
        self.lcd_number.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        # print(self.value)
        if self.is_log:
            # print('%.2e' % self.value)
            self.lcd_number.display('%.2e' % self.value)
        else:
            self.lcd_number.display(str(self.value))
        self.lcd_number.setObjectName(f"lcdNumber_{self.row_index}_{self.col_index}")
        self.layout.addWidget(self.lcd_number)

        self.horizontalSlider = MySlider()
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setCursor(QCursor(Qt.ArrowCursor))
        self.horizontalSlider.setInvertedControls(False)
        self.horizontalSlider.setTickPosition(QSlider.TicksAbove)
        if self.is_log:
            self.horizontalSlider.setMinimum(1)
        else:
            self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setPageStep(5)
        self.horizontalSlider.setValue(int(self.scale))
        self.horizontalSlider.valueChanged.connect(self.on_horizontalSlider_valueChanged)
        self.horizontalSlider.sliderReleased.connect(self.on_horizontalSlider_sliderReleased)
        self.horizontalSlider.setObjectName(f"horizontalSlider_{self.row_index}_{self.col_index}")
        self.layout.addWidget(self.horizontalSlider)

        self.checkBox = QCheckBox("fix")
        if self.fix_flag:
            self.checkBox.setCheckState(Qt.Checked)
        else:
            self.checkBox.setCheckState(Qt.Unchecked)
        self.checkBox.clicked.connect(self.on_checkBox_clicked)
        self.checkBox.setObjectName(f"checkBox_{self.row_index}_{self.col_index}")
        self.layout.addWidget(self.checkBox)
        self.layout.setStretch(2, 1)

        self.has_equation = self.name in img_path_dict
        if self.has_equation:
            self.label_img = QLabel()
            self.label_img.setObjectName(f"label_img_{self.row_index}_{self.col_index}")
            img_path = img_path_dict[self.name].get_img_path()
            self.label_img.setStyleSheet(img_path)
            src_path = img_path_dict[self.name].get_src_path()
            self.label_img.setToolTip("<html><body><img src={}></body></html>".format(src_path))
            self.layout.addWidget(self.label_img)
            self.layout.setStretch(4, 1)

        self.setLayout(self.layout)

    def on_horizontalSlider_valueChanged(self):
        self.scale = Decimal(self.horizontalSlider.value())
        if self.is_log:
            self.value = np.power(10, np.log10(self.min) + (
                    np.log10(self.max) - np.log10(self.min)) * self.scale / Decimal("100.0"))
        else:
            self.value = self.min + (self.max - self.min) * self.scale / Decimal("100.0")
        quantity_dict[self.name].update_value(self.value)
        display_str = '%.2e' % self.value if self.is_log else str(self.value)
        self.lcd_number.display(display_str)
        # print("Min",self.min,"Max",self.max,"Value",self.value,"Scale",self.scale,"Display",display_str)

    def on_horizontalSlider_sliderReleased(self):
        display_str = '%.2e' % self.value if self.is_log else str(self.value)
        same_widget_list = widget_dict[self.name]
        for same_widget in same_widget_list:
            if self != same_widget:
                same_widget.value = self.value
                same_widget.scale = self.scale
                same_widget.lcd_number.display(display_str)
                # print(self.scale,same_widget.scale)
                same_widget.horizontalSlider.setValue(int(same_widget.scale))

    def on_checkBox_clicked(self):
        self.fix_flag = True if self.checkBox.isChecked() else False
        quantity_dict[self.name].update_fix_flag(self.fix_flag)
        same_widget_list = widget_dict[self.name]
        for same_widget in same_widget_list:
            if self != same_widget:
                # 更新值
                same_widget.fix_flag = self.fix_flag
                if same_widget.fix_flag:
                    same_widget.checkBox.setCheckState(Qt.Checked)
                else:
                    same_widget.checkBox.setCheckState(Qt.Unchecked)

        # print(self.fix_flag,quantity_dict[self.name].fix_flag)
    def update_by_quantity(self,new_quantity:Quantity):
        quantity_dict[new_quantity.name] = new_quantity
        self.child_quantity = quantity_dict[new_quantity.name].child_quantity
        self.label.setToolTip(f"<html><body>"
                              f"<p><b>{self.description.upper()}</b></p>"
                              f"<p>-----------------------------------------------</p>"
                              f"<p><i><u>Description</u></i>&nbsp;:&nbsp;{self.description}</p>"
                              f"<p><i><u>Name</u></i>&nbsp;:&nbsp;{self.name}</p>"
                              f"<p><i><u>Symbol</u></i>&nbsp;:&nbsp;{self.symbol}</p>"
                              f"<p><i><u>Min.</u></i>&nbsp;:&nbsp;{self.min}</p>"
                              f"<p><i><u>Max.</u></i>&nbsp;:&nbsp;{self.max}</p>"
                              f"<p><i><u>Unit</u></i>&nbsp;:&nbsp;{self.unit}</p>"
                              f"<p><i><u>Convert factor</u></i>&nbsp;:&nbsp;{self.convert_factor}</p>"
                              f"<p><i><u>Is LOG?</u></i>&nbsp;:&nbsp;{self.is_log}</p>"
                              f"<p><i><u>Child parameters</u></i>&nbsp;:&nbsp;{self.child_quantity}</p>"
                              f"</body></html>")


    def setReadOnly(self,state:bool):
        self.read_only = state
        self.horizontalSlider.setDisabled(state)
        self.checkBox.setDisabled(state)
        quantity_dict[self.name].update_enable_flag(not state)
    def update_value(self,value):
        # print('update_value')
        # print(f'before{self.name}:{self.value}')
        self.value = value
        # print(f'after{self.name}:{self.value}')
        if self.is_log:
            self.scale = np.log10(self.value/self.min)/np.log10(self.max/self.min)*Decimal("100.0")
        else:
            self.scale = (self.value-self.min)/(self.max-self.min)*Decimal("100.0")
        self.horizontalSlider.setValue(int(self.scale))
        display_str = '%.2e' % self.value if self.is_log else str(self.value)
        self.lcd_number.display(display_str)
    def get_quantity(self):
        return quantity_dict[self.name]



def reset_dicts():
    # print("reset_dicts")
    # global equation_dict,quantity_dict,widget_dict,actual_equation_dict,actual_quantity_dict
    global quantity_dict,widget_dict,actual_equation_dict,actual_quantity_dict
    # equation_dict.clear()
    quantity_dict.clear()
    widget_dict.clear()
    actual_equation_dict.clear()
    actual_quantity_dict.clear()

class QuantityTreeView(QTreeView):
    def __init__(self, physical_root_equation: Equation):
        super(QuantityTreeView, self).__init__()
        #这里在重建树的时候需要清空所有的字典
        reset_dicts()
        # print("__init__",physical_root_equation)
        self.model = QStandardItemModel()
        self.setHeaderHidden(True)
        self.setModel(self.model)
        root_item = self.model.invisibleRootItem()
        # root_quantity = Quantity('epsilon_prime')
        root_quantity = physical_root_equation.calculation()
        # equation_dict[root_quantity.name] = physical_root_equation
        self.add_node(root_item, root_quantity)
        self.doubleClicked.connect(self.on_item_doubleClicked)
        self.expanded.connect(self.on_item_expanded)
        self.collapsed.connect(self.on_item_collapsed)
        self.expand(self.model.index(0, 0, self.rootIndex()))

    def on_item_expanded(self,index):
        # print("This item is expanded and CANNOT be edited.")
        quantity_widget = self.indexWidget(index)
        quantity_widget.setReadOnly(True)
        # 更新Item下所有节点的enable_flag为True
        self.update_children_enable_state(parent_index=index,enable_state=True)

    def on_item_collapsed(self,index):
        # print("This item is collapsed and CAN be edited.")
        quantity_widget = self.indexWidget(index)
        quantity_widget.setReadOnly(False)
        # 更新Item下所有节点的enable_flag为False
        self.update_children_enable_state(parent_index=index,enable_state=False)

    def update_children_enable_state(self,parent_index,enable_state:bool):
        child_num = self.model.rowCount(parent_index)
        if child_num:
            for row in range(child_num):
                child_index = self.model.index(row, 0, parent_index)
                child_widget = self.indexWidget(child_index)
                # print(child_widget.name,enable_state)
                quantity_dict[child_widget.name].update_enable_flag(enable_state)
                # print(quantity_dict[child_widget.name].enable_flag)

    def add_node(self, parent, quantity: Quantity):
        item = QStandardItem()
        parent.appendRow(item)
        index = self.model.indexFromItem(item)
        quantity_widget = QuantityWidget(index, quantity)
        item.setData(quantity_widget, role=Qt.EditRole)
        self.setIndexWidget(index, quantity_widget)
        for child in quantity.child_quantity:
            self.add_node(item, child)

    def on_item_doubleClicked(self, index):
        old_item = self.model.itemFromIndex(index)
        old_widget = self.indexWidget(index)
        # *这里的逻辑是这样的：
        # 首先判定被双击的item是不是叶节点：not old_item.hasChildren
        #   是--那么判定当前widget的name是否有对应的公式：name in equation_type_dict
        #       是--那么生成公式，装载参数到节点的下面作为子节点
        #       否--那么代表这个参数已经是末端参数，不会有其他操作
        #   否--更新实际的使用的公式和参数的字典
        # 判定被双击的item是不是叶节点：not old_item.hasChildren
        if not old_item.hasChildren():
            #   是--那么判定当前widget的name是否有对应的公式：name in equation_type_dict
            print("It is a leaf old_item.")
            if old_widget.name in equation_type_dict:
                #   是--那么生成公式，装载参数到节点的下面作为子节点.
                equation_type = equation_type_dict[old_widget.name]
                print('This parameter can be expanded by',equation_type)
                # 创建新的item，替换旧的item，然后添加子节点
                # new_item = QStandardItem()
                # 非常重要：这里使用了parameters={}且构造函数中的默认值是{}的方式，这里需要传入一个空字典的原因是Python会自动缓存上一次被调用的时候使用的参数值
                # 另外：目前是双击才会展开公式，如果需要在初始化的时候就把公式完全展开的话，那么需要删除这里的parameters={}，并将parameters的默认值改为None而非{}
                new_equation = Equation(equation_type,parameters={})
                new_quantity = new_equation.calculation()
                old_widget.update_by_quantity(new_quantity)

                for i,widget in enumerate(widget_dict[new_quantity.name]):
                    if widget == old_widget:
                        widget_dict[new_quantity.name].pop(i)
                        break

                for child in new_quantity.child_quantity:
                    self.add_node(old_item, child)
            else:
                #   否--那么代表这个参数已经是末端参数，不会有其他操作
                print('It is a terminal parameter and cannot be expanded.')
        else:
            #   否--更新实际的使用的公式和参数的字典
            print("It is NOT a leaf old_item.")

    def get_physical_model_in_fit(self):
        independent_variable = quantity_dict["f"]
        dependent_variable = quantity_dict["epsilon_prime"]
        other_variable_list = []
        constant_list = []
        parameter_list = []
        for name, quantity in quantity_dict.items():
            if name not in ["f","epsilon_prime"]:
                if quantity.enable_flag:
                    if quantity.fix_flag:
                        constant_list.append(quantity)
                    else:
                        parameter_list.append(quantity)
                else:
                    other_variable_list.append(quantity)
        return independent_variable,dependent_variable, other_variable_list, constant_list, parameter_list

    def update_physical_modal(self,to_parameter_list:List[Quantity]):
        print('update_physical_modal')
        for to_parameter in to_parameter_list:
            for widget in widget_dict[to_parameter.name]:
                widget.update_value(to_parameter.value)
            # print(f'{to_parameter.name}:{to_parameter.value}')




