from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pyfolio as pf


# import asyncio
# from concurrent.futures import ThreadPoolExecutor

# # ... [rest of your imports]

# executor = ThreadPoolExecutor()
# import threading

# # at the beginning of your script
# plotting_lock = threading.Lock()

import os
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import matplotlib
import matplotlib.pyplot as plt
from pprint import pprint
# plt.switch_backend('Agg')
# import matplotlib
matplotlib.use('Agg')
from datetime import datetime
import time
from multiprocessing import Pool
import pandas as pd
import math
import tempfile
# Add these lines here

# silence warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

df_seconds = pd.read_csv('./data/BTCBUSD_2023_07.csv')
df_seconds.index = pd.DatetimeIndex(df_seconds['Date'])
df_seconds.drop(columns=['Date'], inplace=True)

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
        self.order = False
        self.orderStop = None
        self.position_price = 0
        self.position_direction = 0
        self.barCount = 0
        self.entryPrice = 0
        local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Backtest started at initialization time: {local_time}")
        
    # def start(self):
    #     print("Backtest Starting")
    # def stop(self):
    #     print("Backtest over")
    #     print(self.position.size)
    #     print(self.position.price)
    #     self.cerebro.broker.add_cash(self.position.size*self.position.price)
    #     self.close(size=1, exectype=bt.Order.Market)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # self.order = True
            # Buy/Sell order submitted/accepted by broker - Nothing to do
            return
        # else:
        #     self.order = False

        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entryPrice = order.executed.price
            else:  # Sell
                self.entryPrice = order.executed.price

        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     self.log('Order Canceled/Margin/Rejected')
        #     print(order.status)
        #     print(order.Margin)
        #     print(order.Rejected)
        #     print(order.Canceled)

        # Write down: no pending order
        
        self.order = False
    

    def start(self):
        self.counter = 0
    
    
    def prenext(self):
        self.counter += 1
        # print('prenext len %d - counter %d' % (len(self), self.counter))
    
    def direction(self):
        direction = 0

        # Ensure that there are enough data points
        if len(self) < self.p.bars:
            return 0

        # Iterate through the tick prices to find unique values
        # print(range(self.p.bars))
        for i in range(self.p.bars):
            close = self.data.lines.close[-(i + 1)]
            open = self.data.lines.open[-(i + 1)]
            
            # diff = open - close
            # Skip duplicates and only consider unique values
            # if open not in unique_values:
            # unique_values.append(open)
            # Calculate direction based on unique values
            # if len(unique_values) > 1:
            if close > open:
                direction += 1
            elif close < open:
                direction -= 1

            # Break once we have the last 3 unique values
            # if len(unique_values) == self.p.bars:
            #     print(self.datas[0].datetime.datetime(0), unique_values)
            #     break
        # unique_values            
        # Return positive or negative based on the direction

        return direction


    def next(self):
        self.counter += 1

        position_size = 1
        
        # Aqui monitoro stop loss e take profit a cada segundo.
        # print("self.position: ", self.position)
        if self.position: 
            
            stop_price_long = self.entryPrice - self.p.stop_loss
            take_profit_long = self.entryPrice + self.p.alvo
            stop_price_short = self.entryPrice + self.p.stop_loss
            take_profit_short = self.entryPrice - self.p.alvo
            price_current = self.data0.close[0]
            position_size_open = self.position.size
            
            if (price_current >= take_profit_long and position_size_open > 0) or (price_current <= stop_price_long and position_size_open > 0):
                self.close(size=position_size, exectype=bt.Order.Market)
                # self.buy(size=position_size, exectype=bt.Order.Market)
                self.order = True

            elif (price_current >= stop_price_short and position_size_open < 0) or (price_current <= take_profit_short and position_size_open < 0):
                self.close(size=position_size, exectype=bt.Order.Market)
                # self.sell(size=position_size, exectype=bt.Order.Market)
                self.order = True

        # #######
        ######
        #####
        ####
        ###
        ##

        if self.barCount != len(self):
            
            if self.order:
                return
            
            if len(self.data) < self.p.bars:
                return
            
            

            direction = self.direction()
            # price = self.data0.close[0]
            if direction == 0:
                return

            # print('---next len %d - counter %d - data %s' % (len(self), self.counter, self.datas[0].datetime.time(0)))

            if direction < 0:                
                if not self.position and self.order == False:
                    self.order = True
                    self.sell(size=position_size, exectype=bt.Order.Market)
            else:

                if not self.position and self.order == False:
                    self.order = True
                    self.buy(size=position_size, exectype=bt.Order.Market)
                
            self.barCount = len(self)
        # if len(self) == (self.buflen()):
        #     self.close()
    # def stop(self):
    #     print("params: ", self.p.stop)   
    # 

def run_single_backtest(bars, stop_loss, alvo):
    
    # Reset cerebro
    cerebro = bt.Cerebro(maxcpus=1)
    
    feed = bt.feeds.PandasData(dataname=df_seconds, datetime=None, open=0, high=1, low=2, close=3)
    cerebro.replaydata(feed, timeframe=bt.TimeFrame.Minutes)
    cerebro.addanalyzer(bt.analyzers.PyFolio)
    cerebro.broker.setcommission(commission=0.0001)
    cerebro.broker.setcash(100000)
    
    # Add strategy with current parameters
    # cerebro.optstrategy(strategy, bars=bars, stop_loss=stop_loss, alvo=alvo)
    cerebro.addstrategy(MonkeyScalper, bars=bars, stop_loss=stop_loss, alvo=alvo)
    
    # Run the backtest
    stratruns = cerebro.run()
    strat = stratruns[0]
    try:
        pyfoliozer = strat.analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
        # Check if returns are not empty
        if not returns.empty:
            pf.create_simple_tear_sheet(
                returns,
                positions=positions,
                transactions=transactions,
            )
            
            fig = plt.gcf()

            # Save the figure with the timestamp as the name
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            file_path = os.path.join("./pyfolio", f'{timestamp}_stoploss{stop_loss}_alvo{alvo}_bars{bars}.png')
            transactions.to_csv(os.path.join("./pyfolio", f'transactions-{timestamp}_stoploss{stop_loss}_alvo{alvo}_bars{bars}.csv'))
            positions.to_csv(os.path.join("./pyfolio", f'positions-{timestamp}_stoploss{stop_loss}_alvo{alvo}_bars{bars}.csv'))
            returns.to_csv(os.path.join("./pyfolio", f'returns-{timestamp}_stoploss{stop_loss}_alvo{alvo}_bars{bars}.csv'))

            fig.savefig(file_path)

            # Close the current figure
            plt.close(fig)
            
        else:
            print(f"No returns data for stop_loss={stop_loss} / alvo={alvo} / bars={bars}.")
            
    except Exception as e:
        print(f"Error during plotting: {e}")

    print('==================================================')
    print(f"Finished backtest for stop_loss={stop_loss} / alvo={alvo} / bars={bars}.")
    # time.sleep(10)

def worker(params):
    return run_single_backtest(*params) 

# Convert the backtest function to be coroutine-compatible
# async def run_single_backtest_async(cerebro, strategy, data_opt, bars, stop_loss, alvo):
#     loop = asyncio.get_event_loop()
#     print("loop: ", loop)
#     await loop.run_in_executor(executor, run_single_backtest, cerebro, strategy, data_opt, bars, stop_loss, alvo)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
    

# Adjust your main code block
if __name__ == '__main__':
    # cerebro = bt.Cerebro(maxcpus=1)
    # print("Loading data...")

    # df_seconds = df_seconds[df_seconds.index >= '2023-07-20 23:30:00']
    
    # Create a list to hold our coroutines
    # tasks = []

    for bar in range(1, 6):
        for stop in range(1, 20, 1):
            for a in range(5, 50, 5):
                print(f"Running backtest for stop_loss={stop} / alvo={a} / bars={bar}")
                run_single_backtest(bar, stop, a)
                # tasks.append(task)
                # tasks.append((cerebro, MonkeyScalper, df_seconds, bar, stop, a))
    # Run all the tasks using asyncio
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    
    # Quebro em bacthes
    # chunk_size = 4  # Reduced chunk size
    # total_tasks = len(tasks)
    # num_batches = math.ceil(total_tasks / chunk_size)

    # for i in range(num_batches):
    #     start_index = i * chunk_size
    #     end_index = start_index + chunk_size
    #     current_batch = tasks[start_index:end_index]

    #     print(f"Running batch {i + 1} of {num_batches}")
        
    #     with Pool() as pool:
    #         pool.map(worker, current_batch)
        
    #     print(f"Finished batch {i + 1} of {num_batches}")

    #     if i < num_batches - 1:
    #         print("Pausing for 30 seconds before next batch...")
    #         time.sleep(30)  # Pause for 30 seconds between batches
    
    
    # print("All backtests finished.")















# if __name__ == '__main__':
    
#     print("Loading data...")
#     df_seconds = pd.read_csv('./data/BTCBUSD_2023_07.csv')
#     # timestamp = pd.to_datetime(df_seconds['event_time'], unit='ms')
#     df_seconds.index = pd.DatetimeIndex(df_seconds['Date'])
#     df_seconds.drop(columns=['Date'], inplace=True)
#     df_seconds.dropna(axis=0,inplace=True)
#     df_seconds = df_seconds[df_seconds.index >= '2023-07-28 23:30:00']


#     data_opt = df_seconds 
#     data_bt = df_seconds
#     print()
#     print("Data loaded")

#     # Create a cerebro entity
#     cerebro = bt.Cerebro() # maxcpus=16 maxcpus=16

#     # cerebro.addobserver(bt.observers.BuySell)

#     # Add a strategy
#     cerebro.optstrategy(
#         strategy = MonkeyScalper, 
#         bars=2, 
#         stop_loss=range(5, 35, 5), 
#         alvo=range(10, 60, 10)
#     )
#     # cerebro.addstrategy(
#     #     strategy = MonkeyScalper,
#     #     bars=3, 
#     #     stop_loss=1,
#     #     alvo=50
#     # )

#     feed = bt.feeds.PandasData(dataname=data_opt, datetime=None, open=0, high=1, low=2, close=3)

#     cerebro.replaydata(feed,
#                     timeframe=bt.TimeFrame.Minutes)
    

#     # data = cerebro.resampledata(feed,
#     #                timeframe=bt.TimeFrame.Seconds)
#     # cerebro.replaydata(data,
#     #                 timeframe=bt.TimeFrame.Minutes)
    
#     # Create a Data Feed
#     cerebro.addanalyzer(bt.analyzers.PyFolio)
#     # cerebro.broker.setcommission(0.0003)
#     cerebro.broker.setcommission(
#             commission=0.0001)
#     # Add the Data Feed to Cerebro
#     # cerebro.adddata(data)
#     cerebro.broker.setcash(300000)
#     # clock the start of the process
#     # tstart = time.clock()

#     # Run over everything
#     stratruns = cerebro.run()

#     # #########################################
#     # filename = "plot_output.png"
#     # temp_fig_path = os.path.join(os.getcwd(), filename)
    
#     # figs = cerebro.plot(style='candle')
#     # fig = figs[0][0]

#     # # Adjust the figure size
#     # fig.set_size_inches(14, 8)

#     # # Save the figure with a defined DPI
#     # fig.savefig(temp_fig_path, dpi=300)
#     #########################################
#     # print("Final Value: ", cerebro.broker.get_fina)
#     # clock the end of the process
#     # tend = time.clock()

#     print('==================================================')
#     for stratrun in stratruns:
#         for strat in stratrun:
#             print('--------------------------------------------------')
#             print(strat.p._getkwargs())
#             # print()
#             pyfoliozer = strat.analyzers.getbyname('pyfolio')
#             returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
#             print(transactions) 
#             pf.create_simple_tear_sheet(
#                 returns,
#                 positions=positions,
#                 transactions=transactions,
#                 )
            
#             fig = plt.gcf()

#             # Save the figure with the timestamp as the name
#             timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#             file_path = os.path.join("./pyfolio", f'{timestamp}.png')
#             transactions.to_csv(os.path.join("./pyfolio", f'transactions-{timestamp}.csv'))
#             positions.to_csv(os.path.join("./pyfolio", f'positions-{timestamp}.csv'))
#             returns.to_csv(os.path.join("./pyfolio", f'returns-{timestamp}.csv'))

#             fig.savefig(file_path)
#     print('==================================================')

#     # print out the result
#     # print('Time used:', str(tend - tstart))