import logging
import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.data_factory import Customer
from utils.screenshots import snap

log = logging.getLogger(__name__)


class CustomerPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    # ================= LOCATORS =================
    @property
    def add_customer_button(self):
        # Accessible name starts with an icon glyph, so match on the text only
        return self.page.get_by_role("button", name="Add Customer")

    @property
    def mobile_number(self):
        return self.page.get_by_placeholder("Enter mobile number")

    @property
    def contact_name(self):
        return self.page.get_by_placeholder("Enter contact name")

    @property
    def email_id(self):
        return self.page.get_by_placeholder("Enter email ID")

    @property
    def assign_document(self):
        return self.page.get_by_role("button", name="Assign Documents")

    @property
    def validation_errors(self):
        return self.page.get_by_text("is required")

    # --- SweetAlert2 popup (HTML modal, not a native dialog) ---
    @property
    def swal_container(self):
        return self.page.locator(".swal2-container")

    @property
    def swal_popup(self):
        return self.page.locator(".swal2-container .swal2-popup")

    @property
    def swal_ok(self):
        return self.page.locator(".swal2-container .swal2-confirm")

    # ================= ACTIONS =================
    @allure.step("Open customer form")
    def open_customer_form(self) -> None:
        expect(self.add_customer_button).to_be_visible()
        self.add_customer_button.click()
        expect(self.mobile_number).to_be_visible()
        # let the form's API calls finish so it doesn't reset after we fill it
        self.page.wait_for_load_state("networkidle")

    @allure.step("Fill customer details")
    def fill_customer_details(self, customer: Customer) -> None:
        log.info("Filling customer: %s / %s / %s",
                 customer.contact_name, customer.mobile_number, customer.email_id)

        expect(self.mobile_number).to_be_editable()
        self._type_all(customer)

        # Retry once if the form reset itself after the first fill
        try:
            expect(self.contact_name).to_have_value(customer.contact_name, timeout=3000)
            expect(self.email_id).to_have_value(customer.email_id, timeout=3000)
        except AssertionError:
            log.warning("Form was reset after filling, filling again")
            self.mobile_number.fill("")
            self._type_all(customer)

        expect(self.contact_name).to_have_value(customer.contact_name)
        expect(self.email_id).to_have_value(customer.email_id)
        # The phone field is masked, so compare digits only
        digits = re.sub(r"\D", "", self.mobile_number.input_value())
        assert digits.endswith(customer.mobile_number), \
            f"Mobile not entered correctly: {digits!r}"
        snap(self.page, "Customer form filled")

    def _type_all(self, customer: Customer) -> None:
        # Masked phone input: type key by key instead of fill()
        self.mobile_number.click()
        self.mobile_number.press_sequentially(customer.mobile_number, delay=40)
        self.contact_name.fill(customer.contact_name)
        self.email_id.fill(customer.email_id)

    @allure.step("Click 'Assign Documents' and confirm the success popup")
    def click_assign_document(self) -> None:
        values = {
            "mobile": self.mobile_number.input_value(),
            "name": self.contact_name.input_value(),
            "email": self.email_id.input_value(),
        }
        log.info("Values just before click: %s", values)
        allure.attach(str(values), name="Form values before click",
                      attachment_type=allure.attachment_type.TEXT)

        # No validation errors should be showing before we submit
        expect(self.validation_errors).to_have_count(0)

        self.assign_document.click()
        snap(self.page, "After Assign Documents click")

        expect(self.swal_popup).to_be_visible(timeout=15000)
        message = self.swal_popup.inner_text()
        log.info("Popup message: %s", message)
        allure.attach(message, name="Popup message",
                      attachment_type=allure.attachment_type.TEXT)

        # Fail here, with a clear reason, if the customer was not created
        expect(self.swal_popup).to_contain_text("created successfully")

        self.swal_ok.first.click()
        expect(self.swal_container).to_be_hidden()