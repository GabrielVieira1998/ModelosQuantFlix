# Bandwidth = (Upper Bollinger Band® - Lower Bollinger Band®)/Middle Bollinger Band®

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt



# Create a Strategy
class Sma_reversion(bt.Strategy):
    params = (
        ('period_long_sma', 200),
        ('period_short_sma', 50),
        ('period_bb', 200),
        ('sma_distance', 5.0), # Threshold for distance between SMA200 and SMA50
        ('trail_percent', 0.02)

    )

    name = 'sma_reversion'

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
        self.executedSize = None
        # Adicionando os indicadores
        self.bb = bt.indicators.BollingerBands(self.datas[0], period=self.params.period_bb)        
        self.long_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.period_long_sma)
        self.short_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.period_short_sma)
        # Distancia entre as duas médias
        self.sma_distance = abs(self.long_sma - self.short_sma) # Checar

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

    
            
            self.bar_executed = len(self)

        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     print("ORder status: ", order.status)
            # self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        
        if not trade.isclosed:
            return
  
        # self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        if self.order:
            return
        
        position_size = self.position.size
        # Quando sinal igual a trend follow eu já sei que estou entre as first e second line, portanto basta checar bbwidth com a second line das últimas barras.
        if self.sma_distance[0] < self.params.sma_distance:
            
            if not self.position:  # If not in the market already
                if self.dataclose[0] >= self.bb.top[0]:  # Touching upper band
                    self.order = self.sell()
                elif self.dataclose[0] <= self.bb.bot[0]:  # Touching lower band
                    self.order = self.buy()
            else:
                if ((self.dataclose[0] <= self.bb.mid[0]) and (position_size > 0)): 
                    self.close(size=position_size/2)
                    self.order = self.sell(size=position_size/2, exectype=bt.Order.StopTrail, trailpercent=self.params.trail_percent) 
                elif (self.dataclose[0] >= self.bb.mid[0]) and (position_size < 1):
                    self.close(size=position_size/2)
                    self.order = self.buy(size=position_size/2, exectype=bt.Order.StopTrail, trailpercent=self.params.trail_percent) 