from datetime import date
from ..models import Bar
from .indicators import aggregate,daily_sma_for_aggregate,atr
from .pivots import extract_pivots
from .zones import support_resistance
from .patterns import detect,ALL_TYPES,RULE_VERSION
RANGES={'6mo':126,'2y':504,'5y':1260,'all':None}
def analyze(symbol:str,daily:list[Bar],timeframe='1d',range_name='2y',as_of:date|None=None,snapshot_id='synthetic'):
 final=[b for b in daily if b.is_final and (as_of is None or b.session_date<=as_of)]; provisional=[b for b in daily if not b.is_final and (as_of is None or b.session_date<=as_of)]
 series=aggregate(final,timeframe); av=atr(series); pivots=extract_pivots(series); current_atr=next((v for v in reversed(av) if v is not None),0)
 pats=detect(symbol,timeframe,series,pivots,av) if current_atr and series else []
 for pattern in pats:pattern['snapshot_id']=snapshot_id
 limit=RANGES[range_name]; shown=series[-limit:] if limit else series
 def bar_json(b): return {'date':str(b.session_date),'open':b.open,'high':b.high,'low':b.low,'close':b.close,'volume':b.volume}
 indicators={f'sma{p}':[{'date':str(b.session_date),'value':v,'source_timeframe':'1d'} for b,v in zip(series,daily_sma_for_aggregate(final,series,p))][-len(shown):] for p in (30,75,200)}
 return {'schema_version':'1.0','symbol':symbol,'exchange':'TSE','currency':'JPY','timezone':'Asia/Tokyo','snapshot_id':snapshot_id,'rule_version':RULE_VERSION,'as_of':str(as_of or (final[-1].session_date if final else date.today())),'data_mode':'synthetic' if symbol.startswith('DEMO_') else 'live','metadata':{'fetched_at':str(daily[-1].fetched_at) if daily else None,'latest_final_session':str(final[-1].session_date) if final else None,'provider_timestamp':None,'price_basis':'配当・分割調整後','warnings':[],'coverage_start':str(final[0].session_date) if final else None,'truncated':len(series)>2500},'bars':[bar_json(b) for b in shown],'provisional_bars':[bar_json(b) for b in provisional],'indicators':indicators,'zones':support_resistance(pivots,series[-1].close,current_atr) if series and current_atr else [],'patterns':pats,'chart_overlays':[],'supported_patterns':ALL_TYPES,'insufficient_data_reasons':[] if len(series)>=30 else ['insufficient_history']}
