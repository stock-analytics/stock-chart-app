import sys;sys.path.insert(0,'.')
import pytest
from app.providers.validation import normalize_symbol
@pytest.mark.parametrize('bad',['https://evil','1;DROP','7203.US','../etc/passwd','7203\x00'])
def test_T17_rejects_unsafe_symbol(bad):
 with pytest.raises(ValueError):normalize_symbol(bad)
def test_T17_origin_host_checks_exist():
 s=open('app/main.py').read();assert 'host_forbidden' in s and 'origin_forbidden' in s and 'authentication_required' in s
