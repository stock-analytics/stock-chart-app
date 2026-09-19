"""Window based v1 detectors from specification sections 5 and 7.
All x coordinates are immutable bar indexes; training windows never include breakout bars.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from statistics import mean
from ..models import Bar, Pivot

WINDOWS={'1d':(60,120,252),'1wk':(26,52,104),'1mo':(12,24,60)}
FLAG_WINDOWS={'1d':(10,15,20),'1wk':(10,12,16),'1mo':(10,12,16)}
POLES={'1d':(5,10,20),'1wk':(4,6,8),'1mo':(3,4,6)}
CUP_RANGES={'1d':(30,250),'1wk':(12,104),'1mo':(8,60)}
HANDLE_RANGES={'1d':(5,30),'1wk':(4,12),'1mo':(4,8)}
EXPIRY={'1d':60,'1wk':26,'1mo':12}

def ols(points:list[tuple[int,float]])->tuple[float,float]:
    if len(points)<2: raise ValueError('insufficient_points')
    mx=mean(x for x,_ in points); my=mean(y for _,y in points)
    den=sum((x-mx)**2 for x,_ in points)
    if den==0: raise ValueError('zero_denominator')
    slope=sum((x-mx)*(y-my) for x,y in points)/den
    return slope,my-slope*mx

def _line(model,x): return model[0]*x+model[1]
def _pivots(pivots,kind,start,end): return [p for p in pivots if p.kind==kind and start<=p.index<=end]

def fitted_window(bars,pivots,start,end,a,kind='converging'):
    """Return frozen upper/lower regressions when common geometry conditions pass."""
    highs=_pivots(pivots,'high',start,end); lows=_pivots(pivots,'low',start,end)
    if len(highs)<2 or len(lows)<2 or a<=0:return None
    try:u=ols([(p.index,p.price) for p in highs]);l=ols([(p.index,p.price) for p in lows])
    except ValueError:return None
    if any(abs(p.price-_line(u,p.index))>.5*a for p in highs):return None
    if any(abs(p.price-_line(l,p.index))>.5*a for p in lows):return None
    if any(_line(u,x)<=_line(l,x) for x in range(start,end+1)):return None
    inside=sum(_line(l,i)-.25*a<=bars[i].close<=_line(u,i)+.25*a for i in range(start,end+1))/(end-start+1)
    if inside<.9:return None
    if kind=='channel':
        if abs((u[0]-l[0])*(end-start))>a:return None
    else:
        first=_line(u,start)-_line(l,start);last=_line(u,end)-_line(l,end)
        if first<2*a or not .2<=last/first<=.7:return None
        den=l[0]-u[0]
        if den==0:return None
        cross=(u[1]-l[1])/den
        if not end<cross<=end+(end-start+1):return None
    return {'upper':u,'lower':l,'highs':highs,'lows':lows,'inside':inside}

def _state_after(bars,end,expiry,upper,lower,b,direction):
    events=[{'state':'forming','index':end}]; state='forming'; changed=end
    for i in range(end+1,len(bars)):
        up=bars[i].close>_line(upper,i)+b;down=bars[i].close<_line(lower,i)-b
        invalid=(direction=='bullish' and down) or (direction=='bearish' and up)
        met=(direction=='bullish' and up) or (direction=='bearish' and down) or (direction=='neutral' and (up or down))
        if invalid or (state=='conditions_met' and ((direction=='bullish' and down) or (direction=='bearish' and up))):state='invalidated'
        elif i-end>=expiry:state='expired'
        elif met: state='conditions_met'; direction='bullish' if up else 'bearish'
        else:continue
        changed=i;events.append({'state':state,'index':i,'direction':direction})
        if state in ('invalidated','expired'):break
    return state,direction,changed,events

def detect_converging(symbol,timeframe,bars,pivots,atr_values):
    out=[]
    for w in WINDOWS[timeframe]:
      if len(bars)<w:continue
      # Candidate is frozen at the earliest matching recent training window.
      for end in range(w-1,len(bars)):
        start=end-w+1;a=atr_values[end]
        if not a:continue
        fit=fitted_window(bars,pivots,start,end,a)
        if not fit:continue
        su,sl=fit['upper'][0],fit['lower'][0];span=w-1
        choices=[]
        if abs(su*span)<=.5*a and sl*span>a:choices=[('ascending_triangle','bullish')]
        elif abs(sl*span)<=.5*a and su*span < -a:choices=[('descending_triangle','bearish')]
        elif su*span<-.5*a and sl*span>.5*a:choices=[('symmetrical_triangle','neutral')]
        elif su*span>.5*a and sl>su:choices=[('rising_wedge','bearish')]
        elif sl*span<-.5*a and su<sl:choices=[('falling_wedge','bullish')]
        for typ,direction in choices:
          state,direction,changed,events=_state_after(bars,end,EXPIRY[timeframe],fit['upper'],fit['lower'],.25*a,direction)
          out.append({'type':typ,'direction':direction,'state':state,'training':(start,end),'changed':changed,'events':events,'models':{'upper':fit['upper'],'lower':fit['lower']},'anchors':fit['highs']+fit['lows'],'a':a})
      # avoid alternate rolling windows flooding a single window length
      if out:break
    return out

def _efficiency(closes):
    travel=sum(abs(b-a) for a,b in zip(closes,closes[1:]));return abs(closes[-1]-closes[0])/travel if travel else 0

def detect_flags(symbol,timeframe,bars,pivots,atr_values):
    out=[]
    for fw in FLAG_WINDOWS[timeframe]:
      for pole_len in POLES[timeframe]:
       for end in range(pole_len+fw-1,len(bars)-1):
        start=end-fw+1;ps=start-pole_len;a=atr_values[end]
        if not a:continue
        closes=[x.close for x in bars[ps:start]]
        change=closes[-1]-closes[0]
        if abs(change)<3*a or _efficiency(closes)<.7:continue
        fit=fitted_window(bars,pivots,start,end,a,'channel')
        if not fit:continue
        slope=(fit['upper'][0]+fit['lower'][0])/2;bull=change>0
        if bull and slope*(fw-1)>.5*a:continue
        if not bull and slope*(fw-1)<-.5*a:continue
        pole_range=abs(change); retrace=(closes[-1]-min(b.low for b in bars[start:end+1])) if bull else (max(b.high for b in bars[start:end+1])-closes[-1])
        if retrace>.5*pole_range:continue
        typ='bull_flag' if bull else 'bear_flag';direction='bullish' if bull else 'bearish'
        state,direction,changed,events=_state_after(bars,end,EXPIRY[timeframe],fit['upper'],fit['lower'],.25*a,direction)
        out.append({'type':typ,'direction':direction,'state':state,'training':(start,end),'changed':changed,'events':events,'models':{'upper':fit['upper'],'lower':fit['lower']},'anchors':fit['highs']+fit['lows'],'a':a,'pole_start':ps})
       if out:return out
    return out

def detect_pennants(symbol,timeframe,bars,pivots,atr_values):
    out=[]
    # Same fixed flag/pole scan, but consolidation must meet converging symmetric geometry.
    for fw in FLAG_WINDOWS[timeframe]:
      for pole_len in POLES[timeframe]:
       for end in range(pole_len+fw-1,len(bars)-1):
        start=end-fw+1;ps=start-pole_len;a=atr_values[end]
        if not a:continue
        closes=[x.close for x in bars[ps:start]];change=closes[-1]-closes[0]
        if abs(change)<3*a or _efficiency(closes)<.7:continue
        fit=fitted_window(bars,pivots,start,end,a)
        if not fit:continue
        span=fw-1
        if not (fit['upper'][0]*span<-.5*a and fit['lower'][0]*span>.5*a):continue
        bull=change>0; retrace=(closes[-1]-min(b.low for b in bars[start:end+1])) if bull else (max(b.high for b in bars[start:end+1])-closes[-1])
        if retrace>.5*abs(change):continue
        typ='bull_pennant' if bull else 'bear_pennant';direction='bullish' if bull else 'bearish'
        state,direction,changed,events=_state_after(bars,end,EXPIRY[timeframe],fit['upper'],fit['lower'],.25*a,direction)
        out.append({'type':typ,'direction':direction,'state':state,'training':(start,end),'changed':changed,'events':events,'models':{'upper':fit['upper'],'lower':fit['lower']},'anchors':fit['highs']+fit['lows'],'a':a,'pole_start':ps})
       if out:return out
    return out

def detect_cups(symbol,timeframe,bars,pivots,atr_values):
    lo_gap,hi_gap=CUP_RANGES[timeframe];hmin,hmax=HANDLE_RANGES[timeframe];out=[]
    highs=[p for p in pivots if p.kind=='high']; lows=[p for p in pivots if p.kind=='low']
    for left in highs:
      for right in highs:
       gap=right.index-left.index
       if not lo_gap<=gap<=hi_gap:continue
       a=atr_values[right.index]
       if not a:continue
       e=max(.02*mean((left.price,right.price)),a)
       if abs(left.price-right.price)>e:continue
       between=[p for p in lows if left.index<p.index<right.index]
       if not between:continue
       bottom=min(between,key=lambda p:p.price);depth=min(left.price,right.price)-bottom.price
       if depth<2*a or depth/mean((left.price,right.price))>.5:continue
       pos=(bottom.index-left.index)/gap
       if not .25<=pos<=.75:continue
       near=sum(b.low<=bottom.price+.25*depth for b in bars[left.index:right.index+1])
       if near<max(3,.2*(gap+1)):continue
       if ols([(i,bars[i].close) for i in range(left.index,bottom.index+1)])[0]>=0:continue
       if ols([(i,bars[i].close) for i in range(bottom.index,right.index+1)])[0]<=0:continue
       for hl in range(hmin,hmax+1):
        end=right.index+hl
        if end>=len(bars):break
        handle_lows=[p for p in lows if right.index<p.index<=end and p.known_at<=bars[end].session_date]
        if not handle_lows:continue
        if ols([(i,bars[i].close) for i in range(right.index,end+1)])[0]>0:continue
        floor=min(p.price for p in handle_lows)
        if floor<right.price-.5*depth:continue
        events=[{'state':'forming','index':end}];state='forming';changed=end;b=.25*a
        for i in range(end+1,len(bars)):
         if bars[i].close<floor-b:state='invalidated'
         elif i-end>=EXPIRY[timeframe]:state='expired'
         elif bars[i].close>max(left.price,right.price)+b:state='conditions_met'
         else:continue
         changed=i;events.append({'state':state,'index':i});
         if state!='conditions_met':break
        out.append({'type':'cup_handle','direction':'bullish','state':state,'training':(left.index,end),'changed':changed,'events':events,'anchors':[left,bottom,right]+handle_lows,'a':a,'models':{}})
        return out
    return out
