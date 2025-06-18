"""
Test api through a `django.test.Client` object.
"""
from django.test import LiveServerTestCase
from django.http import HttpResponse
from django.test import Client

from dotenv import load_dotenv, find_dotenv
from typing import List
import json
import os

from ..views import LimitedPagination
from ..models import FstProject

class TestClientApiViews(LiveServerTestCase):
    def setUp(self):
        load_dotenv(find_dotenv('.env'))
        self.url_prefix = os.getenv('FSTHUB_PREFIX')
        self.url_prefix = '' if self.url_prefix is None else self.url_prefix
        self.url_prefix = '/' + self.url_prefix
        self.client = Client()

    def response_tester(self, resp: HttpResponse, 
                        href: str = "href unspecified"):
        """Test if response has a valid format"""
        self.assertIsInstance(resp, HttpResponse)
        self.assertEqual(resp.status_code, 200, f'{href} - {resp}')
        self.assertIn('Content-Type', resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')

    def project_results_tester(self, data: dict, 
                               reference: List[FstProject], 
                               href: str = "href unspecified"): 
        """Test if response format is valid and if response data matches 
        reference data"""
        self.assertIn('results', data, href)
        self.assertIsInstance(data['results'], list, href)
        self.assertEqual(len(data['results']), len(reference), href)
        for res, ref in zip(data['results'], reference):
            self.assertIsInstance(res, dict, href)
            self.assertEqual(set(res.keys()), 
                             set(['id', 'directory']), href)
            for k, v in res.items():
                self.assertIn(k, ref.__dict__, href)
                self.assertEqual(v, ref.__dict__[k], href)

    def test_project_single_dummy(self):
        dummies = [
            FstProject(directory='Dummy')
        ]
        for d in dummies:
            d.save()

        href = f'{self.url_prefix}api/project/all'
        resp = self.client.get(href)
        self.response_tester(resp, href)
        data = json.loads(resp.content)
        self.project_results_tester(data, dummies, href)

    def test_project_item_limit(self):
        limit = LimitedPagination.max_page_size
        dummies = [FstProject(directory=f'Dummy{i}')
                   for i in range(limit)]
        for d in dummies:
            d.save()
        # api returns alphabetical order
        dummies.sort(key=lambda x: x.directory)

        href = f'{self.url_prefix}api/project/all?page_size={limit}'
        resp = self.client.get(href)
        self.response_tester(resp, href)
        data = json.loads(resp.content)
        self.project_results_tester(data, dummies, href)

    def test_project_item_limit_plus_one(self):
        limit = LimitedPagination.max_page_size
        N = limit + 1
        dummies = [FstProject(directory=f'Dummy{i}')
                   for i in range(N)]
        for d in dummies:
            d.save()
        # api returns alphabetical order
        dummies.sort(key=lambda x: x.directory)

        href = f'{self.url_prefix}api/project/all?page_size={N}'
        resp = self.client.get(href)
        self.response_tester(resp, href)
        data = json.loads(resp.content)
        self.project_results_tester(data, dummies[:limit], href)

    def test_project_item_twice_limit(self):
        limit = LimitedPagination.max_page_size
        N = limit * 2
        dummies = [FstProject(directory=f'Dummy{i}')
                   for i in range(N)]
        for d in dummies:
            d.save()
        # api returns alphabetical order
        dummies.sort(key=lambda x: x.directory)

        href = f'{self.url_prefix}api/project/all?page_size={N}'
        resp = self.client.get(href)
        self.response_tester(resp, href)
        data = json.loads(resp.content)
        self.project_results_tester(data, dummies[:limit], href)