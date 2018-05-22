from mooquant_huobi.client.trader import Trader, CoinType

# from liveApi import liveLogger
from mooquant_huobi.livefeed import LiveFeed
from mooquant_huobi.broker import LiveBroker

from mooquant import broker, strategy, logger
from mooquant.bar import Frequency
from mooquant.analyzer import returns
from mooquant.technical import cross, ma

# logger = liveLogger.getLiveLogger("MyStrategy")
logger = logger.getLogger("MyStrategy")

COIN_TYPE = CoinType('ltc', 'usdt')
K_PERIOD = 60
REQ_DELAY = 0

# COIN_TYPE='ltc'


class MyStrategy(strategy.BaseStrategy):
    def __init__(self, feed, instrument, brk):
        super(MyStrategy, self).__init__(feed, brk)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = {}
        self.__sma[60] = ma.SMA(self.__prices, 60)
        self.__sma[10] = ma.SMA(self.__prices, 10)
        self.__sma[30] = ma.SMA(self.__prices, 30)

    def getSMA(self, period):
        return self.__sma[period]

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        logger.info(
            "BUY at $%.2f %.4f" %
            (execInfo.getPrice(), execInfo.getQuantity()))

    def onEnterCanceled(self, position):
        logger.info("onEnterCanceled")
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        logger.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        logger.info("onExitCanceled")
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        bar = bars[self.__instrument]
        if self.getFeed().isHistory():
            return
        if self.__sma[60][-1] is None:
            return
        logger.info(
            "onBars %s:%s: close:%.2f" %
            (self.__instrument,
             bar.getDateTimeLocal(),
             bar.getPrice()))

        bar = bars[self.__instrument]

        # If a position was not opened, check if we should enter a long
        # position.
        if self.__position is None:
            if cross.cross_above(self.__sma[10], self.__sma[30]) > 0:
                mbroker = self.getBroker()
                shares = mbroker.getCash() / bar.getPrice() * 0.9
                self.__position = self.enterLongLimit(
                    self.__instrument, bar.getPrice(), shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__sma[10], self.__sma[30]) > 0:
            self.__position.exitLimit(bar.getPrice())


def run_strategy():
    
    logger.info("-------START-------")
    feed = LiveFeed([COIN_TYPE], Frequency.MINUTE * K_PERIOD, REQ_DELAY)
    
    liveBroker = LiveBroker(COIN_TYPE, Trader(COIN_TYPE))
    myStrategy = MyStrategy(feed, COIN_TYPE, liveBroker)
    myStrategy.run()


run_strategy()