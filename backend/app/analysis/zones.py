from statistics import median
from ..models import Pivot

def support_resistance(pivots:list[Pivot], last_close:float, atr14:float)->list[dict]:
    pivots=pivots[-504:]
    if not pivots: return []
    m=median(p.price for p in pivots); width=max(.01*m,.5*atr14); clusters=[]
    for p in sorted(pivots,key=lambda p:p.price):
        if not clusters or p.price-clusters[-1][0].price>width: clusters.append([p])
        else: clusters[-1].append(p)
    result=[]
    for points in clusters:
        separated=[]
        for p in sorted(points,key=lambda p:p.index):
            if not separated or p.index-separated[-1].index>=3: separated.append(p)
        if len(separated)<2: continue
        lo=min(p.price for p in points)-.1*atr14; hi=max(p.price for p in points)+.1*atr14
        role='support' if hi<last_close else 'resistance' if lo>last_close else 'inside'
        result.append({'representative':median(p.price for p in points),'lower':lo,'upper':hi,'touches':len(separated),'last_touch':str(separated[-1].pivot_at),'role':role})
    return result
