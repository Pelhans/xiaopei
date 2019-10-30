# -*- coding:utf-8 -*-
# Author: yuyongsheng
# Time: 18-9-17 下午5:57
# Description:

import numpy as np

energy = [] # 用于存储能量值
splited_list = []  # 用于存储有效语音片段和"return"换行标志

silence_mean_energy = 0  # 记录静音energy均值
# silence_mean_zero = 0  # 记录静音zero均值
E0_high_para = 6.7  # 设置较高的能量阈值参数，2018.10.9
E0_low_para = 4.3  # 设置较低的能量阈值参数，2018.10.9
E0_high = 0  # 较高的能量阈值
E0_low = 0  # 较低的能量阈值
E0_weight_para = 0.85  # 2018.10.22,设置动态阈值权值
# zero_low = 150  # 使用较低的过零率阈值，对应语音 2018.9.16

triggered_combined = False  # 2018.10.29, 是否触发短句合并，如果有效语音时长小于recognize_time,则触发，否则，不触发。

# estimate silence threshold value of energy and cross-zero
def silence_value_estimate(slice_start_frame, slice_end_frame):
    global E0_high, E0_low, E0_high_para, E0_low_para, E0_weight_para
    global energy
    silence_list = energy[slice_start_frame : slice_end_frame]  # 2018.8.13,存储静音数据列表，用于估计静音和静音更新
    sum_silence = 0
    for i in silence_list:
        sum_silence = sum_silence + i
    silence_mean_energy = sum_silence / len(silence_list)
    print "silence_mean_energy:" + str(silence_mean_energy)
    # 设置动态能量双门限阈值
    if E0_high == 0: # 较高的能量阈值
        E0_high = E0_high_para * silence_mean_energy
    else:
        E0_high = E0_weight_para * E0_high + (1 - E0_weight_para) * (E0_high_para * silence_mean_energy)

    if E0_low == 0:
        E0_low = E0_low_para * silence_mean_energy
    else:
        E0_low = E0_weight_para * E0_low + (1 - E0_weight_para) * (E0_low_para * silence_mean_energy)
    print "较高的动态能量阈值" + str(E0_high)
    print "较低的动态能量阈值" + str(E0_low)

# audio detection，基于能量和过零率的非实时语音检测
def silence_detection(en):
    # global zero_low
    # 记录端点检测激活状态，静音段用0表示；过渡段用1表示；语音段用2表示
    if en >= E0_high: # 如果能量和过零率任一超过较高门限，则进入语音段
        print "语音段"
        return "2"
    elif en >= E0_low: # 如果能量和过零率任一超过低门限，则进入过渡段
        print "过渡段"
        return "1"
    else:
        print "静音段"
        return "0"

# cross-zero computation
# def zero_compute(win_data_flo):
#     sum = 0
#     k = 0
#     while k < len(win_data_flo)-1:
#         if win_data_flo[k] * win_data_flo[k + 1] < 0:
#             sum = sum + 1
#         k += 1
#     return sum

# 2018.10.9, 获取语音起始截取位置,并返回截取音频。语音起始截取位置= 起始点start_point - 起始点延伸时长start_extend_time"
def getBatchSplitBlob(start_point, end_point):
    start_extend_time = 20  # 首句：换行后第一句为首句，首句语音起始往前延伸2s，n*0.1s，注意不能超过上一句的末尾。
    #若起始点延伸没超过上一句end_point，起始截取索引位置start_slice= start_point - start_extend；否则，end_point.index + 1作为起始点
    if ((start_point - start_extend_time) > end_point):
        print "语音起始切割位置：" + str(start_point - start_extend_time)
        start_slice = start_point - start_extend_time #语音起始点前移
    else:
        print "语音起始切割位置：" + str(end_point + 1)
        start_slice = end_point + 1
    # slice_Data = wave_data_arr[start_slice * window_length : bufferLength * window_length] #截取剩余录音
    return start_slice


# 获取识别数据,recognize_start是识别起始点index位置，recognize_end_last是上一句识别的结束点index位置。
def recognize(start_point, end_point, i, wave_data_arr, window_length):
    global splited_list, triggered_combined
    start_slice_point = getBatchSplitBlob(start_point, end_point)
    recognize_Data = wave_data_arr[start_slice_point * window_length: (i + 1) * window_length]
    splited_list.append(recognize_Data)
    triggered_combined = False

# detect speech point
def speech_separate_notRealTime(wave_raw_data): #参数为AudioSegment对象
    global splited_list, energy, triggered_combined
    count_0 = 0  # 记录有效静音段数目，2018.10.8
    count_1 = 0  # 记录过渡段数目，2018.10.8

    triggered_0 = True  # 2018.8.13，用于静音触发
    triggered_1 = False  # 2018.10.8，用于判断status=1是否触发
    triggered_2 = False  # 2018.8.13，用于语音status=2触发
    triggered_enter = False  # 2018.8.13，用于静音触发换行
    count_enter = 0  # 2018.8.13,统计静音时间计数，用来换行
    max_time = 160  # 2018.9.16 设置最高时长,(n/10)s,直接返回最终结果，重新计数
    min_speech = 5  # 2018.9.16 设置最短时长,(n/10)s,每段有效语音必须大于该时长

    # 2018.10.29, 短句合并在一起发送去识别，这里面不包括换行静音
    recognize_time = 20  # 2018.10.29，发送语音进行识别的最短时长。若<2s，则认为是短句；否则，是可以发送的长句
    recognize_combine_time = 50  # 2018.10.29, 短句合并，发送合并短句进行识别的最短时长5s = n*0.1s。
    triggered_combined = False # 防止上一个会议的数据残余
    # 如果触发，则保留最初始的起始点。不触发，则起始点继续往下更新，准备下一次的短句合并。
    recognize_start = 0  # 2018.10.29, 对于时长小于recognize_time的有效语音，记录最初短句的起始点start_point
    recognize_end_last = 0  # 2018.10.29, 对于时长小于recognize_time的有效语音，记录最初短句的上一个结束点recognize_end_last

    enter_time = 20  # 2018.9.16 设置换行时长(n/10)s
    slice_silence_time = 15 # 2018.10.29 设置silence_2s静音的截取长度
    max_silence = 2  # 2018.10.8，设置最短静音时长
    start_time = 4  # 语音起始时长(n/10)s
    start_point = 0  # 2018.10.8，语音起始索引位置
    # start_point_temp = 0  # 2018.10.8，记录语音4s起始索引位置
    end_point = 0  # 2018.10.8，语音结束索引位置,用来指代上一句语音结束的索引位置
    silence_frame_num = 5  # 2018.9.6，语音起始用于静音值估计的静音帧

    # 用于存储非实时语音的能量和过零率值
    # zero = []
    # 防止数据冗余，上一个会议的残留数据可能未清空
    energy = []
    splited_list = []

    # 将AudioSegment对象转换为采样数组，提取音频数据
    wave_data_arr = wave_raw_data.get_array_of_samples()
    framerate, nframes = wave_raw_data.frame_rate, wave_raw_data.frame_count()
    window_length = int(0.1 * framerate) # 与浏览器录音方式对齐，帧长100ms

    #  python2.7 division, float to int--round down
    for i in xrange(int(len(wave_data_arr) / window_length)):
        win_data = wave_data_arr[window_length * i: window_length * (i + 1)]
        win_data_flo = np.array(win_data, dtype=np.float)
        # compute energy
        en = (np.dot(win_data_flo, win_data_flo.T))
        if en < 0:
            print win_data_flo
            exit()
        energy.append(np.sqrt(en))
        # compute cross-zero
        # ze = zero_compute(win_data_flo)
        # zero.append(ze)

    i = 0 # 类比与实时语音端点检测，i表示索引, index = buffer.Length - 1.
    # len(energy) is equal to len(wave_data_arr)/window_length

    while i < len(energy):
        # print i
        if i == silence_frame_num:
            silence_value_estimate(0, silence_frame_num)
        elif i > silence_frame_num:
            # 如果在检测结束点的过程中，到达数据最后，进行输出
            if i == len(energy) - 1:
                if triggered_combined:
                    recognize(recognize_start, recognize_end_last, i, wave_data_arr, window_length )
                elif triggered_2:
                    recognize(start_point, end_point, i, wave_data_arr, window_length)
            en = energy[i]
            print en
            # ze = zero[i]
            # 记录端点检测激活状态，静音段用0表示；过渡段用1表示；语音段用2表示
            status = silence_detection(en)
            if status == '2':
                count_1 += 1
                count_0 = 0
                if triggered_0 and (not triggered_1) and (not triggered_2):
                    triggered_0 = False
                    start_point = i  #如果status由0到1，则需要先确定起始点
                # 判断是否触发语音，语音长度是否达到最大时长max_time和每4s发送一个临时识别结果
                if count_1 >= start_time:
                    print "语音开始"
                    triggered_2 = True
                    triggered_enter = False
                    if count_1 >= max_time:  # 如果连续说话超过最高时长，则直接返回最终结果
                        print "counter_16s:" + str(count_1)
                        # 截取16s的语音数据
                        recognize(start_point, end_point, i, wave_data_arr, window_length)
                        count_1 = 0
                        start_point = i + 1

            elif status == '1':
                count_1 += 1
                count_0 = 0 # 静音帧统计归零
                if triggered_0 and (not triggered_1) and (not triggered_2):
                    triggered_1 = True
                    triggered_0 = False
                    start_point = i - 1
                if triggered_2:
                    if count_1 >= start_time:
                        print "语音开始"
                        triggered_2 = True
                        triggered_enter = False
                        if count_1 >= max_time:  # 如果连续说话超过最高时长，则直接返回最终结果
                            print "counter_16s:" + str(count_1)
                            recognize(start_point, end_point, i, wave_data_arr, window_length)
                            count_1 = 0
                            start_point = i + 1
            else: #status=0
                count_0 += 1
                if not triggered_2: # 判断count_0在status=2之前出现
                    count_1 = 0
                    triggered_0 = True
                    triggered_1 = False
                else: # count_0在status=2之后出现，triggered_2 = true
                    if count_0 < max_silence: # 如果静音时长< 静音时长阈值，则继续录音
                        count_1 += 1
                    elif triggered_2: # count_0 >= max_silence，触发静音
                        triggered_0 = True
                        triggered_1 = False
                        triggered_2 = False
                        triggered_enter = True
                        count_enter = max_silence - 1
                        if count_1 - max_silence >= min_speech: # 最小语音时长
                            # 保存有效语音初始start_point,如果是断句triggered_combined = true，则不更新，否则更新。
                            print "start_point:" + str(start_point)
                            if not triggered_combined:
                                recognize_start = start_point
                                recognize_end_last = end_point
                            print 'recognize_start:' + str(recognize_start)
                            # 2018.10.29, 统计每段有效语音长度，如果length > recognize_time, 去识别；否则，进行短句合并，等下一段有效语音。
                            speech_length = i - start_point
                            print 'speech_length:' + str(speech_length)
                            # 判断有效语音长度是否超过识别最短发送时长recognize_time
                            if speech_length >= recognize_time:
                                # 获取识别数据,recognize_start是识别起始点index位置，recognize_end_last是上一句识别的结束点index位置。
                                recognize(recognize_start, recognize_end_last, i, wave_data_arr, window_length)
                            else:
                                triggered_combined = True # 开始短句合并
                                recognize_combine_length = i - recognize_start
                                print 'recognize_combine_length:' + str(recognize_combine_length)
                                # 判断短句合并的长度是否超过短句合并发送的最短时长recognize_combined_time
                                if recognize_combine_length >= recognize_combine_time:
                                    recognize(recognize_start, recognize_end_last, i, wave_data_arr, window_length)
                            print 'triggered_combined:' + str(triggered_combined)
                            end_point = i -max_silence
                            print 'end_point:' + str(end_point)
                            count_0 = 0
                            count_1 = 0
                        else: # 噪音
                            count_0 = 0
                            count_1 = 0
            # 换行函数
            if triggered_enter:
                count_enter = count_enter + 1;
                print "count_enter: " + str(count_enter)
                if count_enter >= enter_time:  # 如果静音超过2秒，就换行
                    triggered_enter = False
                    print "换行"
                    splited_list.append('return')
                    print "重新进行静音能量值估计"
                    silence_value_estimate(i - silence_frame_num,  i)  # 如果遇到较长静音，则重新进行静音检测
                    # 更新silence_2s, silence_2s在识别前加到语音前后。
                    silence_2s = wave_data_arr[(i - slice_silence_time) * window_length : i * window_length]
                    splited_list.append({"silence_2s": silence_2s})  # 用字典数据类型存储动态更新的silence_2s，用数据类型判断挑选出字典dict。
                    # 如果在断句合并过程中出现换行静音，则直接送去识别
                    if triggered_combined:
                        recognize(recognize_start, recognize_end_last, i, wave_data_arr, window_length)
        i += 1
    return splited_list