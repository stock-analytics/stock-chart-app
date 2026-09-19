from __future__ import annotations
import os,uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlsplit
from .providers.synthetic import SyntheticProvider
from .providers.yahoo import YFinanceProvider
from .providers.coordinator import FetchCoordinator
from .providers.quality import validate_snapshot
from .providers.validation import normalize_symbol
from .analysis.service import analyze
from .analysis.patterns import catalog
from .storage.database import Database,SCHEMA_VERSION
from .security import AuthManager
try:
 from fastapi import FastAPI,Request,HTTPException
 from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 from pydantic import BaseModel
except ImportError: FastAPI=None
LAN_MODE=os.getenv('LAN_MODE','false').lower()=='true'
if LAN_MODE and (not os.getenv('LAN_PASSWORD_HASH') or not os.getenv('SESSION_SECRET')):raise RuntimeError('LAN mode requires LAN_PASSWORD_HASH and SESSION_SECRET')
AUTH=AuthManager(os.getenv('LAN_PASSWORD_HASH',''),os.getenv('SESSION_SECRET','development-not-for-lan'))
DB=Database(os.getenv('CHART_LENS_DB','data/chart-lens.sqlite3')); CACHE={}; JOBS={}; SYMBOL_JOBS={}
provider=YFinanceProvider() if os.getenv('DATA_MODE','synthetic')=='live' else SyntheticProvider();coordinator=FetchCoordinator();executor=ThreadPoolExecutor(max_workers=1)
if FastAPI:
 app=FastAPI(title='Chart Lens',version='1.0.0')
 class AnalyzeRequest(BaseModel): symbol:str; timeframe:str='1d'; range:str='2y'; as_of:date|None=None
 class RefreshRequest(BaseModel): symbol:str
 @app.middleware('http')
 async def security_guard(request:Request,call_next):
  local={'127.0.0.1','localhost','testserver'};allowed_hosts=local|set(filter(None,os.getenv('ALLOWED_HOSTS','').split(',')))
  host=request.url.hostname or ''
  if host not in allowed_hosts:return JSONResponse({'error':{'code':'host_forbidden','message':'許可されていないHostです','retry_after':None}},403)
  origin=request.headers.get('origin')
  if origin:
   parsed=urlsplit(origin);local_http=parsed.scheme=='http' and parsed.hostname in local;lan_https=parsed.scheme=='https' and parsed.hostname in allowed_hosts
   if not (local_http or lan_https):return JSONResponse({'error':{'code':'origin_forbidden','message':'許可されていないOriginです','retry_after':None}},403)
  if LAN_MODE:
   if request.url.scheme!='https' and request.headers.get('x-forwarded-proto')!='https':return JSONResponse({'error':{'code':'https_required','message':'LANモードはHTTPS必須です','retry_after':None}},403)
   if request.url.path!='/api/login':
    if not AUTH.validate(request.cookies.get('chart_lens_session','')):return JSONResponse({'error':{'code':'authentication_required','message':'認証が必要です','retry_after':None}},401)
    if request.method in {'POST','PUT','DELETE','PATCH'} and request.headers.get('x-csrf-token')!=request.cookies.get('chart_lens_csrf'):return JSONResponse({'error':{'code':'csrf_failed','message':'CSRF検証に失敗しました','retry_after':None}},403)
  return await call_next(request)
 @app.post('/api/login')
 async def login(request:Request):
  body=await request.json();client=request.client.host if request.client else 'unknown'
  try:session,csrf=AUTH.login(client,str(body.get('password','')))
  except PermissionError as e:return JSONResponse({'error':{'code':str(e),'message':'ログインできません','retry_after':900 if str(e)=='rate_limited' else None}},429 if str(e)=='rate_limited' else 401)
  response=JSONResponse({'csrf_token':csrf});response.set_cookie('chart_lens_session',session,httponly=True,samesite='strict',secure=LAN_MODE,max_age=43200);response.set_cookie('chart_lens_csrf',csrf,httponly=False,samesite='strict',secure=LAN_MODE,max_age=43200);return response
 @app.get('/api/health')
 def health():return {'version':'1.0.0','db_version':SCHEMA_VERSION,'data_mode':os.getenv('DATA_MODE','synthetic')}
 @app.get('/api/pattern-catalog')
 def patterns():return catalog()
 def _run_refresh(job,symbol):
  try:
   result=coordinator.fetch(symbol,lambda:provider.fetch_daily(symbol,date.today()-timedelta(days=3650),date.today()+timedelta(days=1))).result();result.bars=validate_snapshot(result.bars);sid=DB.save_snapshot(symbol,result.provider,result.bars,result.fetched_at);CACHE[symbol]=(result,sid);JOBS[job]={'status':'succeeded'}
  except Exception as e:JOBS[job]={'status':'failed','error':getattr(e,'code','provider_error'),'retry_after':getattr(e,'retry_after',None)}
  finally:SYMBOL_JOBS.pop(symbol,None)
 @app.post('/api/refresh')
 def refresh(body:RefreshRequest):
  symbol=body.symbol if body.symbol.startswith('DEMO_') else normalize_symbol(body.symbol)
  if isinstance(provider,SyntheticProvider) and not symbol.startswith('DEMO_'):raise HTTPException(503,'live_provider_disabled')
  if isinstance(provider,YFinanceProvider) and symbol.startswith('DEMO_'):raise HTTPException(422,'invalid_live_symbol')
  if symbol in SYMBOL_JOBS:return {'job_id':SYMBOL_JOBS[symbol]}
  job=str(uuid.uuid4());JOBS[job]={'status':'queued'};SYMBOL_JOBS[symbol]=job;executor.submit(_run_refresh,job,symbol);return {'job_id':job}
 @app.get('/api/jobs/{job_id}')
 def jobs(job_id:str): return JOBS.get(job_id,{'status':'failed','error':'job_not_found'})
 @app.post('/api/analyze')
 def do_analyze(body:AnalyzeRequest):
  if body.timeframe not in ('1d','1wk','1mo') or body.range not in ('6mo','2y','5y','all'):raise HTTPException(422,'invalid_parameter')
  symbol=body.symbol if body.symbol.startswith('DEMO_') else normalize_symbol(body.symbol)
  if symbol not in CACHE:return JSONResponse({'job_id':refresh(RefreshRequest(symbol=symbol))['job_id']},status_code=202)
  result,sid=CACHE[symbol]; response=analyze(symbol,result.bars,body.timeframe,body.range,body.as_of,sid); DB.save_pattern_history(symbol,response['patterns']); return response
 @app.get('/api/settings')
 def settings():return {'theme':'dark','auto_refresh':False,'sma75':False,'sma200':False}|DB.get_settings()
 @app.put('/api/settings')
 def put_settings(body:dict):
  try:return DB.put_settings(body)
  except ValueError:raise HTTPException(422,'invalid_setting')
 @app.get('/api/watchlist')
 def watchlist():return DB.watchlist()
 @app.post('/api/watchlist')
 def add_watch(body:dict): symbol=normalize_symbol(body.get('symbol','')); DB.add_watch(symbol); return DB.watchlist()
 @app.delete('/api/watchlist/{symbol}')
 def delete_watch(symbol:str):
  with DB.db: DB.db.execute('DELETE FROM watchlist WHERE symbol=?',(normalize_symbol(symbol),))
  return DB.watchlist()
 @app.delete('/api/local-data')
 def clear_local_data(body:dict):
  if body.get('confirmation')!='DELETE':raise HTTPException(422,'confirmation_required')
  DB.clear_local_data();CACHE.clear();return {'deleted':True}
 @app.get('/api/history')
 def history(symbol:str,family_id:str|None=None):
  return DB.get_history(normalize_symbol(symbol) if not symbol.startswith('DEMO_') else symbol,family_id)
 dist=Path(__file__).parents[2]/'frontend'/'dist'
 if dist.exists(): app.mount('/',StaticFiles(directory=dist,html=True),name='frontend')
else: app=None
