"""Single source of truth for URLs, credentials and timeouts."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    base_url: str = "https://cpastaging.aisignpro.com/"
    phone: str = "+1 666 444 6664"
    otp: str = "123456"
    # Saved Firebase session (created by scripts/save_auth_state.py)
    storage_state: str = "auth/state.json"
    # Timeouts in milliseconds (staging can be slow)
    action_timeout: int = 20_000
    nav_timeout: int = 45_000
    expect_timeout: int = 15_000
    # Mailinator public inbox
    mailinator_url: str = "https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox}"
    mail_wait_seconds: int = 120
    mail_pattern: str = r"sign|agreement|document|aisign"


settings = Settings()