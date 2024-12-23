import logging
import random
from datetime import date
from functools import partial, wraps

import msgpack

from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue, Connection, Producer
from django.conf import settings



logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://lucida:lucida@123@8.210.66.64:5672/ee"
# RABBITMQ_URL = settings.RABBITMQ_URL

class MQ_EXCHANGE:
    SIGNAL_EXCHANGE = "SIGNAL_EXCHANGE"
    MARKET_EXCHANGE = 'MARKET_EXCHANGE'
    ACCOUNT_EXCHANGE = 'ACCOUNT_EXCHANGE'
    ORDER_EXCHANGE = 'ORDER_EXCHANGE'
    RISK_EXCHANGE = 'RISK_EXCHANGE'
    VPOS_EXCHANGE = 'VPOS_EXCHANGE'
    CONFIG_EXCHANGE = 'CONFIG_EXCHANGE'
    DC_EXCHANGE = 'DC_EXCHANGE'
    VPOS_ENTITY_EXCHANGE = 'VPOS_ENTITY_EXCHANGE'


class QUEUE_NAME:
    MARKET_QUEUE = 'MARKET_QUEUE'
    SIGNAL_QUEUE_SHORT = 'SIGNAL_QUEUE_SHORT'
    SIGNAL_QUEUE_LONG = 'SIGNAL_QUEUE_LONG'
    SIGNAL_QUEUE_MULTI_FACTOR_LONG_SHORT = 'SIGNAL_QUEUE_MULTI_FACTOR_LONG_SHORT'

    SIGNAL_QUEUE_DOUBLE_MA_OKEX_SPOT_BTC_USDT = 'SIGNAL_QUEUE_DOUBLE_MA_OKEX_SPOT_BTC_USDT'
    SIGNAL_QUEUE_DOUBLE_MA_OKEX_SWAP_BTC_USDT = 'SIGNAL_QUEUE_DOUBLE_MA_OKEX_SWAP_BTC_USDT'



class ProducerWorker:
    def __init__(self, exchange):
        """
        注意，此处的 exchange 不是交易所而是 RabbitMQ 里面的交换机，用于接收 producer 发出来的消息
        定义在 MQ_EXCHANGE 中
        """
        self.producer = None
        self.connection = None
        self.exchange = exchange

    def init_connection(self):
        self.connection = Connection(RABBITMQ_URL)
        logger.info('establish_connection')
        channel = self.connection.channel()
        self.producer = Producer(channel, exchange=Exchange(self.exchange, type='topic'), auto_declare=True)

    def send(self, topic, payload, retry=1, expiration=None):
        if not topic:
            logger.error('topic can not be none:%s', topic)
            return
        if not self.producer or not self.connection:
            logger.info('main_channel is close, reconnect it')
            self.init_connection()

        exchange = Exchange(self.exchange, type='topic')
        self.producer.publish(
            msgpack.packb(payload),
            retry=True,
            exchange=exchange,
            routing_key=topic,
            expiration=expiration,
        )

    def close(self):
        self.connection.close()


class ConsumerWorker(ConsumerMixin):
    DEFAULT_EXCHANGE = None
    QUEUE_AUTO_DELETE = True
    QUEUE_DURABLE = True
    QUEUE_AUTO_ACK = True
    QUEUE_EXCLUSIVE = False
    QUEUE_MAX_LENGTH = None
    QUEUE_PREFETCH_COUNT = 10

    def __init__(self, exchange=None, heartbeat=10, use_pool=False):
        self._callbacks = {}
        exchange = exchange or type(self).DEFAULT_EXCHANGE
        if not exchange:
            raise Exception('exchange is necessary')
        self.exchange = exchange
        self.task_exchange = Exchange(exchange, type='topic')
        self.heartbeat = heartbeat

    def init_connection(self, conn):
        self.connection = conn

    def on_message(self, message, callback=None):
        try:
            data = msgpack.unpackb(message.body)
            routing_key = message.delivery_info['routing_key']
            callback(data, routing_key=routing_key, message_on_the_fly=message)
        except Exception as e:
            logger.exception(str(e), exc_info=True, stack_info=True)
        message.ack()

    def gen_queue_name(self, prefix):
        if not prefix:
            return ""
        today = str(date.today())
        rand = random.randint(0, 86400)
        return f'{prefix}_{today}_{rand}'

    def get_consumers(self, Consumer, channel):
        print("get_consumer")
        consumers = []
        for routing_key, config in self._callbacks.items():
            auto_ack = config['auto_ack']
            queue_name = config['queue_name']
            durable = config['durable']
            prefix_name = config['prefix_name']
            auto_delete = config['auto_delete']
            cb = config['cb']
            exchange = config['exchange']
            exclusive = config['exclusive']
            max_length = config['max_length']
            prefetch_count = config['prefetch_count']

            queue_arguments = {}

            if auto_delete:
                queue_arguments.update({
                    'x-expires': 2 * 24 * 60 * 60 * 1000  # 2 days
                })

            if auto_delete and not max_length:
                max_length = 1000

            if max_length:
                max_length = max(100, max_length)  # 最小为100
                queue_arguments.update({'x-max-length': max_length})

            if not prefix_name:
                prefix_name = f"{cb.__module__}.{cb.__name__}"[-150:]

            if not queue_name:
                queue_name = self.gen_queue_name(prefix_name)

            logger.info(f"QUEUE_NAME: {queue_name}")
            logger.info(f"ROUTING_KEY: {routing_key}")
            queue = Queue(queue_name, exchange,
                          routing_key=routing_key, auto_ack=auto_ack,
                          durable=durable, auto_delete=auto_delete,
                          exclusive=exclusive,
                          queue_arguments=queue_arguments,
                          )
            consumer = Consumer(
                queues=[],
                accept=['json', 'msgpack'],
                on_message=partial(self.on_message, callback=cb),
                prefetch_count=prefetch_count,  # 每次处理完5个后rmq会再次发送
            )
            consumer.add_queue(queue)
            config['queue'] = queue
            config['consumer'] = consumer
            consumers.append(consumer)

        return consumers

    def start_consuming(self, retry=0):
        logger.info('start connection')
        with Connection(RABBITMQ_URL, heartbeat=self.heartbeat) as conn:
            logger.info('establish_connection')
            try:
                self.init_connection(conn)
                self.run()
            except KeyboardInterrupt:
                logger.info('bye bye')
            except Exception as e:
                logger.exception(e)

    def register(self, routing_key, queue_name='', auto_delete=False, durable=True,
                 auto_ack=True, exchange=None, exclusive=False, max_length=None,
                 prefetch_count=10, prefix_name=''):
        if not auto_delete and not queue_name:
            raise Exception('not auto_delete queue must have a queue_name')
        # 本地测试：不需要queue持久化
        if queue_name.endswith('_develop'):
            durable = False
        routing_key = routing_key.upper()
        if exchange:
            exchange = Exchange(name=exchange, type='topic')
        else:
            exchange = self.task_exchange

        def wrapper(cb):
            @wraps(cb)
            def wrapped_cb(message, *args, **kwargs):

                cb(message, *args, **kwargs)

            self._callbacks[routing_key] = dict(
                cb=wrapped_cb, durable=durable, queue_name=queue_name,
                auto_delete=auto_delete, auto_ack=auto_ack,
                exchange=exchange, exclusive=exclusive,
                max_length=max_length, prefetch_count=prefetch_count,
                prefix_name=prefix_name,
            )
        return wrapper
    
    def online_unregister(self, routing_key):
        config = self._callbacks[routing_key]
        consumer = config['consumer']
        queue = config['queue']
        consumer.cancel_by_queue(queue)

    def online_register(self, routing_key):
        config = self._callbacks[routing_key]
        consumer = config['consumer']
        queue = config['queue']
        consumer.add_queue(queue)
        consumer.consume()
        logger.info('online_register success')

    def stop(self):
        self.should_stop = True




if __name__ == '__main__':
    consumer = ConsumerWorker(MQ_EXCHANGE.MARKET_EXCHANGE)
    consumer.start_consuming()
