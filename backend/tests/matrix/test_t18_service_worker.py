from pathlib import Path
def test_T18_service_worker_excludes_api_and_reports_offline():
 s=Path('../frontend/public/sw.js').read_text();assert "startsWith('/api/')" in s;assert '分析サーバーへ接続できません' in s;assert '/api/' not in s.split('SHELL=')[1].split(';')[0]
