import time
import traceback
from datetime import datetime

import pytz

from mooquant.utils import dt
from mooquant import logger

localTz = pytz.timezone('Asia/Shanghai')
logger = logger.getLogger("huobi.common")

def timestamp():
    return int(time.time())


def utcnow():
    return dt.as_utc(datetime.utcnow())


def timestamp_to_DateTimeLocal(timestamp):
    return datetime.fromtimestamp(timestamp, localTz)


def localTime():
    return timestamp_to_DateTimeLocal(timestamp())


def utcToLocal(utcDatetime):
    return timestamp_to_DateTimeLocal(dt.datetime_to_timestamp(utcDatetime))


def RoundDown(f, n):
    r = round(f, n)
    return r if r <= f else r - (10**-n)


def PriceRound(price):
    return RoundDown(price, 2)


def CoinRound(coin):
    return RoundDown(coin, 4)


def tryForever(func):
    def forever(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning('traceback:{}'.format(traceback.format_exc()))
                logger.warning('{} => {}'.format(func.__name__, e))
                
                time.sleep(1)
                continue
    
    return forever
