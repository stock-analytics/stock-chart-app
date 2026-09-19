from __future__ import annotations
from collections import defaultdict
from datetime import date
from ..models import Bar

def sma(values:list[float|None], period:int)->list[float|None]:
    out=[]; window=[]
    for v in values:
        if v is None:
            window=[]; out.append(None); continue
        window.append(v)
        if len(window)>period: window.pop(0)
        out.append(sum(window)/period if len(window)==period else None)
    return out

def atr(bars:list[Bar], period:int=14)->list[float|None]:
    out=[]; trs=[]; previous=None; current=None
    for bar in bars:
        tr=max(bar.high-bar.low, abs(bar.high-previous), abs(bar.low-previous)) if previous is not None else bar.high-bar.low
        previous=bar.close; trs.append(tr)
        if len(trs)<period: out.append(None)
        elif len(trs)==period: current=sum(trs)/period; out.append(current)
        else: current=(current*(period-1)+tr)/period; out.append(current)
    return out

def aggregate(bars:list[Bar], timeframe:str)->list[Bar]:
    if timeframe=='1d': return list(bars)
    groups=defaultdict(list)
    for b in bars:
        key=b.session_date.isocalendar()[:2] if timeframe=='1wk' else (b.session_date.year,b.session_date.month)
        groups[key].append(b)
    out=[]
    for group in groups.values():
        group.sort(key=lambda b:b.session_date); first,last=group[0],group[-1]
        volume=sum(b.volume for b in group) if all(b.volume is not None for b in group) else None
        out.append(Bar(last.session_date,first.open,max(b.high for b in group),min(b.low for b in group),last.close,volume,is_final=all(b.is_final for b in group),fetched_at=last.fetched_at))
    return out

def daily_sma_for_aggregate(daily:list[Bar], aggregate_bars:list[Bar], period:int)->list[float|None]:
    values=sma([b.close for b in daily],period); by_date={b.session_date:v for b,v in zip(daily,values)}
    return [by_date.get(b.session_date) for b in aggregate_bars]
