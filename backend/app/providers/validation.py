import re,unicodedata,math
PATTERN=re.compile(r'^[0-9][0-9A-Z]{3}(?:\.T)?$')
def normalize_symbol(value:str)->str:
 value=unicodedata.normalize('NFKC',value).strip().upper()
 if not PATTERN.fullmatch(value): raise ValueError('invalid_symbol')
 return value if value.endswith('.T') else value+'.T'
def adjusted_prices(open_,high,low,close,adj_close):
 if close<=0 or adj_close is None or not math.isfinite(adj_close) or adj_close<=0: raise ValueError('adjustment_unavailable')
 factor=adj_close/close
 return tuple(v*factor for v in (open_,high,low,close)),factor
