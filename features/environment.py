import os
from playwright.sync_api import sync_playwright

def before_all(context):
    context.pw = sync_playwright().start()
    options = {'headless':True}
    if os.getenv('BROWSER_CHANNEL'):
        options['channel'] = os.environ['BROWSER_CHANNEL']
    context.browser = getattr(context.pw, os.getenv('BROWSER','chromium')).launch(**options)

def before_scenario(context, scenario):
    context.page = context.browser.new_page(viewport={'width':1912,'height':966})

def after_scenario(context, scenario):
    context.page.close()

def after_all(context):
    context.browser.close()
    context.pw.stop()
