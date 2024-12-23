import hashlib
import time

from cryptography.fernet import Fernet
from ..Tool.lru import LRUCacheDict


def md5(data):
    if isinstance(data, str):
        data = data.encode()
    d = hashlib.md5(data)
    return d.hexdigest()


def decode_key(data, key):
    if not key:
        # 如果 key 参数为空，函数将认为数据是一个简单的逗号分隔字符串，直接使用 split(',') 方法将其拆分成列表并返回。
        return data.split(',')  # for develop env
    f = Fernet(key)
    data = f.decrypt(data.encode())
    data = data.decode()
    return data.split(',')


def encode_key(data, key):
    if not key:
        return data
    f = Fernet(key)
    data = f.encrypt(data.encode())
    return data.decode()


def extend_list(data):
    result = []
    if isinstance(data, list):
        for item in data:
            result.extend(extend_list(item))
        return result
    else:
        return [f'{key}={value}' for key, value in data.items()]


def sign_dict(data):
    m = hashlib.md5()
    quote_datas = extend_list(data)
    ready_data = sorted(quote_datas, reverse=False)
    ready_encode = '&'.join(ready_data)
    m.update(ready_encode.encode())
    return m.hexdigest()


idempotent_lru = LRUCacheDict(max_size=10000, expiration=60)


class PayloadTimeout(Exception):
    pass


class RepeatPayloadError(Exception):
    pass


class SignError(Exception):
    pass


def check_sign(payload_wrapper, check_idempotent=False, timeout_window=200000):
    """ 检查payload中的ts是否超时
    timeout_window 200ms default
    """
    sign = payload_wrapper.pop('sign')
    ts = payload_wrapper.pop('timestamp', 0)
    payload = payload_wrapper['payload']
    cur_sign = sign_dict(payload)
    if sign != cur_sign:
        return '签名不一致错误'

    if check_idempotent and sign in idempotent_lru:
        # 检查是否已经有过该请求
        return '重复的请求！'

    delay_ts = int(time.time() * 1000) - ts
    if delay_ts > timeout_window:
        return f'超过对应的时间窗口,窗口值为{timeout_window}ms, 当前delay:{delay_ts}ms'

    idempotent_lru[sign] = 1
