import base64
from pathlib import Path
import allure
import pytest
from playwright.sync_api import expect
from pytest_html import extras
from config.settings import settings
from pages.agreement_page import AgreementPage
from pages.customer_page import CustomerPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.mailinator_page import MailinatorPage
import base64
import logging

import pytest
from pytest_html import extras

from utils.screenshots import pop_all, snap

log = logging.getLogger(__name__)
expect.set_options(timeout=settings.expect_timeout)
# ---------------- browser context ---------------
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    args = {**browser_context_args, "viewport": {"width": 1440, "height": 900}}
    state = Path(settings.storage_state)
    if state.exists():   # reuse a saved Firebase session
       args["storage_state"] = str(state)
    return args
@pytest.fixture(autouse=True)
def _timeouts(page):
    page.set_default_timeout(settings.action_timeout)
    page.set_default_navigation_timeout(settings.nav_timeout)
# ---------------- page-object fixtures ---------------
@pytest.fixture
def login_page(page):
    return LoginPage(page)
@pytest.fixture
def dashboard_page(page):
    return DashboardPage(page)
@pytest.fixture
def customer_page(page):
    return CustomerPage(page)
@pytest.fixture
def agreement_page(page):
    return AgreementPage(page)
@pytest.fixture
def mailinator(context):
    """Mailinator opens in a SECOND tab so the app tab is untouched."""
    return MailinatorPage(context.new_page())
# ---------------- failure screenshot -> Allure + pytest-html ---------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            try:
                png = page.screenshot(full_page=True)
                allure.attach(png, name="Failure screenshot",
                              attachment_type=allure.attachment_type.PNG)
                allure.attach(page.url, name="URL at failure",
                              attachment_type=allure.attachment_type.TEXT)
                report.extras = getattr(report, "extras", []) + [
                    extras.png(base64.b64encode(png).decode())
                ]
            except Exception as exc:               # never hide the real failure
               print(f"Could not capture screenshot: {exc}")
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    # Final screenshot for every test (pass or fail)
    context = item.funcargs.get("context")
    page = item.funcargs.get("page")
    if page is None and context and context.pages:
        page = context.pages[-1]
    if page is not None and not page.is_closed():
        status = "FAILED" if report.failed else "PASSED"
        snap(page, f"Final screen - {status}")

    # Attach everything queued during the test to pytest-html (v4)
    report.extras = getattr(report, "extras", [])
    for name, png in pop_all():
        report.extras.append(
            extras.png(base64.b64encode(png).decode(), name=name)
        )
    log.info("Test finished: %s (%s)", item.name, report.outcome)