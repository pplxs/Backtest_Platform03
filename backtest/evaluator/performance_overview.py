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
        # 绩效概览
        # 总策略的日收益率 和 累积收益
        strategy_returns = self.symbol_returns["ALL"]
        strategy_cum_returns = self.symbol_cum_returns["ALL"]  # 从0开始
        # 基准的日收益率 和 累积收益
        benchmark_returns = self.benchmark_returns
        benchmark_cum_returns = self.benchmark_cum_returns  # 从0开始
        # 超额收益
        excess_returns = strategy_cum_returns - benchmark_cum_returns

        eval_quant = EvalByQuantStats(portfolio_value=self.symbol_portfolio_value["ALL"],benchmark_price=self.benchmark_price,ann_risk_free=self.ann_risk_free)

        # 滚动回撤
        strategy_drawdown_series = eval_quant.rolling_drawdown(strategy_returns)
        benchmark_drawdown_series = eval_quant.rolling_drawdown(benchmark_returns)

        # 1.1 图
        performance_path = self._performance_graphs(strategy_returns,strategy_cum_returns,strategy_drawdown_series,
                           benchmark_returns,benchmark_cum_returns,benchmark_drawdown_series,excess_returns)

        # 1.2 指标
        performance_indcators = self._performance_indcators(eval_quant,strategy_returns)

        # 1.3 下载报告
        show_report_path = create_performance_returns(self.strategy_name, "ALL", strategy_returns, benchmark_returns, self.BASE_DIR, self.ann_risk_free)


        return performance_path,performance_indcators,show_report_path
    def _performance_graphs(self,strategy_returns,strategy_cum_returns,strategy_drawdown_series,
                           benchmark_returns,benchmark_cum_returns,benchmark_drawdown_series,excess_returns
                           ):
        # 绩效绘制图
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
        # 计算指标
        # 期初资产
        start_term_assets = eval_quant.start_term_asset()
        # 期末资产
        end_term_assets = eval_quant.end_term_asset()
        # 累计盈亏
        cum_pnl = eval_quant.accumulated_pnl()
        # 累计收益率
        accumulate_return = eval_quant.accumulate_returnRate()
        # 基准收益率
        benchmark_accumulate_return = eval_quant.benchmark_accumulate_returnRate()
        # 超额收益率
        excess_return = accumulate_return - benchmark_accumulate_return
        # 年化收益率
        annualized_return = eval_quant.cagr(strategy_returns)
        # 最大回撤
        max_drawdown = eval_quant.max_drawdown()
        # 胜率
        winRate = eval_quant.win_rate()
        # 年化波动率
        annualized_volatity = eval_quant.ann_volatity(strategy_returns)
        # 夏普比率
        sharp_ratio = eval_quant.ann_sharp()
        # beta beta
        alpha, beta = eval_quant.greeks()
        # 索提诺比率
        sortino_ratio = eval_quant.ann_sortino()
        # 卡玛比率
        calmar_ratio = eval_quant.calmar()
        # 信息比率
        info_ratio = eval_quant.information_ratio()
        # 特雷诺比率
        treynor_ratio = eval_quant.treynor_ratio()
        # 包装所有指标
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
        # 统一保留两位小数
        perf_indcators = {key:np.round(value,2) for key,value in perf_indcators.items()}
        return perf_indcators

    def _position(self):
        # 持仓分析
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
            # 填充缺失值
            date_position.fillna(value={"position": 0, "signal":0,"cum_returns":1}, inplace=True)
            create_performance_signal(date_position, signal_path)
            symbol_signal_path[symbol] = signal_path
            time.sleep(2)
        return symbol_signal_path

    def _pnl(self):
        symbol_return_path = {}
        symbol_return_indcators = {}
        for symbol in self.symbol_list:
            # 1.1 图
            symbol_return_path[symbol] = create_performance_returns(self.strategy_name, symbol, self.symbol_returns[symbol], self.benchmark_price, self.BASE_DIR,self.ann_risk_free)
            # 1.2 指标
            eval_quant = EvalByQuantStats(portfolio_value=self.symbol_portfolio_value[symbol],benchmark_price=self.benchmark_price,ann_risk_free=self.ann_risk_free)
            symbol_return_indcators[symbol]=self._performance_indcators(eval_quant=eval_quant,strategy_returns=eval_quant.returns)
            time.sleep(2)
        return symbol_return_path, symbol_return_indcators