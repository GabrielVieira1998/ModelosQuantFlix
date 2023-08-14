from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib
import matplotlib.pyplot as plt

plt.switch_backend('Agg')

# matplotlib.use('Agg')
# Import the backtrader platform
import backtrader.analyzers as btanalyzers
import backtrader as bt
import argparse
import inspect
from decimal import *
from utils.analyzer import analyze_backtest

import os
import datetime
import tempfile


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
    