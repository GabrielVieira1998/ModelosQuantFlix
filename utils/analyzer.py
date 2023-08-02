import pandas as pd
import os
from pprint import pprint
from collections import OrderedDict

def analyze_optimization(x):
    analysis0 = x[0].analyzers.TradeAnalyzer.get_analysis()
    analysis1 = x[1].analyzers.TradeAnalyzer.get_analysis()
    analysers0 = x[0].analyzers
    analysers1 = x[1].analyzers
    if 'pnl' in analysis0 and analysis0['total']['closed'] > 1 and analysis0['won']['pnl']['total'] != 0:
        if analysis0['lost']['pnl']['total'] == 0:
            analysis0['lost']['pnl']['total'] = 1
        elif analysis1['lost']['pnl']['total'] == 0:
            analysis1['lost']['pnl']['total'] = 1
        # print(x[0].analyzers.trades.get_analysis())
        x0_dict = {attr: getattr(x[0].params, attr) for attr in dir(x[0].params) if not callable(getattr(x[0].params, attr)) and not attr.startswith("__")}
        # Alterar '_OS' para minusculo
        x1_dict = {attr+'_OS': getattr(x[1].params, attr) for attr in dir(x[1].params) if not callable(getattr(x[1].params, attr)) and not attr.startswith("__")}
        result = [{**x0_dict},{**x1_dict},{
            'dd_perc': analysers0.DrawDown.get_analysis()['max']['drawdown'],
            'sharpe': analysers0.SharpeRatio.get_analysis()['sharperatio'],
            'pnl_total': analysis0['pnl']['net']['total'],
            'sqn': analysers0.SQN.get_analysis()['sqn'],
            'profit_factor': abs(analysis0['won']['pnl']['total']/analysis0['lost']['pnl']['total']),
            'trades': analysis0['total']['closed'],
            'win_ratio': analysis0['won']['total']/analysis0['total']['closed'],
            'dd_perc_OS': analysers1.DrawDown.get_analysis()['max']['drawdown'],
            'sharpe_OS': analysers1.SharpeRatio.get_analysis()['sharperatio'],
            'pnl_total_OS': analysis1['pnl']['net']['total'],
            'sqn_OS': analysers1.SQN.get_analysis()['sqn'],
            'profit_factor_OS': abs(analysis1['won']['pnl']['total']/analysis1['lost']['pnl']['total']),
            'trades_OS': analysis1['total']['closed'],
            'win_ratio_OS': analysis1['won']['total']/analysis1['total']['closed']
            }]
        
        return result
    
    # print("Condition not met for x[0].params: ", x[0].params)
    # print("Details: 'pnl' in analysis0:", 'pnl' in analysis0, 
    #         "analysis0['total']['closed']:", analysis0['total']['closed'], 
    #         "analysis0['won']['pnl']['total']:", analysis0['won']['pnl']['total'])
    return [{},{},{}]
    
# def analyze_optimization(x):
    
#     x0_dict = {attr: getattr(x[0].params, attr) for attr in dir(x[0].params) if not callable(getattr(x[0].params, attr)) and not attr.startswith("__")}
#     # Alterar '_OS' para minusculo
#     x1_dict = {attr+'_OS': getattr(x[1].params, attr) for attr in dir(x[1].params) if not callable(getattr(x[1].params, attr)) and not attr.startswith("__")}
        
#     for a in x[0].analyzers._items:
#         if a.__class__.__name__ in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'TradeAnalyzer', 'VWR']:
#             analysis = a.get_analysis()
#             x0_dict.update({a.__class__.__name__: flatten_dict(analysis)})
#             x1_dict.update({a.__class__.__name__: flatten_dict(analysis)})

#     result = [{**x0_dict}, {**x1_dict}]
#     # Posso tentar retornar apenas o dicionário concatenando x0 e x1 aí na hora de gerar um dataframe no get top results, não preciso fazer aquele for maluco.
#     # Preciso adicionar '_os' no final de cada valor dentro do dicionário x1_dict e criar o profit factor.


    #return result
def analyze_backtest(x, folder_name, bt_name):
    
    params_dict = {attr: getattr(x[0].params, attr) for attr in dir(x[0].params) if not callable(getattr(x[0].params, attr)) and not attr.startswith("__")}
    merged_dict = {}
    transactions = {}
    
    for a in x[0].analyzers._items:
        if a.__class__.__name__ in ['AnnualReturn', 'DrawDown', 'TimeDrawDown',  'PeriodStats', 'Returns', 'SharpeRatio', 'SharpeRatio_A', 'SQN', 'TradeAnalyzer', 'VWR']:
            analysis = a.get_analysis()
            params_dict.update({a.__class__.__name__: flatten_dict(analysis)})
        else:   
            analysis = a.get_analysis()                        
            transactions.update(flatten_dict(analysis))
        # pprint(dir(a))
        # pprint(dict(analysis))
        # print(type(analysis))
        
    # Determine the directory path
    dir_path = f'./results/{x[0].name}/{folder_name}/{bt_name}'
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    ## Criar dataframe das metrics e retornar dataframe para concatenar todos eles 
    df_metrics = pd.DataFrame(flatten_dict(params_dict), index=['value'])
    
    df_metrics.T.to_csv(f'{dir_path}/metrics.csv', index=True, index_label='metric')
    
    # Create DataFrame using the provided data and structure
    df_transactions = pd.DataFrame(columns=['amount', 'price', 'sid', 'symbol', 'value'])
    # print(transactions.items())
    for date, values_list in transactions.items():
        for value in values_list:
            df_transactions.loc[date] = value

    df_transactions.to_csv(f'{dir_path}/transactions.csv', index=True, index_label='date')
    
    ######
    return df_metrics # None
   

def normalizeDf(df):
    return (df-df.min())/(df.max()-df.min())
    
def get_top_results(IndicatorsJson):
    df = pd.DataFrame([{**sublist[0], **sublist[2]} for sublist in IndicatorsJson])
    
    df_norm = normalizeDf(df[['dd_perc', 'pnl_total', 'profit_factor', 'dd_perc_OS', 'pnl_total_OS', 'profit_factor_OS', 'trades_OS']]).dropna(axis=1)
    df['quality'] = ((df_norm['pnl_total']*0.3)-(df_norm['dd_perc']*0.3))+((df_norm['pnl_total_OS']+df_norm['profit_factor_OS']*0.2)-df_norm['dd_perc_OS']*2)+df_norm['trades_OS']
    df_sorted = df.sort_values('quality', ascending=False)
    return df_sorted.head(10)



def consolidate_csvs(directory_path, output_filename):
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    
    # Read each CSV file into a DataFrame, set filename (without extension) as the index
    dataframes = []
    for csv_file in csv_files:
        df = pd.read_csv(os.path.join(directory_path, csv_file))
        df['filename'] = os.path.splitext(csv_file)[0]  # Get filename without extension
        dataframes.append(df.set_index('filename'))
    
    # Concatenate all the DataFrames
    consolidated_df = pd.concat(dataframes)
    
    # Save the consolidated DataFrame to a new CSV file
    consolidated_df.to_csv(os.path.join(directory_path, output_filename))

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten a nested dictionary structure."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, (dict, OrderedDict)):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items