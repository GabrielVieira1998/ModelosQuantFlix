import pandas as pd
import os
def analyze_optimization(x):
    analysis0 = x[0].analyzers.trades.get_analysis()
    analysis1 = x[1].analyzers.trades.get_analysis()
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
                    'Drawdown %': analysers0.dd.get_analysis()['max']['drawdown'],
                    'Sharpe Ratio': analysers0.sharpe.get_analysis()['sharperatio'],
                    'Net Profit': analysis0['pnl']['net']['total'],
                    'SQN': analysers0.sqn.get_analysis()['sqn'],
                    'Profit Factor': abs(analysis0['won']['pnl']['total']/analysis0['lost']['pnl']['total']),
                    'Total Trades': analysis0['total']['closed'],
                    'Taxa de acerto': analysis0['won']['total']/analysis0['total']['closed'],
                    'Drawdown %_OS': analysers1.dd.get_analysis()['max']['drawdown'],
                    'Sharpe Ratio_OS': analysers1.sharpe.get_analysis()['sharperatio'],
                    'Net Profit_OS': analysis1['pnl']['net']['total'],
                    'SQN_OS': analysers1.sqn.get_analysis()['sqn'],
                    'Profit Factor_OS': abs(analysis1['won']['pnl']['total']/analysis1['lost']['pnl']['total']),
                    'Total Trades_OS': analysis1['total']['closed'],
                    'Taxa de acerto_OS': analysis1['won']['total']/analysis1['total']['closed']
                    }]
    return result

def analyze_backtest(x):
    analysis0 = x[0].analyzers.trades.get_analysis()
    analysers0 = x[0].analyzers
    if 'pnl' in analysis0 and analysis0['total']['closed'] > 1 and analysis0['won']['pnl']['total'] != 0:
        if analysis0['lost']['pnl']['total'] == 0:
            analysis0['lost']['pnl']['total'] = 1

        x0_dict = {attr: getattr(x[0].params, attr) for attr in dir(x[0].params) if not callable(getattr(x[0].params, attr)) and not attr.startswith("__")}

        result = [{**x0_dict,
            'dd_perc': analysers0.dd.get_analysis()['max']['drawdown'],
            'sharpe': analysers0.sharpe.get_analysis()['sharperatio'],
            'pnl_total': analysis0['pnl']['net']['total'],
            'sqn': analysers0.sqn.get_analysis()['sqn'],
            'profit_factor': abs(analysis0['won']['pnl']['total']/analysis0['lost']['pnl']['total']),
            'trades': analysis0['total']['closed'],
            'win_ratio': analysis0['won']['total']/analysis0['total']['closed'],
            }]
    return result

def normalizeDf(df):
    return (df-df.min())/(df.max()-df.min())
    
def get_top_results(IndicatorsJson):
    df = pd.DataFrame([{**sublist[0], **sublist[2]} for sublist in IndicatorsJson])
    
    df_norm = normalizeDf(df[['Drawdown %', 'Net Profit', 'Profit Factor', 'Drawdown %_OS', 'Net Profit_OS', 'Profit Factor_OS', 'Total Trades_OS']]).dropna(axis=1)
    df['quality'] = ((df_norm['Net Profit']*0.3)-(df_norm['Drawdown %']*0.3))+((df_norm['Net Profit_OS']+df_norm['Profit Factor_OS']*0.2)-df_norm['Drawdown %_OS']*2)+df_norm['Total Trades_OS']
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
