from pathlib import Path
def test_T19_readme_has_install_start_stop_migration_test():
 s=Path('../README.md').read_text();assert all(x in s for x in ('python -m venv','npm ci','uvicorn','Ctrl-C','DB移行','pytest -q','npm run build'))
