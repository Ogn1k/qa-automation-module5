"""Учебная модель Select Menu, основанная на модуле 4; не исходный код DemoQA."""
COLORS = ('Green', 'Blue', 'Black', 'Red')

def update_selection(selected, option, clear_requested=False):
    result = set(selected)
    if option in COLORS:
        result.add(option)
    if clear_requested:
        result.clear()
    return result

def available_options(selected, query):
    return [x for x in COLORS if x not in selected and query.casefold() in x.casefold()]

def remove_option(selected, option):
    return set(selected) - {option}

def valid_single(option, allowed):
    if not option:
        return False
    return option in allowed
