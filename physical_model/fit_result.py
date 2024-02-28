import numpy as np

from physical_model.quantity import Quantity
from typing import List,Dict,Tuple


#1个fitresult对应一个可序列化对象
class FitResult:
    def __init__(self,file_name:str,info_dict:Dict[str,float],constant_list:List[Quantity],parameter_list:List[Quantity],x:Quantity,raw_y:Quantity,cal_y:Quantity,popt:List,pcov:List):
        self.file_name = file_name
        self.info_dict = info_dict
        self.constant_list = constant_list
        self.parameter_list = []
        for index,parameter in enumerate(parameter_list):
            parameter.update_value(popt[index])
            self.parameter_list.append(parameter)
        self.x = x
        self.raw_y = raw_y
        self.cal_y = cal_y
        self.popt = popt
        self.pcov = pcov

    def residual(self):
        return self.cal_y.value - self.raw_y.value

    def residual_sum_square(self):
        return np.sum(self.residual()**2)

    def get_science_plot_info_total(self,x_is_log:bool=None,y_is_log:bool=None):
        figure_title_total = f"Dependence of {self.raw_y.name}({self.raw_y.description}) on {self.x.name}({self.x.description})"
        if x_is_log is None:
            x_is_log = self.x.is_log
        if y_is_log is None:
            y_is_log = self.raw_y.is_log
        if x_is_log:
            x_label_total = f"LOG {self.x.name}({self.x.symbol})[{self.x.unit}]"
        else:
            x_label_total = f"{self.x.name}({self.x.symbol})[{self.x.unit}]"
        if y_is_log:
            y_label_total = f"LOG {self.raw_y.name}({self.raw_y.symbol})[{self.raw_y.unit}]"
        else:
            y_label_total = f"{self.raw_y.name}({self.raw_y.symbol})[{self.raw_y.unit}]"
        return figure_title_total,x_label_total,y_label_total

    def get_science_plot_info(self,x_is_log:bool=None,y_is_log:bool=None):
        file_name = self.file_name
        figure_title = f"{self.file_name}: dependence of {self.raw_y.name}({self.raw_y.description}) on {self.x.name}({self.x.description})"
        raw_y_legend = f"{self.raw_y.name}--raw"
        cal_y_legend = f"{self.cal_y.name}--cal"
        if x_is_log is None:
            x_is_log = self.x.is_log
        if y_is_log is None:
            y_is_log = self.raw_y.is_log
        if x_is_log:
            x_label = f"LOG {self.x.name}({self.x.symbol})[{self.x.unit}]"
            x_data = np.log10(self.x.value)
        else:
            x_label = f"{self.x.name}({self.x.symbol})[{self.x.unit}]"
            x_data = self.x.value
        if y_is_log:
            y_label = f"LOG {self.raw_y.name}({self.raw_y.symbol})[{self.raw_y.unit}]"
            raw_y_data = np.log10(self.raw_y.value)
            cal_y_data = np.log10(self.cal_y.value)
        else:
            y_label = f"{self.raw_y.name}({self.raw_y.symbol})[{self.raw_y.unit}]"
            raw_y_data = self.raw_y.value
            cal_y_data = self.cal_y.value
        return file_name, figure_title, x_label, y_label, x_data, raw_y_legend, raw_y_data, cal_y_legend, cal_y_data

    def get_science_plot_info_dependent_total(self,info_str:str)->Tuple[List[str], str, List[str], List[str]]:
        figure_title_list = []
        x_label = info_str
        y_label_list = []
        y_legend_list = []
        for parameter in self.parameter_list:
            figure_title = f"Dependence of {parameter.name}({parameter.description}) on {info_str}"
            if parameter.is_log:
                y_label = f"LOG {parameter.name}({parameter.symbol})[{parameter.unit}]"
            else:
                y_label = f"{parameter.name}({parameter.symbol})[{parameter.unit}]"
            figure_title_list.append(figure_title)
            y_label_list.append(y_label)
            y_legend_list.append(f"{parameter.name}")
        return figure_title_list,x_label,y_label_list,y_legend_list

    def get_science_plot_info_dependent(self,info_str:str):
        x_value = self.info_dict[info_str]
        parameter_value_dict = {}
        for index,parameter in enumerate(self.parameter_list):
            figure_title = f"Dependence of {parameter.name}({parameter.description}) on {info_str}"
            parameter_value_dict[figure_title] = self.popt[index]
            print(f'{figure_title}\n{parameter.name}:{self.popt[index]}')
        return x_value,parameter_value_dict



