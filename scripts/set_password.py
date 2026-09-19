#!/usr/bin/env python3
import getpass,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from backend.app.security import AuthManager
p=getpass.getpass('LAN password: '); confirm=getpass.getpass('Confirm: ')
if len(p)<12 or p!=confirm:raise SystemExit('Passwords must match and contain at least 12 characters')
print('LAN_PASSWORD_HASH='+AuthManager.hash_password(p))
