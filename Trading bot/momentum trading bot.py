import yfinance as yf
import backtrader as bt
import datetime as dt
from secrets_1 import OANDA_API_KEY
from dateutil.relativedelta import relativedelta
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair, Gran, CandleCollector, CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from apscheduler.schedulers.blocking import BlockingScheduler




#end_date = dt.today()
#start_date = lambda: dt.today() - relativedelta(months=2)
#

data = yf.download("NVDA",period="1mo",interval="15m")
num_periods_20 = 50

def get_data_x_days_before(date_string,num_days_before):
    data_object = dt.datatime.strptime(date_string, "%Y-%m-%d")
    new_date= data_object - dt.timedelta(days=num_days_before)
    new_data_string = new_date.strptime("%Y-%m-%d")
    return new_data_string



data["SMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()
data["SMA_50"] = data["Close"].ewm(span=50, adjust=False).mean()



class Momentum_Strategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.ema10 = bt.indicators.EMA(period=10)
        self.ema50 = bt.indicators.EMA(period=50)

    def next(self):
        print(self.datas[0])
        if not self.position:
            if self.ema10 > self.ema50:
                self.log("BUY CREATE, %.2f" )
                #self.notify_trade(self.trade)
                self.buy()
        else:
            if self.ema10 < self.ema50:
                self.log('SELL CREATE, %.2f')
                #self.notify_trade(self.trade)
                self.sell()

        




def signal_generator(df):
    df["Signal"] = 0
    df.loc[df["SMA_10"] > df["SMA_50"],"Signal"] = 1
    df.loc[df["SMA_10"] < df["SMA_50"],"Signal"] = 2



cerebro = bt.Cerebro()
cerebro.addstrategy(Momentum_Strategy)
cerebro.broker.setcash(10000000)

btdata=bt.feeds.PandasData(dataname=data)

cerebro.adddata(btdata)

print(cerebro.broker.getvalue())
cerebro.run()

print(cerebro.broker.getvalue())
