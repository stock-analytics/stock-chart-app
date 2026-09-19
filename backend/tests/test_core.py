from datetime import date,timedelta
import math,sys
sys.path.insert(0,'.')
from app.models import Bar
from app.analysis.indicators import sma,aggregate,atr,daily_sma_for_aggregate
from app.analysis.pivots import extract_pivots
from app.analysis.harmonic import classify,ratios
from app.providers.validation import normalize_symbol,adjusted_prices
from app.analysis.patterns import catalog

def bars(n=220):
 d=date(2024,1,1); out=[]
 for i in range(n):
  p=100+i;out.append(Bar(d+timedelta(days=i),p,p+2,p-2,p+1,100+i))
 return out
def test_sma_boundaries_T01():
 assert sma(list(range(1,30)),30)[-1] is None
 assert sma(list(range(1,31)),30)[-1]==15.5
 assert sma(list(range(1,76)),75)[-1]==38
 assert sma(list(range(1,201)),200)[-1]==100.5
 assert sma([1,2,None]+list(range(30)),30)[-1]==14.5
def test_aggregate_and_daily_sma_T02_T03():
 b=bars(210); b[2]=Bar(b[2].session_date,b[2].open,b[2].high,b[2].low,b[2].close,None)
 w=aggregate(b,'1wk'); assert w[0].open==100 and w[0].volume is None
 m=aggregate(b,'1mo'); assert m[0].high==132 and m[0].low==98
 vals=daily_sma_for_aggregate(b,w,30); assert vals[-1]!=sum(x.close for x in w[-30:])/30
 assert all(x.is_final for x in m)
def test_adjust_validation_T04():
 prices,f=adjusted_prices(90,110,80,100,50);assert f==.5 and prices==(45,55,40,50)
 for bad in (None,0,float('nan')):
  try: adjusted_prices(1,2,1,1,bad)
  except ValueError: pass
  else: assert False
def test_pivots_known_at_tie_and_double_T05():
 vals=[1,2,3,4,3,2,1,1,2,3,2,1]
 b=[Bar(date(2024,1,1)+timedelta(days=i),v,v+.5,v-.5,v,1) for i,v in enumerate(vals)]
 p=extract_pivots(b);assert p[0].known_at==b[p[0].index+3].session_date
 # equal highs in a window select the rightmost
 assert all(x.index!=2 for x in p)
def test_harmonic_positive_reflection_and_invalid_T09_T10():
 cases={'crab':(.618,.75,1.618),'deep_crab':(.886,.6,1.618),'gartley':(.618,(2*.618-.786)/.618,.786),'bat':(.5,.55,.886),'butterfly':(.786,.6,1.27)}
 for name,(b,c,d) in cases.items():
  pts=[100,200,200-100*b,200-100*b+100*b*c,200-100*d]
  assert any(x[0]==name and x[1]=='bullish' for x in classify(pts)),(name,ratios(pts))
  reflected=[300-x for x in pts];assert any(x[0]==name and x[1]=='bearish' for x in classify(reflected))
 assert classify([1,1,1,1,1])==[]
def test_symbol_security_and_catalog_T17_T21():
 assert normalize_symbol(' ７２０３ ')=='7203.T'
 for value in ('https://x','1;DROP','ABCD','7203.US','720\n'):
  try:normalize_symbol(value)
  except ValueError:pass
  else:assert False
 c=catalog();assert len(c)==21 and all(x['implemented'] for x in c)
def test_atr_wilder():
 b=bars(15);a=atr(b);assert all(x is None for x in a[:13]);assert a[13]==4 and a[14]==4
