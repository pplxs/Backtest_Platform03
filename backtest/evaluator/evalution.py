import numpy as np
import pandas as pd
class Evaluation:
    def __init__(self, portfolio_value:pd.Series(),position:pd.Series(),signal=None,risk_free=0.03 / 100):
        self.portfolio_value = portfolio_value
        self.risk_free = risk_free
        self.position = position
        if signal is None:
            self.signal = pd.Series(np.zeros_like(portfolio_value))
        else:
            self.signal = signal
        self.df = pd.DataFrame()
        self.df["portfolio_value"] = portfolio_value
        self.df["position"] = position
        self.df["signal"] = signal

    def eval_returns(self):
        # returns = self.data['close']*self.position.shift(1)
        # returns[returns<0] = -returns[returns<0] # 平仓的收益
        # self.returns = pd.DataFrame(np.where(returns!=0,returns.diff()/returns,0))
        # self.returns.fillna(0,inplace=True)
        # self.returns.replace(1,0,inplace=True)
        # cum_returns = (self.returns+1).cumprod()
        # self.returns = self.returns[0]

        self.returns = self.portfolio_value.pct_change()
        cum_returns = (self.returns + 1).cumprod()

        return self.returns, list(cum_returns.values.flatten())

    def sharp_ratio(self):
        mean_returns = np.mean(self.returns)
        std_returns = np.std(self.returns)
        return (mean_returns-self.risk_free)/std_returns

    def sortino_ratio(self):
        mean_returns = np.mean(self.returns)
        std_down_returns =np.std(self.returns[self.returns<self.risk_free])
        return (mean_returns - self.risk_free) / std_down_returns

    def max_drawdown(self, len_time=None):
        self.returns, _ = self.eval_returns()
        len_time = len(self.returns)
        if self.returns.empty:
            return 0

        max_drawdown = 0.0
        running_max = float('-inf')
        running_drawdown = 0.0

        for return_value in self.returns:
            if return_value > running_max:
                running_max = return_value

            if running_max!=0:
                current_drawdown = (running_max - return_value) / running_max
                if current_drawdown > max_drawdown:
                    max_drawdown = current_drawdown

        return -max_drawdown

    def win_rate(self,total_position_closed=None,win_position_closed=None):
        """
        胜率
        :param total_position_closed: 总平仓次数
        :param win_position_closed: 平仓盈利次数
        :return:
        """
        returns,_ = self.eval_returns()
        self.df["returns"] = returns
        if total_position_closed is None and win_position_closed is None:
            total_position_closed = sum(self.signal==-1)
            win_position_closed=self.df.loc[(self.df["returns"]>0) & (self.df["signal"]==-1)].shape[0]
        if total_position_closed !=0:
            winRate = win_position_closed/total_position_closed
        else:winRate= 0
        return winRate,total_position_closed,win_position_closed
