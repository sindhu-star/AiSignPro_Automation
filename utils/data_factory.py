import random
import time
from dataclasses import dataclass


@dataclass
class Customer:
    mobile_number: str
    contact_name: str
    email_id: str


def _random_us_mobile() -> str:
    # US numbers: area code and exchange can't start with 0 or 1
    area = random.randint(200, 999)
    exchange = random.randint(200, 999)
    line = random.randint(0, 9999)
    return f"{area}{exchange}{line:04d}"


def build_customer() -> Customer:
    stamp = int(time.time())  # keeps names and emails unique per run
    return Customer(
        mobile_number=_random_us_mobile(),
        contact_name=f"Auto Test{stamp % 10000}",
        email_id=f"autotest{stamp}@mailinator.com",
    )