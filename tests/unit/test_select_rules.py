import pytest
from app.select_rules import update_selection, available_options, remove_option, valid_single, COLORS
pytestmark = pytest.mark.unit

@pytest.fixture
def selected():
    return {'Green'}

@pytest.mark.parametrize('option,clear,expected', [
    ('Blue',False,{'Green','Blue'}),('Orange',False,{'Green'}),
    ('Blue',True,set()),('Orange',True,set())])
def test_model_paths(selected, option, clear, expected):
    original = selected.copy()
    assert update_selection(selected, option, clear) == expected
    assert selected == original

@pytest.mark.parametrize('option', COLORS)
def test_allowed_color(option):
    assert update_selection(set(),option) == {option}

def test_duplicate(selected):
    assert update_selection(selected, 'Green') == selected

@pytest.mark.parametrize('query,expected', [
    ('Blue',['Blue']),('blue',['Blue']),('zzzz',[]),
    ('Green',[]),('', ['Blue','Black','Red'])])
def test_search(selected, query, expected):
    assert available_options(selected,query) == expected

@pytest.mark.parametrize('prior,option,expected', [
    ({'Green','Blue'},'Blue',{'Green'}),({'Green'},'Green',set()),
    (set(),'Green',set()),({'Blue'},'Green',{'Blue'})])
def test_remove(prior, option, expected):
    assert remove_option(prior,option) == expected

@pytest.mark.parametrize('option,expected', [('',False),('Dr.',True),('Prof.',True),('unknown',False)])
def test_single(option, expected):
    assert valid_single(option,('Dr.','Prof.')) is expected
