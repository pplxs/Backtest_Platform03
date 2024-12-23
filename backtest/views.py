# coding=utf-8
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import asyncio
import json
from . import utils

from django.shortcuts import render, HttpResponse, redirect
from .data_loader.operate_database import *
from .trade_engine.trade.trade import *
from .evaluator.performance_overview import *
from .evaluator.evalution_quantStats import *
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
import hashlib
import importlib.util
from .forms import CodeForm


from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

def configurate_parameters(req):

    return render(req, "backtest/configurationParameters.html")

def load_data(req):
    if req.method=="POST":
        exchange = req.POST.get('exchange')
        initial_cash = int(req.POST.get('initial_cash'))
        symbol = req.POST.get('symbol')
        symbol_num = int(req.POST.get('symbol_num'))
        start_date = req.POST.get('start_date')
        end_date =  req.POST.get('end_date')
        interval =  req.POST.get('interval')
        handing_fee = float(req.POST.get('handing_fee')) / 100
        slip_fee = float(req.POST.get('slip_fee')) / 100
        symbol_list = symbol.split(' ')

        # 通过session存取数据
        req.session['interval'] = interval
        req.session['start_date'] = start_date
        req.session['end_date'] = end_date
        req.session['symbol_list'] = symbol_list
        req.session['exchange'] = exchange
        req.session['initial_cash'] = initial_cash
        req.session['handing_fee'] = handing_fee
        req.session['slip_fee'] = slip_fee

        all_data_json, benchmark_json, date_range_json = load_and_process_data(symbol_list, start_date, end_date,
                                                                               interval)
        req.session['all_data_json'] = all_data_json
        req.session['benchmark_json'] = benchmark_json
        req.session['date_range_json'] = date_range_json
    return render(req, "backtest/upload_files.html")

def upload_files(req):
    context = {}
    filename = None
    file_url = None
    if req.method == 'POST':
        save_path = settings.MEDIA_ROOT
        fs = FileSystemStorage(location=save_path)
        file_full_path = None
        if 'myfile' in req.FILES:
            myfile = req.FILES['myfile']
            filename = myfile.name
            strategy_name = filename.split('.')[0]
            file_full_path = os.path.join(save_path, myfile.name) # 文件完整路径
            req.session['strategy_name'] = strategy_name
            req.session['strategy_path'] = file_full_path
            # 检查文件是否已存在
            if os.path.exists(file_full_path):
                # 读取现有文件内容并计算哈希值
                with open(file_full_path, 'rb') as existing_file:
                    existing_file_content = existing_file.read()
                    existing_file_hash = hashlib.md5(existing_file_content).hexdigest()

                # 读取上传文件内容并计算哈希值
                uploaded_file_content = myfile.read()
                uploaded_file_hash = hashlib.md5(uploaded_file_content).hexdigest()

                # 比较哈希值
                if existing_file_hash == uploaded_file_hash:   # 如果一致，则 不用覆盖
                    context['message'] = 'File already exists but with the same content. Not overwriting.'
                else: # 如果不一致，则重写进该文件
                    context['message'] = 'File already exists with different content. Overwriting...'
                    myfile.seek(0)  # 重置文件指针到文件开头
                    with open(file_full_path, 'wb') as f:
                        f.write(uploaded_file_content)
            else:
                # 保存新文件
                filename = fs.save(myfile.name, myfile)
                file_url = fs.url(filename)
                context['file_url'] = file_url

            with open(fs.path(filename), 'r', encoding='utf-8') as file:
                file_content = file.read()
                context['file_content'] = file_content
                context['filename'] = filename

                # file_url是提供给用户的文件下载链接
                file_url = req.build_absolute_uri(settings.MEDIA_URL + filename)
                context['file_url'] = file_url

                # 创建表单实例并设置初始值
                form = CodeForm(initial={'code': file_content})
                context['form'] = form

            return render(req, "backtest/upload_files.html", context)

        if 'backtest' in req.POST:
            # 获取编码器中的代码，并存入原来上传路径中，目的在于运行用户在前端页面修改代码
            form = CodeForm(req.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                with open(req.session.get('strategy_path',None), 'w', encoding='utf-8') as file:
                    for line in code.splitlines():
                        file.write(line+'\n')
                print(code)
            return redirect('execute_strategy')



def execute_strategy(req):
    symbol_list = req.session.get('symbol_list',None)
    exchange = req.session.get('exchange',None)
    balance = req.session.get('initial_cash',None)
    handing_fee = req.session.get('handing_fee',None)
    slip_fee = req.session.get('slip_fee',None)
    strategy_name = req.session.get('strategy_name', None)
    strategy_path = req.session.get('strategy_path', None)

    all_data_json = req.session.get('all_data_json', None)
    benchmark_json = req.session.get('benchmark_json', None)
    date_range_json = req.session.get('date_range_json', None)

    # json -> dataframe or list
    all_data = pd.read_json(all_data_json, orient='records')
    date_range = json.loads(date_range_json)
    benchmark = pd.read_json(benchmark_json, orient='records')
    # 修改时间格式
    date_range = [utils.timestamp_datetime(x) for x in date_range]
    all_data['close_time'] = all_data['close_time'].apply(lambda x: utils.datetime_timestamp(x))
    all_data['close_time_date'] = all_data['close_time_date'].apply(lambda x: utils.timestamp_datetime(x))
    benchmark['close_time'] = benchmark['close_time'].apply(lambda x: utils.datetime_timestamp(x))
    benchmark['close_time_date'] = benchmark['close_time_date'].apply(lambda x: utils.timestamp_datetime(x))
    benchmark_price = benchmark["close"]
    benchmark_price.index = date_range

    ae_log_path = str(BASE_DIR) + f'\\backtest/analyse_engine/log/{strategy_name}.log'
    te_log_path = str(BASE_DIR) + f'\\backtest/trade_engine/log/{strategy_name}.log'
    try:
        if strategy_path and os.path.exists(strategy_path):
            parent_dirs = os.path.dirname(strategy_path)
            print(parent_dirs)
            sys.path.insert(0,parent_dirs)
            module_name = strategy_name
            spec = importlib.util.spec_from_file_location(module_name, strategy_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            ae = None
            strategy_class = getattr(module, strategy_name)
            if strategy_class.deal_message and strategy_class.execute_AE_TE:   # 判断是否包含方法deal_message 和 execute_AE_TE
                ae = strategy_class(ae_log_path, strategy_name, symbol_list)
            te = Trade(strategy_name, te_log_path)

            # 执行AE 和 TE
            symbol_balance,symbol_portfolio_value,symbol_positions,symbol_signals, log_te_message = ae.execute_AE_TE(ae=ae, te=te, strategy_name=strategy_name, symbol_list=symbol_list, balance=balance, all_data=all_data,
                                                                                                   exchange=exchange,date_range=date_range,handing_fee=handing_fee, slip_fee=slip_fee, cal_ae_flag=True)  # cal_ae_flag :表示是否需要计算ae中的deal_message
            # 需要显示的 te 日志信息
            log_te_message

            symbol_portfolio_value["ALL"] = pd.Series(np.zeros(len(date_range)))
            symbol_balance["ALL"] = pd.Series(np.zeros(len(date_range)))
            symbol_positions["ALL"] = pd.Series(np.zeros(len(date_range)))
            for symbol in symbol_list:
                # list -> Series
                symbol_balance[symbol] = pd.Series(symbol_balance[symbol])
                symbol_positions[symbol] = pd.Series(symbol_positions[symbol])
                symbol_signals[symbol] = pd.Series(symbol_signals[symbol])
                symbol_portfolio_value[symbol] = pd.Series(symbol_portfolio_value[symbol])

                # print(symbol_signals[symbol][symbol_signals[symbol]!=0])

                # 计算整体表现
                symbol_portfolio_value["ALL"] += symbol_portfolio_value[symbol]
                symbol_balance["ALL"] += symbol_balance[symbol]
                symbol_positions["ALL"] += symbol_positions[symbol]


            symbol_returns = {}
            symbol_cum_returns = {}
            symbol_list_tmp = symbol_list.copy()
            symbol_list_tmp.append("ALL")
            for s in symbol_list_tmp:
                # 统一设置index为 Datetime
                try:
                    symbol_signals[s].index = date_range
                    # print(symbol_signals[symbol][symbol_signals[symbol] != 0])
                except KeyError as e:
                    print(f"KeyError {e}")
                except Exception:
                    raise
                symbol_balance[s].index = date_range
                symbol_positions[s].index = date_range
                symbol_portfolio_value[s].index = date_range

                # 计算symbol and ALL returns
                eval_quant = EvalByQuantStats(symbol_portfolio_value[s],benchmark_price)
                symbol_returns[s] = eval_quant.returns
                symbol_cum_returns[s] = eval_quant.cum_returns

            # 基准收益
            benchmark_returns = eval_quant.benchmark_returns
            benchmark_cum_returns = eval_quant.benchmark_cum_returns

            # 统一保存文件夹
            base_dir = str(BASE_DIR)
            output_dirs = str(BASE_DIR) + '\\' + f'templates/backtest/reports/PerformanceOverview/'


            perf_over = PerformanceOverview(
                all_data=all_data, symbol_list=symbol_list, date_range=date_range, strategy_name=strategy_name,BASE_DIR=base_dir,output_dirs=output_dirs,
                symbol_returns=symbol_returns,symbol_cum_returns=symbol_cum_returns,benchmark_price=benchmark_price,
                benchmark_returns=benchmark_returns,benchmark_cum_returns=benchmark_cum_returns,
                symbol_balance=symbol_balance, symbol_positions=symbol_positions, symbol_signals=symbol_signals, symbol_portfolio_value=symbol_portfolio_value,
                ann_risk_free = 0.03
            )

            # 绩效概览 ALL
            performance_combined = {}
            performance_path, performance_indcators,show_report_path = perf_over._performance()
            performance_combined["performance_path"]=performance_path
            performance_combined["performance_indcators"]=performance_indcators
            performance_combined["show_report_path"]=show_report_path

            # 持仓分析
            performance_position_path = perf_over._position()

            # 信号分析
            symbol_signal_path = perf_over._signal()

            # 收益分析
            symbol_return_path, symbol_return_indcators = perf_over._pnl()
            symbol_returns_combined = {symbol: (symbol_return_path[symbol], symbol_return_indcators[symbol]) for symbol in symbol_list}

            return render(req,"backtest/performance_overview.html",{"performance_combined":performance_combined,
                                                                "symbol_signal_path":symbol_signal_path,"symbol_returns_combined":symbol_returns_combined,
                                                                "performance_position_path":performance_position_path,
                                                                })
    except asyncio.CancelledError:
        raise




