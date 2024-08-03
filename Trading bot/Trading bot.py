import pandas as pd
import yfinance as yf
from secrets_1 import OANDA_API_KEY
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair, Gran, CandleCollector, CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from apscheduler.schedulers.blocking import BlockingScheduler

dataF = yf.download("EURUSD=X",start="2024-06-03",end="2024-08-01",interval="15m")
dataF.iloc[-1:,:]


#print(dataF)



def signal_generator(df):
    open = df.Open.iloc[-1]
    close = df.Close.iloc[-1]
    previous_open = df.Open.iloc[-2]
    previous_close=df.Close.iloc[-2]

    if (open>close and previous_open<previous_close and close<previous_open and open>=previous_close):
        return 1
    
    elif (open<close and previous_open>previous_close and close>previous_open and open<=previous_close):
        return 2
    else:
        return 0
    
#signal = []
#signal.append(0)
#for i in range(1,len(dataF)):
#    df = dataF[i-1:i+1]
#    signal.append(signal_generator(df))
#dataF["signal"] = signal
#print(dataF)


def get_candles(n):
    client = CandleClient(OANDA_API_KEY, real=False)
    collector = client.get_collector(Pair.EUR_USD,Gran.M15)
    candles=collector.grab(n)
    return candles

candles = get_candles(3)


def trading_job():
    candles = get_candles(3)
    dfstream = pd.DataFrame(columns=['Open','Close','High','Low'])
    
    i=0
    for candle in candles:
        dfstream.loc[i, ['Open']] = float(str(candle.bid.o))
        dfstream.loc[i, ['Close']] = float(str(candle.bid.c))
        dfstream.loc[i, ['High']] = float(str(candle.bid.h))
        dfstream.loc[i, ['Low']] = float(str(candle.bid.l))
        i=i+1

    dfstream['Open'] = dfstream['Open'].astype(float)
    dfstream['Close'] = dfstream['Close'].astype(float)
    dfstream['High'] = dfstream['High'].astype(float)
    dfstream['Low'] = dfstream['Low'].astype(float)

    signal = signal_generator(dfstream.iloc[:-1,:])#
    
    # EXECUTING ORDERS
    #accountID = "XXXXXXX" #your account ID here
    client = API(OANDA_API_KEY)
         
    SLTPRatio = 2.
    previous_candleR = abs(dfstream['High'].iloc[-2]-dfstream['Low'].iloc[-2])
    
    SLBuy = float(str(candle.bid.o))-previous_candleR
    SLSell = float(str(candle.bid.o))+previous_candleR

    TPBuy = float(str(candle.bid.o))+previous_candleR*SLTPRatio
    TPSell = float(str(candle.bid.o))-previous_candleR*SLTPRatio
    
    print(dfstream.iloc[:-1,:])
    print(TPBuy, "  ", SLBuy, "  ", TPSell, "  ", SLSell)
    #Sell
    if signal == 1:
        mo = MarketOrderRequest(instrument="EUR_USD", units=-10000, takeProfitOnFill=TakeProfitDetails(price=TPSell).data, stopLossOnFill=StopLossDetails(price=SLSell).data)
        r = orders.OrderCreate("101-004-29608007-001", data=mo.data)
        rv = client.request(r)
        print(rv)
    #Buy
    elif signal == 2:
        mo = MarketOrderRequest(instrument="EUR_USD", units=10000, takeProfitOnFill=TakeProfitDetails(price=TPBuy).data, stopLossOnFill=StopLossDetails(price=SLBuy).data)
        r = orders.OrderCreate("101-004-29608007-001", data=mo.data)
        rv = client.request(r)
        print(rv)





trading_job()

scheduler = BlockingScheduler()
scheduler.add_job(trading_job, 'cron', day_of_week='mon-fri', hour='00-23', minute='1,16,31,46', start_date='2024-08-01 02:30:00', timezone='Europe/London')
scheduler.start()