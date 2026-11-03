"""Deterministic contract checks for the late-loading header layout shift.

The fixture simulates a slow image response, not a delay in production actions.
Run separately: python -m pytest checks/test_page_readiness.py
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time

import pytest
from playwright.sync_api import Error

from pages.select_menu_page import SelectMenuPage


@pytest.fixture
def slow_header_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/logo'):
                time.sleep(0.5)  # Controlled network latency reproduces the original race.
                broken = self.path.endswith('broken')
                self.send_response(404 if broken else 200)
                self.send_header('Content-Type', 'image/svg+xml')
                self.end_headers()
                try:
                    self.wfile.write(b'not an image' if broken else b'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="76"></svg>')
                except ConnectionError:
                    pass  # A failed readiness assertion can close the browser first.
            else:
                logo = '/logo-broken' if self.path.endswith('broken') else '/logo'
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(('<header><img src="' + logo + '"></header>'
                                  '<select id="oldSelectMenu"><option>Blue</option></select>').encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()
    worker.join()


def test_open_waits_for_header_intrinsic_size(page, monkeypatch, slow_header_server):
    monkeypatch.setattr(SelectMenuPage, 'URL', slow_header_server)
    SelectMenuPage(page).open()
    assert page.locator('header img').evaluate('(image) => image.complete && image.naturalWidth > 0')
    assert page.locator('header img').bounding_box()['height'] == 76


def test_broken_header_stops_before_interaction(page, monkeypatch, slow_header_server):
    monkeypatch.setattr(SelectMenuPage, 'URL', slow_header_server + '/broken')
    with pytest.raises(Error, match='header image failed to load'):
        SelectMenuPage(page).open()
