# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'parameter_setting_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ParameterSettingDialog(object):
    def setupUi(self, ParameterSettingDialog):
        ParameterSettingDialog.setObjectName("ParameterSettingDialog")
        ParameterSettingDialog.resize(640, 720)
        self.verticalLayout = QtWidgets.QVBoxLayout(ParameterSettingDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_psd_all = QtWidgets.QGroupBox(ParameterSettingDialog)
        self.groupBox_psd_all.setObjectName("groupBox_psd_all")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_psd_all)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.listView_psd_all = QtWidgets.QListView(self.groupBox_psd_all)
        self.listView_psd_all.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView_psd_all.setObjectName("listView_psd_all")
        self.verticalLayout_2.addWidget(self.listView_psd_all)
        self.verticalLayout.addWidget(self.groupBox_psd_all)
        self.groupBox_psd_info = QtWidgets.QGroupBox(ParameterSettingDialog)
        self.groupBox_psd_info.setMinimumSize(QtCore.QSize(618, 205))
        self.groupBox_psd_info.setMaximumSize(QtCore.QSize(618, 205))
        self.groupBox_psd_info.setObjectName("groupBox_psd_info")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_psd_info)
        self.gridLayout.setObjectName("gridLayout")
        self.label_psd_info_symbol = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_symbol.setObjectName("label_psd_info_symbol")
        self.gridLayout.addWidget(self.label_psd_info_symbol, 0, 2, 1, 1)
        self.label_psd_info_value = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_value.setObjectName("label_psd_info_value")
        self.gridLayout.addWidget(self.label_psd_info_value, 2, 0, 1, 1)
        self.label_psd_info_min = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_min.setObjectName("label_psd_info_min")
        self.gridLayout.addWidget(self.label_psd_info_min, 3, 0, 1, 1)
        self.label_psd_info_max = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_max.setObjectName("label_psd_info_max")
        self.gridLayout.addWidget(self.label_psd_info_max, 3, 2, 1, 1)
        self.label_psd_info_unit = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_unit.setObjectName("label_psd_info_unit")
        self.gridLayout.addWidget(self.label_psd_info_unit, 4, 0, 1, 1)
        self.label_psd_info_convert_factor = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_convert_factor.setObjectName("label_psd_info_convert_factor")
        self.gridLayout.addWidget(self.label_psd_info_convert_factor, 4, 2, 1, 1)
        self.lineEdit_psd_info_unit = QtWidgets.QLineEdit(self.groupBox_psd_info)
        self.lineEdit_psd_info_unit.setObjectName("lineEdit_psd_info_unit")
        self.gridLayout.addWidget(self.lineEdit_psd_info_unit, 4, 1, 1, 1)
        self.lineEdit_psd_info_min = QtWidgets.QLineEdit(self.groupBox_psd_info)
        self.lineEdit_psd_info_min.setObjectName("lineEdit_psd_info_min")
        self.gridLayout.addWidget(self.lineEdit_psd_info_min, 3, 1, 1, 1)
        self.comboBox_psd_info_name = QtWidgets.QComboBox(self.groupBox_psd_info)
        self.comboBox_psd_info_name.setEditable(True)
        self.comboBox_psd_info_name.setObjectName("comboBox_psd_info_name")
        self.gridLayout.addWidget(self.comboBox_psd_info_name, 0, 1, 1, 1)
        self.lineEdit_psd_info_symbol = QtWidgets.QLineEdit(self.groupBox_psd_info)
        self.lineEdit_psd_info_symbol.setEnabled(True)
        self.lineEdit_psd_info_symbol.setReadOnly(True)
        self.lineEdit_psd_info_symbol.setClearButtonEnabled(False)
        self.lineEdit_psd_info_symbol.setObjectName("lineEdit_psd_info_symbol")
        self.gridLayout.addWidget(self.lineEdit_psd_info_symbol, 0, 3, 1, 1)
        self.label_psd_info_description = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_description.setObjectName("label_psd_info_description")
        self.gridLayout.addWidget(self.label_psd_info_description, 1, 0, 1, 1)
        self.checkBox_psd_info_log = QtWidgets.QCheckBox(self.groupBox_psd_info)
        self.checkBox_psd_info_log.setObjectName("checkBox_psd_info_log")
        self.gridLayout.addWidget(self.checkBox_psd_info_log, 5, 0, 1, 2)
        self.checkBox_psd_info_fix = QtWidgets.QCheckBox(self.groupBox_psd_info)
        self.checkBox_psd_info_fix.setObjectName("checkBox_psd_info_fix")
        self.gridLayout.addWidget(self.checkBox_psd_info_fix, 5, 2, 1, 2)
        self.label_psd_info_name = QtWidgets.QLabel(self.groupBox_psd_info)
        self.label_psd_info_name.setObjectName("label_psd_info_name")
        self.gridLayout.addWidget(self.label_psd_info_name, 0, 0, 1, 1)
        self.lineEdit_psd_info_description = QtWidgets.QLineEdit(self.groupBox_psd_info)
        self.lineEdit_psd_info_description.setReadOnly(False)
        self.lineEdit_psd_info_description.setObjectName("lineEdit_psd_info_description")
        self.gridLayout.addWidget(self.lineEdit_psd_info_description, 1, 1, 1, 4)
        self.lineEdit_psd_info_value = QtWidgets.QLineEdit(self.groupBox_psd_info)
        self.lineEdit_psd_info_value.setObjectName("lineEdit_psd_info_value")
        self.gridLayout.addWidget(self.lineEdit_psd_info_value, 2, 1, 1, 4)
        self.lineEdit_psd_info_convert_factor = QtWidgets.QLineEdit(self.groupBox_psd_info)
        self.lineEdit_psd_info_convert_factor.setObjectName("lineEdit_psd_info_convert_factor")
        self.gridLayout.addWidget(self.lineEdit_psd_info_convert_factor, 4, 3, 1, 2)
        self.lineEdit_psd_info_max = QtWidgets.QLineEdit(self.groupBox_psd_info)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_psd_info_max.sizePolicy().hasHeightForWidth())
        self.lineEdit_psd_info_max.setSizePolicy(sizePolicy)
        self.lineEdit_psd_info_max.setObjectName("lineEdit_psd_info_max")
        self.gridLayout.addWidget(self.lineEdit_psd_info_max, 3, 3, 1, 1)
        self.pushButton_psd_info_greek = QtWidgets.QPushButton(self.groupBox_psd_info)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_psd_info_greek.sizePolicy().hasHeightForWidth())
        self.pushButton_psd_info_greek.setSizePolicy(sizePolicy)
        self.pushButton_psd_info_greek.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/img/alpha.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_psd_info_greek.setIcon(icon)
        self.pushButton_psd_info_greek.setObjectName("pushButton_psd_info_greek")
        self.gridLayout.addWidget(self.pushButton_psd_info_greek, 0, 4, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 1)
        self.verticalLayout.addWidget(self.groupBox_psd_info)
        self.gridLayout_psd_buttons = QtWidgets.QGridLayout()
        self.gridLayout_psd_buttons.setObjectName("gridLayout_psd_buttons")
        self.pushButton_psd_del = QtWidgets.QPushButton(ParameterSettingDialog)
        self.pushButton_psd_del.setEnabled(False)
        self.pushButton_psd_del.setObjectName("pushButton_psd_del")
        self.gridLayout_psd_buttons.addWidget(self.pushButton_psd_del, 0, 1, 1, 1)
        self.pushButton_psd_add = QtWidgets.QPushButton(ParameterSettingDialog)
        self.pushButton_psd_add.setObjectName("pushButton_psd_add")
        self.gridLayout_psd_buttons.addWidget(self.pushButton_psd_add, 0, 0, 1, 1)
        self.label_psd_note = QtWidgets.QLabel(ParameterSettingDialog)
        self.label_psd_note.setObjectName("label_psd_note")
        self.gridLayout_psd_buttons.addWidget(self.label_psd_note, 1, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout_psd_buttons)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(ParameterSettingDialog)
        QtCore.QMetaObject.connectSlotsByName(ParameterSettingDialog)

    def retranslateUi(self, ParameterSettingDialog):
        _translate = QtCore.QCoreApplication.translate
        ParameterSettingDialog.setWindowTitle(_translate("ParameterSettingDialog", "Parameter Setting"))
        self.groupBox_psd_all.setTitle(_translate("ParameterSettingDialog", "All parameters"))
        self.groupBox_psd_info.setTitle(_translate("ParameterSettingDialog", "Parameter info"))
        self.label_psd_info_symbol.setText(_translate("ParameterSettingDialog", "Symbol"))
        self.label_psd_info_value.setText(_translate("ParameterSettingDialog", "Default"))
        self.label_psd_info_min.setText(_translate("ParameterSettingDialog", "Min."))
        self.label_psd_info_max.setText(_translate("ParameterSettingDialog", "Max."))
        self.label_psd_info_unit.setText(_translate("ParameterSettingDialog", "Unit"))
        self.label_psd_info_convert_factor.setText(_translate("ParameterSettingDialog", "Convert factor"))
        self.label_psd_info_description.setText(_translate("ParameterSettingDialog", "Description"))
        self.checkBox_psd_info_log.setText(_translate("ParameterSettingDialog", "is LOG?"))
        self.checkBox_psd_info_fix.setText(_translate("ParameterSettingDialog", "is CONSTANT?"))
        self.label_psd_info_name.setText(_translate("ParameterSettingDialog", "Name"))
        self.pushButton_psd_del.setText(_translate("ParameterSettingDialog", "DELETE"))
        self.pushButton_psd_add.setText(_translate("ParameterSettingDialog", "ADD/UPDATE!"))
        self.label_psd_note.setText(_translate("ParameterSettingDialog", "*Please do not delete parameters at will!"))
import ui.parameter_setting_dialog_rc