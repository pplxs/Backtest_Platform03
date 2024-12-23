import logging
import time
from functools import wraps

import zerorpc
from gevent import monkey

from ..Tool.config import ID_TYPE
from .sign import sign_dict
from .rpc_plugin import RPCClientTracingMixin, RPCClientKwargsMixin

local = monkey.get_original("threading", "local")
logger = logging.getLogger(__name__)


#  负责处理 RPC 调用时的重连机制，当 RPC 调用失败时，会自动重试指定次数。
class ReconnectWrapper:
    """
    ReconnectWrapper 是一个包装类，用于包装 zerorpc 客户端函数，
    使其在遇到连接丢失（LostRemote）异常时能够自动重试连接，最多重试 max_retry 次。

    Attributes:
        client (object): zerorpc 客户端实例，负责重新连接。
        func (callable): 需要包装的客户端函数。
        retry (int): 最大重试次数，默认值为 5。
        __name__ (str): 被包装函数的名称。

    Methods:
        __call__(*args, retry=1, **kwargs):
            执行被包装的函数并捕获 LostRemote 异常。
            如果发生异常，尝试重新连接并递归调用自己。
            每次重试将 retry 参数加 1，直到达到最大重试次数。
    """
    def __init__(self, client, func, func_name, max_retry=5):
        self.client = client  # 传入的 zerorpc 客户端实例
        self.func = func  # 被包装的函数
        self.retry = max_retry  # 最大重试次数
        self.__name__ = func_name  # 存储被包装函数的名称

    def __call__(self, *args, retry=1, **kwargs):
        try:
            kwargs.update({"async": True})  # 设置异步调用
            async_result = self.func(*args, **kwargs)  # 调用被包装的函数
            return async_result.get()  # 获取异步调用的结果
        except zerorpc.exceptions.LostRemote as e:  # 捕获连接丢失异常
            logger.error(f'going error:{e}, reconnecting, retry:{retry}')  # 记录错误并尝试重连
            self.client.connect()  # 重新连接客户端
            time.sleep(0.001)  # 等待片刻后重试
            return self.__call__(*args, retry=retry + 1, **kwargs)  # 递归调用自身，重试函数


"""
RPCClient 类用于创建 ZeroRPC 客户端并管理连接。
使用缓存来重用已有的客户端实例。
定义了 connect 方法来建立连接。
使用 ReconnectWrapper 包装实际的 RPC 调用函数，以便在连接丢失时自动重试。
"""
class RPCClient:
    CACHE = local()
    def __init__(self, url, remote_app_name="-", exchange="-", timeout=10, heartbeat=1):
        """
        尝试从类的缓存属性 CACHE 中获取与 url 相关联的客户端实例。如果找到了，就将其赋值给 self.client。
        """
        self.client = getattr(type(self).CACHE, url, None)
        self.url = url
        self._remote_app_name = remote_app_name
        self._exchange = exchange
        if not self.client:
            # 创建新的客户端实例
            self.client = zerorpc.Client(timeout=timeout, heartbeat=heartbeat)
            setattr(type(self).CACHE, url, self.client)
            """
            完成客户端代码
            """
            self.connect()

    def connect(self):
        logger.info(f'client connect to {self.url}')
        self.client.connect(self.url)

    def __getattr__(self, name):
        """当尝试访问对象的属性但该属性不存在时，这个方法会被调用"""
        func = getattr(self.client, name)
        return ReconnectWrapper(self, func, func_name=name)

"""
RPCClientWithSign 类增加了对请求数据的签名和时间戳处理。
update_with_sign 方法用于签名请求数据。
wrapper_sign 方法包装 RPC 调用函数，使其在调用前增加签名和时间戳。
"""


class RPCClientWithSign():
    """
    RPCClientWithSign 类用于给 RPC 客户端的方法添加签名和时间戳，以确保请求的安全性。
    """

    def update_with_sign(self, payload):
        """
        将请求负载添加签名和时间戳。

        Args:
            payload (dict 或 list): 需要签名的请求负载。

        Returns:
            dict: 包含原始负载、签名和时间戳的字典。
        """
        if not isinstance(payload, (list, dict)):
            # 如果 payload 既不是字典也不是列表，直接返回原始 payload
            return payload

        sign = sign_dict(payload)  # 为 payload 生成签名
        payload_wrapper = {
            'timestamp': int(time.time() * 1000),  # 当前时间戳（毫秒级别）
            'payload': payload,  # 原始请求负载
            'sign': sign  # 生成的签名
        }
        return payload_wrapper

    def wrapper_sign(self, func):
        """
        装饰器：为被装饰的函数添加签名和时间戳，并调用它。

        Args:
            func (callable): 需要装饰的函数。

        Returns:
            callable: 装饰后的函数。
        """

        @wraps(func)
        def inner(payload, *args, **kwargs):
            """
            内部包装函数：添加签名和时间戳，并调用实际函数。

            Args:
                payload (dict 或 list): 请求负载。
                *args: 其他位置参数。
                **kwargs: 其他关键字参数。

            Returns:
                函数的返回值。
            """
            payload_wrapper = self.update_with_sign(payload)  # 添加签名和时间戳
            return func(self.uid, payload_wrapper, id_type=ID_TYPE.UID, *args, **kwargs)
            # 调用原始函数，传入用户 ID、负载字典以及其他参数

        return inner

    def __getattr__(self, name):
        """
        重写 __getattr__ 方法以便对 RPC 客户端的方法添加签名。

        Args:
            name (str): 需要访问的属性名称（方法名）。

        Returns:
            callable: 添加了签名和时间戳的装饰器函数。
        """
        func = super().__getattr__(name)  # 获取原始 RPC 客户端方法
        return self.wrapper_sign(func)  # 使用 wrapper_sign 装饰器包装原始方法


class RPCClientWithBIDSign(RPCClientWithSign):
    """BID的无视
    """

    def wrapper_sign(self, func):
        @wraps(func)
        def inner(payload, *args, **kwargs):
            payload_wrapper = self.update_with_sign(payload)
            return func(self.bid, payload_wrapper, id_type=ID_TYPE.BID, *args, **kwargs)
        return inner


class RPCClientWithSBIDSign(RPCClientWithSign):
    """使用SuperBook BOOK ID进行认证(无视)
    """

    def wrapper_sign(self, func):
        @wraps(func)
        def inner(payload, *args, **kwargs):
            payload_wrapper = self.update_with_sign(payload)
            return func(self.sbid, payload_wrapper, id_type=ID_TYPE.SBID, *args, **kwargs)
        return inner


class BaseRPCClient(RPCClientTracingMixin, RPCClientKwargsMixin, RPCClient):
    pass



class SignedRPCClient(RPCClientWithSign, BaseRPCClient):
    pass


class BIDSignedRPCClient(RPCClientWithBIDSign, BaseRPCClient):
    pass


class SBIDSignedRPCClient(RPCClientWithSBIDSign, BaseRPCClient):
    pass


BaseReuseRPCClient = BaseRPCClient
