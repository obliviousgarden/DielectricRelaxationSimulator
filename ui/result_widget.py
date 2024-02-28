import numpy as np
from PyQt5.QtCore import QModelIndex,Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QCheckBox,QSizePolicy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ResultWidget(QWidget):
    def __init__(self,index: QModelIndex,file_name:str,parameter_list,optimal_list,covariance_matrix,x_list,raw_y_list,cal_y_list):
        super(ResultWidget, self).__init__()
        self.file_name = file_name
        self.parameter_list = parameter_list
        self.optimal_list = optimal_list
        self.covariance_matrix = covariance_matrix
        self.x_list = x_list
        self.raw_y_list = raw_y_list
        self.cal_y_list = cal_y_list

        self.row_index = index.row()
        self.col_index = index.column()
        self.layout = QVBoxLayout()
        self.layout.setObjectName(f"horizontalLayout_result_{self.row_index}_{self.col_index}")

        self.is_checked = False
        self.checkbox = QCheckBox(f"File-{self.row_index}:{self.file_name}")
        self.checkbox.stateChanged.connect(self.on_checkbox_stateChanged)
        self.layout.addWidget(self.checkbox)
        # 下面经常会报错ValueError: figure size must be positive finite not [ 3.84 -0.01]
        # 所以改写成以下的形式，输出为默认大小的50%
        default_figsize = plt.rcParams['figure.figsize']
        new_figsize = (default_figsize[0] / 2, default_figsize[1] / 2)
        figure = Figure(figsize=new_figsize)
        ax = figure.add_subplot(111)
        ax.scatter(self.x_list, self.raw_y_list, color='gray')
        ax.plot(self.x_list, self.cal_y_list, color='red')
        ax.set_xscale('log')
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(canvas)

        label_str = ''
        tooltip_str = f"<html><body>" \
                      f"<p><b>File:{self.file_name}</b></p>" \
                      f"<p>-----------------------------------------------</p>" \
                      f"<p><b>Optimal values:</b></p>"
        for i,parameter in enumerate(self.parameter_list):
            if i > 0:
                label_str = label_str + '\n'
            label_str = label_str + f'    {parameter.name},{parameter.symbol}:{"{:.4g}".format(self.optimal_list[i])}[{parameter.unit}]'
            tooltip_str = tooltip_str + f"<p><i><u>{parameter.name},{parameter.symbol}</u></i>&nbsp;:&nbsp;{self.optimal_list[i]}[{parameter.unit}]</p>"
        # covariance_matrix_str = np.array_str(covariance_matrix, precision=2, suppress_small=True)
        covariance_matrix_str = ""
        for row in covariance_matrix:
            # row_str = np.array_str(row, precision=2, suppress_small=True)[1:-1]
            row_str = np.array_str(row, precision=2, suppress_small=True)[1:-1]
            covariance_matrix_str = covariance_matrix_str + f"<p>{row_str}</p>"
        tooltip_str = tooltip_str + f"<p>-----------------------------------------------</p>" \
                                    f"<p><b>Covariance matrix:</b></p>" \
                                    f"{covariance_matrix_str}"
        self.label = QLabel(label_str)
        self.label.setObjectName(f"label_result_{self.row_index}_{self.col_index}")
        self.label.setToolTip(tooltip_str)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def on_checkbox_stateChanged(self,state):
        if state == Qt.Checked:
            self.is_checked = True
        else:
            self.is_checked = False

    def check_this(self,state):
        self.checkbox.setCheckState(state)








