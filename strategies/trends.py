# Bandwidth = (Upper Bollinger Band® - Lower Bollinger Band®)/Middle Bollinger Band®

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import csv
from strategies.indicators.gann_hilo import Gann_hilo_activator

# Create a Strategy
class Trends_strategy(bt.Strategy):
    params = (
        ('atrPeriod', 63),
        ('atrDist', 3),
        ('periodMe1', 12), 
        ('periodMe2', 26), 
        ('periodSignal', 9),
        ('periodHilo', 20),
        ('stopLoss', 0.09)
    )
    name = 'trends'
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

        
        # Add a BB and RSI indicator
        self.atr = bt.indicators.AverageTrueRange(self.datas[0], period=self.params.atrPeriod)
        self.macd = bt.indicators.MACD(self.datas[0], period_me1=self.params.periodMe1, period_me2=self.params.periodMe2, period_signal=self.params.periodSignal)
        self.gann_hilo = Gann_hilo_activator(period=self.params.periodHilo)
        # Sinal quando macd cruzar linha de sinal para baixo e para cima
        # self.crossOver = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        

        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm
                #           ))
                self.buyPrice = order.executed.price
                self.buyComm = order.executed.comm
                self.entryPrice = order.executed.price
                self.exitType = ''
                
                # if self.sellPrice is None or order.executed.price < self.sellPrice:
                #     entry_exitType = 'Entry'
                # else:
                #     entry_exitType = 'Exit'

                

            else:  # Sell
                # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm
                #           ))

                self.sellPrice = order.executed.price
                self.buyComm = order.executed.comm
                self.entryPrice = order.executed.price
                self.exitType = ''
                
                # if self.buyPrice is None or order.executed.price > self.buyPrice:
                #     entry_exitType = 'Entry'
                # else:
                #     entry_exitType = 'Exit'

                

            self.bar_executed = len(self)

        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     # self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        pnl = trade.pnl
        pnlcomm = trade.pnlcomm


        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        if self.exitType == '':
            self.exitType = 'StopLoss' if pnl < 0 else 'SelfClose'

        # self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlcomm))
        
        # if self.exitType == 'SelfClose':
        #     self.broker.cancel(self.orderStop)

        
    def next(self):
        if self.order:
            return
        atrValue = self.atr[0]
        macdValue = self.macd.macd[0]
        macdSignal = self.macd.signal[0] 
        priceClose = self.dataclose[0]    
        priceHilo = self.gann_hilo.hilo[0] 
        positionSize = self.position.size
        
        if self.position:
              
            if (macdValue < macdSignal) and (priceClose < priceHilo) and (positionSize > 0):

                self.order = self.close()

            elif (macdValue > macdSignal) and (priceClose > priceHilo) and (positionSize < 0):

                self.order = self.close()
            
            
        else:
            if (macdValue > macdSignal) and (priceClose > priceHilo):
                # self.log('BUY CREATE, %.2f' % priceClose)
                # # stopPriceBuy =  priceClose * (1 - self.params.stopLoss)
                stopPriceBuy = priceClose - (atrValue * self.params.atrDist)
                positionAdjSizeBuy = 50000/priceClose
                # self.log('STOP LOSS BUY CREATED, %.2f' % stopPriceBuy)
                self.order = self.buy(size=positionAdjSizeBuy)
                # self.orderStop = self.sell(size=positionAdjSizeBuy,price=stopPriceBuy, exectype=bt.Order.Stop)
                # self.order = self.buy_bracket(limitprice=self.dataclose[0] * (1 + self.params.stopLoss), price=self.dataclose[0], stopprice=self.dataclose[0] * (1 - self.params.stopLoss))
            elif (macdValue < macdSignal) and (priceClose < priceHilo):
                # self.log('SELL CREATE, %.2f' % priceClose)
                # stopPriceSell = priceClose  * (1 + self.params.stopLoss)
                positionAdjSizeSell = 50000/priceClose 
                stopPriceSell = priceClose + (atrValue * self.params.atrDist)
                # self.log('STOP LOSS SELL CREATED, %.2f' % stopPriceSell)  
                self.order = self.sell(size=positionAdjSizeSell)
                # self.orderStop = self.buy(size=positionAdjSizeSell,price=stopPriceSell, exectype=bt.Order.Stop)
                # self.order = self.sell_bracket(limitprice=self.dataclose[0] * (1 - self.params.stopLoss), price=self.dataclose[0], stopprice=self.dataclose[0] * (1 + self.params.stopLoss))

          

        

    # def stop(self):
    #     # Close the CSV file after the backtest is complete
    #     self.csvFile.close()
        
