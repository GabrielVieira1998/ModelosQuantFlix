from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt



# Create a Stratey
class cTrendsStrategy(bt.Strategy):
    params = (
        ('periodRsi', 4),
        ('periodBB', 28),
        ('stopLoss', 0.02),
        ('takeProfit', 0.05)
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.sellprice = None
        self.buycomm = None
        # 
       

        # Add a BB and RSI indicator
        self.bb = bt.indicators.BollingerBands(self.datas[0], period=self.params.periodBB)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.datas[0], period=self.params.periodRsi)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, RSI: %.2f, BB: %.2f'  %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     self.rsi[0],
                     self.bb.bot[0]
                     ))
                # # #
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, RSI: %.2f, BB: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          self.rsi[0],
                          self.bb.top[0]))
                
                self.sellprice = order.executed.price
                self.buycomm = order.executed.comm
                

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if self.position:

            if (self.rsi[0] >= 70) and (self.dataclose[0] >= self.bb.top[0]) and (self.position.size > 0): #and (self.dataclose[0] >= self.bb.top[0]): # if(len(self) >= self.bar_executed + 5) self.dataclose[0] < self.sma[0]
                # SELL, SELL, SELL!!! (with all possible default parameters)
                # self.log('CLOSE BUY CREATED, %.2f' % self.dataclose[0])
                # print("self.bb.top[0]: ", self.bb.top[0], " self.rsi[0]: ", self.rsi[0], " price: ", self.data.close[0])
                # # Keep track of the created order to avoid a 2nd order
                self.order = self.close()

            elif (self.rsi[0] <= 30) and (self.dataclose[0] <= self.bb.bot[0]) and (self.position.size < 0):# 
                # BUY, BUY, BUY!!! (with all possible default parameters)
                # self.log('CLOSE SELL CREATED, %.2f' % self.dataclose[0])
                # print("self.bb.bot[0]: ", self.bb.bot[0], " self.rsi[0]: ", self.rsi[0], " price: ", self.data.close[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.close()
        else:
            
             # Not yet ... we MIGHT BUY if ...
            if (self.rsi[0] <= 30) and (self.dataclose[0] <= self.bb.bot[0]):# 
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                print("self.bb.bot[0]: ", self.bb.bot[0], " self.rsi[0]: ", self.rsi[0], " price: ", self.data.close[0])
                # Keep track of the created order to avoid a 2nd order
                stopPrice = self.data.close[0] * (1 - self.params.stopLoss)
                takeProfitPrice = self.data.close[0] * (1 + self.params.stopLoss)
                self.order = self.buy(exectype=bt.Order.Stop, price=self.data.close[0], stopprice=stopPrice)#, limitprice=take_profit_price) 
                #print("Self.Order Compra Com Stop: ", self.order)    
                #self.sell(price=self.data.close[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

            elif (self.rsi[0] >= 70) and (self.dataclose[0] >= self.bb.top[0]): 
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                print("self.bb.top[0]: ", self.bb.top[0], " self.rsi[0]: ", self.rsi[0], " price: ", self.data.close[0])
                # Keep track of the created order to avoid a 2nd order
                stopPrice = self.data.close[0] * (1 + self.params.stopLoss)
                takeProfitPrice = self.data.close[0] * (1 - self.params.stopLoss)
                self.order = self.sell(exectype=bt.Order.Stop, price=self.data.close[0], stopprice=stopPrice)#, limitprice=take_profit_price) 
                #print("Self.Order Venda Com Stop: ", self.order) 
                # #self.buy(price=self.data.close[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)     

