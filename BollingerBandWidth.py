import backtrader as bt
import backtrader.indicators as btind


class BbWidth(bt.Indicator):

    lines = ('bbWidth',)

    params = (    
        ('period', 20),
    )    

    plotinfo = dict(subplot=True)

    plotlines = dict(
        bbWidth=dict(color='blue', _name='BB Width'),
    )


    def __init__(self):
        
        self.addminperiod(3)  # Minimum period required for calculation
        self.bb = btind.BollingerBands(self.datas[0], period=self.params.period)
        
        

    def next(self):

        self.lines.bbWidth[0] = (self.bb.top - self.bb.bot) / self.bb.mid #bt.indicators.BollingerBandsPct(period=20)

