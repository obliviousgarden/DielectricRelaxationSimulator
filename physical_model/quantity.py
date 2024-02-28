import inspect
import types
from enum import Enum
from decimal import Decimal
from typing import List, Tuple

import numpy as np

from physical_model.decimal_complex import DecimalComplex
from scipy import constants
from ui.parameter_info import ParameterInfoDict, ParameterInfo


class QUANTITY_TYPE(Enum):
    CONSTANT = 0
    PARAMETER = 1
    INDEPENDENT_VARIABLE = 2
    DEPENDENT_VARIABLE = 3


class Quantity:
    def __init__(self, name: str, value=None, child_quantity=[]):
        # 非常注意！！！value可能是一个Decimal也可能是一个List[Decimal]
        self.description = ParameterInfoDict.parameter_info_dict[name].description
        self.name = ParameterInfoDict.parameter_info_dict[name].name
        self.symbol = ParameterInfoDict.parameter_info_dict[name].symbol
        self.min = ParameterInfoDict.parameter_info_dict[name].min
        self.max = ParameterInfoDict.parameter_info_dict[name].max
        if value is None:
            self.value = ParameterInfoDict.parameter_info_dict[name].default_value
        else:
            self.value = value
        self.unit = ParameterInfoDict.parameter_info_dict[name].unit
        self.convert_factor = ParameterInfoDict.parameter_info_dict[name].convert_factor
        self.is_log = ParameterInfoDict.parameter_info_dict[name].is_log
        self.child_quantity = child_quantity  # 这里是一个用来装载子节点的东西
        self.fix_flag = ParameterInfoDict.parameter_info_dict[name].fix_flag
        self.enable_flag = False
        print(f"New quantity created:{self.name},{self.child_quantity}")

    def is_leaf(self):
        if self.child_quantity.__len__() == 0:
            return True
        else:
            return False

    def update_value(self, value):
        if isinstance(value, Decimal):
            self.value = value
        elif isinstance(value, (np.ndarray, list)):
            self.value = np.array([Decimal(str(float_value)) for float_value in value])
        else:
            self.value = Decimal(str(value))

    def devide_value_by_convert_factor(self):
        self.value = self.value / self.convert_factor

    def update_fix_flag(self, fix_flag: bool):
        self.fix_flag = fix_flag

    def update_child_quantity(self, child_quantity_list):
        self.child_quantity = child_quantity_list

    def get_value_times_factor(self):
        return self.value * self.convert_factor

    def update_enable_flag(self, enable_flag: bool):
        self.enable_flag = enable_flag

    def get_scan_str(self):
        if self.enable_flag:
            if self.fix_flag:
                return f"{self.symbol}({self.description})[{self.unit}] = {self.value}"
            else:
                return f"{self.symbol}({self.description})[{self.unit}] = {self.value}, {self.min} ~ {self.max}"
        else:
            return f"{self.symbol}({self.description})[{self.unit}]"

    def get_p0_min_max(self):
        return self.name, self.value, self.min, self.max

    def __repr__(self):
        return self.symbol

    def get_symbol_value(self)->str:
        return self.symbol + "[" + self.unit + "] :" + str(self.value)
    def get_header_str(self)->str:
        return f"{self.symbol}[{self.unit}]"


class EQUATION_TYPE(Enum):
    CUSTOM = 0
    REAL_PERMITTIVITY = 1
    RELAXATION_TIME_M = 2
    RELAXATION_TIME_0 = 3
    DECAY_RATE_OF_WAVE_FUNCTION = 4
    POTENTIAL_HEIGHT = 5
    SPACING = 6
    CHARGING_ENERGY_12 = 7
    CHARGING_ENERGY_C1 = 8
    CHARGING_ENERGY_C2 = 9
    DIAMETER_1 = 10
    DIAMETER_2 = 11
    DIELECTRIC_STRENGTH = 12
    NUMBER_DENSITY = 13
    VOLUME = 14
    CENTER_DISTANCE = 15


equation_type_dict = {
    "epsilon_prime": EQUATION_TYPE.REAL_PERMITTIVITY,
    "tau_m": EQUATION_TYPE.RELAXATION_TIME_M,
    "tau_0": EQUATION_TYPE.RELAXATION_TIME_0,
    "kappa": EQUATION_TYPE.DECAY_RATE_OF_WAVE_FUNCTION,
    "U": EQUATION_TYPE.POTENTIAL_HEIGHT,
    "s": EQUATION_TYPE.SPACING,
    "E_12": EQUATION_TYPE.CHARGING_ENERGY_12,
    "E_c1": EQUATION_TYPE.CHARGING_ENERGY_C1,
    "E_c2": EQUATION_TYPE.CHARGING_ENERGY_C2,
    "d_1": EQUATION_TYPE.DIAMETER_1,
    "d_2": EQUATION_TYPE.DIAMETER_2,
    "delta_epsilon": EQUATION_TYPE.DIELECTRIC_STRENGTH,
    "n_p": EQUATION_TYPE.NUMBER_DENSITY,
    "V": EQUATION_TYPE.VOLUME,
    "d_12": EQUATION_TYPE.CENTER_DISTANCE
}


class Equation:
    parameters_dict = {
        "CUSTOM": ('', []),
        "REAL_PERMITTIVITY": ("epsilon_prime", ["f", "epsilon_inf", "alpha", "beta", "tau_m", "delta_epsilon"]),
        "RELAXATION_TIME_M": ("tau_m", ["P_s", "m", "tau_0"]),
        "RELAXATION_TIME_0": ("tau_0", ["gamma_0", "kappa", "s", "E_12", "T"]),
        "DECAY_RATE_OF_WAVE_FUNCTION": ("kappa", ["U"]),
        "POTENTIAL_HEIGHT": ("U", ["U_0", "ye_IM"]),
        "SPACING": ("s", ["s_0", "ye_IM"]),
        "CHARGING_ENERGY_12": ("E_12", ["E_c1", "E_c2"]),
        "CHARGING_ENERGY_C1": ("E_c1", ["d_1","epsilon_r"]),
        "CHARGING_ENERGY_C2": ("E_c2", ["d_2","epsilon_r"]),
        "DIAMETER_1": ("d_1", ["d_1_0", "ye_NG"]),
        "DIAMETER_2": ("d_2", ["d_2_0", "ye_NG"]),
        "DIELECTRIC_STRENGTH": ("delta_epsilon", ["n_p", "d_12", "T", "E_c1", "E_c2"]),
        "NUMBER_DENSITY": ("n_p", ["N", "V"]),
        "VOLUME": ("V", ["V_0", "ye_ALL"]),
        "CENTER_DISTANCE": ("d_12", ["d_1", "d_2", "s"])
    }
    calculation_dict = {
        "CUSTOM": None,
        "REAL_PERMITTIVITY": "real_permittivity_calculation",
        "RELAXATION_TIME_M": "relaxation_time_m_calculation",
        "RELAXATION_TIME_0": "relaxation_time_0_calculation",
        "DECAY_RATE_OF_WAVE_FUNCTION": "decay_rate_of_wave_function_calculation",
        "POTENTIAL_HEIGHT": "potential_height_calculation",
        "SPACING": "spacing_calculation",
        "CHARGING_ENERGY_12": "charging_energy_12_calculation",
        "CHARGING_ENERGY_C1": "charging_energy_c1_calculation",
        "CHARGING_ENERGY_C2": "charging_energy_c2_calculation",
        "DIAMETER_1": "diameter_1_calculation",
        "DIAMETER_2": "diameter_2_calculation",
        "DIELECTRIC_STRENGTH": "dielectric_strength_calculation",
        "NUMBER_DENSITY": "number_density_calculation",
        "VOLUME": "volume_calculation",
        "CENTER_DISTANCE": "center_distance_calculation"
    }
    parameter_info_dict = ParameterInfoDict.parameter_info_dict

    def __init__(self, equation_type: EQUATION_TYPE, parameters=None, custom_method=None):
        # print("__init__",Equation.parameter_info_dict['f'].default_value)
        if parameters is None:
            parameters = {}
        self.equation_type = equation_type
        self.equation_left, self.equation_right = Equation.parameters_dict[equation_type.name]
        # 注意这里的parameter构造的时候会出现3种情况，通过root生成出来的公式，通过递归计算需要的公式，和前端生成节点需要的公式
        self.parameters = parameters
        if parameters.__len__() == 0:
            for quantity_name in self.equation_right:
                self.parameters[quantity_name] = Quantity(quantity_name)

        if custom_method is not None:
            self.custom_method = types.MethodType(custom_method, self)
        self.input_name_list = []  # 存放fit方法的p0参数对应index的参数名称

    def check_parameters(self):
        parameter_name_list = Equation.parameters_dict[self.equation_type.name]
        if self.parameters.__len__() == parameter_name_list.__len__():
            for parameter in self.parameters:
                if parameter.name not in parameter_name_list:
                    return False
            return True
        else:
            return False

    def set_input_info(self, input_name_list: List[str], input_quantity_list: List[Quantity]):
        # 遍历初始化parameters
        self.input_name_list = input_name_list
        self.parameters = {}  # 因为考虑到会有参数需要计算，所以要清空，key没有的时候则代表的需要计算
        for input_quantity in input_quantity_list:
            self.parameters[input_quantity.name] = input_quantity

    def update_parameters(self, other_parameter_list: List[Quantity]):
        for other_parameter in other_parameter_list:
            self.parameters[other_parameter.name] = other_parameter

    def fit(self, *args):
        # print("Fit start!")
        # print(args)
        # fit的情况下,一定有一个参数是一个list作为x变量，从而输出y变量
        for index, p0 in enumerate(args):
            if isinstance(p0, float):
                # float
                self.parameters[self.input_name_list[index]].update_value(Decimal(str(p0)))
            elif isinstance(p0, np.ndarray):
                # list
                value = np.array([Decimal(str(float_value)) for float_value in p0])
                self.parameters[self.input_name_list[index]].update_value(value)
            else:
                print("TypeError")
        # print("Fit end!")
        rst_array = self.calculation().value
        result = [float(decimal_element) for decimal_element in rst_array.tolist()]
        return result

    def simulate(self):
        print("Simulate start!")
        # simulate 的情况下parameters里面包含了自变量的一个quantity和其他的常数quantity
        rst_array = self.calculation().value
        result = [float(decimal_element) for decimal_element in rst_array.tolist()]
        return result


    def calculation(self):
        print("Calculation start!")
        # print(f'{self.equation_type}:self.parameters:{self.parameters}')
        # param_name_list是全部的参数，实际parameters并不是全部参数，不足的参数需要用其他参数来间接计算
        method_name = Equation.calculation_dict[self.equation_type.name]
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                # 重要：这里的目的是需要按顺序组装好参数的list然后传给需要的方法
                need_parameter_name_list = self.get_need_parameter_name_list()
                parameter_list = []  # List[Quantity]
                print(
                    f'Method name: {method_name}\nneed_parameter_name_list: {need_parameter_name_list}\nself.parameters:{self.parameters}')
                for need_parameter_name in need_parameter_name_list:
                    if need_parameter_name in self.parameters.keys():
                        parameter = self.parameters[need_parameter_name]
                        parameter_list.append(parameter)
                    else:
                        if need_parameter_name in equation_type_dict.keys():
                            need_equation_type = equation_type_dict[need_parameter_name]
                            need_equation = Equation(need_equation_type, parameters=self.parameters)
                            parameter = need_equation.calculation()
                            parameter_list.append(parameter)
                        else:
                            # 这里需要考虑的是，怎么组装parameter_list
                            # print(f'{need_parameter_name} NOT IN {equation_type_dict.keys()}')
                            default_parameter = Quantity(need_parameter_name)
                            parameter_list.append(default_parameter)

                # 非常重要！返回前必须记得转换单位
                # return method(parameter_list)
                rst = method(parameter_list)
                rst.devide_value_by_convert_factor()
                print("Calculation end!")
                return rst
        else:
            print(f"Method '{method_name}' not found.")

    def get_need_parameter_name_list(self) -> List[str]:
        return Equation.parameters_dict[self.equation_type.name][1]

    @staticmethod
    def get_equation_type_by_dependent_var(dependent_parameter_name: str) -> EQUATION_TYPE:
        for type_name, parameter_info in Equation.parameters_dict.items():
            if parameter_info[0] == dependent_parameter_name:
                return EQUATION_TYPE.__getitem__(type_name)

    @staticmethod
    def get_parameter_name_list_of_this_method() -> List[str]:
        method_name = inspect.currentframe().f_back.f_code.co_name
        equation_type = ""
        for key, val in Equation.calculation_dict.items():
            if val == method_name:
                equation_type = key
                break
        return Equation.parameters_dict[equation_type][1]

    @staticmethod
    def construction_root_equation():
        real_permittivity_equation = Equation(EQUATION_TYPE.REAL_PERMITTIVITY, parameters={})
        return real_permittivity_equation

    @staticmethod
    def construction_equation(dependent_quantity: Quantity):
        equation_type = equation_type_dict[dependent_quantity.name]
        equation = Equation(equation_type,parameters={})
        return equation

    # ---------------------下面开始是默认的函数--------------------
    @classmethod
    def real_permittivity_calculation(cls, parameter_list) -> Quantity:
        freq, epsilon_inf, alpha, beta, tau_m, delta_epsilon = [param.value * param.convert_factor for param in
                                                                parameter_list]
        # param_name_list = cls.get_parameter_name_list_of_this_method()
        # freq, epsilon_inf, alpha, beta, tau_m, delta_epsilon = [parameters.get(key).get_value_times_factor() for key in param_name_list]
        # term_1 = DecimalComplex(0,freq*tau_m)
        # term_2 = term_1**alpha
        # term_3 = (DecimalComplex(1)+term_2)**beta
        # term_4 = DecimalComplex(delta_epsilon)/term_3
        # term_5 = DecimalComplex(epsilon_inf)+term_4
        value = DecimalComplex(epsilon_inf) + DecimalComplex(delta_epsilon) / (
                DecimalComplex(1) + DecimalComplex(0, freq * tau_m) ** alpha) ** beta
        value_real = Quantity("epsilon_prime", value.real, child_quantity=parameter_list)
        # value_imag = Quantity("epsilon_prime_prime", value.imag, child_quantity=parameters)
        # print(f'Calculation:real_permittivity_calculation\nParameter:{[parameter.get_symbol_value() for parameter in parameter_list]}\nResult:{value_real.value}')
        return value_real

    @classmethod
    def relaxation_time_m_calculation(cls, parameter_list) -> Quantity:
        P, m, tau_0 = [param.value * param.convert_factor for param in parameter_list]
        value = tau_0 / (1 + (P * m) ** 2)
        # convert_factor = Quantity("tau_m").convert_factor
        # value = value / convert_factor # s 转 μs
        # 在得到结果的时候一定记得转换单位！！！
        # print(f'Calculation:relaxation_time_m_calculation\nParameter:{[parameter.get_symbol_value() for parameter in parameter_list]}\nResult:{value}')
        return Quantity("tau_m", value, child_quantity=parameter_list)

    @classmethod
    def relaxation_time_0_calculation(cls, parameter_list) -> Quantity:
        gamma_0, kappa, s, E_12, T = [param.value * param.convert_factor for param in parameter_list]
        term_1 = Decimal('2') * kappa * s + E_12 / (Decimal(constants.k) * T)
        term_2 = Decimal('2') * gamma_0
        if type(term_1) is np.ndarray:
            value = np.exp(term_1) / term_2
        else:
            value = Decimal.exp(term_1) / term_2
        return Quantity("tau_0", value, child_quantity=parameter_list)

    @classmethod
    def decay_rate_of_wave_function_calculation(cls, parameter_list) -> Quantity:
        U = [param.value * param.convert_factor for param in parameter_list]
        if type(U[0]) is np.ndarray:
            value = np.sqrt(Decimal('2') * Decimal(constants.m_e) * U[0] / Decimal(constants.hbar) ** 2)
        else:
            value = Decimal.sqrt(Decimal('2') * Decimal(constants.m_e) * U[0] / Decimal(constants.hbar) ** 2)
        return Quantity("kappa", value, child_quantity=parameter_list)

    @classmethod
    def potential_height_calculation(cls, parameter_list) -> Quantity:
        U_0, ye_IM = [param.value * param.convert_factor for param in parameter_list]
        value = U_0 * (Decimal('1') + ye_IM)
        return Quantity("U", value, child_quantity=parameter_list)

    @classmethod
    def spacing_calculation(cls, parameter_list) -> Quantity:
        s_0, ye_IM = [param.value * param.convert_factor for param in parameter_list]
        value = s_0 * (Decimal('1') + ye_IM)
        return Quantity("s", value, child_quantity=parameter_list)

    @classmethod
    def charging_energy_12_calculation(cls, parameter_list) -> Quantity:
        E_c1, E_c2 = [param.value * param.convert_factor for param in parameter_list]
        value = (abs(E_c1 - E_c2) + E_c1 + E_c2) / Decimal('2')
        return Quantity("E_12", value, child_quantity=parameter_list)

    @classmethod
    def charging_energy_c1_calculation(cls, parameter_list) -> Quantity:
        # SI公式
        d_1, epsilon_r = [param.value * param.convert_factor for param in parameter_list]
        # value = Decimal(str(constants.e ** 2 / constants.epsilon_0)) / d_1[0] # 这个式CGS公式
        value = Decimal(str(constants.e ** 2 / (4 * constants.pi * constants.epsilon_0))) / (epsilon_r * d_1) # 这个式SI公式
        return Quantity("E_c1", value, child_quantity=parameter_list)

    @classmethod
    def charging_energy_c2_calculation(cls, parameter_list) -> Quantity:
        # SI公式
        d_2, epsilon_r = [param.value * param.convert_factor for param in parameter_list]
        # value = Decimal(str(constants.e ** 2 / constants.epsilon_0)) / d_2[0]
        value = Decimal(str(constants.e ** 2 / (4 * constants.pi * constants.epsilon_0))) / (epsilon_r * d_2)
        return Quantity("E_c2", value, child_quantity=parameter_list)

    @classmethod
    def diameter_1_calculation(cls, parameter_list) -> Quantity:
        d_1_0, ye_NG = [param.value * param.convert_factor for param in parameter_list]
        value = d_1_0 * (Decimal('1') + ye_NG)
        return Quantity("d_1", value, child_quantity=parameter_list)

    @classmethod
    def diameter_2_calculation(cls, parameter_list) -> Quantity:
        d_2_0, ye_NG = [param.value * param.convert_factor for param in parameter_list]
        value = d_2_0 * (Decimal('1') + ye_NG)
        return Quantity("d_2", value, child_quantity=parameter_list)

    @classmethod
    def dielectric_strength_calculation(cls, parameter_list) -> Quantity:
        n_p, d_12, T, E_c1, E_c2 = [param.value * param.convert_factor for param in parameter_list]
        term_1 = 2 * Decimal(constants.pi) * (Decimal(constants.e) * d_12) ** 2 / (Decimal(constants.k) * T)
        term_2 = np.exp(-E_c1 / (Decimal(constants.k) * T))
        term_3 = np.exp(-E_c2 / (Decimal(constants.k) * T))
        value = n_p * term_1 * (term_2 + term_3)
        return Quantity("delta_epsilon", value, child_quantity=parameter_list)

    @classmethod
    def number_density_calculation(cls, parameter_list) -> Quantity:
        N, V = [param.value * param.convert_factor for param in parameter_list]
        value = N / V
        return Quantity("n_p", value, child_quantity=parameter_list)

    @classmethod
    def volume_calculation(cls, parameter_list) -> Quantity:
        V_0, ye_ALL = [param.value * param.convert_factor for param in parameter_list]
        value = V_0 * (Decimal('1') + ye_ALL)
        return Quantity("V", value, child_quantity=parameter_list)

    @classmethod
    def center_distance_calculation(cls, parameter_list) -> Quantity:
        d_1, d_2, s = [param.value * param.convert_factor for param in parameter_list]
        value = (d_1 + d_2) / Decimal('2') + s
        return Quantity("d_12", value, child_quantity=parameter_list)


if __name__ == "__main__":
    # # Test 1 - Spacing calculation for normal operation
    # spacing_0 = Quantity(QUANTITY_TYPE.PARAMETER,"s_0",(Decimal('0.0'), Decimal('1.0')), Decimal('0.5')) # nm
    # ye_im = Quantity(QUANTITY_TYPE.PARAMETER,"є_IM",(Decimal('0.0'), Decimal('1.0')), Decimal('0.03')) # 1
    # spacing_equation = Equation(EQUATION_TYPE.SPACING,[spacing_0,ye_im])
    # spacing = spacing_equation.calculation()

    # Test 2 - Complex Permittivity for complex operation
    alpha = Quantity("alpha", QUANTITY_TYPE.PARAMETER, (Decimal('0.0'), Decimal('1.0')), Decimal('0.6'))
    beta = Quantity("beta", QUANTITY_TYPE.PARAMETER, (Decimal('0.0'), Decimal('1.0')), Decimal('0.9'))
    freq = Quantity("frequency", QUANTITY_TYPE.INDEPENDENT_VARIABLE, (Decimal('1.0e3'), Decimal('1.0e8')),
                    Decimal('1.0e6'),
                    is_log=True)  # Hz
    epsilon_inf = Quantity("frequency", QUANTITY_TYPE.PARAMETER, (Decimal('1.0'), Decimal('50.0')),
                           Decimal('5.0'))
    delta_epsilon = Quantity("delta_epsilon", QUANTITY_TYPE.PARAMETER, (Decimal('1.0e1'), Decimal('1.0e3')),
                             Decimal('1.0e2'),
                             is_log=True)

    # tau_m = Quantity(QUANTITY_TYPE.PARAMETER, "τ_m", (Decimal('1.0e-6'), Decimal('1.0e-3')), Decimal('5.0e-5'), is_log=True) #s
    # Test 3 - Complicated formula
    P = Quantity("spin_polarization", QUANTITY_TYPE.PARAMETER, (Decimal('0.0'), Decimal('1.0')), Decimal('0.34'))
    m = Quantity("normalized_magnetization", QUANTITY_TYPE.PARAMETER, (Decimal('0.0'), Decimal('1.0')),
                 Decimal('0.85'))
    tau_0 = Quantity("tau_0", QUANTITY_TYPE.PARAMETER, (Decimal('1.0e-6'), Decimal('1.0e-3')), Decimal('5.0e-5'),
                     is_log=True)  # s
    dielectric_relaxation_time_M_equation = Equation(EQUATION_TYPE.DIELECTRIC_RELAXATION_TIME_M, [P, m, tau_0])
    tau_m = dielectric_relaxation_time_M_equation.calculation()

    complex_permittivity_equation = Equation(EQUATION_TYPE.COMPLEX_PERMITTIVITY,
                                             [freq, epsilon_inf, alpha, beta, tau_m, delta_epsilon])
    epsilon_star_real, epsilon_star_imag = complex_permittivity_equation.calculation()

    print('A')
    # epsilon_caret = Quantity(QUANTITY_TYPE.DEPENDENT_VARIABLE,"ε*",(Decimal('0.0'), Decimal('0.0')), Decimal('0.0'), enable_flag=True,fix_flag=False,)
