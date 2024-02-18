// details.js

window.onload = function () {
    // Parse the query string to get the symbol
    var urlParams = new URLSearchParams(window.location.search);
    var symbol = urlParams.get('symbol');

    // Get historical data for the symbol
    getHistoricalData(symbol);
};

function getHistoricalData(symbol) {
    var toDate = new Date().toISOString().split('T')[0]; // Today's date
    var fromDate = new Date();
    fromDate.setFullYear(fromDate.getFullYear() - 1);
    fromDate = fromDate.toISOString().split('T')[0]; // One year ago

    var apiUrl = `https://api.nasdaq.com/api/quote/${symbol}/historical?assetclass=stocks&fromdate=${fromDate}&limit=1000&todate=${toDate}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            // Process historical data and generate chart
            generateChart(data.data.tradesTable.rows);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function generateChart(historicalData) {
    // Implement logic to generate a chart using the historicalData
    // You can use charting libraries like Chart.js, Highcharts, etc.
    // Example using Chart.js:
    var dates = historicalData.map(entry => entry.date);
    var closingPrices = historicalData.map(entry => parseFloat(entry.close.replace('$', '').replace(',', '')));

    var ctx = document.getElementById('chartContainer').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Closing Prices',
                data: closingPrices,
                borderColor: 'blue',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
            // Add more options as needed
        }
    });
}
