import sys;sys.path.insert(0,'.')
from datetime import date,timedelta
from app.models import Bar,Pivot
from app.analysis.harmonic_state import candidates
def test_T11_zone_touch_D_confirmation_and_reversal_are_separate_events():
 prices=[100,200,138.2,184.55,38.2];idx=[20,40,60,80,100];bars=[]
 for i in range(110):
  c=150
  if i==100:c=38.2
  if i>=104:c=45
  bars.append(Bar(date(2020,1,1)+timedelta(i),c,c+1,c-1,c,1,c))
 piv=[Pivot(i,'low' if n%2==0 else 'high',v,bars[i].session_date,bars[i+3].session_date) for n,(i,v) in enumerate(zip(idx,prices))]
 found=[x for x in candidates('X','1d',bars,piv,[2.0]*len(bars)) if x['type']=='crab'];assert found;names=[e['event'] for e in found[0]['events']];assert 'zone_touched' in names and 'D_confirmed' in names and 'reversal_observed' in names;assert names.index('zone_touched')<=names.index('D_confirmed')<names.index('reversal_observed')
