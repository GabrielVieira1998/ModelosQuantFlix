from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import yfinance as yf
# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd
import argparse



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

# Bandwidth = (Upper Bollinger Band® - Lower Bollinger Band®)/Middle Bollinger Band®
from BollingerBandWidth import BbWidth

# Create a Strategy
class volStrategy(bt.Strategy):
    params = (
        ('periodBB', 200),
        ('nQuartile', 100),
        ('firstLineQuartile', 0),
        ('secondLineQuartile', 3),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.orderStop = None
        self.buyPrice = None
        self.sellPrice = None
        self.buyComm = None

        # self.csvFile = open('backtest_history.csv', 'w', newline='')
        # self.csvWriter = csv.writer(self.csvFile)
        # self.csvWriter.writerow(['Date', 'Price', 'Direction', 'Type', 'Pnl', 'Size', 'EntryPrice', 'ExitType', 'BBtop', 'BBbot'])

        # Add a BB and RSI indicator
        self.bb = bt.indicators.BollingerBands(self.datas[0], period=self.params.periodBB)
        
        self.bbWidth = BbWidth(period=self.params.periodBB, n=self.params.nQuartile, firstLineQuartile=self.params.firstLineQuartile, secondLineQuartile=self.params.secondLineQuartile)

       

    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, BB: %.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm,
                #           self.bb.bot[0]))
                self.buyPrice = order.executed.price
                self.buyComm = order.executed.comm
                self.entryPrice = order.executed.price
                self.exitType = ''
                
                # if self.sellPrice is None or order.executed.price < self.sellPrice:
                #     entry_exitType = 'Entry'
                # else:
                #     entry_exitType = 'Exit'

                # self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Buy',
                #                           0, order.executed.size, '', '', self.bb.top[0], self.bb.bot[0]]) # , self.rsi[0]

            else:  # Sell
                # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, BB: %.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm,
                #           self.bb.top[0]))

                self.sellPrice = order.executed.price
                self.buyComm = order.executed.comm
                self.entryPrice = order.executed.price
                self.exitType = ''
                
                # if self.buyPrice is None or order.executed.price > self.buyPrice:
                #     entry_exitType = 'Entry'
                # else:
                #     entry_exitType = 'Exit'

                # self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Sell',
                #                       0, order.executed.size, '', '', self.bb.top[0], self.bb.bot[0]]) # , self.rsi[0]


            self.bar_executed = len(self)

        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        pnl = trade.pnl
        pnlcomm = trade.pnlcomm
        # print("PNL: ", pnl)
        # print("trade.price: ", trade.price)
        # print("trade.status: ", trade.history)

        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        if self.exitType == '':
            self.exitType = 'StopLoss' if pnl < 0 else 'SelfClose'

        #self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlcomm))
        
        # if self.exitType == 'SelfClose':
        #     self.broker.cancel(self.orderStop)

        # self.csvWriter.writerow([
        #     self.datas[0].datetime.datetime(0),  # Date
        #     self.sellPrice if pnl < 0 else self.buyPrice,  # Price
        #     'Out',  # Direction
        #     'Sell' if pnl < 0 else 'Buy',  # Type
        #     pnl,  # pnl
        #     trade.size,  # Size
        #     self.entryPrice,  # EntryPrice
        #     self.exitType,  # ExitType
        #     self.bb.top[0],
        #     self.bb.bot[0]
            
        # ])


    
    def signalType(self):

        if(self.bbWidth[0] < self.bbWidth.second[0]) and (self.bbWidth[0] > self.bbWidth.first[0]):
            return "Trend Follow"
        elif (self.bbWidth[0] < self.bbWidth.first[0]):
            return "Reversion"
        
        
    def next(self):
        if self.order:
            return

        signal = self.signalType()
        
        if signal == "Trend Follow":
            # Quando sinal igual a trend follow eu já sei que estou entre as first e second line, portanto basta checar bbwidth com a second line das últimas barras.
            if self.position:
                
                if(self.bbWidth[-2] >= self.bbWidth.second[-2]):
                    #print("Zerou tendência")
                    self.order = self.close()
                
            else:
                if (self.dataclose[0] >= self.bb.top[0]): # and (self.bbWidth[0] >= self.bbWidth.second[0]):  
                        # print("comprou tendência")                  
                        positionAdjSizeBuy = 50000/self.dataclose[0]
                        self.order = self.buy(size=positionAdjSizeBuy)
                        # self.orderStop = self.sell(size=positionAdjSizeBuy, price=self.dataclose[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

                elif (self.dataclose[0] <= self.bb.bot[0]):# and (self.bbWidth[0] >= self.bbWidth.second[0]):
                        # print("vendeu tendência")
                        positionAdjSizeSell = 50000/self.dataclose[0]
                        self.order = self.sell(size=positionAdjSizeSell)
                        # self.orderStop = self.buy(size=positionAdjSizeSell, price=self.dataclose[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)     
            
        elif signal == "Reversion":
            # Lembrar que no caso do código que realiza as entradas, zero tanto na banda superior e inferior quanto na inversão do sinal. 
            # Já na logica do trend following, só zero na inversão do sinal. 
            if self.position:

                if ((self.dataclose[0] >= self.bb.top[0]) and (self.position.size > 0)):
                    # print("Zerou reversão compra")
                    self.order = self.close()

                elif (self.dataclose[0] <= self.bb.bot[0]) and (self.position.size < 0):
                    # print("Zerou reversão venda")
                    self.order = self.close()

            else:
                if (self.dataclose[0] <= self.bb.bot[0]): # and (self.bbWidth[0] <= 0.20)
                    # print("Comprou reversão")
                    positionAdjSizeBuyReversion = 50000/self.dataclose[0]
                    self.order = self.buy(size=positionAdjSizeBuyReversion)
                    # self.orderStop = self.sell(size=positionAdjSizeBuyReversion,price=self.dataclose[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

                elif (self.dataclose[0] >= self.bb.top[0]):
                    # print("Vendeu reversão")
                    positionAdjSizeSellReversion = 50000/self.dataclose[0]
                    self.order = self.sell(size=positionAdjSizeSellReversion)
                    # self.orderStop = self.buy(size=positionAdjSizeSellReversion,price=self.dataclose[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)

            
            # print("Len Data Close: ", len(self.dataclose))
            # print("Len Data: ", self.dataclose.buflen())
            
            # if(len(self.dataclose) == self.dataclose.buflen()):
            #     self.order = self.order_target_size(target=0)       

    
                 

if __name__ == '__main__':
    args = parse_args()
    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=None)

    # Add a strategy
    cerebro.optstrategy(
        volStrategy,
        # nQuartile=range(5, 10),
        firstLineQuartile=range(0, 9),
        secondLineQuartile=range(9,19)
        )
    
     # Create a data feed
    data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2021-07-15', '2023-07-04', interval = "60m"))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # # Handy dictionary for the argument timeframe conversion
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
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
    # Adiciono na classe analyzer os indicadores de resultado que quero buscar

    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    # Set the commission
    cerebro.broker.setcommission(commission=0.0)
    
    # Variável optimizationResults retorna uma lista de todos os resultados
    optimizationResults = cerebro.run()

    #print(optimizationResults[0][0].broker.getvalue())
    paramsList = [[
        
      x[0].params.nQuartile,
      x[0].params.firstLineQuartile,
      x[0].params.secondLineQuartile,
      x[0].analyzers.dd.get_analysis()['max']['drawdown'],
      x[0].analyzers.sharpe.get_analysis()['sharperatio'],
      x[0].analyzers.trades.get_analysis()['pnl']['net']['total'],   
      x[0].analyzers.returns.get_analysis()['rtot'],
      x[0].analyzers.sqn.get_analysis()['sqn'], # Indicador SQN do matemático Tharp
      abs(x[0].analyzers.trades.get_analysis()['won']['pnl']['total']/x[0].analyzers.trades.get_analysis()['lost']['pnl']['total']), # Profit Factor
      x[0].analyzers.trades.get_analysis()['total']['closed'], # Número total de trades
      x[0].analyzers.trades.get_analysis()['won']['total']/x[0].analyzers.trades.get_analysis()['total']['closed'] # Taxa de acerto

    ]for x in optimizationResults]
    
    paramsDf = pd.DataFrame(paramsList, columns=['nQuartile','firstLineQuartile', 'secondLineQuartile', 'Drawdown %', 'Sharpe Ratio', 'NetValue', 'SQN', 'Profit Factor', 'Total Trades', 'Taxa de acerto'])
    # 
    paramsDf.to_csv('/home/gabrielvieira/flix/backtest-bots/results.csv', index=False)
