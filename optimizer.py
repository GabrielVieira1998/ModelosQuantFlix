from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.analyzers as btanalyzers
# from utils.backtester import backtester
from tqdm.auto import tqdm
# import datetime
# from strategies import monkey_scalper
# from utils.analyzer import analyze_optimization, get_top_results, consolidate_csvs
import inspect
import pandas as pd
# import matplotlib
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
# matplotlib.use('Agg')
import argparse
from decimal import *
# from utils.analyzer import analyze_backtest
import os
# from pprint import pprint
from collections import OrderedDict
import datetime

def analyze_optimization(x):
    analysis0 = x[0].analyzers.TradeAnalyzer.get_analysis()
    analysis1 = x[1].analyzers.TradeAnalyzer.get_analysis()
    analysers0 = x[0].analyzers
    analysers1 = x[1].analyzers
    if 'pnl' in analysis0 and analysis0['total']['closed'] > 1 and analysis0['won']['pnl']['total'] != 0:
        if analysis0['lost']['pnl']['total'] == 0:
            analysis0['lost']['pnl']['total'] = 1
        elif analysis1['lost']['pnl']['total'] == 0:
            analysis1['lost']['pnl']['total'] = 1
        # print(x[0].analyzers.trades.get_analysis())
        x0_dict = {attr: getattr(x[0].params, attr) for attr in dir(x[0].params) if not callable(getattr(x[0].params, attr)) and not attr.startswith("__")}
        # Alterar '_OS' para minusculo
        x1_dict = {attr+'_OS': getattr(x[1].params, attr) for attr in dir(x[1].params) if not callable(getattr(x[1].params, attr)) and not attr.startswith("__")}
        result = [{**x0_dict},{**x1_dict},{
            'dd_perc': analysers0.DrawDown.get_analysis()['max']['drawdown'],
            'sharpe': analysers0.SharpeRatio.get_analysis()['sharperatio'],
            'pnl_total': analysis0['pnl']['net']['total'],
            'sqn': analysers0.SQN.get_analysis()['sqn'],
            'profit_factor': abs(analysis0['won']['pnl']['total']/analysis0['lost']['pnl']['total']),
            'trades': analysis0['total']['closed'],
            'win_ratio': analysis0['won']['total']/analysis0['total']['closed'],
            'dd_perc_OS': analysers1.DrawDown.get_analysis()['max']['drawdown'],
            'sharpe_OS': analysers1.SharpeRatio.get_analysis()['sharperatio'],
            'pnl_total_OS': analysis1['pnl']['net']['total'],
            'sqn_OS': analysers1.SQN.get_analysis()['sqn'],
            'profit_factor_OS': abs(analysis1['won']['pnl']['total']/analysis1['lost']['pnl']['total']),
            'trades_OS': analysis1['total']['closed'],
            'win_ratio_OS': analysis1['won']['total']/analysis1['total']['closed']
            }]
        
        return result
    
    # print("Condition not met for x[0].params: ", x[0].params)
    # print("Details: 'pnl' in analysis0:", 'pnl' in analysis0, 
    #         "analysis0['total']['closed']:", analysis0['total']['closed'], 
    #         "analysis0['won']['pnl']['total']:", analysis0['won']['pnl']['total'])
    return [{},{},{}]
    


    #return result
def analyze_backtest(x, folder_name, bt_name):
    
    params_dict = {attr: getattr(x[0].params, attr) for attr in dir(x[0].params) if not callable(getattr(x[0].params, attr)) and not attr.startswith("__")}
    merged_dict = {}
    transactions = {}
    
    for a in x[0].analyzers._items:
        if a.__class__.__name__ in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'TradeAnalyzer', 'VWR']:
            analysis = a.get_analysis()
            params_dict.update({a.__class__.__name__: flatten_dict(analysis)})
        else:   
            analysis = a.get_analysis()                        
            transactions.update(flatten_dict(analysis))
        # pprint(dir(a))
        # pprint(dict(analysis))
        # print(type(analysis))
        
    # Determine the directory path
    dir_path = f'./results/{x[0].name}/{folder_name}/{bt_name}'
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    ## Criar dataframe das metrics e retornar dataframe para concatenar todos eles 
    df_metrics = pd.DataFrame(flatten_dict(params_dict), index=['value'])
    
    df_metrics.T.to_csv(f'{dir_path}/metrics.csv', index=True, index_label='metric')
    
    # Create DataFrame using the provided data and structure
    df_transactions = pd.DataFrame(columns=['amount', 'price', 'sid', 'symbol', 'value'])
    # print(transactions.items())
    for date, values_list in transactions.items():
        for value in values_list:
            df_transactions.loc[date] = value

    df_transactions.to_csv(f'{dir_path}/transactions.csv', index=True, index_label='date')
    
    ######
    return df_metrics # None
   

def normalizeDf(df):
    return (df-df.min())/(df.max()-df.min())
    
def get_top_results(IndicatorsJson):
    df = pd.DataFrame([{**sublist[0], **sublist[2]} for sublist in IndicatorsJson])
    
    df_norm = normalizeDf(df[['dd_perc', 'pnl_total', 'profit_factor', 'dd_perc_OS', 'pnl_total_OS', 'profit_factor_OS', 'trades_OS']]).dropna(axis=1)
    df['quality'] = ((df_norm['pnl_total']*0.3)-(df_norm['dd_perc']*0.3))+((df_norm['pnl_total_OS']+df_norm['profit_factor_OS']*0.2)-df_norm['dd_perc_OS']*2)+df_norm['trades_OS']
    df_sorted = df.sort_values('quality', ascending=False)
    return df_sorted.head(10)



def consolidate_csvs(directory_path, output_filename):
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    
    # Read each CSV file into a DataFrame, set filename (without extension) as the index
    dataframes = []
    for csv_file in csv_files:
        df = pd.read_csv(os.path.join(directory_path, csv_file))
        df['filename'] = os.path.splitext(csv_file)[0]  # Get filename without extension
        dataframes.append(df.set_index('filename'))
    
    # Concatenate all the DataFrames
    consolidated_df = pd.concat(dataframes)
    
    # Save the consolidated DataFrame to a new CSV file
    consolidated_df.to_csv(os.path.join(directory_path, output_filename))

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten a nested dictionary structure."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, (dict, OrderedDict)):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

class MonkeyScalper(bt.Strategy):
    params = (
        ('bars', 10),
        # ('onlydaily', False),
        ('stop_loss', 1),
        ('alvo', 1),
    )
    name = 'monkey_scalper'
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # self.sma = btind.SMA(self.data, bars=self.p.bars)
        self.order = None
        self.orderStop = None
        self.position_price = 0
        self.position_direction = 0
        self.barCount = 0


    def start(self):
        self.counter = 0
    
    def prenext(self):
        self.counter += 1
        print('prenext len %d - counter %d' % (len(self), self.counter))
    
           
        
    def direction(self):
        unique_values = []
        direction = 0

        # Ensure that there are enough data points
        if len(self.data0) < self.p.bars:
            return 0

        # Iterate through the tick prices to find unique values
        for i in range(self.p.bars):
            current_value = self.data0.close[-(i + 1)]

            # Skip duplicates and only consider unique values
            if current_value not in unique_values:
                unique_values.append(current_value)

                # Calculate direction based on unique values
                if len(unique_values) > 1:
                    if unique_values[-2] > unique_values[-1]:
                        direction += 1
                    elif unique_values[-2] < unique_values[-1]:
                        direction -= 1

            # Break once we have the last 3 unique values
            if len(unique_values) == self.p.bars:
                break
        unique_values            
        # Return positive or negative based on the direction
        if direction >= 2:
            return 1
        elif direction <= -1:
            return -1

        return 0


    def next(self):
        self.counter += 1
        if self.barCount != len(self):
            
            if self.order:
                return
            
            if len(self.data) < self.p.bars:
                return
            

            
            print('---next len %d - counter %d - data %s' % (len(self), self.counter, self.datas[0].datetime.time(0)))

            position_size = 1
            direction = self.direction()
            price = self.data0.close[0]

            if direction < 0:
                price = self.data0.close[0]
                if self.position.size > 0 and self.position:
                    self.sell_bracket(price=price, stopprice=price+self.p.stop_loss, limitprice=price-self.p.alvo, size=position_size*2, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
                elif not self.position:
                    self.sell_bracket(price=price, stopprice=price+self.p.stop_loss, limitprice=price-self.p.alvo, size=position_size, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)

            else:
                price = self.data0.close[0]
                if self.position.size < 0 and self.position:
                    self.buy_bracket(price=price, stopprice=price-self.p.stop_loss, limitprice=price+self.p.alvo, size=position_size*2, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
                elif not self.position:
                    self.buy_bracket(price=price, stopprice=price-self.p.stop_loss, limitprice=price+self.p.alvo, size=position_size, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
            self.barCount = len(self)
            
def parse_args():
    parser = argparse.ArgumentParser(
        description='Resampling script down to tick data')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--timeframe', default='ticks', required=False,
                        choices=['ticks', 'microseconds', 'seconds',
                                 'minutes', 'daily', 'weekly', 'monthly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=1, required=False, type=int,
                        help=('Compress n bars into 1'))

    return parser.parse_args()


def backtester(strategy, params, data, cash=100000, commission=0, generate_report=False, bt_name='single_run', folder_name=False):
    
    args = parse_args()
    # Create a cerebro entity
    cerebro = bt.Cerebro() # writer=True # stdstats=Falsewriter=False, stdstats=True

    cerebro.addstrategy(strategy, **params)
    
    cerebro.addobserver(bt.observers.Value)
    
    # cerebro.addobserver(bt.observers.LogReturns, timeframe=bt.TimeFrame.Days, compression=1)
    
    feed = bt.feeds.PandasData(dataname=data, datetime=None, open=1, high=1, low=1, close=1, volume=4)
    cerebro.replaydata(feed,
                       timeframe=bt.TimeFrame.Minutes)

    # tframes = dict(
    #     ticks=bt.TimeFrame.Ticks,
    #     microseconds=bt.TimeFrame.MicroSeconds,
    #     seconds=bt.TimeFrame.Seconds,
    #     minutes=bt.TimeFrame.Minutes,
    #     daily=bt.TimeFrame.Days,
    #     weekly=bt.TimeFrame.Weeks,
    #     monthly=bt.TimeFrame.Months)
    
    # data = bt.feeds.GenericCSVData(
    #     dataname='./data/base_BTCBUSD_tick.csv',
    #     dtformat='%Y-%m-%dT%H:%M:%S.%f',
    #     timeframe=bt.TimeFrame.Ticks,
        
    # )
    
    # # Resample the data
    # cerebro.resampledata(
    #     data,
    #     timeframe=tframes['seconds'],
    #     compression=1,
    #     bar2edge=not False, # nobar2edge
    #     adjbartime=not False, # noadjbartime
    #     rightedge=False) # rightedge

    # Add the Data Feed to Cerebro
    # cerebro.adddata(feed)

    cerebro.broker.setcash(cash) # Tenho que aumentar capital nos robôs que dão prejuízo
    # Set the commission
    # cerebro.broker.setcommission(commission=commission)
    cerebro.broker.setcommission(
        commission=0.000027)
    
    # # Print out the starting conditions
    initialDeposit = cerebro.broker.getvalue()
    sizer = (100*(1-commission))
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
    # Adiciono na classe analyzer os indicadores de resultado do backtest
    for name, obj in inspect.getmembers(btanalyzers):
        if inspect.isclass(obj) and name in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'Transactions', 'TradeAnalyzer', 'VWR']:#'TimeReturn','Transactions','PositionsValue', 'LogReturnsRolling', 'GrossLeverage','Calmar',         
            cerebro.addanalyzer(obj, _name=name)
            

    # cerebro.addanalyzer(btanalyzers.PyFolio, _name='pyfolio')
    # Run over everything
    strat = cerebro.run()  

# # #########################################
#     filename = "plot_output.png"
#     temp_fig_path = os.path.join(os.getcwd(), filename)
    
#     figs = cerebro.plot(style='bar', barup='green', bardown='red')
#     fig = figs[0][0]

#     # Adjust the figure size
#     fig.set_size_inches(14, 8)

#     # Save the figure with a defined DPI
#     fig.savefig(temp_fig_path, dpi=300)
# #########################################
    
    
    if generate_report == True:
        
        # fig = cerebro.plot()[0][0] # start=50, end=115 Posso colocar indices para olhar alguma data específica

        # analyzers = strat[0].analyzers
        # analysis = analyzers.trades.get_analysis() 
        # params = strat[0].params   
        # locale.setlocale(locale.LC_ALL, 'en_US.utf8') 
        # getcontext().prec = 2
        
        table_data = analyze_backtest(strat, folder_name, bt_name)
        
        # Determine the directory path
        dir_path = f'./results/{strategy.name}/{folder_name}'

        # Check if the directory exists, if not, create it
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # print("dir_path: ", dir_path, "bt_name: ", bt_name)
        table_data.to_csv(f'{dir_path}/{bt_name}_result.csv', index=False)
        
    
    
    return strat[0]
    



backtesterVar = backtester
# strategy = MonkeyScalper
# strategy
# class Optmizer():


def _callback(strategy):
    
    pbar.update()
    params_dict = {attr: getattr(strategy[0].params, attr) for attr in dir(strategy[0].params) if not callable(getattr(strategy[0].params, attr)) and not attr.startswith("__")}

    strategy.append(backtester(strategy= strategy, params=params_dict, data=data_bt, generate_report=False))
    
    
    return strategy

# def optmize():


# def getBestRuns():
#     results = []
#     formatted_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#     # Faço um for dentro de toda a lista de resultados da otimização e dou um append na lista que uso para criar o json
#     for x in results:
#         result = analyze_optimization(x)
#         if result[0]:  # Check if the first dictionary is not empty
#             results.append(result)
#         # results.append(analyze_optimization(x))
        
    
#     param_size = len(results[0][0])

#     top_results = get_top_results(results)
#     # print(top_results)
#     count = 1
#     for index, params in top_results.iloc[:, :param_size].astype(int).iterrows():
#         backtester(
#             strategy=strategy,
#             params=params,
#             data=data_bt,
#             cash=cash,
#             generate_report=True,
#             bt_name=count,
#             folder_name=formatted_date
#             )
#         count += 1
    
    
#     consolidate_csvs(directory_path=f'./results/{strategy.name}/{formatted_date}', output_filename='consolidated_result.csv')
if __name__ == "__main__":
    
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
    pbar = tqdm(desc='Opt runs', leave=True, position=1, unit='run', colour='violet')
    strategy = MonkeyScalper
    params = dict(
        bars=range(1,4), 
        stop_loss=range(10,50, 10),
        alvo=range(50, 500, 50) 
        )
    data_bt = data_bt
    data_opt = data_opt
    cash = 100000
    results = None
    cerebro = bt.Cerebro(maxcpus=1)

    # Create a cerebro entity

    # feed = bt.feeds.PandasData(dataname=data_opt)
    # # Add the Data Feed to Cerebro
    # cerebro.adddata(feed)

    #  # Add a strategy
    # cerebro.optstrategy(
    #     strategy, **params
    #     )

    # cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
    # Add a strategy
    cerebro.optstrategy(
        MonkeyScalper, **params
        )

    feed = bt.feeds.PandasData(dataname=data_opt, datetime=None, open=1, high=1, low=1, close=1, volume=4)

    # data = cerebro.resampledata(feed,
    #                timeframe=bt.TimeFrame.Seconds)

    cerebro.replaydata(feed,
                timeframe=bt.TimeFrame.Minutes)
    cerebro.broker.setcash(cash) # Tenho que aumentar capital nos robôs que dão prejuízo
    # Set the commission
    # cerebro.broker.setcommission(commission=commission)
    cerebro.broker.setcommission(
        commission=0.00027)
    # Add a FixedSize sizer according to the stake
    # Adiciono na classe analyzer os indicadores de resultado que quero buscar
    for name, obj in inspect.getmembers(btanalyzers):
        if inspect.isclass(obj) and name in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'Transactions', 'TradeAnalyzer', 'VWR']:#'TimeReturn','Transactions','PyFolio','PositionsValue', 'LogReturnsRolling', 'GrossLeverage','Calmar', 
            cerebro.addanalyzer(obj, _name=name)
    # Set the commission
    # cerebro.broker.setcommission(commission=0.0)
    # Variável optimizationResults retorna uma lista de todos os resultados
    cerebro.optcallback(_callback)
    # cerebro.optreturn = False  # If optimization is being used
    results = cerebro.run()     # Force single-core execution
    # getBestRuns()

    results = []
    formatted_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # Faço um for dentro de toda a lista de resultados da otimização e dou um append na lista que uso para criar o json
    for x in results:
        result = analyze_optimization(x)
        if result[0]:  # Check if the first dictionary is not empty
            results.append(result)
        # results.append(analyze_optimization(x))
        
    
    param_size = len(results[0][0])

    top_results = get_top_results(results)
    # print(top_results)
    count = 1
    for index, params in top_results.iloc[:, :param_size].astype(int).iterrows():
        backtester(
            strategy=MonkeyScalper,
            params=params,
            data=data_bt,
            cash=cash,
            generate_report=True,
            bt_name=count,
            folder_name=formatted_date
            )
        count += 1