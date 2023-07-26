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
    df = pd.DataFrame([{**sublist[0], **sublist[2]} for sublist in IndicatorsJson])
    
    df_norm = normalizeDf(df[['Drawdown %', 'Net Profit', 'Profit Factor', 'Drawdown %_OS', 'Net Profit_OS', 'Profit Factor_OS', 'Total Trades_OS']]).dropna(axis=1)
    df['quality'] = ((df_norm['Net Profit']*0.3)-(df_norm['Drawdown %']*0.3))+((df_norm['Net Profit_OS']+df_norm['Profit Factor_OS']*0.2)-df_norm['Drawdown %_OS']*2)+df_norm['Total Trades_OS']
    df_sorted = df.sort_values('quality', ascending=False)
    return df_sorted.head()

pbar = tqdm(desc='Opt runs', leave=True, position=1, unit='run', colour='violet')


def callback(strategy):
    
    pbar.update()
    params_dict = {attr: getattr(strategy[0].params, attr) for attr in dir(strategy[0].params) if not callable(getattr(strategy[0].params, attr)) and not attr.startswith("__")}

    strategy.append(backtester(params_dict, data=data_bt, generate_report=False))
    
    return strategy
def optmizer(strategy, params, data_bt, data_opt, cash=100000):
    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=None)


    # Add a strategy
    cerebro.optstrategy(
        strategy, **params
        )
    
     # Create a data feed


    # Add the Data Feed to Cerebro
    cerebro.adddata(data_opt)

    # Set our desired cash start
    cerebro.broker.setcash(cash)
    
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
    param_size = 0
    # Faço um for dentro de toda a lista de resultados da otimização e dou um append na lista que uso para criar o json
    for x in optimizationResults:
        
        analysis0 = x[0].analyzers.trades.get_analysis()
        analysis1 = x[1].analyzers.trades.get_analysis()
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
            param_size = len(x0_dict)
            IndicatorsJson.append([{**x0_dict},{**x1_dict},{
                'Drawdown %': analysers0.dd.get_analysis()['max']['drawdown'],
                'Sharpe Ratio': analysers0.sharpe.get_analysis()['sharperatio'],
                'Net Profit': analysis0['pnl']['net']['total'],
                'SQN': analysers0.sqn.get_analysis()['sqn'],
                'Profit Factor': abs(analysis0['won']['pnl']['total']/analysis0['lost']['pnl']['total']),
                'Total Trades': analysis0['total']['closed'],
                'Taxa de acerto': analysis0['won']['total']/analysis0['total']['closed'],
                'Drawdown %_OS': analysers1.dd.get_analysis()['max']['drawdown'],
                'Sharpe Ratio_OS': analysers1.sharpe.get_analysis()['sharperatio'],
                'Net Profit_OS': analysis1['pnl']['net']['total'],
                'SQN_OS': analysers1.sqn.get_analysis()['sqn'],
                'Profit Factor_OS': abs(analysis1['won']['pnl']['total']/analysis1['lost']['pnl']['total']),
                'Total Trades_OS': analysis1['total']['closed'],
                'Taxa de acerto_OS': analysis1['won']['total']/analysis1['total']['closed']
                }]) 
    # print(IndicatorsJson)
    top_results = get_top_results(IndicatorsJson)
    ###
    print("top results", top_results)
    
    for index, row in top_results.iloc[:, :param_size].astype(int).iterrows():
        backtester(volStrategy, row, data_bt,True)


### Chamada da função optimizer


data_bt = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2014-07-19', '2023-07-04', interval = "1d"))
data_opt = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2021-01-01', '2023-07-04', interval = "1d"))

optmizer(volStrategy, dict(nQuartile=range(5, 11), 
        periodBB=9,
        tradeReversion=0, 
        tradeTrend=1,
        multiplicador=range(1,6),
        stopLoss=1,
        firstLineQuartile=range(0,6),
        secondLineQuartile=range(0,6)), data_bt, data_opt)


# backtester(volStrategy, dict(nQuartile=range(5, 11), 
#         periodBB=9,
#         tradeReversion=0, 
#         tradeTrend=1,
#         multiplicador=range(1,6),
#         stopLoss=1,
#         firstLineQuartile=range(0,6),
#         secondLineQuartile=range(0,6)), data_bt, generate_report=True)


# optmizer(volStrategy, dict(nQuartile=range(5, 6), 
#         periodBB=9,
#         tradeReversion=0, 
#         tradeTrend=1,
#         multiplicador=1,
#         stopLoss=0.01,
#         firstLineQuartile=0,
#         secondLineQuartile=range(1,3)))