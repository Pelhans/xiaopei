# encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
from collections import Counter
import change_form
# class transform_digit(object):
#     # 主要是
#     def __init__(self):
# 每一个数对应有的结果,num_l:num_location
def number(sentence, num_l):
    if sentence[num_l+1:num_l+4] == '千':
        return int(sentence[num_l]) * 1000
    elif sentence[num_l+1:num_l+4] == '百':
        return int(sentence[num_l]) * 100
    elif sentence[num_l+1:num_l+4] == '十':
        return int(sentence[num_l]) * 10
    # elif sentence[num_l+1:num_l+4] == '元':
    #     return int(sentence[num_l]) * 1
    # elif sentence[num_l+1:num_l+4] == '万':
    #     return int(sentence[num_l]) * 1
    else:
        return int(sentence[num_l]) * 1
# 重复的数字
def find_repeat(sentence, elmt):
    elmt_index = []
    s_index = 0
    e_index = len(sentence)
    while (s_index < e_index):
        try:
            temp = sentence.index(elmt, s_index, e_index)
            elmt_index.append(temp)
            s_index = temp + 1
        except ValueError:
            break
    return elmt_index

# 获得数字字典
def dict_data(sentence):
    # 找出所有的数字
    nums = re.findall('\d', sentence, flags=0)
    counter = Counter(nums)
    total_index = []
    total = []

    for k, v in counter.items():
        if v > 1:
            elmt_index = find_repeat(sentence, k)
            total_index += elmt_index
        else:
            num = sentence.index(k)
            total_index.append(num)
    total_i = sorted(total_index)
    for i in total_i:
        total.append(number(sentence, i))
    d = dict(zip(total_i, total))
    return d




# f = open('./160.txt', 'r').readlines()
# for sentence in f:
#     sentence = change_form.to_number_case("".join(sentence.split()))
#     sentence = dict_data(sentence)
#     print sentence