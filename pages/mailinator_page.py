import re
import allure
from playwright.sync_api import Page, expect
from config.settings import settings
class MailinatorPage:
    """Public Mailinator inbox (no login required)."""
    def __init__(self, page: Page):
        self.page = page
    @allure.step("Open Mailinator inbox: {inbox}")
    def open_inbox(self, inbox: str) -> None:
        self.page.goto(settings.mailinator_url.format(inbox=inbox))
    @allure.step("Verify mail received in Mailinator")
    def expect_mail_received(self, pattern: str = settings.mail_pattern) -> None:
        row = self.page.locator("table tr").filter(has_text=re.compile(pattern, re.I)).first
        deadline_loops = settings.mail_wait_seconds // 15
        for _ in range(deadline_loops):
            try:
                expect(row).to_be_visible(timeout=15_000)
                break
            except AssertionError:
                self.page.reload()
        expect(row).to_be_visible(timeout=5_000)  # final assertion (fails if no mail)
        row.click()                 # open the mail