import csv
import os
import yfinance as yf
import datetime
import requests
from bs4 import BeautifulSoup


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
                    return dividend_info[dividend_info.index.year == current_year]
                elif yearFrom >= 2000:
                    # Return dividends from the specified year onwards
                    return dividend_info[dividend_info.index.year >= yearFrom]
                elif yearFrom < 0:
                    # Return dividends from the current year minus yearFrom
                    current_year = datetime.datetime.now().year
                    from_year = current_year + yearFrom
                    return dividend_info[dividend_info.index.year >= from_year]
                else:
                    return "Invalid yearFrom parameter."
            else:
                # Return all dividend data
                return dividend_info
        except Exception as e:
            return f"Error fetching dividend information for symbol {symbol} on Yahoo Finance: {str(e)}"

    # ... (other methods)

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
    '''
    symbol = "AAPL"  # Replace with the symbol of the company you're interested in
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
    '''
    dividendInfo = stock_dividend.get_dividend_yahoo("USB", -3)
    print(dividendInfo.array)
    print(dividendInfo.index)
    print(dividendInfo.index.strftime)
