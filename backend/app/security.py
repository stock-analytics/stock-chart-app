"""Opt-in LAN security: PBKDF2 password, signed HttpOnly session and double-submit CSRF."""
from __future__ import annotations
import base64,hashlib,hmac,json,secrets,time
from collections import defaultdict,deque
class AuthManager:
 def __init__(self,password_hash:str,secret:str,ttl=43200,max_attempts=5,window=900):
  self.password_hash=password_hash;self.secret=secret.encode();self.ttl=ttl;self.max_attempts=max_attempts;self.window=window;self.attempts=defaultdict(deque)
 @staticmethod
 def hash_password(password,salt=None,rounds=310000):
  salt=salt or secrets.token_bytes(16);digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,rounds)
  return f'pbkdf2_sha256${rounds}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}'
 def verify(self,password):
  try:_,r,s,d=self.password_hash.split('$');actual=hashlib.pbkdf2_hmac('sha256',password.encode(),base64.urlsafe_b64decode(s),int(r));return hmac.compare_digest(actual,base64.urlsafe_b64decode(d))
  except Exception:return False
 def allowed(self,client):
  now=time.time();q=self.attempts[client]
  while q and q[0]<now-self.window:q.popleft()
  return len(q)<self.max_attempts
 def login(self,client,password):
  if not self.allowed(client):raise PermissionError('rate_limited')
  if not self.verify(password):self.attempts[client].append(time.time());raise PermissionError('invalid_credentials')
  self.attempts.pop(client,None);payload={'exp':int(time.time()+self.ttl),'nonce':secrets.token_urlsafe(16)};raw=base64.urlsafe_b64encode(json.dumps(payload).encode()).decode();sig=hmac.new(self.secret,raw.encode(),hashlib.sha256).hexdigest();return raw+'.'+sig,secrets.token_urlsafe(32)
 def validate(self,token):
  try:raw,sig=token.rsplit('.',1);expected=hmac.new(self.secret,raw.encode(),hashlib.sha256).hexdigest();data=json.loads(base64.urlsafe_b64decode(raw));return hmac.compare_digest(sig,expected) and data['exp']>=time.time()
  except Exception:return False
