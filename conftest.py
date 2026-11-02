import json
import os
import pytest

@pytest.fixture(scope='session')
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        engine = os.getenv('BROWSER', 'chromium')
        options = {'headless': True}
        if os.getenv('BROWSER_CHANNEL'):
            options['channel'] = os.environ['BROWSER_CHANNEL']
        b = getattr(p, engine).launch(**options)
        print('Browser version:', b.version)
        yield b
        b.close()

@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={'width':1912,'height':966}, device_scale_factor=1)
    page = context.new_page()
    page.set_default_timeout(15000)
    yield page
    context.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    if report.when == 'call' and report.failed and 'page' in item.funcargs:
        import allure
        page = item.funcargs['page']
        allure.attach(page.url, 'URL', allure.attachment_type.TEXT)
        allure.attach(page.screenshot(), 'Failure', allure.attachment_type.PNG)
        allure.attach(page.content(), 'DOM', allure.attachment_type.HTML)
