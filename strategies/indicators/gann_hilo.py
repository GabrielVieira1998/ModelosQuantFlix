import backtrader as bt
import backtrader.indicators as btind

class Gann_hilo_activator(bt.Indicator):
    lines = ('hilo',)
    params = (
        ('period', 3),
    )
    
    plotinfo = dict(subplot=False)
    plotlines = dict(
        hilo=dict(color='red', _name='HiLo-Low'),
    )

    def __init__(self):
        self.addminperiod(3)  # Minimum period required for calculation

        self.hilo_high_avg = btind.MovingAverageSimple(self.data.high, period=self.params.period)
        self.hilo_low_avg = btind.MovingAverageSimple(self.data.low, period=self.params.period)


    def next(self):
        if self.data.close[0] < self.hilo_low_avg[0]:# and self.lines.hilo[-1] == self.hilo_low_avg[-1]:
            self.lines.hilo[0] = self.hilo_high_avg[0]
            self.plotlines.hilo.color = 'green'
        elif self.data.close[0] > self.hilo_high_avg[0]:# and self.lines.hilo[-1] == self.hilo_high_avg[-1]:
            self.lines.hilo[0] = self.hilo_low_avg[0]
            self.plotlines.hilo.color = 'red'
        else:
            self.lines.hilo[0] = self.lines.hilo[-1]  # Preserve previous hilo value
# Teste