from __future__ import annotations
import threading,time
from concurrent.futures import Future
class FetchError(Exception):
 def __init__(self,code,retry_after=None):self.code=code;self.retry_after=retry_after;super().__init__(code)
class FetchCoordinator:
 """One global fetch lane, per-symbol request coalescing and cooldown enforcement."""
 def __init__(self,clock=time.monotonic,sleep=time.sleep,min_interval=900):self.clock=clock;self.sleep=sleep;self.min_interval=min_interval;self.lock=threading.Lock();self.inflight={};self.last={};self.cooldown={}
 def fetch(self,symbol,operation):
  with self.lock:
   if symbol in self.inflight:return self.inflight[symbol]
   f=Future();self.inflight[symbol]=f
  try:
   now=self.clock()
   if now<self.cooldown.get(symbol,0):raise FetchError('rate_limited',self.cooldown[symbol]-now)
   if now-self.last.get(symbol,-self.min_interval)<self.min_interval:raise FetchError('refresh_too_soon',self.min_interval-(now-self.last[symbol]))
   delays=(0,2,5)
   for attempt,delay in enumerate(delays):
    if delay:self.sleep(delay)
    try:result=operation();break
    except FetchError as e:
     if e.code=='rate_limited':self.cooldown[symbol]=self.clock()+(e.retry_after or 900);raise
     if e.code not in ('timeout','server_error') or attempt==2:raise
   self.last[symbol]=self.clock();f.set_result(result)
  except Exception as e:f.set_exception(e)
  finally:
   with self.lock:self.inflight.pop(symbol,None)
  return f
