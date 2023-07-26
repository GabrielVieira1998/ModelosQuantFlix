from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Import the backtrader platform
import backtrader.analyzers as btanalyzers
import backtrader as bt
import pandas as pd
# Importando classe da estratégia cTrends
# from cTrends import cTrendsStrategy
# from Trends import trendsStrategy
from Vol import volStrategy
import argparse
import json
import uuid
from fpdf import FPDF
import tempfile
from decimal import *
import locale

class UpdatedPDF(FPDF):
    # def header(self):
    #     self.set_font('Arial', 'B', 12)
    #     self.cell(0, 10, 'Backtest Result', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 20, title, ln=True, align='C')

    def chapter_body(self, table_data):
        self.set_fill_color(135, 206, 250)
        self.set_font('Arial', 'B', 10)
        
        col1_width = 55
        col2_width = 135
        row_height = 6
        
        self.cell(col1_width, row_height, 'Parameters', 1, 0, 'C', fill=True)
        self.cell(col2_width, row_height, 'Value', 1, 1, 'C', fill=True)
        
        self.set_font('Arial', '', 10)
        self.set_fill_color(255)
        
        for row in table_data:
            self.cell(col1_width, row_height, str(row[0]), 1)
            self.cell(col2_width, row_height, str(row[1]), 1, align='C')
            self.ln()

    def chapter_image(self, image_path):
        self.image(image_path, x=10, y=self.get_y() + 5, w=190, h=90)


    
def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--timeframe', default='daily', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=2, required=False, type=int,
                        help='Compress n bars into 1')
    

    return parser.parse_args()


def backtester(strategy, params, data, generate_report=False, cash=100000): 
    
    args = parse_args()
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=True) # writer=True # stdstats=Falsewriter=False, stdstats=True
    #
    cerebro.addobserver(bt.observers.Value)
    
    cerebro.addobserver(bt.observers.LogReturns, timeframe=bt.TimeFrame.Days, compression=1)
    # Add a strategy
    
    cerebro.addstrategy(strategy, **params)
    # Create a data feed
    # yf_data = get_timeframe(dataname=yf.download('BTC-USD', '2023-01-01', '2023-06-21', interval = "1d"), 2)
    # data = bt.feeds.GenericCSVData(dataname='BTC_Hourly.csv',fromdate=datetime.datetime(2020, 1, 1),todate=datetime.datetime(2022, 1, 1),datetime=1,open=3,high=4,low=5,close=6,volume=7,openinterest=8)

    
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    # ##Handy dictionary for the argument timeframe conversion
    # tframes = dict(
    #     daily=bt.TimeFrame.Days,
    #     weekly=bt.TimeFrame.Weeks,
    #     monthly=bt.TimeFrame.Months)

    # # Add the resample data instead of the original
    # cerebro.resampledata(dataname=data,
    #                      timeframe=tframes[args.timeframe],
    #                      compression=args.compression)
    # Set our desired cash start
    cerebro.broker.setcash(cash) # Tenho que aumentar capital nos robôs que dão prejuízo
    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # # Print out the starting conditions
    initialDeposit = cerebro.broker.getvalue()

    # Adiciono na classe analyzer os indicadores de resultado do backtest
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')  # Add TradeAnalyzer
    
    # Run over everything
    strat = cerebro.run()  
    
    if generate_report == True:
        
        userId = str(uuid.uuid4())

        # json_path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/volStrategy/'+userId+'_'+'backtest_metrics.json'
        # fig_path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/volStrategy/'+userId+'_'+'plot.png'
        # # Lista dos resultados do backtest
        # with open(json_path , 'x') as json_file:
        #         json.dump(backtestResults, json_file)
        # Plot cerebro
        fig = cerebro.plot()[0][0] # start=50, end=115 Posso colocar indices para olhar alguma data específica
        # Set the desired figure size in inches
        # width = 16
        # height = 9
        # fig.set_size_inches(width, height)
        # Save the figure as a PNG file with the specified size
        # fig.savefig(fig_path, dpi=300)  # Adjust the DPI value as needed
        


        analyzers = strat[0].analyzers
        analysis = analyzers.trades.get_analysis() 
        params = strat[0].params   
        locale.setlocale(locale.LC_ALL, 'en_US.utf8') 
        getcontext().prec = 2
         
        table_data = [
            ('n_quartile', params.nQuartile),
            ('entry_line_quartile', params.secondLineQuartile),
            ('exit_line_quartile', params.firstLineQuartile),
            ('trade_reversion', params.tradeReversion),
            ('trade_trend', params.tradeTrend),
            ('period_bb', params.periodBB),
            ('muliplier', params.multiplicador),
            ('stop_loss', str(params.stopLoss*params.multiplicador)+'%'),
            ('initial_deposit', locale.currency(initialDeposit, grouping=True)),
            ('net_profit', locale.currency(analysis['pnl']['net']['total'], grouping=True)),
            ('max_drawdown_percentage', round(analyzers.dd.get_analysis()['max']['drawdown'], 2)),
            ('max_drawdown_currency', locale.currency(analyzers.dd.get_analysis()['max']['moneydown'])),
            ('sharpe_ratio', round(analyzers.sharpe.get_analysis()['sharperatio'],2)),
            ('total_return', (str(round(analysis['pnl']['net']['total']/initialDeposit*100,2))+'%')),
            ('sqn', round(analyzers.sqn.get_analysis()['sqn'],2)),
            ('profit_factor', round(abs(analysis['won']['pnl']['total']/analysis['lost']['pnl']['total']),2)),
            ('total_trades', analysis['total']['closed']),
            ('win_percentage', (str(round(analysis['won']['total']/analysis['total']['closed']*100,2))+'%')),
            ('lergest_profit_trade', locale.currency(analysis['won']['pnl']['max'])),
            ('largest_loss_trade', locale.currency(analysis['lost']['pnl']['max'])),
            ('average_profit_trade', locale.currency(analysis['won']['pnl']['average'])),
            ('average_loss_trade', locale.currency(analysis['lost']['pnl']['average'])),
            ('total_long_trades', analysis['long']['total']),
            ('long_trades_win_percentage', str(round(analysis['long']['won']/analysis['long']['total']*100,2))+'%'),
            ('total_short_trades', analysis['short']['total']),
            ('short_trades_win_percentage', str(round(analysis['short']['won']/analysis['short']['total']*100,2))+'%')
        ]
        

        temp_fig_path = tempfile.NamedTemporaryFile(suffix='.png').name
        fig = cerebro.plot()[0][0]

        # Adjust the figure size
        fig.set_size_inches(14, 8)

        # Save the figure with a defined DPI
        fig.savefig(temp_fig_path, dpi=300)

        # Get the current date and time
        now = datetime.datetime.now()

        # Convert the datetime object to a string with a specific format
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Create the PDF
        pdf_path = '/home/gabrielvieira/flix/backtest-bots/backtestResults/volStrategy/'+formatted_date+'_'+'result.pdf'
        pdf = UpdatedPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.chapter_title('Optimization Metrics')
        pdf.chapter_body(table_data)
        pdf.chapter_image(temp_fig_path)  # Adjusted this line for correct image placement
        pdf.output(pdf_path)

    
    
    return strat[0]
    
