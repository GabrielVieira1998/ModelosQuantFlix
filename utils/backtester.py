from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib
matplotlib.use('Agg')
# Import the backtrader platform
import backtrader.analyzers as btanalyzers
import backtrader as bt
import pandas as pd
# Importando classe da estratégia cTrends
# from cTrends import cTrendsStrategy
# from Trends import trendsStrategy
import argparse
from fpdf import FPDF
from decimal import *
from utils.analyzer import analyze_backtest
import os

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


def backtester(strategy, params, data, cash=100000, commission=0.015, generate_report=False, bt_name='single_run', folder_name=False):
    
    args = parse_args()
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=True) # writer=True # stdstats=Falsewriter=False, stdstats=True
    #
    cerebro.addobserver(bt.observers.Value)
    
    cerebro.addobserver(bt.observers.LogReturns, timeframe=bt.TimeFrame.Days, compression=1)
    # Add a strategy
    
    cerebro.addstrategy(strategy, **params)
    feed = bt.feeds.PandasData(dataname=data)
    # Add the Data Feed to Cerebro
    cerebro.adddata(feed)

    cerebro.broker.setcash(cash) # Tenho que aumentar capital nos robôs que dão prejuízo
    # Set the commission
    cerebro.broker.setcommission(commission=commission)

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
        
        # fig = cerebro.plot()[0][0] # start=50, end=115 Posso colocar indices para olhar alguma data específica

        # analyzers = strat[0].analyzers
        # analysis = analyzers.trades.get_analysis() 
        # params = strat[0].params   
        # locale.setlocale(locale.LC_ALL, 'en_US.utf8') 
        # getcontext().prec = 2
        
        table_data = analyze_backtest(strat)
        
        # Determine the directory path
        dir_path = f'./results/{strategy.name}/{folder_name}'

        # Check if the directory exists, if not, create it
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        pd.DataFrame(table_data).to_csv(f'{dir_path}/{bt_name}_result.csv', index=False)
        # temp_fig_path = tempfile.NamedTemporaryFile(suffix='.png').name
        # fig = cerebro.plot()[0][0]

        # # Adjust the figure size
        # fig.set_size_inches(14, 8)

        # # Save the figure with a defined DPI
        # fig.savefig(temp_fig_path, dpi=300)

        # # Get the current date and time
        # now = 

        # # Convert the datetime object to a string with a specific format
        # 

        # # Create the PDF
        # pdf_path = f'../backtestResults/{strategy.name}/{formatted_date}/{bt_name}_result.pdf'
        # pdf = UpdatedPDF()
        # pdf.set_auto_page_break(auto=True, margin=15)
        # pdf.add_page()
        # pdf.chapter_title('Optimization Metrics')
        # pdf.chapter_body(table_data)
        # pdf.chapter_image(temp_fig_path)  # Adjusted this line for correct image placement
        # pdf.output(pdf_path)

    
    
    return strat[0]
    
