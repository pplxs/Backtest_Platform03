
from logging.handlers import RotatingFileHandler

from ..Tool.message_queue_sync import ProducerWorker, ConsumerWorker, MQ_EXCHANGE

# from ..Tool.client import OrderRPCClient

import logging

logger = logging.getLogger(__name__)

market_consumer = ConsumerWorker(
            exchange=MQ_EXCHANGE.SIGNAL_EXCHANGE,
            use_pool=False,
        )


class BaseTrade:

    def __int__(self, *args,  receive_routing_key=None, receive_queue_name=None, receive_auto_delete=True,
                strategy_name=None, account_key=None, **kwargs):
        # ���������
        # ������Ϣ��routing_key
        self.receive_routing_key = receive_routing_key
        # ������Ϣ��queue_name
        self.receive_queue_name = receive_queue_name
        # ������Ϣ��consumer�Ƿ��Զ�ɾ��֮ǰ����Ϣ
        self.receive_auto_delete = receive_auto_delete
        self.account_key = account_key

        # self.client = OrderRPCClient(account_key)
        # ��������
        self.strategy_name = strategy_name

    def log(self,log_path):
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)

        formatter = '%(asctime)s -<>- %(filename)s -<>- [line]:%(lineno)d -<>- %(levelname)s -<>- %(message)s'
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=logging.INFO)
        console_formatter = logging.Formatter(formatter)
        console_handler.setFormatter(console_formatter)

        handler = RotatingFileHandler(log_path, maxBytes=1024*1024*5, backupCount=5)
        handler.setLevel(logging.INFO)

        logger.addHandler(console_handler)
        logger.addHandler(handler)

        return logger

    def print_value(self):
        logger.info(self.receive_routing_key)
        logger.info(self.receive_queue_name)
        logger.info(self.receive_auto_delete)
        logger.info(self.account_key)
        logger.info(self.strategy_name)

    # ���������д
    def deal_message(self, message):
        pass


    # ����������Ϣ
    def handle_data(self, message_dict:dict, *args, **kwargs):
        # �������ݲ��ַ�
        te_messages = {}
        for symbol,message in message_dict.items():
            if message["cal_te_flag"]:
                position,te_signal,balance,portfolio_value,log_te_message = self.deal_message(message)  # ����ʵ��
                te_messages[symbol] = {"position": position, "te_signal": te_signal, "balance": balance,
                                       "portfolio_value": portfolio_value}
            else:
                te_messages[symbol] = {"position": None, "te_signal": None, "balance": message["balance"],
                                       "portfolio_value": None}

        # django �ַ�te��־


        return te_messages, log_te_message

    @classmethod
    def start(cls):
        ins = cls()
        logger.info(f"start {ins.strategy_name}")
        @market_consumer.register(routing_key=ins.receive_routing_key, queue_name=ins.receive_queue_name,
                                  auto_delete=ins.receive_auto_delete)
        def adapter(message, *args, **kwrags):
            ins.handle_data(message, *args, **kwrags)

        market_consumer.start_consuming()




