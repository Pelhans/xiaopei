# encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import change_form
import change_date
import change_digit


def change(sentence):
    pattern = '年(.*)月'
    pattern1 = '月(.*)日'

    sentence = change_form.to_number_case("".join(sentence.split()))
    sentence = change_date.trans_date(sentence, pattern)
    sentence = change_date.trans_date(sentence, pattern1)
    # print sentence
    sentence = change_digit.alone_data_tra(sentence)
    # print sentence
    for i in range(2):
        sentence = change_digit.combination_data_tra(sentence)
    # print sentence
    sentence = change_digit.combination_data(sentence)

    combin, alone = change_digit.get_combination_alone(sentence)
    z = change_digit.get_combin(combin)
    if len(z) == 0:
        pass
    else:
        for i in range(len(z)-1):
            x, y = z[i], z[i+1]
            if sentence[x+1:y] == '点':
                sentence = sentence.replace(sentence[x+1:y], '.')
    return sentence

# f = open('./160.txt', 'r').readlines()
# for s in f:
#     print change(s)

# s = '石头丢东西吧那个有３百万。这就是７十８个人，我会跟这个十多有提起了１个。'
# print change(s)