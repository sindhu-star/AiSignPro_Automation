import allure

_shots: list[tuple[str, bytes]] = []


def snap(page, name: str) -> None:
    """Take a screenshot and queue it for the HTML report + Allure."""
    try:
        png = page.screenshot(full_page=True)
    except Exception:
        return
    _shots.append((name, png))
    allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)


def pop_all() -> list[tuple[str, bytes]]:
    items = _shots.copy()
    _shots.clear()
    return items