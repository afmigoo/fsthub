from unittest import TestCase
from pathlib import Path
from typing import List
from random import getrandbits
from time import sleep
import random
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
        PR.update_interval = 0.01
        sleep(0.01)
        PR._update_if_time()
        self.test_root.rmdir()

    def create_project(self, name: str, fsts: List[str]):
        d = self.test_root / name
        d.mkdir()
        for fst_name in fsts:
            f = d / fst_name
            f.touch()
    
    def test_spam_empty(self):
        for _ in range(10_000):
            self.assertFalse(PR.fst_exists(str(getrandbits)))
            self.assertFalse(PR.project_exists(str(getrandbits)))
            self.assertEqual(len(list(PR.get_projects())), 0)
            self.assertEqual(len(list(PR.get_all_fsts())), 0)
            self.assertEqual(PR.get_project_count(), 0)
            self.assertEqual(PR.get_fst_count(), 0)

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

        prefixes = set(fst.split('/')[-2] for fst in PR.get_all_fsts())
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
        PR.update_interval = 3
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

    def test_all_exist(self):
        sleep(0.1)
        Np = 3
        Nfst = 3

        PR.update_interval = 0.1
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)
        self.assertFalse(PR.fst_exists('some/thing'))
        self.assertFalse(PR.project_exists('some'))

        all_projects = []
        all_fst = []
        fsts = [f'fst{i}' for i in range(Nfst)]
        for p in range(Np):
            new_p = f'TEST{p}'
            all_projects.append(new_p)
            all_fst.extend(f'{new_p}/{f}' for f in fsts)
            self.create_project(new_p, fsts)
        sleep(0.1)
        for p in all_projects:
            self.assertTrue(PR.project_exists(p), f'{p} does not exist')
            self.assertSetEqual(set(f'{p}/{f}' for f in fsts),
                                set(PR.get_fsts(p)))
        for fst in all_fst:
            self.assertTrue(PR.fst_exists(fst), f'{fst} does not exist')

        self.assertFalse(PR.fst_exists('some/thing'))
        self.assertFalse(PR.project_exists('some'))

class TestPRRandom(TestCase):
    temp_root = Path(__file__).parent / 'tmp'
    @classmethod
    def setUpClass(cls):
        # Create a temp dir structure
        cls.temp_root.mkdir()
        PR.root = cls.temp_root
        PR.update_interval = 0.5  # Short interval for faster testing
        
        # Create test projects/files
        cls.files = {
            p: [f"file_{i}.hfst" for i in range(random.randint(1, 15))]
            for p in [f"Project_{i}" for i in range(31)]
        }
        
        for project, files in cls.files.items():
            (cls.temp_root / project).mkdir()
            for f in files:
                (cls.temp_root / project / f).touch()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_root)

    def test_random_operations(self):
        operations = [
            self._get_projects,
            self._get_all_fsts,
            self._get_project_fsts,
            self._project_exists,
            self._fst_exists,
            self._add_project,
            self._del_project,
            self._add_fst,
            self._del_fst,
        ]
        
        for _ in range(50):  # Adjust count as needed
            op = random.choice(operations)
            op()
            sleep(0.1)  # Allow cache updates occasionally

    def _get_projects(self):
        result = list(PR.get_projects())
        self.assertEqual(set(result), set(self.files.keys()))
        
    def _get_all_fsts(self):
        all_files = [
            f"{p}/{f}" for p in self.files.keys()
            for f in self.files[p]
        ]
        result = list(PR.get_all_fsts())
        self.assertEqual(set(result), set(all_files))
        
    def _get_project_fsts(self):
        project = random.choice(list(self.files.keys()))
        result = list(PR.get_fsts(project))
        self.assertEqual(set(result), set(f'{project}/{f}' for f in self.files[project]))
        
    def _project_exists(self):
        project = random.choice(list(self.files.keys()) + ["nonexistent"])
        expected = project in self.files.keys()
        self.assertEqual(PR.project_exists(project), expected)
        
    def _fst_exists(self):
        project = random.choice(list(self.files.keys()))
        fname = random.choice(self.files[project] + ["ghost.hfst"])
        path = f"{project}/{fname}"
        expected = fname in self.files[project]
        self.assertEqual(PR.fst_exists(path), expected)

    def _add_project(self):
        new_proj = f'RandProj{random.randint(1, 10_000_000)}'
        before_update = set(PR.get_projects())
        self.assertSetEqual(before_update, set(str(d.relative_to(self.temp_root)) 
                                               for d in self.temp_root.iterdir() if d.is_dir()))
        self.assertSetEqual(before_update, set(self.files.keys()))

        (self.temp_root / new_proj).mkdir(exist_ok=True)
        if not new_proj in self.files.keys():
            self.files[new_proj] = []
        sleep(PR.update_interval)
        after_update = set(PR.get_projects())
        self.assertSetEqual(after_update, set([str(d.relative_to(self.temp_root)) 
                                               for d in self.temp_root.iterdir() if d.is_dir()]))
        self.assertSetEqual(after_update, set(self.files.keys()))

    def _del_project(self):
        pass

    def _add_fst(self):
        pass

    def _del_fst(self):
        pass
