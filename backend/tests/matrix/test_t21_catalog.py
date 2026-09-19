import sys;sys.path.insert(0,'.')
from app.analysis.patterns import catalog,ALL_TYPES
def test_T21_catalog_all_implemented():
 c=catalog();assert {x['type'] for x in c}==set(ALL_TYPES);assert len(c)==21;assert all(x['implemented'] for x in c)
from datetime import date,timedelta
import pytest
from app.models import Bar,Pivot
from app.analysis.harmonic_state import candidates
CASES={'crab':(.618,.75,1.618),'deep_crab':(.886,.6,1.618),'gartley':(.618,(2*.618-.786)/.618,.786),'bat':(.5,.55,.886),'butterfly':(.786,.6,1.27)}
@pytest.mark.parametrize('tf',('1d','1wk','1mo'))
@pytest.mark.parametrize('kind',CASES)
def test_T21_harmonics_execute_all_timeframes(tf,kind):
 b,c,d=CASES[kind];prices=[100,200,200-100*b,200-100*b+100*b*c,200-100*d];idx=[5,15,25,35,45];bars=[]
 for i in range(55):
  close=prices[-1] if i==45 else 150;bars.append(Bar(date(2020,1,1)+timedelta(i),close,close+1,close-1,close,1,close))
 piv=[Pivot(i,'low' if n%2==0 else 'high',v,bars[i].session_date,bars[i+3].session_date) for n,(i,v) in enumerate(zip(idx,prices))]
 assert kind in [x['type'] for x in candidates('X',tf,bars,piv,[2.0]*len(bars))]
from app.analysis.window_patterns import detect_converging
from tests.helpers import line_bars
GEOMETRY={'ascending_triangle':(0,5,'up'),'descending_triangle':(-5,0,'down'),'symmetrical_triangle':(-2.5,2.5,'up'),'rising_wedge':(1,6,'down'),'falling_wedge':(-6,-1,'up')}
@pytest.mark.parametrize('tf,w',[('1d',60),('1wk',26),('1mo',12)])
@pytest.mark.parametrize('kind',GEOMETRY)
def test_T21_converging_types_execute_all_timeframes(tf,w,kind):
 u,l,d=GEOMETRY[kind];b,p,a=line_bars(w,u/(w-1),l/(w-1),d);assert kind in [x['type'] for x in detect_converging('X',tf,b,p,a)]
