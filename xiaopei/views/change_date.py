# encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
from collections import Counter
import change_form
from search_digit import find_repeat

# 日期转换
def trans_date(sentence, pattern):
    date = re.search(pattern, sentence)
    if date is None:
        return sentence
    else:
        a = str(date.group())
        a_local = find_repeat(a, '十')
        if len(a_local) < 1:
            return sentence
        elif all([a[a_local[0] - 1].isdigit(), a[a_local[0] + 3].isdigit()]):
            date_index = int(a[a_local[0] - 1]) * 10 + int(a[a_local[0] + 3])
            a = a.replace(a[a_local[0] - 1:a_local[0] + 4], str(date_index))
        elif a[a_local[0] + 3].isdigit():
            date_index = 1 * 10 + int(a[a_local[0] + 3])
            a = a.replace(a[a_local[0]:a_local[0] + 4], str(date_index))
        elif a[a_local[0] - 1].isdigit():
            date_index = int(a[a_local[0] - 1]) * 10
            a = a.replace(a[a_local[0] - 1:a_local[0] + 3], str(date_index))
        else:
            date_index = 1 * 10
            a = a.replace(a[a_local[0]:a_local[0] + 3], str(date_index))
        date_info = re.compile(pattern)
        sentence = date_info.sub(a, sentence)
        return sentence

# pattern = '年(.*)月'
# pattern1 = '月(.*)日'
# f = open('./160.txt', 'r').readlines()
# for sentence in f:
#     sentence = change_form.to_number_case("".join(sentence.split()))
#     sentence = trans_date(sentence, pattern)
#     sentence = trans_date(sentence, pattern1)
#     print sentence

