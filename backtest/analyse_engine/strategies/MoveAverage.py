import pandas as pd

from base_strategy import BaseStrategy
from Tool.topic import generate_analyse_engine_spot_ma_topic
import talib as ta
import numpy as np

class MoveAverage(BaseStrategy):
    def __init__(self,log_path=None,strategy_name=None,symbol_list=None):
        super().__init__(receive_routing_key="EXECUTE_ENGINE.SPIDER.OKEX.KLINE_SPOT.KLINE_1H.BTC_USDT",
                         receive_queue_name="SIGNAL_QUEUE_OKEX_SPOT_BTC_USDT", receive_auto_delete=True,
                         send_routing_key=generate_analyse_engine_spot_ma_topic("OKEX", "BTC-USDT"),
                         strategy_name=strategy_name,log_path=log_path)
        # self.send_exchange = MQ_EXCHANGE.SIGNAL_EXCHANGE
        self.klines = {}
        self.inTrade = {}
        for symbol in symbol_list:
            self.klines[symbol]=[]
            self.inTrade[symbol]=False

        self.short_ma_old = None
        self.long_ma_old = None
        self.short_ma_new = None
        self.long_ma_new = None

    def deal_message(self,message, *args, **kwargs):
        maShortLength = 6
        maLongLength = 29
        signal_message = None

        self.klines[message["symbol"]].append(message)
        klines = self.klines[message["symbol"]]

        if len(klines) > maLongLength+1:
            del self.klines[message["symbol"]][0]

        if len(self.klines[message["symbol"]]) == maLongLength+1:
            klines_df = pd.DataFrame(klines)
            ma_shorts = ta.MA(np.array(klines_df["close"]),maShortLength)
            ma_longs = ta.MA(np.array(klines_df["close"]),maLongLength)
            self.short_ma_old = ma_shorts[-2]
            self.short_ma_new = ma_shorts[-1]
            self.long_ma_old = ma_longs[-2]
            self.long_ma_new = ma_longs[-1]
            if self.short_ma_old and self.long_ma_old and self.short_ma_new and self.long_ma_new:
                if self.short_ma_old < self.long_ma_old and self.short_ma_new > self.long_ma_new and not self.inTrade[message["symbol"]]:
                    # 上一根K线的短周期ma再长周期ma下方，当前K线的短周期ma再长周期ma上方，产生金叉
                    self.inTrade[message["symbol"]] = True
                    signal_message = {
                        "symbol":message['symbol'],
                        "signal":1,
                    }
                elif self.short_ma_old > self.long_ma_old and self.short_ma_new < self.long_ma_new and self.inTrade[message["symbol"]]:
                    # 上一根K线的短周期ma在长周期ma上方，当前K线的短周期ma在长周期ma下方，产生死叉，并且有多头的时候才能继续
                    # 此时卖出现货
                    self.inTrade[message["symbol"]] = False
                    signal_message = {
                        "symbol": message['symbol'],
                        "signal": -1,
                    }
                    self.ae_signal =-1
                else:
                    signal_message = {
                            "symbol": message['symbol'],
                            "signal": 0,
                    }
            else:
                signal_message = {
                    "symbol": message['symbol'],
                    "signal": 0,
                }
        else:
            signal_message = {
                "symbol": message['symbol'],
                "signal": 0,
            }
        return signal_message

    def execute_AE_TE(self,ae, te, strategy_name, symbol_list, balance, all_data, exchange, date_range,
                      handing_fee, slip_fee, cal_ae_flag=True,cal_te_flag=True):  # cal_ae_flag :表示是否需要计算ae中的deal_message

        symbol_balance = {}  # 初始化每一个symbol的资金
        symbol_positions = {}  # 初始化每个symbol的te_positions
        symbol_signals = {}  # 初始化每一个symbol的te_signals
        symbol_portfolio_value = {}  # 初始化每一个symbol的te_portfolio_value
        balance_adjust_ratio = {}  # 针对每个symbol的资金占用比例
        for symbol in symbol_list:
            symbol_balance[symbol] = [(1 / len(symbol_list)) * balance,]
            symbol_positions[symbol] = [0,]
            symbol_signals[symbol] = [0,]
            symbol_portfolio_value[symbol] = [(1 / len(symbol_list)) * balance, ]
            balance_adjust_ratio[symbol] = None

        for c_time_date in date_range:
            item = all_data[all_data['close_time_date'] == c_time_date]
            ae_m = []
            for symbol in symbol_list:
                ae_item = item[item["symbol"] == symbol].to_dict(orient='records')[0]
                ae_m.append({
                    "close_time_date": ae_item["close_time_date"],
                    "open": ae_item["open"],
                    "close": ae_item["close"],
                    "high": ae_item["high"],
                    "low": ae_item["low"],
                    "symbol": symbol,
                    "exchange": exchange,
                    "cal_ae_flag": cal_ae_flag,
                })
            # AE发送策略信号
            ae_signal_messages = ae.handle_data(ae_m)

            # TE处理策略信号
            te_m = {}
            for symbol in symbol_list:
                te_item = item[item["symbol"] == symbol].to_dict(orient='records')[0]
                # if symbol_balance[symbol][-1]<100000:
                #     balance_adjust_ratio[symbol] = 0.1  # 中途, 对投资比例的调整
                te_m[symbol]={
                    "close_time_date": te_item["close_time_date"],
                    "close": te_item["close"],
                    "symbol": symbol,
                    "strategy_name": strategy_name,
                    "exchange": exchange,
                    "balance": symbol_balance[symbol][-1],
                    "balance_adjust_ratio": balance_adjust_ratio[symbol],
                    "handing_fee": handing_fee,
                    "slip_fee": slip_fee,
                    "ae_signal": ae_signal_messages[symbol],
                    "position": symbol_positions[symbol][-1],
                    "cal_te_flag":cal_te_flag,
                }
            te_messages, log_te_message = te.handle_data(te_m)

            for symbol in symbol_list:
                symbol_balance[symbol].append(te_messages[symbol]["balance"])
                symbol_positions[symbol].append(te_messages[symbol]["position"])
                symbol_signals[symbol].append(te_messages[symbol]["te_signal"])
                symbol_portfolio_value[symbol].append(te_messages[symbol]["portfolio_value"])

        # 去除初始化的值
        for symbol in symbol_list:
            symbol_balance[symbol] = symbol_balance[symbol][1:]
            symbol_positions[symbol] = symbol_positions[symbol][1:]
            symbol_signals[symbol] = symbol_signals[symbol][1:]
            symbol_portfolio_value[symbol] = symbol_portfolio_value[symbol][1:]

        return symbol_balance, symbol_portfolio_value, symbol_positions, symbol_signals, log_te_message
