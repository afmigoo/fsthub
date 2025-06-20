from unittest import TestCase
from pathlib import Path
from typing import List
from random import getrandbits
from time import sleep
import shutil

from . import ProjectReader

class TestProjectReaderViews(TestCase):
    test_root = Path(__file__).parent / 'tmp'

    def setUp(self):
        self.test_root.mkdir(exist_ok=True)
        ProjectReader.root = self.test_root
    def tearDown(self):
        # rm all contents
        shutil.rmtree(self.test_root)
        # make sure to clear all cache
        self.test_root.mkdir()
        tmp = ProjectReader.update_interval
        ProjectReader.update_interval = 0.01
        sleep(0.1)
        ProjectReader._update_if_time()
        self.test_root.rmdir()
        ProjectReader.update_interval = tmp

    def create_project(self, name: str, fsts: List[str]):
        d = self.test_root / name
        d.mkdir()
        for fst_name in fsts:
            f = d / fst_name
            f.touch()
    
    def test_spam_empty(self):
        for _ in range(10_000):
            _ = ProjectReader.fst_exists(str(getrandbits))
            _ = ProjectReader.project_exists(str(getrandbits))
            _ = ProjectReader.get_projects()
            _ = ProjectReader.get_fsts()

    def test_put_single(self):
        ProjectReader.update_interval = 0.5
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), 0)
        self.assertEqual(len(fsts), 0)

        self.create_project('TEST1', [f'fst{i}' for i in range(100)])
        sleep(0.5)

        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), 1)
        self.assertEqual(len(fsts), 100)
    
    def test_put_many(self):
        ProjectReader.update_interval = 0.5
        Np, Nfst = 1_000, 10
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), 0)
        self.assertEqual(len(fsts), 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}' for i in range(Nfst)])
        sleep(0.5)

        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), Np)
        self.assertEqual(len(fsts), Nfst * Np)

        prefixes = set(fst.split('/')[-2] for fst in fsts)
        for pref in prefixes:
            self.assertTrue(ProjectReader.project_exists(str(pref)))
            
    def test_put_many_delete_many(self):
        Np, Nfst = 100, 20
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), 0)
        self.assertEqual(len(fsts), 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}' for i in range(Nfst)])

        ProjectReader.update_interval = 10 ** 10
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), 0)
        self.assertEqual(len(fsts), 0)

        ProjectReader.update_interval = 0.1
        sleep(0.1)
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), Np)
        self.assertEqual(len(fsts), Np * Nfst)

        for p in range(Np):
            self.create_project(f'SECOND_TEST{p}', [f'fst{i}' for i in range(Nfst)])
        ProjectReader.update_interval = 5
        sleep(2)
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), Np)
        self.assertEqual(len(fsts), Np * Nfst)
        sleep(3)
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), Np * 2)
        self.assertEqual(len(fsts), Np * Nfst * 2)

        shutil.rmtree(self.test_root)
        self.test_root.mkdir()
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), Np * 2)
        self.assertEqual(len(fsts), Np * Nfst * 2)

        ProjectReader.update_interval = 0.1
        sleep(0.1)
        projects = ProjectReader.get_projects()
        fsts = ProjectReader.get_fsts()
        self.assertEqual(len(projects), 0)
        self.assertEqual(len(fsts), 0)