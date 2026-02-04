"""
Test apps' views through real HTTP requests from outside.
All tests match tests in `test_client.py`, but are done
from outside with the `reqests` module.
"""
from django.test import LiveServerTestCase
from django.conf import settings

from typing import Tuple
from pathlib import Path
import json
import os
import subprocess
import requests
import shutil
from time import sleep

from project_reader import get_all_fsts, get_projects
from api.management.commands.projectsautoinit import Command as ProjectsAutoInitCommand
from api.models import ProjectMetadata, FstType, FstLanguage, FstTypeRelation, FstLanguageRelation

URL_PREFIX = os.getenv('FSTHUB_URL_PREFIX', '')
URL_PREFIX = '' if URL_PREFIX is None else URL_PREFIX
URL_TO_TEST = os.getenv('FSTHUB_URL_TO_TEST', '')

class ApiTest(LiveServerTestCase):
    db_cmd = ProjectsAutoInitCommand(stdout=open(os.devnull, 'w'))
    test_data = Path(__file__).parent / 'test_data'
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
        super().setUpClass()
        settings.HFST_CONTENT_ROOT = cls.test_root
        cls.test_root.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.test_root)

    @classmethod
    def db_projectsautoinit(cls):
        cls.db_cmd.init_projects()
        cls.db_cmd.init_transducers()

    @classmethod
    def populate_test_root(cls):
        for proj in cls.dummy_projects:
            proj_dir = cls.test_root / proj
            proj_dir.mkdir()
            for type, fsts in cls.dummy_transducers.items():
                for fst in fsts:
                    proj_dir.joinpath(fst).touch()
        cls.db_projectsautoinit()

    @classmethod
    def compile_test_hfst(cls):
        proj_root = cls.test_root / 'pingpong'
        proj_root.mkdir()
        shutil.copyfile(cls.test_data / 'Makefile',
                        proj_root / 'Makefile')
        shutil.copyfile(cls.test_data / 'ping.fst',
                        proj_root / 'ping.fst')
        result = subprocess.run(
            ["make"],
            cwd=proj_root,
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(f'Failed to compile test hfst:\n{result.stdout}\n{result.stderr}')

        cls.db_projectsautoinit()

    def send_request(self, endpoint: str, method: str = 'GET',
                     headers: dict = None, body: dict = None) -> Tuple[int, str, dict]:
        endpoint = f'{URL_PREFIX}{endpoint}'.replace('//', '/')
        base_url = URL_TO_TEST or self.live_server_url
        url = f'{base_url}/{endpoint}'

        default_headers = {
            'Accept': 'application/json'
        }
        if headers:
            default_headers.update(headers)

        if method.upper() == 'GET':
            resp = requests.get(url, headers=default_headers)
        elif method.upper() == 'POST':
            resp = requests.post(url, headers=default_headers, json=body)
        if 'text/html' in resp.headers['Content-Type']:
            return resp.status_code, url, resp.content.decode(encoding='utf-8')
        return resp.status_code, url, json.loads(resp.content.decode(encoding='utf-8'))

class PingAllTest(ApiTest):
    def test_api_ping_all(self):
        def ping_endpoint(endpoint: str, expected_code: int):
            code, url, resp = self.send_request(endpoint)
            self.assertEqual(code, expected_code, f'{url} {code}: {resp}')
        ping_endpoint('/api/fst/',          200)
        ping_endpoint('/api/fst/example/',  400)
        ping_endpoint('/api/fst/metadata/', 400)
        ping_endpoint('/api/fst_type/',     200)
        ping_endpoint('/api/fst_language/', 200)
        ping_endpoint('/api/fst/call/',     405)
        ping_endpoint('/api/fst/filter/',   200)
        ping_endpoint('/api/project/',      200)

class GetProjectsTest(ApiTest):
    def test_api_get_projects(self):
        # test if all projects are returned correctly
        self.populate_test_root()
        sleep(0.01)
        code, url, resp = self.send_request('/api/project')
        self.assertIn('results', resp, url)
        resp_projects = set(v['name'] for v in resp['results'])
        db_projects = set(p.directory for p in ProjectMetadata.objects.all())
        
        self.assertSetEqual(resp_projects, set(self.dummy_projects))
        self.assertSetEqual(db_projects, set(self.dummy_projects))

class GetFstsTest(ApiTest):
    def test_api_get_fsts(self):
        # test if all transducers are returned correctly
        self.populate_test_root()
        sleep(0.01)
        code, url, resp = self.send_request('/api/fst')
        self.assertIn('results', resp, url)
        resp_fsts = set(v['name'] for v in resp['results'])
        filesystem_fsts = set(get_all_fsts())
        
        self.assertSetEqual(resp_fsts, filesystem_fsts)

class GetTypesTest(ApiTest):
    def test_api_get_fst_types(self):
        self.populate_test_root()
        sleep(0.01)
        code, url, resp = self.send_request('/api/fst_type')
        self.assertEqual(code, 200, url)
        self.assertIsInstance(resp, list, url)
        for it in resp:
            self.assertIsInstance(it, dict, url)
            self.assertIn('name', it, url)
        self.assertSetEqual(
            set(x['name'] for x in resp),
            {'generator', 'analyzer', 'transliterator'},
            url
        )

class FstOperationsTest(ApiTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.compile_test_hfst()

    def test_api_hfst_call(self):
        def _assert_hfst_call(body: dict, expected: dict, exp_code: int = 200):
            code, url, resp = self.send_request(
                '/api/fst/call/',
                method='POST',
                headers={'Content-Type': 'application/json'},
                body=body
            )
            self.assertEqual(code, exp_code, resp)
            self.assertEqual(resp, expected)

        _assert_hfst_call(
            body={'hfst_file': 'pingpong/ping.hfstol',
                  'fst_input': 'ping'},
            expected={'output': 'ping\tpong'}
        )
        _assert_hfst_call(
            body={'hfst_file': 'pingpong/ping.hfstol',
                  'fst_input': 'ping',
                  'output_format': 'xerox'},
            expected={'output': 'ping\tpong'}
        )
        _assert_hfst_call(
            body={'hfst_file': 'pingpong/ping.hfstol',
                  'fst_input': 'ping',
                  'output_format': 'apertium'},
            expected={'output': '^ping/pong$'}
        )
        _assert_hfst_call(
            body={'hfst_file': 'pingpong/ping.hfstol',
                  'fst_input': 'ping',
                  'output_format': 'cg'},
            expected={'output': '"<ping>"\n\t"pong"'}
        )
        _assert_hfst_call(
            body={'hfst_file': 'pingpong/ping.hfstol',
                  'fst_input': 'ping',
                  'output_format': 'bar'},
            expected={'output_format': ['"bar" is not a valid choice.']},
            exp_code=400
        )

    def test_api_hfst_example(self):
        for _ in range(20):
            code, url, resp = self.send_request(
                '/api/fst/example/?hfst_file=pingpong/ping.hfstol'
            )
            self.assertEqual(code, 200, resp)
            self.assertEqual(
                resp, 
                {'example': {'input': 'ping', 'output': 'pong'}}
            )

    def test_api_hfst_metadata(self):
        expected_meta = {
            'Author': 'Jane Doe',
            'Year': '2000',
            'foo': 'bar'
        }
        code, url, resp = self.send_request(
            '/api/fst/metadata/?hfst_file=pingpong/ping.hfstol'
        )
        self.assertEqual(code, 200, resp)
        self.assertEqual(resp['metadata'], resp['metadata'] | expected_meta)
