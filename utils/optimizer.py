from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.analyzers as btanalyzers
from utils.backtester import backtester
from tqdm.auto import tqdm
import datetime

from utils.analyzer import analyze_optimization, get_top_results, consolidate_csvs
import inspect

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
            

            
            # print('---next len %d - counter %d - data %s' % (len(self), self.counter, self.datas[0].datetime.time(0)))

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
class Optmizer():
    def __init__(self, strategy, params, data_bt, data_opt, cash=100000):
        self.pbar = tqdm(desc='Opt runs', leave=True, position=1, unit='run', colour='violet')
        self.strategy = strategy
        self.params = params
        self.data_bt = data_bt
        self.data_opt = data_opt
        self.cash = cash 
        self.results = None
        self.cerebro = bt.Cerebro(maxcpus=None)

    def _callback(self, strategy):
        
        self.pbar.update()
        params_dict = {attr: getattr(strategy[0].params, attr) for attr in dir(strategy[0].params) if not callable(getattr(strategy[0].params, attr)) and not attr.startswith("__")}

        strategy.append(backtester(strategy= MonkeyScalper, params=params_dict, data=self.data_bt, generate_report=False))
        
        
        return strategy
    
    def optmize(self):
        # Create a self.cerebro entity

        # feed = bt.feeds.PandasData(dataname=self.data_opt)
        # # Add the Data Feed to Cerebro
        # self.cerebro.adddata(feed)
        
        #  # Add a self.strategy
        # self.cerebro.optstrategy(
        #     self.strategy, **self.params
        #     )

        # self.cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
         # Add a self.strategy
        self.cerebro.optstrategy(
            self.strategy, **self.params
            )
        
        feed = bt.feeds.PandasData(dataname=self.data_opt, datetime=None, open=1, high=1, low=1, close=1, volume=4)
        
        # data = self.cerebro.resampledata(feed,
        #                timeframe=bt.TimeFrame.Seconds)
        
        self.cerebro.replaydata(feed,
                       timeframe=bt.TimeFrame.Minutes)
        self.cerebro.broker.setcash(self.cash) # Tenho que aumentar capital nos robôs que dão prejuízo
        # Set the commission
        # cerebro.broker.setcommission(commission=commission)
        self.cerebro.broker.setcommission(
            commission=0.00027)
        # Add a FixedSize sizer according to the stake
        # Adiciono na classe analyzer os indicadores de resultado que quero buscar
        for name, obj in inspect.getmembers(btanalyzers):
            if inspect.isclass(obj) and name in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'Transactions', 'TradeAnalyzer', 'VWR']:#'TimeReturn','Transactions','PyFolio','PositionsValue', 'LogReturnsRolling', 'GrossLeverage','Calmar', 
                self.cerebro.addanalyzer(obj, _name=name)
        # Set the commission
        # self.cerebro.broker.setcommission(commission=0.0)
        # Variável optimizationResults retorna uma lista de todos os resultados
        self.cerebro.optcallback(self._callback)
        # self.cerebro.optreturn = False  # If optimization is being used
        self.results = self.cerebro.run()     # Force single-core execution
        self.getBestRuns()

    def getBestRuns(self):
        results = []
        formatted_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # Faço um for dentro de toda a lista de resultados da otimização e dou um append na lista que uso para criar o json
        for x in self.results:
            result = analyze_optimization(x)
            if result[0]:  # Check if the first dictionary is not empty
                results.append(result)
            # results.append(analyze_optimization(x))
            
        
        param_size = len(results[0][0])

        top_results = get_top_results(results)
        # print(top_results)
        count = 1
        for index, params in top_results.iloc[:, :param_size].astype(int).iterrows():
            backtester(
                strategy=self.strategy,
                params=params,
                data=self.data_bt,
                cash=self.cash,
                generate_report=True,
                bt_name=count,
                folder_name=formatted_date
                )
            count += 1
        
        
        consolidate_csvs(directory_path=f'./results/{self.strategy.name}/{formatted_date}', output_filename='consolidated_result.csv')