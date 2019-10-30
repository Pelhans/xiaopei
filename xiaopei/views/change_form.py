# encoding:utf-8
import re
# 替换数字格式
def to_number_case(sentence):
    origin_number = ["０", "１", "２", "３", "４", "５", "６", "７", "８"]
    to_number = "012345678"
    d = dict(zip(origin_number, to_number))
    rep = dict((re.escape(k), v) for k, v in d.items())
    pattern = re.compile("|".join(rep.keys()))
    my_str = pattern.sub(lambda m: rep[re.escape(m.group(0))], sentence)
    return my_str