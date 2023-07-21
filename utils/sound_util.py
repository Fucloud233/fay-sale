# -*- coding = utf-8 -*-
# @Time : 2023/07/20 17:34
# @Autor : Fucloud
# @FIle : sound_util.py
# @Software : PyCharm

import wave


def pcm2wav(pcm_data, wav_file, channels=1, bits=16, sample_rate=16000):
    # 打开将要写入的 WAVE 文件
    wavfile = wave.open(wav_file, 'wb')
    # 设置声道数
    wavfile.setnchannels(channels)
    # 设置采样位宽
    wavfile.setsampwidth(bits // 8)
    # 设置采样率
    wavfile.setframerate(sample_rate)
    # 写入 data 部分
    wavfile.writeframes(pcm_data)
    wavfile.close()
