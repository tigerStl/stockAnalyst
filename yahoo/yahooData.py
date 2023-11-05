import yfinance as yf
import pandas as pd
import csv
from get_all_tickers import get_tickers as gt

def get_tradable_symbols(exchange='NYSE'):
    if exchange=='NYSE':
        list_of_tickets = gt.get_tickers(NASDAQ=False, AMEX=False)
        print(list_of_tickets)
        return list_of_tickets

'''
def save_symbols_to_csv(symbols, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Symbol'])

        for symbol in symbols:
            csv_writer.writerow([symbol])
'''

if __name__ == '__main__':
    exchange = 'NYSE'
    tradable_symbols = get_tradable_symbols(exchange)

    file_path = r'C:\tiger\finTect\Yahoo\symbols.csv'
'''
    save_symbols_to_csv(tradable_symbols, file_path)
    print(f"Symbols have been saved to {file_path}")
'''