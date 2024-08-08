import yfinance as yf

import datetime as dt
from secrets_1 import OANDA_API_KEY
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


logging.basicConfig(filename='trading_bot.log', level=logging.INFO)

logging.info('Started monitoring positions')

api = API(access_token="50696cace808324b42df9e5ef936f522-72c6ad111ebde7484ea21b5188784bdd")
accountID = "101-004-29608007-001"
r = accounts.AccountDetails(accountID)
rv = api.request(r)
account_balance = rv["account"]["balance"]
risk_per_trade = round(0.01 * float(account_balance))
print(risk_per_trade)


data = yf.download("EUR_USD",period="1mo",interval="15m")
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
    df.loc[df["SMA_10"] > df["SMA_50"],"Signal"] = 1
    df.loc[df["SMA_10"] < df["SMA_50"],"Signal"] = 2




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
    print(f"Order placed: {r.response}")



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
        return "buy"
    elif signal_generator(data)== 2:
        return "sell"
    else:
        None


def close_postion():
    units = -1000
    trade_close_data = {
        "units": str(units)  # OANDA requires units to be a string
    }
    trade_id = get_open_positions()["positions"][0]["long"]["tradeIDs"][0]

    r = trades.TradeClose(account_id=accountID, tradeID=trade_id, data=data)
    try:
        api.request(r)
        print(f"Position closed: {r.response}")
    except Exception as e:
        print(f"Error closing NVIDIA position: {e}")

def get_open_positions():
    r = positions.OpenPositions(accountID)
    api.request(r)
    return r.response

def trade():
    signal = check_trading_signal()
    print("ADADAS")
    if signal == "buy":
        place_market_order("EUR_USD", risk_per_trade, "1.0900", "1.1000")
    elif signal == "sell":
        close_postion()
    else:
        print("No trade signal")


def run_bot():
    while True:
        print("run_not")
        monitor_position()



run_bot()