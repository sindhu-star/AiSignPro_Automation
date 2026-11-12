import logging
import re
import allure
import logging
from playwright.sync_api import Page, expect

from pages.base_page import BasePage

log = logging.getLogger(__name__)


class AgreementPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    # ================= LOCATORS =================
    # --- page header ---
    @property
    def breadcrumb(self):
        return self.page.locator("nav.ai-crumbs b", has_text="Assign Documents")

    @property
    def page_title(self):
        return self.page.locator(".aa-title", has_text="Assign Documents")

    # --- left "Documents" panel ---
    @property
    def doc_dock(self):
        return self.page.locator(".aa-doc-dock")

    @property
    def doc_rail(self):
        # Shown only when the panel is NOT pinned (auto-hide mode)
        return self.page.locator(".aa-doc-rail")

    @property
    def doc_panel(self):
        return self.page.locator(".aa-left .aa-panel")

    @property
    def doc_items(self):
        return self.page.locator(".aa-doc-list .aa-doc-item")

    @property
    def first_doc_item(self):
        return self.doc_items.first

    @property
    def first_doc_checkbox(self):
        return self.first_doc_item.locator("input[type='checkbox']")

    # --- "Drag to place" section ---
    @property
    def drag_to_place_label(self):
        return self.page.locator(".fpe-section-label", has_text="Drag to place")

    @property
    def signature_chip(self):
        return self.page.locator(".fpe-chip[title='Signature']")

    @property
    def drop_zone(self):
        # First page of the document; use .nth(n) for other pages
        return self.page.locator(".fpe-place-zone").first

    @property
    def placed_fields(self):
        return self.page.locator(".fpe-place-zone .fpe-field-overlay")

    @property
    def send_mail_button(self):
        return self.page.locator("button.btn-primary", has_text="Send Mail")

    @property
    def send_anyway_button(self):
        return self.page.get_by_role("button", name="Send anyway")

    @property
    def continue_to_send_button(self):
        return self.page.get_by_role("button", name="Continue to Send Mail")

    @property
    def continue_button(self):
        # exact=True so it doesn't also match "Continue to Send Mail"
        return self.page.get_by_role("button", name="Continue", exact=True)

    @property
    def swal_popup(self):
        return self.page.locator(".swal2-container .swal2-popup")

    @property
    def swal_ok(self):
        return self.page.locator(".swal2-container .swal2-confirm")

    @property
    def success_popup(self):
        return self.page.locator(".swal2-popup.swal2-icon-success")

    # ================= ACTIONS =================
    @allure.step("Verify Assign Documents page is open")
    def expect_loaded(self) -> None:
        expect(self.page_title).to_be_visible()
        expect(self.breadcrumb).to_contain_text("Assign Documents")
        expect(self.doc_panel).to_be_visible()

    @allure.step("Open the documents list in the left panel")
    def open_documents_list(self) -> None:
        # If the panel is pinned the list is already visible.
        # Otherwise, it is collapsed to a rail and opens on hover.
        if self.page.locator(".aa-doc-dock.pinned").count() == 0:
            log.info("Documents panel is collapsed, hovering the rail")
            self.doc_rail.hover()
        expect(self.doc_items.first).to_be_visible()

    @allure.step("Select the first document checkbox")
    def select_first_document(self) -> None:
        checkbox = self.first_doc_checkbox
        expect(checkbox).to_be_visible()
        checkbox.check()
        expect(checkbox).to_be_checked()
        log.info("Selected document: %s",
                 self.first_doc_item.locator(".aa-doc-name").inner_text())

    @allure.step("Drag the Signature field onto the document")
    def drag_signature_to_document(self, x: int = 250, y: int = 300) -> None:
        expect(self.drag_to_place_label).to_be_visible()
        expect(self.signature_chip).to_be_visible()
        expect(self.drop_zone).to_be_visible()

        before = self.placed_fields.count()

        # Attempt 1: Playwright's native drag (works for most HTML5 DnD)
        self.signature_chip.drag_to(self.drop_zone, target_position={"x": x, "y": y})

        # Attempt 2: dispatch the HTML5 drag events manually
        if not self._field_added(before):
            log.warning("drag_to did not place the field, using JS drag events")
            self.signature_chip.evaluate(
                """(src, a) => {
                    const dst = document.querySelector('.fpe-place-zone');
                    const r = dst.getBoundingClientRect();
                    const dt = new DataTransfer();
                    const o = {bubbles: true, cancelable: true, dataTransfer: dt,
                               clientX: r.left + a.x, clientY: r.top + a.y};
                    src.dispatchEvent(new DragEvent('dragstart', o));
                    dst.dispatchEvent(new DragEvent('dragenter', o));
                    dst.dispatchEvent(new DragEvent('dragover', o));
                    dst.dispatchEvent(new DragEvent('drop', o));
                    src.dispatchEvent(new DragEvent('dragend', o));
                }""",
                {"x": x, "y": y},
            )

        expect(self.placed_fields).to_have_count(before + 1)

    def _field_added(self, before: int) -> bool:
        try:
            expect(self.placed_fields).to_have_count(before + 1, timeout=2000)
            return True
        except AssertionError:
            return False

    @allure.step("Click 'Send Mail' (top right)")
    def click_send_mail(self) -> None:
        expect(self.send_mail_button).to_be_enabled()
        self.send_mail_button.click()

    @allure.step("Click 'Send anyway' in the warning popup")
    def click_send_anyway(self) -> None:
        expect(self.send_anyway_button).to_be_visible()
        self.send_anyway_button.click()

    @allure.step("Click 'Continue to Send Mail' in the preview popup")
    def click_continue_to_send_mail(self) -> None:
        expect(self.continue_to_send_button).to_be_visible()
        self.continue_to_send_button.click()

    @allure.step("Click 'Continue' in the Assignment Options popup")
    def click_continue_assignment_options(self) -> None:
        expect(self.continue_button).to_be_visible()
        self.continue_button.click()

    @allure.step("Verify the success message")
    def verify_success_message(self) -> None:
        expect(self.swal_popup).to_be_visible(timeout=30000)
        message = self.swal_popup.inner_text()
        log.info("Success popup: %s", message)
        allure.attach(message, name="Success popup",
                      attachment_type=allure.attachment_type.TEXT)
        expect(self.swal_popup).to_contain_text(re.compile("success", re.I))
        self.swal_ok.click()
        expect(self.page.locator(".swal2-container")).to_be_hidden()

    @allure.step("Send the document: Send Mail > Send anyway > Continue to Send Mail > Continue")
    def send_document(self) -> None:
        self.click_send_mail()
        self.click_send_anyway()
        self.click_continue_to_send_mail()
        self.click_continue_assignment_options()
        self.verify_success_message()

    @allure.step("Verify the success message")
    def verify_success_message(self) -> None:
        # Skips the "Sending mail..." loading state; waits for the success variant
        expect(self.success_popup).to_be_visible(timeout=60000)
        message = self.success_popup.inner_text()
        log.info("Success popup: %s", message)
        allure.attach(message, name="Success popup",
                      attachment_type=allure.attachment_type.TEXT)
        expect(self.success_popup).to_contain_text("Agreement email sent to the customer")

        # The popup may auto-close, so only click OK if it is still there
        ok = self.page.locator(".swal2-container .swal2-confirm")
        if ok.is_visible():
            ok.click()
        expect(self.page.locator(".swal2-container")).to_be_hidden()

    @allure.step("Fill customer details")
    def fill_customer_details(self, customer) -> None:
        log.info("Filling customer: %s / %s", customer.contact_name, customer.mobile_number)
        ...