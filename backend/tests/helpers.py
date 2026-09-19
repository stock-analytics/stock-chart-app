from datetime import date,timedelta
from app.models import Bar,Pivot

def line_bars(w,su,sl,break_direction='up',a=1.0):
 bars=[]; pivots=[];base=date(2020,1,1)
 for i in range(w):
  u=110+su*i;l=102+sl*i;c=(u+l)/2
  bars.append(Bar(base+timedelta(days=i),c,u+.1,l-.1,c,100))
 for i in sorted(set((0,w//3,2*w//3,w-1))):
  kind='high' if len(pivots)%2==0 else 'low';price=(110+su*i) if kind=='high' else (102+sl*i)
  pivots.append(Pivot(i,kind,price,bars[i].session_date,bars[min(i+3,w-1)].session_date))
 i=w;u=110+su*i;l=102+sl*i;c=u+.5 if break_direction=='up' else l-.5 if break_direction=='down' else (u+l)/2
 bars.append(Bar(base+timedelta(days=i),c,max(c,u)+.1,min(c,l)-.1,c,120))
 return bars,pivots,[a]*len(bars)
def flag_bars(tf='1d',bull=True,pennant=False):
 fw={'1d':10,'1wk':10,'1mo':10}[tf];pole={'1d':5,'1wk':4,'1mo':3}[tf];base=date(2020,1,1);bars=[]
 start_price=100;step=4 if bull else -4
 for i in range(pole):
  c=start_price+step*i;bars.append(Bar(base+timedelta(days=i),c,c+.5,c-.5,c,100))
 endp=bars[-1].close;piv=[]
 for j in range(fw):
  i=pole+j
  if pennant:
   frac=j/(fw-1);u=endp+3.8-2.5*frac;l=endp-3.8+2.5*frac
  else:
   slope=(-.03 if bull else .03)*j;u=endp+2+slope;l=endp-2+slope
  c=(u+l)/2;bars.append(Bar(base+timedelta(days=i),c,u+.1,l-.1,c,100))
 for j,kind in [(0,'high'),(2,'low'),(5,'high'),(8,'low')]:
  i=pole+j
  if pennant:frac=j/(fw-1);price=endp+3.8-2.5*frac if kind=='high' else endp-3.8+2.5*frac
  else:price=endp+(2 if kind=='high' else -2)+(-.03 if bull else .03)*j
  piv.append(Pivot(i,kind,price,bars[i].session_date,bars[min(i+3,len(bars)-1)].session_date))
 i=len(bars);u=endp+(1.3 if pennant else 2)+(-.03 if bull else .03)*fw;l=endp-(1.3 if pennant else 2)+(-.03 if bull else .03)*fw;c=u+.5 if bull else l-.5;bars.append(Bar(base+timedelta(days=i),c,max(c,u)+.1,min(c,l)-.1,c,100))
 return bars,piv,[1.0]*len(bars)
def cup_bars():
 base=date(2020,1,1);bars=[]
 for i in range(20):
  c=90+i;bars.append(Bar(base+timedelta(days=i),c,c+1,c-1,c,100))
 for j in range(31):
  c=90+20*((j-15)/15)**2;bars.append(Bar(base+timedelta(days=20+j),c,c+1,c-1,c,100))
 for j,c in enumerate([109,108,107,106,106,112],51):bars.append(Bar(base+timedelta(days=j),c,c+1,c-1,c,100))
 p=[Pivot(20,'high',111,bars[20].session_date,bars[23].session_date),Pivot(35,'low',89,bars[35].session_date,bars[38].session_date),Pivot(50,'high',111,bars[50].session_date,bars[53].session_date),Pivot(52,'low',106,bars[52].session_date,bars[55].session_date)]
 return bars,p,[1.0]*len(bars)
