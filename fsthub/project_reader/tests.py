from unittest import TestCase
from pathlib import Path
from typing import List
from time import sleep
import shutil
from django.conf import settings

from . import get_all_fsts, get_projects, dir_exists, file_exists, get_fsts

class TestPRViews(TestCase):
    test_root = Path(__file__).parent / 'tmp'

    @classmethod
    def setUpClass(cls):
        settings.HFST_CONTENT_ROOT = cls.test_root
        return super().setUpClass()

    def setUp(self):
        self.test_root.mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def create_project(self, name: str, fsts: List[str]):
        d = self.test_root / name
        d.mkdir()
        for fst_name in fsts:
            f = d / fst_name
            f.touch()

    def test_reader_put_single(self):
        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        self.create_project('TEST1', [f'fst{i}.hfst' for i in range(100)])
        sleep(0.01)

        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, 1)
        self.assertEqual(t_count, 100)
    
    def test_reader_put_many(self):
        Np, Nfst = 1_000, 10
        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}.hfst' for i in range(Nfst)])
        sleep(0.01)

        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)

        prefixes = set(fst.split('/')[-2] for fst in get_all_fsts())
        for pref in prefixes:
            self.assertTrue(dir_exists(str(pref)))
            
    def test_reader_put_many_delete_many(self):
        Np, Nfst = 100, 20
        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}.hfst' for i in range(Nfst)])

        sleep(0.01)
        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)

        for p in range(Np):
            self.create_project(f'SECOND_TEST{p}', [f'fst{i}.hfst' for i in range(Nfst)])
        sleep(0.01)
        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, Np * 2)
        self.assertEqual(t_count, Np * Nfst * 2)

        shutil.rmtree(self.test_root)
        self.test_root.mkdir(exist_ok=True)

        sleep(0.01)
        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

    def test_reader_all_exist(self):
        sleep(0.01)
        Np = 3
        Nfst = 3

        p_count = len(get_projects())
        t_count = len(get_all_fsts())
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)
        self.assertFalse(file_exists('some/thing.hfst'))
        self.assertFalse(dir_exists('some'))

        all_projects = []
        all_fst = []
        fsts = [f'fst{i}.hfst' for i in range(Nfst)]
        for p in range(Np):
            new_p = f'TEST{p}'
            all_projects.append(new_p)
            all_fst.extend(f'{new_p}/{f}' for f in fsts)
            self.create_project(new_p, fsts)
        sleep(0.1)
        for p in all_projects:
            self.assertTrue(dir_exists(p), f'{p} does not exist')
            self.assertSetEqual(set(f'{p}/{f}' for f in fsts),
                                set(get_fsts(p)))
        for fst in all_fst:
            self.assertTrue(file_exists(fst), f'{fst} does not exist')

        self.assertFalse(file_exists('some/thing.hfst'))
        self.assertFalse(dir_exists('some'))
    