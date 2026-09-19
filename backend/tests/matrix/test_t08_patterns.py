import sys;sys.path.insert(0,'.')
import pytest
from app.analysis.window_patterns import detect_converging
from tests.helpers import line_bars
@pytest.mark.parametrize('tf,w,kind,su_total,sl_total,breakout',[('1d',60,'ascending_triangle',0,5,'up'),('1wk',26,'descending_triangle',-5,0,'down'),('1mo',12,'symmetrical_triangle',-2.5,2.5,'up'),('1d',60,'rising_wedge',1,6,'down'),('1d',60,'falling_wedge',-6,-1,'up')])
def test_T08_window_types_form_and_break(tf,w,kind,su_total,sl_total,breakout):
 b,p,a=line_bars(w,su_total/(w-1),sl_total/(w-1),breakout);found=detect_converging('X',tf,b,p,a);assert any(x['type']==kind and x['state']=='conditions_met' for x in found)
from app.analysis.window_patterns import detect_flags,detect_pennants,detect_cups
from tests.helpers import flag_bars,cup_bars
@pytest.mark.parametrize('tf',('1d','1wk','1mo'))
@pytest.mark.parametrize('bull',(True,False))
def test_T08_flags_all_timeframes_directions(tf,bull):
 b,p,a=flag_bars(tf,bull,False);found=detect_flags('X',tf,b,p,a);assert any(x['type']==('bull_flag' if bull else 'bear_flag') and x['state']=='conditions_met' for x in found)
@pytest.mark.parametrize('tf',('1d','1wk','1mo'))
@pytest.mark.parametrize('bull',(True,False))
def test_T08_pennants_all_timeframes_directions(tf,bull):
 b,p,a=flag_bars(tf,bull,True);found=detect_pennants('X',tf,b,p,a);assert any(x['type']==('bull_pennant' if bull else 'bear_pennant') and x['state']=='conditions_met' for x in found)
@pytest.mark.parametrize('tf',('1d','1wk','1mo'))
def test_T08_cup_handle_all_timeframes(tf):
 b,p,a=cup_bars();found=detect_cups('X',tf,b,p,a);assert found and found[0]['type']=='cup_handle' and found[0]['state']=='conditions_met'
from app.analysis.window_patterns import _state_after
def test_T08_state_machine_invalid_before_expiry_and_terminal():
 b,p,a=line_bars(60,0,5/59,'down');fit=detect_converging('X','1d',b,p,a)[0];assert fit['state']=='invalidated';assert [e['state'] for e in fit['events']]==['forming','invalidated']
 b,p,a=line_bars(60,0,5/59,'none');upper=(0,110);lower=(0,102);
 b.extend([type(b[-1])(b[-1].session_date,b[-1].open,112,101,106,1,1) for i in range(61)]);state,_,_,events=_state_after(b,59,60,upper,lower,.25,'bullish');assert state=='expired' and events[-1]['state']=='expired'
from datetime import date,timedelta
from app.models import Bar,Pivot
from app.analysis.patterns import _pivot_patterns

def structural_fixture(tf,kind):
 P={'1d':20,'1wk':12,'1mo':6}[tf];gap={'1d':12,'1wk':4,'1mo':4}[tf];base=date(2020,1,1);bull=kind in ('double_bottom','triple_bottom','inverse_head_shoulders');n=P+gap+5;bars=[]
 for i in range(n):
  c=(120-i*2 if bull else 80+i*2) if i<P else 90
  bars.append(Bar(base+timedelta(i),c,c+2,c-2,c,100,c))
 if kind.startswith('double'):
  inds=[P,P+gap//2,P+gap];vals=[80,100,80] if bull else [100,80,100];kinds=['low','high','low'] if bull else ['high','low','high']
 elif kind.startswith('triple'):
  inds=[P,P+gap//4,P+gap//2,P+3*gap//4,P+gap];vals=[80,100,80,100,80] if bull else [100,80,100,80,100];kinds=['low','high','low','high','low'] if bull else ['high','low','high','low','high']
 else:
  inds=[P,P+gap//4,P+gap//2,P+3*gap//4,P+gap];vals=[80,90,70,90,80] if bull else [100,90,110,90,100];kinds=['low','high','low','high','low'] if bull else ['high','low','high','low','high']
 piv=[Pivot(i,k,v,bars[i].session_date,bars[min(i+3,n-1)].session_date) for i,k,v in zip(inds,kinds,vals)]
 bars[-1]=Bar(bars[-1].session_date,90,103,67,102 if bull else 78,100,102 if bull else 78)
 return bars,piv,[2.0]*n
@pytest.mark.parametrize('tf',('1d','1wk','1mo'))
@pytest.mark.parametrize('kind',('double_bottom','double_top','triple_bottom','triple_top','head_shoulders','inverse_head_shoulders'))
def test_T08_pivot_patterns_all_timeframes(tf,kind):
 b,p,a=structural_fixture(tf,kind);assert kind in [x['type'] for x in _pivot_patterns('X',tf,b,p,a)]
