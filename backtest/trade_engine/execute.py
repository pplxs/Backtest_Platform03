
from Tool.message_queue_sync import QUEUE_NAME
from Backtest_Platform03.backtest.trade_engine.Tool import config
from Tool.topic import generate_analyse_engine_spot_ma_topic
import logging
import uuid
from Tool.client import OrderRPCClient
logger = logging.getLogger(__name__)


class DoubleMaOkexSpotBtcUsdt(BaseStrategy):
    def __init__(self):
        self.receive_routing_key = generate_analyse_engine_spot_ma_topic("OKEX", "BTC-USDT")
        self.receive_queue_name = QUEUE_NAME.SIGNAL_QUEUE_DOUBLE_MA_OKEX_SPOT_BTC_USDT
        self.receive_auto_delete = True
        self.account_key = "2a5b55cb953b4d71a6621910dc799697"
        self.strategy_name = "DoubleMaOkexSpotBtcUsdt"
        self.client = OrderRPCClient(self.account_key)



    def deal_message(self, message, *args, **kwargs):
        # 根据接收的signal执行下单逻辑
        logger.info(message)
        if message["strategy_name"] != "DoubleMaOkexSpotBtcUsdt":
            logger.error(f"TE:[{self.strategy_name}]接收到的signal错误！接收到的是[{message['strategy_name']}]")
            return
        instrument_name = message["data"]["instrument_name"]
        side = message["data"]["side"]
        # 目标币种
        currency = instrument_name.split("-")[0]
        logger.info("查询余额")
        balance_data = None
        obj = {
            'exchange': "OKEX",
            'subject': config.SUBJECT_TYPE.SPOT.name
        }
        auth_res = self.client.init_auth(obj)
        if str(auth_res["succeed"]) == "False":
            logger.error(f"init_auth失败[{auth_res}]")
            return

        if not balance_data:
            param = {
                'exchange': "OKEX",
                'subject': config.SUBJECT_TYPE.SPOT.name,
            }
            logger.info("Te,spot,获取余额")
            res = self.client.get_account_summary(param)
            logger.info(res)
            if res["succeed"]:
                balance_data = res["result"]
            else:
                return

        usdt_vol = None
        currency_vol = None
        if "USDT" in balance_data:
            usdt_vol = balance_data["USDT"]["cash_balance"]

        if currency in balance_data:
            currency_vol = balance_data[currency_vol]["cash_balance"]

        # 现货买入信号
        if usdt_vol > 0 and side == "buy":
            client_id = uuid.uuid4().hex
            buy_payloads = []
            buy_payload = dict(
                currency=currency,
                exchange="OKEX",
                instrument_name=instrument_name,
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
                price=0
            )
            buy_payloads.append(buy_payload)
            buy_res = self.client.batch_take_order(buy_payloads)
            if buy_res['succeed']:
                logger.info(f"{self.strategy_name}买入{currency}成功")
            else:
                logger.error(f"{self.strategy_name}买入{currency}失败:[{buy_res}]")

        # 现货卖出信号
        if currency_vol > 0 and side == "sell":
            client_id = uuid.uuid4().hex
            sell_payloads = []
            sell_payload = dict(
                currency=currency,
                exchange="OKEX",
                instrument_name=instrument_name,
                delta=currency_vol,
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
                price=0
            )
            sell_payloads.append(sell_payload)
            sell_res = self.client.batch_take_order(sell_payloads)
            if sell_res['succeed']:
                logger.info(f"{self.strategy_name}卖出{currency}成功")
            else:
                logger.error(f"{self.strategy_name}卖出{currency}失败:[{sell_res}]")


if __name__ == '__main__':
    child_1 = DoubleMaOkexSpotBtcUsdt()
    child_1.deal_message("test")
    print(type(child_1).__name__)

    print(child_1.send_exchange)
    child_1.print_value()
    #
    child_1.start()
