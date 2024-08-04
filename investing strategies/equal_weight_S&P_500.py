import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import math
import xlsxwriter


#apple = yf.Ticker("AAPL")

stocks = pd.read_csv("sp_500_stocks.csv")
# Get the latest stock price using the history method

#latest_data = apple.history(period="1d")
#latest_price = latest_data['Close'].iloc[0]

#market_cap = apple.info['marketCap']


my_columns=["Ticker","Stock Price","Market Capitalisation","Number of Shares to Buy"]
#final_dataframe = final_dataframe.append(pd.Series(["AAPL",latest_price,market_cap,"N/A"],index=my_columns),ignore_index=True)

def iterate_sp500():
    final_dataframe = pd.DataFrame(columns=my_columns)
    for ticker in stocks["Ticker"]:
        print(ticker)
        company = yf.Ticker(ticker.strip())  # Create a Ticker object for each company
        latest_data = company.history(period="1d")  # Get the latest stock price using the history method
        if not latest_data.empty:  # Check if data is available
            latest_price = latest_data['Close'].iloc[-1]  # Get the latest closing price
            market_cap = company.info.get("marketCap", np.nan)  # Get the market cap, default to NaN if not available
            # Create a new DataFrame for the current row
            new_row = pd.DataFrame([[ticker, latest_price, market_cap, "N/A"]], columns=my_columns)
            # Concatenate the new row to the final DataFrame
            final_dataframe = pd.concat([final_dataframe, new_row], ignore_index=True)

final_dataframe = pd.read_csv("sp500_dataframe.csv")



portfolio_size=int(input("Enter the value of your portfolio: "))

position_size = portfolio_size/len(final_dataframe.index)
for i in range(0,len(final_dataframe.index)):
    price = final_dataframe["Stock Price"].iloc[i]
    print(price)
    number_to_buy= math.floor(position_size/price)
    final_dataframe["Number of Shares to Buy"].iloc[i] = number_to_buy

print(final_dataframe)

writer = pd.ExcelWriter("recommended trades.xlsx", engine ="xlsxwriter")
final_dataframe.to_excel(writer,"Recommended Trades", index = False)

background_colour = "#0a0a23"
font_colour = "ffffff"

string_format = writer.book.add_format({"font_color": font_colour,"bg_color": background_colour,"border":1})
dollar_format = writer.book.add_format({"num_format":"$0.00","font_color": font_colour,"bg_color": background_colour,"border":1})
interger_format = writer.book.add_format({"num_format":"0","font_color": font_colour,"bg_color": background_colour,"border":1})

writer.sheets["Recommended Trades"].write("A1","Ticker",string_format)
writer.sheets["Recommended Trades"].write("B1","Stock Price",string_format)
writer.sheets["Recommended Trades"].write("C1","Market capitalisation",string_format)
writer.sheets["Recommended Trades"].write("D1","Number of Shates to Buy",string_format)

column_formats = {
    "A": ["Ticker",string_format],
    "B": ["Stock Price",dollar_format],
    "C": ["Market Capitalisation",dollar_format],
    "D": ["Number of Shates to Buy",interger_format]
}

for i in column_formats.keys():
    writer.sheets["Recommended Trades"].set_column(f"{i}:{i}",18,column_formats[i][1])

writer.save()