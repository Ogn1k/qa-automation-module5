import re
from playwright.sync_api import expect

class SelectMenuPage:
    URL = 'https://demoqa.com/select-menu'
    ROOTS = {2:'#withOptGroup', 3:'#selectOne'}

    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(self.URL, wait_until='domcontentloaded', timeout=60000)
        expect(self.page.locator('#oldSelectMenu')).to_be_visible()
        return self

    def input(self, field=4):
        return self.page.locator(f'#react-select-{field}-input')

    def option(self, text):
        return self.page.locator('[role="option"]').filter(has_text=re.compile('^'+re.escape(text)+'$'))

    def search(self, text, field=4):
        self.input(field).fill(text)
        expect(self.input(field)).to_have_attribute('aria-expanded','true')

    def choose(self, text, field=4, keyboard=False):
        self.search(text,field)
        expect(self.option(text)).to_be_visible()
        if keyboard:
            self.input(field).press('ArrowDown')
            self.input(field).press('Enter')
        else:
            self.option(text).click()
        if field == 4:
            expect(self.page.get_by_label('Remove '+text,exact=True)).to_be_visible()
        else:
            expect(self.page.locator(self.ROOTS[field])).to_contain_text(text)

    def chips(self):
        return self.page.locator('[aria-label^="Remove "]').evaluate_all('(es)=>es.map(e=>e.getAttribute("aria-label").slice(7))')

    def remove(self, color):
        remove = self.page.get_by_label('Remove '+color,exact=True)
        remove.click()
        expect(remove).to_have_count(0)

    def cars(self, values):
        self.page.locator('#cars').select_option(values)

    def selected_cars(self):
        return self.page.locator('#cars').evaluate('(e)=>[...e.selectedOptions].map(o=>o.text)')

    def no_options(self):
        expect(self.page.get_by_text('No options',exact=True)).to_be_visible()
        expect(self.page.locator('[role="option"]')).to_have_count(0)

    def selected_single(self, field):
        return self.page.locator(self.ROOTS[field]).locator('[class$="-singleValue"]')

    def expect_options(self, values):
        expect(self.page.locator('[role="option"]')).to_have_text(values)

    def clear_search(self):
        self.input().fill('')
        expect(self.input()).to_have_value('')
