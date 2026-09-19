import sys;sys.path.insert(0,'.')
from app.analysis.indicators import sma
def test_T01_sma_boundaries_and_manual_average():
 values=list(range(1,201));out=sma(values,30);assert out[28] is None and out[29]==sum(range(1,31))/30;assert sma(values,75)[74]==38;assert sma(values,200)[199]==100.5
