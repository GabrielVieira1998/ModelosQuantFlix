from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import matplotlib.pyplot as plt
import datetime
import pandas as pd
plt.switch_backend('Agg')

class SMAStrategy(bt.Strategy):
    params = (
        ('period', 10),
        ('onlydaily', False),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # self.sma = btind.SMA(self.data, period=self.p.period)
        self.order = None
        self.orderStop = None
        self.position_price = 0
        self.position_direction = 0


    def start(self):
        self.counter = 0

    def notify_order(self, order):
        # print(order)
        # if order.status in [order.Submitted, order.Accepted]:
        #     # Buy/Sell order submitted/accepted by broker - Nothing to do
        #     return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm
                          ))
            

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm
                          ))

                
                self.exitType = ''
                
                # if self.buyPrice is None or order.executed.price > self.buyPrice:
                #     entry_exitType = 'Entry'
                # else:
                #     entry_exitType = 'Exit'

                

            self.bar_executed = len(self)

        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     self.log('Order Canceled/Margin/Rejected')
            # print(order.Margin)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        pnl = trade.pnl
        pnlcomm = trade.pnlcomm
        # print("Cancelando stop")
        # self.broker.cancel(self.orderStop)
        # self.broker.cancel(self.orderTakeProfit)

        # Self.Close seria nosso take profit, pois ele só zera na inversão do indicador. 
        # if self.exitType == '':
            
        #     self.exitType = 'StopLoss' if pnl < 0 else 'SelfClose'

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlcomm))
    
    
    def prenext(self):
        self.counter += 1
        print('prenext len %d - counter %d' % (len(self), self.counter))
    
    
    
    # def direction(self):
   
    #     unique_values = [self.data0.close[0]]
    #     print(len(self.datas[0]))
    #     direction = 0
    #     last_value = self.data.close[0]
    #     for i in self.datas:
    #         print(i.close[0])
    #         if i == self.data0.close[0]:
    #             continue
    #         if i not in unique_values:
    #             if last_value > i:
    #                 direction += 1
    #             else:
    #                 direction -= 1
    #             last_value = i
    #             unique_values.append(i)
    #             print(unique_values)

    #         if len(unique_values) == 4:
    #             break
    #     return direction        
        
    def direction(self):
        unique_values = []
        direction = 0

        # Ensure that there are enough data points
        if len(self.data0) < self.p.period:
            return 0

        # Iterate through the tick prices to find unique values
        for i in range(self.p.period):
            current_value = self.data0.close[-(i + 1)]

            # Skip duplicates and only consider unique values
            if current_value not in unique_values:
                unique_values.append(current_value)

                # Calculate direction based on unique values
                if len(unique_values) > 1:
                    if unique_values[-2] > unique_values[-1]:
                        direction += 1
                    elif unique_values[-2] < unique_values[-1]:
                        direction -= 1

            # Break once we have the last 3 unique values
            if len(unique_values) == self.p.period:
                break
        unique_values            
        # Return positive or negative based on the direction
        if direction >= 2:
            return 1
        elif direction <= -1:
            return -1

        return 0


    def next(self):
        
        if self.order:
            return
        
        if len(self.data) < self.p.period:
            return
        

        self.counter += 1
        # print('---next len %d - counter %d - data %s' % (len(self), self.counter, self.datas[0].datetime.time(0)))
        # print(self.data0.close[0])
        

        
        
        # print(f"Tick n:{self.counter}")
        position_size = 30
        direction = self.direction()
        price = self.data0.close[0]
        if direction == 0:
            return
        # print(direction)
        if direction < 0:
            price = self.data0.close[0]
            if self.position.size > 0 and self.position:
                self.sell_bracket(price=price, stopprice=price+1, limitprice=price-30, size=position_size*2, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
            elif not self.position:
                self.sell_bracket(price=price, stopprice=price+1, limitprice=price-30, size=position_size, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)

            #compra
            # self.order = self.buy(size=position_size)
            # self.position_price = self.data0.close[0]                               #0.00001
            # self.orderStop = self.sell(size=position_size, price=self.data0.close[0]*0.99999, exectype=bt.Order.Stop)
            # self.orderTakeProfit = self.sell(size=position_size, price=self.data0.close[0]*1.0005, exectype=bt.Order.Limit)
        else:
            price = self.data0.close[0]
            if self.position.size < 0 and self.position:
                self.buy_bracket(price=price, stopprice=price-1, limitprice=price+30, size=position_size*2, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
            elif not self.position:
                self.buy_bracket(price=price, stopprice=price-1, limitprice=price+30, size=position_size, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
            #vender
            
            # self.order = self.sell(size=position_size)
            # self.position_price = self.data0.close[0]
            # self.orderStop = self.buy(size=position_size, price=self.data0.close[0]*1.00001, exectype=bt.Order.Stop)
            # self.orderTakeProfit = self.buy(size=position_size, price=self.data0.close[0]*0.9995, exectype=bt.Order.Limit)
        # self.orderStop = self.buy(size=position_size, exectype=bt.Order.StopTrail, price=self.data0.close[0]*1.00005, trailpercent=0.0005)
            # o1 = self.buy_bracket(price=price, stopprice=price-1, limitprice=price+1)
        # self.sell(size=position_size, price=self.data0.close[0]*1., exectype=bt.Order.Limit)


def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=True)
    
    cerebro.addstrategy(
        SMAStrategy,
        # args for the strategy
        period=3,
    )
    df = pd.read_csv(filepath_or_buffer='./data/BTCBUSD-bookTicker-2023-08-06.csv')
    timestamp = pd.to_datetime(df['event_time'], unit='ms')
    df.index = pd.DatetimeIndex(timestamp)
    df_seconds = df.resample('s').last()
    df_seconds.dropna(axis=0, inplace=True)
    data = bt.feeds.PandasData(dataname=df_seconds, datetime=None, open=1, high=1, low=1, close=1, volume=5)

    # Load the Data
    # datapath = args.dataname or './data/BTCBUSD-bookTicker-2023-08-06.csv'
    # data = bt.feeds.GenericCSVData(
    #     dataname=datapath,
    #     datetime=6,
    #     open=1,
    #     close=1,
    #     high=1,
    #     low=1,
    #     volume=4,
    #     dtformat=lambda x:datetime.datetime.fromtimestamp(round(int(x)/1000)),
    #     timeframe=bt.TimeFrame.Ticks,
    # )

    # Handy dictionary for the argument timeframe conversion
    tframes = dict(
        daily=bt.TimeFrame.Days,
        weekly=bt.TimeFrame.Weeks,
        monthly=bt.TimeFrame.Months)

    # First add the original data - smaller timeframe
    # cerebro.resampledata(data,
    #                    timeframe=bt.TimeFrame.Minutes, compression=30)
    cerebro.replaydata(data,
                       timeframe=bt.TimeFrame.Minutes)


    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(
        commission=0.000012, margin=None, mult=1)
    
    #############
    # Run over everything
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # #############
    filename = "plot_output.png"
    temp_fig_path = os.path.join(os.getcwd(), filename)
    
    figs = cerebro.plot(style='candle', barup='green', bardown='red')
    fig = figs

    # Adjust the figure size
    # fig.set_size_inches(14, 8)

    # Save the figure with a defined DPI
    fig.show()




def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--timeframe', default='daily', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=1, required=False, type=int,
                        help='Compress n bars into 1')

    parser.add_argument('--period', default=10, required=False, type=int,
                        help='Period to apply to indicator')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()