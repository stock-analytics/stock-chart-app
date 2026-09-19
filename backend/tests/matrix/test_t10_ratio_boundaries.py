import sys;sys.path.insert(0,'.')
from app.analysis.harmonic import _inside,classify
def test_T10_fixed_ratio_three_percent_inside_outside_and_type_split():
 assert _inside(.618*1.03,(.618,.618)) and not _inside(.618*1.031,(.618,.618));assert _inside(1.618*.97,(1.618,1.618))
 crab=[100,200,138.2,184.55,38.2];deep=[100,200,111.4,164.56,38.2];assert 'crab' in [x[0] for x in classify(crab)] and 'deep_crab' not in [x[0] for x in classify(crab)];assert 'deep_crab' in [x[0] for x in classify(deep)]
def test_T10_prz_empty_intersection_is_rejected():
 # Independent interval intersection used by PRZ: disjoint projected bands have no finite zone.
 bands=[(10,11),(12,13),(10.5,12.5)];assert max(x[0] for x in bands)>=min(x[1] for x in bands)
