# Importing Tick-by-Tick Data from Binance
1. Access the link: [Binance Data](https://www.binance.com/en/landing/data)
2. Navigate to 'Book Ticker'.
3. Select 'USDⓢ-M'.
4. Enter the desired symbol within 'Symbol (Max: 5)'.
5. Choose the interval type.
6. Select the period.
7. Download the file and place it in the 'data' folder in CSV format.

# Optimization
To run an optimization, simply call the 'Optimizer' function within 'main.py' and define the parameter ranges you want to optimize.

# Backtest
To run a backtest, call the 'backtester' function within 'main.py' and define the parameters you want to optimize.

# Reminder
I am filtering the amount of data used for optimization (1 week) within 'main.py' because my machine couldn't handle the entire dataset for running tests.
