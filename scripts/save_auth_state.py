"""Run ONCE when the captcha blocks automated login (from the project root):

    python scripts/save_auth_state.py

A browser opens. Log in manually (tick Terms, Sign in, solve captcha if shown,
enter OTP 123456), wait until the Dashboard is visible, then press ENTER in the
terminal. The session is saved to auth/state.json and reused by pytest.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))          # so "from config.settings" works from scripts/

from playwright.sync_api import sync_playwright  # noqa: E402

from config.settings import settings  # noqa: E402

state_file = ROOT / settings.storage_state

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto(settings.base_url)
    input("Login manually, wait for the Dashboard, then press ENTER here... ")
    state_file.parent.mkdir(exist_ok=True)
    # indexed_db=True is REQUIRED: Firebase keeps its auth token in IndexedDB
    context.storage_state(path=str(state_file), indexed_db=True)
    browser.close()

print("Saved ->", state_file)