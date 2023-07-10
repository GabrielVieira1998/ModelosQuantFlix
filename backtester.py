from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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

# my_strategy = cTrendsStrategy()

# def get_timeframe(data, desired):
#     print(data)
#     data = data.to_dict(orient="tight")
#     new_data = pd.DataFrame()
#     for i in range(0,len(data['index']),desired):
#         if i == len(data['index'])-1:
#             continue
#         datetime = data['index'][i]
#         close = data['data'][i+(desired-1)][3]
#         open = data['data'][i][0]
#         high = max(data['data'][i+(desired-1)][1], data['data'][i][1])
#         low = min(data['data'][i+(desired-1)][2], data['data'][i][2])
#         adj_close = data['data'][i+(desired-1)][4]
#         volume = data['data'][i+(desired-1)][5] + data['data'][i][5]
#         append_data = pd.DataFrame([[open, high, low, close, adj_close, volume]], index=[datetime], columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
#         append_data.index.name = 'Date'
#         new_data = pd.concat([new_data, append_data])
#     print(new_data)
#     return new_data

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

if __name__ == '__main__':
    
    args = parse_args()
    # Create a cerebro entity
    cerebro = bt.Cerebro(writer=True) # writer=True # stdstats=Falsewriter=False, stdstats=True
    #
    cerebro.addobserver(bt.observers.Value)
    # Add a strategy
    cerebro.addstrategy(volStrategy)
    # Create a data feed
    # yf_data = get_timeframe(dataname=yf.download('BTC-USD', '2023-01-01', '2023-06-21', interval = "1d"), 2)
    data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2022-11-05', '2023-07-04', interval = "60m"))
    
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
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=30)# PercentSizer # DEIXAR MENOS DE 100% PARA NÃO DAR PAU
    #
    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    initialDeposit = cerebro.broker.getvalue()

    # Adiciono na classe analyzer os indicadores de resultado do backtest
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    
    # Run over everything
    strat = cerebro.run()
    # print(strat[0].analyzers.trades.get_analysis())
    # # print(strat[0].analyzers.sqn.get_analysis())
    # # Declaração de variáveis para df com indicadores do backtest 
    # # periodRsi = strat[0].params.periodRsi
    # # periodBB  = strat[0].params.periodBB
    # # stopLoss  = strat[0].params.stopLoss
    # print("Initial Deposit: ", initialDeposit)
    # netProfit = strat[0].analyzers.trades.get_analysis()['pnl']['net']['total']   
    # maxDrawDown = strat[0].analyzers.dd.get_analysis()['max']['drawdown']
    # moneyDrawdown = strat[0].analyzers.dd.get_analysis()['max']['moneydown']
    # sharpeRatio = strat[0].analyzers.sharpe.get_analysis()['sharperatio']
    # totalReturn = strat[0].analyzers.returns.get_analysis()['rtot']
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


    # # Lista dos resultados do backtest
    # # paramsList = [periodRsi, periodBB, stopLoss, maxDrawDown, sharpeRatio, totalReturn, sqn, profitFactor, totalTrades, winPercentage]
    # # paramsList = [periodBB, stopLoss, maxDrawDown, sharpeRatio, totalReturn, sqn, profitFactor, totalTrades, winPercentage]
    # paramsList = [initialDeposit,netProfit, maxDrawDown, moneyDrawdown, sharpeRatio, totalReturn, sqn, profitFactor, totalTrades, winPercentage, largestProfitTrade, largestLossTrade, averageProfitTrade, averageLossTrade,totalLongTrades, longTradeWinPercentage, totalShortTrades, shortTradeWinPercentage]
    
    
    # df = pd.DataFrame(paramsList, columns=['Resultado'])
    # # newIndex = ['Periodo RSI','Periodo BB', 'Stop Loss', 'Drawdown %', 'Sharpe Ratio', 'Retorno', 'SQN', 'Profit Factor', 'Total Trades', 'Taxa de acerto']
    # # newIndex = ['Periodo BB', 'Stop Loss', 'Drawdown %', 'Sharpe Ratio', 'Retorno', 'SQN', 'Profit Factor', 'Total Trades', 'Taxa de acerto']
    # newIndex = ['Initial Deposit', 'Net Profit', 'Drawdown %', 'Drawdown $', 'Sharpe Ratio', 'Retorno', 'SQN', 'Profit Factor', 'Total Trades','Taxa de acerto', 'Maior lucro','Maior perda','Lucro médio','Perda média','Total Long Trades', 'Taxa de acerto compra', 'Total Short Trades', 'Taxa de acerto venda']
    
    # df = df.rename(index=lambda x: newIndex[x])
    # print(df)
    # # Gerando CSV dos resultados
    # pd.DataFrame.to_csv(df, 'resultado_backtest.csv')
    # # print(strat[0].analyzers.returns.get_analysis()) 

    
    
    
    # Plot cerebro
    fig = cerebro.plot()[0][0] # start=50, end=115 Posso colocar indices para olhar alguma data específica

    # Set the desired figure size in inches
    width = 16
    height = 9
    fig.set_size_inches(width, height)

    # Save the figure as a PNG file with the specified size
    fig.savefig('plot.png', dpi=300)  # Adjust the DPI value as needed
    