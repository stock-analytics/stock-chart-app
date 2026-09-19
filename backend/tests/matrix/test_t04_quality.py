import sys;sys.path.insert(0,'.')
from datetime import date
import pytest
from app.models import Bar
from app.providers.quality import validate_snapshot
def test_T04_nan_adjustment_and_conflicting_duplicate_rejected():
 good=Bar(date(2024,1,1),10,11,9,10,1,10);assert len(validate_snapshot([good,good]))==1
 with pytest.raises(ValueError):validate_snapshot([good,Bar(date(2024,1,1),10,12,9,10,1,10)])
 with pytest.raises(ValueError):validate_snapshot([Bar(date(2024,1,2),10,11,9,10,1,float('nan'))])
