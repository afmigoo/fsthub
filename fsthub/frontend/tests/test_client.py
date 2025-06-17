from dotenv import load_dotenv, find_dotenv
from django.test import Client
from unittest import TestCase as UnitTestCase

import os

# Create your tests here.
class TestPingViews(UnitTestCase):
    def setUp(self):
        load_dotenv(find_dotenv('.env'))
        self.url_prefix = os.getenv('FSTHUB_PREFIX')
        self.url_prefix = '' if self.url_prefix is None else self.url_prefix
        self.url_prefix = '/' + self.url_prefix
        self.client = Client()

    def test_ping_index(self):
        href = f'{self.url_prefix}'
        resp = self.client.get(href)
        self.assertEqual(resp.status_code, 200, f'{href} - {resp}')
    def test_ping_browse(self):
        href = f'{self.url_prefix}browse'
        resp = self.client.get(href)
        self.assertEqual(resp.status_code, 200, f'{href} - {resp}')
    def test_ping_about(self):
        href = f'{self.url_prefix}about'
        resp = self.client.get(href)
        self.assertEqual(resp.status_code, 200, f'{href} - {resp}')

class TestLangLocale(UnitTestCase):
    def setUp(self):
        load_dotenv(find_dotenv('.env'))
        self.url_prefix = os.getenv('FSTHUB_PREFIX')
        self.url_prefix = '' if self.url_prefix is None else self.url_prefix
        self.url_prefix = '/' + self.url_prefix
        self.client = Client()

    def test_ping_index_en(self):
        href = f'{self.url_prefix}'
        resp = self.client.get(href, headers={
            'Accept-Language': 'en-US,en;q=0.5'
        })
        html = resp.content.decode()
        self.assertIn('Home', html)
        self.assertIn('FST catalog', html)
        self.assertIn('About', html)
    def test_ping_index_ru(self):
        href = f'{self.url_prefix}'
        resp = self.client.get(href, headers={
            'Accept-Language': 'ru-RU,ru;q=0.5'
        })
        self.assertIn('Каталог! FST', resp.content.decode())