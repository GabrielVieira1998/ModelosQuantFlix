from utils.optimizer import Optmizer
from utils.backtester import backtester
from strategies.bbwidth import bbwidth
from strategies.trends import Trends_strategy
import yfinance as yf
import pandas as pd
# data_bt = yf.download('BTC-USD', '2022-01-01', '2023-07-30', interval = "60m")
# data_opt = yf.download('BTC-USDT', '2017-08-17', '2023-07-26', interval = "1d")


def load_and_filter_data(csv_file_path, start_date, end_date):
    # Load the CSV file into a DataFrame
    transaction_df = pd.read_csv(csv_file_path, parse_dates=['open_time'])
    
    # Rename columns
    transaction_df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    
    # Set datetime as the index
    transaction_df.set_index('open_time', inplace=True)
    
    # Extract data based on the provided date range
    filtered_data = transaction_df.loc[start_date:end_date].copy()
    
    return filtered_data

csv_file_path = './data/base_BTCUSDT_60m.csv'
data_opt = load_and_filter_data(csv_file_path, '2022-01-01', '2023-08-01')
data_bt = load_and_filter_data(csv_file_path, '2017-08-17', '2023-08-01')



cash = 100000


##
## OTIMIZAÇÕES 
##
optimizerclass = Optmizer(
    strategy = bbwidth, 
    params = dict(
        nQuartile=range(5, 10), 
        periodBB=200,
        tradeReversion=0, 
        tradeTrend=1,
        # multiplicador=range(3,6),
        # stopLoss=1,
        firstLineQuartile=range(0,4),
        secondLineQuartile=range(1,6)
        ), 
    data_bt = data_bt, 
    data_opt = data_opt,
    cash = cash
)

optimizerclass.optmize()

# optimizerclass = Optmizer(
#     strategy = Trends_strategy, 
#     params = dict(
#         # atrPeriod = 63,
#         # atrDist = 3,
#         periodMe1=12,
#         periodMe2=26,
#         periodSignal=9,
#         periodHilo=range(20, 40)
#         # stopLoss = 0.09
#         ), 
#     data_bt = data_bt, 
#     data_opt = data_opt,
#     cash = cash
# )
# optimizerclass.optmize()

##
## BACKTEST
##
# backtester(
#     strategy = Trends_strategy, 
#     params = dict(
#         atrPeriod = 63,
#         atrDist = 90,
#         periodMe1=12,
#         periodMe2=26,
#         periodSignal=9,
#         periodHilo=26
#         # stopLoss = 0.09
#         ), 

#     data = data_bt,
#     cash = cash,
#     generate_report=True)

# backtester(
#     strategy = bbwidth, 
#     params = dict(
#         nQuartile=5, 
#         periodBB=200,
#         tradeReversion=0, 
#         tradeTrend=1,
#         multiplicador=5,
#         stopLoss=1,
#         firstLineQuartile=0,
#         secondLineQuartile=3),
#     data = data_bt,
#     cash = cash,
#     generate_report=True)