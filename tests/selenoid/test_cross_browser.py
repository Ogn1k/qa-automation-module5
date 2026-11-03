import json
import os
import uuid
from pathlib import Path

import allure
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.selenium_select_menu_page import SeleniumSelectMenuPage

pytestmark = [pytest.mark.selenoid, allure.feature('Select Menu / Selenoid')]


@pytest.fixture(params=['chrome', 'firefox'])
def remote_menu(request):
    url = os.environ['SELENOID_URL'].rstrip('/')
    browser = request.param
    options = webdriver.ChromeOptions() if browser == 'chrome' else webdriver.FirefoxOptions()
    options.browser_version = '128.0' if browser == 'chrome' else '125.0'
    video_name = f'{request.node.originalname}-{browser}-{uuid.uuid4().hex[:8]}.mp4'
    options.set_capability('selenoid:options', {
        'enableVNC': True, 'enableVideo': True, 'videoName': video_name,
        'screenResolution': '1920x1080x24', 'name': request.node.nodeid,
    })
    driver = webdriver.Remote(command_executor=url + '/wd/hub', options=options)
    driver.set_page_load_timeout(60)
    driver.set_window_size(1912, 966)
    allure.dynamic.parameter('remote_browser', browser)
    folder = Path(os.getenv('SELENOID_EVIDENCE', 'results/selenoid'))
    folder.mkdir(parents=True, exist_ok=True)
    record = {'test': request.node.nodeid, 'session': driver.session_id,
              'browser': driver.capabilities.get('browserName'),
              'version': driver.capabilities.get('browserVersion'), 'video': video_name}
    try:
        menu = SeleniumSelectMenuPage(driver).open()
        yield menu
    finally:
        try:
            screenshot = driver.get_screenshot_as_png()
            (folder / (video_name + '.png')).write_bytes(screenshot)
            allure.attach(screenshot, 'Remote browser', allure.attachment_type.PNG)
            allure.attach(driver.page_source, 'Remote DOM', allure.attachment_type.HTML)
        finally:
            driver.quit()
            (folder / (video_name + '.json')).write_text(json.dumps(record, indent=2), encoding='utf-8')
        # Selenoid finishes and renames video asynchronously after WebDriver quit.
        import time
        for attempt in range(15):
            response = requests.get(url + '/video/' + video_name, timeout=10)
            if response.status_code == 200 and response.content:
                (folder / video_name).write_bytes(response.content)
                allure.attach(response.content, video_name, 'video/mp4', 'mp4')
                break
            if response.status_code not in (200, 404):
                response.raise_for_status()
            time.sleep(1)
        else:
            pytest.fail('Selenoid video was not saved: ' + video_name)


def test_single_choices(remote_menu):
    remote_menu.choose('Group 1, option 1', 2)
    remote_menu.choose('Dr.', 3)
    assert remote_menu.single(2) == 'Group 1, option 1'
    assert remote_menu.single(3) == 'Dr.'


def test_unknown_single_preserves_selection(remote_menu):
    remote_menu.choose('Group 2, option 1', 2)
    remote_menu.search('zzzz_no_such_option', 2)
    remote_menu.no_options()
    remote_menu.field(2).send_keys(Keys.ENTER)
    remote_menu.field(2).send_keys(Keys.CONTROL, 'a')
    remote_menu.field(2).send_keys(Keys.BACKSPACE, Keys.ESCAPE)
    assert remote_menu.single(2) == 'Group 2, option 1'


def test_multiselect_remove_and_independence(remote_menu):
    remote_menu.choose('Mrs.', 3)
    remote_menu.choose('Green')
    remote_menu.choose('Blue')
    remote_menu.remove('Blue')
    assert remote_menu.chips() == ['Green']
    assert remote_menu.single(3) == 'Mrs.'


def test_native_controls(remote_menu):
    remote_menu.native('oldSelectMenu').select_by_visible_text('Blue')
    assert remote_menu.native('oldSelectMenu').first_selected_option.text == 'Blue'
    cars = remote_menu.native('cars')
    cars.deselect_all()
    cars.select_by_value('volvo')
    cars.select_by_value('audi')
    assert [e.text for e in cars.all_selected_options] == ['Volvo', 'Audi']


def test_clear_search_restores_options(remote_menu):
    remote_menu.choose('Green')
    remote_menu.search('zzzz_no_such_option')
    remote_menu.no_options()
    remote_menu.search('')
    remote_menu.wait.until(lambda d: [e.text for e in d.find_elements(By.CSS_SELECTOR, '[role="option"]')] == ['Blue', 'Black', 'Red'])
    assert remote_menu.field().get_attribute('value') == ''
    assert remote_menu.chips() == ['Green']
