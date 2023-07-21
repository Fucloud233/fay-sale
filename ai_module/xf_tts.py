# -*- coding = utf-8 -*-
# @Time : 2023/07/19 19:42
# @Autor : Fucloud
# @FIle : xf_tts.py
# @Software : PyCharm


from utils import util, config_util
from utils import config_util as cfg
from utils import sound_util

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
# 用来表示流式
import ai_module.stream_trans_flag as st_flag

tts_status_disconnected = 0
tts_status_connecting = 1
tts_status_connected = 2


# 确认key是否存在
def check_xf_tts_key() -> bool:
    return config_util.key_xf_tts_app_id \
           and config_util.key_xf_tts_app_secret \
           and config_util.key_xf_tts_api_key is not None


class Speech:
    def __init__(self):
        self.connect_status = tts_status_disconnected
        self.flag = False
        if check_xf_tts_key():
            self.APPID = config_util.key_xf_tts_app_id
            self.APIKey = config_util.key_xf_tts_api_key
            self.APISecret = config_util.key_xf_tts_app_secret

            # 记录与服务端通信的URL
            self.url = self.create_url()
            self.ws = None

            # 记录一个单元包含的帧数
            self.cur_frame_count = 0
            self.total_frame_count = 5

            # 用于追加保存时的文件链接
            self.cur_audio = b''
            self.cur_pcm_data = []
            self.cur_index = 0

            # 标记位
            self.cur_message_flag = None
            self.is_over = False

            self.common_args = {"app_id": self.APPID}
            self.business_args = {
                # 返回mp3格式 aue=lame, sfl=1
                # "aue": "lame",
                # "sfl": 1,
                "aue": "raw",
                "auf": "audio/L16;rate=16000",
                "vcn": "x4_lingfeizhe_zl",
                "tte": "utf8"
            }

            self.flag = True

        self.__connection = None
        self.__history_data = []

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

    def __get_history(self, voice_name, style, text):
        for data in self.__history_data:
            if data[0] == voice_name and data[1] == style and data[2] == text:
                return data[3]
        return None

    # 不能够直接连接 每次传输数据时才会连接
    def connect(self):
        self.connect_server()
        return None

    def connect_server(self):
        def on_open(ws):
            self.connect_status = tts_status_connected
            # print("[debug] TTS连接成功")

        # 收到websocket关闭的处理
        def on_close(wsapp, close_status_code, close_msg):
            # 当服务端关闭连接后设置状态
            self.connect_status = tts_status_disconnected
            # print("### closed ### code:{}, msg:{}".format(close_msg, close_msg))

        def run(*args):
            self.connect_status = tts_status_connecting
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(self.url,
                                             on_message=self.on_message,
                                             on_close=on_close)
            self.ws.on_open = on_open
            self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        # 开启线程等待服务器连接
        thread.start_new_thread(run, ())

        while True:
            # print("[debug] 正在连接中...")
            if self.connect_status is tts_status_connected:
                break

    def close(self):
        # 如果没有断开连接则返回连接
        if self.connect_status is tts_status_connected:
            self.ws.close()

    # 将文本转语音
    def to_sample(self, text, style):
        """
        文字转语音
        :param text: 文本信息
        :param style: 说话风格、语气
        :returns: 音频文件路径
        """

        def run():
            # 如果没有连接 说明超时 需要重新连接
            if self.connect_status is tts_status_disconnected:
                self.connect_server()

            d = {
                "common": self.common_args,
                "business": self.business_args,
                "data": {
                    "status": 2,
                    "text": str(base64.b64encode(text.encode('utf-8')), "UTF8")
                }
            }
            d = json.dumps(d)
            self.file_url = None
            self.ws.send(d)

            # 在发送完毕之后 重新连接服务器
            self.connect_server()

        # 修改状态
        self.cur_file_urls = []
        self.is_over = False
        thread.start_new_thread(run, ())

        # 忙等 等待服务端响应
        # if self.file_url is not None:
        #     file_url = self.file_url
        #     self.file_url = None
        #     return file_url

        # 如果超时 则返回None
        # return None

    def on_message(self, ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]

            # print("[debug] msg: ", message)

            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                # 如果没有计数到头，则累加数据
                self.cur_audio += audio
                # print("[debug] cur audio:", self.cur_audio)
                self.cur_frame_count += 1

                if self.cur_frame_count == self.total_frame_count \
                        or status == 2:

                    # 保存当前的pcm数据
                    # 不保存在硬盘中 保存在内存中
                    self.cur_pcm_data.append(self.cur_audio)

                    # file_name = 'samples/sample-' + str(int(time.time() * 1000))

                    # (1) 保存pcm文件
                    # pcm_file_url = file_name + ".pcm"
                    # with open(pcm_file_url, 'wb') as f:
                    #     f.write(self.cur_audio)

                    # (2) 保存wav文件
                    # wav_file_url = file_name + '.wav'
                    # sound_util.pcm2wav(self.cur_audio, wav_file_url)
                    # self.cur_file_urls.append(wav_file_url)

                    # 重置当前音频
                    self.cur_audio = b''
                    self.cur_frame_count = 0

            # 注意 这个函数判断在后面
            if status == 2:
                # 保存文件URL
                self.cur_frame_count = 0
                self.is_over = True
                print("[debug] is_over = True")

        except Exception as e:
            errMsg = message["message"]
            code = message["code"]
            sid = message["sid"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            print("receive msg,but parse exception:", repr(e))

    def get_message(self) -> (bytes, int):
        # 首先判断还有没有剩余的
        tm = time.time()
        while True:
            if self.cur_index < len(self.cur_pcm_data) or self.is_over:
                break
            time.sleep(0.1)

        util.print_cur_time("等待第一帧完成", tm)

        # 有剩余的就返回播放
        # file_url = self.cur_file_urls[self.cur_index]
        pcm_data = self.cur_pcm_data[self.cur_index]

        # 累加当前坐标
        self.cur_index += 1

        # 根据状态返回标记符
        if self.cur_index == 1:
            flag = st_flag.stream_trans_start
        elif self.is_over and (self.cur_index == len(self.cur_pcm_data)):
            flag = st_flag.stream_trans_over
            self.cur_index = 0
            self.cur_pcm_data = []
        else:
            flag = st_flag.stream_trans_do

        # print("[debug] cur_index: {}, flag: {} ".format(self.cur_index, flag))

        return pcm_data, flag


if __name__ == '__main__':
    cfg.load_config()
    sp = Speech()
    sp.connect()
    text = """这是一段音频，测试一下3"""
    s = sp.to_sample(text, "cheerful")

    print(s)
    sp.close()
