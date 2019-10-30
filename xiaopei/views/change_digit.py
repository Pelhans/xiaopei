# encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
from collections import Counter
from search_digit import dict_data
import change_form

# 获得组合数字和单独数字
def get_combination_alone(sentence):
    d = dict_data(sentence)
    a = sorted(d.keys())
    combination = []
    alone = []
    if len(a) == 0:
        combin = []
    elif len(a) == 1:
        alone.append(a[0])
        combin = []
    else:
        for i in range(len(a)-1):
            if a[i] + 4 == a[i+1]:
                combination.append(a[i])
            elif a[i] - 4 == a[i-1]:
                combination.append(a[i])
            else:
                alone.append(a[i])
        if a[-1] - 4 == a[-2]:
            combination.append(a[-1])
        else:
            alone.append(a[-1])
        combin = []
        # print combination
        for i in range(len(combination) - 1):
            x, y = combination[i], combination[i+1]
            if x + 4 == y:
                combin.append([x, y])
    # print combin
    return combin, alone

# 单独数字转换:只能转换遇到的第一个
def alone_data_tra(sentence):
    d = dict_data(sentence)
    if d == {}:
        return sentence
    else:
        combin, alone = get_combination_alone(sentence)
        for i in alone:
            if sentence[i+1:i+4] in ['十', '百', '千']:
                # padding = 4 - len(str(d.get(i)))
                # print sentence[i:i+4]
                sentence = sentence.replace(sentence[i:i+4], str(d.get(i)), 1)
                return sentence
            elif sentence[i-3:i] == '十':
                sentence = sentence.replace(sentence[i-3:i+1], str(d.get(i) + 10), 1)
                return sentence
            else:
                continue

        return sentence

# s = '石头丢东西吧那个有3百万。我我知道你不容，这就是个3千3百4十万元1个人。'
# s = alone_data_tra(s)
# print s


# 停止词：万和点
def stopwords1(sentence, z):
    for i in range(len(z)-1):
        x, y = z[i], z[i+1]
        if sentence[x+1:y] not in ['十', '百', '千']:
            del z[i+1:]
            return z
        else:
            continue
    return z
def stopwords2(sentence, z):
    for i in range(len(z)-1):
        x, y = z[i], z[i+1]
        if sentence[x+1:y] == '万' and i < 2:
            del z[:i+1]
            return z
        elif sentence[x+1:y] == '万' and i >= 2:
            del z[i+1:]
            return z
        else:
            continue
    return z

# 获得组合数字列表
def get_combin(combin):
    if len(combin) == 0:
        return combin
    else:
        z = []
        for i in range(len(combin)-1):
            x, y = combin[i], combin[i+1]
            if x[1] == y[0]:
                z = z + x + y
        z = list(set(z))
        z = sorted(z)
        return z
# 组合数字转换
def combination_data_tra(sentence):
    d = dict_data(sentence)
    if d == {}:
        return sentence
    else:
        combin, alone = get_combination_alone(sentence)
        z = get_combin(combin)
        # print z
        if len(z) == 0:
            return sentence
        else:
            z = stopwords1(sentence, z)
            # print z
            z = stopwords2(sentence, z)
            # print z
            g = []
            for i in range(len(z)-1):
                x, y = z[i], z[i+1]
                if x + 4 != y:
                    g.append(z[i])
            for i in g:
                z.remove(i)
            g = []
            for i in z:
                g.append(d.get(i))
            start = sorted(z)[0]
            end = sorted(z)[-1]
            if d.get(start) < 10:
                return sentence
            elif d[end] < 10:
                sentence = sentence.replace(sentence[start:end + 1], str(sum(g)))
                return sentence
            else:
                sentence = sentence.replace(sentence[start:end + 4], str(sum(g)))

                return sentence

# print combination_data_tra('325万2千2百3十5点2')
def combination_data(sentence):
    d = dict_data(sentence)
    if d == {}:
        return sentence
    else:
        combin, alone = get_combination_alone(sentence)

        for i in combin:
            # 7十8
            if sentence[i[0]+1:i[1]] == '十':
                sentence = sentence.replace(sentence[i[0]:i[1]+1], str(d.get(i[0]) + d.get(i[1])))
            elif sentence[i[0]+1:i[1]] == '百' and sentence[i[1]+1:i[1]+4] == '十':
                sentence = sentence.replace(sentence[i[0]:i[1]+4], str(d.get(i[0]) + d.get(i[1])))
            elif sentence[i[0]+1:i[1]] == '千' and sentence[i[1]+1:i[1]+4] == '百':
                sentence = sentence.replace(sentence[i[0]:i[1]+4], str(d.get(i[0]) + d.get(i[1])))
            else:
                continue
        return sentence
# print combination_data('325万2千2百3十5点2')


# f = open('./160.txt', 'r').readlines()
# for sentence in f:
#     sentence = change_form.to_number_case("".join(sentence.split()))
#     try:
#         sentence = alone_data_tra(sentence)
#         sentence = combination_data_tra(sentence)
#         sentence = combination_data(sentence)
#         print sentence
#     except:
#         print sentence