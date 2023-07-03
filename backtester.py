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

# my_strategy = cTrendsStrategy()



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro() # writer=True # stdstats=False
    # Add a strategy
    cerebro.addstrategy(cTrendsStrategy)
    # Create a data feed
    data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2023-05-01', '2023-06-21', interval = "60m"))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50) # DEIXAR MENOS DE 100% PARA NÃO DAR PAU

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())


    # Adiciono na classe analyzer os indicadores de resultado do backtest
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    
    # Run over everything
    strat = cerebro.run()

    # Declaração de variáveis para df com indicadores do backtest 
    periodRsi = strat[0].params.periodRsi
    periodBB  = strat[0].params.periodBB
    stopLoss  = strat[0].params.stopLoss  
    maxDrawDown = strat[0].analyzers.dd.get_analysis()['max']['drawdown']
    sharpeRatio = strat[0].analyzers.sharpe.get_analysis()['sharperatio']
    totalReturn = strat[0].analyzers.returns.get_analysis()['rtot']
    sqn =  strat[0].analyzers.sqn.get_analysis()['sqn'] # Indicador SQN do matemático Tharp
    profitFactor = abs(strat[0].analyzers.trades.get_analysis()['won']['pnl']['total']/strat[0].analyzers.trades.get_analysis()['lost']['pnl']['total']) # Profit Factor
    totalTrades  =  strat[0].analyzers.trades.get_analysis()['total']['closed'] # Número total de trades
    winPercentage = strat[0].analyzers.trades.get_analysis()['won']['total']/strat[0].analyzers.trades.get_analysis()['total']['closed'] # Taxa de acerto
    # Lista dos resultados do backtest
    paramsList = [periodRsi, periodBB, stopLoss, maxDrawDown, sharpeRatio, totalReturn, sqn, profitFactor, totalTrades, winPercentage]
    df = pd.DataFrame(paramsList, columns=['Resultado'],)
    newIndex = ['Periodo RSI','Periodo BB', 'Stop Loss', 'Drawdown %', 'Sharpe Ratio', 'Retorno', 'SQN', 'Profit Factor', 'Total Trades', 'Taxa de acerto']
    df = df.rename(index=lambda x: newIndex[x])
    print(df)
    # print(strat[0].analyzers.trades.get_analysis()) 
    
    cerebro.addobserver(bt.observers.DrawDown)
    
    # Plot cerebro
    fig = cerebro.plot(start=0, end=500)[0][0] # start=50, end=115 Posso colocar indices para olhar alguma data específica

    # Set the desired figure size in inches
    width = 10
    height = 6
    fig.set_size_inches(width, height)

    # Save the figure as a PNG file with the specified size
    fig.savefig('plot.png', dpi=100)  # Adjust the DPI value as needed
    