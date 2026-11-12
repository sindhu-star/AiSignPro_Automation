import os
from pathlib import Path
from playwright.sync_api import expect
from config.settings import settings
import allure
import pytest
from utils.data_factory import build_customer
from utils.screenshots import snap
@allure.epic("AiSign Pro")
@allure.feature("Customer & Agreements")
@allure.story("Create customer and assign agreement")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e

def test_login_and_reach_dashboard(login_page, dashboard_page, context, customer_page, agreement_page):
    customer = build_customer()
    # phone -> terms -> Sign in -> (captcha if shown) -> OTP -> Verify
    login_page.login()

    # We have left the login form...
    with allure.step("Login form is gone"):
        expect(login_page.phone_input).to_be_hidden(timeout=30)

    # ...and the Dashboard (Documents section) is displayed
    dashboard_page.expect_loaded()

    # Optional: SAVE_AUTH=1 stores the logged-in session so later runs skip the captcha
    if os.getenv("SAVE_AUTH") == "1":
        Path(settings.storage_state).parent.mkdir(exist_ok=True)
        context.storage_state(path=settings.storage_state, indexed_db=True)

    dashboard_page.open_customer_tab()

    customer = build_customer()
    customer_page.open_customer_form()
    customer_page.fill_customer_details(customer)
    customer_page.click_assign_document()

    agreement_page.expect_loaded()
    agreement_page.open_documents_list()
    agreement_page.select_first_document()
    agreement_page.drag_signature_to_document()
    agreement_page.send_document()

    dashboard_page.click_profile_signout()
    agreement_page.drag_signature_to_document()
    expect(login_page.phone_input).to_be_visible()


