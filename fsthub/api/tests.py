"""
Test apps' views through real HTTP requests from outside.
All tests match tests in `test_client.py`, but are done
from outside with the `reqests` module.
"""
from dotenv import load_dotenv, find_dotenv
from django.test import LiveServerTestCase
from django.conf import settings

from typing import Tuple
from pathlib import Path
import json
import os
import requests
import shutil
from time import sleep

from project_reader import get_all_fsts, get_projects
from .management.commands.projectsautoinit import Command as ProjectsAutoInitCommand
from .models import ProjectMetadata, FstType, FstLanguage, FstTypeRelation, FstLanguageRelation

load_dotenv(find_dotenv('.env'))
URL_PREFIX = os.getenv('FSTHUB_PREFIX')
URL_PREFIX = '' if URL_PREFIX is None else URL_PREFIX
URL_TO_TEST = os.getenv('URL_TO_TEST')

class ApiTest(LiveServerTestCase):
    db_cmd = ProjectsAutoInitCommand(stdout=open(os.devnull, 'w'))
    test_root = Path(__file__).parent / 'tmp'
    dummy_projects = [
        'Russian', 'German', 'Kazakh', 'Tatar', 'Adyghe',
        'Shughni', 'Rutul', 'Kyrgiz', 'Tuva', 'Hakhas'
    ]
    dummy_transducers = {
        'generator': ['gen_smth.hfst', 'smth_gen.hfst', 
                      'generate_smth.hfst', 'smth_generate.hfst'],
        'analyzer': ['ana_smth.hfst', 'smth_ana.hfst', 
                     'analyze_smth.hfst', 'smth_analyze.hfst'],
        'transliterator': ['smth2smth.hfst', 'smth_to_smth.hfst']
    }

    @classmethod
    def setUpClass(cls):
        settings.HFST_CONTENT_ROOT = cls.test_root
        cls.test_root.mkdir(exist_ok=True)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_root)
        return super().tearDownClass()

    @classmethod
    def populate_test_root(cls):
        for proj in cls.dummy_projects:
            proj_dir = cls.test_root / proj
            proj_dir.mkdir()
            for type, fsts in cls.dummy_transducers.items():
                for fst in fsts:
                    proj_dir.joinpath(fst).touch()
        cls.db_cmd.init_projects()
        cls.db_cmd.init_transducers()
        
    def tearDown(self):
        shutil.rmtree(self.test_root)
        self.test_root.mkdir(exist_ok=True)
        sleep(0.01)

    def get_json(self, endpoint: str, headers: dict = None) -> Tuple[int, dict]:
        endpoint = f'{URL_PREFIX}{endpoint}'.replace('//', '/')
        base_url = self.live_server_url if URL_TO_TEST is None else URL_TO_TEST
        url = f'{base_url}/{endpoint}'

        default_headers = {
            'Accept': 'application/json'
        }
        if headers:
            default_headers.update(headers)

        resp = requests.get(url, headers=default_headers)
        if 'text/html' in resp.headers['Content-Type']:
            return resp.status_code, url, resp.content.decode(encoding='utf-8')
        return resp.status_code, url, json.loads(resp.content.decode(encoding='utf-8'))

class PingAllTest(ApiTest):
    def test_ping_all(self):
        def ping_endpoint(endpoint: str, expected_code: int):
            code, url, resp = self.get_json(endpoint)
            self.assertEqual(code, expected_code, f'{url} {code}: {resp}')
        ping_endpoint('/api/fst/',          200)
        ping_endpoint('/api/fst_type/',     200)
        ping_endpoint('/api/fst_language/', 200)
        ping_endpoint('/api/fst/call/',     405)
        ping_endpoint('/api/fst/filter/',   200)
        ping_endpoint('/api/project/',      200)

class GetProjectsTest(ApiTest):
    def test_projects(self):
        # test if all projects are returned correctly
        self.populate_test_root()
        sleep(0.01)
        code, url, resp = self.get_json('/api/project')
        self.assertIn('results', resp, url)
        resp_projects = set(v['name'] for v in resp['results'])
        db_projects = set(p.directory for p in ProjectMetadata.objects.all())
        
        self.assertSetEqual(resp_projects, set(self.dummy_projects))
        self.assertSetEqual(db_projects, set(self.dummy_projects))

class GetFstsTest(ApiTest):
    def test_fsts(self):
        # test if all transducers are returned correctly
        self.populate_test_root()
        sleep(0.01)
        code, url, resp = self.get_json('/api/fst')
        self.assertIn('results', resp, url)
        resp_fsts = set(v['name'] for v in resp['results'])
        filesystem_fsts = set(get_all_fsts())
        
        self.assertSetEqual(resp_fsts, filesystem_fsts)
