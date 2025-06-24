"""
Test apps' views through a `django.test.Client` object.
"""
from dotenv import load_dotenv, find_dotenv
from django.test import Client
from unittest import TestCase as UnitTestCase

import os

class TestClientPingViews(UnitTestCase):
    def setUp(self):
        load_dotenv(find_dotenv('settings.env'))
        self.url_prefix = os.getenv('FSTHUB_PREFIX')
        self.url_prefix = '' if self.url_prefix is None else self.url_prefix
        self.url_prefix = '/' + self.url_prefix
        self.client = Client()

    def ping_page(self, path):
        href = f'{self.url_prefix}{path}'
        resp = self.client.get(href)
        self.assertEqual(resp.status_code, 200, f'{href} - {resp}')
    def test_ping_all(self):
        self.ping_page('')
        self.ping_page('playground')
        self.ping_page('projects')
        self.ping_page('about')

class TestClientLangLocale(UnitTestCase):
    def setUp(self):
        load_dotenv(find_dotenv('settings.env'))
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
        self.assertIn(f'<a href="{self.url_prefix}">Home</a>', html)
    def test_ping_index_ru(self):
        href = f'{self.url_prefix}'
        resp = self.client.get(href, headers={
            'Accept-Language': 'ru-RU,ru;q=0.5'
        })
        html = resp.content.decode()
        self.assertIn(f'<a href="{self.url_prefix}">Главная</a>', html)