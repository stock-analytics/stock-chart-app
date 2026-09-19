from __future__ import annotations
import sqlite3,json,hashlib
from pathlib import Path
SCHEMA_VERSION=1
SCHEMA='''
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS instruments(symbol TEXT PRIMARY KEY,name TEXT,exchange TEXT,currency TEXT);
CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY,symbol TEXT NOT NULL,provider TEXT NOT NULL,fetched_at TEXT NOT NULL,content_hash TEXT NOT NULL,latest INTEGER NOT NULL DEFAULT 0);
CREATE UNIQUE INDEX IF NOT EXISTS snapshots_content ON snapshots(symbol,content_hash);
CREATE TABLE IF NOT EXISTS bars(snapshot_id TEXT NOT NULL,symbol TEXT NOT NULL,session_date TEXT NOT NULL,open REAL,high REAL,low REAL,close REAL,volume INTEGER,raw_json TEXT,factor REAL,is_final INTEGER,PRIMARY KEY(snapshot_id,symbol,session_date));
CREATE TABLE IF NOT EXISTS actions(snapshot_id TEXT,data TEXT);
CREATE TABLE IF NOT EXISTS fetch_events(id INTEGER PRIMARY KEY,status TEXT,detail TEXT,at TEXT);
CREATE TABLE IF NOT EXISTS pattern_families(id TEXT PRIMARY KEY,symbol TEXT,rule_version TEXT,data TEXT);
CREATE TABLE IF NOT EXISTS detection_events(id INTEGER PRIMARY KEY AUTOINCREMENT,family_id TEXT,state TEXT,at TEXT,data TEXT);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS watchlist(symbol TEXT PRIMARY KEY,position INTEGER NOT NULL CHECK(position BETWEEN 0 AND 19));
'''
class Database:
 def __init__(self,path='data/chart-lens.sqlite3'):
  Path(path).parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(path,check_same_thread=False); self.db.row_factory=sqlite3.Row
  self.db.execute('PRAGMA journal_mode=WAL'); self.db.execute('PRAGMA busy_timeout=5000'); self.migrate()
 def migrate(self):
  with self.db: self.db.executescript(SCHEMA); row=self.db.execute('SELECT version FROM schema_version').fetchone(); self.db.execute('INSERT INTO schema_version VALUES(?)',(SCHEMA_VERSION,)) if not row else None
 def save_snapshot(self,symbol,provider,bars,fetched_at):
  payload=json.dumps([vars(b)|{'session_date':str(b.session_date),'fetched_at':str(b.fetched_at)} for b in bars],sort_keys=True,default=str); digest=hashlib.sha256(payload.encode()).hexdigest(); sid=digest[:24]
  with self.db:
   existing=self.db.execute('SELECT id FROM snapshots WHERE symbol=? AND content_hash=?',(symbol,digest)).fetchone()
   if existing:return existing['id']
   self.db.execute('UPDATE snapshots SET latest=0 WHERE symbol=?',(symbol,)); self.db.execute('INSERT INTO snapshots VALUES(?,?,?,?,?,1)',(sid,symbol,provider,str(fetched_at),digest))
   for b in bars:self.db.execute('INSERT INTO bars VALUES(?,?,?,?,?,?,?,?,?,?,?)',(sid,symbol,str(b.session_date),b.open,b.high,b.low,b.close,b.volume,'{}',None,int(b.is_final)))
  return sid
 def watchlist(self): return [r['symbol'] for r in self.db.execute('SELECT symbol FROM watchlist ORDER BY position')]
 def add_watch(self,symbol):
  with self.db:
   n=self.db.execute('SELECT count(*) n FROM watchlist').fetchone()['n']
   if n>=20: raise ValueError('watchlist_full')
   self.db.execute('INSERT OR IGNORE INTO watchlist VALUES(?,?)',(symbol,n))
 def save_pattern_history(self,symbol,patterns):
  """Append immutable state/reaction events while retaining a stable family id."""
  with self.db:
   for p in patterns:
    self.db.execute('INSERT OR IGNORE INTO pattern_families(id,symbol,rule_version,data) VALUES(?,?,?,?)',(p['family_id'],symbol,p['rule_version'],json.dumps({'type':p['type'],'anchors':p['anchors']},ensure_ascii=False)))
    for event in p.get('events',[]):
     payload=json.dumps(event,sort_keys=True,ensure_ascii=False); key=hashlib.sha256((p['family_id']+payload).encode()).hexdigest()
     exists=self.db.execute("SELECT 1 FROM detection_events WHERE json_extract(data,'$.event_hash')=?",(key,)).fetchone()
     if not exists:
      data=dict(event,event_hash=key)
      self.db.execute('INSERT INTO detection_events(family_id,state,at,data) VALUES(?,?,?,?)',(p['family_id'],event.get('state') or event.get('event'),event.get('at') or str(event.get('index')),json.dumps(data,ensure_ascii=False)))
 def get_history(self,symbol=None,family_id=None):
  sql='SELECT e.* FROM detection_events e JOIN pattern_families f ON f.id=e.family_id WHERE 1=1';args=[]
  if symbol:sql+=' AND f.symbol=?';args.append(symbol)
  if family_id:sql+=' AND e.family_id=?';args.append(family_id)
  sql+=' ORDER BY e.id';return [dict(r) for r in self.db.execute(sql,args)]
 def get_settings(self):return {r['key']:json.loads(r['value']) for r in self.db.execute('SELECT * FROM settings')}
 def put_settings(self,values):
  allowed={'auto_refresh','sma75','sma200','theme'}
  with self.db:
   for key,value in values.items():
    if key not in allowed:raise ValueError('invalid_setting')
    self.db.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value)))
  return self.get_settings()
 def clear_local_data(self):
  with self.db:
   for table in ('detection_events','pattern_families','bars','actions','snapshots','fetch_events','watchlist','settings'):self.db.execute(f'DELETE FROM {table}')
