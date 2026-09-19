import sys;sys.path.insert(0,'.')
from tests.test_core import bars
from app.analysis.indicators import aggregate,daily_sma_for_aggregate
def test_T03_weekly_chart_uses_daily_not_weekly_sma():
 d=bars(210);w=aggregate(d,'1wk');actual=daily_sma_for_aggregate(d,w,30)[-1];assert actual!=sum(x.close for x in w[-30:])/30
