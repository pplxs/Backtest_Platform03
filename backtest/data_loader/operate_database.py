from django.shortcuts import render, HttpResponse
import mysql.connector
from ..models import *
from mysql.connector import Error
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
from asgiref.sync import sync_to_async
from django.http import Http404

# daily
DataInfo = BinanceSpotKlineDaily  # 日线的model

# 1m
# DataInfo = BinanceSpotKline1m  # 1m的model


def db_insert(req):
    try:
        connection = mysql.connector.connect(
            host='lucida-pricevolume.rwlb.rds.aliyuncs.com',
            database='lucida_cex_data_trade',
            user='lucida_read',
            password='read123!@#'
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("成功连接到 MySQL 数据库，版本：", db_info)
    except Error as e:
        print("连接错误：", e)

    cursor = connection.cursor()

    # daily
    q = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'lucida_cex_data_trade' AND TABLE_NAME LIKE 'binance_spot_kline_daily_%';"  # 查询以binance_spot_kline_daily_开头的所有表的名称
    # query = 'select * from binance_spot_kline_daily_2024'       # 这儿也要记得改变

    # 1m
    # q = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'lucida_cex_data_trade' AND TABLE_NAME LIKE 'binance_spot_kline_1m_%';"  # 查询以binance_spot_kline_1m_开头的所有表的名称

    cursor.execute(q)
    table_names = cursor.fetchall()

    for i in range(len(table_names)):
        print(table_names[i][0])
        query = f'select * from {table_names[i][0]}'

        cursor.execute(query)
        records = cursor.fetchall()
        data = pd.DataFrame(records)

        q = f'SHOW COLUMNS FROM {table_names[i][0]};'

        cursor.execute(q)
        columns = cursor.fetchall()
        data.columns = [x[0] for x in columns]
        data_dict = data.to_dict(orient='records')

        # 分离已存在的数据和需要创建的数据
        existing_items = []
        new_items = []

        keys_to_check = [(item['symbol'], item['close_time']) for item in data_dict]

        # 使用 in 查询来检查哪些数据已经存在
        existing_keys = set(
            DataInfo.objects.filter(symbol__in=[k[0] for k in keys_to_check], close_time__in=[k[1] for k in keys_to_check])
            .values_list('symbol', 'close_time')
        )

        for item in data_dict:
            key = (item['symbol'], item['close_time'])
            if key in existing_keys:
                existing_items.append(item)
            else:
                new_items.append(item)

        for item in existing_items:
            print(f"{item['symbol'], item['close_time']}数据存在。")

        if new_items:
            for item in new_items:
                data = DataInfo(current_time=item['current_time'],
                                symbol=item['symbol'],
                                open_time=item['open_time'],
                                open_time_date = item['open_time_date'],
                                open=item['open'],
                                high=item['high'],
                                low=item['low'],
                                close=item['close'],
                                volume=item['volume'],
                                close_time=item['close_time'],
                                close_time_date=item['close_time_date'],
                                amount=item['amount'],
                                number_of_trades=item['number_of_trades'],
                                buy_volume=item['buy_volume'],
                                buy_amount=item['buy_amount'],
                                )
                data.save()
                print(f"insert {data} in {DataInfo}")

    return HttpResponse("<p>数据添加成功！</p>")


def db_filter(DataInfo,symbol_list,start_date,end_date):
    data = pd.DataFrame()
    for i in range(len(symbol_list)):
        try:
            data_obj = DataInfo.objects.filter(symbol=symbol_list[i],close_time_date__range=(start_date,end_date))
            data_dict = [{'close_time': item[0],'close_time_date': item[1],'symbol':item[2], 'high':float(item[3]),'open':float(item[4]),'low':float(item[5]),'close': float(item[6])} for item in data_obj.values_list('close_time','close_time_date','symbol','high','open','low','close')]
            data_tmp = pd.DataFrame(data_dict)
            data_tmp.drop_duplicates(inplace=True) # 去重
            data_tmp.sort_values(by='close_time',inplace=True) # 按照时间进行升序排列
            data = pd.concat([data,data_tmp],axis=0)
        except Exception as e:
            raise Http404(f"{symbol_list[i]} is not exist!")
    data.reset_index(inplace=True, drop=True)
    return data
