import backtrader as bt
import backtrader.indicators as btind
import statistics


class BbWidth(bt.Indicator):

    lines = ('bbWidth', 'first', 'second', )

    params = (    
        ('period', 20),
        ('n', 11),
        ('firstLineQuartile', 0),
        ('secondLineQuartile', 5),
    )    

    plotinfo = dict(subplot=True)

    plotlines = dict(
        bbWidth=dict(color='blue', _name='BB Width'),
        first=dict(color='green'),
        second=dict(color='red')
    )


    def __init__(self):
        
        self.addminperiod(self.params.period)  # Minimum period required for calculation
        
        self.bb = btind.BollingerBands(self.datas[0], period=self.params.period)
        self.lines.bbWidth = (self.bb.top - self.bb.bot) / self.bb.mid
        # print("(self.params.n > self.params.secondLineQuartile) and (self.params.secondLineQuartile > self.params.firstLineQuartile) and (self.params.n > (self.params.secondLineQuartile+1)): ", (self.params.n > self.params.secondLineQuartile) and (self.params.secondLineQuartile > self.params.firstLineQuartile) and (self.params.n > (self.params.secondLineQuartile+1)))
        if (self.params.n > self.params.secondLineQuartile) and (self.params.secondLineQuartile > self.params.firstLineQuartile) and (self.params.n > (self.params.secondLineQuartile+1)):
            self.condicao = True
        else: 
            self.condicao = False
        

    def next(self):
        
        if self.condicao == True:
            self.lines.first[0] = [round(q,2) for q in statistics.quantiles(self.lines.bbWidth.get(ago=0, size=self.lines.bbWidth.__len__()), n=self.params.n)][self.params.firstLineQuartile]
            self.lines.second[0] = [round(q,2) for q in statistics.quantiles(self.lines.bbWidth.get(ago=0, size=self.lines.bbWidth.__len__()), n=self.params.n)][self.params.secondLineQuartile]
        else:
            self.lines.first[0] = 0.05
            self.lines.second[0] = 0.2
            # Será que tenho que atribuir um valor para n aqui?? Primeira hipótese

        