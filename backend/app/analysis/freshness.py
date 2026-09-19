from datetime import date
# Built-in closure data is deliberately bounded; unknown years do not receive invented freshness.
TSE_HOLIDAYS_2024={date(2024,1,1),date(2024,1,2),date(2024,1,3),date(2024,1,8),date(2024,2,12),date(2024,2,23),date(2024,3,20),date(2024,4,29),date(2024,5,3),date(2024,5,6),date(2024,7,15),date(2024,8,12),date(2024,9,16),date(2024,9,23),date(2024,10,14),date(2024,11,4),date(2024,12,31)}
def calendar_known(day):return day.year==2024
def is_session(day):
 if not calendar_known(day):return None
 return day.weekday()<5 and day not in TSE_HOLIDAYS_2024
def freshness(latest,today):
 if not calendar_known(today):return 'calendar_unknown'
 if latest==today:return 'provisional'
 return 'final_candidate' if latest<today else 'invalid_future'
