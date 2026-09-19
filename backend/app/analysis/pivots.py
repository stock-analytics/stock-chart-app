from ..models import Bar, Pivot

def extract_pivots(bars:list[Bar], k:int=3)->list[Pivot]:
    raw=[]
    for i in range(k,len(bars)-k):
        window=bars[i-k:i+k+1]
        highs=[b.high for b in window]; lows=[b.low for b in window]
        high=(bars[i].high==max(highs) and highs.index(max(highs))==len(highs)-1-highs[::-1].index(max(highs)))
        low=(bars[i].low==min(lows) and lows.index(min(lows))==len(lows)-1-lows[::-1].index(min(lows)))
        if high==low: continue
        raw.append(Pivot(i,'high' if high else 'low',bars[i].high if high else bars[i].low,bars[i].session_date,bars[i+k].session_date))
    alternating=[]
    for p in raw:
        if alternating and alternating[-1].kind==p.kind:
            old=alternating[-1]
            if (p.kind=='high' and p.price>=old.price) or (p.kind=='low' and p.price<=old.price): alternating[-1]=p
        else: alternating.append(p)
    return alternating
