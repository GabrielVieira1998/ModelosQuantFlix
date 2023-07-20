from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import yfinance as yf
# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
import json
from backtester import backtester
from Vol import volStrategy
from tqdm.auto import tqdm
import itertools
import uuid
import pandas as pd

def normalizeDf(df):
        return (df-df.min())/(df.max()-df.min())
    # replace this with the path to your JSON file

def get_top_results(IndicatorsJson):
    df = pd.DataFrame(IndicatorsJson)
    df_norm = normalizeDf(df[['Drawdown %', 'Net Profit', 'Profit Factor', 'Drawdown %_OS', 'Net Profit_OS', 'Profit Factor_OS', 'Total Trades_OS']]).dropna(axis=1)
    df['quality'] = ((df_norm['Net Profit']*0.3)-(df_norm['Drawdown %']*0.3))+((df_norm['Net Profit_OS']+df_norm['Profit Factor_OS']*0.2)-df_norm['Drawdown %_OS']*2)+df_norm['Total Trades_OS']
    df_sorted = df.sort_values('quality', ascending=False)
    return df_sorted.head()

pbar = tqdm(desc='Opt runs', leave=True, position=1, unit='run', colour='violet')
data_bt = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2014-07-19', '2023-07-04', interval = "1d"))
data_opt = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2021-01-01', '2023-07-04', interval = "1d"))

def callback(strategy):
    
    pbar.update()
    strategy.append(backtester(dict(
        nQuartile=strategy[0].params.nQuartile,
        firstLineQuartile=strategy[0].params.firstLineQuartile,
        secondLineQuartile=strategy[0].params.secondLineQuartile,
        tradeReversion=strategy[0].params.tradeReversion,
        tradeTrend=strategy[0].params.tradeTrend,
        stopLoss=strategy[0].params.stopLoss,
        multiplicador=strategy[0].params.multiplicador,
        periodBB=strategy[0].params.periodBB), data_bt,False))
    
    return strategy

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=None)


    # Add a strategy
    cerebro.optstrategy(
        volStrategy,
        nQuartile=7,# range(5, 11) 
        periodBB=9,
        tradeReversion=0, 
        tradeTrend=1,
        multiplicador=3, # range(1,6)
        stopLoss=0.01,
        firstLineQuartile=range(0,3), # range(0,6)
        secondLineQuartile=range(3,6) # range(0,6)
        )
    
     # Create a data feed


    # Add the Data Feed to Cerebro
    cerebro.adddata(data_opt)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    
    # Add a FixedSize sizer according to the stake
    # Adiciono na classe analyzer os indicadores de resultado que quero buscar

    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    # Set the commission
    cerebro.broker.setcommission(commission=0.0)
    
    # Variável optimizationResults retorna uma lista de todos os resultados
    cerebro.optcallback(callback)
    # opt_count = len(list(itertools.product(*cerebro.strats)))
    # print(f"Total steps {opt_count}")
    optimizationResults = cerebro.run()
    
    ###
    
    IndicatorsJson = []
    
    # Faço um for dentro de toda a lista de resultados da otimização e dou um append na lista que uso para criar o json
    for x in optimizationResults:
        
        
        if (x[0].params.tradeReversion > 0 or x[0].params.tradeTrend > 0) and (x[0].params.firstLineQuartile < x[0].params.secondLineQuartile) and 'pnl' in x[0].analyzers.trades.get_analysis() and x[0].analyzers.trades.get_analysis()['total']['closed'] > 1:
            # print(x[0].analyzers.trades.get_analysis())
            IndicatorsJson.append({
                'Periodo BB': x[0].params.periodBB,
                'nQuartile': x[0].params.nQuartile,
                'firstQuartile': x[0].params.firstLineQuartile,
                'secondQuartile':x[0].params.secondLineQuartile,
                'Opera reversao': x[0].params.tradeReversion,
                'Opera tendencia': x[0].params.tradeTrend,
                'Multiplicador': x[0].params.multiplicador,
                'Stop Loss': x[0].params.stopLoss,
                'Drawdown %': x[0].analyzers.dd.get_analysis()['max']['drawdown'],
                'Sharpe Ratio': x[0].analyzers.sharpe.get_analysis()['sharperatio'],
                'Net Profit': x[0].analyzers.trades.get_analysis()['pnl']['net']['total'],
                'SQN': x[0].analyzers.sqn.get_analysis()['sqn'],
                'Profit Factor': abs(x[0].analyzers.trades.get_analysis()['won']['pnl']['total']/x[0].analyzers.trades.get_analysis()['lost']['pnl']['total']),
                'Total Trades': x[0].analyzers.trades.get_analysis()['total']['closed'],
                'Taxa de acerto': x[0].analyzers.trades.get_analysis()['won']['total']/x[0].analyzers.trades.get_analysis()['total']['closed'],
                'Periodo BB_OS':x[1].params.periodBB, 
                'nQuartile_OS': x[1].params.nQuartile,
                'firstQuartile_OS': x[1].params.firstLineQuartile,
                'secondQuartile_OS':x[1].params.secondLineQuartile,
                'Opera reversao_OS': x[1].params.tradeReversion,
                'Opera tendencia_OS': x[1].params.tradeTrend,
                'Stop Loss': x[1].params.stopLoss,
                'Multiplicador_OS': x[1].params.multiplicador,
                'Drawdown %_OS': x[1].analyzers.dd.get_analysis()['max']['drawdown'],
                'Sharpe Ratio_OS': x[1].analyzers.sharpe.get_analysis()['sharperatio'],
                'Net Profit_OS': x[1].analyzers.trades.get_analysis()['pnl']['net']['total'],
                'SQN_OS': x[1].analyzers.sqn.get_analysis()['sqn'],
                'Profit Factor_OS': abs(x[1].analyzers.trades.get_analysis()['won']['pnl']['total']/x[1].analyzers.trades.get_analysis()['lost']['pnl']['total']),
                'Total Trades_OS': x[1].analyzers.trades.get_analysis()['total']['closed'],
                'Taxa de acerto_OS': x[1].analyzers.trades.get_analysis()['won']['total']/x[1].analyzers.trades.get_analysis()['total']['closed']
                }) 
    
    top_results = get_top_results(IndicatorsJson)
    ###
    print("top results", top_results)
    for index, row in top_results.iterrows():
        
        backtester(dict(
            nQuartile=int(row['nQuartile']),
            firstLineQuartile=int(row['firstQuartile']),
            secondLineQuartile=int(row['secondQuartile']),
            tradeReversion=int(row['Opera reversao']),
            tradeTrend=int(row['Opera tendencia']),
            stopLoss=float(row['Stop Loss']),
            multiplicador=int(row['Multiplicador']),
            periodBB=int(row['Periodo BB'])), data_bt,True)



