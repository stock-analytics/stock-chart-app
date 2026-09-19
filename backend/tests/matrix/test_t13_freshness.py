import sys;sys.path.insert(0,'.')
from datetime import date
from app.analysis.freshness import freshness,is_session
def test_T13_weekend_today_and_unknown_calendar_labels():
 assert freshness(date(2024,6,14),date(2024,6,15))=='final_candidate';assert freshness(date(2024,6,17),date(2024,6,17))=='provisional';assert freshness(date(2025,1,1),date(2025,1,2))=='calendar_unknown';assert is_session(date(2024,1,1)) is False
