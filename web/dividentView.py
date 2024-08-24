from flask import Flask, render_template, request, Blueprint
import pandas as pd
from flask_cors import CORS
from datetime import datetime, timedelta
import properties.svcConst as const
import sys
from restAPIs.klineSvc import klineSvc

sys.path.append("..")
import nasdaq.PyNasdaq as nsdq

app = Flask(__name__)
CORS(app)
app.register_blueprint(klineSvc)

# Load data from dividend.csv
dividend_data = pd.read_csv('../data/dividend.csv')


@app.route('/index')
@app.route('/')
def index():
    symbols = dividend_data[["Symbol", "dividend_yield_Rate", "dividend_Ex_Date"]]
    # 过滤
    symbols.loc[:, 'dividend_yield_Rate'] = symbols['dividend_yield_Rate'].str.rstrip('%').astype(float)
    symbols = symbols[symbols.dividend_yield_Rate > 5]
    return render_template('index.html', symbols=symbols)


@app.route('/details')
def details():
    symbol = request.args.get('symbol')
    # Assume you have a function to get real-time data from Nasdaq
    # nasdaq_data = get_nasdaq_data(symbol)

    return render_template('details.html', symbol=symbol, current_domain=const.Constants.DOMAIN.value)


def get_nasdaq_data(symbol):
    # Implement the logic to fetch real-time data from Nasdaq for the specified symbol
    # This is a placeholder function; you may need to use an API or other method to get real-time data
    # Return a dictionary with the data you want to display
    # nsdq_historical = nsdq.NasdaqFStockDivindent()
    # to_date = datetime.now()
    # from_date = to_date - timedelta(days=365)
    # data = nsdq_historical.get_kLine(symbol, from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'), 365)

    return {'symbol': symbol, 'current_domain': const.Constants.DOMAIN.value}


if __name__ == '__main__':
    app.run(debug=True)
