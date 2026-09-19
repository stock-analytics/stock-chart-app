from __future__ import annotations
import hashlib
from statistics import mean
from ..models import Bar, Pivot
from .harmonic import classify
from .harmonic_state import candidates as harmonic_candidates
from .window_patterns import detect_converging,detect_flags,detect_pennants,detect_cups,EXPIRY
RULE_VERSION='screening_v1'
NORMAL_TYPES=['double_bottom','double_top','triple_bottom','triple_top','head_shoulders','inverse_head_shoulders','ascending_triangle','descending_triangle','symmetrical_triangle','rising_wedge','falling_wedge','bull_flag','bear_flag','bull_pennant','bear_pennant','cup_handle']
HARMONIC_TYPES=['crab','deep_crab','gartley','bat','butterfly']
ALL_TYPES=NORMAL_TYPES+HARMONIC_TYPES

def catalog():
 return [{'type':t,'directions':['bullish','bearish'] if t in HARMONIC_TYPES else ['neutral','bullish','bearish'] if t=='symmetrical_triangle' else ['bullish' if any(s in t for s in ('bottom','inverse','ascending','falling','bull','cup')) else 'bearish'],'implemented':True,'rule_version':RULE_VERSION,'conditions':'docs/implementation_spec.md sections 5,7,8'} for t in ALL_TYPES]
def stable_id(symbol,timeframe,kind,pivots,window=None):
 raw='|'.join([symbol,timeframe,kind,RULE_VERSION]+[str(p.pivot_at) for p in pivots]+([str(window)] if window else []));return hashlib.sha256(raw.encode()).hexdigest()[:24]
def _anchors(points):
 points=sorted(points,key=lambda p:p.index)
 return [{'label':chr(65+n) if n<26 else str(n),'date':str(p.pivot_at),'price':p.price,'known_at':str(p.known_at)} for n,p in enumerate(points)]
def _result(symbol,timeframe,kind,direction,points,state,first,changed,events,checks=None,window=None,models=None):
 family=stable_id(symbol,timeframe,kind,points,window)
 return {'id':family,'family_id':family,'supersedes_id':None,'type':kind,'direction':direction,'state':state,'reaction_state':'none','anchors':_anchors(points),'first_seen_at':str(first),'state_changed_at':str(changed),'expires_at_index':events[0]['index']+EXPIRY[timeframe],'window':{'start':window[0],'end':window[1]} if window else None,'checks':checks or [],'invalidation':'仕様第7節の固定buffer','rule_version':RULE_VERSION,'warnings':[],'events':events,'models':models or {}}
def _prior_direction(bars,anchor,p,a):
 if anchor<p:return None
 pts=[(i,bars[i].close) for i in range(anchor-p,anchor)]
 mx=mean(x for x,_ in pts);my=mean(y for _,y in pts);den=sum((x-mx)**2 for x,_ in pts)
 slope=sum((x-mx)*(y-my) for x,y in pts)/den if den else 0;move=slope*(p-1)
 return 'up' if move>=a else 'down' if move<=-a else 'flat'
def _transition(bars,start,expiry,met,invalid,direction):
 state='forming';events=[{'state':state,'index':start,'direction':direction}];changed=start
 for i in range(start+1,len(bars)):
  if invalid(i,state):n='invalidated'
  elif i-start>=expiry:n='expired'
  elif met(i):n='conditions_met'
  else:continue
  if n!=state:state=n;changed=i;events.append({'state':state,'index':i,'direction':direction})
  if state in ('invalidated','expired'):break
 return state,changed,events

def _pivot_patterns(symbol,timeframe,bars,pivots,atr_values):
 out=[];p_count={'1d':20,'1wk':12,'1mo':6}[timeframe];r_bounds={'1d':(10,120),'1wk':(4,52),'1mo':(3,24)}[timeframe]
 for ps in zip(pivots,pivots[1:],pivots[2:]):
  p1,mid,p2=ps;a=atr_values[p2.index]
  if not a or p1.kind!=p2.kind or p1.kind==mid.kind or not r_bounds[0]<=p2.index-p1.index<=r_bounds[1]:continue
  e=max(.02*mean((p1.price,p2.price)),a);direction='bullish' if p1.kind=='low' else 'bearish'
  depth=mid.price-max(p1.price,p2.price) if direction=='bullish' else min(p1.price,p2.price)-mid.price
  if abs(p1.price-p2.price)>e or depth<1.5*a:continue
  if _prior_direction(bars,p1.index,p_count,a)!=('down' if direction=='bullish' else 'up'):continue
  buffer=.25*a;start=p2.index
  met=lambda i:(bars[i].close>mid.price+buffer if direction=='bullish' else bars[i].close<mid.price-buffer)
  invalid=lambda i,s:(bars[i].close<min(p1.price,p2.price)-buffer if direction=='bullish' else bars[i].close>max(p1.price,p2.price)+buffer)
  state,changed,events=_transition(bars,start,EXPIRY[timeframe],met,invalid,direction)
  out.append(_result(symbol,timeframe,'double_bottom' if direction=='bullish' else 'double_top',direction,list(ps),state,p2.known_at,bars[changed].session_date,events))
 for ps in zip(pivots,pivots[1:],pivots[2:],pivots[3:],pivots[4:]):
  p1,p2,p3,p4,p5=ps;a=atr_values[p5.index]
  if not a or p1.kind!=p3.kind or p3.kind!=p5.kind or p2.kind!=p4.kind or not r_bounds[0]<=p5.index-p1.index<=r_bounds[1]:continue
  direction='bullish' if p1.kind=='low' else 'bearish';e=max(.02*mean((p1.price,p3.price,p5.price)),a);buffer=.25*a
  if _prior_direction(bars,p1.index,p_count,a)!=('down' if direction=='bullish' else 'up'):continue
  outer=[p1.price,p3.price,p5.price]
  if max(outer)-min(outer)<=e and abs(p2.price-p4.price)<=e:
   valid_depth=all((peak-max(l,r)>=1.5*a if direction=='bullish' else min(l,r)-peak>=1.5*a) for peak,l,r in ((p2.price,p1.price,p3.price),(p4.price,p3.price,p5.price)))
   if valid_depth:
    boundary=max(p2.price,p4.price) if direction=='bullish' else min(p2.price,p4.price)
    met=lambda i:(bars[i].close>boundary+buffer if direction=='bullish' else bars[i].close<boundary-buffer)
    invalid=lambda i,s:(bars[i].close<min(outer)-buffer if direction=='bullish' else bars[i].close>max(outer)+buffer)
    state,changed,events=_transition(bars,p5.index,EXPIRY[timeframe],met,invalid,direction)
    out.append(_result(symbol,timeframe,'triple_bottom' if direction=='bullish' else 'triple_top',direction,list(ps),state,p5.known_at,bars[changed].session_date,events))
  shoulders=abs(p1.price-p5.price)<=e;head=(p3.price-max(p1.price,p5.price)>=1.5*a if direction=='bearish' else min(p1.price,p5.price)-p3.price>=1.5*a)
  intervals=((p3.index-p1.index),(p5.index-p3.index));ratio=intervals[0]/intervals[1]
  if shoulders and head and .5<=ratio<=2:
   slope=(p4.price-p2.price)/(p4.index-p2.index);neck=lambda i:p2.price+slope*(i-p2.index)
   met=lambda i:(bars[i].close<neck(i)-buffer if direction=='bearish' else bars[i].close>neck(i)+buffer)
   invalid=lambda i,s:(bars[i].close>p3.price+buffer if direction=='bearish' else bars[i].close<p3.price-buffer)
   state,changed,events=_transition(bars,p5.index,EXPIRY[timeframe],met,invalid,direction)
   out.append(_result(symbol,timeframe,'head_shoulders' if direction=='bearish' else 'inverse_head_shoulders',direction,list(ps),state,p5.known_at,bars[changed].session_date,events))
 return out

def detect(symbol,timeframe,bars,pivots,atr_values):
 out=_pivot_patterns(symbol,timeframe,bars,pivots,atr_values)
 for raw in detect_converging(symbol,timeframe,bars,pivots,atr_values)+detect_flags(symbol,timeframe,bars,pivots,atr_values)+detect_pennants(symbol,timeframe,bars,pivots,atr_values)+detect_cups(symbol,timeframe,bars,pivots,atr_values):
  first=bars[raw['training'][1]].session_date;changed=bars[raw['changed']].session_date
  out.append(_result(symbol,timeframe,raw['type'],raw['direction'],raw['anchors'],raw['state'],first,changed,raw['events'],window=raw['training'],models=raw['models']))
 for raw in harmonic_candidates(symbol,timeframe,bars,pivots,atr_values,RULE_VERSION):
  points=raw['points']; checks=[{'name':'candidate_zone','actual':raw['zone'],'lower':raw['zone'][0],'upper':raw['zone'][1],'passed':True}]
  item=_result(symbol,timeframe,raw['type'],raw['direction'],points,raw['state'],raw['first'],raw['changed'],raw['events'],checks)
  item['id']=raw['id'];item['family_id']=raw['family_id'];item['reaction_state']=raw['reaction_state'];item['candidate_zone']={'lower':raw['zone'][0],'upper':raw['zone'][1]};item['expires_at_index']=raw['expires']
  out.append(item)
 return out[-200:]
