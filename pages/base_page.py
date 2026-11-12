import re
import logging
import allure
from playwright.sync_api import Locator, Page, expect
log = logging.getLogger(__name__)

class BasePage:
    """Reusable helpers shared by all page objects."""

    def __init__(self, page: Page):
        self.page = page

    # ---------- generic locator helpers ----------
    def button(self, name: str, exact: bool = False) -> Locator:
        """exact=True -> exact text match. Otherwise `name` is a case-insensitive REGEX."""
        if exact:
            return self.page.get_by_role("button", name=name, exact=True).first
        return self.page.get_by_role("button", name=re.compile(name, re.I)).first

    def text(self, pattern: str) -> Locator:
        return self.page.get_by_text(re.compile(pattern, re.I)).first

    def field(self, label: str) -> Locator:
        """Find an input by label OR placeholder (case-insensitive regex)."""
        rx = re.compile(label, re.I)
        return self.page.get_by_label(rx).or_(self.page.get_by_placeholder(rx)).first

    def fill_field(self, label: str, value: str, required: bool = False) -> None:
        loc = self.field(label)
        if not required and loc.count() == 0:
            return  # field not on this form -> skip silently
        expect(loc).to_be_visible()
        loc.fill(value)

    # ---------- shared assertions ----------
    @allure.step("Verify success message is displayed")
    def expect_success_message(self) -> None:
        expect(self.text(r"success")).to_be_visible()

    @allure.step("Fill customer details")
    def fill_customer_details(self, customer) -> None:
        log.info("Filling customer: %s / %s", customer.contact_name, customer.mobile_number)
        ...