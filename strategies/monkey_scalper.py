from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pyfolio as pf



import argparse
import os
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import matplotlib.pyplot as plt
import datetime
import pandas as pd
# plt.switch_backend('Agg')
# silence warnings
import warnings
warnings.filterwarnings('ignore')
class MonkeyScalper(bt.Strategy):
    params = (
        ('bars', 10),
        # ('onlydaily', False),
        ('stop_loss', 1),
        ('alvo', 1),
    )
    name = 'monkey_scalper'
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # self.sma = btind.SMA(self.data, bars=self.p.bars)
        self.order = None
        self.orderStop = None
        self.position_price = 0
        self.position_direction = 0
        self.barCount = 0


    def start(self):
        self.counter = 0
    
    
    def prenext(self):
        self.counter += 1
        print('prenext len %d - counter %d' % (len(self), self.counter))
    
    def direction(self):
        unique_values = []
        direction = 0

        # Ensure that there are enough data points
        if len(self.data0) < self.p.bars:
            return 0

        # Iterate through the tick prices to find unique values
        for i in range(self.p.bars):
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
            if len(unique_values) == self.p.bars:
                break
        unique_values            
        # Return positive or negative based on the direction
        if direction >= 2:
            return 1
        elif direction <= -1:
            return -1

        return 0


    def next(self):
        self.counter += 1
        if self.barCount != len(self):
            
            if self.order:
                return
            
            if len(self.data) < self.p.bars:
                return
            

            
            print('---next len %d - counter %d - data %s' % (len(self), self.counter, self.datas[0].datetime.time(0)))

            position_size = 1
            direction = self.direction()
            price = self.data0.close[0]

            if direction < 0:
                price = self.data0.close[0]
                if self.position.size > 0 and self.position:
                    self.sell_bracket(price=price, stopprice=price+self.p.stop_loss, limitprice=price-self.p.alvo, size=position_size*2, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
                elif not self.position:
                    self.sell_bracket(price=price, stopprice=price+self.p.stop_loss, limitprice=price-self.p.alvo, size=position_size, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)

            else:
                price = self.data0.close[0]
                if self.position.size < 0 and self.position:
                    self.buy_bracket(price=price, stopprice=price-self.p.stop_loss, limitprice=price+self.p.alvo, size=position_size*2, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
                elif not self.position:
                    self.buy_bracket(price=price, stopprice=price-self.p.stop_loss, limitprice=price+self.p.alvo, size=position_size, exectype=bt.Order.Limit)#, valid=datetime.timedelta(0,2)
            self.barCount = len(self)
            
if __name__ == '__main__':
    
    # Define data types to reduce memory consumption
    dtypes = {
        'event_time': 'int64'  # Other columns can be added here with appropriate data types
    }

    # Read in chunks
    chunk_size = 1_000_000  # Adjust this based on your system's memory
    chunks = []
    for chunk in pd.read_csv('./data/BTCBUSD-bookTicker-2023-07.csv', chunksize=chunk_size, dtype=dtypes):
        timestamp = pd.to_datetime(chunk['event_time'], unit='ms')
        chunk.index = pd.DatetimeIndex(timestamp)
        chunk_resampled = chunk.resample('s').last().dropna()
        chunk_resampled = chunk_resampled.ffill()
        chunks.append(chunk_resampled)

    # Concatenate chunks
    df_seconds = pd.concat(chunks)
    df_seconds = df_seconds[df_seconds.index <= '2023-07-08']


    data_opt = df_seconds 
    data_bt = df_seconds
    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=None)

    # Add a strategy
    cerebro.optstrategy(
        strategy = MonkeyScalper, 
        bars=range(1,4,1), 
        stop_loss=range(10,50, 10),
        alvo=range(50, 500, 50) 
    )
    feed = bt.feeds.PandasData(dataname=data_opt, datetime=None, open=1, high=1, low=1, close=1, volume=4)

    # data = self.cerebro.resampledata(feed,
    #                timeframe=bt.TimeFrame.Seconds)

    cerebro.replaydata(feed,
                    timeframe=bt.TimeFrame.Minutes)
    # Create a Data Feed
    # datapath = ('../datas/2006-day-001.txt')
    # data = bt.feeds.BacktraderCSVData(dataname=datapath)
    cerebro.addanalyzer(bt.analyzers.PyFolio)
    # Add the Data Feed to Cerebro
    # cerebro.adddata(data)

    # clock the start of the process
    # tstart = time.clock()

    # Run over everything
    stratruns = cerebro.run()

    # clock the end of the process
    # tend = time.clock()

    print('==================================================')
    for stratrun in stratruns:
        print('**************************************************')
        for strat in stratrun:

            print('--------------------------------------------------')
            print(strat.p._getkwargs())
            # print()
            pyfoliozer = strat.analyzers.getbyname('pyfolio')
            returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
            # Get the current figure

            pf.create_full_tear_sheet(
                returns,
                positions=positions,
                transactions=transactions,
                gross_lev=gross_lev,
                round_trips=True)
            
            fig = plt.gcf()

            # Save the figure with the timestamp as the name
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            file_path = os.path.join("./pyfolio", f'{timestamp}.png')
            fig.savefig(file_path)
    print('==================================================')

    # print out the result
    # print('Time used:', str(tend - tstart))