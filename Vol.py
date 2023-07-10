# Bandwidth = (Upper Bollinger Band® - Lower Bollinger Band®)/Middle Bollinger Band®

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import csv
from BollingerBandWidth import BbWidth

# Create a Strategy
class volStrategy(bt.Strategy):
    params = (
        ('periodBB', 200),
        ('stopLoss', 0.09)
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

        self.csvFile = open('backtest_history.csv', 'w', newline='')
        self.csvWriter = csv.writer(self.csvFile)
        self.csvWriter.writerow(['Date', 'Price', 'Direction', 'Type', 'Pnl', 'Size', 'EntryPrice', 'ExitType', 'BBtop', 'BBbot'])

        # Add a BB and RSI indicator
        self.bb = bt.indicators.BollingerBands(self.datas[0], period=self.params.periodBB)
        
        self.bbWidth = BbWidth(period=self.params.periodBB)

       

    
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

                self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Buy',
                                          0, order.executed.size, '', '', self.bb.top[0], self.bb.bot[0]]) # , self.rsi[0]

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

                self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Sell',
                                      0, order.executed.size, '', '', self.bb.top[0], self.bb.bot[0]]) # , self.rsi[0]


            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        pnl = trade.pnl
        pnlcomm = trade.pnlcomm
        print("PNL: ", pnl)
        print("trade.price: ", trade.price)
        print("trade.status: ", trade.history)

        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        if self.exitType == '':
            self.exitType = 'StopLoss' if pnl < 0 else 'SelfClose'

        #self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlcomm))
        
        # if self.exitType == 'SelfClose':
        #     self.broker.cancel(self.orderStop)

        self.csvWriter.writerow([
            self.datas[0].datetime.datetime(0),  # Date
            self.sellPrice if pnl < 0 else self.buyPrice,  # Price
            'Out',  # Direction
            'Sell' if pnl < 0 else 'Buy',  # Type
            pnl,  # pnl
            trade.size,  # Size
            self.entryPrice,  # EntryPrice
            self.exitType,  # ExitType
            self.bb.top[0],
            self.bb.bot[0]
            
        ])

    def next(self):
        if self.order:
            return
        print("self.bbWidth[0]: ", len(self.bbWidth.lines.bbWidth))
        if self.position:
            if  (self.bbWidth[0] <= 0.05) and (self.position.size > 0): # (self.dataclose[0] >= self.bb.top[0])
                self.order = self.close()

            elif (self.bbWidth[0] <= 0.05) and (self.position.size < 0):
                self.order = self.close()

        else:
            if (self.dataclose[0] >= self.bb.top[0]) and (self.bbWidth[0] >= 0.07):
                # self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # self.log('STOP LOSS BUY CREATED, %.2f' % (self.dataclose[0] * (1 - self.params.stopLoss)))
                print("self.bb.top: ", (self.bb.top[0]/self.bb.mid[0]-1)*100, "self.bb.bot: ", (self.bb.bot[0]/self.bb.mid[0]-1)*100, " self.bb.mid: ", self.bb.mid[0], " self.bbWidth[0]: ", self.bbWidth[0])
        
                positionAdjSizeBuy = 50000/self.dataclose[0]
                self.order = self.buy(size=positionAdjSizeBuy)
                #self.order = self.buy_bracket(limitprice=self.dataclose[0] * (1 + self.params.stopLoss), price=self.dataclose[0], stopprice=self.dataclose[0] * (1 - self.params.stopLoss))
                #self.orderStop = self.sell(size=positionAdjSizeBuy, price=self.dataclose[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

            elif (self.dataclose[0] <= self.bb.bot[0]) and (self.bbWidth[0] >= 0.07):
                # self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # self.log('STOP LOSS SELL CREATED, %.2f' % (self.dataclose[0] * (1 + self.params.stopLoss)))
                print("self.bb.top: ", self.bb.top[0], "self.bb.bot: ", self.bb.bot[0], " self.bb.mid: ", self.bb.mid[0], " self.bbWidth[0]: ", self.bbWidth[0])
        
               # print("self,bbwidth: ", self.bbWidth[0])
                positionAdjSizeSell = 50000/self.dataclose[0]
                self.order = self.sell(size=positionAdjSizeSell)
                # self.order = self.sell_bracket(limitprice=self.dataclose[0] * (1 - self.params.stopLoss), price=self.dataclose[0], stopprice=self.dataclose[0] * (1 + self.params.stopLoss))
                #self.orderStop = self.buy(size=positionAdjSizeSell, price=self.dataclose[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)

        # print("Len Data Close: ", len(self.dataclose))
        # print("Len Data: ", self.dataclose.buflen())
        
        # if(len(self.dataclose) == self.dataclose.buflen()):
        #     self.order = self.order_target_size(target=0)       

    def stop(self):
        # Close the CSV file after the backtest is complete
        self.csvFile.close()
