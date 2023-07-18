# Bandwidth = (Upper Bollinger Band® - Lower Bollinger Band®)/Middle Bollinger Band®

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import csv
from BollingerBandWidth import BbWidth
import json
import uuid
import os



# Create a Strategy
class volStrategy(bt.Strategy):
    params = (
        ('periodBB', 200),
        ('tradeReversion', 0), # 0 false, 1 true
        ('tradeTrend', 1), # 0 false, 1 true        
        ('nQuartile', 8),
        ('firstLineQuartile', 0),
        ('secondLineQuartile', 2),
        ('stopLoss', 0.09)
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        
        self.trade_history = []
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.orderStop = None
        self.buyPrice = None
        self.sellPrice = None
        self.buyComm = None
        self.executedSize = None

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
                self.executedSize = order.executed.size

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
                self.executedSize = order.executed.size

                # self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Sell',
                #                       0, order.executed.size, '', '', self.bb.top[0], self.bb.bot[0]]) # , self.rsi[0]

           
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        print(" self.datas[0].datetime.datetime(0): ",  self.datas[0].datetime.datetime(0))
        print("trade.status: ", trade.status)
        print("trade.history: ", trade.history)
        print("trade.justopened: ", trade.justopened)
        print("isclosed: ", trade.isclosed)
        print("-----------")
        if trade.justopened:
            # print("trade.price: ", trade.price)
            # print("trade.size: ", trade.size)
            self.trade_history.append({
                'Date': self.datas[0].datetime.datetime(0).isoformat(),
                'Price': trade.price,
                'Direction': 'In',
                'Type': 'Buy' if trade.size > 0 else 'Sell',
                'Pnl': trade.pnl,  # Placeholder for later calculation
                'Size': trade.size,
                'EntryPrice': trade.price,
                'ExitType': ''
                # 'BBtop': self.bb.top[0],
                # 'BBbot': self.bb.bot[0]
            })
        
        if not trade.isclosed:
            return


        
        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        if self.exitType == '':
            self.exitType = 'StopLoss' if trade.pnl < 0 else 'SelfClose'

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
        
        self.trade_history.append({
                'Date': self.datas[0].datetime.datetime(0).isoformat(),
                'Price': self.entryPrice,
                'Direction': 'Out',
                'Type': 'Buy' if self.executedSize > 0 else 'Sell',
                'Pnl': trade.pnl,  # Placeholder for later calculation
                'Size': self.executedSize,
                'EntryPrice': trade.price,
                'ExitType': ''
                # 'BBtop': self.bb.top[0],
                # 'BBbot': self.bb.bot[0]
            })
    
    def signalType(self):

        if(self.bbWidth[0] < self.bbWidth.second[0]) and (self.bbWidth[0] > self.bbWidth.first[0]):
            return "Trend Follow"
        elif (self.bbWidth[0] < self.bbWidth.first[0]) :
            return "Reversion"
        
        
    def next(self):
        if self.order:
            return

        signal = self.signalType()
        
        if (signal == "Trend Follow") and (self.params.tradeTrend == 1):
            # Quando sinal igual a trend follow eu já sei que estou entre as first e second line, portanto basta checar bbwidth com a second line das últimas barras.
            if self.position:
                
                if(self.bbWidth[-1] >= self.bbWidth.second[-1]):
                    print("Zerou tendência")
                    self.order = self.close()
                
            else:
                if (self.dataclose[0] >= self.bb.top[0]): # and (self.bbWidth[0] >= self.bbWidth.second[0]):  
                        print("comprou tendência")                  
                        positionAdjSizeBuy = 100000/self.dataclose[0]
                        self.order = self.buy(size=positionAdjSizeBuy)
                        # self.orderStop = self.sell(size=positionAdjSizeBuy, price=self.dataclose[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

                elif (self.dataclose[0] <= self.bb.bot[0]):# and (self.bbWidth[0] >= self.bbWidth.second[0]):
                        print("vendeu tendência")
                        positionAdjSizeSell = 100000/self.dataclose[0]
                        self.order = self.sell(size=positionAdjSizeSell)
                        # self.orderStop = self.buy(size=positionAdjSizeSell, price=self.dataclose[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)     
            
        elif (signal == "Reversion") and (self.params.tradeReversion == 1):
            # Lembrar que no caso do código que realiza as entradas, zero tanto na banda superior e inferior quanto na inversão do sinal. 
            # Já na logica do trend following, só zero na inversão do sinal. 
            if self.position:

                if ((self.dataclose[0] >= self.bb.top[0]) and (self.position.size > 0)):
                    print("Zerou reversão compra")
                    self.order = self.close()

                elif (self.dataclose[0] <= self.bb.bot[0]) and (self.position.size < 0):
                    print("Zerou reversão venda")
                    self.order = self.close()

            else:
                if (self.dataclose[0] <= self.bb.bot[0]): # and (self.bbWidth[0] <= 0.20)
                    print("Comprou reversão")
                    positionAdjSizeBuyReversion = 100000/self.dataclose[0]
                    self.order = self.buy(size=positionAdjSizeBuyReversion)
                    # self.orderStop = self.sell(size=positionAdjSizeBuyReversion,price=self.dataclose[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

                elif (self.dataclose[0] >= self.bb.top[0]):
                    print("Vendeu reversão")
                    positionAdjSizeSellReversion = 100000/self.dataclose[0]
                    self.order = self.sell(size=positionAdjSizeSellReversion)
                    # self.orderStop = self.buy(size=positionAdjSizeSellReversion,price=self.dataclose[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)
   

    def stop(self):
        # Close the CSV file after the backtest is complete
        # self.csvFile.close()
        # userId = str(uuid.uuid4())
        # folder_name = userId

        # # Specify the path where you want to create the folder
        # path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/'+folder_name+'/'

        # # Join the path and folder name
        # folder_path = os.path.join(path, folder_name)

        # # Create the folder
        # os.makedirs(folder_path)

        # json_path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/'+folder_name+'/'+userId+'_'+'backtest_history_test.json'
    
        # Create a JSON file and write the trade history

        with open('backtest_transaction_history_novaotimziacao.json', 'x') as json_file:
            json.dump(self.trade_history, json_file)
