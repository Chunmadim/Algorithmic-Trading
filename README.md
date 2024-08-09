# Algorithmic-Trading



### Project Overview Trading bot Momentum Trarading Bot

This project is a momentum-based trading bot designed to trade NVIDIA stocks using the OANDA API. The bot uses a simple moving average 
(SMA) crossover strategy to generate buy and sell signals, with built-in risk management features. The bot is capable of backtesting the 
strategy on historical data and can be deployed for live trading.

### Features

- Momentum Trading Strategy: Implements a momentum-based strategy using moving averages.
- Backtesting: Supports backtesting on historical data using Backtrader.
- Live Trading: Integrates with the OANDA API for live trading.
- Logging and Monitoring: Provides real-time logging and monitoring of trades.


### Prerequisites
- Python 3.7+
- Pip
- OANDA account and API key
- yfinance
- backtrader
- logging

### Strategy Description
The bot implements a simple momentum trading strategy based on the crossover of two moving averages:

SMA 10: Short-term simple moving average.
SMA 50: Long-term simple moving average.
Buy Signal: When SMA 10 crosses above SMA 50 and the difference between them exceeds a certain threshold.

Sell Signal: When SMA 10 crosses below SMA 50.



### BackTesting
For Backtesting I used "backtrader" library.
