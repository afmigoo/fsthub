"""
Test apps' views through real HTTP requests from outside.
All tests match tests in `test_client.py`, but are done
from outside with the `reqests` module.
"""
from django.test import LiveServerTestCase

from typing import Tuple
import os
import requests

def get_html(url: str, headers: dict = None) -> Tuple[int, str]:
    resp = requests.get(url, headers=headers)
    return resp.status_code, resp.content.decode(encoding='utf-8')

class TestRequestsPingViews(LiveServerTestCase):
    def setUp(self):
        self.url_prefix = os.getenv('FSTHUB_URL_PREFIX', '')
        self.url_prefix = '' if self.url_prefix is None else self.url_prefix
        self.url_prefix = '/' + self.url_prefix

    def ping_page(self, path):
        url = f'{self.live_server_url}{self.url_prefix}{path}'
        code, resp = get_html(url)
        self.assertEqual(code, 200, f'{url} - {resp}')
    def test_front_requests_ping_all(self):
        self.ping_page('')
        self.ping_page('playground')
        self.ping_page('projects')
        self.ping_page('about')

class TestRequestsLangLocale(LiveServerTestCase):
    def setUp(self):
        self.url_prefix = os.getenv('FSTHUB_URL_PREFIX', '')
        self.url_prefix = '' if self.url_prefix is None else self.url_prefix
        self.url_prefix = '/' + self.url_prefix

    def test_front_requests_ping_index_en(self):
        url = f'{self.live_server_url}{self.url_prefix}'
        _, html = get_html(url, headers={
            'Accept-Language': 'en-US,en;q=0.5'
        })
        self.assertIn(f'<a href="{self.url_prefix}">Home</a>', html)
    def test_front_requests_ping_index_ru(self):
        url = f'{self.live_server_url}{self.url_prefix}'
        _, html = get_html(url, headers={
            'Accept-Language': 'ru-RU,ru;q=0.5'
        })
        self.assertIn(f'<a href="{self.url_prefix}">Главная</a>', html)
