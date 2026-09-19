import sys;sys.path.insert(0,'.')
from tests.helpers import line_bars
from app.analysis.window_patterns import detect_converging
def test_T06_breakout_not_reported_before_prefix_contains_it():
 b,p,a=line_bars(60,0,5/59,'up');assert detect_converging('X','1d',b[:-1],p,a[:-1])[0]['state']=='forming';assert detect_converging('X','1d',b,p,a)[0]['events'][-1]['index']==60
