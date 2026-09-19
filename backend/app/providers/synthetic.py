from datetime import date,datetime,timedelta,timezone
import math, random
from .base import Provider
from ..models import Bar,ProviderResult
class SyntheticProvider(Provider):
 def __init__(self,seed:int=42): self.seed=seed
 def fetch_daily(self,symbol,start_inclusive,end_exclusive):
  if not symbol.startswith('DEMO_'): raise ValueError('synthetic_symbol_required')
  rng=random.Random(self.seed); bars=[]; p=100.; d=start_inclusive
  while d<end_exclusive:
   if d.weekday()<5:
    p=max(1,p+rng.gauss(.03,1.1)); spread=abs(rng.gauss(1.3,.3)); o=p+rng.gauss(0,.4); c=p
    bars.append(Bar(d,o,max(o,c)+spread,min(o,c)-spread,c,rng.randrange(10000,50000),adj_close=c,is_final=d<datetime.now(timezone.utc).date()))
   d+=timedelta(days=1)
  return ProviderResult(bars,[],'synthetic',datetime.now(timezone.utc),warnings=['合成データ・実在銘柄ではありません'],capabilities={'market':'demo','intervals':['1d'],'max_history':'10y','delayed_seconds':None,'redistribution_allowed':False})
