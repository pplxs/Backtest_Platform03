import time

import numpy as np
import pandas as pd

from .evalution_quantStats import *
from .report_generator.create_performance_overview import *
from .report_generator.create_performance_position import *
from .report_generator.create_performance_signal import *
from .report_generator.create_performance_returns import *

class PerformanceOverview:
    def __init__(self,all_data:pd.DataFrame, symbol_list:list, date_range:list,strategy_name:str,BASE_DIR:str,output_dirs:str,
                 symbol_returns:dict,symbol_cum_returns:dict,
                 benchmark_price:pd.Series,benchmark_returns:pd.Series,benchmark_cum_returns:pd.Series,
                 symbol_balance:dict,symbol_positions:dict,symbol_signals:dict,symbol_portfolio_value:dict,
                 ann_risk_free
                 ):
        # print(symbol_signals[symbol_list[0]][symbol_signals[symbol_list[0]] != 0])

        self.ann_risk_free = ann_risk_free
        self.all_data = all_data
        self.symbol_list = symbol_list
        self.date_range = date_range
        self.strategy_name = strategy_name
        self.BASE_DIR = BASE_DIR
        self.output_dirs = output_dirs
        self.symbol_returns = symbol_returns
        self.symbol_cum_returns = symbol_cum_returns
        self.benchmark_price = benchmark_price
        self.benchmark_returns = benchmark_returns
        self.benchmark_cum_returns = benchmark_cum_returns
        self.symbol_balance = symbol_balance
        self.symbol_positions = symbol_positions
        self.symbol_signals = symbol_signals
        self.symbol_portfolio_value = symbol_portfolio_value
    def _performance(self):
        # ��Ч����
        # �ܲ��Ե��������� �� �ۻ�����
        strategy_returns = self.symbol_returns["ALL"]
        strategy_cum_returns = self.symbol_cum_returns["ALL"]  # ��0��ʼ
        # ��׼���������� �� �ۻ�����
        benchmark_returns = self.benchmark_returns
        benchmark_cum_returns = self.benchmark_cum_returns  # ��0��ʼ
        # ��������
        excess_returns = strategy_cum_returns - benchmark_cum_returns

        eval_quant = EvalByQuantStats(portfolio_value=self.symbol_portfolio_value["ALL"],benchmark_price=self.benchmark_price,ann_risk_free=self.ann_risk_free)

        # �����س�
        strategy_drawdown_series = eval_quant.rolling_drawdown(strategy_returns)
        benchmark_drawdown_series = eval_quant.rolling_drawdown(benchmark_returns)

        # 1.1 ͼ
        performance_path = self._performance_graphs(strategy_returns,strategy_cum_returns,strategy_drawdown_series,
                           benchmark_returns,benchmark_cum_returns,benchmark_drawdown_series,excess_returns)

        # 1.2 ָ��
        performance_indcators = self._performance_indcators(eval_quant,strategy_returns)

        # 1.3 ���ر���
        show_report_path = create_performance_returns(self.strategy_name, "ALL", strategy_returns, benchmark_returns, self.BASE_DIR, self.ann_risk_free)


        return performance_path,performance_indcators,show_report_path
    def _performance_graphs(self,strategy_returns,strategy_cum_returns,strategy_drawdown_series,
                           benchmark_returns,benchmark_cum_returns,benchmark_drawdown_series,excess_returns
                           ):
        # ��Ч����ͼ
        data_performance = pd.DataFrame(
            {"date": self.date_range,
             "strategy_returns": strategy_returns, "strategy_cum_returns": strategy_cum_returns,
             "strategy_drawdown": strategy_drawdown_series,
             "benchmark_returns": benchmark_returns, "benchmark_cum_returns": benchmark_cum_returns,
             "benchmark_drawdown": benchmark_drawdown_series,
             "excess_returns": excess_returns}
        )
        performance_path = self.output_dirs + self.strategy_name + '_performance.html'
        create_performance_overview(data_performance, performance_path)
        return performance_path
    def _performance_indcators(self,eval_quant,strategy_returns):
        # ����ָ��
        # �ڳ��ʲ�
        start_term_assets = eval_quant.start_term_asset()
        # ��ĩ�ʲ�
        end_term_assets = eval_quant.end_term_asset()
        # �ۼ�ӯ��
        cum_pnl = eval_quant.accumulated_pnl()
        # �ۼ�������
        accumulate_return = eval_quant.accumulate_returnRate()
        # ��׼������
        benchmark_accumulate_return = eval_quant.benchmark_accumulate_returnRate()
        # ����������
        excess_return = accumulate_return - benchmark_accumulate_return
        # �껯������
        annualized_return = eval_quant.cagr(strategy_returns)
        # ���س�
        max_drawdown = eval_quant.max_drawdown()
        # ʤ��
        winRate = eval_quant.win_rate()
        # �껯������
        annualized_volatity = eval_quant.ann_volatity(strategy_returns)
        # ���ձ���
        sharp_ratio = eval_quant.ann_sharp()
        # beta beta
        alpha, beta = eval_quant.greeks()
        # ����ŵ����
        sortino_ratio = eval_quant.ann_sortino()
        # �������
        calmar_ratio = eval_quant.calmar()
        # ��Ϣ����
        info_ratio = eval_quant.information_ratio()
        # ����ŵ����
        treynor_ratio = eval_quant.treynor_ratio()
        # ��װ����ָ��
        perf_indcators = {"initial_assets": start_term_assets, "end_term_assets": end_term_assets,
                                 "cum_pnl": cum_pnl,
                                 "accumulate_return": accumulate_return,
                                 "benchmark_accumulate_return": benchmark_accumulate_return,
                                 "excess_return": excess_return, "annualized_return": annualized_return,
                                 "max_drawdown": max_drawdown,
                                 "winRate": winRate, "annualized_volatity": annualized_volatity, "alpha": alpha,
                                 "beta": beta, "sharp_ratio": sharp_ratio,
                                 "sortino_ratio": sortino_ratio, "calmar_ratio": calmar_ratio, "info_ratio": info_ratio,
                                 "treynor_ratio": treynor_ratio,
                                 "ann_risk_free": self.ann_risk_free, "trade_days": len(self.date_range)
                                 }
        # ͳһ������λС��
        perf_indcators = {key:np.round(value,2) for key,value in perf_indcators.items()}
        return perf_indcators

    def _position(self):
        # �ֲַ���
        data_performance_position = pd.DataFrame({
            "date": self.date_range, "balance": self.symbol_balance["ALL"],
            "position": self.symbol_positions["ALL"],
            "benchmark_price": self.benchmark_price
        })

        position_path = self.output_dirs + self.strategy_name + '_position.html'
        create_performance_position(data_performance_position, position_path)
        return position_path


    def _signal(self)->dict:
        symbol_signal_path = {}
        for symbol in self.symbol_list:
            signal_path = self.output_dirs + self.strategy_name + '_' + symbol + '_positions.html'
            symbol_data = self.all_data[self.all_data['symbol'] == symbol]
            symbol_data.reset_index(inplace=True, drop=True)
            date_position = pd.DataFrame()
            date_position['date'] = symbol_data['close_time_date'].values.flatten()
            date_position['high'] = symbol_data['high'].values.flatten()
            date_position['open'] = symbol_data['open'].values.flatten()
            date_position['low'] = symbol_data['low'].values.flatten()
            date_position['close'] = symbol_data['close'].values.flatten()
            date_position['position'] = self.symbol_positions[symbol].values.flatten()
            date_position['signal'] = self.symbol_signals[symbol].values.flatten()
            date_position['cum_returns'] = self.symbol_cum_returns[symbol].values.flatten()
            # ���ȱʧֵ
            date_position.fillna(value={"position": 0, "signal":0,"cum_returns":1}, inplace=True)
            create_performance_signal(date_position, signal_path)
            symbol_signal_path[symbol] = signal_path
            time.sleep(2)
        return symbol_signal_path

    def _pnl(self):
        symbol_return_path = {}
        symbol_return_indcators = {}
        for symbol in self.symbol_list:
            # 1.1 ͼ
            symbol_return_path[symbol] = create_performance_returns(self.strategy_name, symbol, self.symbol_returns[symbol], self.benchmark_price, self.BASE_DIR,self.ann_risk_free)
            # 1.2 ָ��
            eval_quant = EvalByQuantStats(portfolio_value=self.symbol_portfolio_value[symbol],benchmark_price=self.benchmark_price,ann_risk_free=self.ann_risk_free)
            symbol_return_indcators[symbol]=self._performance_indcators(eval_quant=eval_quant,strategy_returns=eval_quant.returns)
            time.sleep(2)
        return symbol_return_path, symbol_return_indcators