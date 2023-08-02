from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.analyzers as btanalyzers
from utils.backtester import backtester
from tqdm.auto import tqdm
import datetime

from utils.analyzer import analyze_optimization, get_top_results, consolidate_csvs
import inspect


class Optmizer():
    def __init__(self, strategy, params, data_bt, data_opt, cash=100000):
        self.pbar = tqdm(desc='Opt runs', leave=True, position=1, unit='run', colour='violet')
        self.strategy = strategy
        self.params = params
        self.data_bt = data_bt
        self.data_opt = data_opt
        self.cash = cash 
        self.results = None
        self.cerebro = bt.Cerebro()

    def _callback(self, strategy):
        
        self.pbar.update()
        params_dict = {attr: getattr(strategy[0].params, attr) for attr in dir(strategy[0].params) if not callable(getattr(strategy[0].params, attr)) and not attr.startswith("__")}

        strategy.append(backtester(strategy= self.strategy, params=params_dict, data=self.data_bt, generate_report=False))
        
        
        return strategy
    
    def optmize(self):
        # Create a self.cerebro entity

        feed = bt.feeds.PandasData(dataname=self.data_opt)
        # Add the Data Feed to Cerebro
        self.cerebro.adddata(feed)
        
         # Add a self.strategy
        self.cerebro.optstrategy(
            self.strategy, **self.params
            )

        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
        # Add a FixedSize sizer according to the stake
        # Adiciono na classe analyzer os indicadores de resultado que quero buscar
        for name, obj in inspect.getmembers(btanalyzers):
            if inspect.isclass(obj) and name in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'Transactions', 'TradeAnalyzer', 'VWR']:#'TimeReturn','Transactions','PyFolio','PositionsValue', 'LogReturnsRolling', 'GrossLeverage','Calmar', 
                self.cerebro.addanalyzer(obj, _name=name)

        # Set the commission
        self.cerebro.broker.setcommission(commission=0.0)
        
        # Variável optimizationResults retorna uma lista de todos os resultados
        self.cerebro.optcallback(self._callback)
        # self.cerebro.optreturn = False  # If optimization is being used
        self.results = self.cerebro.run(maxcpus=1)     # Force single-core execution

        # self.results = self.cerebro.run()

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