from datetime import datetime,timezone
from .base import Provider
from ..models import Bar,ProviderResult
class YFinanceProvider(Provider):
 def fetch_daily(self,symbol,start_inclusive,end_exclusive):
  import yfinance as yf
  frame=yf.download(symbol,start=str(start_inclusive),end=str(end_exclusive),auto_adjust=False,actions=True,repair=False,progress=False,timeout=20)
  if frame.empty: return ProviderResult([],[],'yfinance',datetime.now(timezone.utc),warnings=['no_data'])
  bars=[]
  for idx,row in frame.iterrows():
   close=float(row['Close']); adj=float(row['Adj Close']); factor=adj/close
   bars.append(Bar(idx.date(),float(row['Open'])*factor,float(row['High'])*factor,float(row['Low'])*factor,adj,int(row['Volume']) if row['Volume']==row['Volume'] else None,adj_close=adj,is_final=idx.date()<datetime.now(timezone.utc).date()))
  return ProviderResult(bars,[],'yfinance',datetime.now(timezone.utc),capabilities={'market':'JP','intervals':['1d'],'max_history':'10y','delayed_seconds':None,'redistribution_allowed':False})
