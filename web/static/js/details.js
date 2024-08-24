// details.js

//window.onload = function () {
//    // Parse the query string to get the symbol
//    var urlParams = new URLSearchParams(window.location.search);
//    var symbol = urlParams.get('symbol');
//
//    // Get historical data for the symbol
//    getHistoricalData(symbol);
//};
var chart_data = null ;
function getHistoricalData(symbol, domainUrl) {
    var toDate = new Date().toISOString().split('T')[0]; // Today's date
    var fromDate = new Date();
    fromDate.setFullYear(fromDate.getFullYear() - 1);
    fromDate = fromDate.toISOString().split('T')[0]; // One year ago

    // var apiUrl = domainUrl+`/api/quote/${symbol}/historical?assetclass=stocks&fromdate=${fromDate}&limit=1000&todate=${toDate}`;
    var apiUrl = domainUrl+ "klineSvc/getHistoricalData?symbol="+symbol+"&fromDate="+fromDate+"&toDate="+toDate ;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            // Process historical data and generate chart
            var data_as_json = JSON.parse(data.rows) ;
            generateChart(symbol, data_as_json);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function calculateMA(data, period) {
    return data.map((item, index, array) => {
        if (index < period - 1) {
            return null; // Not enough data to calculate MA
        }

        let sum = 0;
        for (let i = 0; i < period; i++) {
            sum += array[index - i][4]; // Closing price for each day
        }

        return sum / period;
    });
}

function convertDateToTimeStamp(dateString){
    var [month, day, year] = dateString.split('/');
    var utcDate = new Date(Date.UTC(year, month - 1, day));
    var utcTimestamp = utcDate.getTime();
    return utcTimestamp;
}

function generateChart(symbol, historicalData) {
    // Implement logic to generate a chart using the historicalData
    // You can use charting libraries like Chart.js, Highcharts, etc.
    // Example using Chart.js:
//    var dates = historicalData.map(entry => entry.date);
//    var closingPrices = historicalData.map(entry => parseFloat(entry.close.replace('$', '').replace(',', '')));

    //var ctx = document.getElementById(`${symbol}_chart`).getContext('2d');
//    Highcharts.setOptions({
//	lang: {
//            rangeSelectorZoom: ''
//        }
//    });

    var ohlc = [],
		volume = [],
		dataLength = historicalData.length,
		// set the allowed units for data grouping
		groupingUnits = [[
			'week',                         // unit name
			[1]                             // allowed multiples
		], [
			'month',
			[1, 2, 3, 4, 6]
		]],
		i = dataLength-1;
    for (i; i >= 0; i -= 1) {
        var dt = convertDateToTimeStamp(historicalData[i].date);
		ohlc.push([
			dt, // the date
			parseFloat(historicalData[i].open.replace(/[$,]/g, '')), // open
			parseFloat(historicalData[i].high.replace(/[$,]/g, '')), // high
			parseFloat(historicalData[i].low.replace(/[$,]/g, '')), // low
			parseFloat(historicalData[i].close.replace(/[$,]/g, '')) // close
		]);
		volume.push([
			dt, // the date
			parseFloat(historicalData[i].volume.replace(/[$,]/g, '')) // the volume
		]);
	}

	// Calculate moving averages for different periods
    var ma5 = calculateMA(ohlc, 5);
    var ma10 = calculateMA(ohlc, 10);
    var ma60 = calculateMA(ohlc, 60);

    var stockChart = Highcharts.stockChart(`${symbol}_chart`, {
        rangeSelector: {
            selected: 1,
            inputDateFormat: '%m/%d/%Y',
            inputEnabled : false
        },
        title: {
            text: `${symbol} Stock Price`
        },
        xAxis: {
			dateTimeLabelFormats: {
				millisecond: '%H:%M:%S.%L',
				second: '%H:%M:%S',
				minute: '%H:%M',
				hour: '%H:%M',
				day: '%m-%d',
				week: '%m-%d',
				month: '%y-%m',
				year: '%Y'
			}
		},
		tooltip: {
			split: false,
			shared: true,
		},
		yAxis: [{
			labels: {
				align: 'right',
				x: -3
			},
			title: {
				text: 'price'
			},
			height: '65%',
			resize: {
				enabled: true
			},
			lineWidth: 2
		}, {
			labels: {
				align: 'right',
				x: -3
			},
			title: {
				text: 'volume'
			},
			top: '65%',
			height: '35%',
			offset: 0,
			lineWidth: 2
		}],
        series: [{
            type: 'candlestick',
            name: `${symbol} Kline`,
            color: 'green',
			lineColor: 'green',
			upColor: 'red',
			upLineColor: 'red',
			tooltip: {
			},
			id: `${symbol}`,
			navigatorOptions: {
				color: Highcharts.getOptions().colors[0]
			},
			data: ohlc,
			dataGrouping: {
				units: [
                    [
                        'week', // unit name
                        [1] // allowed multiples
                    ], [
                        'month',
                        [1, 2, 3, 4, 6]
                    ]
                ]
			    }
			}, {
			    type: 'line',
                name: 'MA(5)',
                data: ma5,
                color: 'red',
                lineWidth: 1
			}
			, {
                type: 'line',
                name: 'MA(10)',
                data: ma10,
                color: 'blue',
                lineWidth: 1,
                dataGrouping: {
                    units: groupingUnits
                }
            }, {
                type: 'line',
                name: 'MA(60)',
                data: ma60,
                color: 'green',
                lineWidth: 1,
                dataGrouping: {
                    units: groupingUnits
                }
            }, {
                type: 'column',
                data: volume,
                yAxis: 1,
                dataGrouping: {
                    units: groupingUnits
                }
		    }
		]
    });
}
