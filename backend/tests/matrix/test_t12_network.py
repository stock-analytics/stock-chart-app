import sys;sys.path.insert(0,'.')
from app.providers.coordinator import FetchCoordinator,FetchError
def test_T12_timeout_retries_and_429_cooldown_without_fallback():
 now=[1000];sleeps=[];c=FetchCoordinator(lambda:now[0],lambda n:sleeps.append(n),min_interval=0);calls=[0]
 def transient():
  calls[0]+=1
  if calls[0]<3:raise FetchError('timeout')
  return 'real'
 assert c.fetch('7203.T',transient).result()=='real' and sleeps==[2,5]
 c2=FetchCoordinator(lambda:now[0],lambda n:None,min_interval=0)
 f=c2.fetch('x',lambda:(_ for _ in ()).throw(FetchError('rate_limited',30)));assert f.exception().code=='rate_limited';assert c2.fetch('x',lambda:'mock').exception().code=='rate_limited'
