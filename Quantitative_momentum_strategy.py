import numpy as np
import pandas as pd
import math
import yfinance as yf
import xlsxwriter
from statistics import mean
from scipy import stats
from datetime import datetime, timedelta



stocks = pd.read_csv("sp_500_stocks.csv")


#ticker = yf.Ticker("AAPL")
#
#latest_data = ticker.history(period="1y")
#print(latest_data.columns)
#year_ago_price = latest_data["Close"].iloc[0]
#latest_price = latest_data['Close'].iloc[-1]
#
#percetange_return = ((latest_price/ year_ago_price) * 100) -100


my_columns = ["Ticker","Price","1 Year Return","Number of Stocks to Buy"]


final_dataframe= pd.DataFrame(columns=my_columns)


#for i in stocks["Ticker"]:
#    try:
#        company = yf.Ticker(i)
#        data = company.history(period="1y")
#        price = data["Close"].iloc[0]
#        year_ago_price = data["Close"].iloc[-1]
#        percetange_return = ((price/ year_ago_price) * 100) -100
#        new_row = pd.DataFrame([[i, price, percetange_return, "N/A"]], columns=my_columns)
#        final_dataframe = pd.concat([final_dataframe,new_row],ignore_index= True)
#    except:
#        print("Error")
#        continue


#final_dataframe = pd.read_csv("stocks_data.csv")
#final_dataframe.sort_values("1 Year Return",ascending= False,inplace=True)
#final_dataframe = final_dataframe[:50].reset_index()
#
#
#
#def calculate_number_of_shares_to_buy(df):
#    portfolio_price = int(input("Enter portfolio budget:"))
#    budget_per_stock = portfolio_price / len(df["index"])
#    for index in range(0,len(df)):
#        price = df["Price"].iloc[index]
#        number_of_stocks_to_buy = math.floor(budget_per_stock/ price)
#        df[" Number of Stocks to Buy"].iloc[index] = number_of_stocks_to_buy
#    return df 
#
#final_dataframe  = calculate_number_of_shares_to_buy(final_dataframe)




hqm_columns = ["Ticker","Price","Number of Shares to Buy","1 Year Price Return","1 year Percetange Return","6 Month Price Return","6 Month Percentage Return", "3 Month Price Return","3 Month Percentage Return","1 Month Price Return","1 Month Percentage Return"]

hqm_df = pd.DataFrame(columns= hqm_columns)

#for i in stocks["Ticker"]:
#    try:
#        company = yf.Ticker(i)
#        data_1y = company.history(period="1y")
#        data_6m = company.history(period="1y")
#        data_3m = company.history(period="1y")
#        data_1m = company.history(period="1y")
#        print(data_1y)
#        price = data_1y["Close"].iloc[0]
#        year_ago_price = data_1y["Close"].iloc[-1]
#
#        percetange_return = ((price/ year_ago_price) * 100) -100
#        new_row = pd.DataFrame([[i, price, percetange_return, "N/A"]], columns=my_columns)
#        hqm_df = pd.concat([final_dataframe,new_row],ignore_index= True)
#    except:
#        print("Error")
#        continue
#
#

def get_stock_data(tickers, start_date, end_date):
    # Download historical data for the given tickers and date range
    data = yf.download(tickers, start=start_date, end=end_date)
    return data



def calculate_returns(data, current_date):
    # Calculate the required dates
    dates = {
        '1_year': current_date - timedelta(days=365),
        '6_months': current_date - timedelta(days=182),
        '3_months': current_date - timedelta(days=91),
        '1_month': current_date - timedelta(days=30)
    }
    
    # Store the results
    returns = {}

    # Calculate the returns for each ticker
    for ticker in data['Close'].columns:
        current_price = data['Close'][ticker].iloc[-1]  # Latest closing price
        returns[ticker] = {}
        returns[ticker]["Ticker"]= ticker
        returns[ticker]["Price"]=current_price
        returns[ticker]["HQM"] = "N/A"
        returns[ticker]["Number of Shares to Buy"]= "N/A"
        for period, date in dates.items():
            try:
                past_price = data['Close'][ticker].loc[date.strftime('%Y-%m-%d')]
                returns[ticker][period+ "_price"] = ((current_price / past_price) * 100) -100
                returns[ticker][period+ "_%"] = "N/A"
            except KeyError:
                returns[ticker][period] = np.nan

    return pd.DataFrame(returns).T

def batch_process(tickers, batch_size=100):
    # Split tickers into batches
    batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
    all_returns = []

    current_date = datetime.now()
    start_date = current_date - timedelta(days=365)

    for batch in batches:
        print(f"Processing batch: {batch}")
        data = get_stock_data(batch, start_date=start_date.strftime('%Y-%m-%d'), end_date=current_date.strftime('%Y-%m-%d'))
        batch_returns = calculate_returns(data, current_date)
        all_returns.append(batch_returns)

    # Concatenate all the results into a single DataFrame
    final_returns = pd.concat(all_returns)
    return final_returns

# Process all tickers in batches and calculate returns
tickers = list((stocks["Ticker"]))
#final_returns = batch_process(tickers, batch_size=100)
#final_returns.to_csv("Final_returns.csv")
final_returns = pd.read_csv("Final_returns.csv").dropna(subset=["1_year_price","6_months_price","3_months_price","1_month_price"])


del final_returns["Unnamed: 0"]

time_periods = ["1_year","6_months","3_months","1_month"]

for row in final_returns.index:
    for time_period in time_periods:
        final_returns.loc[row,f"{time_period}_%"] = stats.percentileofscore(final_returns[f"{time_period}_price"], final_returns.loc[row,f"{time_period}_price"])
#print(final_returns)



for row in final_returns.index:
    momentum_percitiles = []
    for time_period in time_periods:
        momentum_percitiles.append(final_returns.loc[row,f"{time_period}_%"])
    final_returns.loc[row, "HQM"] = mean(momentum_percitiles)


final_returns.sort_values("HQM",ascending=False,inplace=True)
final_returns = final_returns[:50].reset_index()
del final_returns["index"]
print(final_returns)


#writer = pd.ExcelWriter("momentum_strategy.xlsx",engine=xlsxwriter)
#final_returns.to_excel(writer,sheet_name= "Momentum Strategy",index=False)
#
#string_format = writer.book.add_format({"font_color": font_colour,"bg_color": background_colour,"border":1})
#dollar_format = writer.book.add_format({"num_format":"$0.00","font_color": font_colour,"bg_color": background_colour,"border":1})
#interger_format = writer.book.add_format({"num_format":"0","font_color": font_colour,"bg_color": background_colour,"border":1})
#