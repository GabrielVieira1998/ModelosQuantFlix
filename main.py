from utils.optimizer import Optmizer
from utils.backtester import backtester
from strategies.bbwidth import bbwidth
from strategies.trends import Trends_strategy
import yfinance as yf

data_bt = yf.download('BTC-USD', '2015-01-01', '2023-07-04', interval = "1d")
data_opt = yf.download('BTC-USD', '2021-01-01', '2023-07-04', interval = "1d")

# optimizerclass = Optmizer(
#     strategy = bbwidth, 
#     params = dict(
#         nQuartile=range(5, 8), 
#         periodBB=9,
#         tradeReversion=0, 
#         tradeTrend=1,
#         multiplicador=3,
#         stopLoss=1,
#         firstLineQuartile=0,
#         secondLineQuartile=1
#         ), 
#     data_bt = data_bt, 
#     data_opt = data_opt,
#     cash = 100000
# )
optimizerclass = Optmizer(
    strategy = Trends_strategy, 
    params = dict(
        # atrPeriod = 63,
        # atrDist = 3,
        periodMe1 = 12,
        periodMe2 = 26,
        periodSignal = 9,
        periodHilo = range(20, 40),
        # stopLoss = 0.09
        ), 
    data_bt = data_bt, 
    data_opt = data_opt,
    cash = 100000
)


optimizerclass.optmize()


# backtester(bbwidth, dict(periodMe1=12, 
#         periodMe2=26,
#         periodSignal=9, 
#         periodHilo=20,), data_bt, generate_report=True)