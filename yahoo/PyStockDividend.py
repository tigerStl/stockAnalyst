import csv
import os
import yfinance as yf
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


class PyStockDividend:
    def __init__(self):
        pass

    def get_dividend_yahoo(self, symbol, yearFrom=None):
        try:
            company = yf.Ticker(symbol)
            dividend_info = company.dividends

            if yearFrom is not None:
                if yearFrom == "$":
                    # Return dividends for a specific year
                    current_year = datetime.datetime.now().year
                    dividend_info = dividend_info[dividend_info.index.year == current_year]
                elif yearFrom >= 2000:
                    # Return dividends from the specified year onwards
                    dividend_info =  dividend_info[dividend_info.index.year >= yearFrom]
                elif yearFrom < 0:
                    # Return dividends from the current year minus yearFrom
                    current_year = datetime.datetime.now().year
                    from_year = current_year + yearFrom
                    dividend_info =  dividend_info[dividend_info.index.year >= from_year]
                else:
                    return "Invalid yearFrom parameter."
            '''
            else:
                # Return all dividend data
                return dividend_info
            '''

        except Exception as e:
            return f"Error fetching dividend information for symbol {symbol} on Yahoo Finance: {str(e)}"

    # ... (other methods)
    def get_stocks_with_high_dividend_yield(self, stock_symbols, min_rate):

        try:
            current_year = datetime.datetime.now().year
            #high_yield_stocks  = pd.DataFrame(columns=["Symbol", "annual yield", "ex date"])
            #stock_symbols = ["AAPL"]

            data_frame = pd.DataFrame(columns=["symbol", "ex-date", "last_price", "industry", "annual_rate"])
            tmp_row = {"symbol":"test"}
            data_frame.loc[len(data_frame)] = tmp_row
            idx = 0
            for symbol in stock_symbols:
                print(f"-----to get {symbol}------")
                try:
                    company = yf.Ticker(symbol)
                    info = company.dividends
                    #industry = company.info.get("industry", "N/A")
                    # get all current years divdends
                    #yf.utils()
                    dividend_info = info[info.index.year == current_year]
                    latest_date = dividend_info.index[-1]
                    dividend_recent_3 = info[info.index.year>current_year-3]
                    df_divident_3 =dividend_recent_3.reset_index()
                    df_divident_3.columns = ["Date", "Value"]
                    df_divident_3["Quarter"] = df_divident_3["Date"].dt.to_period('Q')
                    quarter_list= df_divident_3["Quarter"].tolist()
                    value_list = df_divident_3["Value"].tolist()
                    new_df = pd.DataFrame(columns=quarter_list)
                    new_df.loc[0] = value_list
                    # add symbol
                    new_df["symbol"] = symbol
                    # caculate annual rate
                    fast_info = company.fast_info
                    current_price = fast_info.last_price
                    if current_price != 0:
                        rate = dividend_info.mean()*4/current_price
                    else:
                        rate = -100
                    new_df["last_price"] = current_price
                    new_df["annual_rate"] = rate
                    new_df["latest_date"] = latest_date
                    #new_df["industry"] = industry
                    #new_df["ex-date"] =
                    data_frame = pd.concat([data_frame, new_df], ignore_index=True, sort=False)

                    # if 'trailingAnnualDividendYield' in info:
                    #     dividend_yield_rate = info['trailingAnnualDividendYield']
                    #     if dividend_yield_rate >= min_rate:  # 5% threshold
                    #         ex_date = info.index.strftime('%Y-%m-%d')
                    #         new_row = {"Symbol":symbol, "annual yield":dividend_yield_rate, "ex date": ex_date}
                    #         high_yield_stocks.append(new_row)
                except Exception as e:
                    print(f"Error fetching dividend yield for symbol {symbol}: {str(e)}")
                idx = idx+1

            return data_frame
        except Exception as ex:
            print(f"Exception:{str(ex)}")
            return f"Exception:{str(ex)}"

    def get_symbols_from_csv(self, file_path="..\\data\\SAndP.csv"):
        try:
            data = pd.read_csv(file_path)
            symbols = data['Symbol'].tolist()
            return symbols
        except Exception as e:
            return f"Error reading CSV file: {str(e)}"

    def get_latest_dividend_data(self, symbol, years_back=3):
        try:
            company = yf.Ticker(symbol)
            dividend_info = company.dividends

            if not dividend_info.empty:
                # Sort the dividend data by date
                dividend_info = dividend_info.sort_index(ascending=False)

                # Filter the data for the last three years
                current_year = pd.Timestamp.now().year
                end_year = current_year - 1
                start_year = end_year - years_back + 1

                filtered_dividends = dividend_info.loc[
                    (dividend_info.index >= f"{start_year}-01-01") &
                    (dividend_info.index <= f"{current_year}-12-31")
                ]

                # Create a DataFrame to store the desired information
                data = pd.DataFrame(columns=["Symbol", "Dividend Date", "Dividend Amount", "Dividend Yield Rate"])
                '''should only one row for the table'''
                data["Symbol"] = symbol

                for index in filtered_dividends.index:
                    dividend_date = index
                    quarter = dividend_date.quarter #(dividend_date.quarter + 2) // 3  # Calculate the quarter (1, 2, 3, 4)
                    declare_date_col = f"{index.year}_Q{quarter}_declare_date"
                    record_date_col = f"quarter_{quarter}_record_date"
                    dividend_amount = f"quarter_{quarter}_amount"
                    dividend_year_rate = "f"
                    if record_date_col not in data.columns:
                        data[record_date_col] = ''
                    data[0, record_date_col] = filtered_dividends
                    if declare_date_col not in data.columns:
                        data[declare_date_col] = ''

                    data = data.append({
                        "Dividend Date": dividend_date,
                        "Dividend Amount": filtered_dividends[index],
                        "Dividend Yield Rate": company.info.get("trailingAnnualDividendYield", "N/A")
                    }, ignore_index=True)

                return data
            else:
                return f"No dividend information available for symbol {symbol}."
        except Exception as e:
            return f"Error fetching dividend data for symbol {symbol}: {str(e)}"

    def get_s_and_p_dividend_greater_num(self, num=0.0495):
        all_symbols = self.get_symbols_from_csv()
        data = self.get_stocks_with_high_dividend_yield(all_symbols, num)
        data_dir = '..\\data\\SAndPDividendGreater5.csv'
        data.to_csv(data_dir, index=False)  # Set index to False if you don't want to save the index column
        return data

    def get_S_and_P_symbols(self, save_to_csv=True):
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', {'class': 'wikitable'})
                symbols = []

                for row in table.findAll('tr')[1:]:
                    symbol = row.findAll('td')[0].text.strip()
                    symbols.append(symbol)

                if save_to_csv:
                    data_dir = '..\\data\\'
                    os.makedirs(data_dir, exist_ok=True)

                    with open(os.path.join(data_dir, 'SAndP.csv'), 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(['Symbol'])

                        for symbol in symbols:
                            csv_writer.writerow([symbol])

                return symbols
            else:
                return "Failed to retrieve S&P 500 symbols from Wikipedia."
        except Exception as e:
            return f"Error fetching S&P 500 symbols: {str(e)}"

    def getSAndPDividend(self):
        symbols = self.get_S_and_P_symbols(save_to_csv=True)
        return symbols

if __name__ == '__main__':
    stock_dividend = PyStockDividend()
    #stock_dividend.get_S_and_P_symbols()
    symbol = "AAPL"  # Replace with the symbol of the company you're interested in
    '''
    yearFrom = -3  # Modify this parameter as needed

    dividend_data = stock_dividend.get_dividend_yahoo(symbol, yearFrom)

    if isinstance(dividend_data, str):
        print(dividend_data)
    else:
        print("Dividend Information:")
        print(dividend_data)
    
    s_and_p_symbols = stock_dividend.getSAndPDividend()

    if isinstance(s_and_p_symbols, list):
        print("S&P 500 Symbols:")
        print(s_and_p_symbols)
    else:
        print(s_and_p_symbols)
    

    dividendInfo = stock_dividend.get_dividend_yahoo("USB", -3)
    print(dividendInfo.array)
    print(dividendInfo.index)
    print(dividendInfo.index.strftime)
    
    years_back = 3
    dividend_data = stock_dividend.get_latest_dividend_data("AAPL", years_back)
    if isinstance(dividend_data, pd.DataFrame):
        print(f"Dividend Data for {symbol} (Last {years_back} Years):")
        print(dividend_data)
    else:
        print(dividend_data)
    '''

    all_symbols = stock_dividend.get_s_and_p_dividend_greater_num()
    print("done")
    #data = stock_dividend.get_stocks_with_high_dividend_yield(all_symbols, 0.0495)
    #print(data)
