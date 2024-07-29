import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
#apple = yf.download("AAPL", start = "2010-01-01",end="2021-01-01")
#
#ticker = ["SPY","AAPL","KO"]
#
#stocks = yf.download(ticker,start= "2010-01-01",end = "2021-01-01")
#stocks.to_csv("stocks_data.csv")


stocks = pd.read_csv("stocks_data.csv",header=[0,1],index_col=[0],parse_dates=[0])
#stocks.columns=stocks.columns.to_flat_index()
#stocks.columns=pd.MultiIndex.from_tuples(stocks.columns)

close = stocks.loc[:,"Close"].copy()
plt.style.use("seaborn-v0_8")
#close.plot(figsize=(15,8),fontsize=12)
#plt.show()

#print(close.iloc[0])
norm_close = close.div(close.iloc[0]).mul(100)
#norm_close.plot(figsize=(15,8),fontsize=12)
#plt.show()


apple = close.AAPL.copy().to_frame()
#apple["lag1"] =apple.shift()
#apple["diff"] = apple.AAPL.sub(apple.lag1)
#apple["percentage_chagnge"] = apple.AAPL.div(apple.lag1)
#apple["diff2"] = apple.AAPL.diff(periods=1)
#apple["% change"] = apple.AAPL.pct_change(periods=1).mul(100)
#del apple["diff"]
#apple.rename(columns={"% change":"Change"}, inplace = True)
#apple.AAPL.resample("M").last()
#print(apple.AAPL.resample("BM").last().pct_change(periods=1).mul(100))

#ret = apple.pct_change().dropna()
#ret.plot(kind="hist",figsize = (12,8),bins=100)
#plt.show()
#ret_mean = ret.mean()
#ret_var = ret.mean()
#std_ret = ret.std()

#annual_mean_ret=ret_mean * 252
#annual_var_ret = ret_var *252
#annual_std_ret = std_ret *252
#


ticker = ["SPY","AAPL","KO","IBM","DIS","MSFT"]
stocks = yf.download(ticker,start= "2010-01-01",end = "2021-01-01")
stocks.to_csv("stocks_data.csv")


stocks = pd.read_csv("stocks_data.csv",header=[0,1],index_col=[0],parse_dates=[0])

close = stocks.loc[:,"Close"].copy()
norm_close = close.div(close.iloc[0]).mul(100)
#norm_close.plot(figsize=(15,8),fontsize=12)
plt.style.use("seaborn-v0_8")
#plt.show()
ret = close.pct_change().dropna()
#ret = ret.describe().T.loc[:,["mean","std"]]
#ret["mean"] *= 252
#ret["std"] *= np.sqrt(252)
##ret.plot.scatter(x="std",y="mean",figsize=(12,8),s=50,fontsize =15,)
#
#
#
#
#
#
#

# covariance
#print(ret.cov())
#correlation
#print(ret.corr())

sns.set(font_scale=1.4)
sns.heatmap(ret.cov(),cmap="Reds",annot=True,annot_kws={"size":15},vmax=0.001)
plt.show()