from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Import the backtrader platform
import backtrader.analyzers as btanalyzers
import backtrader as bt
import pandas as pd
# Importando classe da estratégia cTrends
from cTrends import cTrendsStrategy
from Trends import trendsStrategy
from Vol import volStrategy
import argparse
import json
import uuid

def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--timeframe', default='daily', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=2, required=False, type=int,
                        help='Compress n bars into 1')
    

    return parser.parse_args()

def backtester(params, data):
    
    args = parse_args()
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=True) # writer=True # stdstats=Falsewriter=False, stdstats=True
    #
    cerebro.addobserver(bt.observers.Value)
    
    cerebro.addobserver(bt.observers.LogReturns, timeframe=bt.TimeFrame.Days, compression=1)
    # Add a strategy
    
    cerebro.addstrategy(volStrategy, **params)
    # Create a data feed
    # yf_data = get_timeframe(dataname=yf.download('BTC-USD', '2023-01-01', '2023-06-21', interval = "1d"), 2)
    # data = bt.feeds.GenericCSVData(dataname='BTC_Hourly.csv',fromdate=datetime.datetime(2020, 1, 1),todate=datetime.datetime(2022, 1, 1),datetime=1,open=3,high=4,low=5,close=6,volume=7,openinterest=8)

    
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    # ##Handy dictionary for the argument timeframe conversion
    # tframes = dict(
    #     daily=bt.TimeFrame.Days,
    #     weekly=bt.TimeFrame.Weeks,
    #     monthly=bt.TimeFrame.Months)

    # # Add the resample data instead of the original
    # cerebro.resampledata(dataname=data,
    #                      timeframe=tframes[args.timeframe],
    #                      compression=args.compression)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0) # Tenho que aumentar capital nos robôs que dão prejuízo
    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    initialDeposit = cerebro.broker.getvalue()

    # Adiciono na classe analyzer os indicadores de resultado do backtest
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    
    # Run over everything
    strat = cerebro.run()
    backtestResults = []

    # Declaração de variáveis para df com indicadores do backtest 
    
    # netProfit = strat[0].analyzers.trades.get_analysis()['pnl']['net']['total']   
    # maxDrawDown = strat[0].analyzers.dd.get_analysis()['max']['drawdown']
    # moneyDrawdown = strat[0].analyzers.dd.get_analysis()['max']['moneydown']
    # sharpeRatio = strat[0].analyzers.sharpe.get_analysis()['sharperatio']
    # totalReturn = (netProfit/initialDeposit)
    # sqn =  strat[0].analyzers.sqn.get_analysis()['sqn'] # Indicador SQN do matemático Tharp (Fórmula: SquareRoot(NumberTrades) * Average(TradesProfit) / StdDev(TradesProfit))
    # profitFactor = abs(strat[0].analyzers.trades.get_analysis()['won']['pnl']['total']/strat[0].analyzers.trades.get_analysis()['lost']['pnl']['total']) # Profit Factor
    # totalTrades  =  strat[0].analyzers.trades.get_analysis()['total']['closed'] # Número total de trades
    # winPercentage = strat[0].analyzers.trades.get_analysis()['won']['total']/strat[0].analyzers.trades.get_analysis()['total']['closed'] # Taxa de acerto
    # longTradeWinPercentage = strat[0].analyzers.trades.get_analysis()['long']['won']/strat[0].analyzers.trades.get_analysis()['long']['total']
    # shortTradeWinPercentage = strat[0].analyzers.trades.get_analysis()['short']['won']/strat[0].analyzers.trades.get_analysis()['short']['total']
    # totalLongTrades = strat[0].analyzers.trades.get_analysis()['long']['total']
    # totalShortTrades = strat[0].analyzers.trades.get_analysis()['short']['total']
    # largestProfitTrade = strat[0].analyzers.trades.get_analysis()['won']['pnl']['max']
    # largestLossTrade = strat[0].analyzers.trades.get_analysis()['lost']['pnl']['max']
    # averageProfitTrade = strat[0].analyzers.trades.get_analysis()['won']['pnl']['average']    
    # averageLossTrade = strat[0].analyzers.trades.get_analysis()['lost']['pnl']['average']

    return strat[0]
    
    # userId = str(uuid.uuid4())
    
    # json_path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/volStrategy/'+userId+'_'+'backtest_metrics.json'
    # fig_path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/volStrategy/'+userId+'_'+'plot.png'
    # # Lista dos resultados do backtest
    # with open(json_path , 'x') as json_file:
    #         json.dump(backtestResults, json_file)

    # # Plot cerebro
    # fig = cerebro.plot()[0][0] # start=50, end=115 Posso colocar indices para olhar alguma data específica

    # # Set the desired figure size in inches
    # width = 16
    # height = 9
    # fig.set_size_inches(width, height)

    # # Save the figure as a PNG file with the specified size
    # fig.savefig(fig_path, dpi=300)  # Adjust the DPI value as needed
    
# if __name__ == '__main__':
#     params = dict( 
#     periodBB= 200,
#     tradeReversion= 0,
#     tradeTrend= 1,        
#     nQuartile= 6,
#     firstLineQuartile= 3,
#     secondLineQuartile= 10,
#     multiplicador= 6,
#     stopLoss= 0.01
#     )
#     backtester(params)
    