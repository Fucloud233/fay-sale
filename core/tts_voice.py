from enum import Enum


class EnumVoice(Enum):
    # 在这里添加其他音频源
    XIAO_XIAO = {
        "name": "晓晓",
        "voiceName": "zh-CN-XiaoxiaoNeural",
        "styleList": {
            "angry": "angry",
            "lyrical": "lyrical",
            "calm": "gentle",
            "assistant": "affectionate",
            "cheerful": "cheerful"
        }
    }
    YUN_XI = {
        "name": "云溪",
        "voiceName": "zh-CN-YunxiNeural",
        "styleList": {
            "angry": "angry",
            "lyrical": "disgruntled",
            "calm": "calm",
            "assistant": "assistant",
            "cheerful": "cheerful"
        }
    }
    XIAO_YI = {
        "name": "晓依",
        "voiceName": "zh-CN-XiaoyiNeural",
        "styleList": {
            "angry": "angry",
            "lyrical": "disgruntled",
            "calm": "calm",
            "assistant": "assistant",
            "cheerful": "cheerful"
        }
    }
    YUN_FENG = {
        "name": "云枫",
        "voiceName": "zh-CN-YunfengNeural",
        "styleList": {
            "angry": "angry",
            "lyrical": "disgruntled",
            "calm": "calm",
            "assistant": "assistant",
            "cheerful": "cheerful"
        }
    }


def get_voice_list():
    return [EnumVoice.YUN_XI, EnumVoice.XIAO_XIAO, EnumVoice.XIAO_YI, EnumVoice.YUN_FENG]


def get_voice_of(name):
    for voice in get_voice_list():
        if voice.name == name:
            return voice
    return None
