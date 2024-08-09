
import yfinance as yf
import backtrader as bt 


data = yf.download("NVDA",period="1mo",interval="15m")
class Momentum_Strategy(bt.Strategy):
    params = (
        ('exitbars', 5),
    )


    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.ema10 = bt.indicators.EMA(period=10)
        self.ema50 = bt.indicators.EMA(period=50)

        self.order = None
        self.buyprice = None
        self.buycomm = None


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f , Comm: %.2f' % (order.executed.price,order.executed.value,order.executed.comm))


            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f , Comm: %.2f' % (order.executed.price,order.executed.value,order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Regected]:
            self.log("Order Canceled/Margin/Regected")

        self.order = None



    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log("OPERATION PROFIT, GROSS %.2f , NET %.2f" % (trade.pnl, trade.pnlcomm) )





    def next(self):
        if self.order:
            return

        if not self.position:
            if self.ema10 > self.ema50:
                self.log(f"BUY CREATE, %.2f" % self.data.close[0])
                #self.notify_trade(self.trade)
                self.order = self.buy()

        else:
            if self.ema10 < self.ema50 and len(self) >= (self.bar_executed + self.params.exitbars):
                self.log(f'SELL CREATE, %.2f' % self.data.close[0])
                #self.notify_trade(self.trade)
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(Momentum_Strategy)
cerebro.broker.setcash(10000000)
cerebro.broker.setcommission(commission=0.001)
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
btdata=bt.feeds.PandasData(dataname=data)

cerebro.adddata(btdata)

print(cerebro.broker.getvalue())
cerebro.run()

print(cerebro.broker.getvalue())

