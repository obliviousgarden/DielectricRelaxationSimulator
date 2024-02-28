import os, sys
from copy import deepcopy

import matplotlib
from decimal import Decimal
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QStringListModel, QEvent, pyqtSlot, QObject, Qt, QModelIndex, QItemSelectionModel, \
    QItemSelection
from PyQt5.QtGui import QDoubleValidator, QStandardItem, QIntValidator, QPalette, QColor
from PyQt5.QtWidgets import QStyledItemDelegate, QApplication, QLineEdit, QDialog, qApp, QMessageBox, QListWidgetItem, \
    QCheckBox, QAbstractItemView
from physical_model.quantity import Equation, QUANTITY_TYPE, EQUATION_TYPE, Quantity
from physical_model.dielectric_relaxation_simulator import DielectricRelaxationSimulator
from physical_model.fit_result import FitResult
from ui.check_header import CheckHeader
from ui.quantity_widget import QuantityWidget, QuantityTreeView
from ui.main_window import Ui_MainWindow
from ui.parameter_setting_dialog import Ui_ParameterSettingDialog
from ui.greek_alphabet_dialog import Ui_GreekAlphabetDialog
from ui.parameter_info import ParameterInfoDict, ParameterInfo
from ui.result_widget import ResultWidget
from utils.file_name_parser import PARSE_TYPE,file_name_parse
from utils.file_data_reader import file_data_read
import matplotlib.pyplot as plt

from utils.science_plot import SciencePlot,SciencePlotData
from utils.tree_node import model_to_tree
from typing import List

matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def on_Action_quit():
    sys.exit(0)
    pass


class Simulator(Ui_MainWindow):
    def __init__(self, parent = None):
        super(Simulator, self).__init__()
        self.intro_text = {
            "en":"This is a fitting/simulation tool based on the tunneling magneto-dielectric theory for dielectric relaxation processes.\n"
                 "Users are required to construct their own physical models on the left, set physical quantities as constants/parameters, and specify their values (or initial values).\n"
                 "On the right, users need to select fitting/simulation, import and set the required configuration information, and then proceed with the fitting/simulation.",
            "cn": "这是一个基于隧道磁介电理论的用于介电弛豫过程的拟合/仿真工具。\n"
                  "用户需要在左侧构建自己的物理模型，设定物理量为常数/参数，并设定其值（或初始值）。\n"
                  "用户需要在右边选择拟合/仿真，并导入且设置需要的设定信息，然后进行拟合/仿真。",
            "jp": "これは誘電弛緩プロセス用のトンネリング磁気誘電理論に基づいた適合/シミュレーションツールです。\n"
                  "ユーザーは左側で独自の物理モデルを構築し、物理量を定数/パラメータとして設定し、その値（または初期値）を指定する必要があります。\n"
                  "右側では、ユーザーは適合/シミュレーションを選択し、必要な設定情報をインポートおよび設定し、その後、適合/シミュレーションを行う必要があります。"
        }
        self.physical_root_equation = Equation.construction_root_equation()
        self.tab_index = 1 # 0-Fit 1-Simulate
        self.fit_independent_variable = None
        self.fit_dependent_variable = None
        self.fit_other_variable_list = []
        self.fit_constant_list = []
        self.fit_parameter_list = []

        self.simulate_variable_tree = None
        self.simulate_independent_list = []
        self.simulate_dependent_list = []
        self.simulate_dependent_node_list = []
        self.simulate_intermediate_list = []
        self.simulate_independent_var = None
        self.simulate_dependent_var = None
        self.comboBox_simulate_independent_var_model = QStringListModel()
        self.comboBox_simulate_dependent_var_model = QStringListModel()
        self.scientific_validator = QDoubleValidator()
        self.scientific_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.simulate_independent_from = None
        self.simulate_independent_to = None
        self.simulate_independent_points = None
        self.need_intermediate_flag = False
        self.scan_str = "Click the button above!"
        # --------------以下是之前的代码--------------
        self.device = None
        self.dependent_flag = False
        self.dependent_str = 'Magnetic field(H)[Oe]'
        self.low_freq_noise_clipping_flag = False
        self.file_path = []
        self.file_name = []
        self.table_view_file_model = QtGui.QStandardItemModel()
        self.resetTableViewHeaderItems(tableviewmodel=self.table_view_file_model)
        self.list_view_results_model = QtGui.QStandardItemModel()
        # file_name为键
        self.fit_result_dict = {} # 存放fit计算的结果
        self.dependent_dict = {} # 存放dependent功能需要的数据

        self.simulate_result_list = [] # 存放simulate计算的结果是一个quantity的list，第一个quantity是x，后面的是y
        self.table_view_simulate_results_model = QtGui.QStandardItemModel()

        self.layout_plot_epsilon = QtWidgets.QVBoxLayout()
        self.layout_plot_delta_epsilon = QtWidgets.QVBoxLayout()
        self.fig_epsilon = plt.Figure()
        self.canvas_epsilon = FigureCanvas(self.fig_epsilon)
        self.fig_delta_epsilon = plt.Figure()
        self.canvas_delta_epsilon = FigureCanvas(self.fig_delta_epsilon)

        self.quantity_tree_view = None

    def setupUi(self, MainWindow):
        # 继承调用父类的
        Ui_MainWindow.setupUi(self, MainWindow)
        # 菜单功能
        self.actionQuit.triggered.connect(on_Action_quit)
        # self.actionSaveResultsAs.triggered.connect(self.on_Action_save_results_as)
        # 选择tab
        self.tabs.setCurrentIndex(self.tab_index)
        self.tabs.currentChanged.connect(self.on_tabs_currentChanged)
        # EN-CN-JP
        self.textEdit_intro.setText(self.intro_text.get("en"))
        self.radioButton_intro_en.clicked.connect(self.update_textEdit_intro)
        self.radioButton_intro_cn.clicked.connect(self.update_textEdit_intro)
        self.radioButton_intro_jp.clicked.connect(self.update_textEdit_intro)
        self.radioButton_intro_en.click()
        # 然后通过物理模型构建树
        self.update_quantity_tree_view()
        # 绑定获取物理模型的所有信息
        self.pushButton_scan.clicked.connect(self.on_pushButton_scan)
        self.textBrowser_scan.setText(self.scan_str)
        self.textBrowser_scan.setReadOnly(True)
        # --------------以下是之前的代码--------------
        # 设定RadioButton,选择设备
        self.RadioButton_device_impedance.clicked.connect(self.on_RadioButton_device_clicked)
        self.RadioButton_device_lcr.clicked.connect(self.on_RadioButton_device_clicked)
        self.RadioButton_other.clicked.connect(self.on_RadioButton_device_clicked)
        self.RadioButton_device_impedance.click()
        # 设定RadioButton,选择依赖性
        self.RadioButton_dependent_H.clicked.connect(self.on_RadioButton_dependent_clicked)
        self.RadioButton_dependent_Co.clicked.connect(self.on_RadioButton_dependent_clicked)
        self.RadioButton_dependent_DCB.clicked.connect(self.on_RadioButton_dependent_clicked)
        self.RadioButton_dependent_H.click()
        # 设定PushButton
        self.PushButton_file.clicked.connect(self.on_PushButton_file_clicked)
        self.PushButton_dir.clicked.connect(self.on_PushButton_dir_clicked)
        self.PushButton_fit.clicked.connect(self.on_PushButton_fit_clicked)
        self.PushButton_plot.clicked.connect(self.on_PushButton_plot_clicked)
        # self.checkBox_lowfreqnoiseclipping.stateChanged.connect(self.on_checkBox_lowfreqnoiseclipping_stateChanged)
        # 设定TableView内的Model，并禁止编辑
        self.TableView_file.setModel(self.table_view_file_model)
        self.ListView_results.setModel(self.list_view_results_model)
        # self.ListView_results.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # Checkbox
        self.GroupBox_dependent.clicked.connect(self.on_GroupBox_dependent_clicked)
        self.CheckBox_All.stateChanged.connect(self.on_CheckBox_All_stateChanged)
        # 保存物理模型为默认的按钮
        self.pushButton_save_as_default.clicked.connect(self.on_pushButton_save_as_default_clicked)
        # -------------------simulate部分
        self.lineEdit_simulate_independent_from.setValidator(self.scientific_validator)
        self.lineEdit_simulate_independent_to.setValidator(self.scientific_validator)
        self.comboBox_simulate_independent_var.setModel(self.comboBox_simulate_independent_var_model)
        self.comboBox_simulate_dependent_var.setModel(self.comboBox_simulate_dependent_var_model)
        self.comboBox_simulate_independent_var.currentIndexChanged.connect(self.on_comboBox_simulate_independent_var_currentIndexChanged)
        self.comboBox_simulate_dependent_var.currentIndexChanged.connect(self.on_comboBox_simulate_dependent_var_currentIndexChanged)
        self.checkBox_simulate_dependent_intermediate.stateChanged.connect(self.on_checkBox_simulate_dependent_intermediate_stateChanged)
        self.pushButton_simulate.clicked.connect(self.on_pushButton_simulate_clicked)
        self.tableView_simulate_results.setModel(self.table_view_simulate_results_model)
        self.pushButton_simulate_plot.clicked.connect(self.on_pushButton_simulate_plot_clicked)

    def on_tabs_currentChanged(self,index):
        self.tab_index = index
        # print(f'Tab changed, index:{self.tab_index}')

    def update_quantity_tree_view(self):
        print("update_quantity_tree_view")
        if self.verticalLayout.count():
            print("CLEAR")
            self.verticalLayout.takeAt(0).widget().deleteLater()

        self.quantity_tree_view = QuantityTreeView(Equation.construction_root_equation())
        # quantity_tree_view = QuantityTreeView(Equation(EQUATION_TYPE.REAL_PERMITTIVITY))
        self.quantity_tree_view.setObjectName("quantityTreeView")
        self.quantity_tree_view.setRootIsDecorated(False)
        self.verticalLayout.addWidget(self.quantity_tree_view)

    def update_textEdit_intro(self):
        if self.radioButton_intro_en.isChecked():
            self.textEdit_intro.setText(self.intro_text.get("en"))
        elif self.radioButton_intro_cn.isChecked():
            self.textEdit_intro.setText(self.intro_text.get("cn"))
        elif self.radioButton_intro_jp.isChecked():
            self.textEdit_intro.setText(self.intro_text.get("jp"))
        else:
            pass

    def update_textBrowser_scan(self):
        if self.tab_index == 0:
            self.scan_str = "Independent variable :\n\t" + f"{self.fit_independent_variable.symbol}({self.fit_independent_variable.description})[{self.fit_independent_variable.unit}]" + "\n"
            self.scan_str += "Dependent variable :\n\t" +f"{self.fit_dependent_variable.symbol}({self.fit_dependent_variable.description})[{self.fit_dependent_variable.unit}]" + "\n"
            # self.scan_str += "Other variables :\n"
            # for other_variable_quantity in self.other_variable_list:
            #     self.scan_str += "\t" + other_variable_quantity.get_scan_str() + "\n"
            self.scan_str += "Constants :\n"
            for constant_quantity in self.fit_constant_list:
                self.scan_str += "\t" + constant_quantity.get_scan_str() + "\n"
            self.scan_str += "Parameters :\n"
            for parameter_quantity in self.fit_parameter_list:
                self.scan_str += "\t" + parameter_quantity.get_scan_str() + "\n"
        else:
            self.scan_str = "Tree of all variables :\n"+self.simulate_variable_tree.print_tree()
            # print(self.scan_str)
        self.textBrowser_scan.setText(self.scan_str)

    def update_independent_var_info_combo(self):
        name_list = []
        for quantity in self.simulate_independent_list:
            name_list.append(f"{quantity.name} ({quantity.symbol}) : {quantity.description}")
        self.comboBox_simulate_independent_var_model.setStringList(name_list)

    def update_dependent_var_info_combo(self):
        name_list = []
        for quantity in self.simulate_dependent_list:
            name_list.append(f"{quantity.name} ({quantity.symbol}) : {quantity.description}")
        self.comboBox_simulate_dependent_var_model.setStringList(name_list)

    def on_comboBox_simulate_independent_var_currentIndexChanged(self,index):
        self.simulate_independent_var = self.simulate_independent_list[index]
        self.update_independent_var_info_text()
        self.lineEdit_simulate_independent_from.setText(str(self.simulate_independent_var.min))
        self.lineEdit_simulate_independent_to.setText(str(self.simulate_independent_var.max))
        # 更新intermediate变量
        start_node = self.simulate_variable_tree.get_node_by_name(name=self.simulate_dependent_var.name)
        stop_node = self.simulate_variable_tree.get_node_by_name(name=self.simulate_independent_var.name)
        self.simulate_intermediate_list,_ = self.simulate_variable_tree.get_nodes_between_by_name(start_node,stop_node)
        # 排除第一项，因为是第一个根项
        if self.simulate_intermediate_list:
            self.simulate_intermediate_list.pop(0)




    def on_comboBox_simulate_dependent_var_currentIndexChanged(self,index):
        self.simulate_dependent_var = self.simulate_dependent_list[index]
        self.update_dependent_var_info_text()
        node = self.simulate_dependent_node_list[index]
        independent_data_list = node.get_leaf_nodes()
        check_name_list = []
        self.simulate_independent_list = []
        for independent_data in independent_data_list:
            if independent_data.name not in check_name_list:
                check_name_list.append(independent_data.name)
                self.simulate_independent_list.append(independent_data)
        # print(self.simulate_independent_list)
        self.update_independent_var_info_combo()

    def update_independent_var_info_text(self):
        var_info_str = f"{self.simulate_independent_var.name} ({self.simulate_independent_var.symbol}) : {self.simulate_independent_var.description}" \
                       f"\n [{self.simulate_independent_var.unit}] * {self.simulate_independent_var.convert_factor} = [SI unit]" \
                       f"\n LOG? : {self.simulate_independent_var.is_log}"
        self.textBrowser_simulate_independent_info.setText(var_info_str)

    def update_dependent_var_info_text(self):
        var_info_str = f"{self.simulate_dependent_var.name} ({self.simulate_dependent_var.symbol}) : {self.simulate_dependent_var.description}" \
                       f"\n  [{self.simulate_dependent_var.unit}] * {self.simulate_dependent_var.convert_factor} = [SI unit]" \
                       f"\n LOG? : {self.simulate_dependent_var.is_log}"
        self.textBrowser_simulate_dependent_info.setText(var_info_str)

    def on_checkBox_simulate_dependent_intermediate_stateChanged(self,state):
        self.need_intermediate_flag = True if state == 2 else False
        # print(f"on_checkBox_simulate_dependent_intermediate_stateChanged:{self.need_intermediate_flag}")

    def on_pushButton_scan(self):
        # print("on_pushButton_scan")
        if self.tab_index == 0:
            self.fit_independent_variable, self.fit_dependent_variable, self.fit_other_variable_list, self.fit_constant_list, self.fit_parameter_list = self.quantity_tree_view.get_physical_model_in_fit()
        else:
            self.simulate_variable_tree = model_to_tree(self.quantity_tree_view)
            # 在更新scan的字符串之前需要把下方的combobox的内容更新掉
            self.simulate_dependent_list,self.simulate_dependent_node_list = self.simulate_variable_tree.get_non_leaf_nodes()
            # FIXME:也许需要去重
            self.simulate_dependent_var = self.simulate_dependent_list[0]
            self.update_dependent_var_info_combo()
            self.update_dependent_var_info_text()
        self.update_textBrowser_scan()

    def on_pushButton_save_as_default_clicked(self):
        print("on_pushButton_save_as_default_clicked")
    # --------------以下是之前的代码--------------
    def on_RadioButton_device_clicked(self):
        if self.RadioButton_other.isChecked():
            # Device: Other
            self.LineEdit_step1_f_row.setEnabled(True)
            self.LineEdit_step1_f_col.setEnabled(True)
            self.ComboBox_step1_f_unit.setEnabled(True)
            self.LineEdit_step1_Cp_row.setEnabled(True)
            self.LineEdit_step1_Cp_col.setEnabled(True)
            self.ComboBox_step1_Cp_unit.setEnabled(True)
        else:
            self.LineEdit_step1_f_row.setEnabled(False)
            self.LineEdit_step1_f_col.setEnabled(False)
            self.ComboBox_step1_f_unit.setEnabled(False)
            self.LineEdit_step1_Cp_row.setEnabled(False)
            self.LineEdit_step1_Cp_col.setEnabled(False)
            self.ComboBox_step1_Cp_unit.setEnabled(False)
            if self.RadioButton_device_impedance.isChecked():
                # Device: Impedance Analyzer (~120MHz)
                self.LineEdit_step1_f_row.setText("20")
                self.LineEdit_step1_f_col.setText("1")
                self.ComboBox_step1_f_unit.setCurrentIndex(0)
                self.LineEdit_step1_Cp_row.setText("20")
                self.LineEdit_step1_Cp_col.setText("3")
                self.ComboBox_step1_Cp_unit.setCurrentIndex(0)
            elif self.RadioButton_device_lcr.isChecked():
                # Device: LCR Meter (~1MHz)
                self.LineEdit_step1_f_row.setText("16")
                self.LineEdit_step1_f_col.setText("1")
                self.ComboBox_step1_f_unit.setCurrentIndex(0)
                self.LineEdit_step1_Cp_row.setText("16")
                self.LineEdit_step1_Cp_col.setText("2")
                self.ComboBox_step1_Cp_unit.setCurrentIndex(0)
            else:
                print('ERROR. Unknown Device.')
    def resetTableViewHeaderItems(self, tableviewmodel: QtGui.QStandardItemModel):
        table_header_item_0 = QtGui.QStandardItem('file_name')
        table_header_item_0.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_1 = QtGui.QStandardItem('thickness(m)')
        table_header_item_1.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_2 = QtGui.QStandardItem('area(m^2)')
        table_header_item_2.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_3 = QtGui.QStandardItem('H(Oe)')
        table_header_item_3.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_4 = QtGui.QStandardItem('x_Co(at.%)')
        table_header_item_4.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_5 = QtGui.QStandardItem('DCB(V)')
        table_header_item_5.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_6 = QtGui.QStandardItem('OSC(V)')
        table_header_item_6.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        table_header_item_7 = QtGui.QStandardItem('C.C.(1)')
        table_header_item_7.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
        tableviewmodel.setHorizontalHeaderItem(0, table_header_item_0)
        tableviewmodel.setHorizontalHeaderItem(1, table_header_item_1)
        tableviewmodel.setHorizontalHeaderItem(2, table_header_item_2)
        tableviewmodel.setHorizontalHeaderItem(3, table_header_item_3)
        tableviewmodel.setHorizontalHeaderItem(4, table_header_item_4)
        tableviewmodel.setHorizontalHeaderItem(5, table_header_item_5)
        tableviewmodel.setHorizontalHeaderItem(6, table_header_item_6)
        tableviewmodel.setHorizontalHeaderItem(7, table_header_item_7)

    def on_GroupBox_dependent_clicked(self):
        self.dependent_flag = True if self.GroupBox_dependent.isChecked() else False

    # def on_checkBox_lowfreqnoiseclipping_stateChanged(self,state):
    #     self.low_freq_noise_clipping_flag = True if state else False

    def on_RadioButton_dependent_clicked(self):
        if self.RadioButton_dependent_H.isChecked():
            self.dependent_str = "Magnetic field(H)[Oe]"
        elif self.RadioButton_dependent_Co.isChecked():
            self.dependent_str = "Co content(x_Co)[at.%]"
        elif self.RadioButton_dependent_DCB.isChecked():
            self.dependent_str = "DC bias(DCB)[V]"
        else:
            print("Unknown Dependent.")
            self.dependent_str = "Co content(x_Co)[at.%]"

    def on_PushButton_file_clicked(self):
        self.file_name = []
        self.file_path = []
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileNames()
        print('file:', file_name)
        self.file_path = file_name
        self.table_view_file_model.clear()
        self.resetTableViewHeaderItems(self.table_view_file_model)
        for i in range(file_name.__len__()):
            self.file_name.append(file_name[i].split('/')[-1])
            file_name_item = QtGui.QStandardItem(self.file_name[i])
            file_name_item.setEditable(False)
            thickness_value = 1./1.e6 # 1000 nm
            area_value = 1./1.e6 # 1 mm^2
            with open(self.file_path[i], 'r') as file:
                lines = file.readlines()
                if self.RadioButton_device_impedance.isChecked():
                    thickness_value = float(lines[4])/1e6  # um -> m
                    area_value = float(lines[5])/1e4  # cm^2 -> m^2
                elif self.RadioButton_device_lcr.isChecked():
                    thickness_value = float(lines[4])  # m -> m
                    area_value = float(lines[5])  # m^2 -> m^2
                else:
                    # 未知设备的膜厚和电极面积的数值未知
                    pass
            thickness_item = QtGui.QStandardItem('%.5g' % thickness_value)
            thickness_item.setEditable(True)
            thickness_item.setSelectable(False)
            area_item = QtGui.QStandardItem('%.5g' % area_value)
            area_item.setEditable(True)
            area_item.setSelectable(False)
            h_value = file_name_parse(parse_type=PARSE_TYPE.Oe,file_name=self.file_name[i])
            h_item = QtGui.QStandardItem('%.5g' % h_value)
            h_item.setEditable(True)
            h_item.setSelectable(False)
            co_value = file_name_parse(parse_type=PARSE_TYPE.Co,file_name=self.file_name[i])
            co_item = QtGui.QStandardItem('%.5g' % co_value)
            co_item.setEditable(True)
            co_item.setSelectable(False)
            dcb_value = file_name_parse(parse_type=PARSE_TYPE.DCB,file_name=self.file_name[i])
            dcb_item = QtGui.QStandardItem('%.5g' % dcb_value)
            dcb_item.setEditable(True)
            dcb_item.setSelectable(False)
            ocs_value = file_name_parse(parse_type=PARSE_TYPE.OCS,file_name=self.file_name[i])
            ocs_item = QtGui.QStandardItem('%.5g' % ocs_value)
            ocs_item.setEditable(True)
            ocs_item.setSelectable(False)
            cc_item = QtGui.QStandardItem('1')
            cc_item.setEditable(True)
            cc_item.setSelectable(False)
            self.table_view_file_model.appendRow([file_name_item, thickness_item, area_item, h_item, co_item, dcb_item, ocs_item, cc_item])
        print(self.file_path)
        print(self.file_name)
        # 因为刚导入数据，结果解析相关部分全部封住
        self.list_view_results_model.clear()
        self.CheckBox_All.setEnabled(False)
        self.PushButton_plot.setEnabled(False)

    def on_PushButton_dir_clicked(self):
        self.file_name = []
        self.file_path = []
        dir_ = QtWidgets.QFileDialog.getExistingDirectory()
        print('dir:', dir_)
        if dir_ != '':
            self.table_view_file_model.clear()
            self.resetTableViewHeaderItems(self.table_view_file_model)
            self.file_name = os.listdir(dir_)
            for i in range(self.file_name.__len__()):
                self.file_path.append(dir_ + '/' + self.file_name[i])
                file_name_item = QtGui.QStandardItem(self.file_name[i])
                file_name_item.setEditable(False)
                thickness_value = 1./1.e6 # 1000 nm
                area_value = 1./1.e6 # 1 mm^2
                with open(self.file_path[i], 'r') as file:
                    lines = file.readlines()
                    if self.RadioButton_device_impedance.isChecked():
                        thickness_value = float(lines[4])/1e6  # um -> m
                        area_value = float(lines[5])/1e4  # cm^2 -> m^2
                    elif self.RadioButton_device_lcr.isChecked():
                        thickness_value = float(lines[4])  # m -> m
                        area_value = float(lines[5])  # m^2 -> m^2
                    else:
                        # 未知设备的膜厚和电极面积的数值未知
                        pass
                thickness_item = QtGui.QStandardItem('%.5g' % thickness_value)
                thickness_item.setEditable(True)
                thickness_item.setSelectable(False)
                area_item = QtGui.QStandardItem('%.5g' % area_value)
                area_item.setEditable(True)
                area_item.setSelectable(False)
                h_value = file_name_parse(parse_type=PARSE_TYPE.Oe,file_name=self.file_name[i])
                h_item = QtGui.QStandardItem('%.5g' % h_value)
                h_item.setEditable(True)
                h_item.setSelectable(False)
                co_value = file_name_parse(parse_type=PARSE_TYPE.Co,file_name=self.file_name[i])
                co_item = QtGui.QStandardItem('%.5g' % co_value)
                co_item.setEditable(True)
                co_item.setSelectable(False)
                dcb_value = file_name_parse(parse_type=PARSE_TYPE.DCB,file_name=self.file_name[i])
                dcb_item = QtGui.QStandardItem('%.5g' % dcb_value)
                dcb_item.setEditable(True)
                dcb_item.setSelectable(False)
                ocs_value = file_name_parse(parse_type=PARSE_TYPE.OCS,file_name=self.file_name[i])
                ocs_item = QtGui.QStandardItem('%.5g' % ocs_value)
                ocs_item.setEditable(True)
                ocs_item.setSelectable(False)
                cc_item = QtGui.QStandardItem('1')
                cc_item.setEditable(True)
                cc_item.setSelectable(False)
                self.table_view_file_model.appendRow([file_name_item, thickness_item, area_item, h_item, co_item, dcb_item, ocs_item, cc_item])
        print(self.file_path)
        print(self.file_name)
        # 因为刚导入数据，结果解析相关部分全部封住
        self.list_view_results_model.clear()
        self.CheckBox_All.setEnabled(False)
        self.PushButton_plot.setEnabled(False)

    def on_PushButton_fit_clicked(self):
        # 清空列表
        self.on_PushButton_clearAll_clicked()
        # 记得清空一下结果字典
        self.fit_result_dict = {}
        # 全选取消
        self.CheckBox_All.setCheckState(QtCore.Qt.Unchecked)
        # 这里需要根据model构造p0和bounds参数
        # 清空结果的listview
        self.list_view_results_model.clear()
        # 需要的额外参数：f以及Cp 的 第一个数据位置 和 单位，试料的膜厚和电极的面积
        first_pos_info_tuple = (
            (int(self.LineEdit_step1_f_row.text()),
             int(self.LineEdit_step1_f_col.text()),
             str(self.ComboBox_step1_f_unit.currentText())),
            (int(self.LineEdit_step1_Cp_row.text()),
             int(self.LineEdit_step1_Cp_col.text()),
             str(self.ComboBox_step1_Cp_unit.currentText()))
        )
        # 来自tableview的size info
        info_dict = {}
        for row in range(self.table_view_file_model.rowCount()):
            info_dict[self.table_view_file_model.item(row, 0).text()] = [
                float(self.table_view_file_model.item(row, 1).text()),
                float(self.table_view_file_model.item(row, 2).text()),
                float(self.table_view_file_model.item(row, 3).text()),
                float(self.table_view_file_model.item(row, 4).text()),
                float(self.table_view_file_model.item(row, 5).text()),
                float(self.table_view_file_model.item(row, 6).text()),
                float(self.table_view_file_model.item(row, 7).text()),
            ]
        raw_data_dict = {}
        for index,file_name in enumerate(self.file_name):
            raw_data_dict[file_name] = file_data_read(self.file_path[index],first_pos_info_tuple,info_dict[file_name])

        my_simulator = DielectricRelaxationSimulator(self.physical_root_equation, self.fit_independent_variable, self.fit_dependent_variable, self.fit_constant_list, self.fit_parameter_list)
        print(f'my_simulator.fit:\nFit info.:\nEquation type:{self.physical_root_equation}\nIndependent value:{self.fit_independent_variable}\nDependent value:{self.fit_dependent_variable}')
        print('Constant list:')
        for constant in self.fit_constant_list:
            print(f'\t{constant.name},{constant.symbol}:{constant.value}[{constant.unit}]')
        print('Parameter List:')
        for parameter in self.fit_parameter_list:
            print(f'\t{parameter.name},{parameter.symbol}:{parameter.value}({parameter.min}~{parameter.max})[{parameter.unit}]')
        cal_data_dict = {}
        popt_dict = {}
        pcov_dict = {}
        for file_name,raw_data in raw_data_dict.items():
            cal_y_list,popt,pcov = my_simulator.fit(raw_data[0],raw_data[1])
            cal_data_dict[file_name] = cal_y_list
            popt_dict[file_name] = popt
            pcov_dict[file_name] = pcov
        print('Fitted!')
        for file_name,cal_data in cal_data_dict.items():
            print(f'Filename:{file_name}')
            for index,parameter in enumerate(self.fit_parameter_list):
                print(f'\tParameter Optimal-{index}:')
                print(f'\t{parameter.name},{parameter.symbol}:{popt_dict[file_name][index]}[{parameter.unit}]')
            print('\tParameter Covariance:')
            print(f'\t{pcov_dict[file_name]}')
            # 更新result_dict
            x = deepcopy(self.fit_independent_variable)
            raw_y = deepcopy(self.fit_dependent_variable)
            cal_y = deepcopy(self.fit_dependent_variable)
            print(type(x))
            x.update_value(raw_data_dict[file_name][0])
            raw_y.update_value(raw_data_dict[file_name][1])
            cal_y.update_value(cal_data_dict[file_name])
            fit_result = FitResult(
                file_name=file_name,
                info_dict={
                    'Thickness(t)[m]':info_dict[file_name][0],
                    'Area(A)[m^2]':info_dict[file_name][1],
                    'Magnetic field(H)[Oe]':info_dict[file_name][2],
                    'Co content(x_Co)[at.%]':info_dict[file_name][3],
                    'DC bias(DCB)[V]':info_dict[file_name][4],
                    'AC oscillation(OSC)[V]':info_dict[file_name][5],
                    'Convert constant(C.C.)[1]':info_dict[file_name][6]
                },
                constant_list=self.fit_constant_list,
                parameter_list=self.fit_parameter_list,
                x=x,
                raw_y=raw_y,
                cal_y=cal_y,
                popt=popt_dict[file_name],
                pcov=pcov_dict[file_name]
            )
            self.fit_result_dict[file_name] = fit_result
            # 更新UI
            result_item = QStandardItem()
            self.list_view_results_model.appendRow(result_item)
            index = self.list_view_results_model.indexFromItem(result_item)
            result_widget = ResultWidget(index, file_name, self.fit_parameter_list, popt_dict[file_name], pcov_dict[file_name], raw_data_dict[file_name][0], raw_data_dict[file_name][1], cal_data)
            result_item.setData(result_widget, role=Qt.EditRole)
            self.ListView_results.setIndexWidget(index, result_widget) # 注意：这句话非常重要
            result_item.setSizeHint(result_widget.sizeHint())
        self.ListView_results.update()
        # 更新parameterlist，用parameterlist更新TreeView里面的数值
        for index,parameter in enumerate(self.fit_parameter_list):
            parameter.update_value(next(iter(popt_dict.values()))[index])
        self.quantity_tree_view.update_physical_modal(self.fit_parameter_list)
        # 拟合完成，可以选择ALL，以及绘图了
        self.CheckBox_All.setEnabled(True)
        self.PushButton_plot.setEnabled(True)
    def on_pushButton_simulate_clicked(self):
        # TODO:参数的检查，检查不通过直接返回
        # 清空记录simulate结果的字典
        self.simulate_result_list = []
        # 清空结果的tableview
        self.table_view_simulate_results_model.clear()
        # 通过因变量找到方程组
        simulate_equation = Equation.construction_equation(self.simulate_dependent_var)
        # 构建常数列表
        constant_list = []
        # 排除simulate_dependent_var
        # 排除intermediate之内的参数！！！否则中间参数会作为常数参与计算
        for constant in self.simulate_independent_list:
            if constant.name != self.simulate_independent_var.name and constant not in self.simulate_intermediate_list:
                constant_list.append(constant)
        my_simulator = DielectricRelaxationSimulator(simulate_equation,
                                                     self.simulate_independent_var,
                                                     self.simulate_dependent_var,
                                                     constant_list,
                                                     [])
        # 构造自变量取值范围x_list
        from_value = Decimal(self.lineEdit_simulate_independent_from.text())
        to_value = Decimal(self.lineEdit_simulate_independent_to.text())
        points = self.spinBox_simulate_dependent_points.value()
        if self.simulate_independent_var.is_log:
            exponents = np.linspace(float(np.log10(from_value)), float(np.log10(to_value)), points)
            x_list = [Decimal(10) ** Decimal(exp) for exp in exponents]
        else:
            x_list = [Decimal(x) for x in np.linspace(float(from_value), float(to_value), points)]
        y_list = my_simulator.simulate(x_list=x_list)
        x_quantity = deepcopy(self.simulate_independent_var)
        x_quantity.update_value(x_list)
        y_quantity = deepcopy(self.simulate_dependent_var)
        y_quantity.update_value(y_list)
        y_quantity_list = [y_quantity]
        if self.need_intermediate_flag:
            for intermediate_quantity in self.simulate_intermediate_list:
                intermediate_equation = Equation.construction_equation(intermediate_quantity)
                intermediate_constant_list = []
                # NOTE:这里需要构造出中间参数的常数列表，不可以用之前的常数列表，因为结果的部分是作为常数存放在其中的
                intermediate_node = self.simulate_variable_tree.get_node_by_name(intermediate_quantity.name)
                intermediate_independent_data_list = intermediate_node.get_leaf_nodes()
                check_name_list = []
                for constant in intermediate_independent_data_list:
                    if constant.name != intermediate_quantity.name and constant not in self.simulate_intermediate_list:
                        check_name_list.append(constant.name)
                        intermediate_constant_list.append(constant)
                intermediate_simulator = DielectricRelaxationSimulator(intermediate_equation,
                                                                       self.simulate_independent_var,
                                                                       intermediate_quantity,
                                                                       intermediate_constant_list,[])
                intermediate_y_list = intermediate_simulator.simulate(x_list=x_list)
                y_quantity = deepcopy(intermediate_quantity)
                y_quantity.update_value(intermediate_y_list)
                y_quantity_list.append(y_quantity)
        # 计算结束，数据更新到结果的TableView中
        self.simulate_result_list = [x_quantity]+y_quantity_list
        self.update_simulate_results_table()

    def update_simulate_results_table(self):
        # 专门用simulate_result_list来更新simulate结果的表格的方法
        for index,quantity in enumerate(self.simulate_result_list):
            header_item = QtGui.QStandardItem(quantity.get_header_str())
            header_item.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Black))
            body_items = []
            for value in quantity.value:
                body_item = QtGui.QStandardItem(f"{value:.5f}")
                if index == 0:
                    body_item.setEditable(False)
                body_items.append(body_item)
            self.table_view_simulate_results_model.appendColumn(body_items)
            self.table_view_simulate_results_model.setHorizontalHeaderItem(index,header_item)
        self.tableView_simulate_results.resizeColumnsToContents()
        self.tableView_simulate_results.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tableView_simulate_results.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.tableView_simulate_results.selectionModel().selectionChanged.connect(self.on_tableView_simulate_results_selectionChanged)

        palette = self.tableView_simulate_results.palette()
        palette.setColor(QPalette.Highlight, QColor("blue"))  # 设置背景颜色为蓝色
        palette.setColor(QPalette.HighlightedText, QColor("white"))  # 设置文本颜色为白色
        self.tableView_simulate_results.setPalette(palette)

        self.tableView_simulate_results.selectAll()
        # for row in range(self.table_view_simulate_results_model.rowCount()):
        #     for col in range(self.table_view_simulate_results_model.columnCount()):
        #         index = self.table_view_simulate_results_model.index(row, col)
        #         self.tableView_simulate_results.selectionModel().select(index, QItemSelectionModel.Select)


    def on_tableView_simulate_results_selectionChanged(self,selected:QItemSelection , deselected:QItemSelection):
        # if selected.indexes():
        #     print(f"selected:{selected.indexes()[0].row()},{selected.indexes()[0].column()}")
        if deselected.indexes():
            # print(f"deselected:{deselected.indexes()[0].row()},{deselected.indexes()[0].column()}")
            if deselected.indexes()[0].column() == 0:
                self.tableView_simulate_results.selectColumn(0)
            else:
                #其他列被取消选择的时候，如果没有一列y被选择那么重新选择这一行
                all_selected_col = self.tableView_simulate_results.selectionModel().selectedColumns()
                if len(all_selected_col) == 1:
                    self.tableView_simulate_results.selectColumn(deselected.indexes()[0].column())

    def on_CheckBox_All_stateChanged(self,state):
        # 遍历model，设定所有的widget的check状态和这个checkbox一致
        for row in range(self.list_view_results_model.rowCount()):
            widget = self.ListView_results.indexWidget(self.list_view_results_model.index(row,0))
            widget.check_this(state)

    def on_PushButton_clearAll_clicked(self):
        self.list_view_results_model.clear()
        print('Result cleared.')

    def on_PushButton_plot_clicked(self):
        print('Plot')
        # FIXME：total感觉没什么用，暂时关闭
        # science_plot_data_total = SciencePlotData()
        science_plot_data_respective = SciencePlotData()
        # total_get_flag = True
        # figure_title_total = 'figure_title_total'
        for row in range(self.list_view_results_model.rowCount()):
            widget = self.ListView_results.indexWidget(self.list_view_results_model.index(row,0))
            if widget.is_checked:
                fit_result = self.fit_result_dict[widget.file_name]
                # if total_get_flag:
                #     figure_title_total,x_label_total,y_label_total = fit_result.get_science_plot_info_total()
                #     science_plot_data_total.add_figure_info(figure_title=figure_title_total,x_label=x_label_total,y_label=y_label_total)
                #     total_get_flag = False
                file_name, figure_title, x_label, y_label, x_data, raw_y_legend, raw_y_data, cal_y_legend, cal_y_data = fit_result.get_science_plot_info()

                # science_plot_data_total.add_plot_data(figure_title=figure_title_total,x_data=x_data,y_data=raw_y_data,y_legend=file_name+raw_y_legend)
                # science_plot_data_total.add_plot_data(figure_title=figure_title_total,x_data=x_data,y_data=cal_y_data,y_legend=file_name+cal_y_legend)
                science_plot_data_respective.add_figure_info(figure_title=figure_title,x_label=x_label,y_label=y_label)
                science_plot_data_respective.add_plot_data(figure_title=figure_title,x_data=x_data,y_data=raw_y_data,y_legend=raw_y_legend)
                science_plot_data_respective.add_plot_data(figure_title=figure_title,x_data=x_data,y_data=cal_y_data,y_legend=cal_y_legend)

        # SciencePlot.sci_plot(science_plot_data_total)
        SciencePlot.sci_plot(science_plot_data_respective)

        if self.dependent_flag:
            # 所有参数关于dependent的变化值
            science_plot_data_dependent = SciencePlotData()
            figure_title_list = []
            x_data_list = [] # info的list
            y_data_dict = {} # x对应的list的dict
            y_legend_list = []
            info_get_flag = True
            for row in range(self.list_view_results_model.rowCount()):
                widget = self.ListView_results.indexWidget(self.list_view_results_model.index(row,0))
                if widget.is_checked:
                    fit_result = self.fit_result_dict[widget.file_name]
                    if info_get_flag:
                        figure_title_list,x_label,y_label_list,y_legend_list = fit_result.get_science_plot_info_dependent_total(self.dependent_str)
                        # 生成不同y参数对应的图
                        for index,figure_title in enumerate(figure_title_list):
                            science_plot_data_dependent.add_figure_info(figure_title=figure_title,x_label=x_label,y_label=y_label_list[index])
                        info_get_flag = False
                    x_value,parameter_value_dict = fit_result.get_science_plot_info_dependent(self.dependent_str)
                    x_data_list.append(x_value)
                    for figure_title, y_value in parameter_value_dict.items():
                        if figure_title in y_data_dict:
                            y_data_dict[figure_title].append(y_value)
                        else:
                            y_data_dict[figure_title]=[y_value]
            for index,figure_title in enumerate(figure_title_list):
                science_plot_data_dependent.add_plot_data(figure_title=figure_title,x_data=x_data_list,y_data=y_data_dict[figure_title],y_legend=y_legend_list[index])
            SciencePlot.sci_plot(science_plot_data_dependent)

    def on_pushButton_simulate_plot_clicked(self):
        # TODO:从表格中获取数据，然后让science_plot_data进行绘图
        print('PLOT')
        selected_col_list = list({index.column() for index in self.tableView_simulate_results.selectedIndexes()})
        header_list = []
        body_list = []
        for col in selected_col_list:
            header_list.append(self.table_view_simulate_results_model.horizontalHeaderItem(col).text())
            body=[]
            for row in range(self.table_view_simulate_results_model.rowCount()):
                body.append(float(self.table_view_simulate_results_model.itemFromIndex(self.table_view_simulate_results_model.index(row,col)).text()))
            body_list.append(body)
        print(header_list,body_list)
        # 开始为绘图组装数据
        if self.simulate_result_list[0].is_log:
            x_label = f'LOG({header_list[0]})'
            x_data = np.log10(body_list[0])
        else:
            x_label = header_list[0]
            x_data = body_list[0]
        y_data_list = body_list[1:]
        science_plot_data = SciencePlotData()
        for index, y_header in enumerate(header_list[1:]):
            y_legend = deepcopy(y_header)
            if self.simulate_result_list[selected_col_list[index]].is_log:
                y_label = f'LOG({y_header})'
                y_data = np.log10(y_data_list[index])
            else:
                y_label = y_header
                y_data = y_data_list[index]
                pass
            figure_title = f'{y_label} on {x_label}'
            science_plot_data.add_figure_info(figure_title=figure_title,x_label=x_label,y_label=y_label)
            science_plot_data.add_plot_data(figure_title=figure_title, x_data=x_data, y_data=y_data,y_legend=y_legend)
        SciencePlot.sci_plot(science_plot_data)

# 这里自定义Dialog的目的在于特殊字符的插入需要知道插入的位置
class ParameterSettingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.previous_line_edit_widget = None
        qApp.installEventFilter(self)
    def eventFilter(self, obj, event):
        # print("eventFilter",obj,event.type())
        if event.type() == event.FocusIn:
            if obj.objectName() in ["lineEdit_psd_info_symbol","lineEdit_psd_info_description","lineEdit_psd_info_unit"]:
                self.previous_line_edit_widget = obj
                # print("FocusIn",obj.objectName())
        return super().eventFilter(obj, event)


class ParameterSettingDialogWindow(Ui_ParameterSettingDialog):
    def __init__(self, parent=None, simulator=None):
        super(ParameterSettingDialogWindow, self).__init__()
        self.simulator = simulator
        self.all_parameter_dict = {}  # 存放所有参数信息的一个dict和最上方的groupBox是对应的
        self.listView_psd_all_model = QStringListModel()
        self.comboBox_psd_info_name_model = QStringListModel()
        self.info_dict = {} # 存放编辑参数信息的一个dict
        self.scientific_validator = QDoubleValidator()
        self.scientific_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.dialog = None

    def setupUi(self, ParameterSettingDialog):
        Ui_ParameterSettingDialog.setupUi(self, ParameterSettingDialog)
        self.dialog = ParameterSettingDialog
        self.lineEdit_psd_info_value.setValidator(self.scientific_validator)
        self.lineEdit_psd_info_min.setValidator(self.scientific_validator)
        self.lineEdit_psd_info_max.setValidator(self.scientific_validator)
        self.lineEdit_psd_info_convert_factor.setValidator(self.scientific_validator)
        self.pushButton_psd_add.clicked.connect(self.on_pushButton_psd_add_clicked)
        self.pushButton_psd_del.clicked.connect(self.on_pushButton_psd_del_clicked)
        self.listView_psd_all.setModel(self.listView_psd_all_model)
        self.listView_psd_all.clicked.connect(self.on_listView_psd_all_clicked)
        self.comboBox_psd_info_name.setModel(self.comboBox_psd_info_name_model)
        self.comboBox_psd_info_name.currentIndexChanged.connect(self.on_comboBox_psd_info_name_currentIndexChanged)
        self.update_listView_psd_all()
        self.lineEdit_psd_info_description.setFocus()  # 聚焦防止特殊字符被插入组件是None

    def update_listView_psd_all(self):
        self.all_parameter_dict = ParameterInfoDict.parameter_info_dict
        all_parameter_str_list = []
        for parameter_info in self.all_parameter_dict.values():
            parameter_info_str = parameter_info.to_str()
            all_parameter_str_list.append(parameter_info_str)
        self.listView_psd_all_model.setStringList(all_parameter_str_list)
        self.update_comboBox_psd_info_name()

    def update_comboBox_psd_info_name(self):
        all_parameter_name_list = []
        for parameter_info in self.all_parameter_dict.values():
            all_parameter_name_list.append(parameter_info.name)
        self.comboBox_psd_info_name_model.setStringList(all_parameter_name_list)

    def on_listView_psd_all_clicked(self,index):
        self.comboBox_psd_info_name.setCurrentIndex(index.row())

    def on_comboBox_psd_info_name_currentIndexChanged(self,index):
        selected_name = self.comboBox_psd_info_name.currentText()
        if selected_name in self.all_parameter_dict:
            self.update_parameter_info(self.all_parameter_dict[selected_name])

    def update_parameter_info(self,parameter_info:ParameterInfo):
        self.lineEdit_psd_info_symbol.setText(parameter_info.symbol)
        self.lineEdit_psd_info_description.setText(parameter_info.description)
        self.lineEdit_psd_info_value.setText(str(parameter_info.default_value))
        self.lineEdit_psd_info_min.setText(str(parameter_info.min))
        self.lineEdit_psd_info_max.setText(str(parameter_info.max))
        self.lineEdit_psd_info_unit.setText(parameter_info.unit)
        self.lineEdit_psd_info_convert_factor.setText(str(parameter_info.convert_factor))
        self.checkBox_psd_info_log.setCheckState(QtCore.Qt.CheckState.Checked if parameter_info.is_log else QtCore.Qt.CheckState.Unchecked)
        self.checkBox_psd_info_fix.setCheckState(QtCore.Qt.CheckState.Checked if parameter_info.fix_flag else QtCore.Qt.CheckState.Unchecked)
        self.checkBox_psd_info_log.update()
        self.checkBox_psd_info_fix.update()

    def on_pushButton_psd_add_clicked(self):
        # 检查数据
        check_flag = True
        new_description = self.lineEdit_psd_info_description.text()
        new_name = self.comboBox_psd_info_name.currentText()
        if not new_name:
            check_flag = False
        new_symbol = self.lineEdit_psd_info_symbol.text()
        if not new_symbol:
            check_flag = False
        new_min = self.lineEdit_psd_info_min.text()
        if not new_min:
            check_flag = False
        new_max = self.lineEdit_psd_info_max.text()
        if not new_max:
            check_flag = False
        new_value = self.lineEdit_psd_info_value.text()
        if not new_value:
            check_flag = False
        new_unit = self.lineEdit_psd_info_unit.text()
        if not new_unit:
            new_unit = "1"
        new_convert_factor = self.lineEdit_psd_info_convert_factor.text()
        if not new_convert_factor:
            new_convert_factor = "1"

        if check_flag and float(new_max)>float(new_min) and float(new_value)>=float(new_min) and float(new_value)<=float(new_max):
            # 打包成ParamInfo的对象传给ParameterInfoDict统一处理
            new_parameter_info = ParameterInfo(new_description,
                                               new_name,
                                               new_symbol,
                                               new_min,
                                               new_max,
                                               new_value,
                                               new_unit,
                                               new_convert_factor,
                                               self.checkBox_psd_info_log.isChecked(),
                                               self.checkBox_psd_info_fix.isChecked())
            rst = param_info_dict_obj.add_update_by_info(new_parameter_info)
            if rst:
                QMessageBox.information(self.dialog, 'Information', 'successfully added/updated.')
                combobox_index = self.comboBox_psd_info_name.currentIndex()
                self.update_listView_psd_all()
                self.update_comboBox_psd_info_name()
                self.comboBox_psd_info_name.setCurrentIndex(combobox_index)
                # TODO:传递给parent，让主界面的参数全部发生变化
                self.simulator.update_quantity_tree_view()
            else:
                QMessageBox.information(self.dialog, 'Information', 'failed to add/update.')
        else:
            QMessageBox.information(self.dialog, 'Information', 'inappropriate parameters.')

    # FIXME:封印删除方法
    def on_pushButton_psd_del_clicked(self):
        # 弹窗警告
        del_parameter_name = self.comboBox_psd_info_name.currentText()
        reply = QMessageBox.question(self.dialog, 'Warning', f'Do you ensure to delete {del_parameter_name}?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            rst = param_info_dict_obj.del_by_name(del_parameter_name)
            if rst:
                QMessageBox.information(self.dialog, 'Information', 'successfully deleted.')
                self.update_listView_psd_all()
                self.update_comboBox_psd_info_name()
            else:
                QMessageBox.information(self.dialog, 'Information', 'failed to delete.')


class GreekAlphabetDialogWindow(Ui_GreekAlphabetDialog):
    def __init__(self, parent=None, parameter_setting_dialog=None):
        super(Ui_GreekAlphabetDialog, self).__init__()
        self.parameter_setting_dialog = parameter_setting_dialog
    def setupUi(self, GreekAlphabetDialog):
        Ui_GreekAlphabetDialog.setupUi(self, GreekAlphabetDialog)
        for row in range(self.gridLayout.rowCount()):
            for col in range(self.gridLayout.columnCount()):
                item = self.gridLayout.itemAtPosition(row,col)
                if item is not None:
                    line_edit_widget = item.widget()
                    line_edit_widget.mouseDoubleClickEvent = lambda event, text=line_edit_widget.text(): self.on_LabelDoubleClicked(text)
    def on_LabelDoubleClicked(self,text):
        focus_widget = self.parameter_setting_dialog.dialog.previous_line_edit_widget
        if focus_widget:
            old_text = focus_widget.text()
            focus_widget.setText(old_text+text)



if __name__ == "__main__":
    # 必须添加应用程序，同时不要忘了sys.argv参数
    app = QtWidgets.QApplication(sys.argv)
    user_data_dir = app.applicationDirPath()  # 获取应用程序的路径
    user_data_dir = os.path.join(user_data_dir, "userdata")  # 拼接子目录
    os.makedirs(user_data_dir, exist_ok=True)  # 确保目录存在
    # 分别对窗体进行实例化
    mainWindow = QtWidgets.QMainWindow()
    # parameterSettingDialog = ParameterSettingDialog()
    parameterSettingDialog = ParameterSettingDialog()
    greekAlphabetDialog = QtWidgets.QDialog()
    # 包装
    param_info_dict_obj = ParameterInfoDict(user_data_dir)
    simulator = Simulator()
    parameterSettingDialogWindow = ParameterSettingDialogWindow(simulator=simulator)
    greekAlphabetDialogWindow = GreekAlphabetDialogWindow(parameter_setting_dialog=parameterSettingDialogWindow)
    # 分别初始化UI
    simulator.setupUi(mainWindow)
    parameterSettingDialogWindow.setupUi(parameterSettingDialog)
    greekAlphabetDialogWindow.setupUi(greekAlphabetDialog)
    # 连接窗体
    simulator.actionParameter_Setting.triggered.connect(parameterSettingDialog.show)
    parameterSettingDialogWindow.pushButton_psd_info_greek.clicked.connect(greekAlphabetDialog.show)

    mainWindow.show()  # show（）显示主窗口

    # 软件正常退出
    sys.exit(app.exec_())
