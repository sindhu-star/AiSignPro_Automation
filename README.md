# AiSignPro Automation

UI test automation for the AiSign Pro web app, built with **Python, Playwright and pytest** using the **Page Object Model (POM)** design.

## Scenario covered
- Login with phone number and OTP
- Reach the Dashboard (Documents section)
- Create a customer
- Assign an agreement to the customer
- In Assign Agreement page, from the dropdown select the first file
- add signature by using drag and drop method
- after sequential of step send mail(send mail> send anyway >continue to send mail> continue> success message)
- Sign out from the Dashboard page and return to login page

## Tech stack
- Python 3
- Playwright (sync API)
- pytest
- Allure reporting

## Project structure
```
auth/      - login/session handling
config/    - settings
pages/     - page objects (login, dashboard, customer, agreement)
scripts/   - helper scripts
tests/     - test cases
utils/     - helpers and test data builders
conftest.py - fixtures
pytest.ini  - pytest configuration
```

## Setup
```
git clone https://github.com/sindhu-star/AiSignPro_Automation.git
cd AiSignPro_Automation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

## Run the tests
```
pytest tests/test_login.py --headed
```

## Notes
- Login uses an OTP (and a captcha if shown), so it may need a manual step during the run.
- Add your own credentials/test data in the config before running.

## Author
[Your Full Name] - [LinkedIn URL]
