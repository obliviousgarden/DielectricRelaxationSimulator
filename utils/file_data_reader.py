import numpy as np
from scipy import constants


def open_file(path):
    try:
        with open(path, 'r', encoding="utf-8") as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(path, 'r', encoding="shift_jis") as file:
            lines = file.readlines()
    return lines


def file_data_read(file_path, first_pos_info_tuple,info_list):
    freq_list = []  # 存取读出来的频率 Hz
    cp_list = []  # 存取读出来的电容率 F
    ((f_start_row,f_start_col,f_start_unit),(cp_start_row,cp_start_col,cp_start_unit)) = first_pos_info_tuple
    [thickness, area, h, co, dcb, osc, cc] = info_list
    lines = open_file(file_path)
    if f_start_row != cp_start_row:
        print("WARNING: self.f_start_row != self.Cp_start_row.")
    for line_index in range(int(f_start_row)-1, lines.__len__()):
        data = lines[line_index].replace('\n','').replace('\t',',').split(',')
        freq_list.append(float(data[int(f_start_col)-1]))
        cp_list.append(float(data[int(cp_start_col)-1]))
    epsilon_list = np.multiply(np.divide(np.multiply(cp_list,thickness),constants.epsilon_0*area),cc)
    start_pos = 0
    # 这里是对噪声的处理
    if True:
        # 接下来用这种方法来切割掉曲线前端可能会出现的噪声，噪声的判断是数据二阶导数大于0的情况
        d2_epsilon_list = np.gradient(np.gradient(epsilon_list))
        start_pos = 0
        for i in range(d2_epsilon_list.size):
            if d2_epsilon_list[i] >= 1:
                start_pos = i
        print('横轴切割完毕开始点是{}'.format(start_pos))
    else:
        print('不去除噪声，横轴开始点是{}'.format(start_pos))
    return freq_list[start_pos:], epsilon_list[start_pos:]



