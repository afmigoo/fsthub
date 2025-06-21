"""
Test apps' views through real HTTP requests from outside.
All tests match tests in `test_client.py`, but are done
from outside with the `reqests` module.
"""
from dotenv import load_dotenv, find_dotenv
from django.test import LiveServerTestCase

from typing import Tuple
from pathlib import Path
import json
import os
import requests
import shutil
from time import sleep

from project_reader import ProjectReader as PR
from .management.commands.projectsautoinit import Command as ProjectsAutoInitCommand
from .models import ProjectMetadata, FstType, FstLanguage, FstTypeRelation, FstLanguageRelation

load_dotenv(find_dotenv('.env'))
URL_PREFIX = os.getenv('FSTHUB_PREFIX')
URL_PREFIX = '' if URL_PREFIX is None else URL_PREFIX
URL_TO_TEST = os.getenv('URL_TO_TEST')

class ApiTest(LiveServerTestCase):
    test_root = Path(__file__).parent / 'tmp'
    cache_upd_interval = 0.01
    db_cmd = ProjectsAutoInitCommand(stdout=open(os.devnull, 'w'))
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

    def wipe_test_root(self):
        # rm all contents
        shutil.rmtree(self.test_root)
        # make sure to clear all cache
        self.test_root.mkdir()
        PR.update_interval = self.cache_upd_interval
        sleep(self.cache_upd_interval)
        PR._update_if_time()
        self.test_root.rmdir()

    def create_test_root(self):
        PR.root = self.test_root
        self.test_root.mkdir(exist_ok=True)

    def populate_test_root(self):
        for proj in self.dummy_projects:
            proj_dir = self.test_root / proj
            proj_dir.mkdir()
            for type, fsts in self.dummy_transducers.items():
                for fst in fsts:
                    proj_dir.joinpath(fst).touch()
        self.db_cmd.init_projects()
        self.db_cmd.init_transducers()

    def setUp(self):
        self.create_test_root()
        
    def tearDown(self):
        self.wipe_test_root()

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

    def test_projects(self):
        # test if all projects are returned correctly
        self.populate_test_root()
        sleep(self.cache_upd_interval)
        code, url, resp = self.get_json('/api/project')
        self.assertIn('results', resp, url)
        resp_projects = set(v['name'] for v in resp['results'])
        db_projects = set(p.directory for p in ProjectMetadata.objects.all())
        
        self.assertSetEqual(resp_projects, set(self.dummy_projects))
        self.assertSetEqual(db_projects, set(self.dummy_projects))

        # test after one was deleted from filesystem
        shutil.rmtree(self.test_root / self.dummy_projects[0])
        sleep(self.cache_upd_interval)
        code, url, resp = self.get_json('/api/project')
        self.assertIn('results', resp, url)
        resp_projects = set(v['name'] for v in resp['results'])
        db_projects = set(p.directory for p in ProjectMetadata.objects.all())

        self.assertSetEqual(resp_projects, set(self.dummy_projects[1:]))
        self.assertSetEqual(db_projects, set(self.dummy_projects))

        # test after one was created in filesystem
        new_proj = self.test_root / 'Gibberish'
        new_proj.mkdir()
        sleep(self.cache_upd_interval)
        code, url, resp = self.get_json('/api/project')
        self.assertIn('results', resp, url)
        resp_projects = set(v['name'] for v in resp['results'])
        db_projects = set(p.directory for p in ProjectMetadata.objects.all())

        self.assertSetEqual(resp_projects, set([str(new_proj.relative_to(self.test_root))] + \
                                               self.dummy_projects[1:]))
        self.assertSetEqual(db_projects, set(self.dummy_projects))

        # update the db and check if its up to date (it must contain deleted dirs too)
        self.db_cmd.init_projects()
        db_projects = set(p.directory for p in ProjectMetadata.objects.all())
        self.assertSetEqual(db_projects, set([str(new_proj.relative_to(self.test_root))] + \
                                             self.dummy_projects))

    def test_fsts(self):
        pass
