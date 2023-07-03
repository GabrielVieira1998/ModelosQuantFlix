from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import yfinance as yf
# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd

# Create a Stratey
class cTrendsStrategy(bt.Strategy):
    params = (
        ('periodRsi', 4),
        ('periodBB', 200),
        ('stopLoss', 0.02),
        ('printlog', False)
    )

    def __init__(self):
        
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyPrice = None
        self.buyComm = None
        self.orderStop = None

        self.bb = bt.indicators.BollingerBands(self.datas[0], period=self.params.periodBB)
        self.rsi = bt.indicators.RSI(self.datas[0], period=self.params.periodRsi)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        
        self.exitType = ''
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        # if order.status in [order.Completed]:
        #     if order.isbuy():
        #         self.buyComm = order.executed.comm
        #     # else:  # Sell
        #     self.bar_executed = len(self)
        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        # self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
        #          (trade.pnl, trade.pnlComm))
        
        pnl = trade.pnl
        pnlComm = trade.pnlComm
        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        if self.exitType == '':
            self.exitType = 'StopLoss' if pnl < 0 else 'SelfClose'

        #self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlComm))
        
        if self.exitType == 'SelfClose':
            self.broker.cancel(self.orderStop)


    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
         # Check if we are in the market
        if self.position:

            if (self.rsi[0] >= 70) and (self.dataclose[0] >= self.bb.top[0]) and (self.position.size > 0): 
                # Keep track of the created order to avoid a 2nd order
                self.order = self.close()

            elif (self.rsi[0] <= 30) and (self.dataclose[0] <= self.bb.bot[0]) and (self.position.size < 0):# 

                # Keep track of the created order to avoid a 2nd order
                self.order = self.close()
        else:            
             # Not yet ... we MIGHT BUY if ...
            if (self.rsi[0] <= 30) and (self.dataclose[0] <= self.bb.bot[0]):# 
                # BUY, BUY, BUY!!! (with all possible default parameters)
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
                self.orderStop = self.sell(price=self.data.close[0] * (1 - (self.params.stopLoss*0.01)), exectype=bt.Order.Stop)
                # stopPrice = self.data.close[0] * (1 - self.params.stopLoss*0.01)
                # takeProfitPrice = self.data.close[0] * (1 + self.params.stopLoss*0.01)
                # self.order = self.buy(exectype=bt.Order.Stop, price=self.data.close[0], stopprice=stopPrice)#, limitprice=take_profit_price) 

            elif (self.rsi[0] >= 70) and (self.dataclose[0] >= self.bb.top[0]): 
                # SELL, SELL, SELL!!! (with all possible default parameters)
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
                self.orderStop = self.buy(price=self.data.close[0] * (1 + (self.params.stopLoss*0.01)), exectype=bt.Order.Stop)
                # stopPrice = self.data.close[0] * (1 + self.params.stopLoss*0.01)
                # takeProfitPrice = self.data.close[0] * (1 - self.params.stopLoss*0.01)   
                # self.order = self.sell(exectype=bt.Order.Stop, price=self.data.close[0], stopprice=stopPrice)#, limitprice=take_profit_price) 

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    strats = cerebro.optstrategy(
        cTrendsStrategy,
        periodRsi=range(4, 15),
        periodBB=range(20, 200),
        stopLoss=range(2,20) 
        )

     # Create a data feed
    data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2015-07-01', '2023-06-21', interval = "1d"))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
    # Adiciono na classe analyzer os indicadores de resultado que quero buscar

    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    # Set the commission
    cerebro.broker.setcommission(commission=0.0)
    
    # Variável optimizationResults retorna uma lista de todos os resultados
    optimizationResults = cerebro.run(maxcpus=4)
    #print(optimizationResults[0][0].broker.getvalue())
    paramsList = [[
        
      x[0].params.periodRsi,
      x[0].params.periodBB,
      x[0].params.stopLoss*0.01,  
      x[0].analyzers.dd.get_analysis()['max']['drawdown'],
      x[0].analyzers.sharpe.get_analysis()['sharperatio'],
      x[0].analyzers.returns.get_analysis()['rtot'],
      x[0].analyzers.sqn.get_analysis()['sqn'], # Indicador SQN do matemático Tharp
      abs(x[0].analyzers.trades.get_analysis()['won']['pnl']['total']/x[0].analyzers.trades.get_analysis()['lost']['pnl']['total']), # Profit Factor
      x[0].analyzers.trades.get_analysis()['total']['closed'], # Número total de trades
      x[0].analyzers.trades.get_analysis()['won']['total']/x[0].analyzers.trades.get_analysis()['total']['closed'] # Taxa de acerto

    ]for x in optimizationResults]
    
    paramsDf = pd.DataFrame(paramsList, columns=['Periodo RSI','Periodo BB', 'Stop Loss', 'Drawdown %', 'Sharpe Ratio', 'Retorno', 'SQN', 'Profit Factor', 'Total Trades', 'Taxa de acerto'])
    # 
    paramsDf.to_csv('/home/gabrielvieira/flix/backtest-bots/results.csv', index=False)
