import re
from enum import Enum


class PARSE_TYPE(Enum):
    Oe = 1
    Co = 2
    DCB = 3
    OCS = 4
    # FIXME:也许需要引入新的类型


def file_name_parse(parse_type:PARSE_TYPE,file_name:str):
    if parse_type is PARSE_TYPE.Oe:
        if 'Oe' in file_name:
            # 对文件名称的处理逻辑：匹配‘-’和‘Oe’之间的内容，用空格切断成字符串数组，去除空字符串的元素：如果最后1个元素包含数字，那么信息都在最后一个元素里处理，否则，最后一个纯字符是倍数，倒数第二个是纯数字的数
            res_list = re.findall(r'.*[-_ ](.*)Oe.*',file_name)[0].split(' ')
            while '' in res_list:
                res_list.remove('')
            if re.match(r'\d',res_list[-1]):
                if 'k' in res_list[-1]:
                    h_value = float(res_list[-1].replace('k',''))*1000
                else:
                    h_value = float(res_list[-1].replace('k',''))
            elif res_list.__len__() > 1:
                if res_list[-1] == 'k':
                    h_value = float(res_list[-2])*1000
                else:
                    h_value = float(res_list[-2])
            else:
                h_value = 0.
        else:
            h_value = 0.
        return h_value
    elif parse_type is PARSE_TYPE.Co:
        if 'Co' in file_name:
            res_list = re.findall(r'.*[-_ ]Co(.*).*',file_name)[0].split(' ')
            while '' in res_list:
                res_list.remove('')
            print("result:{}".format(res_list))
            co_value = float(res_list[-1])
        else:
            co_value = 0.
        return co_value
    elif parse_type is PARSE_TYPE.DCB:
        if 'DCB' in file_name:
            res_list = re.findall(r'.*[-_ ]DCB(.*).*',file_name)[0].split(' ')
            while '' in res_list:
                res_list.remove('')
            print("result:{}".format(res_list))
            dcb_value = float(res_list[-1])
        else:
            dcb_value = 0.
        return dcb_value
    elif parse_type is PARSE_TYPE.OCS:
        if 'V' in file_name:
            res_list = re.findall(r'.*[-_ ](.*)V.*',file_name)[0].split(' ')
            while '' in res_list:
                res_list.remove('')
            if re.match(r'\d',res_list[-1]):
                if 'k' in res_list[-1]:
                    ocs_value = float(res_list[-1].replace('k',''))*1000
                elif 'm' in res_list[-1]:
                    ocs_value = float(res_list[-1].replace('m',''))/1000
                else:
                    ocs_value = float(res_list[-1].replace('k',''))
            elif res_list.__len__() > 1:
                if res_list[-1] == 'k':
                    ocs_value = float(res_list[-2])*1000
                else:
                    ocs_value = float(res_list[-2])
            else:
                ocs_value = 0.
        else:
            ocs_value = 0.
        return ocs_value
    else:
        print("file_name_parser,parse(),Unknown parse type.")
        return None