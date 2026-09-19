import sys;sys.path.insert(0,'.')
from datetime import date,timedelta
from app.models import Bar
from app.analysis.pivots import extract_pivots
def test_T05_known_at_right_tie_and_dual_removed():
 v=[1,2,4,4,3,2,1,2,3,2,1];b=[Bar(date(2024,1,1)+timedelta(i),x,x+1,x-1,x,1, x) for i,x in enumerate(v)];p=extract_pivots(b);assert all(x.known_at==b[x.index+3].session_date for x in p);assert all(x.index!=2 for x in p)
