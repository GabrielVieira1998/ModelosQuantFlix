from utils.optimizer import Optmizer
from utils.backtester import backtester
from strategies.bbwidth import bbwidth
from strategies.trends import Trends_strategy
from strategies.monkey_scalper import MonkeyScalper
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



# Define data types to reduce memory consumption
dtypes = {
    'event_time': 'int64'  # Other columns can be added here with appropriate data types
}

# Read in chunks
chunk_size = 1_000_000  # Adjust this based on your system's memory
chunks = []
for chunk in pd.read_csv('./data/BTCBUSD-bookTicker-2023-07.csv', chunksize=chunk_size, dtype=dtypes):
    timestamp = pd.to_datetime(chunk['event_time'], unit='ms')
    chunk.index = pd.DatetimeIndex(timestamp)
    chunk_resampled = chunk.resample('s').last().dropna()
    chunk_resampled = chunk_resampled.ffill()
    chunks.append(chunk_resampled)

# Concatenate chunks
df_seconds = pd.concat(chunks)
df_seconds = df_seconds[df_seconds.index <= '2023-07-08']


data_opt = df_seconds 
data_bt = df_seconds

# # csv_file_path = './data/base_BTCBUSD_tick.csv'
# csv_file_path = './data/base_BTCUSDT_1d.csv'
# data_opt = load_and_filter_data(csv_file_path, '2023-01-01', '2023-08-01')
# data_bt = load_and_filter_data(csv_file_path, '2022-07-05', '2023-07-31')



cash = 100000

##
# ## OTIMIZAÇÕES 

optimizerclass = Optmizer(
    strategy = MonkeyScalper, 
    params = dict(
        bars=range(1,4,1), 
        stop_loss=range(10,50, 10),
        alvo=range(50, 500, 50) 
        ), 
    data_bt = data_bt, 
    data_opt = data_opt,
    cash = cash
)

optimizerclass.optmize()


# backtester(
#     strategy = MonkeyScalper, 
#     params = dict(
#         bars=1,
#         stop_loss=1,
#         alvo=5
#         ), 
#     data = data_bt, 
#     # data_opt = data_opt,
#     cash = cash,
#     generate_report=True
# )





# optimizerclass = Optmizer(
#     strategy = bbwidth, 
#     params = dict(
#         nQuartile=range(5, 10), 
#         periodBB=200,
#         tradeReversion=0, 
#         tradeTrend=1,
#         # multiplicador=range(3,6),
#         # stopLoss=1,
#         firstLineQuartile=range(0,3),
#         secondLineQuartile=range(1,6)
#         ), 
#     data_bt = data_bt, 
#     data_opt = data_opt,
#     cash = cash
# )

# optimizerclass.optmize()

# optimizerclass = Optmizer(
#     strategy = Trends_strategy, 
#     params = dict(
#         # atrPeriod = 63,
#         atrDist = range(100, 900, 50),
#         periodMe1=12,
#         periodMe2=26,
#         periodSignal=9,
#         periodHilo=range(20, 45,5)
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
#         atrDist = 100,
#         periodMe1=12,
#         periodMe2=26,
#         periodSignal=9,
#         periodHilo=20
#         # stopLoss = 0.09
#         ), 

#     data = data_bt,
#     cash = cash,
#     generate_report=True)

# backtester(
#     strategy = bbwidth, 
#     params = dict(
#         nQuartile=7, 
#         periodBB=9,
#         tradeReversion=0, 
#         tradeTrend=1,
#         multiplicador=6,
#         stopLoss=1,
#         firstLineQuartile=0,
#         secondLineQuartile=4),
#     data = data_bt,
#     cash = cash,
#     generate_report=True)