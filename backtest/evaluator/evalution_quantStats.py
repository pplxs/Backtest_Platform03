# -*- coding: utf-8 -*-
import pandas as pd
import quantstats as qs

# 查看完整的指标
# indicators = [f for f in dir(qs.stats) if f[0] != '_']
# print(indicators)

# 查看绘图函数
# plot_functions = [f for f in dir(qs.plots) if f[0] != '_']
# print(plot_functions)
class EvalByQuantStats:
    def __init__(self,portfolio_value:pd.Series,benchmark_price:pd.Series=None,ann_risk_free=0.03):
        """
        :param portfolio_value: portfolio_value.index is Datetime
        :param risk_free: annualized return
        :param benchmark_price: benchmark_price.index is Datetime
        """
        self.benchmark_price = benchmark_price
        self.portfolio_value = portfolio_value
        self.ann_risk_free = ann_risk_free
        self.start()

        if self.benchmark_price is not None:
            self.benchmark_returns = self.cal_returns(self.benchmark_price)
            self.benchmark_cum_returns = self.cal_cum_returns(self.benchmark_returns)

        self.returns = self.cal_returns(self.portfolio_value)
        self.cum_returns = self.cal_cum_returns(self.returns)

    def start(self):
        # extend pandas functionality with metrics, etc.
        qs.extend_pandas()

    def start_term_asset(self):
        # 期初资产
        start_asset = self.portfolio_value.iloc[0]
        return start_asset

    def end_term_asset(self):
        # 期末资产
        end_asset = self.portfolio_value.iloc[-1]
        return end_asset

    def accumulated_pnl(self):
        # 累计盈亏
        start_asset = self.start_term_asset()
        end_asset = self.end_term_asset()
        return end_asset - start_asset

    def accumulate_returnRate(self):
        # 累计收益率
        start_asset = self.start_term_asset()
        end_asset = self.end_term_asset()
        return end_asset/start_asset - 1

    def benchmark_accumulate_returnRate(self):
        # 基准的累计收益率
        start_price = self.benchmark_price.iloc[0]
        end_price = self.benchmark_price.iloc[-1]
        return end_price/start_price - 1

    def excess_returnRate(self):
        # 超额收益率
        return self.accumulate_returnRate() - self.benchmark_accumulate_returnRate()

    def cal_returns(self, prices):
        return qs.utils._prepare_returns(prices)

    def cal_cum_returns(self,returns):
        return qs.stats.compsum(returns)

    def cagr(self,returns):
        # 年化收益率
        cagr_ratio = qs.stats.cagr(returns,compounded=True, periods=365)
        return cagr_ratio

    def ann_sharp(self):
        # 年化夏普比率
        ann_sharp_ratio = qs.stats.sharpe(self.returns,rf=self.ann_risk_free, periods=365, annualize=True, smart=False)
        return ann_sharp_ratio

    def max_drawdown(self):
        # 最大回撤
        max_dd = qs.stats.max_drawdown(self.returns)
        return max_dd

    def rolling_drawdown(self,returns):
        rolling_dd = qs.stats.to_drawdown_series(returns)
        return rolling_dd


    def ann_sortino(self):
        # 索提诺比率
        sortino_ratio = qs.stats.sortino(self.returns,rf=self.ann_risk_free, periods=365, annualize=True, smart=False)
        return sortino_ratio

    def calmar(self):
        # 卡玛比率
        # calmar_ratio = qs.stats.calmar(self.returns,prepare_returns=True)  # periods = 252, 暂时不使用

        cagr_ratio = self.cagr(self.returns)
        max_dd = self.max_drawdown()
        return cagr_ratio / abs(max_dd)

    def information_ratio(self):
        # 信息比率
        info_ratio = qs.stats.information_ratio(self.returns,self.benchmark_returns,prepare_returns=False)
        return info_ratio

    def treynor_ratio(self):
        # 特雷诺比率
        trey_ratio = qs.stats.treynor_ratio(self.returns, self.benchmark_price, periods=365, rf=self.ann_risk_free)
        return trey_ratio

    def greeks(self):
        # alpha and beta
        greeks_series = qs.stats.greeks(self.returns, self.benchmark_price, periods=365, prepare_returns=False)
        return greeks_series["alpha"], greeks_series["beta"]

    def win_rate(self):
        # 胜率
        winRate = qs.stats.win_rate(self.returns, aggregate=None, compounded=True, prepare_returns=False)
        return winRate

    def ann_volatity(self,returns):
        vol = qs.stats.volatility(returns, periods=365, annualize=True)
        return vol




