import sys;sys.path.insert(0,'.')
from datetime import date
from app.models import Bar
from app.analysis.indicators import aggregate
def test_T02_week_month_ohlcv_null_and_finality():
 b=[Bar(date(2024,1,d),10+d,12+d,9+d,11+d,None if d==3 else 10,is_final=d<5) for d in (2,3,4,5)]
 w=aggregate(b,'1wk')[0];m=aggregate(b,'1mo')[0];assert (w.open,w.high,w.low,w.close,w.volume,w.is_final)==(12,17,11,16,None,False);assert m.volume is None
