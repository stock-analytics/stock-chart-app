import sys,time,threading;sys.path.insert(0,'.')
from app.providers.coordinator import FetchCoordinator
def test_T22_concurrent_same_symbol_is_coalesced():
 c=FetchCoordinator(min_interval=0);started=threading.Event();release=threading.Event();calls=[];results=[]
 def op():calls.append(1);started.set();release.wait(1);return 7
 t=threading.Thread(target=lambda:results.append(c.fetch('X',op)));t.start();started.wait(1);second=c.fetch('X',op);release.set();t.join();assert len(calls)==1 and second.result()==7 and results[0].result()==7
def test_T22_analysis_declares_caps():
 s=open('app/analysis/service.py').read();assert "len(series)>2500" in s;assert '[-200:]' in open('app/analysis/patterns.py').read()
