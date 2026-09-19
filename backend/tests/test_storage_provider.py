from datetime import date,timedelta
import sys
sys.path.insert(0,'.')
from app.providers.synthetic import SyntheticProvider
from app.storage.database import Database

def test_synthetic_is_explicit_and_deterministic_T07_T12(tmp_path):
 p=SyntheticProvider(1);a=p.fetch_daily('DEMO_X',date(2024,1,1),date(2024,2,1));b=p.fetch_daily('DEMO_X',date(2024,1,1),date(2024,2,1));assert [x.close for x in a.bars]==[x.close for x in b.bars]
 try:p.fetch_daily('7203.T',date.today(),date.today()+timedelta(1))
 except ValueError:pass
 else:assert False
def test_snapshot_dedup_and_watchlist_T20(tmp_path):
 p=SyntheticProvider();r=p.fetch_daily('DEMO_X',date(2024,1,1),date(2024,2,1));d=Database(tmp_path/'x.db');a=d.save_snapshot('DEMO_X','synthetic',r.bars,r.fetched_at);b=d.save_snapshot('DEMO_X','synthetic',r.bars,r.fetched_at);assert a==b
 for i in range(20):d.add_watch(f'{i:04d}.T')
 try:d.add_watch('9999.T')
 except ValueError:pass
 else:assert False
