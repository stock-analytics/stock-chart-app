import sys;sys.path.insert(0,'.')
from datetime import date
from app.providers.synthetic import SyntheticProvider
from app.analysis.service import analyze
def test_T07_snapshot_asof_deterministic_across_display_ranges():
 bars=SyntheticProvider().fetch_daily('DEMO_X',date(2020,1,1),date(2025,1,1)).bars;a=analyze('DEMO_X',bars,'1d','6mo',date(2024,1,1),'s');b=analyze('DEMO_X',bars,'1d','all',date(2024,1,1),'s');assert a['patterns']==b['patterns'] and a['snapshot_id']==b['snapshot_id']=='s'
