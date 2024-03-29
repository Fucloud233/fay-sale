import codecs
import os
import random
import time
import math

from core import wsa_server
from scheduler.thread_manager import MyThread

LOGS_FILE_URL = "logs/log-" + time.strftime("%Y%m%d%H%M%S") + ".log"


def random_hex(length):
    result = hex(random.randint(0, 16 ** length)).replace('0x', '').lower()
    if len(result) < length:
        result = '0' * (length - len(result)) + result
    return result


def __write_to_file(text):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file = codecs.open(LOGS_FILE_URL, 'a', 'utf-8')
    file.write(text + "\n")
    file.close()


def printInfo(level, sender, text, send_time=-1):
    if send_time < 0:
        send_time = time.time()
    format_time = time.strftime('%H:%M:%S', time.localtime(send_time))
    logStr = '[{}][{}] {}'.format(format_time, sender, text)
    print(logStr)
    if level >= 3:
        wsa_server.get_web_instance().add_cmd({"panelMsg": text})
    MyThread(target=__write_to_file, args=[logStr]).start()


def log(level, text):
    printInfo(level, "系统", text)


def print_cur_time(text: str, tm):
    log(1, text + '. 耗时: {} ms'.format(math.floor((time.time() - tm) * 1000)))