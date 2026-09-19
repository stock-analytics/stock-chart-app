from __future__ import annotations
from dataclasses import dataclass
from ..models import Pivot
EPS=1e-9
RULES={
'crab':((.382,.618),(1.618,1.618),(2.618,3.618),(1,float('inf')),'extension'),
'deep_crab':((.886,.886),(1.618,1.618),(2.24,3.618),(1,float('inf')),'extension'),
'gartley':((.618,.618),(.786,.786),(1.27,1.618),(1,1),'retracement'),
'bat':((.382,.5),(.886,.886),(1.618,2.618),(1.27,float('inf')),'retracement'),
'butterfly':((.786,.786),(1.27,1.27),(1.618,2.618),(1,1.618),'extension')}
def _inside(v,r):
 l,u=r
 if l==u: return abs(v-l)/l <= .03+EPS
 return v>=l-EPS and v<=u+EPS
def ratios(prices):
 x,a,b,c,d=prices; xa=abs(a-x); ab=abs(a-b); cb=abs(c-b)
 if min(xa,ab,cb)<=EPS: return None
 return {'rB':abs(a-b)/xa,'rC':abs(c-b)/ab,'rD':abs(a-d)/xa,'rBC':abs(c-d)/cb,'rABCD':abs(c-d)/ab}
def classify(prices):
 r=ratios(prices)
 if not r or not _inside(r['rC'],(.382,.886)): return []
 x,a,b,c,d=prices; bullish=x<b<c<a and ((d<x) or (x<d<b)); bearish=x>b>c>a and ((d>x) or (x>d>b))
 if not (bullish or bearish): return []
 placement='extension' if (d<x if bullish else d>x) else 'retracement'
 found=[]
 for name,(rb,rd,rbc,rabcd,pos) in RULES.items():
  if placement==pos and all((_inside(r[k],v) for k,v in [('rB',rb),('rD',rd),('rBC',rbc),('rABCD',rabcd)])):
   found.append((name,'bullish' if bullish else 'bearish',r))
 return found
