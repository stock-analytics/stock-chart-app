import sys;sys.path.insert(0,'.')
from app.storage.database import Database
def test_T20_immutable_rule_versioned_history_and_event_dedup(tmp_path):
 d=Database(tmp_path/'db');p={'family_id':'f','rule_version':'v1','type':'crab','anchors':[],'events':[{'event':'forming','at':'2024-01-01'}]};d.save_pattern_history('X',[p]);d.save_pattern_history('X',[p]);assert len(d.get_history('X'))==1
 q={'family_id':'f2','rule_version':'v2','type':'crab','anchors':[],'events':[{'event':'forming','at':'2024-01-01'}]};d.save_pattern_history('X',[q]);assert len(d.get_history('X'))==2
