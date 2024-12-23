import time
from logging.handlers import RotatingFileHandler

from Tool.message_queue_sync import ProducerWorker, ConsumerWorker, MQ_EXCHANGE
from kombu import Exchange
import msgpack
import logging
from abc import ABC, abstractmethod

market_consumer = ConsumerWorker(
            exchange=MQ_EXCHANGE.MARKET_EXCHANGE,
            use_pool=False,
        )


class BaseStrategy(ABC):

    def __init__(self, receive_routing_key, receive_queue_name, receive_auto_delete, send_routing_key,
                strategy_name,log_path):
        # 子类必填项
        # 接收消息的routing_key
        self.receive_routing_key = receive_routing_key
        # 接收消息的queue_name
        self.receive_queue_name = receive_queue_name
        # 接收消息的consumer是否自动删除之前的消息
        self.receive_auto_delete = receive_auto_delete

        # 发送消息的routing_key
        self.send_routing_key = send_routing_key
        # 发送消息的Exchange
        self.send_exchange = MQ_EXCHANGE.SIGNAL_EXCHANGE

        # 策略名字
        self.strategy_name = strategy_name

        self.log_path =log_path

    def log(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)

        formatter = '%(asctime)s -<>- %(filename)s -<>- [line]:%(lineno)d -<>- %(levelname)s -<>- %(message)s'
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=logging.INFO)
        console_formatter = logging.Formatter(formatter)
        console_handler.setFormatter(console_formatter)

        handler = RotatingFileHandler(self.log_path, maxBytes=1024*1024*5, backupCount=5)
        handler.setLevel(logging.INFO)

        logger.addHandler(console_handler)
        logger.addHandler(handler)

        return logger

    # def print_value(self):
    #     logger.info(self.receive_routing_key)
    #     logger.info(self.receive_queue_name)
    #     logger.info(self.receive_auto_delete)
    #     logger.info(self.send_routing_key)
    #     logger.info(self.send_exchange)
    #     logger.info(self.strategy_name)

    # 子类必须重写
    @abstractmethod
    def deal_message(self, message):
        pass

    # 信号发出方法
    def pushing_signal(self, data: dict):
        signal_msg = {
            "strategy_name": self.strategy_name,
            "data": data,
            "timestamp": time.time()
        }
        # 发送数据到mq
        producer = ProducerWorker(self.send_exchange)
        producer.init_connection()
        producer.producer.publish(
            msgpack.packb(signal_msg),
            retry=True,
            exchange=Exchange(producer.exchange, type='topic'),
            routing_key=self.send_routing_key,
            expiration=None, )

    # 接收上游消息
    def handle_data(self, message_list:list, *args, **kwargs):
        self.logger = self.log()
        # 处理数据并分发
        signal_messages = {}
        for i in range(len(message_list)):
            symbol = message_list[i]['symbol']
            if message_list[i]["cal_ae_flag"]:
                signal_message = self.deal_message(message_list[i])  # 子类实现
                self.logger.info(signal_message)
                signal_messages[symbol] = signal_message["signal"]
            else:
                signal_messages[symbol] = None
        self.logger.handlers.clear()
        return signal_messages

    @classmethod
    def start(cls):
        ins = cls()
        # logger.info(f"启动{ins.strategy_name}")

        @market_consumer.register(routing_key=ins.receive_routing_key, queue_name=ins.receive_queue_name,
                                  auto_delete=ins.receive_auto_delete)
        def adapter(message, *args, **kwrags):
            ins.handle_data(message, *args, **kwrags)

        market_consumer.start_consuming()


