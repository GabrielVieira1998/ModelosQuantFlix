import backtrader as bt
import backtrader.indicators as btind
import statistics


class BbWidth(bt.Indicator):

    lines = ('bbWidth', 'first', 'second', )

    params = (    
        ('period', 20),
    )    

    plotinfo = dict(subplot=True)

    plotlines = dict(
        bbWidth=dict(color='blue', _name='BB Width'),
        first=dict(color='green'),
        second=dict(color='red')
    )


    def __init__(self):
        
        self.addminperiod(self.params.period)  # Minimum period required for calculation
        self.bb = btind.BollingerBands(self.datas[0], period=round(self.params.period))
        
        

    def next(self):
        
        self.lines.bbWidth[0] = (self.bb.top - self.bb.bot) / self.bb.mid #bt.indicators.BollingerBandsPct(period=20)
        # self.lines.upper[0] = statistics.mean(self.lines.bbWidth.get(ago=0, size=self.params.period)) + statistics.stdev(self.lines.bbWidth.get(ago=0, size=self.params.period))*1.25
        self.lines.first[0] = [round(q,2) for q in statistics.quantiles(self.lines.bbWidth.get(ago=0, size=self.lines.bbWidth.__len__()), n=5)][1]
        self.lines.second[0] = [round(q,2) for q in statistics.quantiles(self.lines.bbWidth.get(ago=0, size=self.lines.bbWidth.__len__()), n=5)][3]
