# -*- coding = utf-8 -*-
# @Time : 2023/07/21 14:32
# @Autor : Fucloud
# @FIle : test_pyaudio.py
# @Software : PyCharm

import os
import pyaudio

if __name__ == '__main__':
    audio_player = pyaudio.PyAudio()
    stream = audio_player.open(format=pyaudio.paInt16,
                               channels=1,
                               rate=16000,
                               output=True)

    file_path = "samples/"
    for _, _, file_list in os.walk(file_path):
        for file_url in file_list:
            print("[debug] cur path: ", file_url)
            with open(file_path + file_url, 'rb') as f:
                audio_data = f.read()
                stream.write(audio_data)

    stream.stop_stream()
    stream.close()
