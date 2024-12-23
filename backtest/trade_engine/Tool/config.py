from typing import List



class TimeInForce:
    IOC = 'IOC'
    GTC = 'GTC'
    FOK = 'FOK'


class OrderType:
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    SUPER_MARKET = 'SUPER_MARKET'


class CURRENCY:
    """
    Reference:
    Bybit: https://api.bybit.com/spot/v1/symbols
    """
    BTC = 'BTC'  # 1
    ETH = 'ETH'  # 2
    USDT = 'USDT'  # 3
    USDC = 'USDC'  # 4
    BNB = 'BNB'  # 5

    XRP = "XRP"  # 6
    ADA = "ADA"  # 7
    SOL = "SOL"  # 9
    DOGE = "DOGE"  # 10
    DOT = "DOT"  # 11
    AVAX = "AVAX"  # 12
    MATIC = "MATIC"  # 17
    LTC = "LTC"  # 20
    BCH = "BCH"  # 23
    LINK = "LINK"  # 25
    ALGO = "ALGO"  # 27
    ATOM = "ATOM"  # 28
    ETC = "ETC"  # 30
    SAND = "SAND"  # 40
    EOS = "EOS"  # 44
    CAKE = "CAKE"  # 47
    LUNA = "LUNA"  # Soon to be removed
    KCS = "KCS"


class SIDE:
    BUY = 1
    SELL = -1

class ID_TYPE:
    UID = "UID"
    BID = "BID"  # vpos个人id
    GID = "GID"  # vpos组id
    SBID = "SBID"  # SUPER BOOK ID


class PrefixObject:
    def __init__(self, name: str, prefix: int):
        """ name:名称 prefix 前缀 """
        self.name = name
        self.prefix = prefix

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __call__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other


class SUBJECT_TYPE:
    SPOT = PrefixObject('SPOT', 10)
    SWAP_USD = PrefixObject('SWAP_USD', 20)
    SWAP_USDT = PrefixObject('SWAP_USDT', 30)
    FUTURE_USD = PrefixObject('FUTURE_USD', 40)
    FUTURE_USDT = PrefixObject('FUTURE_USDT', 50)
    FUTURE_USDC = PrefixObject('FUTURE_USDC', 51)  # 系统暂未支持，仅做类型匹配
    OPTION = PrefixObject('OPTION', 60)  # OPTION_USD
    OPTION_USDC = PrefixObject('OPTION_USDC', 61)
    OPTION_USDT = PrefixObject('OPTION_USDT', 62)
    SWAP_USDC = PrefixObject('SWAP_USDC', 70)
    MARGIN = PrefixObject('MARGIN', 80)  # 币币杠杆

    INSTRUMENT_SPOT = PrefixObject('INSTRUMENT_SPOT', 90)
    INSTRUMENT_SWAP_USD = PrefixObject('INSTRUMENT_SWAP_USD', 91)
    INSTRUMENT_SWAP_USDT = PrefixObject('INSTRUMENT_SWAP_USDT', 92)
    INSTRUMENT_FUTURE_USD = PrefixObject('INSTRUMENT_FUTURE_USD', 93)
    INSTRUMENT_FUTURE_USDT = PrefixObject('INSTRUMENT_FUTURE_USDT', 94)
    INSTRUMENT_OPTION = PrefixObject('INSTRUMENT_OPTION', 95)
    INSTRUMENT_SWAP_USDC = PrefixObject('INSTRUMENT_OPTION', 96)

    @classmethod
    def subjects_with_ttl(cls) -> List[str]:
        return [cls.OPTION.name, cls.FUTURE_USD.name, cls.FUTURE_USDT.name]

    @classmethod
    def str_to_cls_map(cls):
        return {value.name: value for value in cls.__dict__.values() if isinstance(value, PrefixObject)}

    @classmethod
    def from_str(cls, name):
        return cls.str_to_cls_map().get(name)

    @classmethod
    def option(cls) -> List[str]:
        return [cls.OPTION.name, cls.OPTION_USDC.name, cls.OPTION_USDT.name]

    @classmethod
    def swap(cls) -> List[str]:
        return [cls.SWAP_USD.name, cls.SWAP_USDC.name, cls.SWAP_USDT.name]

    @classmethod
    def future(cls) -> List[str]:
        return [cls.FUTURE_USD.name, cls.FUTURE_USDT.name]

    @classmethod
    def inverses(cls) -> List[str]:
        """币本位合约"""
        return [cls.FUTURE_USD.name, cls.SWAP_USD.name, cls.OPTION.name]

    @classmethod
    def expiration_date(cls) -> List[str]:
        """有到期日的subject"""
        return [cls.OPTION.name, cls.OPTION_USDC.name, cls.FUTURE_USDT.name, cls.FUTURE_USD.name]