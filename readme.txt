基于能量的语音端点检测v2.0：加入了初始能量精度检测，以确定固定能量阈值。
录音设备：鹅颈麦，声卡(混响竖直-关，音量指向最大，主持模式)，台式机输入(音量40%-50%,单声道模式)。以保持较好的音质
参数：energy_para:6.7;energy_value:56。
文本：测试文本-能量v2.0
阅读方式：普通话朗读模式，20cm，尽量读清每个字。

//2018.10.11
基于能量和过零率的双门限语音端点检测算法
	传统算法：能量双门限、过零率单门限。
		设置一个较高的能量门限E_high，确定语音已开始，再取一个比E_low，确定真正的始止点N1和N2.
		N1往左，N2往右--判断清音和噪音，则采用过零率门限zero，如果zero > Z，则认为是清音，如果zero < Z，则认为是噪音。
		如果语音段energy_low< E < energy_high 或 zero > Z，进入语音过渡段；
		如果语音段 E < energy_low 和 Z > zero，则恢复到静音段
		如果语音段满足 E > energy_high，则进入语音段
		如果语音段满足 E < energy_low 和 Z > zero_high：
			如果噪音时长 < 噪音长度阈值maxsilence，则继续收集语音；否则，认为语音段结束。			
			语音段结束后，如果语音段长度 > 最短语音时长阈值minSpeech，则认为是有效语音，否则认为是噪音。
	改进：
		1. 改进能量计算方式，采用语音能量正向、逆向连续变化差值(类似于方差)，来确定语音始止点。
		2. 中值平滑。将每5个语音信号数据的中值来代替这5个数值做平滑（2次）
		3. 语音最小时长限定。(现有算法已实现)（2次）
			对于语音始止点进行最小时长限定，只找到一个能量和过零率单阈值的案例
		4. 改进过零率。
			问题：电话信道影响，过零率增大
			解决：过零--转变为--过上下门限T
		5. energy双门限、zero单门限过渡段计算方式。
			问题：or方式，容易将噪音段误认为辅音；and方式，容易将清辅音误认为噪音
			解决：多门限和and方式。energy_s < E < energy_c and Z > zero 或 energy_c < E < energy_l and Z < zero,进入过渡段。
本算法采用：
	2.中值平滑
	3.最小时长限定
	5.基础原则：能量双门限、过零率单门限        
		如果语音段energy_low< E < energy_high 和 zero > zero_low，进入语音过渡段；
		如果语音段 E < energy_low 和 Z > zero_low，则恢复到静音段
		如果语音段 E >= energy_high或 Z <= zero_low，则进入语音段
		如果语音段满足 E < energy_low 和 Z > zero_low：
			如果噪音时长 < 噪音长度阈值maxsilence，则继续收集语音；否则，认为语音段结束。
			语音段结束后，如果语音段长度 > 最短语音时长阈值minSpeech，则认为是有效语音，否则认为是噪音。
	
算法流程：记录端点检测状态：0表示静音；1表示过渡段，可能是清音也可能是噪音；2表示语音段。
参数：
	count_0表示静音计数，count_1表示过渡段计数，2表示语音段计数
	triggered_0表示静音触发，triggered_1表示过渡段触发，triggered_2表示语音触发
	能量双门限，过零率单门限。E0_high = e0_high_para * silence_mean_value, E0_low = e0_low_para * silence_mean_value, zero_low。
	start_time起始语音触发时长0.4s，triggered_2= true；max_time表示语音最大时长16s，达到16s就强制发送语音，对语音进行重新计数；min_speech语音最短时长0.2s；max_silence静音最大时长2s，然后换行
	初始状态：triggered_0 = true; triggered_1 = false; triggered_2 = false.
	energy_list,zero_list用于将energy和zero保存到本地txt文件，前端数据通过ajax发送到后端，然后保存到本地。
算法: 
	原则：触发语音triggered_2=true和没触发语音triggered_2=false。
situation1:status=0可能进入status=0, 1, 2三个状态。
		status_0:如果进入0状态，则继续保持静音，count_0计数，count_1=0，triggered_0 = true, triggered_1=false，重复stpe1。
		status_1:如果进入1状态(即没有经过2状态)，则进入过渡段，可能是清音也可能是噪音，count_1计数，count_0=0，triggered_1 = true, triggered_0=false, 起始点start_point=update_audioData_length();
		status_2:如果进入2状态(即没有经过1状态直接进入2)，则直接进入语音段。count_1计数，count_0=0，triggered_0=false, 判断是否触发语音最短时长，起始点start_point=update_audioData_length();
situation2:status=1可能进入status=0, 1, 2三个状态。
		status_0:如果进入0状态(即没有经过2状态)，count_0计数，count_1=0, triggered_0 = true, triggered_1 = false。
		status_1:如果进入1状态，count_1继续计数，但start_point位置不变。
		status_2:如果进入2状态, count_1继续计数，采用初始status=1的start_point位置，判断是否触发语音最短时长。
situation3:status=2可能进入status=0, 1, 2三个状态。(根据triggered_2是否触发，即判断是否超过触发时长start_time)
		status_0:如果进入0状态(即经过来2状态)，count_0计数，判断是否触发静音最短时长，if (count_0 >= max_silence){}，false表示没有触发静音，继续录音，count_1计数；true表示触发静音，triggered_0=true, triggered_1=false, triggered_2=false。
		如果触发静音(count_0 >= max_silence)：判断 if (count_1 -max_silence >= min_speech){}，true表示为满足有效语音的最短时长，将其送去识别HZRecorder.analysis()。count_0=0,count_1=0,count_enter=max_silence-1；false表示能量噪音，舍弃count_1=0。
		Status_1 或 status_2:如果进入1状态 或2状态，count_1继续计数，判断 if (count_1 >= min_speech){}，true表示满足语音有效时长，触发语音，triggered_2=true, triggered_enter=false。判断 if (count_1 > max_time){}连续语音是否到达最大时长max_time，true送去识别HZRecorder.analysis();if (% 40==0){}是否4s发送一次临时识别结果


多个短句合并算法：
	目的：将由结巴、卡壳等原因造成的多个短句合并成一个长句，发送去识别，提高语音识别的准确度。
	短句(碎句子)：0.5～2s
	功能：
		长句子：>=2s，发送去识别
		碎句子合并：>=5s，发送去识别 — — —
		碎句子 + 长句子：发送去识别 —— — ——
		碎句子 + 换行enter：发送去识别
		碎句子 + 暂停会议：发送去识别
	算法：
		step1：如果>=2s， 直接送去识别；否则，进行短句合并吗，triggered_combined = true，起始点start_point不变，赋值给recognize_start = start_point.
		step2：判断在短句合并过程中是否出现换行或暂停会议 (enter or pause) && triggered_combined=true，如果出现，将现有短句发送去识别，否则进行下一段有效语音时长判断。
		step3：
			如果下一段语音时长>=2s，则短句 + 长句，发送去识别。recognize_point，triggered_combined = false.
			如果下一段有效音频0.5～2s，则继续进行短句合并，并判断短句+之前短句时长是否>=5s，如果是，则发送recognize_start去识别，triggered_combined=false，否则继续判断下一段有效音频，直到短句合并时长>=5s


