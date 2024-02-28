from physical_model.quantity import Equation,Quantity,QUANTITY_TYPE
from typing import List
import copy
from scipy.optimize import curve_fit
from decimal import Decimal
import numpy as np
from ui.parameter_info import ParameterInfoDict


class DielectricRelaxationSimulator:
    def __init__(self,equation:Equation,independent_var:Quantity,dependent_var:Quantity,constant_list:List[Quantity],parameter_list:List[Quantity]):
        self.equation = equation
        self.independent_var = independent_var
        self.dependent_var = dependent_var
        self.constant_list = constant_list
        self.parameter_list = parameter_list

    def fit(self,x_list,raw_y_list):
        # 构造参数list[p0]和tuple([min,...],[max,...])
        input_name_list = ["f"]
        input_quantity_list = [self.independent_var] + self.constant_list + self.parameter_list
        p0_list = []
        min_list = []
        max_list = []

        for parameter in self.parameter_list:
            name_str, p0_val, min_val, max_val=parameter.get_p0_min_max()
            input_name_list.append(name_str)
            p0_list.append(float(p0_val))
            min_list.append(float(min_val))
            max_list.append(float(max_val))

        bounds_tuple = (min_list,max_list)
        # 需要给equation传进去一个constant的列表
        self.equation.set_input_info(input_name_list, input_quantity_list)
        # 然后传参给calculation
        popt, pcov = curve_fit(f=self.equation.fit, xdata=x_list,ydata=raw_y_list,p0=p0_list,bounds=bounds_tuple)
        # print(popt,pcov)
        fitted_parameter_list = copy.deepcopy(self.parameter_list)
        for index,fitted_parameter in enumerate(fitted_parameter_list):
            fitted_parameter.update_value(value = popt[index])
        self.equation.update_parameters(other_parameter_list=fitted_parameter_list)
        cal_y_quantity = self.equation.calculation()
        cal_y_list = cal_y_quantity.value
        cal_y_list = np.array([float(value) for value in cal_y_list])
        # print(raw_y_list)
        # print(cal_y_list)
        # print(cal_y_list-raw_y_list)
        # 因为这是最后一步计算的结果了，从这里开始Decimal类型会被转换成float输出，方便后面的绘图等工作
        return cal_y_list,popt,pcov

    def simulate(self,x_list:List[Decimal]):
        input_name_list = [self.independent_var.name]
        self.independent_var.update_value(x_list)
        input_quantity_list = [self.independent_var]
        for constant in self.constant_list:
            name_str, p0_val, min_val, max_val=constant.get_p0_min_max()
            input_name_list.append(name_str)
            input_quantity_list.append(constant)
        self.equation.set_input_info(input_name_list,input_quantity_list)
        y_list = self.equation.simulate()
        return y_list

if __name__=="__main__":
    x_list = [20.0, 21.623, 23.378, 25.276, 27.327, 29.545, 31.943, 34.535, 37.338, 40.369, 43.645, 47.188, 51.017, 55.158, 59.635, 64.475, 69.708, 75.366, 81.482, 88.096, 95.246, 102.976, 111.334, 120.37, 130.139, 140.702, 152.121, 164.468, 177.816, 192.248, 207.851, 224.721, 242.96, 262.679, 283.998, 307.048, 331.969, 358.912, 388.042, 419.536, 453.587, 490.401, 530.202, 573.235, 619.76, 670.061, 724.444, 783.241, 846.811, 915.539, 989.846, 1070.18, 1157.04, 1250.95, 1352.48, 1462.25, 1580.93, 1709.24, 1847.96, 1997.95, 2160.11, 2335.43, 2524.97, 2729.91, 2951.47, 3191.02, 3450.01, 3730.02, 4032.75, 4360.06, 4713.93, 5096.52, 5510.16, 5957.38, 6440.89, 6963.65, 7528.83, 8139.88, 8800.53, 9514.8, 10287.0, 11122.0, 12024.6, 13000.6, 14055.7, 15196.5, 16429.9, 17763.4, 19205.1, 20763.8, 22449.1, 24271.1, 26241.0, 28370.7, 30673.3, 33162.8, 35854.4, 38764.4, 41910.6, 45312.2, 48989.8, 52965.9, 57264.7, 61912.4, 66937.4, 72370.1, 78243.8, 84594.3, 91460.1, 98883.2, 106909.0, 115586.0, 124967.0, 135109.0, 146075.0, 157931.0, 170749.0, 184607.0, 199590.0, 215789.0, 233303.0, 252239.0, 272711.0, 294844.0, 318775.0, 344647.0, 372619.0, 402862.0, 435559.0, 470910.0, 509130.0, 550452.0, 595127.0, 643429.0, 695651.0, 752111.0, 813154.0, 879151.0, 950505.0, 1027650.0, 1111060.0, 1201230.0, 1298730.0, 1404130.0, 1518090.0, 1641310.0, 1774520.0, 1918540.0, 2074250.0, 2242600.0, 2424620.0, 2621410.0, 2834160.0, 3064190.0, 3312890.0, 3581770.0, 3872470.0, 4186770.0, 4526570.0, 4893960.0, 5291160.0, 5720600.0, 6184900.0, 6686880.0, 7229600.0, 7816360.0, 8450760.0, 9136640.0, 9878180.0, 10679900.0, 11546700.0, 12483900.0, 13497100.0, 14592500.0, 15776900.0, 17057400.0, 18441800.0, 19938600.0, 21556800.0, 23306400.0, 25198000.0, 27243100.0, 29454200.0, 31844800.0, 34429400.0, 37223700.0, 40244900.0, 43511200.0, 47042700.0, 50860800.0, 54988700.0, 59451700.0, 64276900.0, 69493800.0, 75134000.0, 81232100.0, 87825000.0, 94953100.0, 102660000.0, 110992000.0, 120000000.0]
    y_list = [1560.7206315624949,1381.231735190308,1267.4078421132635,1166.8548126679307,1040.3934804282594,961.6501248596566,876.9513372728918,829.9288855090541,770.1510037501131,719.3466353032092,651.3156053147198,569.8292733932263,574.1210346734679,574.9264773562162,575.3996826948854,537.0327899997795,530.4122622890785,530.9829653156365,506.36014159091167,495.48697587600117,492.85081227672094,500.3357780864085,514.5064770668497,479.10177527128826,508.26538303321837,482.42228569893274,443.6070278404157,479.5228162419153,450.70386591169324,426.9895715970383,445.347082117255,431.19004523320575,435.8258429407737,440.8410743254113,430.91183527031353,433.39647380051844,429.7275799148772,429.287287808425,430.45415504118057,425.3606771044796,427.59070383828765,427.2770966256524,426.9249871413669,429.1779910372888,427.4106125676654,428.3489501880452,428.1489867772164,427.90120602901555,427.4180646202429,426.15928873903187,423.7404766732613,423.913115891306,423.13189237943453,423.85101545316047,422.76239477246827,422.3016095214281,421.8370982440991,422.03892466807224,421.0937559994964,420.7702127167579,420.5298840211345,420.0697197744757,418.79790280125405,418.3625787298535,418.2576289893875,417.807400812832,417.2441498388515,416.94234170946396,416.0810086323847,415.74566626639853,415.2879860372656,414.64214148055146,414.2819589393071,413.66281757099557,412.9325164184035,412.47359418050763,411.9631285789509,411.1924621415642,410.3199509856187,409.8852479185996,408.6891934799156,407.811093284537,406.90691090513724,406.0654499682646,405.2333040971137,404.0981080878125,403.1436243535148,401.66252890374255,400.68817302923827,399.42815513926433,397.8688131374287,396.3399003502844,394.7401930636541,393.06534424686765,391.03465991950696,388.93007607075305,386.7267525253477,384.10735604436684,381.445731265447,378.59966818523486,375.44558693182057,372.0399989039166,368.40960728992565,364.4923116517021,360.24339967378114,355.6051179486873,350.65509202410266,345.42499312348144,339.6192231612506,333.4625857234972,326.94762875764377,320.01846186935927,312.6620439666332,304.89514216776473,296.7568797487857,288.25036173160333,279.4308575061672,270.29153602428136,260.96653423234017,251.5875050592123,242.09855811056678,232.59532806114774,223.123769235183,213.7969044300974,204.4967428134145,195.60892810601823,187.00180737904003,178.7803303729459,170.87804961892007,163.37631669093332,156.24283936114983,149.49811077415777,143.1750441621742,137.2196121440125,131.6442348073018,126.43649206441296,121.57899579266522,117.03013869850106,112.79550982135356,108.83971191147974,105.14038881114718,101.67953139329367,98.43726751771264,95.3763369215167,92.49860261785027,89.81151665929076,87.27222974351774,84.88198387929415,82.62339094393917,80.47161076219463,78.43161136911212,76.49221468582547,74.63603258965391,72.87113813755636,71.20063635144011,69.58229893336613,68.0322719972523,66.54807152557281,65.14460162348256,63.78584403685714,62.52210012059447,61.257052095130746,60.0405045118587,58.87133956289176,57.73949697725031,56.648205977717936,55.58616428455212,54.56405317311392,53.569576756650505,52.608758777662004,51.68439375586495,50.77710635455794,49.89478332938546,49.03146303828552,48.203788398681155,47.40393475536601,46.63103270220604,45.84123932987048,45.10038110279364,44.367223330046855,43.664370571115114,42.95332055434815,42.24699017088026,41.56307804558292,40.878917518532994,40.14420723483257,39.42185493832312,38.70124145408174,37.93610195568997,37.14959990657613,36.32888051604406,35.55846248040993,34.79363348420888,33.988004500146204,33.12306959765448,32.16107171034121,31.00538255645186,29.865342712975192,28.982584984735684,27.955816340436566,26.317668882594155]
    equation = Equation.construction_root_equation()
    alpha = Quantity("alpha", Decimal('0.6'))
    beta = Quantity("beta", Decimal('0.9'))
    freq = Quantity("f", Decimal('1.0e6'))
    epsilon_inf = Quantity("epsilon_inf", Decimal('5.0'))
    delta_epsilon = Quantity("delta_epsilon", Decimal('1.0e2'))
    tau_m = Quantity("tau_m", Decimal('5.0e-5'))
    epsilon_prime = Quantity("epsilon_prime", Decimal('1.0e2'))
    independent_var = freq
    dependent_var = epsilon_prime
    constant_list = [epsilon_inf,alpha,beta]
    parameter_list = [tau_m,delta_epsilon]
    my_simulator = DielectricRelaxationSimulator(equation=equation,
                                                 independent_var=independent_var,dependent_var=dependent_var,
                                                 constant_list=constant_list,parameter_list=parameter_list)
    my_simulator.fit(x_list=x_list,raw_y_list=y_list)




