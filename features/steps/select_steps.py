from behave import given, when, then
from playwright.sync_api import expect
from pages.select_menu_page import SelectMenuPage

@given('the Select Menu page is open')
def open_page(context):
    context.menu=SelectMenuPage(context.page).open()

@when('I select Green and Blue and choose Mrs.')
def select_values(context):
    context.menu.choose('Green');context.menu.choose('Blue');context.menu.choose('Mrs.',3)

@when('I remove Blue')
def remove(context): context.menu.remove('Blue')

@then('only Green remains and Mrs. is preserved')
def preserved(context):
    assert context.menu.chips()==['Green']
    expect(context.page.locator('#selectOne')).to_contain_text('Mrs.')

@given('Green is selected')
def green(context): context.menu.choose('Green')

@when('I search for an unavailable color')
def search(context): context.menu.search('zzzz_no_such_option')

@then('no options are offered and Green remains')
def no_options(context):
    context.menu.no_options()
    assert context.menu.chips()==['Green']
