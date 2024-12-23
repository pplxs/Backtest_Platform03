"""
生成topic的位置，针对的模块：
trade_engine
"""



def generate_analyse_engine_topic(strategy,subject=None):
    """

    strategy: 策略
    subject: 种类
    """
    topic = f'TRADE_ENGINE.SIGNAL.{strategy}'
    if subject:
        topic = f'{topic}.{subject}'
    return topic.upper()


def generate_analyse_engine_spot_ma_topic(strategy,subject=None):
    """

    strategy: 策略
    subject: 种类
    """
    topic = f'SIGNAL_ENGINE.SIGNAL.SPOT.MA.{strategy}'
    if subject:
        topic = f'{topic}.{subject}'
    return topic.upper()


def generate_analyse_engine_swap_ma_topic(strategy,subject=None):
    """

    strategy: 策略
    subject: 种类
    """
    topic = f'SIGNAL_ENGINE.SIGNAL.SWAP.MA.{strategy}'
    if subject:
        topic = f'{topic}.{subject}'
    return topic.upper()


