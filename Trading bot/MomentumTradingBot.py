import yfinance as yf
import datetime as dt
from secrets_1 import OANDA_API_KEY,ACCOUNTID

from dateutil.relativedelta import relativedelta
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair, Gran, CandleCollector, CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from apscheduler.schedulers.blocking import BlockingScheduler
import oandapyV20.endpoints.trades as trades#
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import logging
import oandapyV20.endpoints.instruments as instruments
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')


api = API(access_token=OANDA_API_KEY)
accountID = ACCOUNTID
r = accounts.AccountDetails(accountID)
rv = api.request(r)
account_balance = rv["account"]["balance"]
risk_per_trade = round(0.01 * float(account_balance))


data = yf.download("EURUSD=X",period="1mo",interval="15m")
num_periods_20 = 50

def get_data_x_days_before(date_string,num_days_before):
    data_object = dt.datatime.strptime(date_string, "%Y-%m-%d")
    new_date= data_object - dt.timedelta(days=num_days_before)
    new_data_string = new_date.strptime("%Y-%m-%d")
    return new_data_string



data["SMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()
data["SMA_50"] = data["Close"].ewm(span=50, adjust=False).mean()





def signal_generator(df):
    df["Signal"] = 0
    df.loc[(df["SMA_10"] > df["SMA_50"]) & ((df["SMA_10"] - df["SMA_50"]) > 0.001), "Signal"] = 1
    df.loc[(df["SMA_10"] < df["SMA_50"]) & ((df["SMA_50"] - df["SMA_10"]) > 0.001), "Signal"] = 2
    
    return df["Signal"].iloc[-1]





def calculate_position_size(self, entry_price, stop_loss_price):
    # Calculate the difference between the entry and stop-loss price
    stop_loss_amount = entry_price - stop_loss_price
    
    # Determine position size based on the risk per trade
    position_size = self.risk_per_trade / stop_loss_amount
    
    return position_size





def calculate_take_profit(self, entry_price, reward_to_risk_ratio):
    take_profit_price = entry_price + (self.stop_loss_amount * reward_to_risk_ratio)
    return take_profit_price



def place_market_order(instrument,units,stop_loss_price,take_profit_price):
    order_data = {
        "order": {
            "units":units,
            "instrument": instrument,
            "timeInForce": "FOK",
            "type":"MARKET",
            "positionFill":"DEFAULT",

        }
        }
    r = orders.OrderCreate(accountID,data=order_data)
    api.request(r)
    logging.info(f"Placing market order for {instrument}")



def get_account_summary():
    r = accounts.AccountDetails(accountID)
    api.request(r)
    return r.response


def monitor_position():
    while True:
        summary = get_account_summary()
        logging.info(f"Balance: {summary['account']['balance']}")
        logging.info(f"Unrealized P/L: {summary['account']['unrealizedPL']}")
        trade()
        time.sleep(15 * 60)  # Wait for 1 minute before checking again



def check_trading_signal():
    r=instruments.InstrumentsCandles(instrument="EUR_USD", params={"granularity": "M1", "count": 1})
    api.request(r)
    candle = r.response['candles'][0]
    if signal_generator(data) == 1:
        logging.info("Strating to buy position")
        return "buy"
    elif signal_generator(data)== 2:
        logging.info("Starting to sell position")
        return "sell"
    else:
        logging.info("No Trades Performed")
        None


def close_postion():
    units = -1000
    trade_close_data = {
        "units": str(units)  # OANDA requires units to be a string
    }
    trade_id = get_open_positions()["positions"][0]["long"]["tradeIDs"][0]

    r = trades.TradeClose(accountID,trade_id, data)
    try:
        api.request(r)
        logging.info(f"Position closed: {r.response}")
    except Exception as e:
        logging.error(f"Error closing position: {e}")

def get_open_positions():
    r = positions.OpenPositions(accountID)
    api.request(r)
    return r.response

def trade():
    signal = check_trading_signal()
    if signal == "buy":
        place_market_order("EUR_USD", risk_per_trade, "1.0900", "1.1000")
    elif signal == "sell":
        close_postion()
    else:
        logging.info("No trade signal")


def run_bot():
    while True:
        logging.info("Start of The code")
        monitor_position()

run_bot()
