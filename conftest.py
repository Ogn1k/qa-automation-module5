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
def page(browser, request):
    import allure
    allure.dynamic.parameter('browser', os.getenv('BROWSER', 'chromium'))
    context = browser.new_context(viewport={'width':1912,'height':966}, device_scale_factor=1)
    page = context.new_page()
    page.set_default_timeout(15000)
    request.node._module5_page = page
    yield page
    context.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    page = item.funcargs.get('page') or getattr(item, '_module5_page', None)
    if report.when in ('setup', 'call') and report.failed and page is not None:
        import allure
        if not page.is_closed():
            for name, producer, kind in [
                ('URL', lambda: page.url, allure.attachment_type.TEXT),
                ('Failure', lambda: page.screenshot(), allure.attachment_type.PNG),
                ('DOM', lambda: page.content(), allure.attachment_type.HTML),
            ]:
                try:
                    allure.attach(producer(), name, kind)
                except Exception as error:
                    # Diagnostics must preserve the original test failure.
                    allure.attach(str(error), name + ' capture error', allure.attachment_type.TEXT)
