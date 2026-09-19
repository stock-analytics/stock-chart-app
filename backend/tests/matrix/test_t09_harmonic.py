import sys;sys.path.insert(0,'.')
from app.analysis.harmonic import classify
CASES={'crab':(.618,.75,1.618),'deep_crab':(.886,.6,1.618),'gartley':(.618,(2*.618-.786)/.618,.786),'bat':(.5,.55,.886),'butterfly':(.786,.6,1.27)}
def test_T09_all_five_positive_zero_and_order_invalid():
 for kind,(b,c,d) in CASES.items():
  p=[100,200,200-100*b,200-100*b+100*b*c,200-100*d];assert kind in [x[0] for x in classify(p)]
 assert classify([1]*5)==[] and classify([100,90,110,80,120])==[]
