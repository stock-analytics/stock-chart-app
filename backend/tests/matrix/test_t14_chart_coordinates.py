from pathlib import Path
def test_T14_chart_uses_time_price_and_resize_observer():
 s=Path('../frontend/src/Chart.tsx').read_text();assert 'time: b.date' in s and 'value:' in s and 'ResizeObserver' in s and 'autoSize: true' in s
