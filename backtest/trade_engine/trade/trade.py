

from ..Tool.message_queue_sync import QUEUE_NAME
from .base_trade import BaseTrade
from ..Tool import config
from ..Tool.topic import generate_analyse_engine_spot_ma_topic
import uuid

class Trade(BaseTrade):
    def __init__(self,strategy_name,log_path):
        self.receive_routing_key = generate_analyse_engine_spot_ma_topic("OKEX", "BTC-USDC")
        self.receive_queue_name = QUEUE_NAME.SIGNAL_QUEUE_DOUBLE_MA_OKEX_SPOT_BTC_USDT
        self.receive_auto_delete = True
        self.account_key = "2a5b55cb953b4d71a6621910dc799697"
        self.strategy_name = strategy_name
        # self.client = OrderRPCClient(self.account_key)
        self.log_path = log_path
        # self.logger.info(strategy_name)

    # 考虑吃单率和挂单率
    # def excute(self,message):
    #     date = message["close_time_date"]
    #     symbol = message["symbol"]
    #     signal = message["ae_signal"]
    #     signal_old = message["signal_old"]
    #     position_old = message["position_old"]
    #     max_buyable_old = message["max_buyable_old"]
    #     actual_buyable_old = message["actual_buyable_old"]
    #     balance = message["balance"]
    #     close = message["close"]
    #     cash_portion = message["cash_portion"]
    #     take_fee = message["take_fee"]
    #     make_fee = message["make_fee"]
    #     slip_fee = message["slip_fee"]
    #
    #     position = 0  # 记录当前的仓位
    #     signal_new = 0 # 记录TE新产生的信号
    #     max_buyable = 0
    #     actual_buyable = 0
    #     if (signal==1) & (balance > close):
    #         if signal_old<=0:
    #             # 计算可买入的股数，考虑吃单费率
    #             max_buyable = (balance * cash_portion) // (close * (1 + slip_fee))
    #             actual_buyable = int(max_buyable * (1 - take_fee))
    #             position = position_old + actual_buyable
    #             balance -= actual_buyable * close * (1 + slip_fee)  # 更新现金余额，考虑滑点费用
    #             signal_new = 1
    #         elif (signal_old==1) & (position_old < max_buyable_old): # 未达到上次最大买入量则继续买入，前提是策略产生买入信号
    #             actual_buyable = int((max_buyable_old - actual_buyable_old) * (1 - take_fee))
    #             balance -= actual_buyable * close * (1 + slip_fee)  # 更新现金余额，考虑滑点费用
    #             position = position_old + actual_buyable
    #             signal_new = 1
    #         elif (signal_old==1) & (position_old >= max_buyable_old):
    #             position = position_old
    #             signal_new = 0
    #
    #     elif (signal == -1) & (position_old) > 0:  # 未考虑借币做空
    #         # 卖出
    #         position = int(make_fee * position_old)
    #         balance += int(position * (1 - make_fee)) * close * (1 - slip_fee)
    #         signal_new = -1
    #
    #     else:
    #         position = 0
    #         signal_new = 0
    #
    #     client_id = uuid.uuid4().hex
    #     buy_payloads = []
    #     sell_payloads = []
    #     if signal_new==1:
    #         buy_payload = dict(
    #             currency=symbol,
    #             exchange=message["exchange"],
    #             instrument_name=symbol,
    #             delta=0.00001,
    #             side=config.SIDE.BUY,
    #             business_id=f'{self.strategy_name}_buy',
    #             reduce_only=False,
    #             post_only=False,
    #             order_type=config.OrderType.MARKET,
    #             client_id=client_id,
    #             td_mode='cash',
    #             # ccy='USDT',
    #             time_in_force=config.TimeInForce.GTC,
    #             subject=config.SUBJECT_TYPE.SPOT.name,
    #             price=close
    #         )
    #         buy_payloads.append(buy_payload)
    #         # buy_res = self.client.batch_take_order(buy_payloads)
    #         # if buy_res['succeed']:
    #         #     logger.info(f"{self.strategy_name}买入{symbol}成功")
    #         # else:
    #         #     logger.error(f"{self.strategy_name}买入{symbol}失败:[{buy_res}]")
    #     elif signal_new==-1:
    #         sell_payload = dict(
    #             currency=symbol,
    #             exchange=message["exchange"],
    #             instrument_name=symbol,
    #             delta=0.00001,
    #             side=config.SIDE.SELL,
    #             business_id=f'{self.strategy_name}_sell',
    #             reduce_only=False,
    #             post_only=False,
    #             order_type=config.OrderType.MARKET,
    #             client_id=client_id,
    #             td_mode='cash',
    #             # ccy='USDT',
    #             time_in_force=config.TimeInForce.GTC,
    #             subject=config.SUBJECT_TYPE.SPOT.name,
    #             price=close
    #         )
    #         sell_payloads.append(sell_payload)
    #         # sell_res = self.client.batch_take_order(sell_payloads)
    #         # if sell_res['succeed']:
    #         #     logger.info(f"{self.strategy_name}卖出{symbol}成功")
    #         # else:
    #         #     logger.error(f"{self.strategy_name}卖出{symbol}失败:[{sell_res}]")
    #
    #     te_signal = None
    #     if (signal_old == 0) and (signal_new == 1) and (position_old == 0) and (position > 0):
    #         te_signal = 'Going Long'
    #     elif (signal_old == 1) and (signal_new == 1) and (position_old > 0) and (position > 0):
    #         te_signal = 'Opening a Long Position'
    #     elif (signal_old == 0) and (signal_new == -1) and (position_old == 0) and (position > 0):
    #         te_signal = 'Going Short'
    #     elif (signal_new == -1) and (position >= 0):
    #         te_signal = 'Opening a Short Position'
    #     self.logger.info(f"{date} {te_signal} {position} at {close}USDC")
    #
    #     # 更新账户总价值
    #     portfolio_value = balance + position * close
    #     return position, signal_new,balance,portfolio_value,max_buyable, actual_buyable

    def excute(self,message):
        date = message["close_time_date"]
        symbol = message["symbol"]
        ae_signal = message["ae_signal"]
        position = message["position"]
        balance = message["balance"]
        close = message["close"]
        handing_fee = message["handing_fee"]
        slip_fee = message["slip_fee"]
        balance_adjust_ratio = message["balance_adjust_ratio"]

        if balance_adjust_ratio is not None:
            balance *= balance_adjust_ratio
        te_signal = 0 # 记录TE新产生的信号
        te_signal_ = None
        if (ae_signal == 1) & (balance > close * (1 + slip_fee + handing_fee)):
            # 买入
            position = balance// close
            balance -= position * close * (1 + slip_fee + handing_fee)
            te_signal = 1
            te_signal_ = "buy"
        elif (ae_signal == 0) and (position>0):
            te_signal = 0
            te_signal_ = "hold"
        elif ae_signal == -1 and position > 0:
            # 卖出
            balance += position * close * (1-slip_fee-handing_fee)
            position = 0
            te_signal = -1
            te_signal_ = "sell"
        else:
            position=0
            te_signal = 0
            te_signal_ = None

        # 更新账户总价值
        portfolio_value = balance + position * close

        client_id = uuid.uuid4().hex
        buy_payloads = []
        sell_payloads = []
        if te_signal==1:
            buy_payload = dict(
                currency=symbol,
                exchange=message["exchange"],
                instrument_name=symbol,
                delta=0.00001,
                side=config.SIDE.BUY,
                business_id=f'{self.strategy_name}_buy',
                reduce_only=False,
                post_only=False,
                order_type=config.OrderType.MARKET,
                client_id=client_id,
                td_mode='cash',
                # ccy='USDT',
                time_in_force=config.TimeInForce.GTC,
                subject=config.SUBJECT_TYPE.SPOT.name,
                price=close
            )
            buy_payloads.append(buy_payload)
            # buy_res = self.client.batch_take_order(buy_payloads)
            # if buy_res['succeed']:
            #     logger.info(f"{self.strategy_name}买入{symbol}成功")
            # else:
            #     logger.error(f"{self.strategy_name}买入{symbol}失败:[{buy_res}]")
        elif te_signal==-1:
            sell_payload = dict(
                currency=symbol,
                exchange=message["exchange"],
                instrument_name=symbol,
                delta=0.00001,
                side=config.SIDE.SELL,
                business_id=f'{self.strategy_name}_sell',
                reduce_only=False,
                post_only=False,
                order_type=config.OrderType.MARKET,
                client_id=client_id,
                td_mode='cash',
                # ccy='USDT',
                time_in_force=config.TimeInForce.GTC,
                subject=config.SUBJECT_TYPE.SPOT.name,
                price=close
            )
            sell_payloads.append(sell_payload)
            # sell_res = self.client.batch_take_order(sell_payloads)
            # if sell_res['succeed']:
            #     logger.info(f"{self.strategy_name}卖出{symbol}成功")
            # else:
            #     logger.error(f"{self.strategy_name}卖出{symbol}失败:[{sell_res}]")
        log_te_message = f"{date} {symbol} {te_signal_} {position} at {close}USDC"
        self.logger.info(log_te_message)

        return position,te_signal,balance,portfolio_value, log_te_message

    def deal_message(self, message, *args, **kwargs):
        self.log_path = self.log_path
        self.logger = super().log(self.log_path)
        # 根据接收的signal执行下单逻辑
        # self.logger.info(message)
        # if message["strategy_name"] != "MoveAverage":
        #     self.logger.error(f"TE:[{self.strategy_name}]receiver signal wrong")
        #     return
        # 目标币种
        # logger.info("查询余额")
        # balance_data = None
        # obj = {
        #     'exchange': "OKEX",
        #     'subject': config.SUBJECT_TYPE.SPOT.name
        # }
        # auth_res = self.client.init_auth(obj)
        # if str(auth_res["succeed"]) == "False":
        #     logger.error(f"init_auth失败[{auth_res}]")
        #     return
        # if not balance:
        #     param = {
        #         'exchange': message["exchange"],
        #         'subject': config.SUBJECT_TYPE.SPOT.name,
        #     }
        #     logger.info("Te,spot,获取余额")
        #     res = self.client.get_account_summary(param)
        #     logger.info(res)
        #     if res["succeed"]:
        #         balance_data = res["result"]
        #     else:
        #         return
        # usdt_vol = None
        # currency_vol = None
        # if "USDT" in balance_data:
        #     usdt_vol = balance_data["USDT"]["cash_balance"]
        #
        # if currency in balance_data:
        #     currency_vol = balance_data[currency_vol]["cash_balance"]

        position,te_signal,balance,portfolio_value,log_te_message = self.excute(message)
        self.logger.handlers.clear()
        return position,te_signal,balance,portfolio_value, log_te_message




