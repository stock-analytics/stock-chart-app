from __future__ import annotations
import hashlib
from .harmonic import RULES,ratios,_inside
HMAX={'1d':250,'1wk':104,'1mo':60};HMIN={'1d':20,'1wk':8,'1mo':6};EXPIRY={'1d':60,'1wk':26,'1mo':12}
def _fixed_band(origin,distance,q,direction):
 lo=q*(1-.03);hi=q*(1+.03);vals=(origin+direction*lo*distance,origin+direction*hi*distance);return min(vals),max(vals)
def _range_band(origin,distance,r,direction):
 lo,hi=r
 if hi==float('inf'): hi=1000.0
 vals=(origin+direction*lo*distance,origin+direction*hi*distance);return min(vals),max(vals)
def _band(origin,distance,r,direction):return _fixed_band(origin,distance,r[0],direction) if r[0]==r[1] else _range_band(origin,distance,r,direction)
def candidates(symbol,timeframe,bars,pivots,atr_values,rule_version='screening_v1'):
 out=[];hmin,hmax=HMIN[timeframe],HMAX[timeframe]
 for x,a,b,c in zip(pivots,pivots[1:],pivots[2:],pivots[3:]):
  bullish=(x.kind,a.kind,b.kind,c.kind)==('low','high','low','high');bearish=(x.kind,a.kind,b.kind,c.kind)==('high','low','high','low')
  if not (bullish or bearish) or c.index-x.index>=hmax:continue
  xa=abs(a.price-x.price);ab=abs(a.price-b.price)
  if not xa or not ab:continue
  rb=ab/xa;rc=abs(c.price-b.price)/ab
  if not _inside(rc,(.382,.886)):continue
  for typ,(rb_rule,rd,rbc,rabcd,placement) in RULES.items():
   if not _inside(rb,rb_rule):continue
   direction=-1 if bullish else 1
   bands=[_band(a.price,xa,rd,direction),_band(c.price,abs(c.price-b.price),rbc,direction),_band(c.price,ab,rabcd,direction)]
   lower=max(v[0] for v in bands);upper=min(v[1] for v in bands)
   if placement=='extension':
    if bullish:upper=min(upper,x.price)
    else:lower=max(lower,x.price)
   else:
    if bullish:lower=max(lower,x.price);upper=min(upper,b.price)
    else:lower=max(lower,b.price);upper=min(upper,x.price)
   if not lower<upper:continue
   raw='|'.join((symbol,timeframe,typ,str(x.pivot_at),str(a.pivot_at),str(b.pivot_at),str(c.pivot_at),rule_version));family=hashlib.sha256(raw.encode()).hexdigest()[:24]
   first=c.index;frozen_a=atr_values[first]
   if not frozen_a:continue
   end=min(len(bars)-1,x.index+hmax,first+EXPIRY[timeframe]);reaction='none';state='forming';events=[{'event':'forming','index':first,'at':str(c.known_at)}];d=None
   for i in range(first+1,end+1):
    probe=bars[i].low if bullish else bars[i].high
    if lower<=probe<=upper and reaction=='none':reaction='zone_touched';events.append({'event':'zone_touched','index':i,'at':str(bars[i].session_date)})
    if (bullish and bars[i].close<lower-.5*frozen_a) or (bearish and bars[i].close>upper+.5*frozen_a):
     state='invalidated';events.append({'event':'invalidated','index':i,'at':str(bars[i].session_date)});break
    nextp=next((p for p in pivots if p.index>c.index and p.kind==('low' if bullish else 'high')),None)
    if nextp and nextp.known_at<=bars[i].session_date:
     rr=ratios([x.price,a.price,b.price,c.price,nextp.price])
     if rr and all(_inside(rr[k],v) for k,v in [('rD',rd),('rBC',rbc),('rABCD',rabcd)]):
      d=nextp;state='conditions_met';events.append({'event':'D_confirmed','index':i,'at':str(bars[i].session_date)});break
   if d:
    for i in range(max(d.index+1,next(j for j,z in enumerate(bars) if z.session_date>=d.known_at)),end+1):
     observed=bars[i].close>bars[d.index].high if bullish else bars[i].close<bars[d.index].low
     # OHLC contract calls for D bar high/low rather than pivot value (equal for pivot extremum).
     if observed:reaction='reversal_observed';events.append({'event':'reversal_observed','index':i,'at':str(bars[i].session_date)});break
   if state=='forming' and end<len(bars):state='expired';events.append({'event':'expired','index':end,'at':str(bars[end].session_date)})
   out.append({'family_id':family,'id':family,'type':typ,'direction':'bullish' if bullish else 'bearish','state':state,'reaction_state':reaction,'points':[x,a,b,c]+([d] if d else []),'zone':(lower,upper),'events':events,'first':c.known_at,'changed':events[-1]['at'],'expires':end})
 return out[-200:]
