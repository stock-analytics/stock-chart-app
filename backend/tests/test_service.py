from datetime import date,timedelta
import sys
sys.path.insert(0,'.')
from app.providers.synthetic import SyntheticProvider
from app.analysis.service import analyze

def test_prefix_determinism_ranges_and_timeframes_T06_T07_T21():
 r=SyntheticProvider().fetch_daily('DEMO_X',date(2018,1,1),date(2025,1,1));
 for tf in ('1d','1wk','1mo'):
  a=analyze('DEMO_X',r.bars,tf,'6mo',date(2024,1,1));b=analyze('DEMO_X',r.bars,tf,'all',date(2024,1,1));assert a['snapshot_id']==b['snapshot_id'];assert a['patterns']==b['patterns'];assert all(x['date']<='2024-01-01' for x in a['bars'])
def test_search_caps_T22():
 r=SyntheticProvider().fetch_daily('DEMO_X',date(2010,1,1),date(2025,1,1));a=analyze('DEMO_X',r.bars,'1d','all');assert a['metadata']['truncated']
