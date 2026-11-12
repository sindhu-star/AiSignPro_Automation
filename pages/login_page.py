import os
import re
import time
import logging
import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from pages.base_page import BasePage
log = logging.getLogger(__name__)

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    # ------------------------------------------------------------------
    # Locators (confirmed against the real application HTML)
    # ------------------------------------------------------------------
    @property
    def phone_input(self):
        return self.page.locator("#phone")

    @property
    def terms_checkbox(self):
        return self.page.locator('input[formcontrolname="termsAndConditions"]')

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign In")

    @property
    def otp_fields(self):
        """All OTP boxes (one input per digit, name=otp1..otp6)."""
        return self.page.locator(
            ".otp-inputs input[name^='otp'], input[autocomplete='one-time-code']"
        )

    @property
    def otp_field(self):
        """First OTP box - used to detect that the OTP step is visible."""
        return self.otp_fields.first

    @property
    def verify_button(self):
        return self.page.get_by_role("button", name="Verify").first

    @property
    def documents_tab(self):
        return self.page.get_by_text(re.compile(r"^\s*documents\s*$", re.I)).first

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------
    def open(self) -> None:
        self.page.goto("/")

    def is_logged_in(self, timeout: int = 6_000) -> bool:
        """True when a saved session already landed us on the dashboard."""
        try:
            expect(self.documents_tab).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    # ------------------------------------------------------------------
    # Login steps
    # ------------------------------------------------------------------
    @allure.step("Enter mobile number")
    def enter_phone(self, phone: str = settings.phone) -> None:
        # +1 is a separate prefix and the field has maxlength=14,
        # so type only the 10 national digits; the mask formats them.
        national = re.sub(r"\D", "", phone)[-10:]
        expect(self.phone_input).to_be_visible()
        self.phone_input.click()
        self.phone_input.press_sequentially(national, delay=40)

    @allure.step("Accept Terms & Conditions")
    def accept_terms(self) -> None:
        try:
            self.terms_checkbox.check(timeout=5_000)
        except Exception:                        # custom-styled checkbox: click its label
            self.page.get_by_text("I agree to the").click()
        expect(self.sign_in_button).to_be_enabled()

    # ---------- captcha handling ----------
    def _challenge_on_screen(self) -> bool:
        """True when the reCAPTCHA picture pop-up is really displayed (not parked off-screen)."""
        challenge = self.page.locator("iframe[title*='recaptcha challenge' i]")
        box = challenge.first.bounding_box() if challenge.count() else None
        return bool(box and box["y"] >= 0 and box["width"] > 100)

    def _page_messages(self) -> str:
        """Visible alert/toast/validation text - explains a stuck login."""
        loc = self.page.locator("[role='alert'], .toast, .toast-message, .Toastify__toast, "
                                ".alert, .invalid-feedback, .text-danger")
        texts = [t.strip() for t in loc.all_inner_texts() if t.strip()]
        return " | ".join(texts) or "none"

    def _wait_for_human(self, seconds: int = 180) -> None:
        """Headed mode: a person solves the captcha; continue as soon as the OTP step shows.
        If the pop-up closes/expires and we are still on step 1, press Sign in again (max 2x)."""
        deadline = time.time() + seconds
        idle, retries = 0, 0
        while time.time() < deadline:
            if self.otp_field.is_visible():
                return
            if self._challenge_on_screen():
                idle = 0
            else:
                idle += 1
                if idle >= 8 and retries < 2 and self.sign_in_button.is_enabled():
                    retries += 1
                    idle = 0
                    self.sign_in_button.click()
                    self.page.wait_for_timeout(2_000)
            self.page.wait_for_timeout(1_000)
        raise AssertionError("OTP step did not appear after the captcha. "
                             f"Messages on page: {self._page_messages()} "
                             f"(sign-in re-clicks: {retries})")

    @allure.step("Handle reCAPTCHA if shown")
    def handle_captcha(self) -> None:
        """Invisible captcha normally passes silently. A challenge ON SCREEN needs a human."""
        self.page.wait_for_timeout(2_000)
        if self.otp_field.is_visible():          # already on the OTP step -> no captcha
            return
        if self._challenge_on_screen():
            if os.getenv("MANUAL_CAPTCHA") == "1":
                with allure.step("Waiting up to 3 min for a human to solve the captcha"):
                    self._wait_for_human()
                return
            pytest.skip("Captcha challenge on screen. Run with MANUAL_CAPTCHA=1 "
                        "(headed) or use scripts/save_auth_state.py.")

    @allure.step("Click Sign in (requests OTP)")
    def request_otp(self) -> None:
        self.sign_in_button.click()
        self.handle_captcha()

    # ---------- OTP ----------
    @allure.step("Enter OTP and verify")
    def enter_otp(self, otp: str = settings.otp) -> None:
        fields = self.otp_fields
        fields.first.wait_for(state="visible")
        if fields.count() > 1:                   # one box per digit
            for i, digit in enumerate(otp):
                fields.nth(i).fill(digit)
        else:                                     # single input field
            fields.first.fill(otp)
        # Some apps auto-submit after the last digit; click Verify only if it is there.
        if self.verify_button.is_visible():
            expect(self.verify_button).to_be_enabled()
            self.verify_button.click()

    @allure.step("Login with phone + OTP (skip if session already active)")
    def login(self) -> None:
        self.open()
        if self.is_logged_in():
            return
        self.enter_phone()
        self.accept_terms()
        self.request_otp()
        self.enter_otp()
        expect(self.documents_tab).to_be_visible   # Dashboard loaded

    @allure.step("Verify login page is displayed (signed out)")
    def expect_login_page(self) -> None:
        expect(self.phone_input).to_be_visible()

    @allure.step("Fill customer details")
    def fill_customer_details(self, customer) -> None:
        log.info("Filling customer: %s / %s", customer.contact_name, customer.mobile_number)
        ...