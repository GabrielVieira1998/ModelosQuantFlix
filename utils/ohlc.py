import datetime
import backtrader.feeds as btfeed

class MyHLOC(btfeed.GenericCSVData):
   
    def __init__(self, fromdate=None, todate=None, **kwargs):
        super(MyHLOC, self).__init__(**kwargs)
        
        if fromdate:
            self.p.fromdate = fromdate
        if todate:
            self.p.todate = todate


    params = (
        ('fromdate', datetime.datetime(2017,9,1)),
        ('todate', datetime.datetime(2023, 7, 31)),
        ('nullvalue', 0.0),
        ('dtformat', ('%Y-%m-%d')),
        ('tmformat', ('%H:%M:%S')),
        
        ('datetime', 0),
        ('time', 1),
        ('open', 2),
        ('high', 3),
        ('low', 4),
        ('close', 5),
        ('volume', 6),
        ('openinterest', -1)
    )

