from pathlib import Path
def test_T16_responsive_and_accessibility_contract():
 css=Path('../frontend/src/style.css').read_text();app=Path('../frontend/src/App.tsx').read_text();assert 'min-height: 44px' in css and '@media (max-width: 600px)' in css and 'aria-label' in app and 'role="status"' in app
