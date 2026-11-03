"""WebDriver Page Object for Docker/Selenoid; no DOM rewriting."""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SeleniumSelectMenuPage:
    URL = 'https://demoqa.com/select-menu'

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'oldSelectMenu')))
        return self

    def field(self, number=4):
        locator = (By.ID, f'react-select-{number}-input')
        element = self.wait.until(EC.presence_of_element_located(locator))
        if not element.is_displayed():
            # React hides the single-select input after selection; reopen its control.
            control = element.find_element(By.XPATH, 'ancestor::div[contains(@class,"-control")][1]')
            control.click()
        return self.wait.until(EC.visibility_of_element_located(locator))

    def search(self, text, number=4):
        element = self.field(number)
        element.click()
        if element.get_attribute('value'):
            # Backspace in an empty React multiselect removes the last selection.
            element.send_keys(Keys.CONTROL, 'a', Keys.NULL, Keys.BACKSPACE)
        if text:
            element.send_keys(text)
        self.wait.until(lambda _: element.get_attribute('aria-expanded') == 'true')

    def choose(self, text, number=4):
        self.search(text, number)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@role="option" and normalize-space(.)="{text}"]'))).click()
        if number == 4:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'[aria-label="Remove {text}"]')))
        else:
            self.wait.until(lambda _: self.single(number) == text)

    def single(self, number):
        root = '#withOptGroup' if number == 2 else '#selectOne'
        values = self.driver.find_elements(By.CSS_SELECTOR, root + ' [class$="-singleValue"]')
        return values[0].text if values else None

    def chips(self):
        return [e.get_attribute('aria-label')[7:] for e in self.driver.find_elements(By.CSS_SELECTOR, '[aria-label^="Remove "]')]

    def remove(self, text):
        locator = (By.CSS_SELECTOR, f'[aria-label="Remove {text}"]')
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        self.wait.until(lambda _: text not in self.chips())

    def no_options(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[text()="No options"]')))
        assert not self.driver.find_elements(By.CSS_SELECTOR, '[role="option"]')

    def native(self, element_id):
        element = self.driver.find_element(By.ID, element_id)
        # A fixed footer can cover native options in Firefox. Scroll the actual
        # control to the viewport centre; do not change DOM or selected values.
        self.driver.execute_script('arguments[0].scrollIntoView({block:"center"})', element)
        return Select(element)
