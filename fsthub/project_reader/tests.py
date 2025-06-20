from unittest import TestCase
from pathlib import Path
from typing import List
from random import getrandbits
from time import sleep
import shutil

from . import ProjectReader as PR

class TestPRViews(TestCase):
    test_root = Path(__file__).parent / 'tmp'

    def setUp(self):
        self.test_root.mkdir(exist_ok=True)
        PR.root = self.test_root
    def tearDown(self):
        # rm all contents
        shutil.rmtree(self.test_root)
        # make sure to clear all cache
        self.test_root.mkdir()
        tmp = PR.update_interval
        PR.update_interval = 0.01
        sleep(0.1)
        PR._update_if_time()
        self.test_root.rmdir()
        PR.update_interval = tmp

    def create_project(self, name: str, fsts: List[str]):
        d = self.test_root / name
        d.mkdir()
        for fst_name in fsts:
            f = d / fst_name
            f.touch()
    
    def test_spam_empty(self):
        for _ in range(10_000):
            _ = PR.fst_exists(str(getrandbits))
            _ = PR.project_exists(str(getrandbits))
            _ = PR.get_projects()
            _ = PR.get_fsts()

    def test_put_single(self):
        PR.update_interval = 0.5
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        self.create_project('TEST1', [f'fst{i}' for i in range(100)])
        sleep(0.5)

        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 1)
        self.assertEqual(t_count, 100)
    
    def test_put_many(self):
        PR.update_interval = 0.5
        Np, Nfst = 1_000, 10
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}' for i in range(Nfst)])
        sleep(0.5)

        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)

        prefixes = set(fst.split('/')[-2] for fst in PR.get_fsts())
        for pref in prefixes:
            self.assertTrue(PR.project_exists(str(pref)))
            
    def test_put_many_delete_many(self):
        Np, Nfst = 100, 20
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}' for i in range(Nfst)])

        PR.update_interval = 10 ** 10
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        PR.update_interval = 0.1
        sleep(0.1)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)

        for p in range(Np):
            self.create_project(f'SECOND_TEST{p}', [f'fst{i}' for i in range(Nfst)])
        PR.update_interval = 5
        sleep(2)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)
        sleep(3)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np * 2)
        self.assertEqual(t_count, Np * Nfst * 2)

        shutil.rmtree(self.test_root)
        self.test_root.mkdir()
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np * 2)
        self.assertEqual(t_count, Np * Nfst * 2)

        PR.update_interval = 0.1
        sleep(0.1)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)