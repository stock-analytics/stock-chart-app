from pathlib import Path
def test_T15_stale_async_response_guard():
 s=Path('../frontend/src/App.tsx').read_text();assert '++request.current' in s and 'id === request.current' in s
def test_T15_analysis_patterns_share_parent_snapshot():
 import sys;sys.path.insert(0,'.')
 from datetime import date
 from app.providers.synthetic import SyntheticProvider
 from app.analysis.service import analyze
 r=SyntheticProvider().fetch_daily('DEMO_X',date(2023,1,1),date(2025,1,1));a=analyze('DEMO_X',r.bars,'1d','all',snapshot_id='generation-A');assert all(p['snapshot_id']=='generation-A' for p in a['patterns'])
