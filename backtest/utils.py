# coding=utf-8

from datetime import datetime as dt

def timestamp_datetime(time:int)->dt:
    """
    :param timestamp: 毫秒级别
    :return: datetime
    """
    return dt.fromtimestamp(time/1000)

def datetime_timestamp(date:dt)->int:
    """
    :param datetime: datetime
    :return: 毫秒级别的int类型
    """
    return int(date.timestamp() * 1000)