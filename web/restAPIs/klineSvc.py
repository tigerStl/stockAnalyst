from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sys

sys.path.append('..\\..')
import nasdaq.PyNasdaq as nsdq

klineSvc = Blueprint('klineSvc', __name__)


@klineSvc.route('/klineSvc/getHistoricalData')
def get_historical_data():
    try:
        symbol = request.args.get('symbol')
        from_date = request.args.get('fromDate')
        to_date = request.args.get('toDate')

        if not all([symbol, from_date, to_date]):
            raise ValueError("Symbol, fromDate, and toDate are required parameters.")

        nsdq_inst = nsdq.NasdaqFStockDivindent()
        historical_data = nsdq_inst.get_k_line(from_date=from_date, to_date=to_date, count=365, symbol=symbol)
        # Generate sample data (replace this with actual data retrieval logic)
        # historical_data = generate_sample_data(symbol, from_date, to_date)
        data_json = historical_data.to_json(orient='records')
        response_data = {
            "result": "SUCCESS",
            "symbol": symbol,
            "rows": data_json
        }

        return jsonify(response_data)

    except Exception as e:
        response_data = {
            "result": "ERROR",
            "error_message": str(e)
        }
        return jsonify(response_data), 400  # Return 400 status code for bad requests
