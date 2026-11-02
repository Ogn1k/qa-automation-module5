import csv
from pathlib import Path
import pytest
import allure
from playwright.sync_api import expect
from pages.select_menu_page import SelectMenuPage
pytestmark = [pytest.mark.ui, allure.feature('Select Menu — Module 4')]

@pytest.fixture
def menu(page):
    return SelectMenuPage(page).open()

@allure.story('TC-SM-01')
def test_tc_sm_01_five_controls(menu, page):
    expect(page.get_by_role('combobox')).to_have_count(4)
    expect(page.locator('select')).to_have_count(2)
    for field in (2,3,4): expect(menu.input(field)).to_be_visible()
    expect(page.locator('#cars')).to_be_visible()

@allure.story('TC-SM-02')
def test_tc_sm_02_single_values(menu):
    menu.choose('Group 1, option 1',2)
    menu.choose('Dr.',3)

@allure.story('TC-SM-03')
def test_tc_sm_03_unknown_value(menu, page):
    menu.search('zzzz_no_such_option',2)
    menu.no_options()
    menu.input(2).press('Enter')
    expect(page.locator('#withOptGroup')).not_to_contain_text('option zzzz_no_such_option, selected')

@allure.story('TC-SM-04')
def test_tc_sm_04_native_values(menu, page):
    page.locator('#oldSelectMenu').select_option(label='Blue')
    expect(page.locator('#oldSelectMenu option:checked')).to_have_text('Blue')
    menu.cars(['volvo','audi'])
    assert menu.selected_cars()==['Volvo','Audi']

@allure.story('TC-SM-05')
def test_tc_sm_05_empty_boundary(menu):
    menu.choose('Green');menu.remove('Green');menu.cars([])
    assert menu.chips()==[] and menu.selected_cars()==[]

@allure.story('TC-SM-06')
def test_tc_sm_06_one_boundary(menu):
    menu.choose('Green');menu.cars(['volvo'])
    assert menu.chips()==['Green'] and menu.selected_cars()==['Volvo']

@allure.story('TC-SM-07')
def test_tc_sm_07_four_boundary(menu):
    colors=['Green','Blue','Black','Red']
    for color in colors: menu.choose(color)
    menu.cars(['volvo','saab','opel','audi'])
    menu.search('Green');menu.no_options()
    assert menu.chips()==colors
    assert menu.selected_cars()==['Volvo','Saab','Opel','Audi']

@allure.story('TC-SM-08')
def test_tc_sm_08_matching_candidate(menu):
    menu.choose('Green');menu.search('Blue')
    expect(menu.option('Blue')).to_have_count(1)
    menu.option('Blue').click();menu.search('Green');menu.no_options()
    assert menu.chips()==['Green','Blue']

@allure.story('TC-SM-09')
def test_tc_sm_09_no_match_preserves_selection(menu):
    menu.search('zzzz_no_such_option');menu.no_options()
    assert menu.chips()==[]
    menu.choose('Green');menu.search('zzzz_no_such_option');menu.no_options()
    assert menu.chips()==['Green']

@allure.story('TC-SM-10')
def test_tc_sm_10_state_transitions(menu):
    field=menu.input()
    expect(field).to_have_attribute('aria-expanded','false')
    assert menu.chips()==[]
    field.click();expect(field).to_have_attribute('aria-expanded','true')
    menu.choose('Green');expect(field).to_have_attribute('aria-expanded','true')
    field.press('Escape');expect(field).to_have_attribute('aria-expanded','false')
    assert menu.chips()==['Green']
    menu.remove('Green');field.press('Escape')
    expect(field).to_have_attribute('aria-expanded','false')
    assert menu.chips()==[]

@allure.story('TC-SM-11')
def test_tc_sm_11_invalid_transitions(menu):
    menu.search('zzzz_no_such_option');menu.no_options()
    field=menu.input();field.press('Enter')
    assert menu.chips()==[]
    field.press('Escape');field.focus();field.press('Backspace')
    assert menu.chips()==[]

rows=list(csv.DictReader((Path(__file__).parents[2]/'data/pairwise.csv').open(encoding='utf-8')))
@allure.story('TC-SM-12')
@pytest.mark.ddt
@pytest.mark.parametrize('row',rows,ids=[f"{r['field']}-{r['method']}" for r in rows])
def test_tc_sm_12_pairwise(menu,row):
    menu.choose(row['value'],int(row['field']),row['method']=='keyboard')

@allure.story('TC-SM-13')
def test_tc_sm_13_use_case(menu,page):
    menu.choose('Group 2, option 1',2);menu.choose('Mrs.',3)
    page.locator('#oldSelectMenu').select_option(label='Black')
    menu.choose('Green');menu.choose('Blue');menu.cars(['volvo','audi'])
    menu.remove('Blue');menu.search('zzzz_no_such_option');menu.no_options()
    assert menu.chips()==['Green'] and menu.selected_cars()==['Volvo','Audi']
    expect(page.locator('#withOptGroup')).to_contain_text('Group 2, option 1')
    expect(page.locator('#selectOne')).to_contain_text('Mrs.')
    expect(page.locator('#oldSelectMenu option:checked')).to_have_text('Black')

@allure.story('TC-SM-15')
def test_tc_sm_15_repetition_and_independence(menu):
    for _ in range(5): menu.choose('Green');menu.remove('Green')
    menu.choose('Blue');menu.choose('Dr.',3)
    assert menu.chips()==['Blue']

@allure.story('TC-SM-16')
def test_tc_sm_16_clear_search(menu):
    menu.choose('Green');menu.search('zzzz');menu.no_options()
    menu.input().fill('');menu.input().press('Escape')
    assert menu.chips()==['Green']
