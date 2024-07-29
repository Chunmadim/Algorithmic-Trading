import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

ticker = ["AMZN","TSLA","META","GOOG","MSFT","SONY","NVDA","AMD","ARM","TSM","INTC","NFLX","F","GM","LCID","RIVN","NIO","GC=F","LLOY.L"]

#stocks = yf.download(ticker,start="2014-01-01",end="2024-07-29")
#stocks = stocks.to_csv("stocks_data.csv")

stocks= pd.read_csv("stocks_data.csv",header =[0,1],index_col=[0],parse_dates=[0])
close = stocks.loc[:,"Close"].copy()
close = close.pct_change()
mean_and_std = close.describe().T.loc[:,["mean","std"]]
mean_and_std["mean"] *=252
mean_and_std["std"] *= np.sqrt(252)
print(mean_and_std)
mean_and_std.plot.scatter(x="std",figsize=(12,8),y="mean",s=50)
for i in mean_and_std.index:
    plt.annotate(i,xy=(mean_and_std.loc[i,"std"]+0.002, mean_and_std.loc[i,"mean"]+0.002))
plt.xlabel("Annual risk(std)",fontsize=15)
plt.ylabel("Annual return(mean)",fontsize=15)

sns.set(font_scale=1)
sns.heatmap(close.corr(),cmap="Reds",annot=True,annot_kws={"size":4},vmax=0.5)
plt.show()