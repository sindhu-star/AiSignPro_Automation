import re
import allure
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
log = logging.getLogger(__name__)

class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    # ================= LOCATORS (from the real aria snapshot) =================
    @property
    def heading(self):
        return self.page.get_by_role("heading", name="Documents", level=1)
    @property
    def customer_button(self):
        return self.page.locator("a.nav-link[role='button']").filter(has_text="Customers")

    @property
    def profile_button(self):
        # Bottom-left account button, e.g. "QA QA Automation CPA"
        return self.page.get_by_role("complementary").get_by_role("button", name="Account menu")

    @property
    def sign_out_item(self):
        # Menu item shown after opening the profile menu
        return self.page.get_by_text(re.compile(r"^\s*Sign out\s*$", re.I))

    # ================= ACTIONS =================
    @allure.step("Verify dashboard opened with the Documents section selected")
    def expect_loaded(self) -> None:
        expect(self.heading).to_be_visible()

    @allure.step("Open Customers tab")
    def open_customer_tab(self) -> None:
        expect(self.customer_button).to_be_visible()
        self.customer_button.click()

    @allure.step("Open the profile menu and click Sign out")
    def click_profile_signout(self) -> None:
        expect(self.profile_button).to_be_visible(timeout=30000)
        self.profile_button.click()
        expect(self.sign_out_item).to_be_visible()
        self.sign_out_item.click()

    @allure.step("Fill customer details")
    def fill_customer_details(self, customer) -> None:
        log.info("Filling customer: %s / %s", customer.contact_name, customer.mobile_number)
        ...