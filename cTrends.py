from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import csv


# Create a Strategy
class cTrendsStrategyTest(bt.Strategy):
    params = (
        ('periodRsi', 4),
        ('periodBB', 20),
        ('stopLoss', 0.02),
        ('takeProfit', 0.05)
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
        self.csvWriter.writerow(['Date', 'Price', 'Direction', 'Type', 'Pnl', 'Size', 'EntryPrice', 'ExitType', 'IRF', 'BB top', 'BB bot'])

        # Add a BB and RSI indicator
        self.bb = bt.indicators.BollingerBands(self.datas[0], period=self.params.periodBB)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.datas[0], period=self.params.periodRsi)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, RSI: %.2f, BB: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          self.rsi[0],
                          self.bb.bot[0]))
                self.buyPrice = order.executed.price
                self.buyComm = order.executed.comm
                self.entryPrice = order.executed.price
                self.exitType = ''

                if self.sellPrice is None or order.executed.price < self.sellPrice:
                    entry_exitType = 'Entry'
                else:
                    entry_exitType = 'Exit'

                self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Buy',
                                          0, order.executed.size, '', '', self.rsi[0], self.bb.top[0], self.bb.bot[0]])

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, RSI: %.2f, BB: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          self.rsi[0],
                          self.bb.top[0]))

                self.sellPrice = order.executed.price
                self.buyComm = order.executed.comm
                self.entryPrice = order.executed.price
                self.exitType = ''

                if self.buyPrice is None or order.executed.price > self.buyPrice:
                    entry_exitType = 'Entry'
                else:
                    entry_exitType = 'Exit'

                self.csvWriter.writerow([self.datas[0].datetime.datetime(0), order.executed.price, 'In', 'Sell',
                                      0, order.executed.size, '', '', self.rsi[0], self.bb.top[0], self.bb.bot[0]])


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
        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        if self.exitType == '':
            self.exitType = 'StopLoss' if pnl < 0 else 'SelfClose'

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlcomm))
        
        if self.exitType == 'SelfClose':
            self.broker.cancel(self.orderStop)

        self.csvWriter.writerow([
            self.datas[0].datetime.datetime(0),  # Date
            self.sellPrice if pnl < 0 else self.buyPrice,  # Price
            'Out',  # Direction
            'Sell' if pnl < 0 else 'Buy',  # Type
            pnl,  # pnl
            trade.size,  # Size
            self.entryPrice,  # EntryPrice
            self.exitType,  # ExitType
            self.rsi[0], 
            self.bb.top[0],
            self.bb.bot[0]
            
        ])

    def next(self):
        if self.order:
            return

        if self.position:
            if (self.rsi[0] >= 70) and (self.dataclose[0] >= self.bb.top[0]) and (self.position.size > 0):
                self.order = self.close()

            elif (self.rsi[0] <= 30) and (self.dataclose[0] <= self.bb.bot[0]) and (self.position.size < 0):
                self.order = self.close()

        else:
            if (self.rsi[0] <= 30) and (self.dataclose[0] <= self.bb.bot[0]):
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.log('BUY STOP LOSS CREATED, %.2f' % (self.dataclose[0] * (1 - self.params.stopLoss)))
                self.order = self.buy()
                self.orderStop = self.sell(price=self.dataclose[0] * (1 - self.params.stopLoss), exectype=bt.Order.Stop)

            elif (self.rsi[0] >= 70) and (self.dataclose[0] >= self.bb.top[0]):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
                self.log('SELL STOP LOSS CREATED, %.2f' % (self.dataclose[0] * (1 + self.params.stopLoss)))
                self.orderStop = self.buy(price=self.dataclose[0] * (1 + self.params.stopLoss), exectype=bt.Order.Stop)

        

    def stop(self):
        # Close the CSV file after the backtest is complete
        self.csvFile.close()
